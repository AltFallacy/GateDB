from sqlite3 import connect
from Auth.db_config import get_db_path

def checkdb():
    conn = connect(get_db_path("auth.db"))
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    users = cursor.fetchall()
    conn.close()
    return users

if __name__ == "__main__":
    print(checkdb())