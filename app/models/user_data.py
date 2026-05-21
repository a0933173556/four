import sqlite3
import os

# 確保對應的絕對路徑正確：four/instance/database.db
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
    'instance', 
    'database.db'
)

def get_db_connection():
    """
    建立並回傳 SQLite 資料庫連線。
    預期資料庫路徑位於 instance/database.db
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"資料庫連線錯誤: {e}")
        return None

class UserModel:
    """使用者資料表操作方法"""
    
    @staticmethod
    def create(data):
        """
        新增一筆使用者記錄
        :param data: dict 包含 username, password_hash, target_carbon_emission (可選)
        :return: int 新增記錄的 ID，失敗則回傳 None
        """
        conn = get_db_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            target = data.get('target_carbon_emission', 0)
            cursor.execute(
                "INSERT INTO users (username, password_hash, target_carbon_emission) VALUES (?, ?, ?)",
                (data['username'], data['password_hash'], target)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"UserModel.create 錯誤: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_all():
        """
        取得所有使用者記錄
        :return: list 包含使用者的 sqlite3.Row，失敗則回傳空 list
        """
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"UserModel.get_all 錯誤: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_by_id(user_id):
        """
        取得單一使用者記錄
        :param user_id: int 使用者 ID
        :return: sqlite3.Row 單筆使用者，找不到或失敗則回傳 None
        """
        conn = get_db_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"UserModel.get_by_id 錯誤: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def update(user_id, data):
        """
        更新一筆使用者記錄
        :param user_id: int 使用者 ID
        :param data: dict 包含欲更新的欄位名稱與值
        :return: bool 是否更新成功
        """
        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
            values = list(data.values())
            values.append(user_id)
            cursor.execute(f"UPDATE users SET {set_clause} WHERE id = ?", tuple(values))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"UserModel.update 錯誤: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(user_id):
        """
        刪除一筆使用者記錄
        :param user_id: int 使用者 ID
        :return: bool 是否刪除成功
        """
        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"UserModel.delete 錯誤: {e}")
            return False
        finally:
            conn.close()


class CarbonRecordModel:
    """碳排紀錄表操作方法"""
    
    @staticmethod
    def create(data):
        """
        新增一筆碳排放記錄
        :param data: dict 包含 user_id, category, action_name, parameter_value, carbon_amount, suggestion (可選)
        :return: int 新增記錄的 ID，失敗則回傳 None
        """
        conn = get_db_connection()
        if not conn: return None
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
            print(f"CarbonRecordModel.create 錯誤: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_all(user_id=None):
        """
        取得所有碳排記錄（若提供 user_id 則篩選特定使用者的記錄）
        :param user_id: int 使用者 ID（選填）
        :return: list 包含記錄的 sqlite3.Row，失敗則回傳空 list
        """
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            if user_id is not None:
                cursor.execute("SELECT * FROM carbon_records WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
            else:
                cursor.execute("SELECT * FROM carbon_records ORDER BY created_at DESC")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"CarbonRecordModel.get_all 錯誤: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_by_id(record_id):
        """
        取得單一碳排記錄
        :param record_id: int 紀錄 ID
        :return: sqlite3.Row 單筆紀錄，找不到或失敗則回傳 None
        """
        conn = get_db_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM carbon_records WHERE id = ?", (record_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"CarbonRecordModel.get_by_id 錯誤: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def update(record_id, data):
        """
        更新一筆碳排記錄
        :param record_id: int 紀錄 ID
        :param data: dict 包含欲更新的欄位名稱與值
        :return: bool 是否更新成功
        """
        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            if not data: return True # 沒有提供更新欄位
            set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
            values = list(data.values())
            values.append(record_id)
            cursor.execute(f"UPDATE carbon_records SET {set_clause} WHERE id = ?", tuple(values))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"CarbonRecordModel.update 錯誤: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(record_id):
        """
        刪除一筆碳排記錄
        :param record_id: int 紀錄 ID
        :return: bool 是否刪除成功
        """
        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM carbon_records WHERE id = ?", (record_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"CarbonRecordModel.delete 錯誤: {e}")
            return False
        finally:
            conn.close()
