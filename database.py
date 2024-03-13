import sqlite3


def create_user_table(conn):
    # create the users table
    conn.execute('''
    CREATE TABLE IF NOT EXISTS users
    (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        access_token TEXT
    );
    ''')


def create_tasks_table(conn):
    # create the tasks table
    conn.execute('''
    CREATE TABLE IF NOT EXISTS tasks
    (
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        task TEXT NOT NULL,
        datetime DATETIME NOT NULL,
        priority TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
    ''')


if __name__ == "__main__":
    conn = sqlite3.connect('todo.sqlite3')
    create_user_table(conn)
    create_tasks_table(conn)
