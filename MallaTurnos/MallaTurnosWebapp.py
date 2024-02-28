# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 12:23:16 2020

@author: jsdelgadoc
"""
import modulo_conn_sql as mcq
import numpy as np
import pandas as pd 
import datetime 
from io import BytesIO
import pyodbc
import sqlalchemy as sa
import urllib
import warnings
warnings.filterwarnings('ignore')
#"""

from flask import Flask
from flask import send_file

#from flask_cors import CORS

app = Flask(__name__)
#CORS(app)

#"""


def conectarSQL():
    conn = mcq.ConexionSQL()
    cursor = conn.getCursor()
    return cursor


def encolarServicios(resultadoSQL):
    
    
    """
    ----------------------Encolar servicios----------------------
    """
    #elimino el primer elemento porque me quedo con zeros
    resultadoSQL = np.delete( resultadoSQL, (0), axis = 0)
    
    #Centro
    lineaAux = resultadoSQL[0][1]
    
    #HoraInicioCargueSE
    inicioAnterior = datetime.datetime.combine(datetime.date.today(), resultadoSQL[1][16] )
    
    #HoraFinCargueSE
    finAnterior = datetime.datetime.combine(datetime.date.today(), resultadoSQL[1][18] )
    
    #inicializo el inicio actual
    inicioActual = datetime.date.today()
    #ocios son aquellos tiempos entre cargues en los cuales la planta no tiene producción
    ocios = np.array([datetime.timedelta(minutes=0)])
    #parqueos es el tiempo extra de anticipacion que se le suma a ese viaje 
    parqueos = np.array([])
    
    #Tiempo maximo de anticipacion para llegar al cliente
    anticipacionMaxLlegadaCliente = datetime.timedelta(minutes=15)
    
    #Inicio con la programacion del ultimo servicio hacia el primero
    for i in range ( len(resultadoSQL) - 1 ):
    
        #HoraInicioCargueSE
        inicioActual = datetime.datetime.combine(datetime.date.today(), resultadoSQL[i][16] )
        
        #solo de la segunda linea hacia adelante puede existir una linea que representa el servicio anterior, 
        #recordar que estamos de atras hacia adelante
        if( i > 0) :
    
            inicioAnterior = datetime.datetime.combine(datetime.date.today(), resultadoSQL[i+1][16] )
            finAnterior = datetime.datetime.combine(datetime.date.today(), resultadoSQL[i+1][18] )
            lineaAux = resultadoSQL[i+1][1]
            
            ocio = inicioActual - finAnterior 
            if ocio > datetime.timedelta(minutes=0):
                ocios = np.append(ocios,[ocio])
            else:
                ocios = np.append(ocios,[datetime.timedelta(minutes=0)])
            
        #si las cargas se estan solapando se deben correr hacia atras y no son aun cargas reales
        if (inicioActual < finAnterior and lineaAux ==  resultadoSQL[i][1] and resultadoSQL[i+1][17] == 0):
            
            #obtengo la diferencia
            dif = finAnterior - inicioActual
            #corro el inicio y fin de carga lo que marque la diferencia
            resultadoSQL[i+1][16] = (datetime.datetime.combine(datetime.date.today(),resultadoSQL[i+1][16]) - dif).time()
            resultadoSQL[i+1][18] = (datetime.datetime.combine(datetime.date.today(),resultadoSQL[i+1][18]) - dif).time()
            
            #Corro hacia atras los demas componentes del ciclo la diferencia obtenida o el maximo de anticipacion
            if dif < anticipacionMaxLlegadaCliente : difAux = dif 
            else : difAux = anticipacionMaxLlegadaCliente
            #Salida a obra
            resultadoSQL[i+1][20] = (datetime.datetime.combine(datetime.date.today(),resultadoSQL[i+1][20]) - difAux).time()
            #Llegada a obra
            resultadoSQL[i+1][22] = (datetime.datetime.combine(datetime.date.today(),resultadoSQL[i+1][22]) - difAux).time()
            #Salida de obra
            resultadoSQL[i+1][24] = (datetime.datetime.combine(datetime.date.today(),resultadoSQL[i+1][24]) - difAux).time()
            #Llegada a planta
            resultadoSQL[i+1][26] = (datetime.datetime.combine(datetime.date.today(),resultadoSQL[i+1][26]) - difAux).time()
            
            
            #añado tiempo de parqueo
            parqueos = np.append(parqueos, [dif]) 
        else:
            parqueos = np.append(parqueos, [datetime.timedelta(minutes=0)]) 
        
        
    ocios = np.append(ocios,[datetime.timedelta(minutes=0)])
    parqueos = np.append(parqueos, [datetime.timedelta(minutes=0)]) 
            
    ocios = np.reshape(ocios, (ocios.shape[0],1))
    parqueos = np.reshape(parqueos, (parqueos.shape[0],1))
    
    resultadoSQL = resultadoSQL[::-1]
    ocios = ocios[::-1]
    parqueos = parqueos[::-1]
    
    #añado parqueos
    resultadoSQL = np.append(resultadoSQL, ocios, axis=1)
    resultadoSQL = np.append(resultadoSQL, parqueos, axis=1) 
    
    
    return resultadoSQL


"""
parametros:
    
    pPlanta: Nombre de la planta unica 
    pLineas: Numero de lineas que tiene esa planta
    pFecha: Fecha de la programación que se quiere procesar
    
    noPrecargadores: Número de conductores que va a realizar el precargue, si es 0 se entiende que no tiene precargadores
    tiempoPrecargando: Tiempo en minutos que un precargador antes de salir con su primer viaje
    
    pJornada: Jornada maxima de un conductor en minutos
    pAnticipacionllegada: Minutos de anticipacion de llegada de los conductores antes de su primer viaje
    
"""

def generarMalla(pPlanta, pLineas, pFecha, noPrecargadores, tiempoPrecargando, pJornada, pAnticipacionllegada):
    #Conectar con base sql y ejecutar consulta
    cursor = conectarSQL()
    
    #planta = "CO-PLANTA PUENTE ARANDA"
    #fechaEntrega = "2020-07-03"
    planta = pPlanta
    fechaEntrega = pFecha
    try:
        cursor.execute("{CALL SCAC_AP5_MallaTurnos_SinEncolar (?,?)}" , (planta, fechaEntrega) )
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
        if len(resultadoSQL) > 0:
            resultadoSQL = np.array(resultadoSQL)
            resultadoSQL = np.reshape(resultadoSQL, (resultadoSQL.shape[1], resultadoSQL.shape[2]) )
    finally:
            if cursor is not None:
                cursor.close()
    
    if len(resultadoSQL) > 0:
        
        """
        ID nuevas columnas agregadas a resultados SQL
        """
        
        ID_Ocio = 29
        ID_TiempoParqueo = 30
        ID_IdCamion = 31
        ID_IdConductor = 32
        ID_NumeroDeViaje = 33

        
        lineas = [ np.zeros(shape=(1, resultadoSQL.shape[1] ) ) for x in range(pLineas) ]
        
        #Partir la programacion segun la cantidad de lineas
        j = 0
        while j < len(resultadoSQL):
            for k in range(pLineas):
                
                if j < len(resultadoSQL):
                    l = resultadoSQL[j]
                    l = np.reshape(l, (1 , l.shape[0]))
                    lineas[k] = np.append(lineas[k], l, axis=0)
                    
                    j += 1
                
                
        #encolar los servicios y luego unirlo en una sola sabana de programacion
        for i in range(len(lineas)): 
            lineas[i] = encolarServicios(lineas[i])
            if i > 0:
                lineas[0] = np.concatenate((lineas[0], lineas[i]), axis = 0 )
        
        #paso el resultado a Dataframe para poder ordenarlo por hora de inicio de cargue porque por numpy no supe por donde
        resultadoSQL = pd.DataFrame( lineas[0] ).sort_values(16)
        #Vuelvo a convertirlo a numpy, solo que ya esta ordenado
        resultadoSQL = np.array(resultadoSQL)
        
        names.append('ocios')
        names.append('parqueos')

        
        """
        Asignacion de camiones
        """
        
        camiones = [
            {"Id": 0, "viajes": 0, "volumen": 0, "primerViaje": datetime.datetime(1, 1, 1, 0, 0), "ultimoRegreso": datetime.datetime(1, 1, 1, 0, 0) } ]
        
        camionesAsignados = np.array([])
        #flag para saber si el camion se asigno
        camion_asignado = False
        #Recorro la programacion para asignar camiones
        for i in range ( len(resultadoSQL) ):
            #reinicio del flag
            camion_asignado = False
            #recorro la base de camiones para asignar servicio a camion disponible
            for j in camiones:
                if datetime.datetime.combine(datetime.date.today(),resultadoSQL[i][16]) > j["ultimoRegreso"]:
                    #asigno el inicio de jornada
                    if j["primerViaje"] == datetime.datetime(1, 1, 1, 0, 0) : j["primerViaje"] = datetime.datetime.combine(datetime.date.today() , resultadoSQL[i][16] )
                    camionesAsignados = np.append(camionesAsignados, [ j["Id"]])
                    #HoraLlegadaPlantaSE
                    j["ultimoRegreso"] = datetime.datetime.combine(datetime.date.today(),resultadoSQL[i][26])
                    j["viajes"] += 1
                    j["volumen"] += resultadoSQL[i][4]
                    j["Centro"] = resultadoSQL[i][1]
                    camion_asignado = True
                    break
            #si no encuentro camiones disponibles agrego un nuevo camion
            if camion_asignado == False:
                camiones.append( {"Id": len(camiones) , "viajes": 1, "volumen": resultadoSQL[i][4],  "primerViaje": datetime.datetime.combine(datetime.date.today() ,resultadoSQL[i][16]), "ultimoRegreso": datetime.datetime.combine(datetime.date.today(),resultadoSQL[i][26]), "Centro": resultadoSQL[i][1] })
                camionesAsignados = np.append(camionesAsignados, [ len(camiones) - 1 ])
                
        camionesAsignados = np.reshape(camionesAsignados, (camionesAsignados.shape[0],1))
        #añado camiones asignados a cada viaje
        resultadoSQL = np.append(resultadoSQL, camionesAsignados, axis=1)
        
        names.append('IdCamion')
        
        """
        Asignacion de conductores
        """
        
        #Jornada maxima de trabajo en minutos
        minutosLabMax =  pJornada
        #Anticipacion llegada al primer cargue (en minutos)
        anticipacionConductores = pAnticipacionllegada
        
        conductores = [
            {"Id": 0, "viajes": 0, "volumen": 0, "llegadaPlanta": datetime.datetime(1, 1, 1, 0, 0),  "primerViaje": datetime.datetime(1, 1, 1, 0, 0), "ultimoRegreso": datetime.datetime(1, 1, 1, 0, 0) } ]
        
        conductoresAsignados = np.array([])
        viajeDelConductor = np.array([])
        
        #flag para saber si el conductor se asigno
        conductor_asignado = False
        #Recorro la programacion para asignar conductores
         
        for i in range ( len(resultadoSQL) ):
            #reinicio del flag
            conductor_asignado = False
            #recorro la base de conductores para asignar servicio a conductor disponible
            for j in conductores:
                if datetime.datetime.combine(datetime.date.today(),resultadoSQL[i][16]) > j["ultimoRegreso"] and ( j["primerViaje"] == datetime.datetime(1, 1, 1, 0, 0) or  datetime.datetime.combine(datetime.date.today(), resultadoSQL[i][26]) - j["primerViaje"] < datetime.timedelta(minutes=minutosLabMax) ) :
                    
                    if j["primerViaje"] == datetime.datetime(1, 1, 1, 0, 0) : 
                        #Asigno llegada del conductor
                        j["llegadaPlanta"] = datetime.datetime.combine(datetime.date.today() , resultadoSQL[i][16]) - datetime.timedelta(minutes = anticipacionConductores)
                        #asigno el inicio de jornada
                        j["primerViaje"] = datetime.datetime.combine(datetime.date.today() , resultadoSQL[i][16] )
                        
                    #Agrego el id de conductores a la columna para identificar que conductor debe llevar el viaje    
                    conductoresAsignados = np.append(conductoresAsignados, [ j["Id"]])
                    
                    #Agrego el numero de viaje de ese conductor
                    viajeDelConductor = np.append(viajeDelConductor, j["viajes"] + 1 )
                    #HoraLlegadaPlantaSE
                    j["ultimoRegreso"] = datetime.datetime.combine(datetime.date.today(),resultadoSQL[i][26])
                    j["viajes"] += 1
                    j["volumen"] += resultadoSQL[i][4]
                    j["Centro"] = resultadoSQL[i][1]
                    j["Tipo"] = "Normal"
                    conductor_asignado = True
                    break
            #si no encuentro conductores disponibles agrego un nuevo conductor
            if conductor_asignado == False:
                conductores.append( {"Id": len(conductores) , "viajes": 1, "volumen": resultadoSQL[i][4], "llegadaPlanta": datetime.datetime.combine(datetime.date.today() , resultadoSQL[i][16]) - datetime.timedelta(minutes = anticipacionConductores) , "primerViaje": datetime.datetime.combine(datetime.date.today() , resultadoSQL[i][16]), "ultimoRegreso": datetime.datetime.combine(datetime.date.today(),resultadoSQL[i][26]), "Centro": resultadoSQL[i][1], "Tipo":"Normal" })
                conductoresAsignados = np.append(conductoresAsignados, [ len(conductores) - 1 ])
                
                #Agrego el numero de viaje de ese conductor
                viajeDelConductor = np.append(viajeDelConductor, j["viajes"] )
                
        conductoresAsignados = np.reshape(conductoresAsignados, (conductoresAsignados.shape[0],1))
        viajeDelConductor = np.reshape(viajeDelConductor, (viajeDelConductor.shape[0],1))
        
        #añado camiones asignados a cada viaje
        resultadoSQL = np.append(resultadoSQL, conductoresAsignados, axis=1)
        resultadoSQL = np.append(resultadoSQL, viajeDelConductor, axis=1)

        names.append('IdConductor')
        names.append('No. Viaje')
        
        """
        Algoritmo de precague
        """
        if noPrecargadores > 0:
            terminarAlgoritmo = False
            hrLlegadaPrecargador = conductores[0]["llegadaPlanta"]
            iteradorProgramacion = 0
            tiempoAcumuladoPrecargador = 0
            tiempoMinimoPrecargando = datetime.timedelta(minutes = tiempoPrecargando)
            
            while iteradorProgramacion < len(resultadoSQL) and terminarAlgoritmo == False:
                for i in range (len(conductores) - 1 ):
                    if resultadoSQL[iteradorProgramacion][ID_IdConductor] == conductores[i]["Id"] and resultadoSQL[iteradorProgramacion][ID_NumeroDeViaje] == 1:
                        #La nueva hora de llegada del conductor va a ser su hora de salida menos el tiempo de anticipacion de llegada a su primer cargue
                        conductores[i]["llegadaPlanta"] = (datetime.datetime.combine(datetime.date.today(),resultadoSQL[iteradorProgramacion][20] ) - datetime.timedelta(minutes = anticipacionConductores) )
                        #El siguiente conductor es el candidato  a precargador, asi que calculo cuanto tiempo estaria pre-cargando
                        tiempoAcumuladoPrecargador = conductores[i + 1]["llegadaPlanta"] -  hrLlegadaPrecargador 
                        #si ese tiempo supera el minimo, ya encontre al precargador
                        if tiempoAcumuladoPrecargador > tiempoMinimoPrecargando:
                            for k in range(noPrecargadores):
                                if i + k + 1 < len(conductores):
                                    conductores[i+k+1]["llegadaPlanta"] = hrLlegadaPrecargador - datetime.timedelta(minutes = 40)
                                    conductores[i+k+1]["Tipo"] = "Precargador"
                            terminarAlgoritmo = True
                        break
                iteradorProgramacion += 1
        
        
        #Ajuste final para que se vea bien el la hora
        for i in conductores:
            #i["Jornada"] =  (datetime.datetime.min + (i["ultimoRegreso"] - i["llegadaPlanta"])).time()
            i["llegadaPlanta"] = i["llegadaPlanta"].time()
            i["primerViaje"] = i["primerViaje"].time()
            i["ultimoRegreso"] = i["ultimoRegreso"].time()
            
                    
        for i in camiones:
            i["primerViaje"] = i["primerViaje"].time()
            i["ultimoRegreso"] = i["ultimoRegreso"].time()
        
        
        """
        Información para el asignador
        """ 
        infoAsignaciones = []
        llegadaPlantaAS = np.array([])
        
        llegadaConductrorInfoAsignacion = resultadoSQL[1][ID_IdConductor]
        for i in resultadoSQL:
            for j in conductores:
                if i[ID_IdConductor] == j["Id"] : 
                    llegadaConductrorInfoAsignacion = j["llegadaPlanta"]
                    break
                
            infoAsignaciones.append({"Pedido": i[2], "Servicio":i[3], "HrEntrega":i[8], "InicioCargue":i[16], "Obra": i[6], "LlegadaPlantaAS": llegadaConductrorInfoAsignacion, "Volumen": i[4], "IdConductor":i[ID_IdConductor], "CondLogisticas":i[28]})    
            #Informacion para la malla a nivel de datalle, para guardar la llegada del as en el SQL
            llegadaPlantaAS = np.append(llegadaPlantaAS, [llegadaConductrorInfoAsignacion] )
        
        llegadaPlantaAS = np.reshape(llegadaPlantaAS, (llegadaPlantaAS.shape[0],1))
        resultadoSQL = np.append(resultadoSQL, llegadaPlantaAS, axis=1)
        names.append('llegadaPlantaAS')
        
        #Grilla final
        
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        
            
        #writer = pd.ExcelWriter("MallaTurnos_Programacion" + planta + fechaEntrega + ".xlsx", engine='xlsxwriter')
        
        programacion = pd.DataFrame(resultadoSQL, columns = names)
        programacion.to_excel( writer, sheet_name="Malla" )
            
        camionesAsignadosDF = pd.DataFrame(camiones)
        camionesAsignadosDF.to_excel( writer, sheet_name="Camiones" )
        
        conductoresAsignadosDF = pd.DataFrame(conductores)
        conductoresAsignadosDF.to_excel( writer, sheet_name="Conductores" )
        
        infoAsignacionesDF = pd.DataFrame(infoAsignaciones)
        infoAsignacionesDF.to_excel( writer, sheet_name="InfoAsignaciones" )
        
        #writer.save()
        #"""
        writer.close()
        output.seek(0)
        #"""        
        
        df_toSQL = pd.DataFrame(programacion[[ 'Centro','Pedido','Servicio', 'Volumen',	'Obra',	'NombreObra',	'FechaEntrega',	'HoraEntrega',	'EstatusPosicion',	'Posicion',	'TCargue',	'TAlistamiento',	'TIda',	'TObra',	'TRegreso',	'HoraInicioCargueSE',	'HoraFinCargueSE',	'HoraSalidaSE',	'LlegadaObra',	'HoraSalidaDeObraSE',	'HoraLlegadaPlantaSE',	'ofertaLogisticaObra', 'IdCamion', 'IdConductor', 'llegadaPlantaAS']])
        df_toSQL['Version'] =  pd.to_datetime("now").strftime("%Y-%m-%d-%H-%M-%S")
        
        params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};SERVER=USCLDBITVMP01;DATABASE=BI_Tableau;UID=usertableau;PWD=usertableau$")
        engine = sa.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
        
        df_toSQL.to_sql("SCAC_AT32_MallaTurnos", engine, index=False, if_exists="append", schema="dbo")
        
        return send_file(path_or_file=output, download_name="MallaTurnos_Programacion" + planta + fechaEntrega + ".xlsx", as_attachment=True)

def obtenerPlantasCentrales(planta):
    #Conectar con base sql y ejecutar consulta
    cursor = conectarSQL()
    try:
        cursor.execute("{CALL SCAC_AP6_PlantasCentrales (?)}" , (planta) )
        #Reunir todos los resultado en rows
        rows = cursor.fetchall()
        resultadoPlantas = []
            
        #Hacer un array con los resultados
        while rows:
            resultadoPlantas.append(rows)
            if cursor.nextset():
                rows = cursor.fetchall()
            else:
                rows = None
        #Redimensionar el array para que quede en dos dimensiones
        resultadoPlantas = np.array(resultadoPlantas)
        resultadoPlantas = np.reshape(resultadoPlantas, (resultadoPlantas.shape[1], resultadoPlantas.shape[2]) )
    finally:
            if cursor is not None:
                cursor.close()
    return resultadoPlantas


"""
plantasCentrales = obtenerPlantasCentrales("Colombia")

for i in plantasCentrales:
    generarMalla(i[0], int(i[1]),"2020-08-03", 2, 60, 660, 20)

"""


# parametros: pPlanta, pLineas, pFecha, noPrecargadores, tiempoPrecargando, pJornada, pAnticipacionllegada
    
#generarMalla("CO-PLANTA TOCANCIPA", 1, "2020-08-20", 3, 20, 660, 25)
#generarMalla("CO-PLANTA SOACHA", 1, "2020-08-20", 0, 20, 660, 25)

#generarMalla("CO-PLANTA NEIVA", 1, "2020-08-20", 0, 20, 660, 20)
#generarMalla("CO-PLANTA CALI", 1, "2020-08-20", 0, 20, 660, 20)

#generarMalla("CO-PLANTA BELLO", 1, "2020-08-20", 0, 20, 660, 30)

#""""


def generarm( planta,fecha, precargadores, jornada, anticipacion, paramrandom):
   
    plantaDecode =  urllib.parse.unquote(planta)
    infoPlanta = obtenerPlantasCentrales(plantaDecode) 
    return generarMalla( plantaDecode ,int(infoPlanta[0][1]), fecha, int(precargadores), 20, int(jornada), int(anticipacion))


def generarm2( planta,fecha, precargadores, jornada, anticipacion, paramrandom, tp):
   
    plantaDecode =  urllib.parse.unquote(planta)
    infoPlanta = obtenerPlantasCentrales(plantaDecode) 
    return generarMalla2( plantaDecode ,int(infoPlanta[0][1]), fecha, int(precargadores), 20, int(jornada), int(anticipacion), tp)


"""
parametros:
    
    pPlanta: Nombre de la planta unica 
    pLineas: Numero de lineas que tiene esa planta
    pFecha: Fecha de la programación que se quiere procesar
    
    noPrecargadores: Número de conductores que va a realizar el precargue, si es 0 se entiende que no tiene precargadores
    tiempoPrecargando: Tiempo en minutos que un precargador antes de salir con su primer viaje
    
    pJornada: Jornada maxima de un conductor en minutos
    pAnticipacionllegada: Minutos de anticipacion de llegada de los conductores antes de su primer viaje
    
    tipoPedidos: 1-> programacion confirmada 2 -> Programacion no confirmada
    
"""

def generarMalla2(pPlanta, pLineas, pFecha, noPrecargadores, tiempoPrecargando, pJornada, pAnticipacionllegada, tipoPedidos):
    #Conectar con base sql y ejecutar consulta
    cursor = conectarSQL()
    
    #planta = "CO-PLANTA PUENTE ARANDA"
    #fechaEntrega = "2020-07-03"
    planta = pPlanta
    fechaEntrega = pFecha
    try:
        if(tipoPedidos == 1):
            cursor.execute("{CALL SCAC_AP5_MallaTurnos_SinEncolar (?,?)}" , (planta, fechaEntrega) )
        else:
            cursor.execute("{CALL SCAC_AP5_MallaTurnos_SinEncolar_NoConfirmada (?,?)}" , (planta, fechaEntrega) )
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
        if len(resultadoSQL) > 0:
            resultadoSQL = np.array(resultadoSQL)
            resultadoSQL = np.reshape(resultadoSQL, (resultadoSQL.shape[1], resultadoSQL.shape[2]) )
    finally:
            if cursor is not None:
                cursor.close()
    
    if len(resultadoSQL) > 0:
        
        """
        ID nuevas columnas agregadas a resultados SQL
        """
        
        ID_Ocio = 29
        ID_TiempoParqueo = 30
        ID_IdCamion = 31
        ID_IdConductor = 32
        ID_NumeroDeViaje = 33

        
        lineas = [ np.zeros(shape=(1, resultadoSQL.shape[1] ) ) for x in range(pLineas) ]
        
        #Partir la programacion segun la cantidad de lineas
        j = 0
        while j < len(resultadoSQL):
            for k in range(pLineas):
                
                if j < len(resultadoSQL):
                    l = resultadoSQL[j]
                    l = np.reshape(l, (1 , l.shape[0]))
                    lineas[k] = np.append(lineas[k], l, axis=0)
                    
                    j += 1
                
                
        #encolar los servicios y luego unirlo en una sola sabana de programacion
        for i in range(len(lineas)): 
            lineas[i] = encolarServicios(lineas[i])
            if i > 0:
                lineas[0] = np.concatenate((lineas[0], lineas[i]), axis = 0 )
        
        #paso el resultado a Dataframe para poder ordenarlo por hora de inicio de cargue porque por numpy no supe por donde
        resultadoSQL = pd.DataFrame( lineas[0] ).sort_values(16)
        #Vuelvo a convertirlo a numpy, solo que ya esta ordenado
        resultadoSQL = np.array(resultadoSQL)
        
        names.append('ocios')
        names.append('parqueos')

        
        """
        Asignacion de camiones
        """
        
        camiones = [
            {"Id": 0, "viajes": 0, "volumen": 0, "primerViaje": datetime.datetime(1, 1, 1, 0, 0), "ultimoRegreso": datetime.datetime(1, 1, 1, 0, 0) } ]
        
        camionesAsignados = np.array([])
        #flag para saber si el camion se asigno
        camion_asignado = False
        #Recorro la programacion para asignar camiones
        for i in range ( len(resultadoSQL) ):
            #reinicio del flag
            camion_asignado = False
            #recorro la base de camiones para asignar servicio a camion disponible
            for j in camiones:
                if datetime.datetime.combine(datetime.date.today(),resultadoSQL[i][16]) > j["ultimoRegreso"]:
                    #asigno el inicio de jornada
                    if j["primerViaje"] == datetime.datetime(1, 1, 1, 0, 0) : j["primerViaje"] = datetime.datetime.combine(datetime.date.today() , resultadoSQL[i][16] )
                    camionesAsignados = np.append(camionesAsignados, [ j["Id"]])
                    #HoraLlegadaPlantaSE
                    j["ultimoRegreso"] = datetime.datetime.combine(datetime.date.today(),resultadoSQL[i][26])
                    j["viajes"] += 1
                    j["volumen"] += resultadoSQL[i][4]
                    j["Centro"] = resultadoSQL[i][1]
                    camion_asignado = True
                    break
            #si no encuentro camiones disponibles agrego un nuevo camion
            if camion_asignado == False:
                camiones.append( {"Id": len(camiones) , "viajes": 1, "volumen": resultadoSQL[i][4],  "primerViaje": datetime.datetime.combine(datetime.date.today() ,resultadoSQL[i][16]), "ultimoRegreso": datetime.datetime.combine(datetime.date.today(),resultadoSQL[i][26]), "Centro": resultadoSQL[i][1] })
                camionesAsignados = np.append(camionesAsignados, [ len(camiones) - 1 ])
                
        camionesAsignados = np.reshape(camionesAsignados, (camionesAsignados.shape[0],1))
        #añado camiones asignados a cada viaje
        resultadoSQL = np.append(resultadoSQL, camionesAsignados, axis=1)
        
        names.append('IdCamion')
        
        """
        Asignacion de conductores
        """
        
        #Jornada maxima de trabajo en minutos
        minutosLabMax =  pJornada
        #Anticipacion llegada al primer cargue (en minutos)
        anticipacionConductores = pAnticipacionllegada
        
        conductores = [
            {"Id": 0, "viajes": 0, "volumen": 0, "llegadaPlanta": datetime.datetime(1, 1, 1, 0, 0),  "primerViaje": datetime.datetime(1, 1, 1, 0, 0), "ultimoRegreso": datetime.datetime(1, 1, 1, 0, 0) } ]
        
        conductoresAsignados = np.array([])
        viajeDelConductor = np.array([])
        
        #flag para saber si el conductor se asigno
        conductor_asignado = False
        #Recorro la programacion para asignar conductores
         
        for i in range ( len(resultadoSQL) ):
            #reinicio del flag
            conductor_asignado = False
            #recorro la base de conductores para asignar servicio a conductor disponible
            for j in conductores:
                if datetime.datetime.combine(datetime.date.today(),resultadoSQL[i][16]) > j["ultimoRegreso"] and ( j["primerViaje"] == datetime.datetime(1, 1, 1, 0, 0) or  datetime.datetime.combine(datetime.date.today(), resultadoSQL[i][26]) - j["primerViaje"] < datetime.timedelta(minutes=minutosLabMax) ) :
                    
                    if j["primerViaje"] == datetime.datetime(1, 1, 1, 0, 0) : 
                        #Asigno llegada del conductor
                        j["llegadaPlanta"] = datetime.datetime.combine(datetime.date.today() , resultadoSQL[i][16]) - datetime.timedelta(minutes = anticipacionConductores)
                        #asigno el inicio de jornada
                        j["primerViaje"] = datetime.datetime.combine(datetime.date.today() , resultadoSQL[i][16] )
                        
                    #Agrego el id de conductores a la columna para identificar que conductor debe llevar el viaje    
                    conductoresAsignados = np.append(conductoresAsignados, [ j["Id"]])
                    
                    #Agrego el numero de viaje de ese conductor
                    viajeDelConductor = np.append(viajeDelConductor, j["viajes"] + 1 )
                    #HoraLlegadaPlantaSE
                    j["ultimoRegreso"] = datetime.datetime.combine(datetime.date.today(),resultadoSQL[i][26])
                    j["viajes"] += 1
                    j["volumen"] += resultadoSQL[i][4]
                    j["Centro"] = resultadoSQL[i][1]
                    j["Tipo"] = "Normal"
                    conductor_asignado = True
                    break
            #si no encuentro conductores disponibles agrego un nuevo conductor
            if conductor_asignado == False:
                conductores.append( {"Id": len(conductores) , "viajes": 1, "volumen": resultadoSQL[i][4], "llegadaPlanta": datetime.datetime.combine(datetime.date.today() , resultadoSQL[i][16]) - datetime.timedelta(minutes = anticipacionConductores) , "primerViaje": datetime.datetime.combine(datetime.date.today() , resultadoSQL[i][16]), "ultimoRegreso": datetime.datetime.combine(datetime.date.today(),resultadoSQL[i][26]), "Centro": resultadoSQL[i][1], "Tipo":"Normal" })
                conductoresAsignados = np.append(conductoresAsignados, [ len(conductores) - 1 ])
                
                #Agrego el numero de viaje de ese conductor
                viajeDelConductor = np.append(viajeDelConductor, j["viajes"] )
                
        conductoresAsignados = np.reshape(conductoresAsignados, (conductoresAsignados.shape[0],1))
        viajeDelConductor = np.reshape(viajeDelConductor, (viajeDelConductor.shape[0],1))
        
        #añado camiones asignados a cada viaje
        resultadoSQL = np.append(resultadoSQL, conductoresAsignados, axis=1)
        resultadoSQL = np.append(resultadoSQL, viajeDelConductor, axis=1)

        names.append('IdConductor')
        names.append('No. Viaje')
        
        """
        Algoritmo de precague
        """
        if noPrecargadores > 0:
            terminarAlgoritmo = False
            hrLlegadaPrecargador = conductores[0]["llegadaPlanta"]
            iteradorProgramacion = 0
            tiempoAcumuladoPrecargador = 0
            tiempoMinimoPrecargando = datetime.timedelta(minutes = tiempoPrecargando)
            
            while iteradorProgramacion < len(resultadoSQL) and terminarAlgoritmo == False:
                for i in range (len(conductores) - 1 ):
                    if resultadoSQL[iteradorProgramacion][ID_IdConductor] == conductores[i]["Id"] and resultadoSQL[iteradorProgramacion][ID_NumeroDeViaje] == 1:
                        #La nueva hora de llegada del conductor va a ser su hora de salida menos el tiempo de anticipacion de llegada a su primer cargue
                        conductores[i]["llegadaPlanta"] = (datetime.datetime.combine(datetime.date.today(),resultadoSQL[iteradorProgramacion][20] ) - datetime.timedelta(minutes = anticipacionConductores) )
                        #El siguiente conductor es el candidato  a precargador, asi que calculo cuanto tiempo estaria pre-cargando
                        tiempoAcumuladoPrecargador = conductores[i + 1]["llegadaPlanta"] -  hrLlegadaPrecargador 
                        #si ese tiempo supera el minimo, ya encontre al precargador
                        if tiempoAcumuladoPrecargador > tiempoMinimoPrecargando:
                            for k in range(noPrecargadores):
                                if i + k + 1 < len(conductores):
                                    conductores[i+k+1]["llegadaPlanta"] = hrLlegadaPrecargador - datetime.timedelta(minutes = 40)
                                    conductores[i+k+1]["Tipo"] = "Precargador"
                            terminarAlgoritmo = True
                        break
                iteradorProgramacion += 1
        
        
        #Ajuste final para que se vea bien el la hora
        for i in conductores:
            #i["Jornada"] =  (datetime.datetime.min + (i["ultimoRegreso"] - i["llegadaPlanta"])).time()
            i["llegadaPlanta"] = i["llegadaPlanta"].time()
            i["primerViaje"] = i["primerViaje"].time()
            i["ultimoRegreso"] = i["ultimoRegreso"].time()
            
                    
        for i in camiones:
            i["primerViaje"] = i["primerViaje"].time()
            i["ultimoRegreso"] = i["ultimoRegreso"].time()
        
        
        """
        Información para el asignador
        """ 
        infoAsignaciones = []
        llegadaPlantaAS = np.array([])
        
        llegadaConductrorInfoAsignacion = resultadoSQL[1][ID_IdConductor]
        for i in resultadoSQL:
            for j in conductores:
                if i[ID_IdConductor] == j["Id"] : 
                    llegadaConductrorInfoAsignacion = j["llegadaPlanta"]
                    break
                
            infoAsignaciones.append({"Pedido": i[2], "Servicio":i[3], "HrEntrega":i[8], "InicioCargue":i[16], "Obra": i[6], "LlegadaPlantaAS": llegadaConductrorInfoAsignacion, "Volumen": i[4], "IdConductor":i[ID_IdConductor], "CondLogisticas":i[28]})    
            #Informacion para la malla a nivel de datalle, para guardar la llegada del as en el SQL
            llegadaPlantaAS = np.append(llegadaPlantaAS, [llegadaConductrorInfoAsignacion] )
        
        llegadaPlantaAS = np.reshape(llegadaPlantaAS, (llegadaPlantaAS.shape[0],1))
        resultadoSQL = np.append(resultadoSQL, llegadaPlantaAS, axis=1)
        names.append('llegadaPlantaAS')
        
        #Grilla final
        
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        
            
        #writer = pd.ExcelWriter("MallaTurnos_Programacion" + planta + fechaEntrega + ".xlsx", engine='xlsxwriter')
        
        programacion = pd.DataFrame(resultadoSQL, columns = names)
        programacion.to_excel( writer, sheet_name="Malla" )
            
        camionesAsignadosDF = pd.DataFrame(camiones)
        camionesAsignadosDF.to_excel( writer, sheet_name="Camiones" )
        
        conductoresAsignadosDF = pd.DataFrame(conductores)
        conductoresAsignadosDF.to_excel( writer, sheet_name="Conductores" )
        
        infoAsignacionesDF = pd.DataFrame(infoAsignaciones)
        infoAsignacionesDF.to_excel( writer, sheet_name="InfoAsignaciones" )
        
        #writer.save()
        #"""
        writer.close()
        output.seek(0)
        #"""        
        
        """
        df_toSQL = pd.DataFrame(programacion[[ 'Centro','Pedido','Servicio', 'Volumen',	'Obra',	'NombreObra',	'FechaEntrega',	'HoraEntrega',	'EstatusPosicion',	'Posicion',	'TCargue',	'TAlistamiento',	'TIda',	'TObra',	'TRegreso',	'HoraInicioCargueSE',	'HoraFinCargueSE',	'HoraSalidaSE',	'LlegadaObra',	'HoraSalidaDeObraSE',	'HoraLlegadaPlantaSE',	'ofertaLogisticaObra', 'IdCamion', 'IdConductor', 'llegadaPlantaAS']])
        df_toSQL['Version'] =  pd.to_datetime("now").strftime("%Y-%m-%d-%H-%M-%S")
        
        params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};SERVER=COOCCAPP11A;DATABASE=BI_Tableau;UID=usertableau;PWD=usertableau$")
        engine = sa.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
        
        df_toSQL.to_sql("SCAC_AT32_MallaTurnos", engine, index=False, if_exists="append", schema="dbo")
        """
        
        return send_file(path_or_file=output, download_name="MallaTurnos_Programacion" + planta + fechaEntrega + ".xlsx", as_attachment=True)
