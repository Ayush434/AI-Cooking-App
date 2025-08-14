import React, { useState, useEffect } from 'react';
import './NutritionFacts.css';
import config from '../config';

function NutritionFacts({ ingredients, servingSize, isVisible, onClose, onLoadingChange }) {
  const [nutritionData, setNutritionData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Update parent component with loading state
  useEffect(() => {
    if (onLoadingChange) {
      onLoadingChange(loading);
    }
  }, [loading, onLoadingChange]);

  // Fetch nutrition data when component becomes visible
  useEffect(() => {
    if (isVisible && ingredients && ingredients.length > 0 && !nutritionData) {
      // Validate ingredients before making API call
      const validIngredients = ingredients.filter(ingredient => 
        ingredient && ingredient.trim().length > 0
      );
      
      if (validIngredients.length === 0) {
        setError('No valid ingredients found for nutrition calculation');
        return;
      }
      
      fetchNutritionData();
    }
  }, [isVisible, ingredients, nutritionData]);

  const fetchNutritionData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Call backend nutrition facts endpoint
      const response = await fetch(`${config.API_BASE_URL}${config.ENDPOINTS.NUTRITION_FACTS}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ingredients: ingredients,
          serving_size: servingSize
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Nutrition API Error:', response.status, errorText);
        throw new Error(`API error: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log('Nutrition API Response:', data);
      
      if (!data.nutrition_data || !data.nutrition_data.items || data.nutrition_data.items.length === 0) {
        throw new Error('No nutrition data found for the ingredients');
      }
      
      setNutritionData(data.nutrition_data);
    } catch (err) {
      console.error('Nutrition fetch error:', err);
      setError(`Failed to fetch nutrition data: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (!isVisible) return null;

  const calculateTotals = () => {
    if (!nutritionData || !nutritionData.items) return null;
    
    return nutritionData.items.reduce((totals, item) => ({
      calories: (totals.calories || 0) + (item.calories || 0),
      protein_g: (totals.protein_g || 0) + (item.protein_g || 0),
      carbohydrates_total_g: (totals.carbohydrates_total_g || 0) + (item.carbohydrates_total_g || 0),
      fat_total_g: (totals.fat_total_g || 0) + (item.fat_total_g || 0),
      fiber_g: (totals.fiber_g || 0) + (item.fiber_g || 0),
      sugar_g: (totals.sugar_g || 0) + (item.sugar_g || 0),
      sodium_mg: (totals.sodium_mg || 0) + (item.sodium_mg || 0),
      cholesterol_mg: (totals.cholesterol_mg || 0) + (item.cholesterol_mg || 0)
    }), {});
  };

  const totals = calculateTotals();

  return (
    <div className="nutrition-facts-inline">
      <div className="nutrition-facts-header-inline">
        <h2>🍎 Nutrition Facts</h2>
        <button className="close-btn-inline" onClick={onClose}>×</button>
      </div>
      
      <div className="nutrition-facts-content">
        {loading && (
          <div className="nutrition-loading">
            <div className="spinner"></div>
            <p>Calculating nutrition facts...</p>
          </div>
        )}
        
        {error && (
          <div className="nutrition-error">
            <p>⚠️ {error}</p>
            <button onClick={fetchNutritionData} className="retry-btn">
              Try Again
            </button>
          </div>
        )}
        
        {nutritionData && totals && (
          <>
            <div className="nutrition-summary">
              <h3>Total Nutrition Per Serving</h3>
              <div className="nutrition-grid">
                <div className="nutrition-item main">
                  <span className="label">Calories</span>
                  <span className="value">{Math.round(totals.calories)}</span>
                  {servingSize > 1 && (
                    <span className="per-person">({Math.round(totals.calories / servingSize)} per person)</span>
                  )}
                </div>
                <div className="nutrition-item">
                  <span className="label">Total Fat</span>
                  <span className="value">{totals.fat_total_g.toFixed(1)}g</span>
                </div>
                <div className="nutrition-item">
                  <span className="label">Protein</span>
                  <span className="value">{totals.protein_g.toFixed(1)}g</span>
                </div>
                <div className="nutrition-item">
                  <span className="label">Total Carbohydrates</span>
                  <span className="value">{totals.carbohydrates_total_g.toFixed(1)}g</span>
                </div>
                <div className="nutrition-item">
                  <span className="label">Fiber</span>
                  <span className="value">{totals.fiber_g.toFixed(1)}g</span>
                </div>
                <div className="nutrition-item">
                  <span className="label">Sugar</span>
                  <span className="value">{totals.sugar_g.toFixed(1)}g</span>
                </div>
                <div className="nutrition-item">
                  <span className="label">Sodium</span>
                  <span className="value">{Math.round(totals.sodium_mg)}mg</span>
                </div>
                <div className="nutrition-item">
                  <span className="label">Cholesterol</span>
                  <span className="value">{Math.round(totals.cholesterol_mg)}mg</span>
                </div>
              </div>
            </div>
            
            <div className="ingredient-breakdown">
              <h3>Per Ingredient Breakdown</h3>
              <div className="ingredient-nutrition">
                {nutritionData.items.map((item, index) => (
                  <div key={index} className="ingredient-item">
                    <div className="ingredient-header">
                      <h4>{item.name}</h4>
                      <span className="serving-size">{Math.round(item.serving_size_g)}g</span>
                    </div>
                    <div className="ingredient-nutrition-grid">
                      <span className="mini-label">Calories</span>
                      <span className="mini-value">{Math.round(item.calories)}</span>
                      <span className="mini-label">Protein</span>
                      <span className="mini-value">{item.protein_g.toFixed(1)}g</span>
                      <span className="mini-label">Carbs</span>
                      <span className="mini-value">{item.carbohydrates_total_g.toFixed(1)}g</span>
                      <span className="mini-label">Fat</span>
                      <span className="mini-value">{item.fat_total_g.toFixed(1)}g</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="nutrition-disclaimer">
              <p>
                <strong>Note:</strong> Nutrition information is estimated based on ingredient quantities and may vary. 
                Values are calculated per serving and should be used as a general guideline.
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default NutritionFacts;
