import sqlite3
import os

def get_db_connection():
    """
    建立並回傳資料庫連線。
    使用 sqlite3.Row 讓查詢結果可以用欄位名稱取值。
    """
    db_path = os.path.join('instance', 'database.db')
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        raise

class UserModel:
    """
    處理 users 資料表的 CRUD 操作
    """
    
    @staticmethod
    def create(data):
        """
        新增一筆使用者記錄。
        :param data: dict，包含 username, password_hash, (可選) target_carbon_emission
        :return: 新增的使用者 ID，若失敗則回傳 None
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            target_carbon_emission = data.get('target_carbon_emission', 0.0)
            cursor.execute(
                'INSERT INTO users (username, password_hash, target_carbon_emission) VALUES (?, ?, ?)',
                (data['username'], data['password_hash'], target_carbon_emission)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error creating user: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_all():
        """
        取得所有使用者記錄。
        :return: list of sqlite3.Row，若失敗則回傳空 list
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users')
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting all users: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_by_id(user_id):
        """
        取得單筆使用者記錄。
        :param user_id: int, 使用者 ID
        :return: sqlite3.Row 或 None
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error getting user by ID: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_username(username):
        """
        根據 username 取得使用者記錄 (供登入驗證使用)。
        :param username: str, 使用者名稱
        :return: sqlite3.Row 或 None
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error getting user by username: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def update(user_id, data):
        """
        更新使用者記錄。
        :param user_id: int, 使用者 ID
        :param data: dict，包含欲更新的欄位
        :return: bool，成功回傳 True，失敗回傳 False
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # 動態產生 UPDATE 語法
            set_clause = []
            values = []
            for key, value in data.items():
                set_clause.append(f"{key} = ?")
                values.append(value)
            
            if not set_clause:
                return False
                
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(set_clause)} WHERE id = ?"
            
            cursor.execute(query, tuple(values))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating user: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(user_id):
        """
        刪除使用者記錄。
        :param user_id: int, 使用者 ID
        :return: bool，成功回傳 True，失敗回傳 False
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting user: {e}")
            return False
        finally:
            conn.close()

class CarbonRecordModel:
    """
    處理 carbon_records 資料表的 CRUD 操作
    """
    
    @staticmethod
    def create(data):
        """
        新增一筆碳排記錄。
        :param data: dict，包含 user_id, category, action_name, parameter_value, carbon_amount, (可選) suggestion
        :return: 新增的記錄 ID，若失敗則回傳 None
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            suggestion = data.get('suggestion', None)
            cursor.execute(
                '''INSERT INTO carbon_records 
                   (user_id, category, action_name, parameter_value, carbon_amount, suggestion) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (data['user_id'], data['category'], data['action_name'], 
                 data['parameter_value'], data['carbon_amount'], suggestion)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error creating carbon record: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_all():
        """
        取得所有碳排記錄。
        :return: list of sqlite3.Row，若失敗則回傳空 list
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM carbon_records')
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting all carbon records: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_by_user_id(user_id):
        """
        取得特定使用者的所有碳排記錄。
        :param user_id: int, 使用者 ID
        :return: list of sqlite3.Row，若失敗則回傳空 list
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM carbon_records WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting records by user ID: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_by_id(record_id):
        """
        取得單筆碳排記錄。
        :param record_id: int, 記錄 ID
        :return: sqlite3.Row 或 None
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM carbon_records WHERE id = ?', (record_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error getting record by ID: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def update(record_id, data):
        """
        更新碳排記錄。
        :param record_id: int, 記錄 ID
        :param data: dict，包含欲更新的欄位
        :return: bool，成功回傳 True，失敗回傳 False
        """
        conn = get_db_connection()
        try:
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
            
            cursor.execute(query, tuple(values))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating record: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(record_id):
        """
        刪除碳排記錄。
        :param record_id: int, 記錄 ID
        :return: bool，成功回傳 True，失敗回傳 False
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM carbon_records WHERE id = ?', (record_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting record: {e}")
            return False
        finally:
            conn.close()
