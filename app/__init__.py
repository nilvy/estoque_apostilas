from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from config import Config
import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

# Instâncias globais das extensões
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()

def create_app(config_class: Optional[type] = Config) -> Flask:
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # Configuração do LoginManager com type hints
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'

    # Configuração do logging (somente em produção)
    configure_logging(app)

    # Registra blueprints
    register_blueprints(app)

    return app

def configure_logging(app: Flask) -> None:
    """Configura o sistema de logging da aplicação"""
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler(
            'logs/estoque_apostilas.log',
            maxBytes=10240,
            backupCount=10
        )

        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)

        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Estoque de Apostilas startup')

def register_blueprints(app: Flask) -> None:
    """Registra todos os blueprints da aplicação"""
    from app.routes.auth import bp as auth_bp
    from app.routes.main import bp as main_bp
    from app.routes.movimentacoes import bp as movimentacoes_bp
    from app.routes.apostilas import bp as apostilas_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(movimentacoes_bp, url_prefix='/movimentacoes')
    app.register_blueprint(apostilas_bp, url_prefix='/apostilas')

# Import de modelos para garantir que são registrados com SQLAlchemy
from app import models