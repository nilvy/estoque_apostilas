import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')
    DB_URL = os.getenv('DATABASE_URL')
    SQLALCHEMY_DATABASE_URI = DB_URL.replace('postgres://', 'postgresql://', 1) if DB_URL and DB_URL.startswith('postgres://') else DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False