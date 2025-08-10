from datetime import datetime
from ..database import db

class User(db.Model):
    """User model for storing user information and preferences"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # User preferences stored as JSON
    dietary_preferences = db.Column(db.JSON, default=list)  # ['vegetarian', 'gluten-free', etc.]
    allergies = db.Column(db.JSON, default=list)  # ['nuts', 'dairy', etc.]
    favorite_cuisines = db.Column(db.JSON, default=list)  # ['italian', 'asian', etc.]
    
    # Relationships
    recipes = db.relationship('Recipe', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'dietary_preferences': self.dietary_preferences or [],
            'allergies': self.allergies or [],
            'favorite_cuisines': self.favorite_cuisines or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }