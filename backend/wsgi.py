# wsgi.py - Production WSGI entry point for Render.com
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
