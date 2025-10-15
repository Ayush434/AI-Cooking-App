import re
from datetime import datetime, timedelta
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from ..database import db
from ..models.user import User

class AuthService:
    """Service class for handling user authentication operations"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        return True, "Password is valid"
    
    @staticmethod
    def validate_username(username):
        """Validate username format"""
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 20:
            return False, "Username must be less than 20 characters long"
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        
        return True, "Username is valid"
    
    @staticmethod
    def register_user(email, username, password):
        """Register a new user"""
        try:
            # Validate input
            if not AuthService.validate_email(email):
                return False, "Invalid email format", None
            
            is_valid, message = AuthService.validate_password(password)
            if not is_valid:
                return False, message, None
            
            is_valid, message = AuthService.validate_username(username)
            if not is_valid:
                return False, message, None
            
            # Check if user already exists
            if User.query.filter_by(email=email).first():
                return False, "Email already registered", None
            
            if User.query.filter_by(username=username).first():
                return False, "Username already taken", None
            
            # Create new user
            user = User(
                email=email,
                username=username
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return True, "User registered successfully", user
            
        except Exception as e:
            db.session.rollback()
            return False, f"Registration failed: {str(e)}", None
    
    @staticmethod
    def authenticate_user(email_or_username, password):
        """Authenticate user with email/username and password"""
        try:
            # Find user by email or username
            user = User.query.filter(
                (User.email == email_or_username) | (User.username == email_or_username)
            ).first()
            
            if not user:
                return False, "Invalid credentials", None
            
            if not user.check_password(password):
                return False, "Invalid credentials", None
            
            return True, "Authentication successful", user
            
        except Exception as e:
            return False, f"Authentication failed: {str(e)}", None
    
    @staticmethod
    def create_tokens(user):
        """Create access and refresh tokens for user"""
        try:
            access_token = create_access_token(
                identity=user.id,
                expires_delta=timedelta(hours=1)
            )
            refresh_token = create_refresh_token(
                identity=user.id,
                expires_delta=timedelta(days=7)
            )
            
            return True, "Tokens created successfully", {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict_safe()
            }
            
        except Exception as e:
            return False, f"Token creation failed: {str(e)}"
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found", None
            
            return True, "User found", user
            
        except Exception as e:
            return False, f"Failed to get user: {str(e)}", None
    
    @staticmethod
    def update_user_profile(user_id, **kwargs):
        """Update user profile information"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found", None
            
            # Update allowed fields
            allowed_fields = ['username', 'email', 'dietary_preferences', 'allergies', 'favorite_cuisines']
            
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(user, field):
                    # Check for username/email uniqueness
                    if field == 'username' and value != user.username:
                        if User.query.filter_by(username=value).first():
                            return False, "Username already taken", None
                    elif field == 'email' and value != user.email:
                        if not AuthService.validate_email(value):
                            return False, "Invalid email format", None
                        if User.query.filter_by(email=value).first():
                            return False, "Email already registered", None
                    
                    setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return True, "Profile updated successfully", user
            
        except Exception as e:
            db.session.rollback()
            return False, f"Profile update failed: {str(e)}", None
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """Change user password"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found", None
            
            # Verify current password
            if not user.check_password(current_password):
                return False, "Current password is incorrect", None
            
            # Validate new password
            is_valid, message = AuthService.validate_password(new_password)
            if not is_valid:
                return False, message, None
            
            # Set new password
            user.set_password(new_password)
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return True, "Password changed successfully", user
            
        except Exception as e:
            db.session.rollback()
            return False, f"Password change failed: {str(e)}", None
