#!/usr/bin/env python3
"""
Database initialization script for AI Cooking App
Run this script to create database tables and populate initial data
"""

import os
import sys
from flask import Flask
from app import create_app
from app.database import db
from app.models import User, Recipe, Ingredient, RecipeIngredient

def init_database():
    """Initialize database tables and add sample data"""
    
    print("Initializing AI Cooking App Database...")
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Add sample ingredients if none exist
            if Ingredient.query.count() == 0:
                print("Adding sample ingredients...")
                add_sample_ingredients()
                print("✅ Sample ingredients added!")
            else:
                print("ℹ️ Ingredients already exist, skipping sample data")
            
            print("\n🎉 Database initialization completed successfully!")
            print("\nNext steps:")
            print("1. Set your environment variables (see .env.example)")
            print("2. Install dependencies: pip install -r requirements.txt")
            print("3. Run the app: python run.py")
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            sys.exit(1)

def add_sample_ingredients():
    """Add sample ingredients to the database"""
    
    sample_ingredients = [
        # Vegetables
        {'name': 'tomato', 'category': 'vegetables', 'alternative_names': ['tomatoes', 'cherry tomatoes']},
        {'name': 'onion', 'category': 'vegetables', 'alternative_names': ['onions', 'yellow onion', 'white onion']},
        {'name': 'garlic', 'category': 'vegetables', 'alternative_names': ['garlic cloves', 'garlic bulb']},
        {'name': 'potato', 'category': 'vegetables', 'alternative_names': ['potatoes', 'russet potato']},
        {'name': 'carrot', 'category': 'vegetables', 'alternative_names': ['carrots', 'baby carrots']},
        {'name': 'bell pepper', 'category': 'vegetables', 'alternative_names': ['bell peppers', 'red pepper', 'green pepper']},
        {'name': 'mushroom', 'category': 'vegetables', 'alternative_names': ['mushrooms', 'button mushrooms']},
        {'name': 'spinach', 'category': 'vegetables', 'alternative_names': ['baby spinach', 'fresh spinach']},
        
        # Proteins
        {'name': 'chicken breast', 'category': 'proteins', 'alternative_names': ['chicken', 'chicken breasts']},
        {'name': 'ground beef', 'category': 'proteins', 'alternative_names': ['beef', 'ground meat']},
        {'name': 'salmon', 'category': 'proteins', 'alternative_names': ['salmon fillet', 'fresh salmon']},
        {'name': 'eggs', 'category': 'proteins', 'alternative_names': ['egg', 'chicken eggs']},
        {'name': 'tofu', 'category': 'proteins', 'alternative_names': ['bean curd', 'firm tofu']},
        
        # Grains & Starches
        {'name': 'rice', 'category': 'grains', 'alternative_names': ['white rice', 'jasmine rice', 'basmati rice']},
        {'name': 'pasta', 'category': 'grains', 'alternative_names': ['spaghetti', 'penne', 'fusilli']},
        {'name': 'bread', 'category': 'grains', 'alternative_names': ['loaf', 'white bread', 'whole wheat bread']},
        {'name': 'quinoa', 'category': 'grains', 'alternative_names': ['quinoa grain']},
        
        # Fruits
        {'name': 'apple', 'category': 'fruits', 'alternative_names': ['apples', 'red apple', 'green apple']},
        {'name': 'banana', 'category': 'fruits', 'alternative_names': ['bananas', 'ripe banana']},
        {'name': 'lemon', 'category': 'fruits', 'alternative_names': ['lemons', 'fresh lemon']},
        {'name': 'lime', 'category': 'fruits', 'alternative_names': ['limes', 'fresh lime']},
        
        # Dairy
        {'name': 'cheese', 'category': 'dairy', 'alternative_names': ['cheddar cheese', 'mozzarella', 'parmesan']},
        {'name': 'milk', 'category': 'dairy', 'alternative_names': ['whole milk', '2% milk', 'skim milk']},
        {'name': 'butter', 'category': 'dairy', 'alternative_names': ['unsalted butter', 'salted butter']},
        {'name': 'yogurt', 'category': 'dairy', 'alternative_names': ['greek yogurt', 'plain yogurt']},
        
        # Herbs & Spices
        {'name': 'basil', 'category': 'herbs', 'alternative_names': ['fresh basil', 'basil leaves']},
        {'name': 'oregano', 'category': 'herbs', 'alternative_names': ['dried oregano', 'fresh oregano']},
        {'name': 'thyme', 'category': 'herbs', 'alternative_names': ['fresh thyme', 'dried thyme']},
        {'name': 'salt', 'category': 'seasonings', 'alternative_names': ['table salt', 'sea salt', 'kosher salt']},
        {'name': 'black pepper', 'category': 'seasonings', 'alternative_names': ['pepper', 'ground black pepper']},
        {'name': 'olive oil', 'category': 'oils', 'alternative_names': ['extra virgin olive oil', 'EVOO']},
    ]
    
    for ingredient_data in sample_ingredients:
        ingredient = Ingredient(
            name=ingredient_data['name'],
            category=ingredient_data['category'],
            alternative_names=ingredient_data.get('alternative_names', []),
            common_units=['cup', 'tablespoon', 'teaspoon', 'piece', 'gram']
        )
        db.session.add(ingredient)
    
    db.session.commit()

if __name__ == '__main__':
    init_database()