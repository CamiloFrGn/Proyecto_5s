#libraries
from datetime import datetime
import timeit
import warnings
warnings.filterwarnings('ignore')
import sys
import os
#our own py scripts
#insert path to get help files 
#sys.path.insert(0, r'C:\Users\jsdelgadoc\Documents\Proyectos-Cemex\sap_extraction\consu_ticket')
current_folder = os.getcwd() #get current working directory
sys.path.insert(0, current_folder+'\disorganized_clients')
from help_files.sql.connect_sql_server import query_sql_df
from help_files.clean_data.clean_data import clean_data
from help_files.send_to_excel.send_to_excel import send_to_excel

#run program
try:
    def main():
        
       
        print("RUNNING PROGRAM FOR DISORGANIZED CLIENTS")
        #start timer for runtime
        start = timeit.default_timer()
        #get current date        
        today_date = datetime.now()              
        today_date = today_date.strftime("%Y-%m-%d") #convert to format for dataframe filter
        #parameters
        country = "Colombia"
        startdate = "2023-01-01" #must be year-month-day
        enddate = "2023-03-15"
        cluster = "CLUSTER SANTANDER"
        #get dataset
        dataset = query_sql_df("{call scac_ap2_so_desorganizedclientes (?,?,?,?)}",
                                   (country,startdate,enddate,cluster))
        dataset_clients = query_sql_df("select distinct trim(cliente) as Cliente, trim(nombrecliente) \
                                       as NombreCliente \
                                       from SCAC_AT2_CondensadoServicio as cd inner join \
                                       SCAC_AT1_NombreCluster as nc \
                                       on  cd.Planta = nc.Centro where nc.Pais = ? and \
                                       nc.[Desc Cluster] = '"+cluster+"' and \
                                       FechaEntrega between ? and ?", (country,startdate,enddate))
        #clean data
        df = clean_data(dataset,dataset_clients)
        #send to excel
        send_to_excel(df)
    
        #print info to cmd
        stop = timeit.default_timer()
        runtime = ((stop - start)/60)
        print('Runtime: ', str(runtime)+" minutes") 
        print("-------------------------------")

    main()
    
except Exception as e:
    print(str(e))
    sys.exit()

