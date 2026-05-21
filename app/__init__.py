# Initialize app package
from flask import Flask
from app.routes.auth import auth_bp
from app.routes.ledger import ledger_bp
from app.routes.report import report_bp
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key_for_flash_messages')
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(ledger_bp)
    app.register_blueprint(report_bp)
    
    return app

def init_db():
    from app.models.user_data import get_db_connection
    conn = get_db_connection()
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.close()
    print("Database initialized successfully.")
