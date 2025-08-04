import os
from google.cloud import vision
import io
from .food_validation_service import FoodValidationService

class VisionService:
    def __init__(self):
        # Set the Google Cloud credentials
        credentials_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'capstone-ai-cooking-app-5692391a2963.json'
        )
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        self.client = vision.ImageAnnotatorClient()
        
        # Initialize food validation service
        self.food_validator = FoodValidationService()

    def detect_ingredients_from_image(self, image_file):
        """
        Detect ingredients from an uploaded image using Google Vision API
        """
        try:
            # Read the image file
            content = image_file.read()
            image = vision.Image(content=content)

            # Perform label detection
            response = self.client.label_detection(image=image)
            labels = response.label_annotations

            # Extract all detected labels without hardcoded filtering
            detected_ingredients = []
            for label in labels:
                label_text = label.description.lower().strip()
                # Only filter out very short or non-descriptive labels
                if len(label_text) > 2 and label_text not in ['food', 'vegetable', 'fruit', 'ingredient']:
                    detected_ingredients.append(label_text)

            # Remove duplicates and return unique ingredients
            unique_ingredients = list(set(detected_ingredients))
            
            # Validate and correct ingredients using food validation service (which uses Open Food Facts API)
            validated_ingredients = []
            validation_results = []
            
            for ingredient in unique_ingredients[:15]:  # Increased limit to get more candidates
                validation_result = self.food_validator.validate_ingredient(ingredient, prioritize_api=True)
                validation_results.append(validation_result)
                
                if validation_result['is_valid']:
                    validated_ingredients.append(validation_result['corrected'])
                else:
                    # If not valid, try to use the best suggestion
                    if validation_result['suggestions']:
                        validated_ingredients.append(validation_result['suggestions'][0])
                    else:
                        # Keep the original if no suggestions available
                        validated_ingredients.append(ingredient)
            
            # If no ingredients detected, return some common ones as fallback
            if not validated_ingredients:
                validated_ingredients = ['tomato', 'onion', 'garlic']

            return validated_ingredients

        except Exception as e:
            print(f"Error detecting ingredients: {str(e)}")
            return ['tomato', 'onion', 'garlic']  # Fallback ingredients