import mysql.connector
from flask import Flask, request, render_template
import os
import requests
import json
from datetime import datetime
from flask import jsonify
from flask import session, redirect, url_for
from flask import Response
# import Flask libraries
from flask import Flask, request, render_template, jsonify
# import SPARQL query function

import requests
import urllib.parse
import json

# ... (existing code for MySQL connection and WingUCTBOT class definition) ...

# Create a connection to the database
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="aizen",
    database="lexdb",
    port=3306
)
singulargram="Q110786"
# Create a cursor object to interact with the MySQL server
cursor = connection.cursor()

# Execute the SPARQL query
cursor.execute("SELECT * from user")
userdata=cursor.fetchall()
print("")
print("User Data!")
print(userdata)
print("")
class WingUCTBOT:
    def __init__(self):
        self.url= "https://test.wikidata.org/w/api.php"
        self.session = requests.Session()
        cursor.execute("SELECT * FROM batchupload")
        self.batchdata = cursor.fetchall()
        self.batchusername = ""

    def record_batch_upload(self, batch_size, success_count, language):
        # Get the current time
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        # Insert the record using self.batchusername
        print("USERNAME: " + self.batchusername)
        print("Language: "+ language)
        query = "INSERT INTO batchupload (batch_upload_size, upload_success_rate, UploadDate, username,languages) VALUES (%s, %s, %s, %s,%s)"
        cursor.execute(query, (batch_size, success_count, formatted_date, self.batchusername,language))
        connection.commit()
        get_batch_data()

        


    def uploadlexemes(self,batchsize):
        cursor.execute(f"SELECT LexicalEntry_id FROM lexicalentry LIMIT {batchsize}")
        # Fetch and print the results
        results = cursor.fetchall()
        lexicalids = [row[0] for row in results]
        success_count = 0
        for i in lexicalids:           
            lexical_entry_id=i
            query = (
                "SELECT l.Language_code "
                "FROM word AS w "
                "JOIN language AS l ON w.Language_id = l.Language_id "
                "WHERE w.LexicalEntry_id = %s;"
                )
            cursor.execute(query, (lexical_entry_id,))

            # Fetch the result
            result = cursor.fetchone()
            language_code = result[0]
            query = (
                "SELECT word FROM word WHERE LexicalEntry_id = %s"
            )
            cursor.execute(query, (lexical_entry_id,))
            result = cursor.fetchone()
            word = result[0]
            query = (
                "SELECT category_code FROM grammaticalcategory WHERE LexicalEntry_id = %s"
            )
            cursor.execute(query, (lexical_entry_id,))
            result = cursor.fetchone()
            cat = result[0]
  
            query = (
                "SELECT Language_id FROM word WHERE LexicalEntry_id = %s"
            )
            cursor.execute(query, (lexical_entry_id,))
            result = cursor.fetchone()
            lang = result[0]


            query = (
                "SELECT gramfeaturesid, inflection "
                "FROM inflection AS i "
                "JOIN lexicalentry AS l ON i.base = l.Word "
                "WHERE l.LexicalEntry_id = %s"
            )
            cursor.execute(query, (lexical_entry_id,))

            # Fetch the results
            results = cursor.fetchall()
            forms =results


            query = (
                "SELECT m.BantuContext "
                "FROM meanings AS m "
                "JOIN lexicalentry AS l ON m.word = l.Word "
                "WHERE l.LexicalEntry_id = %s;"
                )
            cursor.execute(query, (lexical_entry_id,))


            results = cursor.fetchall()

            # Extract the senses
            senses = results

            print("SESNSES")
            print(senses)

            print("FORMS")
            print(forms)

  
            LOGIN_TOKEN = self.session .get(url=self.url, params={
                "action": "query",
                "meta": "tokens",
                "type": "login",
                "format": "json"
            }).json()['query']['tokens']['logintoken']
    
            LOGIN_DATA = {
                "action": "login",
                "lgname": "WingUCTBOT",
                "lgpassword": "$Tinkmeaner7",
                "format": "json",
                "lgtoken": LOGIN_TOKEN
            }
    
            self.session .post(self.url, data=LOGIN_DATA)
    
            CSRF_TOKEN = self.session .get(url=self.url, params={
                "action": "query",
                "meta": "tokens",
                "format": "json"
            }).json()['query']['tokens']['csrftoken']

            if(forms[0][1]==''):
                LEXEME_DATA = {
                    "action": "wbeditentity",
                    "new": "lexeme",
                    "data": json.dumps({
                        "lemmas": {
                            language_code: {
                                "language": language_code,
                                "value": word
                            }
                        },
                        "lexicalCategory": cat,  # Shona language
                        "language": lang  ,# Word
                        "forms": [     
                                           {
                                "add": "",
                                "representations": {
                                    language_code: {
                                        "language": language_code,
                                        "value": word # This should be the string representation of the form
                                    }
                                },
                                "grammaticalFeatures":[singulargram] # This should be a list of Wikidata item IDs
                            }
                        ],
                        "senses": [
                            {   "add": "",
                                "glosses":{
                                    language_code:{
                                        "language": language_code,
                                        "value": senses[0][0]
                                    }
                                }
                            }
                        ]
                    }),
                    "format": "json",
                    "token": CSRF_TOKEN
                }
            else:
                LEXEME_DATA = {
                    "action": "wbeditentity",
                    "new": "lexeme",
                    "data": json.dumps({
                        "lemmas": {
                            language_code: {
                                "language": language_code,
                                "value": word
                            }
                        },
                        "lexicalCategory": cat,  # Shona language
                        "language": lang  ,# Word
                        "forms": [
                                           {
                                "add": "",
                                "representations": {
                                    language_code: {
                                        "language": language_code,
                                        "value": word # This should be the string representation of the form
                                    }
                                },
                                "grammaticalFeatures":[singulargram] # This should be a list of Wikidata item IDs
                            },
                            {
                                "add": "",
                                "representations": {
                                    language_code: {
                                        "language": language_code,
                                        "value": forms[0][1]  # This should be the string representation of the form
                                    }
                                },
                                "grammaticalFeatures": [forms[0][0]]# This should be a list of Wikidata item IDs
                            }
                        ],
                        "senses": [
                            {   "add": "",
                                "glosses":{
                                    language_code:{
                                        "language": language_code,
                                        "value": senses[0][0]
                                    }
                                }
                            }
                        ]
                    }),
                    "format": "json",
                    "token": CSRF_TOKEN
                }

            response = self.session.post(self.url, data=LEXEME_DATA)
            data=response.json()
            success_count += 1
            print(json.dumps(data, indent=4))

        return success_count


    def get_batch_data(self):
        return self.batchdata



app = Flask(__name__)

# Base URL of the SPARQL endpoint
base_url = "http://localhost:2020/sparql"

def run_sparql_query(select_clause):
    # SPARQL query prefixes
    prefixes = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX vocab: <http://localhost:2020/resource/vocab/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX map: <http://localhost:2020/resource/#>
    PREFIX db: <http://localhost:2020/resource/>
    """

    # Full SPARQL query
    query = prefixes + select_clause

    # URL encode the query
    encoded_query = urllib.parse.quote_plus(query)

    # Construct the full URL
    full_url = base_url + "?query=" + encoded_query + "&output=json"

    # Send the GET request
    response = requests.get(full_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response as JSON
        data = response.json()

        # Return the JSON data
        return data
    else:
        return {"error": f"Failed to retrieve data, status code: {response.status_code}"}

app.secret_key = '42'

bot = WingUCTBOT() # Instance of your existing bot class
print(bot.batchdata)
@app.route('/')
def index():
    return render_template('index.html')


def get_BatchUpload_data():
    print("Getting batch data")
    cursor.execute("SELECT * FROM batchupload")
    bot.batchdata = cursor.fetchall()
    for i in range(len(bot.batchdata)):
        batch = list(bot.batchdata[i])
        batch[2] = batch[2].strftime("%Y-%m-%d %H:%M:%S")  # convert datetime to string
        bot.batchdata[i] = tuple(batch)
    return json.dumps(bot.batchdata), 200

@app.route('/get_batch_data', methods=['GET'])
def get_batch_data():
    print("Getting batch data")
    cursor.execute("SELECT * FROM batchupload")
    bot.batchdata = cursor.fetchall()
    for i in range(len(bot.batchdata)):
        batch = list(bot.batchdata[i])
        batch[2] = batch[2].strftime("%Y-%m-%d %H:%M:%S")  # convert datetime to string
        bot.batchdata[i] = tuple(batch)
    return json.dumps(bot.batchdata), 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the username and password from the form
        username = request.form['username']
        password = request.form['password']

        # Check credentials
        if authenticate(username, password):
            bot.loggedin="Y"
            bot.batchusername = username 
            return "Logged in successfully!", 200
        else:
            return "Incorrect username or password.", 401

    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    # Get the registration details from the form data
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']

    # Call the register_user function to handle registration
    status, message = register_user(email, username, password)

    return message, status



def register_user(email, username, password):
    try:
        # Check if email or username already exists
        cursor.execute("SELECT * FROM user WHERE UserEmail=%s OR username=%s", (email, username))
        existing_user = cursor.fetchone()

        if existing_user:
            return 400, "Email or username already exists."

        # Insert the new user details into the database
        cursor.execute("INSERT INTO user (UserEmail, username, UserPassword) VALUES (%s, %s, %s)", (email, username, password))
        connection.commit()

        return 200, "Registration successful!"
    except Exception as e:
        print(f"Error during registration: {e}")
        return 500, "Registration failed due to server error."




def authenticate(username, password):
    try:
        cursor.execute("SELECT * FROM user WHERE username=%s AND UserPassword=%s", (username, password))
        if cursor.fetchone():
            return True
        return False
    except Exception as e:
        print(f"Error during authentication: {e}")
        return False


@app.route('/sparql', methods=['GET', 'POST'])
def sparql():
    if request.method == 'POST':
        query = request.form['query']

        # Try to run the query
        try:
            data = run_sparql_query(query)
            # Convert data to a string format
            data_str = json.dumps(data)
            return jsonify(data_str), 200
        except Exception as e:
            return jsonify(str(e)), 500

    return render_template('index.html') 


@app.route('/download_db_dump', methods=['GET'])
def download_db_dump():
    try:
        # Execute command to fetch entire database
        
        query = "SELECT * FROM information_schema.tables WHERE table_schema = 'lexdb'"
        
        cursor.execute(query)
        print("Here")
        tables = cursor.fetchall()
        data = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT * FROM {table_name}")
            data[table_name] = cursor.fetchall()
        
        # Convert data to JSON string for download
        data_str = json.dumps(data, default=str)
        print(data_str)  # Convert datetime to str
        
        # Return data as a downloadable file
        return Response(data_str, mimetype="application/json",
                        headers={"Content-Disposition": "attachment;filename=db_dump.json"})
    except Exception as e:
        return f"Error while fetching database dump: {e}", 500

@app.route('/batch_upload', methods=['POST'])
def batch_upload():
    # Get the batch size from the form data
    batch_size = int(request.form['batch_size'])

    language = request.form['language']

    
    # Call the uploadlexemes method
    success_count = bot.uploadlexemes(batch_size)  # We assume uploadlexemes will return the count of successful uploads.
    
    # Record the batch upload
    bot.record_batch_upload(batch_size, success_count, language)
    
    return 'Batch upload successful', 200


if __name__ == "__main__":
    app.run(debug=True, port=8619)

