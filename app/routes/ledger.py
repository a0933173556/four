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
    '衣': {
        '購買新衣': {'factor': 10.0, 'suggestion': '每件新衣產生約 10 kg CO₂e，建議優先考慮二手衣或租借服飾！'},
        '購買二手衣': {'factor': 5.0, 'suggestion': '二手衣碳排（5 kg CO₂e）是新衣的一半，繼續支持循環時尚！'},
    },
    '行': {
        '開車':      {'factor': 0.2,  'suggestion': '開車每公里產生 0.2 kg CO₂e，建議改搭大眾運輸或共乘！'},
        '機車':      {'factor': 0.05, 'suggestion': '機車每公里產生 0.05 kg CO₂e，短程可考慮步行或騎腳踏車！'},
        '大眾運輸':  {'factor': 0.03, 'suggestion': '大眾運輸每公里僅 0.03 kg CO₂e，是很棒的低碳選擇，請繼續保持！'},
        '步行/腳踏車': {'factor': 0.01, 'suggestion': '步行或騎腳踏車碳排極低，對健康與環境都很好！'},
    },
    '住': {
        '家庭用電': {'factor': 0.5,  'suggestion': '家庭用電每度產生 0.5 kg CO₂e，節能從隨手關燈開始！'},
        '家庭用水': {'factor': 0.15, 'suggestion': '家庭用水每度產生 0.15 kg CO₂e，縮短洗澡時間可有效節省！'},
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
