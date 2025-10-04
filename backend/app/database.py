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
    
    print(f"Setting up Cloud SQL connector:")
    print(f"  Project ID: {project_id}")
    print(f"  Region: {region}")
    print(f"  Instance: {instance_name}")
    print(f"  Database: {database_name}")
    print(f"  Username: {username}")
    print(f"  Password: {'SET' if password else 'NOT SET'}")
    
    # Don't set up connector in production environments (they use unix sockets)
    if os.environ.get('GAE_ENV') or os.environ.get('CLOUD_RUN_SERVICE'):
        print("Skipping Cloud SQL connector setup - running in production environment")
        return
    
    try:
        # Initialize Connector object
        print("Initializing Cloud SQL Connector...")
        connector = Connector()
        
        # Function to return the database connection
        def getconn():
            print(f"Creating connection to {project_id}:{region}:{instance_name}")
            conn = connector.connect(
                f"{project_id}:{region}:{instance_name}",
                "pg8000",
                user=username,
                password=password,
                db=database_name,
            )
            print("Connection established successfully")
            return conn
        
        # Create SQLAlchemy engine with the connector
        print("Creating SQLAlchemy engine...")
        engine = sqlalchemy.create_engine(
            "postgresql+pg8000://",
            creator=getconn,
            pool_size=5,
            max_overflow=2,
            pool_pre_ping=True,
            pool_recycle=300,
        )
        
        # Test the connection
        print("Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text("SELECT 1"))
            print("Database connection test successful!")
        
        # Update Flask-SQLAlchemy to use our custom engine
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'creator': getconn,
            'pool_size': 5,
            'max_overflow': 2,
            'pool_pre_ping': True,
            'pool_recycle': 300,
        }
        app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+pg8000://"
        
        # Store the engine and connector for Flask-SQLAlchemy
        app.cloud_sql_engine = engine
        app.cloud_sql_connector = connector
        
        print(f"✅ Successfully connected to Cloud SQL instance: {project_id}:{region}:{instance_name}")
        
    except Exception as e:
        print(f"❌ Failed to connect to Cloud SQL: {e}")
        print("Falling back to local SQLite database")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ai_cooking_app.db'

def cleanup_connector(app):
    """Clean up Cloud SQL connector when app shuts down"""
    connector = getattr(app, 'cloud_sql_connector', None)
    if connector:
        connector.close()