import requests
import os
from ..config import Config

class NutritionService:
    """Service for fetching nutrition information from CalorieNinjas API"""
    
    def __init__(self):
        self.api_key = Config.CALORIE_NINJAS_API_KEY
        self.base_url = Config.CALORIE_NINJAS_BASE_URL
        
        if not self.api_key:
            raise ValueError("CALORIE_NINJAS_API_KEY environment variable is required")
    
    def get_nutrition_facts(self, ingredients, serving_size=1):
        """
        Get nutrition facts for a list of ingredients
        
        Args:
            ingredients (list): List of ingredient names
            serving_size (int): Number of servings
            
        Returns:
            dict: Nutrition data from CalorieNinjas API
        """
        try:
            # Format ingredients for the API query - use more realistic portions
            query = self._format_ingredients_query(ingredients, serving_size)
            
            print(f"Nutrition API Query: {query}")
            
            # Make API request
            response = requests.get(
                f"{self.base_url}?query={query}",
                headers={'X-Api-Key': self.api_key}
            )
            
            if not response.ok:
                print(f"Nutrition API Error: {response.status_code} - {response.text}")
                raise Exception(f"API error: {response.status_code} - {response.text}")
            
            data = response.json()
            print(f"Nutrition API Response: {data}")
            
            if not data.get('items') or len(data['items']) == 0:
                raise Exception('No nutrition data found for the ingredients')
            
            # Validate that we have the required nutrition fields
            valid_items = self._validate_nutrition_data(data['items'])
            
            if len(valid_items) == 0:
                raise Exception('Nutrition data is incomplete or invalid')
            
            return {
                'items': valid_items,
                'query': query,
                'serving_size': serving_size
            }
            
        except Exception as e:
            print(f"Nutrition service error: {str(e)}")
            raise e
    
    def _format_ingredients_query(self, ingredients, serving_size):
        """Format ingredients into a query string with realistic portions"""
        formatted_ingredients = []
        
        for ingredient in ingredients:
            if not ingredient or not ingredient.strip():
                continue
                
            # For AI-generated recipe ingredients, use more natural portion formatting
            # Let CalorieNinjas API handle the portion calculations more intelligently
            ingredient_lower = ingredient.lower()
            
            # Check if ingredient already has a quantity specified
            if any(char.isdigit() for char in ingredient):
                # Ingredient already has quantity, use as-is
                formatted_ingredients.append(ingredient.strip())
            else:
                # Use serving-size adjusted portions for common ingredients
                if any(word in ingredient_lower for word in ['chicken', 'beef', 'meat', 'pork', 'lamb', 'turkey']):
                    portion = f"{round(serving_size * 150)}g"
                elif any(word in ingredient_lower for word in ['rice', 'pasta', 'potato', 'bread', 'noodles']):
                    portion = f"{round(serving_size * 80)}g"
                elif any(word in ingredient_lower for word in ['vegetable', 'tomato', 'onion', 'carrot', 'broccoli', 'spinach']):
                    portion = f"{round(serving_size * 50)}g"
                elif any(word in ingredient_lower for word in ['oil', 'butter', 'olive oil', 'coconut oil']):
                    portion = f"{round(serving_size * 15)}g"
                elif any(word in ingredient_lower for word in ['egg', 'eggs']):
                    portion = f"{round(serving_size * 60)}g"
                elif any(word in ingredient_lower for word in ['milk', 'cheese', 'yogurt']):
                    portion = f"{round(serving_size * 120)}g"
                else:
                    portion = f"{round(serving_size * 100)}g"
                
                formatted_ingredients.append(f"{portion} {ingredient.strip()}")
        
        return " and ".join(formatted_ingredients)
    
    def _validate_nutrition_data(self, items):
        """Validate that nutrition items have required fields"""
        required_fields = ['calories', 'protein_g', 'carbohydrates_total_g', 'fat_total_g']
        
        valid_items = []
        for item in items:
            if all(field in item and item[field] is not None for field in required_fields):
                valid_items.append(item)
        
        return valid_items
