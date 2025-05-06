from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField, DateField,
                    SelectField, DecimalField, IntegerField, TextAreaField)
from wtforms import validators  # Adicione esta linha
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from app.models import Curso, Matricula


class ApostilaForm(FlaskForm):
    id = StringField('ID', validators=[DataRequired()])
    nome = StringField('Nome', validators=[DataRequired()])
    curso_id = SelectField('Curso', coerce=int, validators=[DataRequired()])
    area = SelectField('Área', choices=[
        ('', 'Selecione uma área'),
        ('Informática e Tecnologia', 'Informática e Tecnologia'),
        ('Administração e Vendas', 'Administração e Vendas'),
        ('Design, Web e Games', 'Design, Web e Games'),
        ('Saúde', 'Saúde'),
        ('Inglês', 'Inglês'),
        ('Cursos VIP', 'Cursos VIP')
    ], validators=[Optional()])
    paginas = IntegerField('Páginas', validators=[Optional()])
    autor = StringField('Autor', validators=[Optional()])
    quantidade = IntegerField('Quantidade', validators=[DataRequired()])


class VendaForm(FlaskForm):
    curso_id = SelectField(
        'Curso',
        coerce=lambda x: int(x) if x else None,
        validators=[DataRequired()],
        choices=[]
    )
    matricula_codigo = SelectField(
        'Matrícula',
        coerce=str,
        validators=[DataRequired()],
        choices=[],
        validate_choice=False
    )
    apostila_id = SelectField(
        'Apostila',
        coerce=str,
        validators=[DataRequired()],
        choices=[],
        validate_choice=False
    )
    quantidade = IntegerField('Quantidade', validators=[DataRequired(), NumberRange(min=1)])
    observacao = TextAreaField('Observações', validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super(VendaForm, self).__init__(*args, **kwargs)
        self.curso_id.choices = [(str(c.id), c.nome) for c in Curso.query.order_by(Curso.nome).all()]
        self.curso_id.choices.insert(0, ('', 'Selecione um curso'))

class DynamicSelectField(SelectField):
    def pre_validate(self, form):
        """Override para evitar validação de choices"""
        pass

class EntregaForm(FlaskForm):
    curso_id = SelectField(
        'Curso',
        coerce=lambda x: int(x) if x else None,
        validators=[DataRequired()],
        choices=[]
    )
    matricula_codigo = SelectField(
        'Matrícula',
        coerce=str,
        validators=[Optional()],
        choices=[],
        validate_choice=False  # Permite valores não listados nas choices
    )
    observacao = TextAreaField('Observações', validators=[Optional()])
    submit = SubmitField('Registrar Entrega')

    def __init__(self, *args, **kwargs):
        super(EntregaForm, self).__init__(*args, **kwargs)
        # Carrega apenas os cursos (matrículas via AJAX)
        self.curso_id.choices = [(str(c.id), c.nome) for c in Curso.query.order_by(Curso.nome).all()]
        self.curso_id.choices.insert(0, ('', 'Selecione um curso'))