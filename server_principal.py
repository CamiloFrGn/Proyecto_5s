# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 15:06:28 2020

@author: jsdelgadoc
"""
import pyodbc
import sys
sys.path.insert(0, r'C:\Users\E-JFRANCOGON\OneDrive - CEMEX\Documentos\Visoft\otros\proyectos_cemex')
from flask import Flask, request, redirect, url_for, send_from_directory,send_file, render_template,session
import os
#from SegmentacionClientes import SegmentacionClientes
from MallaTurnos import MallaTurnosWebapp
#from sld_v2.ranking.app.app import main_app as main_sld_v2
#from sld_v2.ranking.app.app_plant import main_app_plant as main_sld_v2_plant
#from sld_v2.ranking.centro.help_files.sql.connect_sql_server import query_sql_df
from sld_v2.cargue_masivo_oferta.cargue_masivo_oferta import main_cargue_masivo_oferta
from datetime import datetime
import pandas as pd
import sqlalchemy as sa
import urllib
import warnings
warnings.filterwarnings('ignore')
import sys
from zipfile import ZipFile
from werkzeug.utils import secure_filename
import win32com.client as win32
import easyocr
import cv2
from difflib import SequenceMatcher
import secrets
import string
import base64

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

app = Flask(__name__, template_folder=r"C:\Users\E-JFRANCOGON\OneDrive - CEMEX\Documentos\Visoft\otros\proyectos_cemex\templates", static_folder=r'C:\Users\E-JFRANCOGON\OneDrive - CEMEX\Documentos\Visoft\otros\proyectos_cemex\static')
app.secret_key = "cemex secret key"

#-----------------------------------------------------------------------------------------------------------------------------------------        
UPLOAD_FOLDER = r'C:\Users\E-JFRANCOGON\OneDrive - CEMEX\Documentos\Visoft\otros\proyectos_cemex\static\zip'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.'in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


def send_email(e, image_path=None):
    try:
        print("Sending email")
        # Construct Outlook app instance
        ol_app = win32.Dispatch('Outlook.Application')
        ol_ns = ol_app.GetNameSpace('MAPI')

        mail_item = ol_app.CreateItem(0)
        mail_item.Subject = "Error Script Programación"
        mail_item.BodyFormat = 1
        mail_item.Body = "Error!"
        mail_item.HTMLBody = "Ha sucedido el siguiente error: " + str(e)

        # Add recipients
        mail_item.To = 'santiagoandres.ortiz@cemex.com'

        if image_path:
            # Attach image if image_path is provided
            attachment = mail_item.Attachments.Add(image_path)
            attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "MyImage")
            mail_item.HTMLBody += f'<br><img src="cid:MyImage">'

        mail_item.Save()
        mail_item.Send()
    except Exception as e:
        print(str(e))
        sys.exit()

def obtener_nombres_plantas_desde_sql():
    # Configuración de la conexión a SQL Server
    server_name = "USCLDBITVMP01"
    database_name = "BI_Tableau"
    username = "usertableau"
    password = "usertableau$"

    # Cadena de conexión
    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server_name};DATABASE={database_name};UID={username};PWD={password}'

    # Conectar a SQL Server
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    # Ejecutar la consulta para obtener los nombres de las plantas de Colombia
    cursor.execute("SELECT [Planta Unica] FROM SCAC_AT1_NombreCluster WHERE Pais = 'Colombia' and Activo = '1'")
    nombres_plantas = [row[0] for row in cursor.fetchall()]

    # Cerrar la conexión a la base de datos
    conn.close()

    return nombres_plantas

# Example usage:
# send_email("An error occurred", "path_to_your_image.png")

@app.route("/index", methods=['GET'])
def welcome():
    return "al servidor principal de aplicacion inhouse de Asignaciones Cemex"

"""@app.route("/segmentacion/<pais>/<dias>/<paramrandom>", methods=['GET'])
def generar_segmentacion(pais, dias, paramrandom):
    
    return SegmentacionClientes.segmentar_clientes( pais, int(dias), paramrandom)"""

@app.route("/malla/<planta>/<fecha>/<precargadores>/<jornada>/<anticipacion>/<paramrandom>", methods=['GET'])
def generarmallaturnos( planta, fecha, precargadores, jornada, anticipacion, paramrandom):
   
    return MallaTurnosWebapp.generarm( planta,fecha, precargadores, jornada, anticipacion, paramrandom )

@app.route("/malla2/<planta>/<fecha>/<precargadores>/<jornada>/<anticipacion>/<paramrandom>/<tipopedido>", methods=['GET'])
def generarmallaturnos2( planta, fecha, precargadores, jornada, anticipacion, paramrandom, tipopedido):
   
    return MallaTurnosWebapp.generarm2( planta,fecha, precargadores, jornada, anticipacion, paramrandom, tipopedido )

"""@app.route("/mmpp/<fecha>/<pais>/<paramrandom>", methods=['GET'])
def generar_desagregacion_mmpp(fecha, pais, paramrandom):
   
    return DesagregacionMateriasPrimas.exportar_materias_primas_programacion(fecha, pais)"""

############## SLD ##################################################


"""@app.route("/sld/v2/ranking_form", methods=['GET'])
def sld_v2_ranking_form():
    sqlstatement = "{CALL sld_get_plants_list ()}"
    clusterplants_df =  query_sql_df(sqlstatement,())
    clusterplants = clusterplants_df.values.tolist()
    
    clusters = clusterplants_df['Desc Cluster'].unique()

    # create an empty dictionary to store the values
    result = {}
    # loop through the dataframe and add the values to the dictionary
    for cluster, plant in zip(clusterplants_df['Desc Cluster'], clusterplants_df['cod_plant']):
        if cluster not in result:
            result[cluster] = []
        result[cluster].append(plant)
    filter_dic = result
    filter_dic = json.dumps(filter_dic)

    
    sqlstatement_c = "{CALL sld_get_plants_list_country ()}"
    clusterplants_df_c =  query_sql_df(sqlstatement_c,())
    paises = clusterplants_df_c['Pais'].unique()
    # create an empty dictionary to store the values
    result_country = {}
    # loop through the dataframe and add the values to the dictionary
    for cluster, plant in zip(clusterplants_df_c['Pais'], clusterplants_df_c['Desc Cluster']):
        if cluster not in result_country:
            result_country[cluster] = []
        result_country[cluster].append(plant)
    filter_dic_country = result_country
    filter_dic_country = json.dumps(filter_dic_country)

    return render_template("ranking_sld_form.html",clusterplants=clusterplants,clusters=clusters,\
        paises=paises,filter_dic=filter_dic,filter_dic_country=filter_dic_country)

@app.route("/sld/v2/cluster=<cluster>&rannum=<paramrandom>", methods=['GET'])
def generate_sld_ranking(cluster,paramrandom):
   
    return main_sld_v2(cluster,paramrandom)

@app.route("/sld/v2/cluster=<cluster>&rannum=<paramrandom>&plant=<plant>", methods=['GET'])
def generate_sld_ranking_plant(cluster,plant,paramrandom):
   
    return main_sld_v2_plant(cluster,plant,paramrandom)"""


@app.route("/sld/v2/cargue_masivo_oferta", methods=['GET','POST'])
def cargue_masivo_oferta():
    
    if request.method == "POST":
        
        params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};SERVER=USCLDBITVMP01;DATABASE=BI_Tableau;UID=usertableau;PWD=usertableau$")
        engine = sa.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params, fast_executemany=True)
        try:
            plantilla = request.files.get('plantilla')
            marca_temp = datetime.now()
            df = pd.read_excel(plantilla, sheet_name="registro")
            df['fecha_cargue'] = marca_temp
            database_name = "SCAC_AT55_MatrizCupos"
            df.to_sql(database_name, engine, index=False, if_exists="append", schema="dbo")  
            return render_template("exitoso.html")
        except Exception as e:
            print(str(e))
            return render_template("error.html")
    return render_template("cargue_masivo_oferta.html")

@app.route("/sld/v2/descargue_plantilla_cargue_oferta/<rannum>", methods=['GET'])
def descargue_plantilla_cargue_oferta(rannum):
    file_path = r"C:\Users\E-JFRANCOGON\OneDrive - CEMEX\Documentos\Visoft\otros\proyectos_cemex\sld_v2\cargue_masivo_oferta"
    filename = "plantilla_cargue_masivo.xlsx"
    return send_from_directory(file_path , filename, as_attachment=True)


###########pagina web excelencia operacional############


@app.route("/excelencia_operacional/enlaces", methods=['GET'])
def index_enlaces_excelencia_op():
    return render_template("index_enlaces_excelencia_op.html")

@app.route("/excelencia_operacional/inicio", methods=['GET'])
def index_inicio_excelencia_op():
    return render_template("index_inicio.html")


#########################ready mix######################
@app.route('/')
def home():
    try:
        if 'user_cemex_repordig' in session: 
            return render_template('index.html')   
        else:
            return redirect(url_for('login'))       
    except Exception as e:
        return str(e)  

@app.route('/navbar')
def navbar():
    return render_template('VerticalSidebarNavigation.html')  


@app.route('/exito')
def exito():
    return render_template('exito.html')  

@app.route('/login', methods=['GET','POST'])
def login():
    try:
            # Configuración de la conexión a SQL Server
        server_name = "USCLDBITVMP01"
        database_name = "BI_Tableau"
        username = "usertableau"
        password = "usertableau$"
    # Cadena de conexión
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server_name};DATABASE={database_name};UID={username};PWD={password}'
    # Conectar a SQL Server
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor() 
        if 'user_cemex_repordig' in session:
            return redirect(url_for('home'))  
        else:
            if request.method == "POST":
                
                #avoid session permanece. When browser is closed, so is the session
                session.permanent = False
                password = request.form['password']
                #validate the existences of the user and password
                #mycursor.execute("select * from usuarios where cedula = '"+str(user)+"' and clave = '"+str(password)+"' and estado = 1 ;")
                #user_valid = mycursor.fetchone()
                cursor.execute("SELECT * FROM scac_at_usuarios_portal where cedula ='"+str(password)+"'")
                user_valid = cursor.fetchall()
                if not user_valid:
                    return redirect(url_for('login'))
                else:
                    #create session json        
                    session['user_cemex_repordig'] = user_valid[0][1]
                    session['password'] = password
                    session['cargo'] = user_valid[0][2]
                                    
                    return redirect(url_for('home'))  
            return render_template("login.html") 
        
    except Exception as e:
        return str(e)
    
    finally: 
        conn.close()
      
    

@app.route('/logout')
def logout():
    try:   
        return "logout"     
    except Exception as e:
        return str(e)   


@app.route('/form_preoperacional_inspeccion_360', methods=['GET','POST'])
def form_preoperacional_inspeccion_360():
    try:
        if request.method == "POST":
            return "success"
        return render_template('form_preoperacional_inspeccion_360.html')          
    except Exception as e:
        return str(e)  

@app.route('/evaluacion_5s', methods=['GET','POST'])
def evaluacion_5s():
    try:
        # Establish a connection to your database
        conn = pyodbc.connect(connection_string)
        nombres_plantas = obtener_nombres_plantas_desde_sql()
        # Create a cursor to execute SQL queries
        cursor = conn.cursor()
        params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};SERVER=USCLDBITVMP01;DATABASE=BI_Tableau;UID=usertableau;PWD=usertableau$")
        engine = sa.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params, fast_executemany=True)
        if request.method == "POST":
            
            #registro 
            timestamp = datetime.now()
            planta = request.form['planta']
            auditor = session['user_cemex_repordig']
            auditado = request.form['auditado']
            df_registro = pd.DataFrame(columns=['fecha', 'planta', 'auditor', 'auditado'])
            df_registro_list = [timestamp,planta,auditor,auditado]
            df_registro.loc[0] = df_registro_list
            database_name = "scac_at_registros_evaluacion5s"
            df_registro.to_sql(database_name, engine, index=False, if_exists="append", schema="dbo")
            # Execute a SELECT statement to get the max ID number from a table (assuming the table is named 'your_table')
            cursor.execute("SELECT MAX(id) AS max_id FROM "+database_name)
            # Fetch the result
            max_id = cursor.fetchone()
            # Print the maximum ID number
            if max_id[0] is not None:
                print("Maximum ID number:", max_id[0])
            else:
                print("Table is empty or ID column contains only NULL values")
            # Close the cursor and the connection
            cursor.close()
            conn.close()

            #registro de respuesta
            num_questions = 144  # Update this with the actual number of questions

            # Initialize a dictionary to store form responses
            form_responses = {}
            indices_multiples_archivos = [0,9,18,27,36,45,54,62,70,79,89,96,104,112,122,130,138]
            file_paths=[]

            # Iterate through each question and retrieve its response
            for i in range(num_questions):
                question_key = f"pregunta_{i}"
                response = request.form.get(question_key)
                # Extract only the number from the question key
                question_number = question_key.split('_')[-1]
                form_responses[question_number] = response

                if i in indices_multiples_archivos:
                    file_key = f"pregunta_{i}"
                    files = request.files.getlist(file_key)
                    encoded_images = []
                    for file in files:
                        if file and allowed_file(file.filename):
                            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                            file.save(file_path)
                            file_paths.append(file_path)

                            with open(file_path, "rb") as img_file:
                                encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
                                encoded_images.append(encoded_image)
                                print("IMAGEN:", encoded_image)
                        elif file:
                        # Manejar el caso en que la extensión del archivo no sea permitida
                            return render_template("error.html", message="Formato de archivo no permitido")
            df = pd.DataFrame(form_responses.items(), columns=['id_pregunta', 'respuesta'])
            # Add an 'id_registro' column at the start of the DataFrame
            df.insert(0, 'id_registro', value=max_id[0])  # Replace 'your_id_value_here' with your desired ID
            destination_folder = r'C:\Users\E-JFRANCOGON\OneDrive - CEMEX\Documentos\Visoft\otros\proyectos_cemex\static\zip'
            os.makedirs(destination_folder, exist_ok=True)
            # Comprimir archivos en un archivo zip
            zip_principal_filename = f'{max_id[0]}.zip'
            zip_principal_path = os.path.join(destination_folder, zip_principal_filename)
            with ZipFile(zip_principal_path, 'w') as zip_principal:
                for i, file_path in enumerate(file_paths):

                    zip_individual_filename = f'{i}.zip'
                    zip_individual_path = os.path.join(destination_folder, zip_individual_filename)

                    with ZipFile(zip_individual_path, 'w') as zip_individual:
                        zip_individual.write(file_path, f'pregunta_{i}.jpg')

                    zip_principal.write(zip_individual_path, zip_individual_filename)
                    os.remove(zip_individual_path)
                    os.remove(file_path)
            database_name = "scac_at_respuestas_evaluacion5s"
            df.to_sql(database_name, engine, index=False, if_exists="append", schema="dbo")
            return render_template("exito.html")
        return render_template('evaluacion_5s.html',plantas=nombres_plantas)          
    except Exception as e:
        return str(e)

@app.route('/descargar_zip', methods=['GET'])
def descargar_zip():
    try:
        nombre_zip = request.args.get('nombre_zip')
        if nombre_zip:
            zip_path = r'C:\Users\E-JFRANCOGON\OneDrive - CEMEX\Documentos\Visoft\otros\proyectos_cemex\static\zip'  # Ruta al directorio de los archivos ZIP

            archivo_zip = os.path.join(zip_path, f'{nombre_zip}.zip')

            if os.path.exists(archivo_zip):
                return send_file(archivo_zip, as_attachment=True)
            else:
                return "El archivo ZIP no existe.", 404
        else:
            return "No se proporcionó el nombre del ZIP.", 400
    except Exception as e:
        return str(e)

@app.route('/formulario_descargar_zip', methods=['GET'])
def mostrar_formulario_descargar_zip():
    return render_template('descargar_zip.html')

@app.route('/ocr', methods=['GET','POST'])
def ocr():
    try:
        if request.method == "POST":
            placa = request.form['placa']
            img = request.files['img']
            # Define the directory where you want to save the image
            save_directory = r'C:\Users\E-JFRANCOGON\OneDrive - CEMEX\Documentos\Visoft\otros\img'
            img.save(os.path.join(save_directory, img.filename))
            IMAGE_PATH = os.path.join(save_directory, img.filename)
            print(IMAGE_PATH)
            reader = easyocr.Reader(['en'],gpu=False)
            result = reader.readtext(IMAGE_PATH)
            print(result)

            top_left = tuple(map(int, result[0][0][0]))
            bottom_right = tuple(map(int, result[0][0][2]))
            text = result[0][1]
            font = cv2.FONT_HERSHEY_SIMPLEX


            img = cv2.imread(IMAGE_PATH)
            img = cv2.rectangle(img,top_left,bottom_right,(0,255,0),4)
            img = cv2.putText(img,text,top_left,font,2,(255,255,255),2,cv2.LINE_AA)

            output_name = "test.jpg"
            output_path = os.path.join(save_directory, output_name)
            cv2.imwrite(output_path, img)

            text2 = placa
            print("texto real: ",text2)
            text = text.replace(" ", "")
            text = text.lower()
            print("texto detectado: ",text)

            similitud = SequenceMatcher(None, text, text2).ratio() * 100
            print(f"El porcentaje de similitud entre las cadenas es: {similitud:.2f}%")
            length = 10
            alphabet = string.ascii_letters + string.digits  # Includes uppercase, lowercase letters, and digits
            token = ''.join(secrets.choice(alphabet) for _ in range(length))
            token = str(token)

            #return redirect(url_for('form_preoperacional_inspeccion_360',rannum=token))
            #return redirect(url_for('exito'))
            return send_file(output_path, mimetype='image/png')
        return render_template('ocr.html')          
    except Exception as e:
        return str(e)  


@app.route('/ocr2', methods=['GET','POST'])
def ocr2():
    try:
        if request.method == "POST":
            placa = request.form['placa']
            img = request.files['img']
            # Define the directory where you want to save the image
            save_directory = r'C:\Users\E-JFRANCOGON\OneDrive - CEMEX\Documentos\Visoft\otros\img'
            img.save(os.path.join(save_directory, img.filename))


            IMAGE_PATH = os.path.join(save_directory, img.filename)
            text2 = placa

            # Cargar la imagen
            img = cv2.imread(IMAGE_PATH)
            # Convertir a imagen a escala de grises
            #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Aplicar umbralización adaptativa para manejar las sombras
            #thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
            thresh = img
            reader = easyocr.Reader(['en'],gpu=False)
            result = reader.readtext(thresh)
            if result:
                for detection in result:
                    coordinates = detection[0]
                    text = detection[1]
                    text = text.replace(" ","")
                    text = text.lower()
                    text_to_compare = text2.lower()
                    top_left = tuple(coordinates[0])
                    bottom_right = tuple(coordinates[2])
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 4)
                    cv2.putText(img, text, top_left, font, 2, (255, 255, 255), 2, cv2.LINE_AA)
                    # Calculate similarity percentage between text and text_to_compare
                    similarity = SequenceMatcher(None, text, text_to_compare).ratio() * 100
                    if similarity > 50:
                        print(f"El porcentaje de similitud entre las cadenas es: {similarity:.2f}%")
                        print("Found higher than 50%")
                        break

                if similarity <= 50:
                    print("Not found")

                # Mostrar resultados         
                print("")
                #create tokem
                length = 10
                alphabet = string.ascii_letters + string.digits  # Includes uppercase, lowercase letters, and digits
                token = ''.join(secrets.choice(alphabet) for _ in range(length))
                token = str(token)

                #return redirect(url_for('form_preoperacional_inspeccion_360',rannum=token))
                #return redirect(url_for('exito'))
                output_name = "test.jpg"
                output_path = os.path.join(save_directory, output_name)
                cv2.imwrite(output_path, img)

                return send_file(output_path, mimetype='image/png')


                # Resto del código para comparar el texto detectado con el texto real
            else:
                return "No se encontró texto en la imagen."
            

            
        return render_template('ocr.html')          
    except Exception as e:
        return str(e)  
    
"""server = WSGIServer(('192.168.80.17',49838),app)
server.serve_forever()"""

"""if(__name__=="__main__"):
    app.run()"""

if(__name__=="__main__"):
    app.run(host='0.0.0.0', port=5000)

