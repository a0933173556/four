import sqlite3
import os

def init_db():
    db_dir = os.path.join(os.path.dirname(__file__), 'instance')
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, 'database.db')
    schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
    
    with sqlite3.connect(db_path) as conn:
        with open(schema_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()
