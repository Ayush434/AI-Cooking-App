import os
import requests
import json
from typing import List

class RecipeService:
    def __init__(self):
        # Get Hugging Face API token from environment variable
        self.hf_token = os.getenv('HF_ACCESS_TOKEN')
        if not self.hf_token:
            print("Warning: HF_ACCESS_TOKEN not set. Recipe generation will use fallback.")
        
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
        self.headers = {"Authorization": f"Bearer {self.hf_token}"} if self.hf_token else {}

    def get_recipes_from_ingredients(self, ingredients: List[str]) -> List[dict]:
        """
        Generate recipes from a list of ingredients using Hugging Face API
        """
        try:
            if not self.hf_token:
                return self._get_fallback_recipes(ingredients)

            ingredients_string = ", ".join(ingredients)
            
            system_prompt = """
            You are an assistant that receives a list of ingredients that a user has and suggests a recipe they could make with some or all of those ingredients. You don't need to use every ingredient they mention in your recipe. The recipe can include additional ingredients they didn't mention, but try not to include too many extra ingredients. Format your response in markdown to make it easier to render to a web page.
            """

            payload = {
                "inputs": f"{system_prompt} I have {ingredients_string}. Please give me a recipe you'd recommend I make!",
                "parameters": {
                    "max_new_tokens": 1024,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "do_sample": True
                }
            }

            response = requests.post(self.api_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    recipe_text = result[0].get('generated_text', '')
                    # Parse the recipe text and extract title and ingredients
                    return self._parse_recipe_response(recipe_text, ingredients)
                else:
                    return self._get_fallback_recipes(ingredients)
            else:
                print(f"API Error: {response.status_code}")
                return self._get_fallback_recipes(ingredients)

        except Exception as e:
            print(f"Error generating recipes: {str(e)}")
            return self._get_fallback_recipes(ingredients)

    def _parse_recipe_response(self, recipe_text: str, original_ingredients: List[str]) -> List[dict]:
        """
        Parse the AI-generated recipe text into structured format
        """
        try:
            # Simple parsing - extract title and ingredients
            lines = recipe_text.split('\n')
            title = "AI Generated Recipe"
            ingredients = original_ingredients.copy()
            
            # Try to extract a title from the response
            for line in lines:
                if line.strip().startswith('#') or line.strip().startswith('**'):
                    title = line.strip().replace('#', '').replace('*', '').strip()
                    break
                elif line.strip() and not line.strip().startswith('-') and not line.strip().startswith('*'):
                    title = line.strip()
                    break

            return [{
                'title': title,
                'ingredients': ingredients,
                'instructions': recipe_text[:500] + "..." if len(recipe_text) > 500 else recipe_text
            }]

        except Exception as e:
            print(f"Error parsing recipe: {str(e)}")
            return self._get_fallback_recipes(original_ingredients)

    def _get_fallback_recipes(self, ingredients: List[str]) -> List[dict]:
        """
        Return fallback recipes when API is not available
        """
        ingredient_str = ", ".join(ingredients[:5])  # Use first 5 ingredients
        
        fallback_recipes = [
            {
                'title': f'Delicious {ingredients[0].title()} Recipe',
                'ingredients': ingredients,
                'instructions': f'Create a wonderful dish using {ingredient_str}. This is a simple and tasty recipe that you can customize based on your preferences.'
            },
            {
                'title': f'Quick {ingredients[1].title()} Meal',
                'ingredients': ingredients,
                'instructions': f'Make a quick and healthy meal with {ingredient_str}. Perfect for busy weeknights!'
            }
        ]
        
        return fallback_recipes