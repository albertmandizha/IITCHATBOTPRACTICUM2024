import csv
from flask import Flask, request, jsonify
import os
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app, origins=['*'])
CORS(app, allow_headers=['Content-Type', 'Authorization'])

# MySQL database
conn = mysql.connector.connect(host="localhost", user="root", passwd="sahil11", db="p1")

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_csv(file_content):
    parsed_data = []
    rows = csv.reader(file_content.splitlines())
    next(rows)  # Skip the header row
    for row in rows:
        if len(row) != 3:
            return False, "File does not have the expected number of columns"
        parsed_data.append(row)
    return True, parsed_data

def insert_into_database(data):
    cursor = conn.cursor()
    try:
        if data:
            cursor.executemany("INSERT INTO chat_responses (ques, ans, tag) VALUES (%s, %s, %s)", data)
            conn.commit()
            return True, "Data inserted into the database successfully"
    except Exception as e:
        conn.rollback()
        return False, f"Error inserting data into the database: {str(e)}"
    finally:
        cursor.close()

@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist('files')
    file_contents = {}
    for file in files:
        if file and allowed_file(file.filename):
            file_contents[file.filename] = file.read().decode('utf-8')
        else:
            return jsonify({'error': 'Only CSV files are allowed'}), 400
    
    success = False
    message = None

    for file_name, file_content in file_contents.items():
        if file_name.endswith('.csv'):
            success, parsed_data = parse_csv(file_content)
            if success:
                success, message = insert_into_database(parsed_data)
                if not success:
                    break
            else:
                message = "Error parsing CSV file"
                break
        else:
            message = "Only CSV files are allowed"
            break

    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'error': message}), 400

if __name__ == "__main__":
    app.run(port=5001)
