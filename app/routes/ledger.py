from flask import Blueprint, request, redirect, url_for, render_template, session, flash

ledger_bp = Blueprint('ledger', __name__)

@ledger_bp.route('/', methods=['GET'])
def index():
    """顯示首頁儀表板，包含累積碳排、目標進度與近期紀錄列表"""
    pass

@ledger_bp.route('/records/new', methods=['GET'])
def new_record_page():
    """顯示行為分類登錄表單"""
    pass

@ledger_bp.route('/records', methods=['POST'])
def create_record():
    """接收行為表單，計算碳排與建議，存入資料庫，重導向至首頁"""
    pass

@ledger_bp.route('/records/<int:record_id>/delete', methods=['POST'])
def delete_record(record_id):
    """刪除單筆紀錄，重導向至首頁"""
    pass
