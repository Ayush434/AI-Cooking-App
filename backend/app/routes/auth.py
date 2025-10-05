from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from ..services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not all([email, username, password]):
            return jsonify({'error': 'Email, username, and password are required'}), 400
        
        success, message, user = AuthService.register_user(email, username, password)
        
        if success:
            # Create tokens for the new user
            token_success, token_message, token_data = AuthService.create_tokens(user)
            
            if token_success:
                return jsonify({
                    'message': message,
                    'tokens': token_data
                }), 201
            else:
                return jsonify({
                    'message': message,
                    'error': token_message
                }), 201
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user with email/username and password"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email_or_username = data.get('email_or_username', '').strip()
        password = data.get('password', '')
        
        if not all([email_or_username, password]):
            return jsonify({'error': 'Email/username and password are required'}), 400
        
        success, message, user = AuthService.authenticate_user(email_or_username, password)
        
        if success:
            # Create tokens for the user
            token_success, token_message, token_data = AuthService.create_tokens(user)
            
            if token_success:
                return jsonify({
                    'message': message,
                    'tokens': token_data
                }), 200
            else:
                return jsonify({'error': token_message}), 500
        else:
            return jsonify({'error': message}), 401
            
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token"""
    try:
        user_id = get_jwt_identity()
        success, message, user = AuthService.get_user_by_id(user_id)
        
        if success:
            new_access_token = create_access_token(identity=user_id)
            return jsonify({
                'access_token': new_access_token,
                'user': user.to_dict_safe()
            }), 200
        else:
            return jsonify({'error': message}), 401
            
    except Exception as e:
        return jsonify({'error': f'Token refresh failed: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user's profile"""
    try:
        user_id = get_jwt_identity()
        success, message, user = AuthService.get_user_by_id(user_id)
        
        if success:
            return jsonify({
                'user': user.to_dict_safe()
            }), 200
        else:
            return jsonify({'error': message}), 404
            
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user's profile"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract allowed fields for update
        update_data = {}
        allowed_fields = ['dietary_preferences', 'allergies', 'favorite_cuisines']
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        success, message, user = AuthService.update_user_profile(user_id, **update_data)
        
        if success:
            return jsonify({
                'message': message,
                'user': user.to_dict_safe()
            }), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': f'Profile update failed: {str(e)}'}), 500

@auth_bp.route('/validate', methods=['POST'])
def validate_credentials():
    """Validate email, username, or password format"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        validation_type = data.get('type')
        value = data.get('value', '').strip()
        
        if not validation_type or not value:
            return jsonify({'error': 'Type and value are required'}), 400
        
        if validation_type == 'email':
            is_valid = AuthService.validate_email(value)
            message = "Valid email" if is_valid else "Invalid email format"
        elif validation_type == 'username':
            is_valid, message = AuthService.validate_username(value)
        elif validation_type == 'password':
            is_valid, message = AuthService.validate_password(value)
        else:
            return jsonify({'error': 'Invalid validation type'}), 400
        
        return jsonify({
            'valid': is_valid,
            'message': message
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Validation failed: {str(e)}'}), 500
