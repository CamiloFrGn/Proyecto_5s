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
            file_paths=[]

            # Iterate through each question and retrieve its response
            for i in range(0,num_questions+1):
                question_key = f"pregunta_{i}"
                response = request.form.get(question_key)
                # Extract only the number from the question key
                question_number = question_key.split('_')[-1]
                form_responses[question_number] = response

                if i in [0,9,18,27,36,45,54,62,70,79,89,96,104,112,122,130,138]:
                    file_key = f"pregunta_{i}"
                    file = request.files[file_key]
                    # Verificar si la extensión del archivo es permitida
                    if file and allowed_file(file.filename):
                    # Guardar el archivo en el servidor
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                        file.save(file_path)
                        file_paths.append(file_path)
                    elif file:
                        # Manejar el caso en que la extensión del archivo no sea permitida
                        return render_template("error.html", message="Formato de archivo no permitido")

            # Create a DataFrame from the form responses
            df = pd.DataFrame(form_responses.items(), columns=['id_pregunta', 'respuesta'])
            # Add an 'id_registro' column at the start of the DataFrame
            df.insert(0, 'id_registro', value=max_id[0])  # Replace 'your_id_value_here' with your desired ID
            destination_folder = r'C:\Users\E-JFRANCOGON\OneDrive - CEMEX\Documentos\Visoft\otros\proyectos_cemex\static\zip'
            os.makedirs(destination_folder, exist_ok=True)
            # Comprimir archivos en un archivo zip
            zip_principal_filename = f'{max_id[0]}_imagenes.zip'
            zip_principal_path = os.path.join(destination_folder, zip_principal_filename)
            with ZipFile(zip_principal_path, 'w') as zip_principal:
                for i, file_path in enumerate(file_paths):

                    zip_individual_filename = f'pregunta_{i}.zip'
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