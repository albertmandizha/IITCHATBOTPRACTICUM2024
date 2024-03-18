import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from collections import Counter

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
        time.sleep(1)
        return jsonify({'message': response})

    else:
        # Handle action query
        action = data.get('action')
        cursor = conn.cursor()
        cursor.execute("SELECT ques, ans FROM chat_responses WHERE tag = %s LIMIT 3", (action,))
        result = cursor.fetchall()
        cursor.close()

        if result:
            # Construct a list of dictionaries containing questions and answers
            response = [{'question': row[0]} for row in result]
            print(response)
        else:
            # If no results found, provide a default response
            response = [{'question': "Please email admission111@iit.edu for assistance."}]

        time.sleep(1)
        return jsonify({'actions': response})
    

@app.route('/getTopActions', methods=['GET'])
def get_top_actions():
    cursor = conn.cursor()
    cursor.execute("SELECT tag FROM chat_responses")
    tags = [row[0] for row in cursor.fetchall()]
    cursor.close()

    if tags:
        top_actions = Counter(tags).most_common(5)
        response = [{'action': action} for action, count in top_actions]
    else:
        response = [{'action': 'Fees'}, {'action': 'Grants'}, {'action': 'Admission'}, {'action': 'Policies'}, {'action': 'Scholarships'}]

    return jsonify({'actions': response})


if __name__ == '__main__':
    app.run(debug=True)
