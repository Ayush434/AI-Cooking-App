#!/usr/bin/env python3
"""
Test script for the Enhanced Food Validation Service
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.food_validation_service import FoodValidationService

def test_enhanced_validation():
    """Test the enhanced food validation service with diverse ingredients"""
    
    print("Initializing Enhanced Food Validation Service...")
    validator = FoodValidationService()
    
    # Test cases for diverse ingredients
    test_cases = [
        # Asian ingredients
        "tofu", "paneer", "tempeh", "miso", "natto", "kimchi", "gochujang",
        "sriracha", "fish sauce", "oyster sauce", "hoisin sauce", "teriyaki",
        "wasabi", "nori", "wakame", "kombu", "dashi", "mirin", "sake",
        "udon", "soba", "ramen", "pho", "pad thai", "curry", "masala",
        
        # Middle Eastern ingredients
        "hummus", "falafel", "tahini", "za'atar", "sumac", "harissa",
        "labneh", "feta", "halloumi", "pita", "naan", "flatbread",
        
        # Latin American ingredients
        "quinoa", "amaranto", "chayote", "jicama", "nopales", "tomatillo",
        "achiote", "annatto", "epazote", "hoja santa", "achiote",
        
        # African ingredients
        "teff", "sorghum", "millet", "fonio", "amaranth", "bambara groundnut",
        "cassava", "taro", "yam", "plantain", "okra", "bitter leaf",
        
        # European ingredients
        "roquefort", "gorgonzola", "stilton", "camembert", "brie",
        "provolone", "asiago", "pecorino", "manchego", "halloumi",
        
        # Modern ingredients
        "seitan", "nutritional yeast", "agar agar", "xanthan gum",
        "psyllium husk", "spirulina", "chlorella", "moringa",
        
        # Common typos and variations
        "toffu", "paneer", "tempe", "miso soup", "kimchee", "siracha",
        "fishsauce", "oystersauce", "teriyaki sauce", "wasabi paste",
        
        # Invalid items (should be marked as not food)
        "computer", "book", "car", "phone", "table", "chair"
    ]
    
    print("\n" + "="*80)
    print("ENHANCED FOOD VALIDATION TEST RESULTS")
    print("="*80)
    
    valid_count = 0
    invalid_count = 0
    
    for test_input in test_cases:
        print(f"\nTesting: '{test_input}'")
        try:
            result = validator.validate_ingredient(test_input)
            
            status = "✓ VALID" if result['is_valid'] else "✗ INVALID"
            print(f"  Status: {status}")
            print(f"  Original: '{result['original']}'")
            print(f"  Corrected: '{result['corrected']}'")
            print(f"  Confidence: {result['confidence']:.2f}")
            
            if result['suggestions']:
                print(f"  Suggestions: {result['suggestions']}")
            
            if 'source' in result:
                print(f"  Source: {result['source']}")
            
            if result['is_valid']:
                valid_count += 1
            else:
                invalid_count += 1
                
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            invalid_count += 1
    
    print(f"\n" + "="*80)
    print(f"SUMMARY: {valid_count} valid, {invalid_count} invalid")
    print("="*80)
    
    # Test autocomplete functionality
    print("\n" + "="*80)
    print("AUTOCOMPLETE TEST")
    print("="*80)
    
    autocomplete_tests = ["tof", "pan", "tem", "mis", "cur", "che", "ric"]
    
    for query in autocomplete_tests:
        print(f"\nAutocomplete for '{query}':")
        try:
            suggestions = validator.autocomplete_ingredients(query, limit=5)
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion['name']} ({suggestion['category']}) - {suggestion['source']}")
        except Exception as e:
            print(f"  ERROR: {str(e)}")
    
    # Test search functionality
    print("\n" + "="*80)
    print("SEARCH TEST")
    print("="*80)
    
    search_tests = ["tofu", "paneer", "curry", "cheese"]
    
    for query in search_tests:
        print(f"\nSearch for '{query}':")
        try:
            results = validator.search_ingredients(query, limit=3)
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['name']} ({result['category']}) - {result['description']}")
        except Exception as e:
            print(f"  ERROR: {str(e)}")
    
    print("\n" + "="*80)
    print("ENHANCED TEST COMPLETED")
    print("="*80)

if __name__ == "__main__":
    test_enhanced_validation() 