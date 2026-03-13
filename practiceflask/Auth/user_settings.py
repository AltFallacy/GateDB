import sqlite3

class UserSettings:
    DB_NAME = "user_settings.db"

    def create_table(self):
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()
        
        # We store credentials per user, per environment (Central vs Personal), per DB type
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                env_type TEXT,
                db_type TEXT,
                host TEXT,
                username TEXT,
                password TEXT,
                database_name TEXT,
                UNIQUE(user_id, env_type, db_type)
            )
        """)
        conn.commit()
        conn.close()

    def save_setting(self, user_id, env_type, db_type, host, username, password, database_name):
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()
        
        # Upsert logic: if setting exists for this user/env/db, update it. Otherwise insert.
        cursor.execute("""
            INSERT INTO settings (user_id, env_type, db_type, host, username, password, database_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, env_type, db_type) DO UPDATE SET
                host=excluded.host,
                username=excluded.username,
                password=excluded.password,
                database_name=excluded.database_name
        """, (user_id, env_type, db_type, host, username, password, database_name))
        
        conn.commit()
        conn.close()

    def get_setting(self, user_id, env_type, db_type):
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT host, username, password, database_name 
            FROM settings 
            WHERE user_id = ? AND env_type = ? AND db_type = ?
        """, (user_id, env_type, db_type))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "host": result[0],
                "username": result[1],
                "password": result[2],
                "database_name": result[3]
            }
        return None

    def get_all_settings(self, user_id):
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT env_type, db_type, host, username, database_name 
            FROM settings 
            WHERE user_id = ?
        """, (user_id,))
        
        results = cursor.fetchall()
        conn.close()
        return results

    def delete_setting(self, user_id, env_type, db_type):
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM settings 
            WHERE user_id = ? AND env_type = ? AND db_type = ?
        """, (user_id, env_type, db_type))
        
        conn.commit()
        conn.close()
