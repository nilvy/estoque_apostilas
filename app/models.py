from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, TextAreaField, SubmitField, DateField, SelectField, DecimalField
from wtforms.validators import DataRequired, Optional, Length, Email, EqualTo, NumberRange
from datetime import datetime
from flask import current_app
from flask_login import UserMixin, current_user
from app import db, login_manager


class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14), unique=True)
    data_nascimento = db.Column(db.Date)
    funcao = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def get_id(self):
        return str(self.id)

    # Relacionamentos
    movimentacoes = db.relationship('Movimentacao', back_populates='usuario')
    mensagens = db.relationship('Mensagem', back_populates='usuario')


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


class Curso(db.Model):
    __tablename__ = 'curso'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    duracao = db.Column(db.String(50))
    status = db.Column(db.String(10), server_default='ativo')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    categoria = db.Column(db.String(100))

    # Relacionamentos
    apostilas = db.relationship('Apostila', back_populates='curso', cascade='all, delete-orphan')
    matriculas = db.relationship('Matricula', back_populates='curso')
    movimentacoes = db.relationship('Movimentacao', back_populates='curso')


class Matricula(db.Model):
    __tablename__ = 'matricula'

    codigo = db.Column(db.String(20), primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    status = db.Column(db.String(10), server_default='ativo')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relacionamentos
    curso = db.relationship('Curso', back_populates='matriculas')
    movimentacoes = db.relationship('Movimentacao', back_populates='matricula')


class Apostila(db.Model):
    __tablename__ = 'apostila'

    id = db.Column(db.String(20), primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    area = db.Column(db.String(50))
    paginas = db.Column(db.Integer)
    autor = db.Column(db.String(100))
    quantidade = db.Column(db.Integer, nullable=False, server_default='0')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relacionamentos
    curso = db.relationship('Curso', back_populates='apostilas')
    itens_movimentacao = db.relationship('ItemMovimentacao', back_populates='apostila', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'curso_id': self.curso_id,
            'curso_nome': self.curso.nome if self.curso else None,
            'area': self.area,
            'paginas': self.paginas,
            'autor': self.autor,
            'quantidade': self.quantidade,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Movimentacao(db.Model):
    __tablename__ = 'movimentacao'

    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    matricula_codigo = db.Column(db.String(20), db.ForeignKey('matricula.codigo'))
    tipo = db.Column(db.String(10), nullable=False)
    data = db.Column(db.DateTime, server_default=db.func.now())
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    observacao = db.Column(db.Text)

    # Relacionamentos
    usuario = db.relationship('Usuario', back_populates='movimentacoes')
    curso = db.relationship('Curso', back_populates='movimentacoes')
    matricula = db.relationship('Matricula', back_populates='movimentacoes')
    itens = db.relationship('ItemMovimentacao', back_populates='movimentacao', cascade='all, delete-orphan')


class ItemMovimentacao(db.Model):
    __tablename__ = 'item_movimentacao'

    id = db.Column(db.Integer, primary_key=True)
    movimentacao_id = db.Column(db.Integer, db.ForeignKey('movimentacao.id'), nullable=False)
    apostila_id = db.Column(db.String(20), db.ForeignKey('apostila.id'), nullable=True)
    quantidade = db.Column(db.Integer, nullable=False, server_default='1')

    # Relacionamentos
    movimentacao = db.relationship('Movimentacao', back_populates='itens')
    apostila = db.relationship('Apostila', back_populates='itens_movimentacao')


class Mensagem(db.Model):
    __tablename__ = 'mensagem'

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    lida = db.Column(db.Boolean, server_default='false')
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relacionamentos
    usuario = db.relationship('Usuario', back_populates='mensagens')


# Formulários (mantidos iguais)
class EntregaForm(FlaskForm):
    curso_id = SelectField('Curso', coerce=int, validators=[DataRequired()])
    matricula_codigo = SelectField('Matrícula', coerce=str, validators=[Optional()])
    observacao = TextAreaField('Observações', validators=[Optional()])


class VendaForm(FlaskForm):
    curso_id = SelectField('Curso', coerce=int, validators=[DataRequired()])
    matricula_codigo = SelectField('Matrícula', coerce=str, validators=[DataRequired()])
    apostila_id = SelectField('Apostila', coerce=str, validators=[DataRequired()])
    quantidade = IntegerField('Quantidade', validators=[DataRequired(), NumberRange(min=1)])
    observacao = TextAreaField('Observações', validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super(VendaForm, self).__init__(*args, **kwargs)
        self.curso_id.choices = [(c.id, c.nome) for c in Curso.query.order_by(Curso.nome).all()]
        self.curso_id.choices.insert(0, ('', 'Selecione um curso'))
        self.matricula_codigo.choices = [('', 'Selecione um curso primeiro')]
        self.apostila_id.choices = [('', 'Selecione um curso primeiro')]


def verificar_estoque_baixo():
    try:
        apostilas = Apostila.query.filter(Apostila.quantidade < 5).all()
        for apostila in apostilas:
            msg = Mensagem(
                tipo='estoque',
                conteudo=f'Apostila {apostila.nome} está com estoque baixo: {apostila.quantidade} unidades',
                usuario_id=current_user.id
            )
            db.session.add(msg)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao verificar estoque baixo: {str(e)}")