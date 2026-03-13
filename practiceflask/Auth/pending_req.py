from sqlite3 import connect

class PendingReq:

    DB_NAME = "pending_req.db"

    def create_table(self):
        conn = connect(self.DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_requests (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                sql_query TEXT,
                status TEXT,
                created_at TEXT,
                processed_by INTEGER,
                processed_at TEXT,
                db_type TEXT,
                result TEXT
            )
        """)

        conn.commit()
        conn.close()

    def insert_req(self, user_id, sql_query, db_type, status, created_at, processed_by, processed_at):
        conn = connect(self.DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO pending_requests 
            (user_id, sql_query, db_type, status, created_at, processed_by, processed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, sql_query, db_type, status, created_at, processed_by, processed_at))

        conn.commit()
        conn.close()

    def get_req(self, request_id):
        conn = connect(self.DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM pending_requests WHERE id = ?",
            (request_id,)
        )

        result = cursor.fetchone()
        conn.close()
        return result

    def __init__(self):
        from datetime import datetime
        self.datetime = datetime

    def get_all_req(self):
        conn = connect(self.DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM pending_requests WHERE status = 'pending'")
        results = cursor.fetchall()
        conn.close()
        return results

    def get_user_reqs(self, user_id):
        conn = connect(self.DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM pending_requests WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        results = cursor.fetchall()
        conn.close()
        return results

    def mark_approved(self, request_id, processed_by, result_string):
        conn = connect(self.DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE pending_requests SET status = 'approved', processed_by = ?, processed_at = ?, result = ? WHERE id = ?",
            (processed_by, self.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), result_string, request_id)
        )
        conn.commit()
        conn.close()

    def mark_rejected(self, request_id, processed_by):
        conn = connect(self.DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE pending_requests SET status = 'rejected', processed_by = ?, processed_at = ? WHERE id = ?",
            (processed_by, self.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), request_id)
        )
        conn.commit()
        conn.close()

    def delete_req(self, request_id):
        conn = connect(self.DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM pending_requests WHERE id = ?",
            (request_id,)
        )
        conn.commit()
        conn.close()