from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
import os
import logging
from logging.handlers import RotatingFileHandler

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Corrige URL do PostgreSQL se necessário
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        # Importa modelos
        from app.models import Usuario, Curso, Matricula, Apostila, Movimentacao, ItemMovimentacao

        # Importa blueprints
        from app.routes.auth import bp as auth_bp
        from app.routes.main import bp as main_bp
        from app.routes.movimentacoes import bp as movimentacoes_bp
        from app.routes.apostilas import bp as apostilas_bp

        # Registra blueprints
        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(movimentacoes_bp, url_prefix='/movimentacoes')
        app.register_blueprint(apostilas_bp, url_prefix='/apostilas')

        # Cria tabelas (só executa se não existirem)
        db.create_all()

        # Configura logging
        if not app.debug:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/estoque_apostilas.log', maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Estoque de Apostilas startup')

    return app