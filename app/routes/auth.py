from flask import Blueprint, request, redirect, url_for, render_template, session, flash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET'])
def register_page():
    """顯示註冊表單"""
    pass

@auth_bp.route('/register', methods=['POST'])
def handle_register():
    """接收註冊表單，寫入資料庫，重導向至登入頁"""
    pass

@auth_bp.route('/login', methods=['GET'])
def login_page():
    """顯示登入表單"""
    pass

@auth_bp.route('/login', methods=['POST'])
def handle_login():
    """驗證帳密，設定 Session，重導向至首頁"""
    pass

@auth_bp.route('/logout', methods=['GET'])
def logout():
    """清除 Session，重導向至登入頁"""
    pass
