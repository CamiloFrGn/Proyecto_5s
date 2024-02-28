import pandas as pd
import numpy as np
import sys


def clean_data(now,now_date):
    try:
        print("Cleaning data")
        #read conser.txt file to get data from sap
        #full_path = r"C:\Users\jsdelgadoc\Documents\Proyectos-Cemex\sap_extraction\text_files\progscac.txt"
        full_path = r"C:\Users\snortiz\Documents\projects\sap_extraction\text_files\progscac.txt"        
        data = pd.read_csv(full_path,sep='|', encoding='latin-1', skiprows=1)

        #get total rows in dataframe to then filter out the first and last row that are non valid rows
        data_len = len(data.index)-2
        data = data.loc[1:data_len]
        #clean dataset
        data = data.reset_index(drop=True)
        #drop unnamed columns
        data = data.drop(columns=['Unnamed: 0'])
        data = data.drop(columns=['Unnamed: '+str(len(data.columns.values))])  

        #rename columns to sql columns
        data = data.rename(columns={
            'Entrega  ': 'Entrega', 
            'Pos.': 'posicion', 
            'Remision      ': 'Remision', 
            'Planta': 'Planta', 
            'Nombre Planta          ': 'NombrePlanta', 
            'Pedido.     ': 'Pedido',
            'Estatus pedido                ': 'EstatusPedido', 
            'Volumen de': 'VolumenPedido', 
            '# de servi': 'servicio',
            'Pos.': 'Posicion', 
            'Est. Pos.': 'EstatusPosicion', 
            'Estatus Posición              ': 'EstatusPosicion2',
            'Vol.Partid': 'VolPartida', 
            'Frecuencia': 'Frecuencia', 
            'Estatus                ': 'Estatus',
            'Nombre cliente                     ': 'NombreCliente', 
            'Cliente ': 'Cliente', 
            'Nombre Obra                        ': 'NombreObra',
            'Obra    ': 'Obra', 
            'Nombre Frente                      ': 'NombreFrente', 
            'Frente  ': 'Frente',
            'Prod. com.': 'ProductoComercial', 
            'Desc.Tecnica           ': 'DescTecnica', 
            'Solicitante                              ': 'Solicitante',
            'Obs.': 'ComentarioInterno', 
            'ID Conduct': 'IDConductor', 
            'Nombre Conductor                 ': 'NombreConductor',
            'F. Req    ': 'FechaReq', 
            'Hr. Req ': 'HrReq', 
            'Ult C. Fec': 'FReqUlt',
            'Ult C. Hr.': 'HrReqUlt', 
            'Fecha Entr': 'FechaEntrega', 
            'H.Entrega': 'HoraEntregaPartida',
            'Creado el ': 'CreadoEl', 
            'Hora    ': 'HoraCreacion', 
            'H.Real Ini': 'HRealInicioCarga',
            'H.Real Fin': 'HRealFinCarga', 
            'R. Hacia O': 'RHaciaObra', 
            'R. en Obra': 'REnObra',
            'R. Hacia P': 'RHaciaPlanta', 
            'R. Llegada': 'RLlegada', 
            'Fecha Canc': 'FechaCancelacion',
            'Hora Cance': 'HoraCancelacion', 
            'Cl. Doc.  ': 'ClaseDocumento', 
            'Nº vehíc.': 'Placa',
            'Medio            ': 'ElementoAColar', 
            'Elem Colar ': 'Contrato', 
            'OC': 'OrdenCompra',
            'Mtv. Cancelación                   ': 'MtvCancelacion', 
            '  Grado latitud': 'Latitud', 
            '       Grad.long.': 'Longitud',
            'Nombre 1                      ': 'Comercial', 
            'H.Carga Pr': 'FechaConsulta'})

        if len(data) <= 1:
            print("FINALIZADO SIN DATOS")
        else:
             
            #covert datetime for date columns
            data['FechaReq'] = data['FechaReq'].astype(str)
            data['FechaReq'] = data['FechaReq'].str.replace('.','-')
            data['FechaReq'] = data['FechaReq'].replace(r'^\s*$', np.nan, regex=True)
            data['FechaReq'] = data['FechaReq'].astype(str)
            data['FechaReq'] = data.FechaReq.str.strip()
            data['FechaReq'] = pd.to_datetime(data['FechaReq'], format="%d-%m-%Y")

            data['FReqUlt'] = data['FReqUlt'].astype(str)
            data['FReqUlt'] = data['FReqUlt'].str.replace('.','-')
            data['FReqUlt'] = data['FReqUlt'].replace(r'^\s*$', np.nan, regex=True)
            data['FReqUlt'] = data['FReqUlt'].astype(str)
            data['FReqUlt'] = data.FReqUlt.str.strip()
            data['FReqUlt'] = pd.to_datetime(data['FReqUlt'], format="%d-%m-%Y")

            data['FechaEntrega'] = data['FechaEntrega'].astype(str)
            data['FechaEntrega'] = data['FechaEntrega'].str.replace('.','-')
            data['FechaEntrega'] = data['FechaEntrega'].replace(r'^\s*$', np.nan, regex=True)
            data['FechaEntrega'] = data['FechaEntrega'].astype(str)
            data['FechaEntrega'] = data.FechaEntrega.str.strip()
            data['FechaEntrega'] = pd.to_datetime(data['FechaEntrega'], format="%d-%m-%Y")

            data['CreadoEl'] = data['CreadoEl'].astype(str)
            data['CreadoEl'] = data['CreadoEl'].str.replace('.','-')
            data['CreadoEl'] = data['CreadoEl'].replace(r'^\s*$', np.nan, regex=True)
            data['CreadoEl'] = data['CreadoEl'].astype(str)
            data['CreadoEl'] = data.CreadoEl.str.strip()
            data['CreadoEl'] = pd.to_datetime(data['CreadoEl'], format="%d-%m-%Y")

            data['FechaCancelacion'] = data['FechaCancelacion'].astype(str)
            data['FechaCancelacion'] = data['FechaCancelacion'].str.replace('.','-')
            data['FechaCancelacion'] = data['FechaCancelacion'].replace(r'^\s*$', np.nan, regex=True)
            data['FechaCancelacion'] = data['FechaCancelacion'].astype(str)
            data['FechaCancelacion'] = data.FechaCancelacion.str.strip()
            data['FechaCancelacion'] = pd.to_datetime(data['FechaCancelacion'], format="%d-%m-%Y")

            #replace commas for numeric values
            data['VolPartida'] = data['VolPartida'].astype(str)
            data['VolPartida'] = data['VolPartida'].str.replace(',','.')
            data['VolumenPedido'] = data['VolumenPedido'].astype(str)
            data['VolumenPedido'] = data['VolumenPedido'].str.replace(',','.')
            #set lat and long tu null for now
            data['Latitud'] = None
            data['Longitud'] = None        
        
            #add timestamp column and reverse hora consulta and hora carga prog
            data['HoraCargaProg'] = data['FechaConsulta']
            data['FechaConsulta'] = now

            #filter out dates that are not current date
            data = data[(data['FechaEntrega'] == now_date)]   

            #datatype setup
            print("CONVERTING COLUMNS DATA TYPE")
            data['Entrega'] = data['Entrega'].astype(str)
            data['Remision'] = data['Remision'].astype(str)
            data['Planta'] = data['Planta'].astype(str)
            data['NombrePlanta'] = data['NombrePlanta'].astype(str)
            data['Pedido'] = data['Pedido'].astype(str)
            data['EstatusPedido'] = data['EstatusPedido'].astype(str)
            data['VolumenPedido'] = data['VolumenPedido'].astype(float)
            data['servicio'] = data['servicio'].astype(str)
            data['Posicion'] = data['Posicion'].astype(int)
            data['EstatusPosicion'] = data['EstatusPosicion'].astype(str)
            data['EstatusPosicion2'] = data['EstatusPosicion2'].astype(str)
            data['VolPartida'] = data['VolPartida'].astype(float)
            data['Frecuencia'] = data['Frecuencia'].astype(int)
            data['Estatus'] = data['Estatus'].astype(str)
            data['NombreCliente'] = data['NombreCliente'].astype(str)
            data['Cliente'] = data['Cliente'].astype(int)
            data['NombreObra'] = data['NombreObra'].astype(str)
            data['Obra'] = data['Obra'].astype(str)
            data['NombreFrente'] = data['NombreFrente'].astype(str)
            data['Frente'] = data['Frente'].astype(str)
            data['ProductoComercial'] = data['ProductoComercial'].astype(int)
            data['DescTecnica'] = data['DescTecnica'].astype(str)
            data['Solicitante'] = data['Solicitante'].astype(str)
            data['ComentarioInterno'] = data['ComentarioInterno'].astype(str)
            data['IDConductor'] = data['IDConductor'].astype(str)
            data['NombreConductor'] = data['NombreConductor'].astype(str)
            data['ClaseDocumento'] = data['ClaseDocumento'].astype(str)
            data['Placa'] = data['Placa'].astype(str)
            data['ElementoAColar'] = data['ElementoAColar'].astype(str)
            data['Contrato'] = data['Contrato'].astype(str)
            data['OrdenCompra'] = data['OrdenCompra'].astype(str)
            data['MtvCancelacion'] = data['MtvCancelacion'].astype(str)
            data['Comercial'] = data['Comercial'].astype(str)
            data['HrReq'] = data['HrReq'].astype(str)
            data['HrReqUlt'] = data['HrReqUlt'].astype(str)
            data['HoraEntregaPartida'] = data['HoraEntregaPartida'].astype(str)
            data['HoraCreacion'] = data['HoraCreacion'].astype(str)
            data['HRealInicioCarga'] = data['HRealInicioCarga'].astype(str)
            data['HRealFinCarga'] = data['HRealFinCarga'].astype(str)
            data['RHaciaObra'] = data['RHaciaObra'].astype(str)
            data['REnObra'] = data['REnObra'].astype(str)
            data['RHaciaPlanta'] = data['RHaciaPlanta'].astype(str)
            data['RLlegada'] = data['RLlegada'].astype(str)
            data['HoraCancelacion'] = data['HoraCancelacion'].astype(str)
            data['HoraCargaProg'] = data['HoraCargaProg'].astype(str)
            
            #strip string columns
            #data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            #replace blanks for null values
            data = data.replace(r'^\s*$', np.nan, regex=True)
            #convert latin-1 to utf-8
            data['MtvCancelacion'] = data['MtvCancelacion'].astype(str)
            data.MtvCancelacion = data.MtvCancelacion.str.encode('utf-8')
            data['MtvCancelacion'] = data['MtvCancelacion'].astype(str)
            data.MtvCancelacion = data.MtvCancelacion.str.decode('utf-8')
            
            print("CONVERSION SUCCESSFULL")

            data['VolPartida'] = data['VolPartida'].fillna(0)
            data['VolumenPedido'] = data['VolumenPedido'].fillna(0)
            
            #convert yards to m3 for factories that apply. Conversion rate 0.764555
            data.loc[data['NombrePlanta'].str.contains('PR-',na=False), 'VolPartida'] = data['VolPartida'] * 0.764555
            data.loc[data['NombrePlanta'].str.contains('PR-',na=False), 'VolumenPedido'] = data['VolumenPedido'] * 0.764555
        
        return data
    except Exception as e:
        print(str(e))
        sys.exit()