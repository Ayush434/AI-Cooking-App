import { useState } from 'react';
import './App.css';
import IngredientInput from './components/IngredientInput';
import IngredientList from './components/IngredientList';
import RecipeList from './components/RecipeList';
import Loader from './components/Loader';

const currentYear = new Date().getFullYear();

function App() {
  const [ingredients, setIngredients] = useState([]);
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [buttonDisabled, setButtonDisabled] = useState(false); // For hiding get recipe button
  const [mode, setMode] = useState('initial'); // 'initial', 'adding', 'afterRecipe'
  const [dietaryPreferences, setDietaryPreferences] = useState(''); // New state for dietary preferences
  const [servingSize, setServingSize] = useState(1); // New state for serving size

  // Add ingredient (from input or detected)
  const addIngredient = (ingredient) => {
    setIngredients((prev) => {
      const lower = ingredient.trim().toLowerCase();
      if (!lower || prev.includes(lower)) return prev;
      return [...prev, lower];
    });
  };

  // Remove ingredient
  const removeIngredient = (ingredient) => {
    setIngredients((prev) => prev.filter((ing) => ing !== ingredient));
  };

  // Clear all ingredients and recipes
  const clearIngredients = () => {
    setIngredients([]);
    setRecipes([]);
  };

  // Detect ingredients from image
  const detectIngredients = async (imageFile) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('image', imageFile);
    try {
      const res = await fetch('http://localhost:5000/api/recipes/detect-ingredients', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      const data = await res.json();
      
      // The backend now automatically validates and corrects ingredients
      // from Google Vision API, so we can add them directly
      (data.ingredients || []).forEach(addIngredient);
      
      // Show a message if ingredients were corrected
      const originalCount = data.ingredients?.length || 0;
      if (originalCount > 0) {
        console.log(`Detected and validated ${originalCount} ingredients from image`);
      }
    } catch (err) {
      alert(`Failed to detect ingredients: ${err.message}`);
    }
    setLoading(false);
  };

  // Check if a recipe appears complete
  const isRecipeComplete = (recipe) => {
    if (!recipe || !recipe.markdown_content) return false;
    
    const content = recipe.markdown_content;
    const hasTitle = content.includes('#');
    const hasIngredients = content.toLowerCase().includes('## ingredients');
    const hasInstructions = content.toLowerCase().includes('## instructions');
    const hasSteps = /[1-5]\./g.test(content); // Has numbered steps
    const hasReasonableLength = content.length > 200;
    
    return hasTitle && hasIngredients && hasInstructions && hasSteps && hasReasonableLength;
  };

  // Get recipes from backend
  const getRecipes = async () => {
    setLoading(true);
    setButtonDisabled(true); // Hide button for 5 seconds
    try {
      const res = await fetch('http://localhost:5000/api/recipes/get-recipes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          ingredients,
          dietary_preferences: dietaryPreferences.trim(),
          serving_size: servingSize
        }),
      });
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      const data = await res.json();
      const recipes = data.recipes || [];
      
      // Validate that recipes are complete before displaying
      const hasCompleteRecipes = recipes.length > 0 && recipes.some(isRecipeComplete);
      
      if (!hasCompleteRecipes && recipes.length > 0) {
        console.warn('Received incomplete recipes, waiting a bit longer...');
        // Add a small delay for incomplete recipes
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
      setRecipes(recipes);
      setMode('afterRecipe');
    } catch (err) {
      alert(`Failed to get recipes: ${err.message}`);
    }
    setLoading(false);
    setTimeout(() => setButtonDisabled(false), 5000); // 5 seconds
  };

  // New Recipe button handler (full reset)
  const handleNewRecipe = () => {
    setIngredients([]);
    setRecipes([]);
    setDietaryPreferences('');
    setServingSize(1);
    setMode('adding');
  };

  // Add Ingredient after recipe is shown
  const handleAddIngredient = () => {
    setMode('adding');
  };

  return (
    <div className="main-bg">
      <div className="app-container">
        <h1 className="app-title">AI Cooking Assistant</h1>
        <p className="subtitle">Discover recipes with what you have!</p>
        {(mode === 'initial' || mode === 'afterRecipe') && (
          <>
            <button
              className="main-new-recipe new-recipe-btn"
              onClick={handleNewRecipe}
              style={{ marginBottom: '2rem' }}
            >
              New Recipe
            </button>
            
            {/* Show informational content only on initial load */}
            {mode === 'initial' && (
              <div className="home-content">
                {/* Why Use This App Section */}
                <div className="info-section">
                  <h2>🍳 Why Use AI Cooking Assistant?</h2>
                  <div className="benefits-grid">
                    <div className="benefit-card">
                      <div className="benefit-icon">🥘</div>
                      <h3>Use What You Have</h3>
                      <p>Transform ingredients sitting in your fridge into delicious meals. No more food waste!</p>
                    </div>
                    <div className="benefit-card">
                      <div className="benefit-icon">🤖</div>
                      <h3>AI-Powered Recipes</h3>
                      <p>Get personalized recipe suggestions powered by advanced AI technology.</p>
                    </div>
                    <div className="benefit-card">
                      <div className="benefit-icon">⚡</div>
                      <h3>Quick & Easy</h3>
                      <p>Find recipes in seconds. Perfect for busy schedules and spontaneous cooking.</p>
                    </div>
                    <div className="benefit-card">
                      <div className="benefit-icon">🍽️</div>
                      <h3>Dietary Preferences</h3>
                      <p>Customize recipes for your dietary needs - vegetarian, gluten-free, and more!</p>
                    </div>
                  </div>
                </div>

                {/* How It Works Section */}
                <div className="info-section">
                  <h2>📋 How It Works</h2>
                  <div className="steps-container">
                    <div className="step-card">
                      <div className="step-number">1</div>
                      <h3>Add Ingredients</h3>
                      <p>Type in ingredients you have or take a photo to detect them automatically</p>
                    </div>
                    <div className="step-card">
                      <div className="step-number">2</div>
                      <h3>Set Preferences</h3>
                      <p>Specify dietary preferences and number of servings</p>
                    </div>
                    <div className="step-card">
                      <div className="step-number">3</div>
                      <h3>Get Recipes</h3>
                      <p>Receive personalized, AI-generated recipes with step-by-step instructions</p>
                    </div>
                  </div>
                </div>

                {/* Features Section */}
                <div className="info-section">
                  <h2>✨ Features</h2>
                  <div className="features-list">
                    <div className="feature-item">
                      <span className="feature-icon">📸</span>
                      <strong>Image Recognition:</strong> Take photos of ingredients for automatic detection
                    </div>
                    <div className="feature-item">
                      <span className="feature-icon">✅</span>
                      <strong>Ingredient Validation:</strong> Smart validation ensures you're using real food items
                    </div>
                    <div className="feature-item">
                      <span className="feature-icon">🍃</span>
                      <strong>Dietary Options:</strong> Support for various dietary restrictions and preferences
                    </div>
                    <div className="feature-item">
                      <span className="feature-icon">👥</span>
                      <strong>Serving Sizes:</strong> Adjust recipes for 1-10 people automatically
                    </div>
                    <div className="feature-item">
                      <span className="feature-icon">📱</span>
                      <strong>Mobile Friendly:</strong> Works perfectly on all devices
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        {mode === 'adding' && (
          <>
            <IngredientInput
              onAdd={addIngredient}
              onDetect={detectIngredients}
              loading={loading}
            />
            <div style={{ width: '100%' }}>
              <IngredientList
                ingredients={ingredients}
                onRemove={removeIngredient}
                onClear={clearIngredients}
              />
              <p className="ingredient-note">You need at least <b>4 ingredients</b> to generate recipe suggestions.</p>
              
              {/* Dietary Preferences and Serving Size Section */}
              <div className="recipe-preferences" style={{ 
                marginTop: '1rem', 
                marginBottom: '1rem',
                padding: '1rem',
                backgroundColor: '#f8f9fa',
                borderRadius: '8px',
                border: '1px solid #e9ecef'
              }}>
                <div style={{ marginBottom: '1rem' }}>
                  <label htmlFor="dietary-preferences" style={{ 
                    display: 'block', 
                    marginBottom: '0.5rem', 
                    fontWeight: '600',
                    color: '#495057'
                  }}>
                    Dietary Preferences (Optional):
                  </label>
                  <textarea
                    id="dietary-preferences"
                    value={dietaryPreferences}
                    onChange={(e) => setDietaryPreferences(e.target.value)}
                    placeholder="Add specific details like 'more protein', 'less fat', 'gluten-free', 'vegetarian', 'low sodium', etc."
                    rows="3"
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      border: '1px solid #ced4da',
                      borderRadius: '4px',
                      fontSize: '14px',
                      resize: 'vertical',
                      fontFamily: 'inherit'
                    }}
                  />
                </div>
                
                <div>
                  <label htmlFor="serving-size" style={{ 
                    display: 'block', 
                    marginBottom: '0.5rem', 
                    fontWeight: '600',
                    color: '#495057'
                  }}>
                    Number of Servings:
                  </label>
                  <select
                    id="serving-size"
                    value={servingSize}
                    onChange={(e) => setServingSize(parseInt(e.target.value))}
                    style={{
                      padding: '0.5rem',
                      border: '1px solid #ced4da',
                      borderRadius: '4px',
                      fontSize: '14px',
                      backgroundColor: 'white',
                      minWidth: '100px'
                    }}
                  >
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(num => (
                      <option key={num} value={num}>
                        {num} {num === 1 ? 'person' : 'people'}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
            <button
              className="get-recipes-btn"
              onClick={getRecipes}
              disabled={ingredients.length < 4 || loading || buttonDisabled}
              style={{ display: buttonDisabled ? 'none' : 'block' }}
            >
              Get Recipe Suggestions
            </button>
          </>
        )}
        {loading && <Loader />}
        {mode === 'afterRecipe' && (
          <>
            <RecipeList 
              recipes={recipes} 
              originalIngredients={ingredients}
              dietaryPreferences={dietaryPreferences}
              servingSize={servingSize}
            />
            <button
              className="add-ingredient-btn"
              onClick={handleAddIngredient}
              style={{ marginTop: '1.5rem' }}
            >
              Add Ingredient
            </button>
          </>
        )}
      </div>
      <footer className="footer">
        &copy; {currentYear} Ayush Mehta
      </footer>
    </div>
  );
}

export default App;
