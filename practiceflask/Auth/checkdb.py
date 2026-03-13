from sqlite3 import connect
from werkzeug.security import check_password_hash
def checkdb():
    conn = connect("auth.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    users = cursor.fetchall()
    conn.close()
    return users

print(checkdb())