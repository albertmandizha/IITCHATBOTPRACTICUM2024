import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app, origins=['*'])
CORS(app, allow_headers=['Content-Type', 'Authorization'])

#  MySQL database
conn = mysql.connector.connect(host= "localhost", user="root", passwd="sahil11", db="p1")

@app.route('/sendMessage', methods=['POST'])
def send_message():
    # Retrieve message from request
    data = request.get_json()
    message = data['message']
    print(message)
    # Database operations
    cursor = conn.cursor()
    cursor.execute("SELECT ans FROM chat_responses WHERE ques = %s", (message,))
    result = cursor.fetchone()
    print(result)
    if result:
        response = result[0]
    else:
        response = "Please email admission@iit.edu for assistance."
    
    # Close cursor
    cursor.close()
    time.sleep(2)
    return jsonify({'message': response})

if __name__ == '__main__':
    app.run(debug=True)
