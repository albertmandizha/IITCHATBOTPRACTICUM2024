import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app, origins=['*'])
CORS(app, allow_headers=['Content-Type', 'Authorization'])

# MySQL database
conn = mysql.connector.connect(host="localhost", user="root", passwd="sahil11", db="pj")

@app.route('/sendMessage', methods=['POST'])
def send_message():
    data = request.get_json()
    message = data.get('message')  # Use .get() to safely retrieve message, it returns None if not found
    
    if message:
        # Handle regular message query
        cursor = conn.cursor()
        cursor.execute("SELECT answer_text FROM answers a JOIN questions q ON a.question_id = q.question_id WHERE q.question_text = %s", (message,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            response = result[0]
        else:
            response = "Please email admission@iit.edu for assistance."
            insert_cursor = conn.cursor()
            insert_query = "INSERT INTO questions (question_text) VALUES (%s)"
            insert_cursor.execute(insert_query, (message,))
            conn.commit()
            insert_cursor.close()
        time.sleep(1)
        return jsonify({'message': response})

    else:
        # Handle action query
        action = data.get('action')
        cursor = conn.cursor()
        cursor.execute("SELECT q.question_text, a.answer_text FROM questions q JOIN answers a ON q.question_id = a.question_id JOIN question_tags qt ON q.question_id = qt.question_id JOIN tags t ON qt.tag_id = t.tag_id WHERE t.tag_name = %s LIMIT 3", (action,))
        result = cursor.fetchall()
        cursor.close()

        if result:
            # Construct a list of dictionaries containing questions and answers
            response = [{'question': row[0], 'answer': row[1]} for row in result]
        else:
            # If no results found, provide a default response
            response = [{'question': "Please email admission@iit.edu for assistance.", 'answer': ""}]

        time.sleep(1)
        return jsonify({'actions': response})
    

@app.route('/getTopActions', methods=['GET'])
def get_top_actions():
    cursor = conn.cursor()
    cursor.execute("SELECT tag_name FROM tags")
    tags = [row[0] for row in cursor.fetchall()]
    cursor.close()

    if tags:
        response = [{'action': tag} for tag in tags]
    else:
        response = [{'action': 'Fees'}, {'action': 'Grants'}, {'action': 'Admission'}, {'action': 'Policies'}, {'action': 'Scholarships'}]

    return jsonify({'actions': response})


if __name__ == '__main__':
    app.run(debug=True)