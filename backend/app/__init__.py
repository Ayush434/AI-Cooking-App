import os
import atexit
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
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
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Configure JWT to handle user identity properly
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id if hasattr(user, 'id') else str(user)
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        from .models.user import User
        # Convert identity to integer since user.id is an integer column
        try:
            user_id = int(identity)
            return User.query.filter_by(id=user_id).one_or_none()
        except (ValueError, TypeError):
            return None
    
    # Initialize database
    init_db(app)
    
    # Register cleanup function
    atexit.register(lambda: cleanup_connector(app))
    
    # Register Blueprints
    from .routes.recipes import recipes_bp
    from .routes.auth import auth_bp
    app.register_blueprint(recipes_bp, url_prefix="/api/recipes")
    app.register_blueprint(auth_bp)
    
    # Simple health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return {'status': 'healthy', 'message': 'SnackHack API is running'}

    return app


