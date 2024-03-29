#libraries
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
import sys
from dateutil.relativedelta import relativedelta
#our own py scripts
#insert path to get help files 
#sys.path.insert(0, r'C:\Users\snortiz\Documents\projects\sld\ranking\antioquia')
sys.path.insert(0, r'C:\Users\snortiz\Documents\projects\Proyectos-Cemex\otros\proyectos_cemex\sld_v2\ranking\antioquia')

from help_files_an.sql_an.connect_sql_server import query_sql_df
from help_files_an.clean_data_an.clean_data import clean_data
from help_files_an.send_to_excel_an.send_to_excel import send_to_excel
from help_files_an.functions_an.functions import *


#run program
try:
    def main_antioquia(cluster,paramrandom):
         
        #get current date        
        today_date_dt = datetime.now()              
    
        #RUN ALL FUNCTIONS

        
        #get client list from last 3 months
        get_clients_df = get_clients(cluster,today_date_dt,relativedelta,query_sql_df)

        

        #run for volumen attribute
        volumen_attribute_df = volumen_attribute(cluster,today_date_dt,relativedelta,query_sql_df)

        

        #run for profits
        profits_attribute_df = profits_attribute(query_sql_df,get_clients_df)

        

        #run for payment discipline
        payment_discipline_attribute_df = payment_discipline_attribute(query_sql_df)
            
        #run for average site time
        time_in_site_attribute_df = time_in_site_attribute(cluster,today_date_dt,relativedelta,query_sql_df)

        #use of tools
        tools_adoption_attribute_df = tools_adoption_attribute(query_sql_df,get_clients_df)

        #fidelity
        fidelity_attribute_df = fidelity_attribute(query_sql_df,get_clients_df)

        

        #clean data to get final DF
        x = clean_data(get_clients_df,volumen_attribute_df,
                       time_in_site_attribute_df,profits_attribute_df,
                       payment_discipline_attribute_df,fidelity_attribute_df,tools_adoption_attribute_df)
        
   

        return send_to_excel(x)
    
except Exception as e:
    print(str(e))
    sys.exit()

