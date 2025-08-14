import os

def get_database_url():
    """Get the appropriate database URL based on environment"""
    
    # Get environment variables
    local_db_url = os.environ.get('DATABASE_URL')
    project_id = os.environ.get('CLOUD_SQL_PROJECT_ID')
    password = os.environ.get('CLOUD_SQL_PASSWORD')
    region = os.environ.get('CLOUD_SQL_REGION', 'us-central1')
    instance_name = os.environ.get('CLOUD_SQL_INSTANCE_NAME', 'ai-cooking-db')
    database_name = os.environ.get('CLOUD_SQL_DATABASE_NAME', 'ai_cooking_app')
    username = os.environ.get('CLOUD_SQL_USERNAME', 'postgres')
    
    # Debug: Print environment variables
    print(f"Environment variables loaded:")
    print(f"  CALORIE_NINJAS_API_KEY: {'SET' if os.environ.get('CALORIE_NINJAS_API_KEY') else 'NOT SET'}")
    print(f"  DATABASE_URL: {'SET' if local_db_url else 'NOT SET'}")
    print(f"  CLOUD_SQL_PROJECT_ID: {'SET' if project_id else 'NOT SET'}")
    
    # If running in local development with a local database
    if local_db_url:
        return local_db_url
    
    # If all Cloud SQL parameters are available
    if all([project_id, password]):
        # For Google Cloud SQL with private IP (Cloud Run, GKE, etc.)
        if os.environ.get('GAE_ENV') or os.environ.get('CLOUD_RUN_SERVICE'):
            return (
                f"postgresql+psycopg2://{username}:{password}"
                f"@/{database_name}?"
                f"host=/cloudsql/{project_id}:{region}:{instance_name}"
            )
        
        # For local development connecting to Cloud SQL via Cloud SQL Proxy or public IP
        else:
            # This will be set up with the Cloud SQL Connector
            return "postgresql+psycopg2://placeholder"
    
    # Fallback to SQLite for development
    return 'sqlite:///ai_cooking_app.db'

class Config:
    """Base configuration class"""
    
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Google Cloud SQL Configuration
    CLOUD_SQL_PROJECT_ID = os.environ.get('CLOUD_SQL_PROJECT_ID')
    CLOUD_SQL_REGION = os.environ.get('CLOUD_SQL_REGION', 'us-central1')
    CLOUD_SQL_INSTANCE_NAME = os.environ.get('CLOUD_SQL_INSTANCE_NAME', 'ai-cooking-db')
    CLOUD_SQL_DATABASE_NAME = os.environ.get('CLOUD_SQL_DATABASE_NAME', 'ai_cooking_app')
    CLOUD_SQL_USERNAME = os.environ.get('CLOUD_SQL_USERNAME', 'postgres')
    CLOUD_SQL_PASSWORD = os.environ.get('CLOUD_SQL_PASSWORD')
    
    # Local development database (fallback)
    LOCAL_DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # CalorieNinjas API Configuration
    CALORIE_NINJAS_API_KEY = os.environ.get('CALORIE_NINJAS_API_KEY')
    CALORIE_NINJAS_BASE_URL = 'https://api.calorieninjas.com/v1/nutrition'
    
    # AI Service API Keys
    HF_ACCESS_TOKEN = os.environ.get('HF_ACCESS_TOKEN')
    
    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}