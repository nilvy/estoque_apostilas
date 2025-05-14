from flask import Blueprint, jsonify, render_template, current_app, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import Apostila, Curso, Matricula, Usuario, Mensagem, Movimentacao, ItemMovimentacao
from app.forms import EntregaForm, VendaForm
from app import db
from datetime import datetime, timedelta
from typing import List, Tuple  # Adicionado para type hints


bp = Blueprint('movimentacoes', __name__)

def verificar_estoque_baixo():
    try:
        # Limpar alertas antigos
        Mensagem.query.filter_by(tipo='estoque').delete()

        # Verificar todos os níveis de estoque
        apostilas = Apostila.query.all()

        for apostila in apostilas:
            if apostila.quantidade <= 35:
                if apostila.quantidade > 15:
                    nivel = 'atenção'
                elif apostila.quantidade > 5:
                    nivel = 'baixo'
                elif apostila.quantidade > 0:
                    nivel = 'crítico'
                else:
                    nivel = 'esgotado'

                msg = Mensagem(
                    tipo='estoque',
                    conteudo=f'Estoque {nivel}: {apostila.nome}',
                    apostila=apostila,
                    usuario_id=current_user.id
                )
                db.session.add(msg)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao verificar estoque: {str(e)}")


@bp.route('/entrega', methods=['GET', 'POST'])
@login_required
def entrega():
    form = EntregaForm()

    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Verifica se o curso existe
            curso = Curso.query.get(int(form.curso_id.data))
            if not curso:
                flash('Curso não encontrado', 'danger')
                return redirect(url_for('movimentacoes.entrega'))

            # Cria a movimentação
            movimentacao = Movimentacao(
                tipo='entrega',
                usuario_id=current_user.id,
                curso_id=curso.id,
                matricula_codigo=form.matricula_codigo.data if form.matricula_codigo.data else None,
                observacao=form.observacao.data
            )
            db.session.add(movimentacao)
            db.session.flush()  # Garante que o ID da movimentação é gerado

            # Atualiza o estoque das apostilas do curso
            apostilas = Apostila.query.filter_by(curso_id=curso.id).all()
            for apostila in apostilas:
                if apostila.quantidade < 1:
                    flash(f'Estoque insuficiente para apostila: {apostila.nome}', 'warning')
                    continue

                apostila.quantidade -= 1
                item = ItemMovimentacao(
                    movimentacao_id=movimentacao.id,
                    apostila_id=apostila.id,
                    quantidade=1
                )
                db.session.add(item)

            db.session.commit()
            flash('Entrega registrada com sucesso!', 'success')
            return redirect(url_for('movimentacoes.movimentacao'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar entrega: {str(e)}', 'danger')
            current_app.logger.error(f"Erro na entrega: {str(e)}", exc_info=True)

    return render_template('movimentacoes/entrega.html', form=form)


@bp.route('/entrega/matriculas/<int:curso_id>', methods=['GET'])
@login_required
def get_matriculas_entrega(curso_id):
    """Retorna matrículas ativas de um curso específico para a rota de entrega."""
    try:
        matriculas = Matricula.query.filter_by(curso_id=curso_id, status='ativo').order_by(Matricula.nome).all()
        return jsonify([{'codigo': m.codigo, 'nome': m.nome} for m in matriculas])
    except Exception as e:
        current_app.logger.error(f"Erro ao carregar matrículas: {str(e)}", exc_info=True)
        return jsonify([]), 500

@bp.route('/venda', methods=['GET', 'POST'])
@login_required
def venda():
    form = VendaForm()

    if request.method == 'GET':
        # Carrega apenas cursos (matrículas/apostilas via AJAX)
        cursos = Curso.query.order_by(Curso.nome).all()
        form.curso_id.choices = [(str(c.id), c.nome) for c in cursos]
        form.curso_id.choices.insert(0, ('', 'Selecione um curso'))

    if form.validate_on_submit():
        try:
            # Verifica se os valores existem no banco
            matricula = Matricula.query.filter_by(codigo=form.matricula_codigo.data).first()
            apostila = Apostila.query.get(form.apostila_id.data)

            if not matricula:
                flash('Matrícula não encontrada', 'danger')
                return redirect(url_for('movimentacoes.venda'))

            if not apostila:
                flash('Apostila não encontrada', 'danger')
                return redirect(url_for('movimentacoes.venda'))

            # Restante da lógica de venda...
            movimentacao = Movimentacao(
                tipo='venda',
                usuario_id=current_user.id,
                curso_id=int(form.curso_id.data),
                matricula_codigo=form.matricula_codigo.data,
                observacao=form.observacao.data
            )
            db.session.add(movimentacao)
            db.session.flush()

            item = ItemMovimentacao(
                movimentacao_id=movimentacao.id,
                apostila_id=form.apostila_id.data,
                quantidade=form.quantidade.data
            )
            db.session.add(item)

            apostila.quantidade -= form.quantidade.data
            db.session.commit()

            flash('Venda registrada com sucesso!', 'success')
            return redirect(url_for('movimentacoes.movimentacao'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar venda: {str(e)}', 'danger')

    return render_template('movimentacoes/venda.html', form=form)

# movimentacoes.py
@bp.route('/api/movimentacoes/matriculas_por_curso/<int:curso_id>')
@login_required
def api_matriculas_por_curso(curso_id):
    matriculas = Matricula.query.filter_by(
        curso_id=curso_id,
        status='ativo'
    ).order_by(Matricula.nome).all()

    return jsonify([{
        'codigo': m.codigo,
        'nome': m.nome
    } for m in matriculas])

@bp.route('/api/movimentacoes/apostilas_por_curso/<int:curso_id>')
@login_required
def api_apostilas_por_curso(curso_id):
    apostilas = Apostila.query.filter_by(
        curso_id=curso_id
    ).order_by(Apostila.nome).all()

    return jsonify([{
        'id': a.id,
        'nome': a.nome,
        'quantidade': a.quantidade
    } for a in apostilas])


@bp.route('/movimentacao')
@login_required
def movimentacao():
    try:
        current_app.logger.info("Acessando rota movimentacao")

        # Filtros
        curso_id = request.args.get('curso_id', type=int)
        tipo = request.args.get('tipo', type=str)
        page = request.args.get('page', 1, type=int)

        query = db.session.query(Movimentacao).options(
            db.joinedload(Movimentacao.usuario),
            db.joinedload(Movimentacao.curso),
            db.joinedload(Movimentacao.matricula_rel),
            db.joinedload(Movimentacao.itens).joinedload(ItemMovimentacao.apostila)
        )

        if curso_id:
            query = query.filter(Movimentacao.curso_id == curso_id)
        if tipo:
            query = query.filter(Movimentacao.tipo == tipo)

        movimentacoes = query.order_by(Movimentacao.data.desc()).paginate(page=page, per_page=10)

        # Carregar cursos para o filtro
        cursos = Curso.query.order_by(Curso.nome).all()

        return render_template('movimentacoes/movimentacao.html',
                               movimentacoes=movimentacoes,
                               cursos=cursos)
    except Exception as e:
        current_app.logger.error(f"Erro ao carregar movimentações: {str(e)}", exc_info=True)
        flash("Ocorreu um erro ao carregar as movimentações. Verifique os logs para mais detalhes.", "danger")
        return redirect(url_for('main.admin'))

@bp.route('/movimentacao/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_movimentacao(id):
    try:
        movimentacao = Movimentacao.query.get_or_404(id)

        # Se for venda, devolve o estoque
        if movimentacao.tipo == 'venda':
            for item in movimentacao.itens:
                apostila = Apostila.query.get(item.apostila_id)
                apostila.quantidade += item.quantidade

        db.session.delete(movimentacao)
        db.session.commit()
        flash('Movimentação excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir movimentação', 'danger')
        current_app.logger.error(f"Erro ao excluir movimentação {id}: {str(e)}")

    return redirect(url_for('movimentacoes.movimentacao'))

@bp.route('/relatorios')
@login_required
def relatorios():
    try:
        current_year = datetime.now().year
        last_month = datetime.now() - timedelta(days=30)

        # Consulta segura para totais
        total_movimentacoes = db.session.query(
            db.func.count(Movimentacao.id)
        ).filter(
            db.extract('year', Movimentacao.data) == current_year
        ).scalar() or 0  # Retorna 0 se nenhum resultado

        # Cursos com mais entregas (com tratamento para None)
        cursos_entregas = db.session.query(
            Curso.nome,
            db.func.count(Movimentacao.id).label('total')
        ).join(Movimentacao, Movimentacao.curso_id == Curso.id)\
         .filter(Movimentacao.tipo == 'entrega')\
         .filter(Movimentacao.data >= last_month)\
         .group_by(Curso.id)\
         .order_by(db.desc('total'))\
         .limit(5)\
         .all() or []  # Retorna lista vazia se nenhum resultado

        # Apostilas mais vendidas (com tratamento para None)
        apostilas_vendidas = db.session.query(
            Apostila.nome,
            db.func.sum(ItemMovimentacao.quantidade).label('total')
        ).join(ItemMovimentacao, ItemMovimentacao.apostila_id == Apostila.id)\
         .join(Movimentacao, ItemMovimentacao.movimentacao_id == Movimentacao.id)\
         .filter(Movimentacao.tipo == 'venda')\
         .filter(Movimentacao.data >= last_month)\
         .group_by(Apostila.id)\
         .order_by(db.desc('total'))\
         .limit(5)\
         .all() or []  # Retorna lista vazia se nenhum resultado

        return render_template('movimentacoes/relatorios.html',
                            total_movimentacoes=total_movimentacoes,
                            cursos_entregas=cursos_entregas,
                            apostilas_vendidas=apostilas_vendidas,
                            current_year=current_year)

    except Exception as e:
        current_app.logger.error(f"Erro ao gerar relatórios: {str(e)}", exc_info=True)
        flash("Ocorreu um erro ao gerar os relatórios. Verifique os logs para mais detalhes.", "danger")
        return redirect(url_for('main.admin'))

@bp.route('/api/relatorios/dados')
@login_required
def dados_relatorios():
    try:
        current_year = datetime.now().year

        # Movimentações por tipo (últimos 30 dias)
        movimentacoes_por_tipo = db.session.query(
            Movimentacao.tipo,
            db.func.count(Movimentacao.id).label('total')
        ).filter(Movimentacao.data >= datetime.now() - timedelta(days=30))\
         .group_by(Movimentacao.tipo)\
         .all()

        # Categorias de cursos mais movimentadas
        categorias_movimentadas = db.session.query(
            Curso.categoria,
            db.func.count(Movimentacao.id).label('total')
        ).join(Movimentacao.curso)\
         .filter(Movimentacao.data >= datetime.now() - timedelta(days=30))\
         .group_by(Curso.categoria)\
         .order_by(db.desc('total'))\
         .all()

        # Dados para gráfico de dispersão de movimentações anuais
        movimentacoes_anuais = db.session.query(
            db.extract('month', Movimentacao.data).label('mes'),
            Movimentacao.tipo,
            db.func.count(Movimentacao.id).label('total')
        ).filter(db.extract('year', Movimentacao.data) == current_year)\
         .group_by(db.extract('month', Movimentacao.data), Movimentacao.tipo)\
         .order_by(db.asc('mes'))\
         .all()

        return jsonify({
            'movimentacoes_por_tipo': [
                {'tipo': tipo, 'total': total}
                for tipo, total in movimentacoes_por_tipo
            ],
            'categorias_movimentadas': [
                {'categoria': cat, 'total': total}
                for cat, total in categorias_movimentadas
            ],
            'movimentacoes_anuais': [
                {'mes': mes, 'tipo': tipo, 'total': total}
                for mes, tipo, total in movimentacoes_anuais
            ]
        })

    except Exception as e:
        current_app.logger.error(f"Erro na API de relatórios: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Erro ao gerar relatório',
            'movimentacoes_por_tipo': [],
            'categorias_movimentadas': [],
            'movimentacoes_anuais': []
        }), 200


@bp.route('/api/apostilas/por-curso/<int:curso_id>')
@login_required
def get_apostilas_por_curso(curso_id):
    apostilas = Apostila.query.filter_by(curso_id=curso_id).all()
    return jsonify([{
        'id': a.id,
        'nome': a.nome,
        'quantidade': a.quantidade
    } for a in apostilas])

