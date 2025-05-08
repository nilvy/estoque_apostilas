from app.routes.debug import bp as debug_bp
app.register_blueprint(debug_bp, url_prefix='/debug')