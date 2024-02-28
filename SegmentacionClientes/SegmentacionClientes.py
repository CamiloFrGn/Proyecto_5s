# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 09:34:17 2020

@author: jsdelgadoc
"""
import modulo_conn_sql as mcq
import numpy as np
import pandas as pd 
import datetime 
from io import BytesIO
from flask import send_file

#Query BD SQL-Server Cemex
def querySQL(query, parametros):
    #Conectar con base sql y ejecutar consulta
    cursor = conectarSQL()
    try:
        cursor.execute(query, parametros)
        #obtener nombre de columnas
        names = [ x[0] for x in cursor.description]
        
        #Reunir todos los resultado en rows
        rows = cursor.fetchall()
        resultadoSQL = []
            
        #Hacer un array con los resultados
        while rows:
            resultadoSQL.append(rows)
            if cursor.nextset():
                rows = cursor.fetchall()
            else:
                rows = None
                
        #Redimensionar el array para que quede en dos dimensiones
        resultadoSQL = np.array(resultadoSQL)
        resultadoSQL = np.reshape(resultadoSQL, (resultadoSQL.shape[1], resultadoSQL.shape[2]) )
    finally:
            if cursor is not None:
                cursor.close()
    return pd.DataFrame(resultadoSQL, columns = names)

#SQL Methods to get operation data
def conectarSQL():
    conn = mcq.ConexionSQL()
    cursor = conn.getCursor()
    return cursor

def obtener_criterios(pais):
    df = pd.read_excel("criterioSLD.xlsx")
    df = df[df['Pais'] == pais]
    return df

def Volumen(pais, dias, peso, df):
    #df = querySQL( "{CALL SCAC_AP10_dataset_servicios (?,?)}" , (pais, float(dias) ) )
    #df = df.fillna(value=np.nan)
    
    #se toma el volumen entregado, sin tener en cuenta los ATS
    df = df[ (df['TipoPlanta']=='Central') & (df['Estatus']=='Normal') & ( ~df['NombreObra'].str.contains('ATS') & (df['Entrega'] != '') ) ]
    
    #volumen por codigo de cliente
    volumen_cliente = df.groupby(['Cliente'])['VolPartida'].sum().reset_index()
    volumen_cliente = volumen_cliente.rename(columns = {'VolPartida':'volumen_cliente'})
    
    #cliente con mayor volumen
    maxVolumenCliente = volumen_cliente[volumen_cliente['Cliente'] != '7460' ]['volumen_cliente'].max()
    
    #base para obtener el puntaje por obras 
    puntaje_volumen = df.groupby(['Obra', 'Cliente'])['VolPartida'].sum().reset_index()
    puntaje_volumen = puntaje_volumen.rename(columns = {'VolPartida':'volumen_obra'})
    
    puntaje_volumen = pd.merge( puntaje_volumen, volumen_cliente, on='Cliente' )
    
    #se calcula el puntaje con respecto al cliente con mayor puntaje y el peso, el cual se multipica por 100 ya que esta en terminos de porcentaje
    puntaje_volumen['puntaje_volumen'] = (puntaje_volumen['volumen_cliente'] / maxVolumenCliente) * (peso * 100)
    
    
    return puntaje_volumen[['Obra', 'volumen_obra', 'puntaje_volumen']]
    
def Cancelacion(pais, dias, peso, df_pedidos):
    
    #Dataset de la programación
    #df_pedidos = querySQL( "{CALL SCAC_AP11_Dataset_Pedidos (?,?)}" , (pais, dias) )
    #df_pedidos = df_pedidos.fillna(value=np.nan)
    
    df_canc = pd.pivot_table(
        df_pedidos,
        index = ['Obra'],
        values = ['CancelacionCliente', 'VolPartida'],
        aggfunc = np.sum
    )
    df_canc = df_canc.reset_index()
    df_canc['cancelacion_Cliente'] = (df_canc['CancelacionCliente']/df_canc['VolPartida'])*100
    df_canc = df_canc.drop(['CancelacionCliente', 'VolPartida'], axis= 1)
    
    df_canc.loc[df_canc['cancelacion_Cliente'] < 10, 'Puntaje %'] = 1
    df_canc.loc[(df_canc['cancelacion_Cliente'] >= 10) & (df_canc['cancelacion_Cliente'] < 12), 'Puntaje %'] = 0.8
    df_canc.loc[(df_canc['cancelacion_Cliente'] >= 12) & (df_canc['cancelacion_Cliente'] < 14), 'Puntaje %'] = 0.6
    df_canc.loc[(df_canc['cancelacion_Cliente'] >= 14) & (df_canc['cancelacion_Cliente'] < 16), 'Puntaje %'] = 0.4
    df_canc.loc[(df_canc['cancelacion_Cliente'] >= 16) & (df_canc['cancelacion_Cliente'] < 20), 'Puntaje %'] = 0.2
    df_canc.loc[df_canc['cancelacion_Cliente'] >= 20, 'Puntaje %'] = 0
        
    puntaje = 100 * peso
    df_canc['puntaje_cancelaciones'] = df_canc['Puntaje %'] * puntaje
    
    df_canc = df_canc.drop(['cancelacion_Cliente', 'Puntaje %'], axis= 1)
    return df_canc

    
def TiempoObra(pais, dias, peso):
    df_componentes = querySQL("SELECT * FROM AV37_Componentes_Ciclo_Malla_Turnos_Clientes_Tabla", () )
    df_componentes['T.Obra'] = df_componentes['T.Obra'].fillna((df_componentes['T.Obra'].mean())) 
    
    df_teo = df_componentes.groupby(['Cliente'])['T.Obra'].agg(['mean']).reset_index()
    df_teo = df_teo.rename(columns = {'mean':'tiempo_obra'})
    df_teo = df_teo.rename(columns = {'Cliente':'Obra'})
    
    
    df_teo.loc[df_teo['tiempo_obra'] <= 60, 'Puntaje %'] = 1
    df_teo.loc[(df_teo['tiempo_obra'] > 60) & (df_teo['tiempo_obra'] <= 70), 'Puntaje %'] = 0.5
    df_teo.loc[(df_teo['tiempo_obra'] > 70), 'Puntaje %'] = 0
    
    puntaje = 100 * peso
    df_teo['puntaje_tiempo_obra'] = df_teo['Puntaje %'] * puntaje
    df_teo = df_teo.drop(['tiempo_obra', 'Puntaje %'], axis= 1)
    return df_teo

def Fop(baseObras, peso):
    
    df_fop = querySQL( "SELECT * FROM  SCAC_AT13_FOP" , () )
    df = pd.merge(baseObras[['Obra']], df_fop, how = 'inner', on='Obra' )
    df[df['Fop'] < 0 ] = 0
    
    fop_max = df['Fop'].max()
    #se calcula el puntaje con respecto a la obra con mayor puntaje y el peso, el cual se multipica por 100 ya que esta en terminos de porcentaje
    df['puntaje_fop'] = (df['Fop'] / fop_max) * (peso * 100)
    return df[['Obra', 'puntaje_fop']]


def Dropsize(pais, dias, peso, df_serv):
    #Dataset de los despachos
    #df_serv = querySQL( "{CALL SCAC_AP10_dataset_servicios (?,?)}" , (pais, dias) )
    #df_serv = df_serv.fillna(value=np.nan)
    #df_serv['year_month'] = df_serv.FechaEntrega.dt.to_period('M')
    
    
    df_dz = df_serv[(df_serv['Entrega'] != '') & (df_serv['Estatus'] == 'Normal') & (df_serv['EstatusPedido'] == 'Completada - Cabecera')].groupby(['Obra'])['VolPartida'].agg(['mean'])
    df_dz = df_dz.rename(columns = {'mean':'vol_partida'})
    df_dz = df_dz.sort_values(by='vol_partida', ascending=False).reset_index()
    
    puntaje_max = peso * 100
    
    max_DzObra = df_dz['vol_partida'].max()
    
    df_dz['puntaje_dropsize'] = (df_dz['vol_partida'] / max_DzObra) * puntaje_max
    
    df_dz = df_dz.drop(['vol_partida'], axis= 1)
    return  df_dz

def segmentar_clientes(pais, dias, paramrandom ):
    
    if  pais == 'Panama' or pais == 'Puerto Rico':
        porcentaje_volumen_asertivo = 0.5
    else:
        porcentaje_volumen_asertivo = 0.6
    
    #Base para asignar una obra a una planta - BASE DESPACHOS
    df = querySQL( "{CALL SCAC_AP14_dataset_segmentacion (?,?)}" , (pais, dias ) )
    df = df.fillna(value=np.nan)
    
    #Dataset de la programación
    #df_pedidos = querySQL( "{CALL SCAC_AP11_Dataset_Pedidos (?,?)}" , (pais, dias) )
    #df_pedidos = df_pedidos.fillna(value=np.nan)
    
    df_pedidos = df
    
    #determino el volumen acumulado de la planta para al final filtrar las obras que solo ocupen el 60% relativo de su capacidad
    volumen_planta = df[(df['Entrega'] != '') &  (df['Estatus']=='Normal') ].groupby(['Planta'])['VolPartida'].sum().reset_index()
    volumen_planta['volumen_asertivos'] = volumen_planta['VolPartida'] * porcentaje_volumen_asertivo
    
    #se toma el volumen entregado, sin tener en cuenta los ATS
    df = df[ (df['TipoPlanta']=='Central') & (df['Estatus']=='Normal') & ( ~df['NombreObra'].str.contains('ATS') & (df['Entrega'] != '') ) ]   
    ultimos30Dias = datetime.datetime.today() - datetime.timedelta(30)
    volumen_obras_por_planta = df[(df['Entrega'] != '') &  (df['Estatus']=='Normal') & (df['Cliente'] != '7460') & (df['FechaEntrega'] >=  ultimos30Dias )  ].groupby(['Planta', 'Obra', 'NombreObra', 'Cliente', 'NombreCliente'])['VolPartida'].sum().reset_index()
    
    #se aplica ranking para determinar cual planta atiende a cada obra
    planta_base = volumen_obras_por_planta.assign(rnk=volumen_obras_por_planta.groupby(['Obra'])['VolPartida'].rank(method='first', ascending=False) ).query('rnk ==1').sort_values(['Obra', 'rnk'])
    
    planta_base = planta_base[['Planta', 'Obra', 'NombreObra', 'Cliente', 'NombreCliente']]
    
    if pais == 'Colombia' or pais == 'Panama' or pais == 'Puerto Rico' or pais == 'Costa Rica' :
        
        df1 =   Volumen(pais, dias, 0.40, df)
        df2 = Cancelacion(pais, dias, 0.20, df_pedidos)
        df3 = TiempoObra(pais, dias, 0.20)
        df4 = Fop(planta_base, 0.20)
        
        puntaje_obras = planta_base
        puntaje_obras = pd.merge( puntaje_obras, df1, how = 'left', on ='Obra' )
        puntaje_obras = pd.merge( puntaje_obras, df2, how = 'left', on ='Obra' )
        puntaje_obras = pd.merge( puntaje_obras, df3, how = 'left', on ='Obra' )
        puntaje_obras = pd.merge( puntaje_obras, df4, how = 'left', on ='Obra' )
        
        puntaje_obras = puntaje_obras.fillna(value=0)
        #puntaje_obras = puntaje_obras[puntaje_obras['volumen_obra'] > 50]
        puntaje_obras['puntaje'] = puntaje_obras['puntaje_volumen'] + puntaje_obras['puntaje_cancelaciones'] + puntaje_obras['puntaje_tiempo_obra'] + puntaje_obras['puntaje_fop']    
        
        #Se organiza por puntaje total y planta
        puntaje_obras = puntaje_obras.sort_values(['Planta', 'puntaje'], ascending=[True, False]).reset_index()
        puntaje_obras['vol_acumulado_obra'] = puntaje_obras.groupby(['Planta'])['volumen_obra'].cumsum()
        
        #se adjunta cota superior para filtrar la cantidad de obras que entran dentro de los asertivos, posteriormente se filtra
        puntaje_obras = pd.merge(puntaje_obras, volumen_planta[['Planta','volumen_asertivos']], on='Planta' )
        #puntaje_obras_asertivas = puntaje_obras[(puntaje_obras['vol_acumulado_obra'] <= puntaje_obras['volumen_asertivos']) &   (puntaje_obras['volumen_obra' ] >= 0.8 ) & (puntaje_obras['puntaje_volumen'] >= 0.8 ) & (puntaje_obras['puntaje'] >= 20) ]
        puntaje_obras_asertivas = puntaje_obras[(puntaje_obras['vol_acumulado_obra'] <= puntaje_obras['volumen_asertivos']) & (puntaje_obras['puntaje_volumen'] > 0.5 ) & (puntaje_obras['volumen_obra' ] > 45 ) & (puntaje_obras['puntaje'] >= 20) ]
        puntaje_obras_asertivas = puntaje_obras_asertivas[['Planta', 'Obra', 'NombreObra', 'Cliente', 'NombreCliente', 'puntaje_volumen', 'puntaje_cancelaciones', 'puntaje_tiempo_obra', 'puntaje_fop', 'puntaje']]
        
        #Asignar el numero de orden por planta
        puntaje_obras_asertivas = puntaje_obras_asertivas.assign(rnk=puntaje_obras_asertivas.groupby(['Planta'])['puntaje'].rank(method='first', ascending=False) )
        puntaje_obras = puntaje_obras[['Planta', 'Obra', 'NombreObra', 'Cliente', 'NombreCliente', 'puntaje_volumen', 'puntaje_cancelaciones', 'puntaje_tiempo_obra', 'puntaje_fop', 'puntaje']]
        
    #elif pais == 'Panama':
    else:    
        df1 =   Volumen(pais, dias, 0.40, df)
        df2 = Cancelacion(pais, dias, 0.10, df_pedidos)
        df3 = Dropsize(pais, dias, 0.10, df)
        df4 = Fop(planta_base, 0.20)
        df5 = TiempoObra(pais, dias, 0.20)
        
        puntaje_obras = planta_base
        puntaje_obras = pd.merge( puntaje_obras, df1, how = 'left', on ='Obra' )
        puntaje_obras = pd.merge( puntaje_obras, df2, how = 'left', on ='Obra' )
        puntaje_obras = pd.merge( puntaje_obras, df3, how = 'left', on ='Obra' )
        puntaje_obras = pd.merge( puntaje_obras, df4, how = 'left', on ='Obra' )
        puntaje_obras = pd.merge( puntaje_obras, df5, how = 'left', on ='Obra' )
        
        ######### Se realiza la sumatoria para el puntaje total #########
        puntaje_obras = puntaje_obras.fillna(value=0)
        puntaje_obras['puntaje'] = puntaje_obras['puntaje_volumen'] + puntaje_obras['puntaje_cancelaciones'] + puntaje_obras['puntaje_dropsize'] + puntaje_obras['puntaje_tiempo_obra'] + puntaje_obras['puntaje_fop']    
        
        #Se organiza por puntaje total y planta
        puntaje_obras = puntaje_obras.sort_values(['Planta', 'puntaje'], ascending=[True, False]).reset_index()
        puntaje_obras['vol_acumulado_obra'] = puntaje_obras.groupby(['Planta'])['volumen_obra'].cumsum()
        
        #se adjunta cota superior para filtrar la cantidad de obras que entran dentro de los asertivos, posteriormente se filtra
        puntaje_obras = pd.merge(puntaje_obras, volumen_planta[['Planta','volumen_asertivos']], on='Planta' )
        puntaje_obras_asertivas = puntaje_obras[(puntaje_obras['vol_acumulado_obra'] <= puntaje_obras['volumen_asertivos']) & (puntaje_obras['puntaje_volumen'] > 0.8 ) & (puntaje_obras['puntaje'] >= 20) ]
        puntaje_obras_asertivas = puntaje_obras_asertivas[['Planta', 'Obra', 'NombreObra', 'Cliente', 'NombreCliente', 'puntaje_volumen', 'puntaje_cancelaciones', 'puntaje_dropsize', 'puntaje_tiempo_obra', 'puntaje_fop', 'puntaje']]
        
        #Asignar el numero de orden por planta
        puntaje_obras_asertivas = puntaje_obras_asertivas.assign(rnk=puntaje_obras_asertivas.groupby(['Planta'])['puntaje'].rank(method='first', ascending=False) )
        puntaje_obras = puntaje_obras[['Planta', 'Obra', 'NombreObra', 'Cliente', 'NombreCliente', 'puntaje_volumen', 'puntaje_cancelaciones', 'puntaje_dropsize', 'puntaje_tiempo_obra', 'puntaje_fop', 'puntaje']]
    
    """
    writer = pd.ExcelWriter("resultados/SegmentacionClientes - " + pais + pd.to_datetime("now").strftime("%Y-%m-%d-%H-%M-%S") + ".xlsx", engine='xlsxwriter')
    puntaje_obras_asertivas.to_excel( writer, sheet_name="SLD")
    puntaje_obras.to_excel( writer, sheet_name="puntaje obras")
    
    writer.save()
    
    """
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    puntaje_obras_asertivas.to_excel( writer, sheet_name="SLD" )
    puntaje_obras.to_excel( writer, sheet_name="PuntajeTodas_Obras" )
    
    writer.close()
    output.seek(0)
    return send_file(output, attachment_filename="SegmentacionClientes - " + pais + pd.to_datetime("now").strftime("%Y-%m-%d-%H-%M-%S") + ".xlsx", as_attachment=True)
    
"""    
pais = 'Colombia'
dias = 180
segmentar_clientes(pais, dias, 151)
"""

