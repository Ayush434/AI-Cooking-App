from datetime import datetime
from ..database import db

class Ingredient(db.Model):
    """Ingredient model for storing ingredient information"""
    
    __tablename__ = 'ingredients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50))  # 'vegetables', 'fruits', 'proteins', etc.
    
    # Nutritional information (per 100g) stored as JSON
    nutrition_data = db.Column(db.JSON)  # {'calories': 20, 'protein': 1.5, 'carbs': 4.0, etc.}
    
    # Common units and conversions
    common_units = db.Column(db.JSON, default=list)  # ['cup', 'tbsp', 'piece', etc.]
    
    # Validation and matching data
    alternative_names = db.Column(db.JSON, default=list)  # ['tomato', 'tomatoe', 'roma tomato']
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recipe_ingredients = db.relationship('RecipeIngredient', back_populates='ingredient')
    
    def __repr__(self):
        return f'<Ingredient {self.name}>'
    
    def to_dict(self):
        """Convert ingredient object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'nutrition_data': self.nutrition_data or {},
            'common_units': self.common_units or [],
            'alternative_names': self.alternative_names or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }