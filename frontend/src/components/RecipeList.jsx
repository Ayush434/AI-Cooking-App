import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import NutritionFacts from './NutritionFacts';
import { useAuth } from '../contexts/AuthContext';
import config from '../config';
import './RecipeList.css';

function RecipeList({ recipes, originalIngredients, dietaryPreferences, servingSize }) {
  const [showNutrition, setShowNutrition] = useState(false);
  const [nutritionLoading, setNutritionLoading] = useState(false);
  const [favouritingRecipe, setFavouritingRecipe] = useState(null);
  const [favouriteRecipes, setFavouriteRecipes] = useState(new Set());
  
  const { isAuthenticated, getAuthHeaders } = useAuth();
  
  // Format AI model name for display
  const formatAIModelName = (modelName) => {
    if (!modelName) return 'AI';
    
    // Format Gemini models
    if (modelName.includes('gemini')) {
      if (modelName.includes('2.5-flash-lite')) return 'Gemini 2.5 Flash Lite';
      if (modelName.includes('2.5-flash')) return 'Gemini 2.5 Flash';
      if (modelName.includes('2.5-pro')) return 'Gemini 2.5 Pro';
      if (modelName.includes('2.0-flash')) return 'Gemini 2.0 Flash';
      if (modelName.includes('1.5-flash')) return 'Gemini 1.5 Flash';
      if (modelName.includes('1.5-pro')) return 'Gemini 1.5 Pro';
      if (modelName.includes('flash')) return 'Gemini Flash';
      if (modelName.includes('pro')) return 'Gemini Pro';
      return 'Gemini AI';
    }
    
    // Format Groq models (FREE AI API)
    if (modelName.includes('llama') || modelName.includes('groq') || modelName.includes('mixtral')) {
      if (modelName.includes('llama-3.1-70b')) return 'Groq (Llama 3.1 70B)';
      if (modelName.includes('llama-3.1')) return 'Groq (Llama 3.1)';
      if (modelName.includes('llama-3')) return 'Groq (Llama 3)';
      if (modelName.includes('llama')) return 'Groq (Llama)';
      if (modelName.includes('mixtral')) return 'Groq (Mixtral)';
      return 'Groq';
    }
    
    // Format OpenAI models (paid alternative)
    if (modelName.includes('gpt') || modelName.includes('openai')) {
      if (modelName.includes('4o-mini')) return 'OpenAI GPT-4o Mini';
      if (modelName.includes('4o')) return 'OpenAI GPT-4o';
      if (modelName.includes('4')) return 'OpenAI GPT-4';
      if (modelName.includes('3.5')) return 'OpenAI GPT-3.5';
      return 'OpenAI';
    }
    
    // Format Mistral models (deprecated, kept for backwards compatibility)
    if (modelName.includes('mistral') || modelName.includes('Mixtral')) {
      return 'Mistral AI (Deprecated)';
    }
    
    // Fallback: return as-is or simplified
    return modelName.replace(/^models\//, '').replace(/-\d+\.\d+.*$/, '');
  };
  
  // Check if a recipe is favourited (by ID if available, or by title)
  const isFavourite = (recipe) => {
    // First check if recipe has is_saved flag (from database)
    if (recipe.is_saved !== undefined) {
      return recipe.is_saved;
    }
    // Fallback to local state
    if (recipe.id) {
      return favouriteRecipes.has(recipe.id);
    }
    return favouriteRecipes.has(recipe.title);
  };
  
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
  
  // Toggle favourite function
  const toggleFavourite = async (recipe) => {
    if (!isAuthenticated) {
      alert('Please log in to favourite recipes');
      return;
    }
    
    if (!recipe.id) {
      alert('Recipe ID not found. Please wait for the recipe to be saved.');
      return;
    }
    
    setFavouritingRecipe(recipe.id);
    try {
      const headers = {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      };
      
      const response = await fetch(`${config.API_BASE_URL}${config.ENDPOINTS.TOGGLE_FAVOURITE}`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ recipe_id: recipe.id })
      });
      
      if (response.ok) {
        const data = await response.json();
        const isNowFavourite = data.is_favourite;
        
        // Update local state
        if (isNowFavourite) {
          setFavouriteRecipes(prev => new Set([...prev, recipe.id]));
        } else {
          setFavouriteRecipes(prev => {
            const newSet = new Set(prev);
            newSet.delete(recipe.id);
            return newSet;
          });
        }
      } else {
        const errorData = await response.json();
        // Show user-friendly error message for max favourites limit
        if (errorData.max_favourites) {
          alert(`You can only have ${errorData.max_favourites} favourite recipes. Please unfavourite one first.`);
          return; // Exit early since we've shown the alert
        }
        throw new Error(errorData.error || 'Failed to toggle favourite');
      }
    } catch (error) {
      console.error('Error toggling favourite:', error);
      // Only show alert if we haven't already shown one for max favourites
      if (!error.message.includes('max_favourites')) {
        alert(`Failed to toggle favourite: ${error.message}`);
      }
    } finally {
      setFavouritingRecipe(null);
    }
  };
  
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
                
                {/* AI Model Acknowledgment */}
                {rec.ai_model_used && (
                  <div className="ai-model-acknowledgment">
                    <p className="ai-model-text">
                      Recipe generated by <strong>{formatAIModelName(rec.ai_model_used)}</strong>
                    </p>
                  </div>
                )}
                
                {/* Favourite Toggle Button */}
                {isAuthenticated && rec.id && (
                  <div className="recipe-actions">
                    <button
                      className={`favourite-btn ${isFavourite(rec) ? 'favourited' : ''} ${favouritingRecipe === rec.id ? 'loading' : ''}`}
                      onClick={() => toggleFavourite(rec)}
                      disabled={favouritingRecipe === rec.id}
                      title={isFavourite(rec) ? 'Unfavourite recipe' : 'Favourite recipe'}
                    >
                      {favouritingRecipe === rec.id ? (
                        <>
                          <div className="btn-spinner"></div>
                          ...
                        </>
                      ) : (
                        <>
                          {isFavourite(rec) ? '⭐ Favourited' : '☆ Favourite'}
                        </>
                      )}
                    </button>
                  </div>
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