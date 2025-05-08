import os

class Config:
    SQLALCHEMY_DATABASE_URI =  "postgresql://neondb_owner:npg_l31qaRPvgNFo@ep-lucky-rain-a4sebw1a-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "5070ce319b9765a54035932b51c2e291a7d1cce65488fc68df3bd5ea07d59809"
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,  # Verifica se a conexão está ativa antes de usá-la
    "pool_size": 5,         # Número de conexões no pool
    "max_overflow": 10      # Conexões extras permitidas além do pool
}