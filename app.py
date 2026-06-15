import os
from flask import Flask

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key')

from app.routes.auth import auth_bp
from app.routes.ledger import ledger_bp
from app.routes.report import report_bp

app.register_blueprint(auth_bp)
app.register_blueprint(ledger_bp)
app.register_blueprint(report_bp)

if __name__ == '__main__':
    app.run(debug=True)
