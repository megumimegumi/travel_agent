import mysql.connector
import json
from datetime import datetime

class MemoryService:
    def __init__(self):
        # Database Configuration
        self.config = {
            'user': 'Megumi',
            'password': '09231110jthJTH.',
            'host': 'localhost',
            'auth_plugin': 'mysql_native_password' 
        }
        self.db_name = 'travel_agent_memory'
        self._ensure_db()

    def _get_conn(self, db=None):
        try:
            cfg = self.config.copy()
            if db:
                cfg['database'] = db
            return mysql.connector.connect(**cfg)
        except mysql.connector.Error as err:
            print(f"Connection Error: {err}")
            raise

    def _ensure_db(self):
        try:
            # 1. Connect without DB to create it
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
            conn.close()
            
            # 2. Connect with DB to create table
            conn = self._get_conn(self.db_name)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_name VARCHAR(255) NOT NULL,
                    query_data JSON,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"DB Initialization Warning: {e}")

    def add_record(self, user_name: str, query_dict: dict):
        """Add user query record and maintain max 20 records limit"""
        try:
            conn = self._get_conn(self.db_name)
            cursor = conn.cursor()
            
            # Serialize data
            json_str = json.dumps(query_dict, ensure_ascii=False)
            
            # Insert
            insert_sql = "INSERT INTO user_history (user_name, query_data) VALUES (%s, %s)"
            cursor.execute(insert_sql, (user_name, json_str))
            
            # Cleanup: Keep only last 20
            # Find IDs to delete
            cursor.execute("SELECT id FROM user_history WHERE user_name = %s ORDER BY created_at DESC", (user_name,))
            rows = cursor.fetchall()
            
            if len(rows) > 20:
                # rows[20:] are the ones to delete (since we ordered DESC, 0-19 are newest)
                # No, wait. 0 is newest. So index 20 is the 21st item.
                ids_to_delete = [str(r[0]) for r in rows[20:]]
                if ids_to_delete:
                    format_strings = ','.join(['%s'] * len(ids_to_delete))
                    delete_sql = f"DELETE FROM user_history WHERE id IN ({format_strings})"
                    cursor.execute(delete_sql, tuple(ids_to_delete))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding record: {e}")
            return False

    def get_user_history(self, user_name: str, limit: int = 5) -> str:
        """Get formatted history string for LLM context"""
        try:
            conn = self._get_conn(self.db_name)
            cursor = conn.cursor(dictionary=True)
            
            sql = "SELECT query_data, created_at FROM user_history WHERE user_name = %s ORDER BY created_at DESC LIMIT %s"
            cursor.execute(sql, (user_name, limit))
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                return ""
                
            history_text = "User's Recent Travel Requests:\n"
            for r in results:
                try:
                    data = json.loads(r['query_data']) if isinstance(r['query_data'], str) else r['query_data']
                    time_str = r['created_at'].strftime("%Y-%m-%d")
                    # Summarize the request
                    dest = data.get('destination', 'Unknown')
                    days = data.get('days', '?')
                    budget = data.get('budget', '?')
                    prefs = data.get('preferences', [])
                    history_text += f"- [{time_str}] To {dest}, {days} Days, Budget {budget}, Prefs: {prefs}\n"
                except:
                    continue
            
            return history_text
        except Exception as e:
            print(f"Error reading history: {e}")
            return ""
