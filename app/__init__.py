import os
import sqlite3

def init_db():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'database.db')
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'schema.sql')
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = f.read()
        
    conn = sqlite3.connect(db_path)
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print("Database initialized successfully.")
