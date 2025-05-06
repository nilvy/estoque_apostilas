import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()  # Carrega variáveis do .env

def get_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

def check_tables():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            return [row[0] for row in cur.fetchall()]

if __name__ == "__main__":
    print("Tabelas existentes:", check_tables())