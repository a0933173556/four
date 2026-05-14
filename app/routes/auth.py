import functools
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user_data import User

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
