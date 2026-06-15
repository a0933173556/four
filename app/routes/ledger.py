from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.routes.auth import login_required
from app.models.user_data import CarbonRecordModel, UserModel

ledger_bp = bp = Blueprint('ledger', __name__)

# 碳排係數與建議對照表
CARBON_COEFFICIENTS = {
    '食': {
        '牛肉': {'factor': 40.0, 'suggestion': '牛肉碳排極高（每公斤產生 40 kg CO₂e），建議一週可安排一天嘗試蔬食！'},
        '豬肉': {'factor': 12.0, 'suggestion': '豬肉碳排偏高（每公斤產生 12 kg CO₂e），可考慮改吃白肉或蔬食。'},
        '雞肉': {'factor': 6.0,  'suggestion': '雞肉相對紅肉碳排較低（每公斤產生 6 kg CO₂e），是不錯的蛋白質來源。'},
        '魚肉': {'factor': 4.0,  'suggestion': '魚肉碳排較低（每公斤產生 4 kg CO₂e），是友善環境的葷食選擇！'},
        '蔬食': {'factor': 2.0,  'suggestion': '蔬食碳排最低（每公斤產生 2 kg CO₂e），感謝您為地球盡一份心力！'},
    },
    '行': {
        '開車': {'factor': 0.25, 'suggestion': '開車碳排較高，建議下次可嘗試搭乘大眾運輸或共乘！'},
        '機車': {'factor': 0.1, 'suggestion': '騎機車雖然方便，短程可以考慮步行或騎腳踏車喔！'},
        '大眾運輸': {'factor': 0.04, 'suggestion': '搭乘大眾運輸是很棒的低碳選擇，請繼續保持！'},
        '步行/腳踏車': {'factor': 0.0, 'suggestion': '零碳排放！對健康與環境都非常好的完美選擇！'}
    },
    '住': {
        '冷氣': {'factor': 0.8, 'suggestion': '冷氣設定 26-28 度並搭配電風扇可有效節能。'},
        '電燈': {'factor': 0.1, 'suggestion': '隨手關燈，小動作大改變！'},
        '熱水器': {'factor': 0.5, 'suggestion': '洗澡時間縮短 5 分鐘，每次可省不少能源！'}
    }
}


@bp.route('/')
@login_required
def index():
    """顯示首頁儀表板，包含累積碳排、目標進度與近期紀錄列表"""
    user_id = session.get('user_id')

    records = CarbonRecordModel.get_all(user_id=user_id)
    user = UserModel.get_by_id(user_id)

    total_carbon = sum([r['carbon_amount'] for r in records]) if records else 0
    target = user['target_carbon_emission'] if user else 0

    return render_template('index.html', records=records, total_carbon=total_carbon, target=target)


@bp.route('/records/new', methods=['GET'])
@login_required
def new_record():
    """顯示行為分類登錄表單"""
    return render_template('ledger/record.html', categories=CARBON_COEFFICIENTS)


@bp.route('/records', methods=['POST'])
@login_required
def create_record():
    """接收行為表單，計算碳排與建議，存入資料庫，重導向至首頁"""
    user_id = session.get('user_id')

    category = request.form.get('category')
    action_name = request.form.get('action_name')
    parameter_value = request.form.get('parameter_value')

    if not category or not action_name or not parameter_value:
        flash('請填寫所有必填欄位', 'danger')
        return redirect(url_for('ledger.new_record'))

    try:
        parameter_value = float(parameter_value)
    except ValueError:
        flash('參數值必須為數字', 'danger')
        return redirect(url_for('ledger.new_record'))

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
        flash(f'行為紀錄已成功新增！本次產生了 {carbon_amount:.2f} kg 碳排。', 'success')
    else:
        flash('新增失敗，請稍後再試。', 'danger')

    return redirect(url_for('ledger.index'))


@bp.route('/records/<int:record_id>/delete', methods=['POST'])
@login_required
def delete_record(record_id):
    """刪除單筆紀錄，重導向至首頁"""
    user_id = session.get('user_id')

    record = CarbonRecordModel.get_by_id(record_id)
    if not record or record['user_id'] != user_id:
        flash('找不到該紀錄或無權限刪除', 'danger')
        return redirect(url_for('ledger.index'))

    if CarbonRecordModel.delete(record_id):
        flash('紀錄已刪除', 'success')
    else:
        flash('刪除失敗', 'danger')

    return redirect(url_for('ledger.index'))
