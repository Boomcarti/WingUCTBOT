import mysql.connector
from flask import Flask, request, jsonify
import json
import requests

# Create a connection to the database
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="aizen",
    database="lexdb",
    port=3306
)

# Create a cursor object to interact with the MySQL server
cursor = connection.cursor()

class WingUCTBOT:
    def __init__(self):
        self.url= "https://test.wikidata.org/w/api.php"
        self.session = requests.Session()

    def printlexemes(self,batchsize):
        cursor.execute(f"SELECT LexicalEntry_id FROM lexicalentry LIMIT {batchsize}")
        # Fetch and print the results
        results = cursor.fetchall()
        lexicalids = [row[0] for row in results]
        for i in lexicalids:
            lexical_entry_id=i
            query = (
                "SELECT l.Language_code "
                "FROM word AS w "
                "JOIN language AS l ON w.Language_id = l.Language_id "
                "WHERE w.LexicalEntry_id = %s"
            )
            cursor.execute(query, (lexical_entry_id,))

            # Fetch the result
            result = cursor.fetchone()
            language_code = result[0]
           # print(f"Language_code for LexicalEntry_id {lexical_entry_id}: {language_code}")
            query = (
                "SELECT word FROM word WHERE LexicalEntry_id = %s"
            )
            cursor.execute(query, (lexical_entry_id,))
            result = cursor.fetchone()
            word = result[0]
           # print(f"Word for LexicalEntry_id {lexical_entry_id}: {word}")
            query = (
                "SELECT GrammaticalCategory_name FROM grammaticalcategory WHERE LexicalEntry_id = %s"
            )
            cursor.execute(query, (lexical_entry_id,))
            result = cursor.fetchone()
            cat = result[0]
           # print(f"grammaticalcategory for LexicalEntry_id {lexical_entry_id}: {cat}")
            query = (
                "SELECT Language_id FROM word WHERE LexicalEntry_id = %s"
            )
            cursor.execute(query, (lexical_entry_id,))
            result = cursor.fetchone()
            lang = result[0]
            #print(f"grammaticalcategory for LexicalEntry_id {lexical_entry_id}: {lang}")
            print(" ")

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
                    "lexicalCategory": word,  # Shona language
                    "language": lang  # Word
                }),
                "format": "json",
              #  "token": CSRF_TOKEN
            }
            print(LEXEME_DATA)

    def uploadlexemes(self,batchsize):
        cursor.execute(f"SELECT LexicalEntry_id FROM lexicalentry LIMIT {batchsize}")
        # Fetch and print the results
        results = cursor.fetchall()
        lexicalids = [row[0] for row in results]
        for i in lexicalids:
            lexical_entry_id=i
            query = (
                "SELECT l.Language_code "
                "FROM word AS w "
                "JOIN language AS l ON w.Language_id = l.Language_id "
                "WHERE w.LexicalEntry_id = %s"
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
                "SELECT GrammaticalCategory_name FROM grammaticalcategory WHERE LexicalEntry_id = %s"
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

            LOGIN_TOKEN = self.session .get(url=self.url, params={
                "action": "query",
                "meta": "tokens",
                "type": "login",
                "format": "json"
            }).json()['query']['tokens']['logintoken']
    
            LOGIN_DATA = {
                "action": "login",
                "lgname": "Tadiwa Magwenzi",
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
                    "language": lang  # Word
                }),
                "format": "json",
                "token": CSRF_TOKEN
            }


            response = self.session.post(self.url, data=LEXEME_DATA)
    
            print(response.json())
    


bot = WingUCTBOT()

bot.printlexemes(2)
bot.uploadlexemes(2)








            
    

# Close the cursor and connection
cursor.close()
connection.close()
