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

@app.route('/sendMessage', methods=['POST'])
def send_message():
    data = request.get_json()
    user_question = data.get('message')  # Use .get() to safely retrieve message, it returns None if not found

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
        top_matches_indices = np.argsort(cosine_similarities)[-3:][::-1]

        # Get top matching questions and their answers
        top_matches = []
        for idx in top_matches_indices:
            if cosine_similarities[idx] >= 0.8:
                question_id = question_ids[idx]
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
                    top_matches.append({
                        'question': result[0],
                        'answer': result[1],
                        'options': result[2].split(',') if result[2] else []
                    })

        if top_matches:
            response = {'matches': top_matches}
        else:
            response = {
                'answer': "Please email admission@iit.edu for assistance.",
                'options': []
            }

        time.sleep(1)
        return jsonify(response)

    else:
        # Handle action query
        action = data.get('action')
        cursor = conn.cursor()
        cursor.execute("SELECT q.question_text, a.answer_text FROM questions q JOIN answers a ON q.question_id = a.question_id JOIN question_tags qt ON q.question_id = qt.question_id JOIN tags t ON qt.tag_id = t.tag_id WHERE t.tag_name = %s LIMIT 3", (action,))
        result = cursor.fetchall()
        cursor.close()

        if result:
            options = []
            for row in result:
                options.append({
                    'option': row[0],
                    'answer': row[1]
                })
            response = {'options': options}
        else:
            # If no results found, provide a default response
            response = {'answer': "Please email admission@iit.edu for assistance."}

        time.sleep(1)
        return jsonify(response)

@app.route('/getTopQuestions', methods=['POST'])
def get_top_questions():
    data = request.get_json()
    tag_name = data.get('tag_name')
    cursor = conn.cursor()
    cursor.execute("SELECT q.question_text FROM questions q JOIN question_tags qt ON q.question_id = qt.question_id JOIN tags t ON qt.tag_id = t.tag_id WHERE t.tag_name = %s LIMIT 3", (tag_name,))
    questions = [row[0] for row in cursor.fetchall()]
    cursor.close()

    if questions:
        response = {'questions': questions}
    else:
        response = {'message': 'No questions found for this tag.'}

    return jsonify(response)

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
