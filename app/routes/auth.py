import functools
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user_data import User
from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__)

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.get_by_id(user_id)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        error = None

        if not username:
            error = '請輸入帳號。'
        elif not password:
            error = '請輸入密碼。'
        elif password != confirm_password:
            error = '密碼與確認密碼不相符。'
        elif User.get_by_username(username) is not None:
            error = f"帳號 {username} 已經註冊過。"
@auth_bp.route('/register', methods=['GET'])
def register_page():
    """顯示註冊表單"""
    return render_template('auth/register.html')

@auth_bp.route('/register', methods=['POST'])
def handle_register():
    """接收註冊表單，寫入資料庫，重導向至登入頁"""
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    if not username or not password:
        flash('請填寫所有欄位', 'warning')
        return redirect(url_for('auth.register_page'))
        
    if password != confirm_password:
        flash('兩次密碼輸入不相符', 'warning')
        return redirect(url_for('auth.register_page'))
        
    if User.get_by_username(username):
        flash('此帳號已被註冊', 'danger')
        return redirect(url_for('auth.register_page'))
        
    password_hash = generate_password_hash(password)
    user_id = User.create({'username': username, 'password_hash': password_hash})
    
    if user_id:
        flash('註冊成功，請登入', 'success')
        return redirect(url_for('auth.login_page'))
    else:
        flash('註冊失敗，請稍後再試', 'danger')
        return redirect(url_for('auth.register_page'))

@auth_bp.route('/login', methods=['GET'])
def login_page():
    """顯示登入表單"""
    if 'user_id' in session:
        return redirect(url_for('ledger.index'))
    return render_template('auth/login.html')

@auth_bp.route('/login', methods=['POST'])
def handle_login():
    """驗證帳密，設定 Session，重導向至首頁"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = User.get_by_username(username)
    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        flash(f'歡迎回來，{username}！', 'success')
        return redirect(url_for('ledger.index'))
    else:
        flash('帳號或密碼錯誤', 'danger')
        return redirect(url_for('auth.login_page'))

        if error is None:
            User.create({
                'username': username,
                'password_hash': generate_password_hash(password)
            })
            flash('註冊成功！請登入。', 'success')
            return redirect(url_for('auth.login'))

        flash(error, 'danger')

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if g.user:
        return redirect(url_for('ledger.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        error = None
        user = User.get_by_username(username)

        if user is None:
            error = '帳號錯誤。'
        elif not check_password_hash(user['password_hash'], password):
            error = '密碼錯誤。'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('ledger.index'))

        flash(error, 'danger')

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
    """清除 Session，重導向至登入頁"""
    session.clear()
    flash('您已成功登出', 'info')
    return redirect(url_for('auth.login_page'))
