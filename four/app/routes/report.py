from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.user_data import UserModel

report_bp = Blueprint('report', __name__)

@report_bp.route('/target', methods=['GET', 'POST'])
def target():
    # 檢查是否已登入
    if 'user_id' not in session:
        flash('請先登入', 'warning')
        # 假設 auth blueprint 裡的 login 路由名稱為 auth.login
        return redirect(url_for('auth.login'))
        
    user_id = session['user_id']
    
    if request.method == 'POST':
        # 取得表單輸入
        target_value = request.form.get('target_carbon_emission')
        
        # 基本輸入驗證
        if not target_value:
            flash('請輸入減碳目標數值', 'danger')
            return redirect(url_for('report.target'))
            
        try:
            target_value = float(target_value)
            if target_value < 0:
                flash('減碳目標不能為負數', 'danger')
                return redirect(url_for('report.target'))
        except ValueError:
            flash('請輸入有效的數字', 'danger')
            return redirect(url_for('report.target'))
            
        # 更新資料庫
        success = UserModel.update(user_id, {'target_carbon_emission': target_value})
        
        if success:
            flash('減碳目標更新成功！', 'success')
            # 根據 ROUTES.md，更新成功後重導向至首頁
            return redirect(url_for('index'))
        else:
            flash('更新失敗，請稍後再試', 'danger')
            return redirect(url_for('report.target'))
            
    # GET 請求，取得目前目標並渲染模板
    user = UserModel.get_by_id(user_id)
    if not user:
        flash('找不到使用者資料，請重新登入', 'danger')
        session.pop('user_id', None)
        return redirect(url_for('auth.login'))
        
    return render_template('report/target.html', current_target=user['target_carbon_emission'])
