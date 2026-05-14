from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from app.models import User, CarbonRecord
from functools import wraps

report_bp = Blueprint('report', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('請先登入', 'warning')
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated_function

@report_bp.route('/report', methods=['GET'])
@login_required
def report_page():
    """顯示視覺化圖表統計數據"""
    user_id = session['user_id']
    records = CarbonRecord.get_all(user_id=user_id)
    
    # 準備前端 Chart.js 需要的數據
    # 1. 各分類的碳排總計 (圓餅圖)
    category_data = {}
    
    # 2. 歷史排放趨勢 (折線圖) - 依日期分組
    trend_data_dict = {}
    
    for r in records:
        # 分類統計
        cat = r['category']
        category_data[cat] = category_data.get(cat, 0) + r['carbon_amount']
        
        # 趨勢統計 (以天為單位)
        # created_at 格式為 'YYYY-MM-DD HH:MM:SS'
        date_str = r['created_at'].split(' ')[0]
        trend_data_dict[date_str] = trend_data_dict.get(date_str, 0) + r['carbon_amount']
    
    # 將趨勢數據依日期排序
    sorted_dates = sorted(trend_data_dict.keys())
    trend_labels = sorted_dates
    trend_values = [trend_data_dict[d] for d in sorted_dates]
    
    return render_template(
        'report/index.html', 
        category_data=category_data,
        trend_labels=trend_labels,
        trend_values=trend_values
    )

@report_bp.route('/target', methods=['GET'])
@login_required
def target_page():
    """顯示每月減碳目標設定表單"""
    user_id = session['user_id']
    user = User.get_by_id(user_id)
    if not user:
        flash('找不到使用者資料', 'danger')
        return redirect(url_for('auth.login_page'))
        
    return render_template('report/target.html', target=user['target_carbon_emission'])

@report_bp.route('/target', methods=['POST'])
@login_required
def update_target():
    """接收表單，更新目標，重導向至首頁"""
    user_id = session['user_id']
    target_value = request.form.get('target_carbon_emission')
    
    if not target_value:
        flash('請輸入減碳目標', 'warning')
        return redirect(url_for('report.target_page'))
        
    try:
        target_value = float(target_value)
    except ValueError:
        flash('請輸入有效的數字', 'warning')
        return redirect(url_for('report.target_page'))
        
    success = User.update(user_id, {'target_carbon_emission': target_value})
    if success:
        flash('減碳目標更新成功！', 'success')
        return redirect(url_for('ledger.index'))
    else:
        flash('更新目標時發生錯誤', 'danger')
        return redirect(url_for('report.target_page'))
