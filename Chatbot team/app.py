import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app, origins=['*'])
CORS(app, allow_headers=['Content-Type', 'Authorization'])

# MySQL database
conn = mysql.connector.connect(host="localhost", user="root", passwd="sahil11", db="p1")

@app.route('/sendMessage', methods=['POST'])
def send_message():
    # Retrieve message from request
    if():
        data = request.get_json()
        message = data['message']
        
        # Database operations
        cursor = conn.cursor()
        cursor.execute("SELECT ans FROM chat_responses WHERE ques = %s", (message,))
        result = cursor.fetchone()
        if result:
            response = result[0]
        else:
            response = "Please email admission@iit.edu for assistance."
            insert_cursor = conn.cursor()
            insert_query = "INSERT INTO unanswered (ques) VALUES (%s)"
            insert_cursor.execute(insert_query, (message,))
            conn.commit()
            insert_cursor.close()
        
        # Close cursor
        cursor.close()
        time.sleep(1)
        return jsonify({'message': response})
    else:
        data = request.get_json()
        message = data['action']
        
        # Database operations
        cursor = conn.cursor()
        cursor.execute("SELECT ques FROM chat_responses WHERE tag = %s LIMIT 3", (message,))
        result = cursor.fetchall()
        if result:
            response = result
        else:
            response = "Please email admission111@iit.edu for assistance."
        # Close cursor
        cursor.close()
        time.sleep(1)
        return jsonify({'message': response})

if __name__ == '__main__':
    app.run(debug=True)
