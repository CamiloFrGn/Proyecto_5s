import pandas as pd
import sys
import os

def send_to_excel(df):
    try:
        print("Sending to excel")
        current_folder = os.getcwd()
        #create excel
        now = pd.to_datetime("now").strftime("%Y-%m-%d-%H-%M-%S")
        create_excel = pd.ExcelWriter(current_folder+"\disorganized_clients\help_files\data\export_"+str(now)+".xlsx", engine='xlsxwriter') #create excel to save dataframe
        df.to_excel( create_excel, sheet_name="data", index=False ) #send dataframe day to excel sheet created previously
        create_excel.save() #save the workbook
    except Exception as e:
        print(str(e))
        sys.exit()