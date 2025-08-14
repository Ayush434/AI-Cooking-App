import os
import atexit
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from .config import config
from .database import init_db, cleanup_connector

def create_app(config_name=None):
    """Create and configure Flask application"""
    
    # Load environment variables from .env file
    load_dotenv()
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config.get(config_name, config['default']))
    
    # Initialize CORS
    CORS(app)
    
    # Initialize database
    init_db(app)
    
    # Register cleanup function
    atexit.register(lambda: cleanup_connector(app))
    
    # Register Blueprints
    from .routes.recipes import recipes_bp
    app.register_blueprint(recipes_bp, url_prefix="/api/recipes")

    return app


