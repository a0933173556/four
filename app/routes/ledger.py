from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from app.models.user_data import CarbonRecordModel, UserModel

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

# 簡易碳排係數與建議對照表
CARBON_COEFFICIENTS = {
    '食': {
        '牛肉': {'factor': 27.0, 'suggestion': '牛肉碳排極高，建議一週可安排一天嘗試蔬食！'},
        '豬肉': {'factor': 12.1, 'suggestion': '豬肉碳排偏高，可考慮改吃白肉或蔬食。'},
        '雞肉': {'factor': 6.9, 'suggestion': '雞肉是不錯的蛋白質來源，碳排相對紅肉較低。'},
        '蔬食': {'factor': 2.0, 'suggestion': '蔬食是最環保的選擇，感謝您為地球盡一份心力！'}
    },
    '行': {
        '開車': {'factor': 0.25, 'suggestion': '開車碳排較高，建議下次可嘗試搭乘大眾運輸或共乘！'},
        '機車': {'factor': 0.1, 'suggestion': '騎機車雖然方便，短程可以考慮步行或騎腳踏車喔！'},
        '大眾運輸': {'factor': 0.04, 'suggestion': '搭乘大眾運輸是很棒的低碳選擇，請繼續保持！'},
        '步行/腳踏車': {'factor': 0.0, 'suggestion': '零碳排放！對健康與環境都非常好的完美選擇！'}
    }
}

@ledger_bp.route('/', methods=['GET'])
@login_required
def index():
    """顯示首頁儀表板，包含累積碳排、目標進度與近期紀錄列表"""
    user_id = session.get('user_id', 1) # 開發測試預設 user_id=1
    
    records = CarbonRecordModel.get_all(user_id=user_id)
    user = UserModel.get_by_id(user_id)
    
    total_carbon = sum([r['carbon_amount'] for r in records]) if records else 0
    target = user['target_carbon_emission'] if user else 0
    
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
    user_id = session.get('user_id', 1)

    category = request.form.get('category')
    action_name = request.form.get('action_name')
    parameter_value = request.form.get('parameter_value')

    if not category or not action_name or not parameter_value:
        flash('請填寫所有必填欄位', 'danger')
        return redirect(url_for('ledger.new_record_page'))

    try:
        parameter_value = float(parameter_value)
    except ValueError:
        flash('參數值必須為數字', 'danger')
        return redirect(url_for('ledger.new_record_page'))

    factor_data = CARBON_COEFFICIENTS.get(category, {}).get(action_name)
    if factor_data:
        carbon_amount = parameter_value * factor_data['factor']
        suggestion = factor_data['suggestion']
    else:
        carbon_amount = parameter_value * 1.0
        suggestion = '系統已記錄此項行為。'

    data = {
        'user_id': user_id,
        'category': category,
        'action_name': action_name,
        'parameter_value': parameter_value,
        'carbon_amount': round(carbon_amount, 2),
        'suggestion': suggestion
    }

    record_id = CarbonRecordModel.create(data)
    if record_id:
        flash('行為紀錄已成功新增！', 'success')
    else:
        flash('新增失敗，請稍後再試。', 'danger')

    return redirect(url_for('ledger.index'))

@ledger_bp.route('/records/<int:record_id>/delete', methods=['POST'])
@login_required
def delete_record(record_id):
    """刪除單筆紀錄，重導向至首頁"""
    user_id = session.get('user_id', 1)
        
    record = CarbonRecordModel.get_by_id(record_id)
    if not record or record['user_id'] != user_id:
        flash('找不到該紀錄或無權限刪除', 'danger')
        return redirect(url_for('ledger.index'))
        
    if CarbonRecordModel.delete(record_id):
        flash('紀錄已刪除', 'success')
    else:
        flash('刪除失敗', 'danger')
        
    return redirect(url_for('ledger.index'))
