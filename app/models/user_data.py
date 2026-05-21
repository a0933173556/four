import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'database.db')

def get_db_connection():
    """
    建立並回傳 SQLite 資料庫連線
    設定 row_factory 讓查詢結果可以用欄位名稱存取
    """
    # 確保 instance 目錄存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class User:
    @staticmethod
    def create(data):
        """
        新增一位使用者
        :param data: dict, 包含 'username', 'password_hash', 'target_carbon_emission'
        :return: int, 新增的 user id，若失敗回傳 None
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password_hash, target_carbon_emission)
                VALUES (?, ?, ?)
            ''', (data.get('username'), data.get('password_hash'), data.get('target_carbon_emission', 0)))
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return last_id
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    @staticmethod
    def get_all():
        """
        取得所有使用者
        :return: list of sqlite3.Row
        """
        try:
            conn = get_db_connection()
            users = conn.execute('SELECT * FROM users').fetchall()
            conn.close()
            return users
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []

    @staticmethod
    def get_by_id(user_id):
        """
        根據 ID 取得單一使用者
        :param user_id: int
        :return: sqlite3.Row, 若找不到回傳 None
        """
        try:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            conn.close()
            return user
        except Exception as e:
            print(f"Error getting user by id: {e}")
            return None

    @staticmethod
    def get_by_username(username):
        """
        根據 username 取得單一使用者 (登入時使用)
        :param username: str
        :return: sqlite3.Row, 若找不到回傳 None
        """
        try:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()
            return user
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None

    @staticmethod
    def update(user_id, data):
        """
        更新使用者資料
        :param user_id: int
        :param data: dict, 包含要更新的欄位
        :return: bool, 成功為 True
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            set_clause = []
            values = []
            for key, value in data.items():
                set_clause.append(f"{key} = ?")
                values.append(value)
                
            if not set_clause:
                return False
                
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(set_clause)} WHERE id = ?"
            
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    @staticmethod
    def delete(user_id):
        """
        刪除使用者
        :param user_id: int
        :return: bool, 成功為 True
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False


class CarbonRecord:
    @staticmethod
    def create(data):
        """
        新增一筆碳排紀錄
        :param data: dict, 包含 user_id, category, action_name, parameter_value, carbon_amount, suggestion
        :return: int, 新增的 record id，若失敗回傳 None
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO carbon_records (user_id, category, action_name, parameter_value, carbon_amount, suggestion)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data.get('user_id'),
                data.get('category'),
                data.get('action_name'),
                data.get('parameter_value'),
                data.get('carbon_amount'),
                data.get('suggestion')
            ))
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return last_id
        except Exception as e:
            print(f"Error creating carbon record: {e}")
            return None

    @staticmethod
    def get_all(user_id=None):
        """
        取得所有碳排紀錄，若提供 user_id 則只取該使用者的紀錄
        :param user_id: int (optional)
        :return: list of sqlite3.Row
        """
        try:
            conn = get_db_connection()
            if user_id:
                records = conn.execute(
                    'SELECT * FROM carbon_records WHERE user_id = ? ORDER BY created_at DESC', 
                    (user_id,)
                ).fetchall()
            else:
                records = conn.execute('SELECT * FROM carbon_records ORDER BY created_at DESC').fetchall()
            conn.close()
            return records
        except Exception as e:
            print(f"Error getting carbon records: {e}")
            return []

    @staticmethod
    def get_by_id(record_id):
        """
        根據 ID 取得單一碳排紀錄
        :param record_id: int
        :return: sqlite3.Row, 若找不到回傳 None
        """
        try:
            conn = get_db_connection()
            record = conn.execute('SELECT * FROM carbon_records WHERE id = ?', (record_id,)).fetchone()
            conn.close()
            return record
        except Exception as e:
            print(f"Error getting carbon record by id: {e}")
            return None

    @staticmethod
    def update(record_id, data):
        """
        更新碳排紀錄
        :param record_id: int
        :param data: dict, 包含要更新的欄位
        :return: bool, 成功為 True
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            set_clause = []
            values = []
            for key, value in data.items():
                set_clause.append(f"{key} = ?")
                values.append(value)
                
            if not set_clause:
                return False
                
            values.append(record_id)
            query = f"UPDATE carbon_records SET {', '.join(set_clause)} WHERE id = ?"
            
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating carbon record: {e}")
            return False

    @staticmethod
    def delete(record_id):
        """
        刪除碳排紀錄
        :param record_id: int
        :return: bool, 成功為 True
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM carbon_records WHERE id = ?', (record_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting carbon record: {e}")
            return False
