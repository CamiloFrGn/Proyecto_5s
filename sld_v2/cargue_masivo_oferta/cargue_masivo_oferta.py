import pandas as pd
import sqlalchemy as sa
import urllib
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
#---------------------SQLALCHEMY CONNECTION---------------------------------
params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};SERVER=USCLDBITVMP01;DATABASE=BI_Tableau;UID=usertableau;PWD=usertableau$")
engine = sa.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params, fast_executemany=True)
#---------------------------------------------------------------------------

def main_cargue_masivo_oferta(plantilla):
    try:
        marca_temp = datetime.now()
        df = pd.read_excel(plantilla, sheet_name="registro")
        df['fecha_cargue'] = marca_temp
        database_name = "SCAC_AT55_MatrizCupos"
        df.to_sql(database_name, engine, index=False, if_exists="append", schema="dbo")  
    except Exception as e:
        print(str(e))
