#libraries
from datetime import datetime
import timeit
import warnings
warnings.filterwarnings('ignore')
import sys
from dateutil.relativedelta import relativedelta
#our own py scripts
#insert path to get help files 
#sys.path.insert(0, r'C:\Users\snortiz\Documents\projects\sld\ranking\santo_domingo')
sys.path.insert(0, r'C:\Users\jsdelgadoc\Documents\Proyectos-Cemex\sld_v2\ranking\santo_domingo')
#current_folder = os.getcwd() #get current working directory
#sys.path.insert(0, current_folder+'\ranking')

from help_files_santodom.sql_santodom.connect_sql_server import query_sql_df
from help_files_santodom.clean_data_santodom.clean_data import clean_data
from help_files_santodom.send_to_excel_santodom.send_to_excel import send_to_excel
from help_files_santodom.functions_santodom.functions import *


#run program
try:
    def main_santodom(cluster,paramrandom):
         
        #get current date        
        today_date_dt = datetime.now()              
    
        #RUN ALL FUNCTIONS

        #get client list from last 3 months
        get_clients_df = get_clients(cluster,today_date_dt,relativedelta,query_sql_df)


        #run for volumen attribute
        volumen_attribute_df = volumen_attribute(cluster,today_date_dt,relativedelta,query_sql_df)

        #run for profits
        #profits_attribute_df = profits_attribute(query_sql_df,get_clients_df)
    
        #run for payment discipline
        payment_discipline_attribute_df = payment_discipline_attribute(query_sql_df)
            
        #run for cancelations
        cancelations_attribute_df = cancelations_attribute(cluster,query_sql_df,get_clients_df)

        #run for fidelity
        fidelity_attribute_df = fidelity_attribute(query_sql_df,get_clients_df)

        #clean data to get final DF
        x = clean_data(get_clients_df,volumen_attribute_df,
                       payment_discipline_attribute_df,fidelity_attribute_df,cancelations_attribute_df)
 

        #send to excel file
        return send_to_excel(x)

        

    
    
except Exception as e:
    print(str(e))
    sys.exit()

