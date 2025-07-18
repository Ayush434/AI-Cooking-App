from flask import Blueprint, request, jsonify

recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('/detect-ingredients', methods=['POST'])
def detect_ingredients():
    # Placeholder: In real use, process image and call Google Vision API
    # For now, return dummy ingredients
    return jsonify({
        'ingredients': ['tomato', 'cheese', 'bread', 'lettuce']
    })

@recipes_bp.route('/get-recipes', methods=['POST'])
def get_recipes():
    data = request.get_json()
    ingredients = data.get('ingredients', [])
    # Placeholder: In real use, call Hugging Face API
    # For now, return dummy recipes
    return jsonify({
        'recipes': [
            {'title': 'Tomato Cheese Sandwich', 'ingredients': ingredients},
            {'title': 'Lettuce Salad', 'ingredients': ingredients}
        ]
    })