from datetime import datetime
import bcrypt
from ..database import db

class User(db.Model):
    """User model for storing user information and preferences"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
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
    
    def set_password(self, password):
        """Hash and set the user's password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if the provided password matches the stored hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
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
    
    def to_dict_safe(self):
        """Convert user object to dictionary without sensitive information"""
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