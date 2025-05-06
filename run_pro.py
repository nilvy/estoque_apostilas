from app import create_app

app = create_app()

if __name__ == "__main__":
    # Para desenvolvimento no Windows
    from waitress import serve
    serve(app, host="0.0.0.0", port=10000)