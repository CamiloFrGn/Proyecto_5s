import pandas as pd
import sys
from flask import send_file

def send_to_excel(df):
    try:
    
        #current_folder = os.getcwd()
        #create excel
        now = pd.to_datetime("now").strftime("%Y-%m-%d-%H-%M-%S")
        #create_excel = pd.ExcelWriter(r"C:\Users\snortiz\Documents\projects\sld\ranking\santander\florida\help_files_san_flor\data_san_flor\plantaFlorida_"+str(now)+".xlsx", engine='xlsxwriter') #create excel to save dataframe
        path = r"C:\Users\jsdelgadoc\Documents\Proyectos-Cemex\sld_v2\ranking\santander\florida\help_files_san_flor\data_san_flor\clusterFlorida_"+str(now)+".xlsx"
        create_excel = pd.ExcelWriter(path, engine='xlsxwriter') #create excel to save dataframe
        df.to_excel( create_excel, sheet_name="data", index=False ) #send dataframe day to excel sheet created previously
        df_len = len(df)+1
        #conditional formating and normal formatting

        workbook = create_excel.book
        worksheet = create_excel.sheets['data']
        worksheet.set_zoom(90)

        worksheet.set_column("A:AH",20)
        worksheet.set_column("F:F",0)
        worksheet.set_column("H:H",0)
        worksheet.set_column("I:I",0)
        worksheet.set_column("K:K",0)
        worksheet.set_column("M:M",0)
        worksheet.set_column("O:O",0)
        worksheet.set_column("Q:Q",0)
        worksheet.set_column("R:R",0)
        worksheet.set_column("T:T",0)
        worksheet.set_column("U:U",0)
        worksheet.set_column("W:W",0)
        worksheet.set_column("X:X",0)
        worksheet.set_column("Z:Z",0)
        worksheet.set_column("AA:AA",0)
        worksheet.set_column("AC:AC",0)


        #number format
        number_format = workbook.add_format({"num_format" : "#,###.##"})

        worksheet.set_column("C:C", 12, number_format)

        #percent format
        percent_format = workbook.add_format({"num_format" : "0.0%"})

        worksheet.set_column("E:E", 20, percent_format)
        worksheet.set_column("H:H", 0, percent_format)
        worksheet.set_column("AC:AC", 0, percent_format)
        worksheet.set_column("AF:AF", 0, percent_format)

        #formatting sld column
        #platinum
        platinum = workbook.add_format({"bg_color" : "#e5e4e2", "font_color": "#000000"})
        worksheet.conditional_format('AG2:AG'+str(df_len),
                             {'type': 'text',
                              'criteria': 'containing',
                              'value': 'PLATINUM',
                              'format':   platinum
                              })
      
        #gold
        gold = workbook.add_format({"bg_color" : "#FFD700", "font_color": "#000000"})
        worksheet.conditional_format('AG2:AG'+str(df_len),
                             {'type': 'text',
                              'criteria': 'containing',
                              'value': 'GOLD',
                              'format':   gold
                              })
    
        #silver
        silver = workbook.add_format({"bg_color" : "#C0C0C0", "font_color": "#000000"})
        worksheet.conditional_format('AG2:AG'+str(df_len),
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