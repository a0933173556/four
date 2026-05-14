import os
from flask import Flask

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key')

from app.routes.ledger import ledger_bp
app.register_blueprint(ledger_bp)

if __name__ == '__main__':
    app.run(debug=True)
