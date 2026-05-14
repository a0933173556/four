from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.routes.auth import login_required
from app.models.user_data import CarbonRecord, User

bp = Blueprint('report', __name__)

@bp.route('/report')
@login_required
def index():
    # 視覺化報表邏輯：將資料彙整後傳遞給前端
    records = CarbonRecord.get_by_user_id(g.user['id'])
    
    # 簡單聚合：依據分類計算總碳排
    category_data = {}
    for r in records:
        cat = r['category']
        category_data[cat] = category_data.get(cat, 0) + r['carbon_amount']
        
    return render_template('report/index.html', category_data=category_data)

@bp.route('/target', methods=('GET', 'POST'))
@login_required
def target():
    if request.method == 'POST':
        target_emission = request.form.get('target_carbon_emission', type=float)
        if target_emission is None or target_emission < 0:
            flash('請輸入有效的目標數值。', 'danger')
        else:
            User.update(g.user['id'], {'target_carbon_emission': target_emission})
            flash('目標已更新！', 'success')
            return redirect(url_for('ledger.index'))
            
    return render_template('report/target.html')
