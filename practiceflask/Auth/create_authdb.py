from sqlite3 import connect
from werkzeug.security import generate_password_hash
def create_authdb():
    conn = connect("auth.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash blob, role TEXT)")
    conn.commit()
    conn.close()
    return True
def password_hash(password):
    return generate_password_hash(password)
def insert_user(username, password, role):
    conn = connect("auth.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (username, password_hash(password), role))
    conn.commit()
    conn.close()
    return True

def get_user_by_username(username):
    conn = connect("auth.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = connect("auth.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user
