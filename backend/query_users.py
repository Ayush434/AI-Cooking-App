#!/usr/bin/env python3
"""
Script to query Google Cloud SQL database and show user data
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

def query_users():
    """Query and display all users from the database"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Connecting to database...")
            print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print("-" * 50)
            
            # Get all users
            users = User.query.all()
            
            if not users:
                print("No users found in the database.")
                return
            
            print(f"Found {len(users)} user(s) in the database:")
            print("-" * 50)
            
            for i, user in enumerate(users, 1):
                print(f"User {i}:")
                print(f"  ID: {user.id}")
                print(f"  Username: {user.username}")
                print(f"  Email: {user.email}")
                print(f"  Created: {user.created_at}")
                print(f"  Updated: {user.updated_at}")
                print(f"  Dietary Preferences: {user.dietary_preferences}")
                print(f"  Allergies: {user.allergies}")
                print(f"  Favorite Cuisines: {user.favorite_cuisines}")
                print(f"  Has Password Hash: {'Yes' if user.password_hash else 'No'}")
                print("-" * 30)
            
            # Show database info
            print("\nDatabase Information:")
            print(f"  Database Type: {db.engine.url.drivername}")
            print(f"  Database Name: {db.engine.url.database}")
            print(f"  Host: {db.engine.url.host}")
            
        except Exception as e:
            print(f"Error querying database: {str(e)}")

if __name__ == '__main__':
    print("Querying Google Cloud SQL Database...")
    query_users()
