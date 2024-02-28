"""This script will be used to open a connection to our database engine. We will create a function
that will return both the cursor (a cursor is an object that allows us to execute our sql queries) and connection objects.
Our second function with return an sql query as a dataframe
"""
#import libraries

import pyodbc #import pyodbc since we are currently using sql server as our database engine
import pandas as pd # dataframe library
import numpy as np #mathematical library
import sqlalchemy as sa
import urllib
import sys

#----------------------PYODBC CONNECTION-------------------------
#declare out variables that we will use to create our connection string to the engine
driver = "ODBC Driver 17 for SQL Server" #sql engine that we are using
server_name = "USCLDBITVMP01" #name assigned to the server. Any issues please talk with IT department
database_name = "BI_Tableau" #the database that will be used in this connection
user_name = "usertableau" 
password = "usertableau$"
"""concatenate previous variabels to create connection string. We use 3 {} in the driver name since the syntax 
requieres 1 set of {} for the driver parameter. This will be passed to the odbc library to open connection.
We use f string to integrate previous variables. Trust_connection = yes sprecifies that a user account is used to
open the connection"""
connection_string = f"""DRIVER={{{driver}}};
                        SERVER={server_name};
                        DATABASE={database_name};
                        Trust_connection = yes;
                        UID={user_name};
                        PWD={password}"""



#---------------------SQLALCHEMY CONNECTION---------------------------------
params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};SERVER=USCLDBITVMP01;DATABASE=BI_Tableau;UID=usertableau;PWD=usertableau$")
engine = sa.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params, fast_executemany=True)
#---------------------------------------------------------------------------

def send_df_to_sql(data,database_name):
    try:          
        data.to_sql(database_name, engine, index=False, if_exists="append", schema="dbo")  
        return "success"       
    except Exception as e:
        print(str(e))
        sys.exit()


def query_sql_crud(query, parameters):   
    try:     
        #reference the odbc module to open connection 
        connection = pyodbc.connect(connection_string)
        #declare cursor for sql query execution
        cursor = connection.cursor()     
        cursor.execute(query, parameters)  
        connection.commit()   
        return "success"       
    except Exception as e:
        print(str(e))
        sys.exit()
    finally:
        cursor.close()
        connection.close()
        
        
#Function to return sql query as a dataframe. The function receives the query statement as well as the parameters required.

def query_sql_df(query, parameters):
    
    try:
        #execute pass query statement and parameters
        #reference the odbc module to open connection 
        connection = pyodbc.connect(connection_string)
        #declare cursor for sql query execution
        cursor = connection.cursor()
        cursor.execute(query, parameters)
        
        """get all column names for our dataframe. The .description makes this possible. This is to avoid having to manually 
        put the column names for every distinct query statement we execute. Because the .description gives us all
        the details for each column and we only need the name, we declare the for every x in . description, just return
        the first spot in each tuple/list"""
        
        names = [ x[0] for x in cursor.description] 
        
        #get all data from the cursor execution with fetchall() method
        
        rows = cursor.fetchall()
        resultadoSQL = []
            
        #before we create the dataframe, we must first pass the cursor response into an array.
        #while rows is <> from None, get next result set if it exists, else rows = None and the while loop finishes.
        
        while rows:
            resultadoSQL.append(rows)
            if cursor.nextset():
                rows = cursor.fetchall()
            else:
                rows = None
                
        #we must redimension the previous array to 2 dimensions.
        #Turn resultadosSQL from a traditional list to a numpy array that allows us to use more funtions such as reshape.
        
        resultadoSQL = np.array(resultadoSQL)
        resultadoSQL = np.reshape(resultadoSQL, (resultadoSQL.shape[1], resultadoSQL.shape[2]) )
        
        """use .DataFrame to insert our resultadosSQL np array into a pandas dataframe. The first parameter is the
        array and the second is the column names that we obtained with the cursor.description."""
        
        df = pd.DataFrame(resultadoSQL, columns = names)
        
        #reutrn dataframe to start analysis
        
        return df
    
    except Exception as e:
        
        #if exception is captured, return exception statement and close the connection to engine
        
        print(str(e))
        connection.close()
        sys.exit()
    # close cursor always after try or except block.
    
    finally:
    
    #first check if cursor is <> to None before closing to avoid possible error.
    
            if cursor is not None:
                cursor.close()
                
