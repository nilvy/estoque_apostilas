from flask import Blueprint

bp = Blueprint('debug', __name__)

@bp.route('/debug-db')
def debug_db():
    try:
        # Importar db apenas dentro da função
        from app import db
        result = db.session.execute('SELECT 1').scalar()
        return f"Database connection successful: {result}"
    except Exception as e:
        return f"Database connection failed: {str(e)}"