from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
from flask_login import login_required, current_user, logout_user
from app.models import Apostila, Curso  # Adicione esta importação

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    return redirect(url_for('main.admin'))

@bp.route('/admin')
@login_required
def admin():
    print("Acessando admin como:", current_user.nome)
    session['user'] = current_user.nome
    return render_template('admin/admin.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user', None)
    return redirect(url_for('auth.login'))

# Rotas de mensagens e busca
@bp.route('/mensagem')
@login_required
def mensagem():
    # Obter apostilas com estoque crítico (≤ 10 unidades)
    apostilas_criticas = Apostila.query\
        .join(Curso, isouter=True)\
        .filter(Apostila.quantidade <= 10)\
        .order_by(Apostila.quantidade.asc())\
        .all()

    return render_template('mensagem.html',
                         apostilas_criticas=apostilas_criticas)

@bp.route('/busca_detalhada/<string:id>')
@login_required
def busca_detalhada(id):
    """Mostra detalhes de uma apostila específica"""
    apostila = Apostila.query.get_or_404(id)
    return render_template('busca_detalhada.html', apostila=apostila)

@bp.route('/busca')
@login_required
def busca():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('apostilas.cadastrada'))

    results = Apostila.query.join(Curso).filter(
        (Apostila.nome.ilike(f'%{query}%')) |
        (Apostila.id.ilike(f'%{query}%')) |
        (Curso.nome.ilike(f'%{query}%')) |
        (Apostila.autor.ilike(f'%{query}%'))
    ).all()

    return render_template('busca.html', apostilas=results, query=query)