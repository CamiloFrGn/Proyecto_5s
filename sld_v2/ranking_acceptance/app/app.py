#libraries
from datetime import datetime, timedelta
import time
import timeit
import warnings
warnings.filterwarnings('ignore')
import sys
import schedule
#our own py scripts
#insert path to get help files 
sys.path.insert(0, r'C:\Users\snortiz\Documents\projects\sld\ranking_acceptance')
from help_files.sql.connect_sql_server import query_sql_crud, send_df_to_sql
from help_files.clean_data.clean_data import clean_data

#run program
try:
    def main():
        print("RUNNING PROGRAM FOR RANKING ACCEPTENCE")
        #start timer for runtime
        start = timeit.default_timer()
                
        
        stop = timeit.default_timer()
        runtime = ((stop - start)/60)
        print('Runtime: ', str(runtime)+" minutes") 
        print("-------------------------------")




    main()
    #schedule.every().day.at("21:35").do(main)
    #while True:
    #    schedule.run_pending()
    #    time.sleep(5)
    
except Exception as e:
    print(str(e))
    sys.exit()

