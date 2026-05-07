from flask import Blueprint, request, redirect, url_for, render_template, session, flash

report_bp = Blueprint('report', __name__)

@report_bp.route('/report', methods=['GET'])
def report_page():
    """顯示視覺化圖表統計數據"""
    pass

@report_bp.route('/target', methods=['GET'])
def target_page():
    """顯示每月減碳目標設定表單"""
    pass

@report_bp.route('/target', methods=['POST'])
def update_target():
    """接收表單，更新目標，重導向至首頁"""
    pass
