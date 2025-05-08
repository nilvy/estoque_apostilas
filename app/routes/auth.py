from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, current_user
from werkzeug.security import check_password_hash
from app.models import Usuario

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # Redireciona se já estiver logado

    if request.method == 'POST':
        username = request.form.get('username', '').strip()  # Nome do campo no formulário
        password = request.form.get('password', '').strip()  # Nome do campo no formulário

        if not username or not password:
            flash('Por favor, preencha todos os campos.', 'danger')
            return redirect(url_for('auth.login'))

        # Validação de credenciais
        user = Usuario.query.filter_by(nome=username).first()
        if user and check_password_hash(user.senha, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))

        flash('Usuário ou senha incorretos.', 'danger')

    return render_template('auth/login.html')