import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from sentence_transformers import SentenceTransformer
import torch
import numpy as np

app = Flask(__name__)
CORS(app, origins=['*'])
CORS(app, allow_headers=['Content-Type', 'Authorization'])

# MySQL database
conn = mysql.connector.connect(host="localhost", user="root", passwd="sahil11", db="pj")

# Load the SentenceTransformer model
model_name = 'all-MiniLM-L6-v2'
model = SentenceTransformer(model_name)

@app.route('/getToptags', methods=['GET'])
def get_top_tags():
    cursor = conn.cursor()
    cursor.execute("SELECT tag_name FROM tags")
    tags = [row[0] for row in cursor.fetchall()]
    cursor.close()

    if tags:
        response = [{'tag': tag} for tag in tags]
    else:
        response = [{'tag': 'Fees'}, {'tag': 'Grants'}, {'tag': 'Admission'}, {'tag': 'Policies'}, {'tag': 'Scholarships'}]

    return jsonify({'tags': response})

@app.route('/tagQuestions', methods=['POST'])
def tag_questions():
    data = request.get_json()
    tag = data.get('tag')

    cursor = conn.cursor()
    cursor.execute("SELECT q.question_text FROM questions q JOIN question_tags qt ON q.question_id = qt.question_id JOIN tags t ON qt.tag_id = t.tag_id WHERE t.tag_name = %s LIMIT 3", (tag,))
    questions = [row[0] for row in cursor.fetchall()]
    cursor.close()

    response = {'questions': questions}
    return jsonify(response)

@app.route('/sendMessage', methods=['POST'])
def send_message():
    data = request.get_json()
    user_input = data.get('input')

    if user_input.isdigit():
        # Handle question ID
        question_id = int(user_input)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT q.question_text, a.answer_text, GROUP_CONCAT(o.option_text) AS options
            FROM questions q
            JOIN answers a ON q.question_id = a.question_id
            LEFT JOIN options o ON a.answer_id = o.answer_id
            WHERE q.question_id = %s
            GROUP BY a.answer_id
        """, (question_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:

            response = {
                'answer': result[1],
                'options': result[2].split(',') if result[2] else [] 
            }
            print(response)

        else:
            response = {
                'answer': "Please email admission@iit.edu for assistance.",
                'options': []
            }

    else:
        # Handle user message
        user_question = user_input
        cursor = conn.cursor()
        cursor.execute("""
            SELECT q.question_text, a.answer_id, a.answer_text, GROUP_CONCAT(o.option_text) AS options
            FROM questions q
            JOIN answers a ON q.question_id = a.question_id
            LEFT JOIN options o ON a.answer_id = o.answer_id
            WHERE q.question_text = %s
            GROUP BY a.answer_id
        """, (user_question,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            response = {
                'question': result[0],
                'answer_id': result[1],  # Using the answer_id from the result tuple
                'answer': result[2],
                'options': result[3].split(',') if result[3] else []
            }
        else:
            response = {
                'answer': "Please email admission@iit.edu for assistance.",
                'options': []
            }

    time.sleep(1)
    return jsonify(response)

@app.route('/clientTopThree', methods=['POST'])
def client_top_three():
    data = request.get_json()
    user_question = data.get('message')

    if user_question:
        # Get question vectors from the database
        cursor = conn.cursor()
        cursor.execute("SELECT question_id, vector FROM vectors")
        question_vectors = cursor.fetchall()
        cursor.close()

        # Convert question vectors to tensor format
        question_ids = [row[0] for row in question_vectors]
        embeddings = [torch.tensor(eval(row[1])) for row in question_vectors]
        question_embeddings = torch.stack(embeddings)

        # Encode user question and find top matches
        user_question_embedding = model.encode([user_question])[0]
        user_question_embedding = torch.tensor(user_question_embedding).unsqueeze(0)
        cosine_similarities = torch.nn.functional.cosine_similarity(user_question_embedding, question_embeddings, dim=1).numpy()
        top_matches_indices = np.argsort(cosine_similarities)[-4:][::-1]

        # Get top matching questions
        top_matches = []
        for idx in top_matches_indices:
            if cosine_similarities[idx] >= 0.7:
                question_id = question_ids[idx]
                cursor = conn.cursor()
                cursor.execute("SELECT question_text FROM questions WHERE question_id = %s", (question_id,))
                question_text = cursor.fetchone()[0]
                cursor.close()
                top_matches.append(question_text)

        if top_matches:
            response = {'questions': top_matches + ['None of the Above']}
        else:
            response = {
                'answer': "Please email admission@iit.edu for assistance.",
                'options': []
            }

        time.sleep(1)
        return jsonify(response)

    else:
        response = {
            'answer': "Please email admission@iit.edu for assistance.",
            'options': []
        }

        time.sleep(1)
        return jsonify(response)

@app.route('/clientAns', methods=['POST'])
def client_ans():
    data = request.get_json()
    question = data.get('question')

    cursor = conn.cursor()
    cursor.execute("""
        SELECT q.question_text, a.answer_text, GROUP_CONCAT(o.option_text) AS options
        FROM questions q
        JOIN answers a ON q.question_id = a.question_id
        LEFT JOIN options o ON a.answer_id = o.answer_id
        WHERE q.question_text = %s
        GROUP BY a.answer_id
    """, (question,))
    result = cursor.fetchone()
    cursor.close()

    if result:
        response = {
            'question': result[0],
            'answer': result[1],
            'options': result[2].split(',') if result[2] else []
        }
    else:
        response = {
            'answer': "Please email admission@iit.edu for assistance.",
            'options': []
        }

    time.sleep(1)
    return jsonify(response)

@app.route('/getOptionAnswer', methods=['POST'])
def get_option_answer():
    data = request.get_json()
    answer_id = data.get('answer_id')
    option_text = data.get('option_text')

    cursor = conn.cursor()
    cursor.execute("""
        SELECT option_answer
        FROM options
        WHERE answer_id = %s AND option_text = %s
    """, (answer_id, option_text))
    result = cursor.fetchone()
    cursor.close()

    if result:
        option_answer = result[0]
        response = {
            'answer_id': answer_id,
            'option_text': option_text,
            'option_answer': option_answer
        }
    else:
        response = {
            'answer': "Sorry, we couldn't find the requested option.",
            'options': []
        }

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)