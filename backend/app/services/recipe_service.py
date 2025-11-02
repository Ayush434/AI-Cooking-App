import os
import json
import sys
from typing import List
from openai import OpenAI

# Optional import for Gemini AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai package not installed. Gemini AI will not be available.", flush=True)

class RecipeService:
    def __init__(self):
        # Get Gemini API key from environment variable
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.gemini_model = None
        self.gemini_model_name = None  # Store the actual model name that worked
        if not GEMINI_AVAILABLE:
            print("Warning: google-generativeai package not installed. Gemini AI will not be available.", flush=True)
        elif not self.gemini_api_key:
            print("Warning: GEMINI_API_KEY not set. Will use Mistral as fallback.", flush=True)
        else:
            # Initialize Gemini client
            try:
                genai.configure(api_key=self.gemini_api_key)
                # Try to list available models first to see what's available
                try:
                    models = genai.list_models()
                    available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
                    # Extract just the model name part (remove 'models/' prefix if present)
                    available_models_clean = [m.split('/')[-1] if '/' in m else m for m in available_models[:10]]
                except Exception:
                    available_models_clean = []
                
                # Prioritize free-tier friendly models (avoid experimental models)
                preferred_models = [
                    'gemini-2.5-flash-lite',  # Best free tier limits (1K RPD)
                    'gemini-2.5-flash',      # Good free tier limits (250 RPD)
                    'gemini-2.0-flash',      # Good free tier limits (200 RPD)
                    'gemini-2.5-pro',        # Lower limits but still free tier (50 RPD)
                    'gemini-1.5-flash',      # Older but still available
                    'gemini-1.5-pro'         # Older but still available
                ]
                
                # Filter available models to exclude experimental (-exp) versions
                if available_models_clean:
                    non_exp_models = [m for m in available_models_clean if '-exp' not in m.lower() and 'experimental' not in m.lower()]
                    # Prioritize preferred models that are in the available list
                    model_names_to_try = []
                    for pref in preferred_models:
                        if pref in non_exp_models:
                            model_names_to_try.append(pref)
                    # Add other available non-experimental models
                    for model in non_exp_models:
                        if model not in model_names_to_try:
                            model_names_to_try.append(model)
                    # Limit to top 5 from available
                    model_names_to_try = model_names_to_try[:5]
                else:
                    model_names_to_try = preferred_models
                
                # Add preferred models that weren't in available list (in case listing failed)
                for pref in preferred_models:
                    if pref not in model_names_to_try:
                        model_names_to_try.append(pref)
                
                # Remove duplicates while preserving order
                model_names_to_try = list(dict.fromkeys(model_names_to_try))
                
                self.gemini_model = None
                for model_name in model_names_to_try:
                    try:
                        self.gemini_model = genai.GenerativeModel(model_name)
                        self.gemini_model_name = model_name  # Store the working model name
                        print(f"[GEMINI] Initialized - Using {model_name}", flush=True)
                        break
                    except Exception:
                        continue
                
                if not self.gemini_model:
                    raise Exception("Could not initialize any Gemini model")
                    
            except Exception as e:
                print(f"[GEMINI] Not available - Will use Mistral", flush=True)
                self.gemini_model = None
                self.gemini_model_name = None
        
        # Get Hugging Face API token from environment variable (for Mistral fallback)
        self.hf_token = os.getenv('HF_ACCESS_TOKEN')
        if self.hf_token:
            print(f"[MISTRAL] Initialized - Ready as fallback", flush=True)
        
        # Initialize OpenAI client for Together AI router (Mistral fallback)
        self.mistral_client = OpenAI(
            base_url="https://router.huggingface.co/together/v1",
            api_key=self.hf_token,
        ) if self.hf_token else None

    def get_recipes_from_ingredients(self, ingredients: List[str], dietary_preferences: str = '', serving_size: int = 1, use_gemini: bool = False) -> List[dict]:
        """
        Generate recipes from a list of ingredients.
        Default uses Mistral AI. Gemini AI is only used if use_gemini=True (requires logged-in user).
        """
        print(f"🔧 RecipeService.get_recipes_from_ingredients called - use_gemini: {use_gemini}, gemini_available: {self.gemini_model is not None}, mistral_available: {self.mistral_client is not None}", flush=True)
        
        # Only try Gemini if explicitly requested (and user is logged in - checked in route)
        if use_gemini:
            if not self.gemini_api_key:
                print(f"[GEMINI] ✗ Not available - API key not configured", flush=True)
            elif not self.gemini_model:
                print(f"[GEMINI] ✗ Not available - Model not initialized", flush=True)
            else:
                try:
                    print(f"[GEMINI] User opted in - Using Gemini AI", flush=True)
                    result = self._get_recipes_with_gemini(ingredients, dietary_preferences, serving_size)
                    # Check if result is successful (not an error)
                    if result and len(result) > 0 and not result[0].get('is_error', False):
                        print(f"[GEMINI] ✓ Success - Recipe generated", flush=True)
                        return result
                    else:
                        raise Exception("Gemini returned error response")
                except Exception as e:
                    error_msg = str(e)
                    if "quota" in error_msg.lower() or "429" in error_msg:
                        print(f"[GEMINI] ✗ Quota exceeded, falling back to Mistral...", flush=True)
                    else:
                        print(f"[GEMINI] ✗ Failed: {error_msg[:100]}", flush=True)
                    # Fall through to Mistral fallback
        
        # Default to Mistral AI (or fallback if Gemini failed)
        if self.hf_token and self.mistral_client:
            try:
                if use_gemini:
                    print(f"[MISTRAL] Fallback - Using Mistral AI", flush=True)
                else:
                    print(f"[MISTRAL] Default - Using Mistral AI", flush=True)
                result = self._get_recipes_with_mistral(ingredients, dietary_preferences, serving_size)
                # Check if result is successful (not an error)
                if result and len(result) > 0 and not result[0].get('is_error', False):
                    print(f"[MISTRAL] ✓ Success - Recipe generated", flush=True)
                    return result
                else:
                    raise Exception("Mistral returned error response")
            except Exception as e:
                print(f"[MISTRAL] ✗ Failed: {str(e)[:100]}", flush=True)
                return self._get_api_error_response(f"Both AI services failed. Please try again later.")
        else:
            return self._get_api_error_response("No AI service configured.")

    def _get_recipes_with_gemini(self, ingredients: List[str], dietary_preferences: str = '', serving_size: int = 1) -> List[dict]:
        """
        Generate recipes using Gemini AI
        """
        ingredients_string = ", ".join(ingredients)
        
        # Build dietary preferences text
        dietary_text = ""
        if dietary_preferences and dietary_preferences.strip():
            dietary_text = f"\n\nDietary Requirements/Preferences: {dietary_preferences.strip()}"
        
        # Build serving size text
        serving_text = f"\n\nServing Size: This recipe should serve {serving_size} {'person' if serving_size == 1 else 'people'}."
        
        # Create the prompt for recipe generation
        prompt = f"""You are a helpful cooking assistant. Given the following ingredients, create a delicious and practical recipe.

Ingredients: {ingredients_string}{dietary_text}{serving_text}

Please provide a recipe in **Markdown format** with the following structure:

# [Recipe Name]

## Ingredients
- [ingredient 1 with quantity adjusted for {serving_size} {'person' if serving_size == 1 else 'people'}]
- [ingredient 2 with quantity adjusted for {serving_size} {'person' if serving_size == 1 else 'people'}]
- [continue for all ingredients...]

## Instructions
1. [First step with clear details]
2. [Second step with clear details]
3. [Continue with numbered steps...]

## Tips
- [Any helpful cooking tips or variations]

Make sure the recipe is:
- Easy to follow with clear step-by-step instructions
- Uses the provided ingredients as the main components
- Includes reasonable quantities and cooking times adjusted for {serving_size} {'person' if serving_size == 1 else 'people'}
- Safe and practical for home cooking{' and follows the dietary preferences specified' if dietary_preferences else ''}
- **Formatted in proper Markdown with headers, lists, and clear structure**"""

        # Generate content with Gemini
        response = self.gemini_model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.7,
                'max_output_tokens': 3000,
            }
        )
        
        # Extract the generated recipe text
        generated_text = response.text
        
        # Validate that the recipe is complete before parsing
        if not self._is_recipe_complete(generated_text):
            print("[GEMINI] Warning: Recipe appears incomplete", flush=True)
        
        # Parse the generated recipe (Gemini uses same format as Mistral)
        model_name = self.gemini_model_name or 'gemini-1.5-flash'  # Use stored model name or default
        parsed_result = self._parse_recipe(generated_text, ingredients, model_name)
        return parsed_result

    def _get_recipes_with_mistral(self, ingredients: List[str], dietary_preferences: str = '', serving_size: int = 1) -> List[dict]:
        """
        Generate recipes using Mistral AI (fallback method)
        """
        ingredients_string = ", ".join(ingredients)
        
        # Build dietary preferences text
        dietary_text = ""
        if dietary_preferences and dietary_preferences.strip():
            dietary_text = f"\n\nDietary Requirements/Preferences: {dietary_preferences.strip()}"
        
        # Build serving size text
        serving_text = f"\n\nServing Size: This recipe should serve {serving_size} {'person' if serving_size == 1 else 'people'}."
        
        # Create the prompt for recipe generation
        prompt = f"""You are a helpful cooking assistant. Given the following ingredients, create a delicious and practical recipe.

Ingredients: {ingredients_string}{dietary_text}{serving_text}

Please provide a recipe in **Markdown format** with the following structure:

# [Recipe Name]

## Ingredients
- [ingredient 1 with quantity adjusted for {serving_size} {'person' if serving_size == 1 else 'people'}]
- [ingredient 2 with quantity adjusted for {serving_size} {'person' if serving_size == 1 else 'people'}]
- [continue for all ingredients...]

## Instructions
1. [First step with clear details]
2. [Second step with clear details]
3. [Continue with numbered steps...]

## Tips
- [Any helpful cooking tips or variations]

Make sure the recipe is:
- Easy to follow with clear step-by-step instructions
- Uses the provided ingredients as the main components
- Includes reasonable quantities and cooking times adjusted for {serving_size} {'person' if serving_size == 1 else 'people'}
- Safe and practical for home cooking{' and follows the dietary preferences specified' if dietary_preferences else ''}
- **Formatted in proper Markdown with headers, lists, and clear structure**"""

        completion = self.mistral_client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=3000,
            temperature=0.7
        )

        # Extract the generated recipe text
        generated_text = completion.choices[0].message.content
        
        # Validate that the recipe is complete before parsing
        if not self._is_recipe_complete(generated_text):
            print("[MISTRAL] Warning: Recipe appears incomplete", flush=True)
        
        # Parse the generated recipe
        parsed_result = self._parse_recipe(generated_text, ingredients, 'mistralai/Mixtral-8x7B-Instruct-v0.1')
        return parsed_result

    def _is_recipe_complete(self, recipe_text: str) -> bool:
        """
        Check if the generated recipe appears to be complete
        """
        if not recipe_text or len(recipe_text.strip()) < 100:
            return False
        
        # Check for essential sections in markdown format
        has_title = '#' in recipe_text
        has_ingredients = '## Ingredients' in recipe_text or '## ingredients' in recipe_text
        has_instructions = '## Instructions' in recipe_text or '## instructions' in recipe_text
        
        # Check if there are numbered steps in instructions
        has_numbered_steps = any(f"{i}." in recipe_text for i in range(1, 6))
        
        # Check if the text ends abruptly (incomplete generation)
        ends_properly = not recipe_text.strip().endswith(('...', 'Ingred', 'Instru', '#'))
        
        return has_title and has_ingredients and has_instructions and has_numbered_steps and ends_properly

    def _parse_recipe(self, recipe_text: str, original_ingredients: List[str], model_used: str) -> List[dict]:
        """
        Parse the AI-generated recipe text into structured format
        Works for both Gemini and Mistral outputs
        """
        try:
            print(f"Parsing recipe text from {model_used}: {recipe_text}")
            
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
                
                # Check for title in markdown format (# Title)
                if line.startswith('# ') and title == "Generated Recipe":
                    title_part = line[2:].strip()  # Remove '# ' prefix
                    # Make sure it's not a section header
                    if (title_part.lower() not in ['ingredients', 'instructions', 'tips', 'directions', 'steps'] and
                        len(title_part) > 5 and ' ' in title_part):
                        title = title_part.replace('*', '').replace('#', '').strip()
                        continue
                
                # Check for title in old format (title: ...)
                if line.lower().startswith('title:'):
                    title = line.split(':', 1)[1].strip()
                    if title.startswith('[') and title.endswith(']'):
                        title = title[1:-1]  # Remove brackets
                
                # Check for ingredients section (## Ingredients or ## ingredients)
                elif line.lower().startswith('## ingredients'):
                    current_section = 'ingredients'
                    # Extract ingredients from the same line if present
                    ingredients_text = line.split(':', 1)[1].strip() if ':' in line else ""
                    if ingredients_text:
                        ingredients.extend(self._parse_ingredients_text(ingredients_text))
                
                # Check for instructions section (## Instructions or ## instructions)
                elif line.lower().startswith('## instructions'):
                    current_section = 'instructions'
                    # Extract instructions from the same line if present
                    instructions_text = line.split(':', 1)[1].strip() if ':' in line else ""
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
                'instructions': instructions,
                'markdown_content': recipe_text,  # Store full markdown content for frontend
                'ai_model_used': model_used  # Track which AI model generated this
            }]

        except Exception as e:
            print(f"Error parsing recipe from {model_used}: {str(e)}")
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
