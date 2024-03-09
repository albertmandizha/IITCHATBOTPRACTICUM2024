from flask import Flask, render_template, jsonify, request, make_response
import mysql.connector
from flask_cors import CORS
import csv
from io import StringIO

app = Flask(__name__)
CORS(app, origins=['*'])
CORS(app, allow_headers=['Content-Type', 'Authorization'])

conn = mysql.connector.connect(host="localhost", user="root", passwd="sahil11", db="p1")
cursor = conn.cursor()


@app.route('/get_data/<button_id>')
def get_data(button_id):
    if button_id == 'chatResponsesBtn':
        cursor.execute("SELECT id, ques, ans, tag FROM chat_responses")
        data = cursor.fetchall()
        return jsonify(data)
    elif button_id == 'qaTableBtn':
        cursor.execute("SELECT qa_id, question, answer FROM qa_table")
        data = cursor.fetchall()
        return jsonify(data)
    elif button_id == 'qaTagsBtn':
        cursor.execute("SELECT qa_id, tag_id FROM qa_tags")
        data = cursor.fetchall()
        return jsonify(data)
    elif button_id == 'tagTableBtn':
        cursor.execute("SELECT tag_id, tag_name FROM tags_table")
        data = cursor.fetchall()
        return jsonify(data)
    elif button_id == 'unansweredBtn':
        cursor.execute("SELECT ques, ans FROM unanswered")
        data = cursor.fetchall()
        return jsonify(data)

@app.route('/download_qa_table')
def download_qa_table():
    cursor.execute("SELECT qa_id, question, answer FROM qa_table")
    data = cursor.fetchall()

    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerow(['QA ID', 'Question Text', 'Answer Text'])
    csv_writer.writerows(data)

    response = make_response(csv_buffer.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=qa_table.csv'
    response.headers['Content-Type'] = 'text/csv'

    return response


if __name__ == '__main__':
    app.run(debug=True,port=5000)