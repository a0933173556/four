from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

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

@auth_bp.route('/logout', methods=['GET'])
def logout():
    """清除 Session，重導向至登入頁"""
    session.clear()
    flash('您已成功登出', 'info')
    return redirect(url_for('auth.login_page'))
