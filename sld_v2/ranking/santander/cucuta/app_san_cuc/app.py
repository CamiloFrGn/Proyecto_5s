#libraries
from datetime import datetime, timedelta
import timeit
import warnings
warnings.filterwarnings('ignore')
import sys
import os
from dateutil.relativedelta import relativedelta
#our own py scripts
#insert path to get help files 
#sys.path.insert(0, r'C:\Users\snortiz\Documents\projects\sld\ranking\santander\cucuta')
sys.path.insert(0, r'C:\Users\jsdelgadoc\Documents\Proyectos-Cemex\sld_v2\ranking\santander\cucuta')
from help_files_san_cuc.sql_san_cuc.connect_sql_server import query_sql_df
from help_files_san_cuc.clean_data_san_cuc.clean_data import clean_data
from help_files_san_cuc.send_to_excel_san_cuc.send_to_excel import send_to_excel
from help_files_san_cuc.functions_san_cuc.functions import *


#run program
try:
    def main_cucuta(plant):
         
       
        #get current date        
        today_date_dt = datetime.now()              
    
        #RUN ALL FUNCTIONS

        #get client list from last 3 months
        get_clients_df = get_clients(plant,today_date_dt,relativedelta,query_sql_df)
  

        #run for volumen attribute
        volumen_attribute_df = volumen_attribute(plant,query_sql_df)

        #run for profits
        profits_attribute_df = profits_attribute(query_sql_df,get_clients_df)
   
        #run for payment discipline
        payment_discipline_attribute_df = payment_discipline_attribute(query_sql_df)
        
        #run for brand visibility and brand growth potential
        brandvis_growthpot_attribute_df = brandvis_growthpot_attribute(query_sql_df)
        
        #run for fidelity
        fidelity_attribute_df = fidelity_attribute(query_sql_df,get_clients_df)
        
        #run for fidelity integrated
        fidelity_integrated_attribute_df = fidelity_integrated_attribute(query_sql_df,get_clients_df)

        #run for bran permanence
        brand_permanence_attribute_df = brand_permanence_attribute(plant,query_sql_df,get_clients_df)

        #run for value proposition
        value_proposition_attribute_df = value_proposition_attribute(query_sql_df,get_clients_df)

        #run for unload zone safety measures
        unload_zone_safety_attribute_df = unload_zone_safety_attribute(query_sql_df)

        #run for cancelations
        cancelations_attribute_df = cancelations_attribute(plant,query_sql_df,get_clients_df)
            
        #run for average site time
        time_in_site_attribute_df = time_in_site_attribute(plant,today_date_dt,relativedelta,query_sql_df)

        #clean data to get final DF
        x = clean_data(get_clients_df,volumen_attribute_df,
                       time_in_site_attribute_df,profits_attribute_df,brandvis_growthpot_attribute_df,
                       payment_discipline_attribute_df,unload_zone_safety_attribute_df,fidelity_attribute_df,\
                        fidelity_integrated_attribute_df,brand_permanence_attribute_df,value_proposition_attribute_df,\
                            cancelations_attribute_df)
        

        #send to excel file
        x = send_to_excel(x)

        return x


    
except Exception as e:
    print(str(e))
    sys.exit()

