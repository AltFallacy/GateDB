import mysql.connector
class mysql_conns:
    def __init__(self,host,user,password,database):
        self.config={
            "host": host,
            "user": user,
            "password": password,
            "database": database
        }
    def connect(self):
        return mysql.connector.connect(**self.config)

    def execute(self, query, params=None):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        q_lower = query.strip().lower()
        if q_lower.startswith(("select", "show", "describe", "explain")):
            result = cursor.fetchall()
            conn.close()
            return result
        else:
            conn.commit()
            conn.close()
        return True