from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from ..services.vision_service import VisionService
from ..services.recipe_service import RecipeService
from ..services.food_validation_service import FoodValidationService

recipes_bp = Blueprint('recipes', __name__)

# Initialize services
vision_service = VisionService()
recipe_service = RecipeService()
food_validation_service = FoodValidationService()

@recipes_bp.route('/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'message': 'API is working correctly',
        'endpoints': [
            '/api/recipes/health',
            '/api/recipes/detect-ingredients',
            '/api/recipes/get-recipes',
            '/api/recipes/validate-ingredient',
            '/api/recipes/validate-ingredients',
            '/api/recipes/autocomplete',
            '/api/recipes/search-ingredients'
        ]
    })

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
        
        # Get optional parameters
        dietary_preferences = data.get('dietary_preferences', '')
        serving_size = data.get('serving_size', 1)
        
        # Generate recipes using Hugging Face API
        recipes = recipe_service.get_recipes_from_ingredients(
            ingredients, 
            dietary_preferences=dietary_preferences, 
            serving_size=serving_size
        )
        
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
                    'instructions': f'This is a fallback recipe due to API error. Recipe for {serving_size if "serving_size" in locals() else 1} {"person" if (serving_size if "serving_size" in locals() else 1) == 1 else "people"}.'
                }
            ],
            'message': 'Using fallback recipes due to API error'
        })

@recipes_bp.route('/validate-ingredient', methods=['POST'])
def validate_ingredient():
    """
    Validate a single ingredient and suggest corrections
    """
    try:
        data = request.get_json()
        if not data or 'ingredient' not in data:
            return jsonify({'error': 'No ingredient provided'}), 400
        
        ingredient = data.get('ingredient', '').strip()
        if not ingredient:
            return jsonify({'error': 'Empty ingredient'}), 400
        
        # Validate the ingredient
        validation_result = food_validation_service.validate_ingredient(ingredient)
        
        return jsonify({
            'validation_result': validation_result,
            'message': 'Ingredient validation completed'
        })
        
    except Exception as e:
        print(f"Error in validate_ingredient: {str(e)}")
        return jsonify({
            'error': 'Validation service error',
            'message': str(e)
        }), 500

@recipes_bp.route('/validate-ingredients', methods=['POST'])
def validate_ingredients():
    """
    Validate a list of ingredients and suggest corrections
    """
    try:
        data = request.get_json()
        if not data or 'ingredients' not in data:
            return jsonify({'error': 'No ingredients provided'}), 400
        
        ingredients = data.get('ingredients', [])
        if not ingredients:
            return jsonify({'error': 'Empty ingredients list'}), 400
        
        # Validate all ingredients
        validation_results = food_validation_service.validate_ingredients_list(ingredients)
        
        # Separate valid and invalid ingredients
        valid_ingredients = []
        invalid_ingredients = []
        suggestions = {}
        
        for result in validation_results:
            if result['is_valid']:
                valid_ingredients.append(result['corrected'])
            else:
                invalid_ingredients.append(result['original'])
                if result['suggestions']:
                    suggestions[result['original']] = result['suggestions']
        
        return jsonify({
            'validation_results': validation_results,
            'valid_ingredients': valid_ingredients,
            'invalid_ingredients': invalid_ingredients,
            'suggestions': suggestions,
            'message': f'Validated {len(ingredients)} ingredients'
        })
        
    except Exception as e:
        print(f"Error in validate_ingredients: {str(e)}")
        return jsonify({
            'error': 'Validation service error',
            'message': str(e)
        }), 500

@recipes_bp.route('/autocomplete', methods=['GET'])
def autocomplete_ingredients():
    """
    Get ingredient suggestions for autocompletion
    """
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({'suggestions': []})
        
        # Get autocomplete suggestions
        suggestions = food_validation_service.autocomplete_ingredients(query, limit)
        
        return jsonify({
            'suggestions': suggestions,
            'query': query,
            'count': len(suggestions)
        })
        
    except Exception as e:
        print(f"Error in autocomplete_ingredients: {str(e)}")
        return jsonify({
            'error': 'Autocomplete service error',
            'message': str(e)
        }), 500

@recipes_bp.route('/search-ingredients', methods=['GET'])
def search_ingredients():
    """
    Search for ingredients with detailed information
    """
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 15))
        
        if not query:
            return jsonify({'results': []})
        
        # Search for ingredients
        results = food_validation_service.search_ingredients(query, limit)
        
        return jsonify({
            'results': results,
            'query': query,
            'count': len(results)
        })
        
    except Exception as e:
        print(f"Error in search_ingredients: {str(e)}")
        return jsonify({
            'error': 'Search service error',
            'message': str(e)
        }), 500