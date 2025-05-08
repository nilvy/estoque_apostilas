import os

class Config:
    SQLALCHEMY_DATABASE_URI =  "postgresql://neondb_owner:npg_l31qaRPvgNFo@ep-lucky-rain-a4sebw1a-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "uma-chave-secreta-padrao")