import os
from urllib.parse import urlparse, urlunparse

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            raise ValueError("DATABASE_URL não configurada")

        # Parse e ajuste da URL
        parsed = urlparse(db_url)
        if parsed.scheme == 'postgres':
            parsed = parsed._replace(scheme='postgresql')
        return urlunparse(parsed)

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 5,
        'max_overflow': 10,
        'connect_args': {
            'connect_timeout': 10,
            'sslmode': 'require'
        }
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False