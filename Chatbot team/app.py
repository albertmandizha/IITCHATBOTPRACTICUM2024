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
    data = request.get_json()
    message = data.get('message')  # Use .get() to safely retrieve message, it returns None if not found
    
    if message:
        # Handle regular message query
        cursor = conn.cursor()
        cursor.execute("SELECT ans FROM chat_responses WHERE ques = %s", (message,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            response = result[0]
        else:
            response = "Please email admission@iit.edu for assistance."
            insert_cursor = conn.cursor()
            insert_query = "INSERT INTO unanswered (ques) VALUES (%s)"
            insert_cursor.execute(insert_query, (message,))
            conn.commit()
            insert_cursor.close()

    else:
        # Handle action query
        message = data.get('action')
        cursor = conn.cursor()
        cursor.execute("SELECT ques, ans FROM chat_responses WHERE tag = %s LIMIT 3", (message,))
        result = cursor.fetchall()
        response_pairs = []
        for row in result:
            question, answer = row  # Extracting 'ques' and 'ans' from each row
            response_pairs.append({'question': question, 'answer': answer})  # Appending pairs to list
        print(response_pairs)
        cursor.close()

        if result:
            response = [item[0] for item in result]
            print(response)
        else:
            response = ["Please email admission111@iit.edu for assistance."]  # Ensure response is a list

    time.sleep(1)
    return jsonify({'message': response})


if __name__ == '__main__':
    app.run(debug=True)
