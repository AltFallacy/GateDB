import sqlite3

class UserNotes:
    DB_NAME = "user_settings.db"

    def create_table(self):
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                user_id INTEGER PRIMARY KEY,
                content TEXT
            )
        """)
        conn.commit()
        conn.close()

    def save_note(self, user_id, content):
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notes (user_id, content)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                content=excluded.content
        """, (user_id, content))
        conn.commit()
        conn.close()

    def get_note(self, user_id):
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM notes WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else ""
