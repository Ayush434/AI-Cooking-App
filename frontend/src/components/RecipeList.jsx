import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import NutritionFacts from './NutritionFacts';
import './RecipeList.css';

function RecipeList({ recipes, originalIngredients, dietaryPreferences, servingSize }) {
  const [showNutrition, setShowNutrition] = useState(false);
  const [nutritionLoading, setNutritionLoading] = useState(false);
  
  if (!recipes.length) return null;
  
  // Check if any recipes appear incomplete
  const checkRecipeCompleteness = (recipe) => {
    if (!recipe.markdown_content) return false;
    const content = recipe.markdown_content;
    return content.toLowerCase().includes('## ingredients') && 
           content.toLowerCase().includes('## instructions') && 
           content.length > 200;
  };
  
  const hasIncompleteRecipes = recipes.some(recipe => 
    !recipe.is_error && !checkRecipeCompleteness(recipe)
  );

  // Extract ingredients from AI-generated recipe content
  const extractRecipeIngredients = () => {
    if (!recipes || recipes.length === 0) return [];
    
    // Try to find ingredients from the first complete recipe
    const completeRecipe = recipes.find(recipe => 
      !recipe.is_error && checkRecipeCompleteness(recipe)
    );
    
    if (completeRecipe) {
      // Try to extract ingredients from markdown content
      if (completeRecipe.markdown_content) {
        const content = completeRecipe.markdown_content;
        const ingredientsMatch = content.match(/## ingredients\s*\n([\s\S]*?)(?=##|$)/i);
        
        if (ingredientsMatch) {
          const ingredientsText = ingredientsMatch[1].trim();
          // Parse ingredients list (remove bullets, numbers, etc.)
          const ingredients = ingredientsText
            .split('\n')
            .map(line => line.trim())
            .filter(line => line.length > 0)
            .map(line => {
              // Remove common list markers and extra whitespace
              return line.replace(/^[-*•\d\.\s]+/, '').trim();
            })
            .filter(ingredient => ingredient.length > 0);
          
          if (ingredients.length > 0) {
            return ingredients;
          }
        }
      }
      
      // Fallback to old format ingredients
      if (completeRecipe.ingredients && completeRecipe.ingredients.length > 0) {
        return completeRecipe.ingredients;
      }
    }
    
    // If no recipe ingredients found, fall back to original ingredients
    return originalIngredients || [];
  };

  const recipeIngredients = extractRecipeIngredients();
  
  // Log extracted ingredients for debugging
  console.log('Original user ingredients:', originalIngredients);
  console.log('AI-generated recipe ingredients:', recipeIngredients);
  
  return (
    <div className="recipes-list-card">
      {/* Request Summary Section */}
      <div className="request-summary">
        <h3>Your Recipe Request:</h3>
        <div className="summary-content">
          <div className="summary-item">
            <strong>Ingredients:</strong> {originalIngredients?.join(', ') || 'None specified'}
          </div>
          <div className="summary-item">
            <strong>Serving Size:</strong> {servingSize || 1} {(servingSize || 1) === 1 ? 'person' : 'people'}
          </div>
          {dietaryPreferences && dietaryPreferences.trim() && (
            <div className="summary-item">
              <strong>Dietary Preferences:</strong> {dietaryPreferences.trim()}
            </div>
          )}
        </div>
      </div>

      <h3>AI-Generated Recipe Suggestions:</h3>
      
      {/* Warning for incomplete recipes */}
      {hasIncompleteRecipes && (
        <div className="incomplete-warning">
          <p>
            <strong>⚠️ Notice:</strong> Some recipes may appear incomplete due to generation limits. 
            Try regenerating for complete recipes or adjust your ingredients.
          </p>
        </div>
      )}
      
      <div className="recipe-cards">
        {recipes.map((rec, idx) => (
          <div className={`recipe-card ${rec.is_error ? 'error-card' : ''}`} key={idx}>
            {rec.is_error ? (
              // Error card - render as before
              <>
                <div className="recipe-title error-title">
                  ⚠️ {rec.title}
                </div>
                <div className="recipe-instructions error-instructions">
                  <div className="instructions-text">{rec.instructions}</div>
                </div>
              </>
            ) : (
              // Normal recipe - render markdown content
              <div className="recipe-markdown">
                {rec.markdown_content || (rec.instructions && rec.instructions.includes('#')) ? (
                  <ReactMarkdown>{rec.markdown_content || rec.instructions}</ReactMarkdown>
                ) : (
                  // Fallback for old format recipes
                  <>
                    <div className="recipe-title">{rec.title}</div>
                    {rec.ingredients && rec.ingredients.length > 0 && (
                      <div className="recipe-ingredients">
                        <b>Ingredients:</b> {rec.ingredients.join(', ')}
                      </div>
                    )}
                    {rec.instructions && (
                      <div className="recipe-instructions">
                        <b>Instructions:</b>
                        <div className="instructions-text">{rec.instructions}</div>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
      
      {/* Nutrition Facts Button */}
      <div className="nutrition-section">
        <button
          className={`nutrition-facts-btn ${nutritionLoading ? 'loading' : ''}`}
          onClick={() => setShowNutrition(true)}
          disabled={nutritionLoading}
        >
          {nutritionLoading ? (
            <>
              <div className="btn-spinner"></div>
              Calculating...
            </>
          ) : (
            recipeIngredients.length > 0 && recipeIngredients !== originalIngredients
              ? '🍎 View Nutrition Facts (AI Recipe)'
              : '🍎 View Nutrition Facts (User Ingredients)'
          )}
        </button>
        <p className="nutrition-note">
          Get detailed nutritional information based on the AI-generated recipe ingredients and serving size
        </p>
      </div>
      
      {/* AI Disclaimer */}
      <div className="ai-disclaimer">
        <p>
          <strong>⚠️ AI-Generated Content:</strong> This recipe was generated by artificial intelligence. 
          Please review all ingredients and cooking instructions carefully before use. Always ensure food safety 
          and adjust cooking times/temperatures as needed based on your equipment and preferences.
        </p>
      </div>
      
      {/* Nutrition Facts Modal */}
      <NutritionFacts
        ingredients={recipeIngredients}
        servingSize={servingSize}
        isVisible={showNutrition}
        onClose={() => setShowNutrition(false)}
        onLoadingChange={setNutritionLoading}
      />
    </div>
  );
}

export default RecipeList;