from sqlite3 import connect

class sq3_conns:
    def __init__(self,path):
        self.path=path
    def connect(self):
        return connect(self.path)

    def execute(self, query, params=None):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        q_lower = query.strip().lower()
        if q_lower.startswith(("select", "show", "describe", "explain", "pragma")):
            result = cursor.fetchall()
            conn.close()
            return result
        conn.commit()
        conn.close()
        return True
