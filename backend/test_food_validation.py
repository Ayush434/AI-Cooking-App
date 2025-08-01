#!/usr/bin/env python3
"""
Test script for the Food Validation Service
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.food_validation_service import FoodValidationService

def test_food_validation():
    """Test the food validation service with various inputs"""
    
    print("Initializing Food Validation Service...")
    validator = FoodValidationService()
    
    # Test cases
    test_cases = [
        # Valid ingredients
        "tomato",
        "apple",
        "chicken",
        "rice",
        "salt",
        
        # Common typos
        "appel",  # should suggest "apple"
        "bananna",  # should suggest "banana"
        "tomatos",  # should suggest "tomato"
        
        # Invalid items (non-food)
        "computer",
        "book",
        "car",
        "phone",
        
        # Edge cases
        "",
        "   ",
        "a",
        "123",
        
        # Mixed case
        "ToMaTo",
        "APPLE",
        "ChIcKeN"
    ]
    
    print("\n" + "="*60)
    print("FOOD VALIDATION TEST RESULTS")
    print("="*60)
    
    for test_input in test_cases:
        print(f"\nTesting: '{test_input}'")
        try:
            result = validator.validate_ingredient(test_input)
            
            print(f"  Valid: {result['is_valid']}")
            print(f"  Original: '{result['original']}'")
            print(f"  Corrected: '{result['corrected']}'")
            print(f"  Confidence: {result['confidence']:.2f}")
            
            if result['suggestions']:
                print(f"  Suggestions: {result['suggestions']}")
            
            if 'source' in result:
                print(f"  Source: {result['source']}")
                
        except Exception as e:
            print(f"  ERROR: {str(e)}")
    
    # Test common typo detection
    print("\n" + "="*60)
    print("COMMON TYPO DETECTION TEST")
    print("="*60)
    
    typo_tests = ["appel", "bananna", "tomatos", "onions", "garlics"]
    
    for typo in typo_tests:
        is_typo, correction = validator.is_common_typo(typo)
        print(f"'{typo}' -> is_typo: {is_typo}, correction: '{correction}'")
    
    # Test food category detection
    print("\n" + "="*60)
    print("FOOD CATEGORY DETECTION TEST")
    print("="*60)
    
    category_tests = ["tomato", "apple", "chicken", "milk", "rice", "almond", "basil", "olive oil"]
    
    for food in category_tests:
        category = validator.get_food_category(food)
        print(f"'{food}' -> category: {category}")
    
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60)

if __name__ == "__main__":
    test_food_validation() 