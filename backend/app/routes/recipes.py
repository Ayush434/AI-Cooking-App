from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from ..services.vision_service import VisionService
from ..services.recipe_service import RecipeService

recipes_bp = Blueprint('recipes', __name__)

# Initialize services
vision_service = VisionService()
recipe_service = RecipeService()

@recipes_bp.route('/detect-ingredients', methods=['POST'])
def detect_ingredients():
    """
    Detect ingredients from uploaded image using Google Vision API
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Detect ingredients using Google Vision API
        detected_ingredients = vision_service.detect_ingredients_from_image(image_file)
        
        return jsonify({
            'ingredients': detected_ingredients,
            'message': f'Detected {len(detected_ingredients)} ingredients'
        })
        
    except Exception as e:
        print(f"Error in detect_ingredients: {str(e)}")
        return jsonify({
            'ingredients': ['tomato', 'onion', 'garlic'],
            'message': 'Using fallback ingredients due to API error'
        })

@recipes_bp.route('/get-recipes', methods=['POST'])
def get_recipes():
    """
    Generate recipes from ingredients using Hugging Face API
    """
    try:
        data = request.get_json()
        if not data or 'ingredients' not in data:
            return jsonify({'error': 'No ingredients provided'}), 400
        
        ingredients = data.get('ingredients', [])
        if not ingredients:
            return jsonify({'error': 'Empty ingredients list'}), 400
        
        # Generate recipes using Hugging Face API
        recipes = recipe_service.get_recipes_from_ingredients(ingredients)
        
        return jsonify({
            'recipes': recipes,
            'message': f'Generated {len(recipes)} recipes'
        })
        
    except Exception as e:
        print(f"Error in get_recipes: {str(e)}")
        return jsonify({
            'recipes': [
                {
                    'title': 'Fallback Recipe',
                    'ingredients': ingredients if 'ingredients' in locals() else ['tomato', 'onion'],
                    'instructions': 'This is a fallback recipe due to API error.'
                }
            ],
            'message': 'Using fallback recipes due to API error'
        })