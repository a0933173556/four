import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'database.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

class CarbonRecord:
    @staticmethod
    def create(user_id, category, action_name, parameter_value, carbon_amount, suggestion=""):
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO carbon_records (user_id, category, action_name, parameter_value, carbon_amount, suggestion)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, category, action_name, parameter_value, carbon_amount, suggestion)
        )
        conn.commit()
        record_id = cur.lastrowid
        conn.close()
        return record_id

    @staticmethod
    def get_by_id(record_id):
        conn = get_db()
        record = conn.execute("SELECT * FROM carbon_records WHERE id = ?", (record_id,)).fetchone()
        conn.close()
        return dict(record) if record else None

    @staticmethod
    def get_all_by_user(user_id):
        conn = get_db()
        records = conn.execute("SELECT * FROM carbon_records WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
        conn.close()
        return [dict(r) for r in records]

    @staticmethod
    def delete(record_id):
        conn = get_db()
        conn.execute("DELETE FROM carbon_records WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
