#libraries
from datetime import datetime
import timeit
import warnings
warnings.filterwarnings('ignore')
import sys
from dateutil.relativedelta import relativedelta
import os
current_dir = os.getcwd()
path_file = r"Documents\Proyectos-Cemex\sld_v2\ranking_country"
current_dir = os.path.join(current_dir,path_file)
# Define the relative path to the data directory
data_dir = os.path.join(current_dir, 'panama\juan_diaz')
print(data_dir)
#our own py scripts
#insert path to get help files 
sys.path.insert(0, data_dir)
from help_files_juandiaz.sql_juandiaz.connect_sql_server import *
from help_files_juandiaz.clean_data_juandiaz.clean_data import clean_data
from help_files_juandiaz.send_to_excel_juandiaz.send_to_excel import send_to_excel
from help_files_juandiaz.functions_juandiaz.functions import *



#run program
try:
    def main_juandiaz(plant):
         
        #get current date        
        today_date_dt = datetime.now()              
    
        #RUN ALL FUNCTIONS

        #get client list from last 3 months
        get_clients_df = get_clients(plant,today_date_dt,relativedelta,query_sql_df)

        #run for volumen attribute
        volumen_attribute_df = volumen_attribute(plant,today_date_dt,relativedelta,query_sql_df)

        #run for profits
        profits_attribute_df = profits_attribute(query_sql_df,get_clients_df)
            
        #run for cancelations
        cancelations_attribute_df = cancelations_attribute(plant,query_sql_df,get_clients_df)

        #run for fidelity integrated
        fidelity_integrated_attribute_df = fidelity_integrated_attribute(query_sql_df,get_clients_df)

        #run for payment discipline
        payment_discipline_attribute_df = payment_discipline_attribute(query_sql_df)

        #use of tools
        tools_adoption_attribute_df = tools_adoption_attribute(query_sql_df,get_clients_df)

        plant = 'PA-PLANTA JUAN DIAZ'
        cluster = 'CLUSTER PANAMA'
        #clean data to get final DF
        x = clean_data(get_clients_df,volumen_attribute_df,cancelations_attribute_df,
        profits_attribute_df,fidelity_integrated_attribute_df,payment_discipline_attribute_df,tools_adoption_attribute_df,cluster,plant)
 


        #delete data and send to sql
        database_name = "SCAC_AT51_SLDClientes_teorico"
        sql_statement = "delete from "+database_name+" where planta = ?"
        
        query_sql_crud(sql_statement,(plant))
        send_df_to_sql(x,database_name)
    

        

    

except Exception as e:
    print(str(e))
    sys.exit()



