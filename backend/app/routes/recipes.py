from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from ..services.vision_service import VisionService
from ..services.recipe_service import RecipeService
from ..services.food_validation_service import FoodValidationService
from ..models.recipe import Recipe
from ..models.ingredient import Ingredient
from ..models.recipe_ingredient import RecipeIngredient
from ..models.user import User
from ..database import db

recipes_bp = Blueprint('recipes', __name__)

# Initialize services
recipe_service = RecipeService()
food_validation_service = FoodValidationService()

# Lazy initialization of vision service to avoid startup failures
_vision_service = None
def get_vision_service():
    global _vision_service
    if _vision_service is None:
        try:
            _vision_service = VisionService()
        except Exception as e:
            print(f"Warning: Vision service not available: {e}")
            return None
    return _vision_service

# Lazy initialization of nutrition service to avoid startup failures
def get_nutrition_service():
    try:
        from ..services.nutrition_service import NutritionService
        return NutritionService()
    except Exception as e:
        print(f"Warning: Nutrition service not available: {e}")
        return None

@recipes_bp.route('/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint
    """
    # Check service availability
    vision_service_available = get_vision_service() is not None
    nutrition_service_available = get_nutrition_service() is not None
    
    return jsonify({
        'status': 'healthy',
        'message': 'API is working correctly',
        'services': {
            'vision': vision_service_available,
            'recipe': True,
            'food_validation': True,
            'nutrition': nutrition_service_available
        },
        'endpoints': [
            '/api/recipes/health',
            '/api/recipes/detect-ingredients',
            '/api/recipes/get-recipes',
            '/api/recipes/validate-ingredient',
            '/api/recipes/validate-ingredients',
            '/api/recipes/autocomplete',
            '/api/recipes/search-ingredients',
            '/api/recipes/nutrition-facts'
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
        
        # Get vision service (lazy initialization)
        vision_service = get_vision_service()
        if not vision_service:
            return jsonify({
                'ingredients': ['tomato', 'onion', 'garlic'],
                'message': 'Vision service not available. Using fallback ingredients.'
            }), 200
        
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

def _get_or_create_ingredient(ingredient_name):
    """Get existing ingredient or create a new one"""
    ingredient_name = ingredient_name.strip().lower()
    ingredient = Ingredient.query.filter_by(name=ingredient_name).first()
    
    if not ingredient:
        ingredient = Ingredient(name=ingredient_name)
        db.session.add(ingredient)
        db.session.flush()  # Flush to get the ID
    
    return ingredient

def _extract_title_from_markdown(markdown_content):
    """Extract recipe title from markdown content"""
    if not markdown_content:
        return None
    
    lines = markdown_content.split('\n')
    
    for line in lines:
        trimmed = line.strip()
        if not trimmed:
            continue
        
        # Look for lines starting with # that contain recipe titles
        if trimmed.startswith('#') and len(trimmed) > 2:
            # Extract the title part (after #)
            title_part = trimmed.lstrip('#').strip()
            
            # Skip if it's just a section header
            if (title_part.lower() not in ['ingredients', 'instructions', 'tips', 'directions', 'steps'] and
                len(title_part) > 5 and
                ' ' in title_part):  # Contains spaces (likely a proper title)
                
                # Clean up the title
                title = title_part.replace('*', '').replace('#', '').strip()
                if title:
                    return title
    
    return None

def _save_recipe_to_db(recipe_data, user_id, original_ingredients, dietary_preferences, serving_size):
    """Save a recipe to the database with its ingredients"""
    try:
        # Extract recipe information
        title = recipe_data.get('title', 'Untitled Recipe')
        instructions = recipe_data.get('instructions', [])
        markdown_content = recipe_data.get('markdown_content', '')
        
        # Extract title from markdown if not found in recipe_data
        if (title == 'Untitled Recipe' or title == 'Generated Recipe') and markdown_content:
            extracted_title = _extract_title_from_markdown(markdown_content)
            if extracted_title:
                title = extracted_title
                print(f"Extracted title from markdown: {title}")
        
        # If we have markdown_content, use it as instructions (stored as JSON, can be string)
        if markdown_content:
            instructions = markdown_content
        # If instructions is a string, keep it as string (will be stored in JSON field)
        elif isinstance(instructions, str):
            instructions = instructions
        # If instructions is a list, join them with newlines
        elif isinstance(instructions, list):
            instructions = '\n'.join(str(step) for step in instructions if step)
        
        # Create recipe
        recipe = Recipe(
            title=title,
            description=recipe_data.get('description', ''),
            instructions=instructions,  # Store as string (JSON field can handle it)
            user_id=user_id,
            is_saved=False,  # Not explicitly saved, just requested
            original_ingredients=original_ingredients,
            serving_size=serving_size,
            dietary_tags=[dietary_preferences] if dietary_preferences else [],
            ai_model_used=recipe_data.get('ai_model_used', 'mistralai/Mixtral-8x7B-Instruct-v0.1'),  # Use AI model from recipe data, fallback to Mistral for backwards compatibility
            generation_prompt=f"Ingredients: {', '.join(original_ingredients)}",
            created_at=datetime.utcnow()
        )
        
        db.session.add(recipe)
        db.session.flush()  # Flush to get the recipe ID
        
        # Process ingredients from the recipe
        recipe_ingredients_list = recipe_data.get('ingredients', [])
        
        # If ingredients list is empty, use original ingredients as fallback
        if not recipe_ingredients_list or len(recipe_ingredients_list) == 0:
            print(f"Warning: No ingredients in recipe data, using original ingredients: {original_ingredients}")
            recipe_ingredients_list = original_ingredients if isinstance(original_ingredients, list) else []
        
        # If ingredients is a list of strings, process them
        if recipe_ingredients_list:
            for idx, ing in enumerate(recipe_ingredients_list):
                if not ing or (isinstance(ing, str) and not ing.strip()):
                    continue
                    
                if isinstance(ing, str):
                    # Parse ingredient string (e.g., "2 cups tomatoes" or just "tomatoes")
                    ingredient_name = ing.strip()
                    
                    # Skip if empty after stripping
                    if not ingredient_name:
                        continue
                    
                    # Try to extract quantity and unit if present
                    quantity = None
                    unit = None
                    
                    # Simple parsing: look for numbers at the start
                    parts = ingredient_name.split(' ', 2)
                    if len(parts) >= 2:
                        try:
                            quantity = float(parts[0])
                            unit = parts[1]
                            ingredient_name = parts[2] if len(parts) > 2 else parts[1]
                        except ValueError:
                            # First part is not a number, use full string as ingredient name
                            pass
                    
                    # Get or create ingredient
                    ingredient = _get_or_create_ingredient(ingredient_name)
                    
                    # Create recipe-ingredient relationship
                    recipe_ingredient = RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=ingredient.id,
                        quantity=quantity,
                        unit=unit,
                        order_index=idx
                    )
                    db.session.add(recipe_ingredient)
        else:
            print(f"Warning: No ingredients to process for recipe {recipe.id}")
        
        db.session.commit()
        return recipe
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving recipe to database: {str(e)}")
        raise

@recipes_bp.route('/get-recipes', methods=['POST'])
def get_recipes():
    """
    Generate recipes from ingredients using Hugging Face API
    Automatically saves recipes to database if user is logged in
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
        
        # Check if user is logged in - verify JWT token if present
        user_id = None
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header and auth_header.startswith('Bearer '):
            try:
                # Try to verify and get identity
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity()
                if user_id:
                    user_id = int(user_id)
                    print(f"User authenticated: user_id={user_id}")
                else:
                    print("No user_id found in token")
            except Exception as e:
                # Token is invalid - user is not logged in
                print(f"JWT verification failed: {str(e)}")
                user_id = None
        else:
            print("No Authorization header found - user not logged in")
            user_id = None
        
        # Generate recipes using Hugging Face API
        recipes = recipe_service.get_recipes_from_ingredients(
            ingredients, 
            dietary_preferences=dietary_preferences, 
            serving_size=serving_size
        )
        
        # If user is logged in, save recipes to database (limit to 10 most recent)
        saved_recipe_ids = []
        if user_id and recipes:
            print(f"Attempting to save {len(recipes)} recipes for user_id={user_id}")
            
            # Limit recipes to 10 per user - delete oldest if needed
            MAX_RECIPES_PER_USER = 10
            
            for idx, recipe_data in enumerate(recipes):
                try:
                    print(f"Saving recipe {idx+1}/{len(recipes)}: {recipe_data.get('title', 'Unknown')}")
                    saved_recipe = _save_recipe_to_db(
                        recipe_data, 
                        user_id, 
                        ingredients, 
                        dietary_preferences, 
                        serving_size
                    )
                    saved_recipe_ids.append(saved_recipe.id)
                    # Add recipe ID to response
                    recipe_data['id'] = saved_recipe.id
                    print(f"Successfully saved recipe with id={saved_recipe.id}")
                    
                    # After saving, check if we need to delete old recipes
                    total_recipes = Recipe.query.filter_by(user_id=user_id).count()
                    if total_recipes > MAX_RECIPES_PER_USER:
                        # Get oldest recipes (excluding favourites)
                        excess_count = total_recipes - MAX_RECIPES_PER_USER
                        old_recipes = Recipe.query.filter_by(
                            user_id=user_id,
                            is_saved=False  # Only delete non-favourite recipes
                        ).order_by(Recipe.created_at.asc()).limit(excess_count).all()
                        
                        for old_recipe in old_recipes:
                            print(f"Deleting old recipe (id={old_recipe.id}, title={old_recipe.title}) to maintain {MAX_RECIPES_PER_USER} recipe limit")
                            db.session.delete(old_recipe)
                        
                        db.session.commit()
                        print(f"Deleted {len(old_recipes)} old recipes to maintain limit")
                        
                except Exception as e:
                    import traceback
                    print(f"Failed to save recipe {idx+1} to database: {str(e)}")
                    print(traceback.format_exc())
                    # Continue even if saving fails
        else:
            if not user_id:
                print("User not logged in, skipping recipe save")
            if not recipes:
                print("No recipes to save")
        
        return jsonify({
            'recipes': recipes,
            'message': f'Generated {len(recipes)} recipes',
            'saved': len(saved_recipe_ids) > 0,
            'saved_ids': saved_recipe_ids if saved_recipe_ids else []
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

@recipes_bp.route('/nutrition-facts', methods=['POST'])
def get_nutrition_facts():
    """
    Get nutrition facts for a list of ingredients
    """
    try:
        data = request.get_json()
        if not data or 'ingredients' not in data:
            return jsonify({'error': 'No ingredients provided'}), 400
        
        ingredients = data.get('ingredients', [])
        serving_size = data.get('serving_size', 1)
        
        if not ingredients:
            return jsonify({'error': 'Empty ingredients list'}), 400
        
        # Validate ingredients before making API call
        valid_ingredients = [ingredient for ingredient in ingredients if ingredient and ingredient.strip()]
        
        if len(valid_ingredients) == 0:
            return jsonify({'error': 'No valid ingredients found for nutrition calculation'}), 400
        
        # Get nutrition facts from CalorieNinjas API
        nutrition_service = get_nutrition_service()
        if not nutrition_service:
            return jsonify({
                'error': 'Nutrition service not available',
                'message': 'Nutrition facts cannot be retrieved due to missing API key.'
            }), 503

        nutrition_data = nutrition_service.get_nutrition_facts(valid_ingredients, serving_size)
        
        return jsonify({
            'nutrition_data': nutrition_data,
            'message': f'Retrieved nutrition facts for {len(valid_ingredients)} ingredients'
        })
        
    except Exception as e:
        print(f"Error in get_nutrition_facts: {str(e)}")
        return jsonify({
            'error': 'Nutrition service error',
            'message': str(e)
        }), 500

@recipes_bp.route('/my-recipes', methods=['GET'])
@jwt_required()
def get_my_recipes():
    """
    Get all recipes (requested and saved) for the current user
    """
    try:
        user_id = get_jwt_identity()
        
        # Convert to int if needed
        user_id = int(user_id) if user_id else None
        
        if not user_id:
            return jsonify({'error': 'Invalid user ID'}), 400
        
        print(f"Fetching all recipes for user_id={user_id}")
        
        # Get all recipes for the user (both saved and requested)
        recipes = Recipe.query.filter_by(
            user_id=user_id
        ).order_by(Recipe.created_at.desc()).all()
        
        # Log recipe details
        saved_count = sum(1 for r in recipes if r.is_saved)
        requested_count = len(recipes) - saved_count
        print(f"Found {len(recipes)} total recipes: {saved_count} saved, {requested_count} requested")
        
        return jsonify({
            'recipes': [recipe.to_dict() for recipe in recipes],
            'count': len(recipes)
        }), 200
        
    except Exception as e:
        import traceback
        print(f"Error in get_my_recipes: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to retrieve recipes: {str(e)}'}), 500

@recipes_bp.route('/toggle-favourite', methods=['POST'])
@jwt_required()
def toggle_favourite():
    """
    Toggle favourite status of a recipe (favourite/unfavourite)
    Maximum 5 favourite recipes per user
    """
    try:
        user_id = get_jwt_identity()
        user_id = int(user_id) if user_id else None
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        recipe_id = data.get('recipe_id')
        if not recipe_id:
            return jsonify({'error': 'Recipe ID is required'}), 400
        
        # Find the recipe
        recipe = Recipe.query.filter_by(
            id=recipe_id,
            user_id=user_id
        ).first()
        
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404
        
        MAX_FAVOURITES = 5
        
        # Check if trying to favourite (not unfavourite)
        if not recipe.is_saved:
            # Count current favourites
            current_favourites = Recipe.query.filter_by(
                user_id=user_id,
                is_saved=True
            ).count()
            
            if current_favourites >= MAX_FAVOURITES:
                return jsonify({
                    'error': f'You can only have {MAX_FAVOURITES} favourite recipes. Please unfavourite one first.',
                    'max_favourites': MAX_FAVOURITES,
                    'current_count': current_favourites
                }), 400
        
        # Toggle favourite status
        recipe.is_saved = not recipe.is_saved
        db.session.commit()
        
        action = 'favourited' if recipe.is_saved else 'unfavourited'
        
        return jsonify({
            'message': f'Recipe {action} successfully',
            'recipe': recipe.to_dict(),
            'is_favourite': recipe.is_saved
        }), 200
        
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Error toggling favourite: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to toggle favourite: {str(e)}'}), 500

@recipes_bp.route('/saved-recipes', methods=['GET'])
@recipes_bp.route('/favourite-recipes', methods=['GET'])
@jwt_required()
def get_favourite_recipes():
    """
    Get all favourite recipes for the current user
    """
    try:
        user_id = get_jwt_identity()
        
        # Convert to int if needed
        user_id = int(user_id) if user_id else None
        
        # Get favourite recipes for the user
        recipes = Recipe.query.filter_by(
            user_id=user_id,
            is_saved=True
        ).order_by(Recipe.created_at.desc()).all()
        
        return jsonify({
            'recipes': [recipe.to_dict() for recipe in recipes],
            'count': len(recipes)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve favourite recipes: {str(e)}'}), 500

@recipes_bp.route('/saved-recipe/<int:recipe_id>', methods=['GET'])
@jwt_required()
def get_saved_recipe(recipe_id):
    """
    Get a specific saved recipe by ID
    """
    try:
        user_id = get_jwt_identity()
        
        # Convert to int if needed
        user_id = int(user_id) if user_id else None
        
        # Get the recipe
        recipe = Recipe.query.filter_by(
            id=recipe_id,
            user_id=user_id,
            is_saved=True
        ).first()
        
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404
        
        return jsonify({
            'recipe': recipe.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve recipe: {str(e)}'}), 500

@recipes_bp.route('/saved-recipe/<int:recipe_id>', methods=['DELETE'])
@jwt_required()
def delete_saved_recipe(recipe_id):
    """
    Delete a recipe (both saved and requested recipes can be deleted)
    """
    try:
        user_id = get_jwt_identity()
        
        # Convert to int if needed
        user_id = int(user_id) if user_id else None
        
        # Get the recipe - allow deleting any recipe belonging to the user
        recipe = Recipe.query.filter_by(
            id=recipe_id,
            user_id=user_id
        ).first()
        
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404
        
        db.session.delete(recipe)
        db.session.commit()
        
        return jsonify({
            'message': 'Recipe deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Error deleting recipe: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to delete recipe: {str(e)}'}), 500