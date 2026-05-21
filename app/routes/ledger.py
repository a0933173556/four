from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from app.models import CarbonRecord, User
from app.routes.report import login_required

bp = Blueprint('ledger', __name__)

# 簡易碳排係數表 (kg CO2e)
CARBON_FACTORS = {
    '搭乘捷運': 0.04,
    '獨自開車': 0.25,
    '外帶餐盒': 0.5,
    '冷氣一小時': 0.8
}

SUGGESTIONS = {
    '獨自開車': '建議改搭大眾運輸工具，可減少約 80% 碳排',
    '外帶餐盒': '建議自備環保餐盒，減少一次性塑膠垃圾',
    '冷氣一小時': '建議冷氣設定 26-28 度並搭配電風扇'
}

@ledger_bp.route('/', methods=['GET'])
@login_required
def index():
    """顯示首頁儀表板，包含累積碳排、目標進度與近期紀錄列表"""
    user_id = session['user_id']
    user = User.get_by_id(user_id)
    records = CarbonRecord.get_all(user_id=user_id)
    
    total_carbon = sum(r['carbon_amount'] for r in records)
    target = user['target_carbon_emission']
    
    return render_template('index.html', records=records, total_carbon=total_carbon, target=target)

@ledger_bp.route('/records/new', methods=['GET'])
@login_required
def new_record_page():
    """顯示行為分類登錄表單"""
    return render_template('ledger/record.html')

@ledger_bp.route('/records', methods=['POST'])
@login_required
def create_record():
    """接收行為表單，計算碳排與建議，存入資料庫，重導向至首頁"""
    user_id = session['user_id']
    category = request.form.get('category')
    action_name = request.form.get('action_name')
    parameter_value = request.form.get('parameter_value')
    
    if not category or not action_name or not parameter_value:
        flash('請填寫所有必填欄位', 'warning')
        return redirect(url_for('ledger.new_record_page'))
        
    try:
        parameter_value = float(parameter_value)
    except ValueError:
        flash('數值格式不正確', 'danger')
        return redirect(url_for('ledger.new_record_page'))
        
    factor = CARBON_FACTORS.get(action_name, 0.1)
    carbon_amount = factor * parameter_value
    suggestion = SUGGESTIONS.get(action_name, '表現不錯，請繼續保持低碳生活！')
    
    data = {
        'user_id': user_id,
        'category': category,
        'action_name': action_name,
        'parameter_value': parameter_value,
        'carbon_amount': carbon_amount,
        'suggestion': suggestion
    }
    
    if CarbonRecord.create(data):
        flash(f'成功新增一筆紀錄！本次產生約 {carbon_amount:.2f} kg 碳排放。', 'success')
    else:
        flash('新增紀錄失敗', 'danger')
        
    return redirect(url_for('ledger.index'))

@ledger_bp.route('/records/<int:record_id>/delete', methods=['POST'])
@login_required
def delete_record(record_id):
    """刪除單筆紀錄，重導向至首頁"""
    # 確認紀錄屬於該使用者
    record = CarbonRecord.get_by_id(record_id)
    if record and record['user_id'] == session['user_id']:
        CarbonRecord.delete(record_id)
        flash('紀錄已刪除', 'info')
    else:
        flash('無權限或找不到紀錄', 'danger')
        
    return redirect(url_for('ledger.index'))
