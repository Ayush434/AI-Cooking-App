import os
import logging
from google.cloud.sql.connector import Connector
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize SQLAlchemy and Migrate
db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialize database with Flask app"""
    
    # Configure SQLAlchemy
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Set up Cloud SQL Connector if using Cloud SQL
    if should_use_cloud_sql():
        setup_cloud_sql_connector(app)
    
    return db

def should_use_cloud_sql():
    """Check if we should use Cloud SQL based on environment variables"""
    return all([
        os.environ.get('CLOUD_SQL_PROJECT_ID'),
        os.environ.get('CLOUD_SQL_PASSWORD'),
        not os.environ.get('DATABASE_URL')  # No local DB URL provided
    ])

def setup_cloud_sql_connector(app):
    """Set up Google Cloud SQL Connector for local development"""
    
    project_id = os.environ.get('CLOUD_SQL_PROJECT_ID')
    region = os.environ.get('CLOUD_SQL_REGION', 'us-central1')
    instance_name = os.environ.get('CLOUD_SQL_INSTANCE_NAME', 'ai-cooking-db')
    database_name = os.environ.get('CLOUD_SQL_DATABASE_NAME', 'ai_cooking_app')
    username = os.environ.get('CLOUD_SQL_USERNAME', 'postgres')
    password = os.environ.get('CLOUD_SQL_PASSWORD')
    
    # Don't set up connector in production environments (they use unix sockets)
    if os.environ.get('GAE_ENV') or os.environ.get('CLOUD_RUN_SERVICE'):
        return
    
    try:
        # Initialize Connector object
        connector = Connector()
        
        # Function to return the database connection
        def getconn():
            conn = connector.connect(
                f"{project_id}:{region}:{instance_name}",
                "pg8000",
                user=username,
                password=password,
                db=database_name,
            )
            return conn
        
        # Create connection pool
        pool = sqlalchemy.create_engine(
            "postgresql+pg8000://",
            creator=getconn,
            pool_size=5,
            max_overflow=2,
            pool_pre_ping=True,
            pool_recycle=300,
        )
        
        # Create a custom engine with the connector
        engine = sqlalchemy.create_engine(
            "postgresql+pg8000://",
            creator=getconn,
            pool_size=5,
            max_overflow=2,
            pool_pre_ping=True,
            pool_recycle=300,
        )
        
        # Update the database URI to use the pool
        app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+pg8000://"
        
        logging.info(f"Connected to Cloud SQL instance: {project_id}:{region}:{instance_name}")
        
        # Store connector for cleanup
        app.cloud_sql_connector = connector
        
    except Exception as e:
        logging.error(f"Failed to connect to Cloud SQL: {e}")
        logging.info("Falling back to local SQLite database")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ai_cooking_app.db'

def cleanup_connector(app):
    """Clean up Cloud SQL connector when app shuts down"""
    connector = getattr(app, 'cloud_sql_connector', None)
    if connector:
        connector.close()