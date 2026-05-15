import sqlite3
import os

def get_db_connection():
    """
    建立並回傳一個與 SQLite 資料庫的連線。
    資料庫路徑設定為 instance/database.db。
    
    Returns:
        sqlite3.Connection: 資料庫連線物件。
    """
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

class UserModel:
    """
    負責 users 資料表的 CRUD 操作。
    """
    
    @staticmethod
    def create(data):
        """
        新增一筆使用者記錄。
        
        Args:
            data (dict): 包含 username, password_hash, target_carbon_emission 的字典。
            
        Returns:
            int: 新增成功的回傳記錄 ID，失敗則回傳 None。
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, target_carbon_emission) VALUES (?, ?, ?)",
                (data.get('username'), data.get('password_hash'), data.get('target_carbon_emission', 0))
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
        
        Returns:
            list: 包含所有使用者的 sqlite3.Row 物件列表。
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting users: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_by_id(user_id):
        """
        根據 ID 取得單筆使用者記錄。
        
        Args:
            user_id (int): 使用者的 ID。
            
        Returns:
            sqlite3.Row: 若找到則回傳該筆記錄，否則回傳 None。
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error getting user by id: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_username(username):
        """
        根據 username 取得單筆使用者記錄 (供登入驗證使用)。
        
        Args:
            username (str): 使用者名稱。
            
        Returns:
            sqlite3.Row: 若找到則回傳該筆記錄，否則回傳 None。
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
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
        
        Args:
            user_id (int): 欲更新的使用者 ID。
            data (dict): 包含要更新的欄位與對應值的字典。
            
        Returns:
            bool: 更新成功回傳 True，否則回傳 False。
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            set_clause = []
            params = []
            for key, value in data.items():
                set_clause.append(f"{key} = ?")
                params.append(value)
            
            if not set_clause:
                return False
                
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(set_clause)} WHERE id = ?"
            cursor.execute(query, tuple(params))
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
        
        Args:
            user_id (int): 欲刪除的使用者 ID。
            
        Returns:
            bool: 刪除成功回傳 True，否則回傳 False。
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            # 由于在 SQLite schema 中设定了 ON DELETE CASCADE，如果启用了 pragma foreign_keys，
            # 这里删除 user 时也会连带删除相关的 carbon_records。
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting user: {e}")
            return False
        finally:
            conn.close()


class CarbonRecordModel:
    """
    負責 carbon_records 資料表的 CRUD 操作。
    """
    
    @staticmethod
    def create(data):
        """
        新增一筆碳排放記錄。
        
        Args:
            data (dict): 包含 user_id, category, action_name, parameter_value, carbon_amount, suggestion 等欄位的字典。
            
        Returns:
            int: 新增成功的回傳記錄 ID，失敗則回傳 None。
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO carbon_records 
                   (user_id, category, action_name, parameter_value, carbon_amount, suggestion) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (data.get('user_id'), data.get('category'), data.get('action_name'), 
                 data.get('parameter_value'), data.get('carbon_amount'), data.get('suggestion'))
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
        取得所有碳排放記錄。
        
        Returns:
            list: 包含所有碳排放記錄的 sqlite3.Row 物件列表。
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM carbon_records")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting carbon records: {e}")
            return []
        finally:
            conn.close()
            
    @staticmethod
    def get_by_user_id(user_id):
        """
        取得特定使用者的所有碳排放記錄。
        
        Args:
            user_id (int): 使用者的 ID。
            
        Returns:
            list: 包含該使用者的所有碳排放記錄的 sqlite3.Row 物件列表。
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM carbon_records WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting carbon records by user id: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_by_id(record_id):
        """
        根據 ID 取得單筆碳排放記錄。
        
        Args:
            record_id (int): 記錄的 ID。
            
        Returns:
            sqlite3.Row: 若找到則回傳該筆記錄，否則回傳 None。
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM carbon_records WHERE id = ?", (record_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error getting carbon record by id: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def update(record_id, data):
        """
        更新碳排放記錄。
        
        Args:
            record_id (int): 欲更新的記錄 ID。
            data (dict): 包含要更新的欄位與對應值的字典。
            
        Returns:
            bool: 更新成功回傳 True，否則回傳 False。
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            set_clause = []
            params = []
            for key, value in data.items():
                set_clause.append(f"{key} = ?")
                params.append(value)
            
            if not set_clause:
                return False
                
            params.append(record_id)
            query = f"UPDATE carbon_records SET {', '.join(set_clause)} WHERE id = ?"
            cursor.execute(query, tuple(params))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating carbon record: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(record_id):
        """
        刪除碳排放記錄。
        
        Args:
            record_id (int): 欲刪除的記錄 ID。
            
        Returns:
            bool: 刪除成功回傳 True，否則回傳 False。
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM carbon_records WHERE id = ?", (record_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting carbon record: {e}")
            return False
        finally:
            conn.close()
