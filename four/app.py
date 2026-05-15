import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_dev_key')
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')

# 註冊 Blueprints
from app.routes.report import report_bp
app.register_blueprint(report_bp)

# 建立一個暫時的 auth dummy 路由與首頁路由，避免 url_for 找不到 target endpoint 報錯
from flask import Blueprint
auth_bp = Blueprint('auth', __name__)
@auth_bp.route('/login')
def login(): return "Login Page"
app.register_blueprint(auth_bp)

@app.route('/')
def index():
    return "Home Page"

if __name__ == '__main__':
    app.run(debug=True)
