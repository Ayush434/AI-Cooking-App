from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Register Blueprints
    from .routes.recipes import recipes_bp
    app.register_blueprint(recipes_bp, url_prefix="/api/recipes")

    return app


