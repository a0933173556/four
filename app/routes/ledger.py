from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.routes.auth import login_required
from app.models.user_data import CarbonRecord

bp = Blueprint('ledger', __name__)

# 碳排係數字典 (假設值，單位 kg CO2e / 參數單位)
CARBON_COEFFICIENTS = {
    'car': 0.25,        # 汽車 (每公里)
    'motorcycle': 0.1,  # 機車 (每公里)
    'bus': 0.04,        # 公車 (每公里)
    'mrt': 0.04,        # 捷運 (每公里)
    'beef': 5.0,        # 牛肉餐 (每餐)
    'chicken': 1.5,     # 雞肉餐 (每餐)
    'veg': 0.5,         # 蔬食餐 (每餐)
    'electricity': 0.5  # 用電 (每度)
}

# 智慧替代建議字典
SUGGESTIONS = {
    'car': '建議下次可以改搭大眾運輸工具，或與朋友共乘來降低碳排！',
    'motorcycle': '短程可以考慮騎自行車或步行，有益健康又環保！',
    'beef': '嘗試每週一日蔬食，能有效大幅降低飲食碳足跡喔！',
    'electricity': '隨手關燈、拔掉不必要的插頭，也是減碳好習慣。'
}

@bp.route('/')
@login_required
def index():
    records = CarbonRecord.get_by_user_id(g.user['id'])
    
    # 計算總碳排
    total_carbon = sum(r['carbon_amount'] for r in records)
    
    return render_template('index.html', records=records, total_carbon=total_carbon)

@bp.route('/records/new')
@login_required
def new_record():
    return render_template('ledger/record.html')

@bp.route('/records', methods=('POST',))
@login_required
def create_record():
    category = request.form.get('category')
    action_name = request.form.get('action_name')
    parameter_value = request.form.get('parameter_value', type=float)
    
    if not category or not action_name or parameter_value is None:
        flash('請填寫所有必填欄位並確保數值格式正確。', 'danger')
        return redirect(url_for('ledger.new_record'))

    # 計算碳排
    coefficient = CARBON_COEFFICIENTS.get(action_name, 0)
    carbon_amount = coefficient * parameter_value
    
    # 產生建議
    suggestion = SUGGESTIONS.get(action_name, '')
    
    CarbonRecord.create({
        'user_id': g.user['id'],
        'category': category,
        'action_name': action_name,
        'parameter_value': parameter_value,
        'carbon_amount': carbon_amount,
        'suggestion': suggestion
    })
    
    flash(f'成功記錄！本次產生了 {carbon_amount:.2f} kg 碳排。 {suggestion}', 'success')
    return redirect(url_for('ledger.index'))

@bp.route('/records/<int:id>/delete', methods=('POST',))
@login_required
def delete_record(id):
    record = CarbonRecord.get_by_id(id)
    if record and record['user_id'] == g.user['id']:
        CarbonRecord.delete(id)
        flash('紀錄已刪除。', 'success')
    else:
        flash('無法刪除此紀錄。', 'danger')
        
    return redirect(url_for('ledger.index'))
