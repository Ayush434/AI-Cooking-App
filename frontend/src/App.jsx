import { useState, useEffect } from 'react';
import './App.css';
import IngredientInput from './components/IngredientInput';
import IngredientList from './components/IngredientList';
import RecipeList from './components/RecipeList';
import Loader from './components/Loader';
import AuthModal from './components/AuthModal';
import Navbar from './components/Navbar';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import config from './config';

const currentYear = new Date().getFullYear();

function AppContent() {
  // Load state from localStorage on component mount
  const [ingredients, setIngredients] = useState(() => {
    const saved = localStorage.getItem('app_ingredients');
    return saved ? JSON.parse(saved) : [];
  });
  const [recipes, setRecipes] = useState(() => {
    const saved = localStorage.getItem('app_recipes');
    return saved ? JSON.parse(saved) : [];
  });
  const [loading, setLoading] = useState(false);
  const [buttonDisabled, setButtonDisabled] = useState(false); // For hiding get recipe button
  const [mode, setMode] = useState(() => {
    const saved = localStorage.getItem('app_mode');
    return saved || 'initial';
  }); // 'initial', 'adding', 'afterRecipe'
  const [dietaryPreferences, setDietaryPreferences] = useState(() => {
    const saved = localStorage.getItem('app_dietary_preferences');
    return saved || '';
  }); // New state for dietary preferences
  const [servingSize, setServingSize] = useState(() => {
    const saved = localStorage.getItem('app_serving_size');
    return saved ? parseInt(saved) : 1;
  }); // New state for serving size
  const [randomIngredients, setRandomIngredients] = useState(() => {
    const saved = localStorage.getItem('app_random_ingredients');
    return saved ? JSON.parse(saved) : [];
  }); // State for random ingredients
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState('login'); // 'login', 'register', 'profile'
  
  const { user, loading: authLoading, getAuthHeaders } = useAuth();

  // Save state to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('app_ingredients', JSON.stringify(ingredients));
  }, [ingredients]);

  useEffect(() => {
    localStorage.setItem('app_recipes', JSON.stringify(recipes));
  }, [recipes]);

  useEffect(() => {
    localStorage.setItem('app_mode', mode);
  }, [mode]);

  useEffect(() => {
    localStorage.setItem('app_dietary_preferences', dietaryPreferences);
  }, [dietaryPreferences]);

  useEffect(() => {
    localStorage.setItem('app_serving_size', servingSize.toString());
  }, [servingSize]);

  useEffect(() => {
    localStorage.setItem('app_random_ingredients', JSON.stringify(randomIngredients));
  }, [randomIngredients]);

  // Auth functions
  const openAuthModal = (mode = 'login') => {
    setAuthMode(mode);
    setAuthModalOpen(true);
  };

  const closeAuthModal = () => {
    setAuthModalOpen(false);
  };

  // Navigation functions
  const goHome = () => {
    setMode('initial');
    // Scroll to top smoothly
    setTimeout(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 100);
  };

  // Comprehensive list of common ingredients
  const ingredientList = [
    // Proteins
    'chicken breast', 'ground beef', 'salmon', 'eggs', 'tofu', 'shrimp', 'pork chops', 'turkey', 'tuna', 'bacon',
    'black beans', 'chickpeas', 'lentils', 'quinoa', 'greek yogurt', 'cottage cheese', 'almonds', 'walnuts',
    
    // Vegetables
    'tomatoes', 'onions', 'garlic', 'bell peppers', 'mushrooms', 'spinach', 'broccoli', 'carrots', 'potatoes',
    'sweet potatoes', 'zucchini', 'cucumber', 'lettuce', 'celery', 'corn', 'peas', 'green beans', 'asparagus',
    'cauliflower', 'brussels sprouts', 'kale', 'cabbage', 'eggplant', 'avocado', 'cilantro', 'parsley',
    
    // Fruits
    'bananas', 'apples', 'lemons', 'limes', 'oranges', 'strawberries', 'blueberries', 'grapes', 'pineapple',
    'mango', 'papaya', 'kiwi', 'peaches', 'pears', 'cherries', 'watermelon', 'cantaloupe',
    
    // Grains & Starches
    'rice', 'pasta', 'bread', 'oats', 'barley', 'couscous', 'bulgur', 'tortillas', 'crackers', 'noodles',
    
    // Dairy & Alternatives
    'milk', 'cheese', 'butter', 'cream', 'sour cream', 'mozzarella', 'parmesan', 'cheddar', 'feta',
    'coconut milk', 'almond milk', 'cream cheese',
    
    // Pantry Staples
    'olive oil', 'coconut oil', 'honey', 'maple syrup', 'soy sauce', 'vinegar', 'mustard', 'ketchup',
    'hot sauce', 'vanilla extract', 'flour', 'sugar', 'brown sugar', 'baking soda', 'baking powder',
    
    // Herbs & Spices
    'basil', 'oregano', 'thyme', 'rosemary', 'sage', 'paprika', 'cumin', 'chili powder', 'black pepper',
    'salt', 'ginger', 'turmeric', 'cinnamon', 'nutmeg', 'bay leaves', 'red pepper flakes',
    
    // Nuts & Seeds
    'sunflower seeds', 'pumpkin seeds', 'cashews', 'pistachios', 'peanuts', 'pine nuts', 'chia seeds', 'flax seeds'
  ];

  // Generate random ingredients
  const generateRandomIngredients = () => {
    const shuffled = [...ingredientList].sort(() => 0.5 - Math.random());
    const selected = shuffled.slice(0, 6);
    setRandomIngredients(selected);
  };

  // Add random ingredient to main list
  const addRandomIngredient = (ingredient) => {
    addIngredient(ingredient);
    // Remove from random suggestions
    setRandomIngredients(prev => prev.filter(item => item !== ingredient));
  };

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
    setRandomIngredients([]);
    setDietaryPreferences('');
    setServingSize(1);
    setMode('initial');
  };

  // Clear all app state (for logout or complete reset)
  const clearAllAppState = () => {
    localStorage.removeItem('app_ingredients');
    localStorage.removeItem('app_recipes');
    localStorage.removeItem('app_mode');
    localStorage.removeItem('app_dietary_preferences');
    localStorage.removeItem('app_serving_size');
    localStorage.removeItem('app_random_ingredients');
    setIngredients([]);
    setRecipes([]);
    setMode('initial');
    setDietaryPreferences('');
    setServingSize(1);
    setRandomIngredients([]);
  };

  // Detect ingredients from image
  const detectIngredients = async (imageFile) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('image', imageFile);
    try {
      const res = await fetch(`${config.API_BASE_URL}${config.ENDPOINTS.DETECT_INGREDIENTS}`, {
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
      const headers = {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      };
      
      const res = await fetch(`${config.API_BASE_URL}${config.ENDPOINTS.GET_RECIPES}`, {
        method: 'POST',
        headers,
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
    setRandomIngredients([]);
    setMode('adding');
  };

  // Add Ingredient after recipe is shown
  const handleAddIngredient = () => {
    setMode('adding');
  };

  return (
    <div className="main-bg">
      {/* Navigation Bar */}
      <Navbar 
        onNewRecipe={handleNewRecipe}
        onOpenAuthModal={openAuthModal}
        onGoHome={goHome}
        currentMode={mode}
      />
      
      <div className="app-container">
        {/* Main Content Header */}
        <div className="app-header">
          <div className="app-title-section">
            <h1 className="app-title">SnackHack</h1>
            <p className="subtitle">Discover recipes with what you have!</p>
          </div>
        </div>
        {(mode === 'initial' || mode === 'afterRecipe') && (
          <>
            <button
              className="main-new-recipe new-recipe-btn home-new-recipe"
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
              
              {/* Random Ingredients Section */}
              <div className="random-ingredients-section">
                <div className="random-header">
                  <h3>🎲 Need inspiration?</h3>
                  <button 
                    className="generate-random-btn"
                    onClick={generateRandomIngredients}
                    type="button"
                  >
                    Generate Random Ingredients
                  </button>
                </div>
                
                {randomIngredients.length > 0 && (
                  <div className="random-ingredients-grid">
                    <p className="random-subtitle">Click any ingredient to add it to your list:</p>
                    <div className="random-ingredients-list">
                      {randomIngredients.map((ingredient, index) => (
                        <button
                          key={index}
                          className="random-ingredient-btn"
                          onClick={() => addRandomIngredient(ingredient)}
                          type="button"
                        >
                          + {ingredient}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
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
        
        <AuthModal
          isOpen={authModalOpen}
          onClose={closeAuthModal}
        />
      </div>
      <footer className="footer">
        &copy; {currentYear} Ayush Mehta
      </footer>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
