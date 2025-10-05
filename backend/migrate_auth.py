#!/usr/bin/env python3
"""
Database migration script to add password_hash column to users table
Run this script to update the existing database schema
"""

import os
import sys
from flask import Flask
from flask_migrate import upgrade, downgrade
from flask_sqlalchemy import SQLAlchemy

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import db
from app.models.user import User

def run_migration():
    """Run the database migration"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if password_hash column already exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            if 'password_hash' in columns:
                print("password_hash column already exists in users table")
                return True
            
            # Add the password_hash column
            print("Adding password_hash column to users table...")
            
            # For SQLite (development)
            if 'sqlite' in str(db.engine.url):
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE users ADD COLUMN password_hash VARCHAR(128)'))
                print("Added password_hash column to SQLite database")
            
            # For PostgreSQL (production)
            elif 'postgresql' in str(db.engine.url):
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE users ADD COLUMN password_hash VARCHAR(128)'))
                print("Added password_hash column to PostgreSQL database")
            
            else:
                print("Unsupported database type")
                return False
            
            # Commit the changes
            db.session.commit()
            print("Migration completed successfully!")
            
        except Exception as e:
            print(f"Migration failed: {str(e)}")
            db.session.rollback()
            return False
    
    return True

def create_test_user():
    """Create a test user for development"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if test user already exists
            test_user = User.query.filter_by(email='test@example.com').first()
            if test_user:
                print("Test user already exists")
                return True
            
            # Create test user
            test_user = User(
                email='test@example.com',
                username='testuser'
            )
            test_user.set_password('TestPassword123')
            
            db.session.add(test_user)
            db.session.commit()
            
            print("Test user created successfully!")
            print("   Email: test@example.com")
            print("   Username: testuser")
            print("   Password: TestPassword123")
            
        except Exception as e:
            print(f"Failed to create test user: {str(e)}")
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    print("Starting database migration...")
    
    if run_migration():
        print("\nCreating test user...")
        create_test_user()
        print("\nAll migrations completed successfully!")
    else:
        print("\nMigration failed!")
        sys.exit(1)