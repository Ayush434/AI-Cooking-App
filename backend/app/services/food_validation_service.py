import openfoodfacts
from fuzzywuzzy import fuzz, process
from typing import List, Dict, Tuple, Optional
import re

class FoodValidationService:
    def __init__(self):
        # Initialize Open Food Facts API with a user agent
        self.api = openfoodfacts.API(user_agent="AI-Cooking-App/1.0")
        
        # Common food categories and ingredients for validation
        self.food_categories = {
            'vegetables': [
                'tomato', 'onion', 'garlic', 'potato', 'carrot', 'lettuce', 'spinach',
                'broccoli', 'cauliflower', 'bell pepper', 'cucumber', 'mushroom',
                'eggplant', 'zucchini', 'squash', 'corn', 'peas', 'beans', 'celery',
                'kale', 'cabbage', 'radish', 'turnip', 'beet', 'asparagus', 'artichoke',
                'bok choy', 'napa cabbage', 'daikon', 'watercress', 'arugula', 'endive',
                'fennel', 'leek', 'shallot', 'scallion', 'green onion', 'chives',
                'parsnip', 'rutabaga', 'sweet potato', 'yam', 'pumpkin', 'butternut squash',
                'acorn squash', 'spaghetti squash', 'pattypan squash', 'chayote',
                'jicama', 'taro', 'cassava', 'plantain', 'okra', 'brussels sprouts',
                'collard greens', 'mustard greens', 'turnip greens', 'beet greens'
            ],
            'fruits': [
                'apple', 'banana', 'orange', 'lemon', 'lime', 'strawberry', 'blueberry',
                'grape', 'peach', 'pear', 'plum', 'cherry', 'mango', 'pineapple',
                'coconut', 'avocado', 'olive', 'kiwi', 'raspberry', 'blackberry',
                'cranberry', 'fig', 'date', 'prune', 'raisin', 'apricot', 'nectarine',
                'persimmon', 'pomegranate', 'guava', 'papaya', 'dragon fruit', 'lychee',
                'longan', 'rambutan', 'durian', 'jackfruit', 'breadfruit', 'soursop',
                'custard apple', 'sapodilla', 'star fruit', 'kumquat', 'calamondin',
                'yuzu', 'buddha hand', 'finger lime', 'blood orange', 'clementine',
                'tangerine', 'mandarin', 'satsuma', 'ugli fruit', 'tangelo'
            ],
            'meats': [
                'chicken', 'beef', 'pork', 'lamb', 'turkey', 'duck', 'fish', 'salmon',
                'tuna', 'shrimp', 'crab', 'lobster', 'bacon', 'ham', 'sausage',
                'steak', 'ground beef', 'pork chop', 'chicken breast', 'fish fillet',
                'cod', 'halibut', 'mackerel', 'sardine', 'anchovy', 'herring',
                'trout', 'bass', 'tilapia', 'catfish', 'swordfish', 'mahi mahi',
                'grouper', 'red snapper', 'sea bass', 'flounder', 'sole', 'perch',
                'pike', 'walleye', 'bluefish', 'marlin', 'sailfish', 'wahoo',
                'goose', 'quail', 'pheasant', 'partridge', 'guinea fowl', 'squab',
                'venison', 'bison', 'elk', 'moose', 'rabbit', 'goat', 'mutton',
                'veal', 'liver', 'kidney', 'heart', 'tongue', 'tripe', 'oxtail'
            ],
            'dairy': [
                'milk', 'cheese', 'yogurt', 'butter', 'cream', 'sour cream',
                'cottage cheese', 'cream cheese', 'mozzarella', 'cheddar',
                'parmesan', 'feta', 'ricotta', 'gouda', 'swiss', 'brie', 'camembert',
                'blue cheese', 'roquefort', 'stilton', 'gorgonzola', 'provolone',
                'asiago', 'pecorino', 'manchego', 'halloumi', 'paneer', 'tofu',
                'tempeh', 'soy milk', 'almond milk', 'oat milk', 'coconut milk',
                'cashew milk', 'rice milk', 'hemp milk', 'flax milk', 'quark',
                'kefir', 'buttermilk', 'heavy cream', 'half and half', 'whipping cream',
                'clotted cream', 'mascarpone', 'crème fraîche', 'labneh', 'skyr'
            ],
            'grains': [
                'rice', 'pasta', 'bread', 'flour', 'wheat', 'oats', 'quinoa',
                'barley', 'cornmeal', 'couscous', 'bulgur', 'millet', 'rye',
                'buckwheat', 'spelt', 'farro', 'amaranth', 'teff', 'sorghum',
                'job\'s tears', 'wild rice', 'black rice', 'red rice', 'brown rice',
                'jasmine rice', 'basmati rice', 'arborio rice', 'carnaroli rice',
                'vialone nano rice', 'bomba rice', 'calrose rice', 'sticky rice',
                'glutinous rice', 'sushi rice', 'risotto rice', 'paella rice',
                'forbidden rice', 'purple rice', 'japonica rice', 'indica rice'
            ],
            'nuts_seeds': [
                'almond', 'walnut', 'peanut', 'cashew', 'pistachio', 'pecan',
                'macadamia', 'hazelnut', 'sunflower seed', 'pumpkin seed',
                'chia seed', 'flax seed', 'sesame seed', 'pine nut', 'brazil nut',
                'pili nut', 'candlenut', 'kukui nut', 'tiger nut', 'water chestnut',
                'lotus seed', 'lotus root', 'taro root', 'arrowroot', 'sago',
                'tapioca', 'agar agar', 'carrageenan', 'xanthan gum', 'guar gum',
                'locust bean gum', 'psyllium husk', 'hemp seed', 'pumpkin seed',
                'watermelon seed', 'cantaloupe seed', 'apricot kernel', 'peach kernel'
            ],
            'herbs_spices': [
                'salt', 'pepper', 'basil', 'oregano', 'thyme', 'rosemary',
                'sage', 'parsley', 'cilantro', 'dill', 'mint', 'bay leaf',
                'cinnamon', 'nutmeg', 'ginger', 'turmeric', 'cumin', 'paprika',
                'chili powder', 'garlic powder', 'onion powder', 'cardamom',
                'cloves', 'allspice', 'star anise', 'fennel seed', 'caraway seed',
                'celery seed', 'mustard seed', 'poppy seed', 'nigella seed',
                'fenugreek', 'asafoetida', 'sumac', 'za\'atar', 'ras el hanout',
                'berbere', 'garam masala', 'curry powder', 'five spice powder',
                'seven spice powder', 'dukkah', 'furikake', 'shichimi togarashi'
            ],
            'oils_condiments': [
                'olive oil', 'vegetable oil', 'canola oil', 'coconut oil',
                'vinegar', 'soy sauce', 'ketchup', 'mustard', 'mayonnaise',
                'hot sauce', 'worcestershire sauce', 'fish sauce', 'sesame oil',
                'avocado oil', 'grapeseed oil', 'sunflower oil', 'safflower oil',
                'peanut oil', 'walnut oil', 'almond oil', 'hazelnut oil',
                'pumpkin seed oil', 'flaxseed oil', 'hemp oil', 'argan oil',
                'truffle oil', 'chili oil', 'garlic oil', 'onion oil', 'lemon oil',
                'lime oil', 'orange oil', 'bergamot oil', 'rose oil', 'lavender oil',
                'balsamic vinegar', 'apple cider vinegar', 'red wine vinegar',
                'white wine vinegar', 'rice vinegar', 'malt vinegar', 'sherry vinegar',
                'champagne vinegar', 'black vinegar', 'coconut vinegar', 'date vinegar'
            ],
            'legumes': [
                'lentil', 'chickpea', 'black bean', 'kidney bean', 'pinto bean',
                'navy bean', 'cannellini bean', 'lima bean', 'fava bean',
                'adzuki bean', 'mung bean', 'soybean', 'split pea', 'black eyed pea',
                'cowpea', 'pigeon pea', 'bambara groundnut', 'winged bean',
                'hyacinth bean', 'lablab bean', 'velvet bean', 'jack bean',
                'sword bean', 'rice bean', 'moth bean', 'urad dal', 'toor dal',
                'masoor dal', 'chana dal', 'moong dal', 'rajma', 'chole'
            ],
            'seaweed': [
                'nori', 'wakame', 'kombu', 'dulse', 'arame', 'hijiki',
                'sea lettuce', 'irish moss', 'bladderwrack', 'rockweed',
                'sea grapes', 'ogo', 'mozuku', 'tengusa', 'agar agar'
            ],
            'fungi': [
                'mushroom', 'shiitake', 'oyster mushroom', 'portobello',
                'cremini', 'button mushroom', 'enoki', 'maitake', 'reishi',
                'chaga', 'cordyceps', 'lion\'s mane', 'turkey tail', 'chicken of the woods',
                'morel', 'chanterelle', 'porcini', 'truffle', 'black truffle',
                'white truffle', 'summer truffle', 'winter truffle'
            ]
        }
        
        # Flatten all food items for easier searching
        self.all_food_items = []
        for category_items in self.food_categories.values():
            self.all_food_items.extend(category_items)

    def validate_ingredient(self, ingredient: str) -> Dict:
        """
        Validate if an ingredient is actually a food item and suggest corrections
        """
        ingredient = ingredient.lower().strip()
        
        # Handle edge cases
        if not ingredient or len(ingredient) < 2:
            return {
                'is_valid': False,
                'original': ingredient,
                'corrected': None,
                'confidence': 0.0,
                'suggestions': []
            }
        
        # Check for common typos first
        is_typo, correction = self.is_common_typo(ingredient)
        if is_typo:
            return {
                'is_valid': True,
                'original': ingredient,
                'corrected': correction,
                'confidence': 0.95,
                'suggestions': [],
                'source': 'typo_correction'
            }
        
        # First, try to find exact match in our food database
        if self._is_exact_food_match(ingredient):
            return {
                'is_valid': True,
                'original': ingredient,
                'corrected': ingredient,
                'confidence': 1.0,
                'suggestions': []
            }
        
        # Try fuzzy matching with our food database
        fuzzy_result = self._fuzzy_match_ingredient(ingredient)
        if fuzzy_result['is_valid']:
            return fuzzy_result
        
        # Try Open Food Facts API search (with stricter validation)
        of_result = self._search_openfoodfacts(ingredient)
        if of_result['is_valid']:
            return of_result
        
        # If no match found, return invalid with suggestions
        return {
            'is_valid': False,
            'original': ingredient,
            'corrected': None,
            'confidence': 0.0,
            'suggestions': self._get_suggestions(ingredient)
        }

    def validate_ingredients_list(self, ingredients: List[str]) -> List[Dict]:
        """
        Validate a list of ingredients and return validation results for each
        """
        results = []
        for ingredient in ingredients:
            result = self.validate_ingredient(ingredient)
            results.append(result)
        return results

    def _is_exact_food_match(self, ingredient: str) -> bool:
        """
        Check if ingredient exactly matches any known food item
        """
        return ingredient in self.all_food_items

    def _search_openfoodfacts(self, ingredient: str) -> Dict:
        """
        Search Open Food Facts API for the ingredient with stricter validation
        """
        try:
            # Skip very short or non-food-like terms
            if len(ingredient) < 3 or ingredient in ['a', 'an', 'the', 'and', 'or', 'but']:
                return {
                    'is_valid': False,
                    'original': ingredient,
                    'corrected': None,
                    'confidence': 0.0,
                    'suggestions': []
                }
            
            # Search for products containing this ingredient
            search_results = self.api.product.text_search(ingredient, page_size=10)
            
            if search_results and 'products' in search_results:
                products = search_results['products']
                if products:
                    # More strict validation: check if ingredient appears in food-related contexts
                    food_indicators = 0
                    total_products = min(len(products), 5)
                    
                    for product in products[:5]:
                        product_name = product.get('product_name', '').lower()
                        ingredients_text = product.get('ingredients_text', '').lower()
                        categories = product.get('categories_tags', [])
                        
                        # Check if this looks like a food product
                        is_food_product = any(cat in ['en:foods', 'en:ingredients'] for cat in categories)
                        
                        # Check if ingredient appears in food context
                        if ingredient in ingredients_text and is_food_product:
                            food_indicators += 1
                        elif ingredient in product_name and is_food_product:
                            food_indicators += 0.5
                    
                    # Require at least 2 food indicators to consider it valid
                    if food_indicators >= 2:
                        return {
                            'is_valid': True,
                            'original': ingredient,
                            'corrected': ingredient,
                            'confidence': min(0.8 + (food_indicators * 0.05), 0.95),
                            'suggestions': [],
                            'source': 'openfoodfacts'
                        }
            
            return {
                'is_valid': False,
                'original': ingredient,
                'corrected': None,
                'confidence': 0.0,
                'suggestions': []
            }
            
        except Exception as e:
            print(f"Error searching Open Food Facts: {str(e)}")
            return {
                'is_valid': False,
                'original': ingredient,
                'corrected': None,
                'confidence': 0.0,
                'suggestions': []
            }

    def _fuzzy_match_ingredient(self, ingredient: str) -> Dict:
        """
        Use fuzzy matching to find similar food items
        """
        try:
            # Use fuzzywuzzy to find the best matches
            matches = process.extract(ingredient, self.all_food_items, limit=5, scorer=fuzz.ratio)
            
            # Filter matches with high confidence (80% or higher)
            high_confidence_matches = [match for match in matches if match[1] >= 80]
            
            if high_confidence_matches:
                best_match = high_confidence_matches[0]
                return {
                    'is_valid': True,
                    'original': ingredient,
                    'corrected': best_match[0],
                    'confidence': best_match[1] / 100.0,
                    'suggestions': [match[0] for match in high_confidence_matches[1:3]],
                    'source': 'fuzzy_match'
                }
            
            return {
                'is_valid': False,
                'original': ingredient,
                'corrected': None,
                'confidence': 0.0,
                'suggestions': [match[0] for match in matches[:3]]
            }
            
        except Exception as e:
            print(f"Error in fuzzy matching: {str(e)}")
            return {
                'is_valid': False,
                'original': ingredient,
                'corrected': None,
                'confidence': 0.0,
                'suggestions': []
            }

    def _get_suggestions(self, ingredient: str) -> List[str]:
        """
        Get suggestions for similar food items
        """
        try:
            # Use fuzzy matching to get suggestions
            matches = process.extract(ingredient, self.all_food_items, limit=5, scorer=fuzz.ratio)
            return [match[0] for match in matches[:3]]
        except:
            return []

    def get_food_category(self, ingredient: str) -> Optional[str]:
        """
        Get the food category for a given ingredient
        """
        ingredient = ingredient.lower().strip()
        
        for category, items in self.food_categories.items():
            if ingredient in items:
                return category
        
        return None

    def is_common_typo(self, ingredient: str) -> Tuple[bool, Optional[str]]:
        """
        Check if the ingredient is a common typo and return the correction
        """
        common_typos = {
            'appel': 'apple',
            'bananna': 'banana',
            'tomatos': 'tomato',
            'onions': 'onion',
            'garlics': 'garlic',
            'potatos': 'potato',
            'carrots': 'carrot',
            'lettuces': 'lettuce',
            'spinaches': 'spinach',
            'broccolis': 'broccoli',
            'cauliflowers': 'cauliflower',
            'cucumbers': 'cucumber',
            'mushrooms': 'mushroom',
            'eggplants': 'eggplant',
            'zucchinis': 'zucchini',
            'squashes': 'squash',
            'corns': 'corn',
            'peas': 'pea',
            'beans': 'bean',
            'rices': 'rice',
            'pastas': 'pasta',
            'breads': 'bread',
            'flours': 'flour',
            'sugars': 'sugar',
            'salts': 'salt',
            'peppers': 'pepper',
            'oils': 'oil',
            'vinegars': 'vinegar',
            'cheeses': 'cheese',
            'milks': 'milk',
            'yogurts': 'yogurt',
            'butters': 'butter',
            'eggs': 'egg',
            'chickens': 'chicken',
            'beefs': 'beef',
            'porks': 'pork',
            'fishes': 'fish',
            'shrimps': 'shrimp',
            'salmons': 'salmon',
            'tunas': 'tuna',
            'oranges': 'orange',
            'lemons': 'lemon',
            'limes': 'lime',
            'strawberries': 'strawberry',
            'blueberries': 'blueberry',
            'grapes': 'grape',
            'peaches': 'peach',
            'pears': 'pear',
            'plums': 'plum',
            'cherries': 'cherry',
            'mangos': 'mango',
            'pineapples': 'pineapple',
            'coconuts': 'coconut',
            'avocados': 'avocado',
            'olives': 'olive',
            'almonds': 'almond',
            'walnuts': 'walnut',
            'peanuts': 'peanut',
            'cashews': 'cashew',
            'pistachios': 'pistachio'
        }
        
        if ingredient in common_typos:
            return True, common_typos[ingredient]
        
        return False, None

    def autocomplete_ingredients(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Get ingredient suggestions for autocompletion using Open Food Facts
        """
        try:
            if not query or len(query) < 2:
                return []
            
            # First, try local database for fast results
            local_suggestions = []
            query_lower = query.lower()
            
            for category, items in self.food_categories.items():
                for item in items:
                    if query_lower in item.lower():
                        local_suggestions.append({
                            'name': item,
                            'category': category,
                            'source': 'local',
                            'confidence': 1.0
                        })
            
            # Sort local suggestions by relevance
            local_suggestions.sort(key=lambda x: x['name'].lower().find(query_lower))
            
            # If we have enough local suggestions, return them
            if len(local_suggestions) >= limit:
                return local_suggestions[:limit]
            
            # Otherwise, search Open Food Facts for more suggestions
            try:
                search_results = self.api.product.text_search(query, page_size=20)
                
                if search_results and 'products' in search_results:
                    products = search_results['products']
                    of_suggestions = []
                    
                    for product in products[:10]:  # Limit to 10 products
                        product_name = product.get('product_name', '').lower()
                        ingredients_text = product.get('ingredients_text', '').lower()
                        categories = product.get('categories_tags', [])
                        
                        # Check if this is a food product
                        is_food = any(cat in ['en:foods', 'en:ingredients', 'en:snacks', 'en:beverages'] for cat in categories)
                        
                        if is_food:
                            # Extract ingredient names from product name or ingredients
                            potential_ingredients = []
                            
                            # Check product name
                            if query_lower in product_name:
                                # Extract the matching part
                                words = product_name.split()
                                for word in words:
                                    if query_lower in word.lower() and len(word) > 2:
                                        potential_ingredients.append(word.lower())
                            
                            # Check ingredients text
                            if query_lower in ingredients_text:
                                # Extract ingredients containing the query
                                ingredients = ingredients_text.split(',')
                                for ingredient in ingredients:
                                    if query_lower in ingredient.lower():
                                        # Clean up the ingredient
                                        clean_ingredient = ingredient.strip().lower()
                                        if len(clean_ingredient) > 2:
                                            potential_ingredients.append(clean_ingredient)
                            
                            # Add unique ingredients
                            for ingredient in potential_ingredients:
                                if ingredient not in [s['name'] for s in of_suggestions]:
                                    of_suggestions.append({
                                        'name': ingredient,
                                        'category': 'unknown',
                                        'source': 'openfoodfacts',
                                        'confidence': 0.8
                                    })
                    
                    # Combine local and Open Food Facts suggestions
                    all_suggestions = local_suggestions + of_suggestions
                    
                    # Remove duplicates and sort by confidence
                    seen = set()
                    unique_suggestions = []
                    for suggestion in all_suggestions:
                        if suggestion['name'] not in seen:
                            seen.add(suggestion['name'])
                            unique_suggestions.append(suggestion)
                    
                    # Sort by confidence and relevance
                    unique_suggestions.sort(key=lambda x: (x['confidence'], x['name'].lower().find(query_lower)))
                    
                    return unique_suggestions[:limit]
                
            except Exception as e:
                print(f"Error searching Open Food Facts for autocomplete: {str(e)}")
            
            # Return local suggestions if Open Food Facts fails
            return local_suggestions[:limit]
            
        except Exception as e:
            print(f"Error in autocomplete_ingredients: {str(e)}")
            return []

    def search_ingredients(self, query: str, limit: int = 15) -> List[Dict]:
        """
        Search for ingredients with more detailed information
        """
        try:
            if not query or len(query) < 2:
                return []
            
            results = []
            query_lower = query.lower()
            
            # Search local database
            for category, items in self.food_categories.items():
                for item in items:
                    if query_lower in item.lower():
                        results.append({
                            'name': item,
                            'category': category,
                            'source': 'local',
                            'confidence': 1.0,
                            'description': f'{item} ({category})'
                        })
            
            # Search Open Food Facts for additional results
            try:
                search_results = self.api.product.text_search(query, page_size=30)
                
                if search_results and 'products' in search_results:
                    products = search_results['products']
                    
                    for product in products[:20]:
                        product_name = product.get('product_name', '')
                        ingredients_text = product.get('ingredients_text', '')
                        categories = product.get('categories_tags', [])
                        brands = product.get('brands', '')
                        
                        # Check if this is a food product
                        is_food = any(cat in ['en:foods', 'en:ingredients', 'en:snacks', 'en:beverages'] for cat in categories)
                        
                        if is_food and product_name:
                            # Extract ingredient-like terms from product name
                            words = product_name.lower().split()
                            for word in words:
                                if (query_lower in word and len(word) > 2 and 
                                    word not in [r['name'] for r in results]):
                                    
                                    # Determine category from product categories
                                    category = 'unknown'
                                    if any('dairy' in cat.lower() for cat in categories):
                                        category = 'dairy'
                                    elif any('meat' in cat.lower() for cat in categories):
                                        category = 'meats'
                                    elif any('vegetable' in cat.lower() for cat in categories):
                                        category = 'vegetables'
                                    elif any('fruit' in cat.lower() for cat in categories):
                                        category = 'fruits'
                                    elif any('grain' in cat.lower() for cat in categories):
                                        category = 'grains'
                                    
                                    results.append({
                                        'name': word,
                                        'category': category,
                                        'source': 'openfoodfacts',
                                        'confidence': 0.7,
                                        'description': f'{word} (found in {product_name})'
                                    })
                                    
                                    if len(results) >= limit:
                                        break
                        
                        if len(results) >= limit:
                            break
                
            except Exception as e:
                print(f"Error searching Open Food Facts: {str(e)}")
            
            # Sort by confidence and relevance
            results.sort(key=lambda x: (x['confidence'], x['name'].lower().find(query_lower)))
            
            return results[:limit]
            
        except Exception as e:
            print(f"Error in search_ingredients: {str(e)}")
            return [] 