from datetime import datetime
import hashlib

import sqlite3

from flask import Flask, request
from flask_restful import Api, Resource


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


if __name__ == '__main__':
    app.run(debug=True)
