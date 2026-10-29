from sqlite3 import connect
from werkzeug.security import generate_password_hash
from Auth.db_config import get_db_path

AUTH_DB = get_db_path("auth.db")

def create_authdb():
    conn = connect(AUTH_DB)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash blob, role TEXT)")
    conn.commit()
    conn.close()
    return True

def password_hash(password):
    return generate_password_hash(password)

def insert_user(username, password, role):
    conn = connect(AUTH_DB)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (username, password_hash(password), role))
    conn.commit()
    conn.close()
    return True

def get_user_by_username(username):
    conn = connect(AUTH_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = connect(AUTH_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user
