import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from app.models.user_data import CarbonRecordModel, UserModel

bp = Blueprint('ledger', __name__)

# 模擬登入驗證裝飾器 (後續會在 auth.py 正式實作時替換)
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('user_id') is None:
            # 開發測試階段，如果沒有 user_id，暫時給預設值 1 (假設有 id=1 的使用者)
            # 在整合階段會改為： return redirect(url_for('auth.login'))
            session['user_id'] = 1 
            
            # 若資料庫沒有 id=1 的使用者，先自動建立一個供測試
            if not UserModel.get_by_id(1):
                UserModel.create({
                    'username': 'testuser',
                    'password_hash': 'fakehash',
                    'target_carbon_emission': 100.0
                })
                
        return view(**kwargs)
    return wrapped_view

# 碳排係數字典 (單位: kg CO2e)
CARBON_FACTORS = {
    'transport': {
        'car': {'factor': 0.25, 'name': '開車', 'unit': '公里', 'suggestion': '建議改搭捷運或公車，可減少約 80% 碳排。'},
        'motorcycle': {'factor': 0.1, 'name': '騎機車', 'unit': '公里', 'suggestion': '短程可考慮騎乘自行車或步行。'},
        'mrt': {'factor': 0.04, 'name': '搭捷運', 'unit': '公里', 'suggestion': '很棒的低碳選擇！'},
        'bus': {'factor': 0.05, 'name': '搭公車', 'unit': '公里', 'suggestion': '很棒的低碳選擇！'}
    },
    'food': {
        'beef': {'factor': 27.0, 'name': '吃牛肉', 'unit': '公斤', 'suggestion': '牛肉碳排較高，建議可嘗試替換為雞肉或植物肉。'},
        'pork': {'factor': 12.1, 'name': '吃豬肉', 'unit': '公斤', 'suggestion': '可考慮多吃蔬菜，減少肉類攝取。'},
        'chicken': {'factor': 6.9, 'name': '吃雞肉', 'unit': '公斤', 'suggestion': '雞肉是相對較低碳的肉類選擇。'},
        'vegetable': {'factor': 2.0, 'name': '吃蔬菜', 'unit': '公斤', 'suggestion': '多吃蔬菜對身體和地球都好！'}
    },
    'electricity': {
        'ac': {'factor': 0.509, 'name': '吹冷氣', 'unit': '度', 'suggestion': '冷氣溫度可設定在 26-28 度，並搭配電風扇。'},
        'lighting': {'factor': 0.509, 'name': '開燈', 'unit': '度', 'suggestion': '隨手關燈，考慮更換 LED 節能燈泡。'}
    }
}

@bp.route('/')
@login_required
def index():
    user_id = session.get('user_id')
    records = CarbonRecordModel.get_by_user_id(user_id)
    user = UserModel.get_by_id(user_id)
    
    # 計算本月總碳排 (目前簡化為計算所有歷史總和)
    total_carbon = sum(record['carbon_amount'] for record in records)
    target = user['target_carbon_emission'] if user else 0.0
    
    return render_template('index.html', records=records, total_carbon=total_carbon, target=target)

@bp.route('/records/new', methods=('GET',))
@login_required
def new_record():
    return render_template('ledger/record.html', factors=CARBON_FACTORS)

@bp.route('/records', methods=('POST',))
@login_required
def create_record():
    user_id = session.get('user_id')
    category = request.form.get('category')
    action_name = request.form.get('action_name')
    parameter_value = request.form.get('parameter_value')
    
    error = None
    if not category or not action_name or not parameter_value:
        error = '所有欄位皆為必填。'
    
    try:
        parameter_value = float(parameter_value)
    except ValueError:
        error = '參數值必須為數字。'
        
    if error is None:
        factor_info = CARBON_FACTORS.get(category, {}).get(action_name)
        if factor_info:
            # 根據公式：碳排量 = 參數值 * 碳排係數
            carbon_amount = parameter_value * factor_info['factor']
            suggestion = factor_info['suggestion']
            
            CarbonRecordModel.create({
                'user_id': user_id,
                'category': category,
                'action_name': factor_info['name'],
                'parameter_value': parameter_value,
                'carbon_amount': carbon_amount,
                'suggestion': suggestion
            })
            flash('紀錄新增成功！')
            return redirect(url_for('ledger.index'))
        else:
            error = '無效的分類或行為。'
            
    flash(error)
    return redirect(url_for('ledger.new_record'))

@bp.route('/records/<int:id>/delete', methods=('POST',))
@login_required
def delete_record(id):
    record = CarbonRecordModel.get_by_id(id)
    if record and record['user_id'] == session.get('user_id'):
        CarbonRecordModel.delete(id)
        flash('紀錄已刪除。')
    else:
        flash('找不到該紀錄或無權限刪除。')
    return redirect(url_for('ledger.index'))
