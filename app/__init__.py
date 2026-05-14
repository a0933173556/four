# Initialize app package
from flask import Flask
from app.routes.auth import auth_bp
from app.routes.ledger import ledger_bp
from app.routes.report import report_bp

def create_app():
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(ledger_bp)
    app.register_blueprint(report_bp)
    
    return app
