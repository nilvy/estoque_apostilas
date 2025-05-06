import os

class Config:
    # Usa DATABASE_URL do Railway ou sua conexão Neon
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://usuario:senha@ep-nome-do-neon.aws-region.aws.neon.tech/nomedb?sslmode=require')

    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'sua-chave-secreta')