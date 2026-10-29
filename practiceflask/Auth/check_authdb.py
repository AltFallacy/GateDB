from sqlite3 import connect
from werkzeug.security import check_password_hash
from Auth.db_config import get_db_path

AUTH_DB = get_db_path("auth.db")

def authenticate(username, password):
    conn = connect(AUTH_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user[2], password):
        return user
    return None