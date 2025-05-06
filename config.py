import os

class Config:
    DB_URL = os.getenv('DATABASE_URL', 'postgresql://neondb_owner:npg_l31qaRPvgNFo@ep-lucky-rain-a4sebw1a-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require')
    SQLALCHEMY_DATABASE_URI = DB_URL.replace('postgres://', 'postgresql://', 1) if DB_URL.startswith('postgres://') else DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False