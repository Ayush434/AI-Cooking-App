import os
import json
from typing import List
from openai import OpenAI

class RecipeService:
    def __init__(self):
        # Get Hugging Face API token from environment variable
        self.hf_token = os.getenv('HF_ACCESS_TOKEN')
        if not self.hf_token:
            print("Warning: HF_ACCESS_TOKEN not set. Recipe generation will fail.")
        
        # Initialize OpenAI client for Together AI router
        self.client = OpenAI(
            base_url="https://router.huggingface.co/together/v1",
            api_key=self.hf_token,
        ) if self.hf_token else None

    def get_recipes_from_ingredients(self, ingredients: List[str]) -> List[dict]:
        """
        Generate recipes from a list of ingredients using Mistral model via Together AI
        """
        try:
            # If no token, return error
            if not self.hf_token or not self.client:
                print("No HF_ACCESS_TOKEN found")
                return self._get_api_error_response("Hugging Face API token not configured")

            ingredients_string = ", ".join(ingredients)
            
            # Create the prompt for recipe generation
            prompt = f"""You are a helpful cooking assistant. Given the following ingredients, create a delicious and practical recipe.

Ingredients: {ingredients_string}

Please provide a recipe with the following format:
Title: [Recipe Name]
Ingredients: [List of ingredients with quantities]
Instructions: [Step-by-step cooking instructions]

Make sure the recipe is:
- Easy to follow
- Uses the provided ingredients as the main components
- Includes reasonable quantities and cooking times
- Safe and practical for home cooking"""

            print(f"Calling Mistral API with token: {self.hf_token[:10]}...")
            print(f"Input ingredients: {ingredients_string}")
            
            completion = self.client.chat.completions.create(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )

            print(f"API Response received successfully")
            
            # Extract the generated recipe text
            generated_text = completion.choices[0].message.content
            print(f"Generated recipe text: {generated_text}")
            
            # Parse the generated recipe
            return self._parse_mistral_recipe(generated_text, ingredients)

        except Exception as e:
            print(f"Error generating recipes: {str(e)}")
            return self._get_api_error_response(f"Error: {str(e)}")

    def _parse_mistral_recipe(self, recipe_text: str, original_ingredients: List[str]) -> List[dict]:
        """
        Parse the Mistral-generated recipe text into structured format
        """
        try:
            print(f"Parsing recipe text: {recipe_text}")
            
            # Initialize default values
            title = "Generated Recipe"
            ingredients = []
            instructions = ""
            
            # Split the text into lines and parse
            lines = recipe_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for title
                if line.lower().startswith('title:'):
                    title = line.split(':', 1)[1].strip()
                    if title.startswith('[') and title.endswith(']'):
                        title = title[1:-1]  # Remove brackets
                
                # Check for ingredients section
                elif line.lower().startswith('ingredients:'):
                    current_section = 'ingredients'
                    # Extract ingredients from the same line if present
                    ingredients_text = line.split(':', 1)[1].strip()
                    if ingredients_text:
                        ingredients.extend(self._parse_ingredients_text(ingredients_text))
                
                # Check for instructions section
                elif line.lower().startswith('instructions:'):
                    current_section = 'instructions'
                    # Extract instructions from the same line if present
                    instructions_text = line.split(':', 1)[1].strip()
                    if instructions_text:
                        instructions = instructions_text
                
                # Continue parsing based on current section
                elif current_section == 'ingredients':
                    ingredients.extend(self._parse_ingredients_text(line))
                
                elif current_section == 'instructions':
                    if instructions:
                        instructions += "\n" + line
                    else:
                        instructions = line
            
            # If no ingredients were parsed, use original ingredients
            if not ingredients:
                ingredients = original_ingredients
            
            # If no instructions, provide a default message
            if not instructions:
                instructions = "Recipe instructions not available."
            
            return [{
                'title': title,
                'ingredients': ingredients,
                'instructions': instructions
            }]

        except Exception as e:
            print(f"Error parsing Mistral recipe: {str(e)}")
            return self._get_api_error_response("Error parsing recipe response")

    def _parse_ingredients_text(self, text: str) -> List[str]:
        """
        Parse ingredients from text, handling various formats
        """
        ingredients = []
        
        # Remove common prefixes and clean up
        text = text.strip()
        if text.startswith('-') or text.startswith('•') or text.startswith('*'):
            text = text[1:].strip()
        
        # If text contains multiple ingredients (separated by commas, semicolons, etc.)
        if ',' in text or ';' in text:
            # Split by common separators
            parts = text.replace(';', ',').split(',')
            for part in parts:
                part = part.strip()
                if part and not part.startswith('[') and not part.endswith(']'):
                    ingredients.append(part)
        else:
            # Single ingredient
            if text and not text.startswith('[') and not text.endswith(']'):
                ingredients.append(text)
        
        return [ing for ing in ingredients if ing]

    def _get_api_error_response(self, error_message: str) -> List[dict]:
        """
        Return an error response instead of fallback recipes
        """
        return [{
            'title': 'API Error',
            'ingredients': [],
            'instructions': f"Sorry, the recipe generation service is currently unavailable. {error_message}. Please try again later or contact support if the issue persists.",
            'is_error': True
        }]