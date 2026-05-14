import sqlite3
import logging

DB_PATH = 'instance/database.db'

def get_db_connection():
    """
    建立並回傳一個 SQLite 資料庫連線。
    使用 sqlite3.Row 讓查詢結果可以用欄位名稱取值。
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class User:
    """使用者資料表 (users) 的 Model 實作"""
    
    @staticmethod
    def create(data):
        """
        新增一筆使用者記錄
        :param data: dict，包含 username, password_hash, (可選) target_carbon_emission
        :return: 新增的資料 id，若失敗則回傳 None
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password_hash, target_carbon_emission)
                VALUES (?, ?, ?)
            ''', (data.get('username'), data.get('password_hash'), data.get('target_carbon_emission', 0)))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return new_id
        except Exception as e:
            logging.error(f"Error creating user: {e}")
            return None

    @staticmethod
    def get_all():
        """
        取得所有使用者記錄
        :return: list of sqlite3.Row
        """
        try:
            conn = get_db_connection()
            users = conn.execute('SELECT * FROM users').fetchall()
            conn.close()
            return users
        except Exception as e:
            logging.error(f"Error getting all users: {e}")
            return []

    @staticmethod
    def get_by_id(id):
        """
        取得單筆使用者記錄
        :param id: 使用者 ID
        :return: sqlite3.Row 或 None
        """
        try:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE id = ?', (id,)).fetchone()
            conn.close()
            return user
        except Exception as e:
            logging.error(f"Error getting user by id {id}: {e}")
            return None

    @staticmethod
    def get_by_username(username):
        """
        透過 username 取得單筆使用者記錄 (用於登入驗證)
        :param username: 使用者名稱
        :return: sqlite3.Row 或 None
        """
        try:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()
            return user
        except Exception as e:
            logging.error(f"Error getting user by username {username}: {e}")
            return None

    @staticmethod
    def update(id, data):
        """
        更新使用者記錄
        :param id: 使用者 ID
        :param data: dict，包含要更新的欄位 (如 target_carbon_emission)
        :return: bool，表示是否成功
        """
        try:
            conn = get_db_connection()
            # 這裡僅開放更新目標碳排量
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET target_carbon_emission = ? WHERE id = ?
            ''', (data.get('target_carbon_emission'), id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error updating user {id}: {e}")
            return False

    @staticmethod
    def delete(id):
        """
        刪除使用者記錄
        :param id: 使用者 ID
        :return: bool，表示是否成功
        """
        try:
            conn = get_db_connection()
            conn.execute('DELETE FROM users WHERE id = ?', (id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error deleting user {id}: {e}")
            return False


class CarbonRecord:
    """碳排紀錄表 (carbon_records) 的 Model 實作"""

    @staticmethod
    def create(data):
        """
        新增一筆碳排記錄
        :param data: dict，包含 user_id, category, action_name, parameter_value, carbon_amount, suggestion
        :return: 新增的資料 id，若失敗則回傳 None
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO carbon_records 
                (user_id, category, action_name, parameter_value, carbon_amount, suggestion)
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
            new_id = cursor.lastrowid
            conn.close()
            return new_id
        except Exception as e:
            logging.error(f"Error creating carbon record: {e}")
            return None

    @staticmethod
    def get_all():
        """
        取得所有碳排記錄
        :return: list of sqlite3.Row
        """
        try:
            conn = get_db_connection()
            records = conn.execute('SELECT * FROM carbon_records').fetchall()
            conn.close()
            return records
        except Exception as e:
            logging.error(f"Error getting all carbon records: {e}")
            return []

    @staticmethod
    def get_by_id(id):
        """
        取得單筆碳排記錄
        :param id: 記錄 ID
        :return: sqlite3.Row 或 None
        """
        try:
            conn = get_db_connection()
            record = conn.execute('SELECT * FROM carbon_records WHERE id = ?', (id,)).fetchone()
            conn.close()
            return record
        except Exception as e:
            logging.error(f"Error getting carbon record {id}: {e}")
            return None

    @staticmethod
    def get_by_user_id(user_id):
        """
        取得特定使用者的所有碳排記錄
        :param user_id: 使用者 ID
        :return: list of sqlite3.Row
        """
        try:
            conn = get_db_connection()
            records = conn.execute('SELECT * FROM carbon_records WHERE user_id = ? ORDER BY created_at DESC', (user_id,)).fetchall()
            conn.close()
            return records
        except Exception as e:
            logging.error(f"Error getting carbon records for user {user_id}: {e}")
            return []

    @staticmethod
    def update(id, data):
        """
        更新碳排記錄
        :param id: 記錄 ID
        :param data: dict，包含要更新的欄位
        :return: bool，表示是否成功
        """
        try:
            conn = get_db_connection()
            conn.execute('''
                UPDATE carbon_records 
                SET category = ?, action_name = ?, parameter_value = ?, carbon_amount = ?, suggestion = ?
                WHERE id = ?
            ''', (
                data.get('category'),
                data.get('action_name'),
                data.get('parameter_value'),
                data.get('carbon_amount'),
                data.get('suggestion'),
                id
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error updating carbon record {id}: {e}")
            return False

    @staticmethod
    def delete(id):
        """
        刪除碳排記錄
        :param id: 記錄 ID
        :return: bool，表示是否成功
        """
        try:
            conn = get_db_connection()
            conn.execute('DELETE FROM carbon_records WHERE id = ?', (id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error deleting carbon record {id}: {e}")
            return False
