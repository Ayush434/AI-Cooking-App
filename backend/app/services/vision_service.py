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

            # Filter for food-related ingredients
            food_keywords = [
                'food', 'vegetable', 'fruit', 'meat', 'dairy', 'grain', 'spice',
                'herb', 'nut', 'seed', 'tomato', 'onion', 'garlic', 'potato',
                'carrot', 'lettuce', 'spinach', 'broccoli', 'cauliflower',
                'bell pepper', 'cucumber', 'mushroom', 'eggplant', 'zucchini',
                'squash', 'corn', 'peas', 'beans', 'rice', 'pasta', 'bread',
                'cheese', 'milk', 'yogurt', 'butter', 'egg', 'chicken', 'beef',
                'pork', 'fish', 'shrimp', 'salmon', 'tuna', 'apple', 'banana',
                'orange', 'lemon', 'lime', 'strawberry', 'blueberry', 'grape',
                'peach', 'pear', 'plum', 'cherry', 'mango', 'pineapple',
                'coconut', 'avocado', 'olive', 'almond', 'walnut', 'peanut',
                'cashew', 'pistachio', 'sunflower seed', 'pumpkin seed',
                'flour', 'sugar', 'salt', 'pepper', 'oil', 'vinegar',
                'soy sauce', 'ketchup', 'mustard', 'mayonnaise'
            ]

            detected_ingredients = []
            for label in labels:
                label_text = label.description.lower()
                # Check if the label contains food-related keywords
                for keyword in food_keywords:
                    if keyword in label_text:
                        # Clean up the ingredient name
                        ingredient = label_text.replace('food', '').replace('vegetable', '').replace('fruit', '').strip()
                        if ingredient and len(ingredient) > 2:
                            detected_ingredients.append(ingredient)
                        break

            # Remove duplicates and return unique ingredients
            unique_ingredients = list(set(detected_ingredients))
            
            # Validate and correct ingredients using food validation service
            validated_ingredients = []
            validation_results = []
            
            for ingredient in unique_ingredients[:10]:  # Limit to 10 ingredients
                validation_result = self.food_validator.validate_ingredient(ingredient)
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