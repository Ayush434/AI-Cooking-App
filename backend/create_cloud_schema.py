#!/usr/bin/env python3
"""
Script to create database schema in Google Cloud SQL
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import db
from app.models.user import User

def create_schema():
    """Create database schema in Google Cloud SQL"""
    
    print("Connecting to Google Cloud SQL...")
    app = create_app()
    
    with app.app_context():
        try:
            print("Creating database schema...")
            
            # Create all tables
            db.create_all()
            
            print("Database schema created successfully!")
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Tables created: {tables}")
            
            # Check if users table exists and has the right structure
            if 'users' in tables:
                columns = [col['name'] for col in inspector.get_columns('users')]
                print(f"Users table columns: {columns}")
                
                # Check if password_hash column exists
                if 'password_hash' in columns:
                    print("✅ Users table with password_hash column is ready!")
                else:
                    print("❌ password_hash column missing - need to add it")
                    # Add password_hash column
                    with db.engine.connect() as conn:
                        conn.execute(db.text('ALTER TABLE users ADD COLUMN password_hash VARCHAR(128)'))
                    print("✅ Added password_hash column")
            else:
                print("❌ Users table not found")
                
        except Exception as e:
            print(f"Schema creation failed: {str(e)}")
            return False
    
    return True

if __name__ == '__main__':
    print("Creating database schema in Google Cloud SQL...")
    create_schema()
