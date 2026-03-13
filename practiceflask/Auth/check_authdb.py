from sqlite3 import connect
from werkzeug.security import check_password_hash
def authenticate(username, password):
    conn = connect("auth.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user[2], password):
        return user
    return None