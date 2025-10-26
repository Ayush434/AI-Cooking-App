from datetime import datetime
from ..database import db

class Recipe(db.Model):
    """Recipe model for storing generated and saved recipes"""
    
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Recipe content stored as JSON (from AI generation)
    instructions = db.Column(db.JSON, nullable=False)  # List of instruction steps
    
    # Recipe metadata
    prep_time = db.Column(db.Integer)  # minutes
    cook_time = db.Column(db.Integer)  # minutes
    total_time = db.Column(db.Integer)  # minutes
    serving_size = db.Column(db.Integer, default=1)
    difficulty_level = db.Column(db.String(20))  # 'easy', 'medium', 'hard'
    cuisine_type = db.Column(db.String(50))  # 'italian', 'asian', etc.
    
    # Dietary information
    dietary_tags = db.Column(db.JSON, default=list)  # ['vegetarian', 'gluten-free', etc.]
    
    # User interaction
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # null for anonymous users
    rating = db.Column(db.Float)  # User rating 1-5
    notes = db.Column(db.Text)  # User notes about the recipe
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_made = db.Column(db.DateTime)  # When user last made this recipe
    times_made = db.Column(db.Integer, default=0)  # How many times user made this
    
    # AI generation metadata
    ai_model_used = db.Column(db.String(50))  # Which AI model generated this
    generation_prompt = db.Column(db.Text)  # Original prompt used
    
    # Recipe source and status
    is_saved = db.Column(db.Boolean, default=False)  # True if user saved this recipe
    original_ingredients = db.Column(db.JSON)  # Store original ingredients used to generate recipe
    
    # Relationships
    recipe_ingredients = db.relationship('RecipeIngredient', back_populates='recipe', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Recipe {self.title}>'
    
    def to_dict(self, include_ingredients=True):
        """Convert recipe object to dictionary"""
        recipe_dict = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'instructions': self.instructions or [],
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'total_time': self.total_time,
            'serving_size': self.serving_size,
            'difficulty_level': self.difficulty_level,
            'cuisine_type': self.cuisine_type,
            'dietary_tags': self.dietary_tags or [],
            'user_id': self.user_id,
            'rating': self.rating,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_made': self.last_made.isoformat() if self.last_made else None,
            'times_made': self.times_made,
            'ai_model_used': self.ai_model_used,
            'generation_prompt': self.generation_prompt,
            'is_saved': self.is_saved,
            'original_ingredients': self.original_ingredients or []
        }
        
        if include_ingredients:
            recipe_dict['ingredients'] = [ri.to_dict() for ri in self.recipe_ingredients]
        
        return recipe_dict