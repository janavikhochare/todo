from datetime import datetime
import hashlib

import sqlite3

from flask import Flask, request
from flask_restful import Api, Resource

import spacy
from spacy import displacy
import parsedatetime as pdt
from datetime import datetime

# Load the English language model
nlp = spacy.load("en_core_web_sm")

# Create a ParseDateTime object
cal = pdt.Calendar()

# Function to preprocess the input text


def extract_task_and_date(input_text):
    task = ""
    due_date = None

    # Extract the due date using parsedatetime
    time_struct, parse_status = cal.parse(input_text)
    if parse_status:
        due_date = datetime(*time_struct[:6])

    # Extract the task using spaCy's NER and pattern matching
    doc = nlp(input_text)
    # search for the verb and the noun
    # remove everything related to the date
    doc = [token for token in doc if token.pos_ not in ("NUM", "SYM", "PUNCT", "SPACE", "DET")]
    doc = [token for token in doc if token.ent_type_ not in ("DATE", "TIME")]

    print("Tokens:", [token.text for token in doc])

    for token in doc:
        if token.pos_ == "VERB":
            task += token.lemma_
            break
    for token in doc:
        if token.pos_ == "NOUN":
            task += " " + token.lemma_
            break
    for token in doc:
        if token.pos_ == "ADP":
            task += " " + token.lemma_
            break
    for token in doc:
        if token.pos_ == "PROPN" and token.ent_type_ == "PERSON":
            task += " " + token.lemma_
            break

    return task.strip(), due_date

####

app = Flask(__name__)
api = Api(app)

conn = sqlite3.connect('todo.sqlite3', check_same_thread=False)


def authenticate_token(user_id, access_token):
    cursor = conn.execute(
        'SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()

    if user is None:
        return 404
    if user[5] != access_token:
        return 401
    return 200


class User(Resource):
    def post(self):
        # TODO: check if password is strong
        cursor = conn.execute(
            'SELECT * FROM users WHERE email = ?', (request.form['email'],))
        user = cursor.fetchone()
        if user is not None:
            return '', 409

        access_token = hashlib.md5(
            (request.form['email']).encode()).hexdigest()
        cursor = conn.execute(
            '''
            INSERT INTO users
            (email, password, first_name, last_name, access_token)
            VALUES (?, ?, ?, ?, ?)
            ''', (request.form['email'],
                  hashlib.md5(request.form['password'].encode()).hexdigest(),
                  request.form['first_name'], request.form['last_name'],
                  access_token)
        )
        conn.commit()

        user_id = cursor.lastrowid
        user = {
            'user_id': user_id,
            'email': request.form['email'],
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'access_token': access_token
        }
        return user, 201
    
    def get(self, user_id):
        status = authenticate_token(
            user_id, request.form['access_token'])
        if status != 200:
            return '', status

        cursor = conn.execute(
            'SELECT * FROM tasks WHERE user_id = ?', (user_id,))
        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                'task_id': row[0],
                'user_id': row[1],
                'task': row[2],
                'datetime': row[3],
                'priority': row[4],
                'status': row[5]
            })
        return tasks, 200


class Task(Resource):
    def post(self):
        status = authenticate_token(
            request.form['user_id'], request.form['access_token'])
        if status != 200:
            return '', status

        today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
        op_task, op_time = extract_task_and_date(request.form['task'])
        op_time = op_time.strftime('%Y-%m-%d %H:%M:%S')
        cursor = conn.execute(
            '''
            INSERT INTO tasks (user_id, task, datetime, priority, status)
            VALUES (?, ?, ?, ?, ?)
            ''', (request.form['user_id'], op_task, op_time,
                  request.form['priority'], request.form['status'])
        )
        conn.commit()
        task_id = cursor.lastrowid
        
        print(op_time, op_task)
        task = {
            'task_id': task_id,
            'user_id': request.form['user_id'],
            'task': op_task,
            'datetime': op_time,
            'priority': request.form['priority'],
            'status': request.form['status']
        }
        return task, 201

    def put(self, task_id):
        status = authenticate_token(
            request.form['user_id'], request.form['access_token'])
        if status != 200:
            return '', status

        today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        op_task, op_time = extract_task_and_date(request.form['task'])
        op_time = op_time.strftime('%Y-%m-%d %H:%M:%S')

        conn.execute('''
        UPDATE tasks
        SET task = ?, datetime = ?, priority = ?, status = ?
        WHERE task_id = ?
        ''', (
            op_task, op_time,
            request.form['priority'], request.form['status'], task_id)
        )
        conn.commit()

        task = {
            'task_id': task_id,
            'task': op_task,
            'datetime': op_time,
            'priority': request.form['priority'],
            'status': request.form['status']
        }
        return task, 200

    def delete(self, task_id):
        status = authenticate_token(
            request.form['user_id'], request.form['access_token'])
        if status != 200:
            return '', status

        conn.execute('DELETE FROM tasks WHERE task_id = ?', (task_id,))
        conn.commit()
        return '', 204


api.add_resource(User, '/users/', '/users/<int:user_id>')
api.add_resource(Task, '/tasks/', '/tasks/<string:task_id>')


if __name__ == '__main__':
    app.run(debug=True)
