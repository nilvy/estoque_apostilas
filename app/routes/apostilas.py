from flask import Blueprint, jsonify, g, session, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import Apostila, Curso, Mensagem, ItemMovimentacao
from app.forms import ApostilaForm
from app import db
from datetime import datetime
import logging

bp = Blueprint('apostilas', __name__)

def verificar_estoque_baixo(apostila=None):
    try:
        if apostila:
            # Verifica se já existe mensagem não lida para esta apostila
            existing_msg = Mensagem.query.filter_by(
                tipo='estoque',
                apostila_id=apostila.id,
                lida=False
            ).first()

            if not existing_msg and apostila.quantidade < 5:
                msg = Mensagem(
                    tipo='estoque',
                    conteudo=f'Apostila {apostila.nome} está com estoque baixo: {apostila.quantidade} unidades',
                    usuario_id=current_user.id,
                    apostila_id=apostila.id
                )
                db.session.add(msg)
        else:
            # Verifica todas as apostilas
            apostilas = Apostila.query.filter(Apostila.quantidade < 5).all()
            for apostila in apostilas:
                existing_msg = Mensagem.query.filter_by(
                    tipo='estoque',
                    apostila_id=apostila.id,
                    lida=False
                ).first()

                if not existing_msg:
                    msg = Mensagem(
                        tipo='estoque',
                        conteudo=f'Apostila {apostila.nome} está com estoque baixo: {apostila.quantidade} unidades',
                        usuario_id=current_user.id,
                        apostila_id=apostila.id
                    )
                    db.session.add(msg)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao verificar estoque baixo: {str(e)}")

@bp.app_context_processor
def inject_estoque_baixo_count():
    """Adiciona o número de apostilas com estoque baixo ao contexto global"""
    if 'user' in session:  # Verifica se o usuário está logado
        try:
            estoque_baixo_count = Apostila.query.filter(Apostila.quantidade < 5).count()
            return {'estoque_baixo_count': estoque_baixo_count}
        except Exception as e:
            current_app.logger.error(f"Erro ao calcular estoque baixo: {str(e)}")
            return {'estoque_baixo_count': 0}
    return {'estoque_baixo_count': 0}

def apostila_to_dict(apostila):
    """Converte objeto Apostila para dicionário"""
    return {
        'id': apostila.id,
        'nome': apostila.nome,
        'curso_id': apostila.curso_id,
        'curso_nome': apostila.curso.nome if apostila.curso else '',
        'area': apostila.area,
        'paginas': apostila.paginas,
        'autor': apostila.autor,
        'quantidade': apostila.quantidade
    }

@bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    """Cadastra nova apostila"""
    form = ApostilaForm()
    form.curso_id.choices = [(c.id, c.nome) for c in Curso.query.order_by(Curso.nome).all()]

    if form.validate_on_submit():
        try:
            if Apostila.query.get(form.id.data):
                flash('Já existe uma apostila com este ID', 'danger')
                return redirect(url_for('apostilas.nova'))

            apostila = Apostila(
                id=form.id.data,
                nome=form.nome.data,
                curso_id=int(form.curso_id.data),
                area=form.area.data,
                paginas=int(form.paginas.data) if form.paginas.data else None,
                autor=form.autor.data,
                quantidade=int(form.quantidade.data) if form.quantidade.data else 0
            )
            db.session.add(apostila)
            db.session.commit()
            flash('Apostila cadastrada com sucesso!', 'success')
            return redirect(url_for('apostilas.cadastrada'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar apostila: {str(e)}', 'danger')

    return render_template('apostilas/nova.html', form=form)

@bp.route('/cadastrada')
@login_required
def cadastrada():
    """Lista apostilas cadastradas"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_term = request.args.get('q', '').strip()
    filter_type = request.args.get('filter', '')
    area_filter = request.args.get('area', '')

    # Obter todas as áreas distintas para o dropdown
    areas = db.session.query(Apostila.area.distinct()).filter(Apostila.area.isnot(None)).order_by(Apostila.area).all()
    areas = [area[0] for area in areas]

    cursos = Curso.query.order_by(Curso.nome).all()
    query = Apostila.query.join(Curso).order_by(Apostila.nome)

    if search_term:
        query = query.filter(
            (Apostila.nome.ilike(f'%{search_term}%')) |
            (Apostila.id.ilike(f'%{search_term}%')) |
            (Curso.nome.ilike(f'%{search_term}%'))
        )

    if area_filter:
        query = query.filter(Apostila.area == area_filter)

    if filter_type == 'estoque_baixo':
        query = query.filter(Apostila.quantidade <= 10)
    elif filter_type == 'sem_estoque':
        query = query.filter(Apostila.quantidade == 0)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('apostilas/cadastrada.html',
                         pagination=pagination,
                         apostilas=pagination.items,
                         cursos=cursos,
                         areas=areas)

@bp.route('/editar/<string:id>', methods=['GET', 'POST'])
@login_required
def editar_apostila(id):
    """Edita uma apostila existente"""
    apostila = Apostila.query.get_or_404(id)
    cursos = Curso.query.order_by(Curso.nome).all()

    if request.method == 'POST':
        try:
            # Atualiza os campos com tratamento seguro
            apostila.nome = request.form.get('nome', apostila.nome)

            # Tratamento seguro para curso_id
            curso_id = request.form.get('curso_id')
            if curso_id is not None:
                apostila.curso_id = int(curso_id)

            # Tratamento para campos opcionais
            apostila.area = request.form.get('area') or None

            paginas = request.form.get('paginas')
            apostila.paginas = int(paginas) if paginas and paginas.isdigit() else None

            quantidade = request.form.get('quantidade')
            if quantidade is not None:
                apostila.quantidade = int(quantidade)

            apostila.autor = request.form.get('autor') or None

            db.session.commit()
            flash('Apostila atualizada com sucesso!', 'success')
            return redirect(url_for('apostilas.cadastrada'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar apostila: {str(e)}', 'danger')

    return render_template('apostilas/editar.html', apostila=apostila, cursos=cursos)

@bp.route('/api/apostilas/<string:id>', methods=['GET'])
@login_required
def api_apostila(id):
    """Retorna os dados de uma apostila específica"""
    try:
        apostila = Apostila.query.get_or_404(id)
        return jsonify(apostila.to_dict())
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar apostila {id}: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro ao buscar apostila.'}), 500

@bp.route('/excluir/<string:id>', methods=['POST'])
@login_required
def excluir_apostila(id):
    """Exclui uma apostila existente"""
    try:
        apostila = Apostila.query.get_or_404(id)

        # Define apostila_id como NULL para todas as movimentações associadas
        ItemMovimentacao.query.filter_by(apostila_id=id).update({'apostila_id': None})
        db.session.delete(apostila)  # Exclui a apostila
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Apostila excluída com sucesso! Todas as movimentações associadas foram atualizadas.'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao excluir apostila {id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir apostila: {str(e)}'
        }), 500