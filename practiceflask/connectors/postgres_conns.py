try:
    import psycopg2
except ImportError:
    psycopg2 = None

class postgres_conns:
    def __init__(self, host, user, password, database):
        self.conn_info = f"host={host} dbname={database} user={user} password={password} port=5432"

    def connect(self):
        if not psycopg2:
            raise ImportError("psycopg2 not installed. Run 'pip install psycopg2-binary'")
        return psycopg2.connect(self.conn_info)

    def execute(self, query, params=None):
        try:
            with self.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params or ())
                    q_lower = query.strip().lower()
                    if q_lower.startswith(("select", "show", "describe", "explain")):
                        result = cur.fetchall()
                        return result
                    else:
                        conn.commit()
                        return True
        except Exception as e:
            return f"Error: {e}"
