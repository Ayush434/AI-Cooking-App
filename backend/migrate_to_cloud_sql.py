#!/usr/bin/env python3
"""
Simple script to migrate SQLite data to Google Cloud SQL
"""

import sqlite3
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import db
from app.models.user import User

def migrate_to_cloud_sql():
    """Migrate SQLite data to Google Cloud SQL using direct SQLite access"""
    
    # Read from SQLite directly
    print("Reading data from SQLite database...")
    sqlite_path = os.path.join(os.path.dirname(__file__), 'instance', 'ai_cooking_app.db')
    
    if not os.path.exists(sqlite_path):
        print(f"SQLite database not found at {sqlite_path}")
        return False
    
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    
    # Get all users from SQLite
    cursor.execute("SELECT id, username, email, password_hash, dietary_preferences, allergies, favorite_cuisines, created_at, updated_at FROM users")
    sqlite_users = cursor.fetchall()
    conn.close()
    
    print(f"Found {len(sqlite_users)} users in SQLite database")
    
    if not sqlite_users:
        print("No users to migrate from SQLite")
        return True
    
    # Now connect to Cloud SQL and migrate
    print("\nConnecting to Google Cloud SQL...")
    cloud_app = create_app()
    
    with cloud_app.app_context():
        try:
            # Check existing users in Cloud SQL
            existing_users = User.query.all()
            print(f"Found {len(existing_users)} existing users in Cloud SQL")
            
            # Migrate users
            migrated_count = 0
            for sqlite_user in sqlite_users:
                user_id, username, email, password_hash, dietary_preferences, allergies, favorite_cuisines, created_at, updated_at = sqlite_user
                
                # Check if user already exists in Cloud SQL
                existing_user = User.query.filter_by(email=email).first()
                
                if existing_user:
                    print(f"User {email} already exists in Cloud SQL, skipping...")
                    continue
                
                # Create new user in Cloud SQL
                new_user = User(
                    email=email,
                    username=username,
                    password_hash=password_hash,
                    dietary_preferences=eval(dietary_preferences) if dietary_preferences else [],
                    allergies=eval(allergies) if allergies else [],
                    favorite_cuisines=eval(favorite_cuisines) if favorite_cuisines else []
                )
                
                db.session.add(new_user)
                migrated_count += 1
                print(f"Migrated user: {email}")
            
            if migrated_count > 0:
                db.session.commit()
                print(f"\nSuccessfully migrated {migrated_count} users to Google Cloud SQL!")
            else:
                print("\nNo new users to migrate (all users already exist in Cloud SQL)")
            
            # Verify migration
            print("\nVerifying migration...")
            cloud_users = User.query.all()
            print(f"Total users in Cloud SQL: {len(cloud_users)}")
            
            for user in cloud_users:
                print(f"  - {user.username} ({user.email})")
                
        except Exception as e:
            print(f"Migration failed: {str(e)}")
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    print("Migrating SQLite data to Google Cloud SQL...")
    migrate_to_cloud_sql()