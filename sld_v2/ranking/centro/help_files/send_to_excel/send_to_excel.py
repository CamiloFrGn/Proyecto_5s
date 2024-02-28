import pandas as pd
import sys
import os
import xlsxwriter 
from flask import send_file

def send_to_excel(df):
    try:
        
        #create excel
        now = pd.to_datetime("now").strftime("%Y-%m-%d-%H-%M-%S")
        path = r"C:\Users\jsdelgadoc\Documents\Proyectos-Cemex\sld_v2\ranking\centro\help_files\data\clusterCentro_"+str(now)+".xlsx"
        create_excel = pd.ExcelWriter(path, engine='xlsxwriter') #create excel to save dataframe
        df.to_excel( create_excel, sheet_name="data", index=False ) #send dataframe day to excel sheet created previously
        df_len = len(df)+1
        #conditional formating and normal formatting

        workbook = create_excel.book
        worksheet = create_excel.sheets['data']
        worksheet.set_zoom(90)

        worksheet.set_column("A:X",20)
        worksheet.set_column("F:F",0)
        worksheet.set_column("H:H",0)
        worksheet.set_column("K:K",0)
        worksheet.set_column("M:N",0)
        worksheet.set_column("Q:Q",0)
        worksheet.set_column("S:S",0)


        #number format
        number_format = workbook.add_format({"num_format" : "#,###.##"})

        worksheet.set_column("C:C", 12, number_format)

        #percent format
        percent_format = workbook.add_format({"num_format" : "0.0%"})

        worksheet.set_column("E:E", 20, percent_format)
        worksheet.set_column("J:J", 0, percent_format)
        worksheet.set_column("V:V", 0, percent_format)

        #formatting sld column
        #platinum
        platinum = workbook.add_format({"bg_color" : "#e5e4e2", "font_color": "#000000"})
        worksheet.conditional_format('W2:W'+str(df_len),
                             {'type': 'text',
                              'criteria': 'containing',
                              'value': 'PLATINUM',
                              'format':   platinum
                              })
      
        #gold
        gold = workbook.add_format({"bg_color" : "#FFD700", "font_color": "#000000"})
        worksheet.conditional_format('W2:W'+str(df_len),
                             {'type': 'text',
                              'criteria': 'containing',
                              'value': 'GOLD',
                              'format':   gold
                              })
    
        #silver
        silver = workbook.add_format({"bg_color" : "#C0C0C0", "font_color": "#000000"})
        worksheet.conditional_format('W2:W'+str(df_len),
                             {'type': 'text',
                              'criteria': 'containing',
                              'value': 'SILVER',
                              'format':   silver
                              })
      

        create_excel.close() #save the workbook

        return send_file(path, as_attachment=True)

    except Exception as e:
        print(str(e))
        sys.exit()