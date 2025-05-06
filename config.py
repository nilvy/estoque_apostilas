import os

class Config:
    # Usa DATABASE_URL do Railway se existir, senão usa a do Neon
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://neondb_owner:npg_l31qaRPvgNFo@ep-lucky-rain-a4sebw1a-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-aqui'
    LOGIN_DISABLED = False