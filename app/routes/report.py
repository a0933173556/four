from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.routes.auth import login_required
from app.models.user_data import CarbonRecordModel, UserModel

report_bp = bp = Blueprint('report', __name__)


@bp.route('/report', methods=['GET'])
@login_required
def report_page():
    """顯示視覺化圖表統計數據"""
    user_id = session.get('user_id')
    records = CarbonRecordModel.get_all(user_id=user_id)

    # 各分類的碳排總計 (圓餅圖)
    category_data = {}

    # 歷史排放趨勢 (折線圖) - 依日期分組
    trend_data_dict = {}

    for r in records:
        # 分類統計
        cat = r['category']
        category_data[cat] = category_data.get(cat, 0) + r['carbon_amount']

        # 趨勢統計 (以天為單位)
        date_str = str(r['created_at']).split(' ')[0] if r['created_at'] else '未知'
        trend_data_dict[date_str] = trend_data_dict.get(date_str, 0) + r['carbon_amount']

    # 將趨勢數據依日期排序
    sorted_dates = sorted(trend_data_dict.keys())
    trend_labels = sorted_dates
    trend_values = [round(trend_data_dict[d], 2) for d in sorted_dates]

    return render_template(
        'report/index.html',
        category_data=category_data,
        trend_labels=trend_labels,
        trend_values=trend_values
    )


@bp.route('/target', methods=['GET'])
@login_required
def target_page():
    """顯示每月減碳目標設定表單"""
    user_id = session.get('user_id')
    user = UserModel.get_by_id(user_id)
    if not user:
        flash('找不到使用者資料', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('report/target.html', target=user['target_carbon_emission'])


@bp.route('/target', methods=['POST'])
@login_required
def update_target():
    """接收表單，更新目標，重導向至首頁"""
    user_id = session.get('user_id')
    target_value = request.form.get('target_carbon_emission')

    if not target_value:
        flash('請輸入減碳目標', 'warning')
        return redirect(url_for('report.target_page'))

    try:
        target_value = float(target_value)
    except ValueError:
        flash('請輸入有效的數字', 'warning')
        return redirect(url_for('report.target_page'))

    success = UserModel.update(user_id, {'target_carbon_emission': target_value})
    if success:
        flash('減碳目標更新成功！', 'success')
        return redirect(url_for('ledger.index'))
    else:
        flash('更新目標時發生錯誤', 'danger')
        return redirect(url_for('report.target_page'))
