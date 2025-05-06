from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user
from app.models import Usuario
from app import login_manager
from flask_wtf.csrf import CSRFProtect

bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('senha', '').strip()
        
        if not username or not password:
            flash('Preencha todos os campos', 'danger')
            return redirect(url_for('auth.login'))
        
        user = Usuario.query.filter_by(nome=username).first()
        
        if user and user.senha == password:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        
        flash('Usuário ou senha incorretos', 'danger')
    
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    logout_user()
    flash('Você foi deslogado com sucesso', 'info')
    return redirect(url_for('auth.login'))