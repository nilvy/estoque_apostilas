web: gunicorn "run:app" --bind 0.0.0.0:$PORT --timeout 120 --workers 2
release: flask db upgrade
