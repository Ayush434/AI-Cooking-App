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
      (data.ingredients || []).forEach(addIngredient);
    } catch (err) {
      alert(`Failed to detect ingredients: ${err.message}`);
    }
    setLoading(false);
  };

  // Get recipes from backend
  const getRecipes = async () => {
    setLoading(true);
    setButtonDisabled(true); // Hide button for 5 seconds
    try {
      const res = await fetch('http://localhost:5000/api/recipes/get-recipes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ingredients }),
      });
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      const data = await res.json();
      setRecipes(data.recipes || []);
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
          <button
            className="main-new-recipe new-recipe-btn"
            onClick={handleNewRecipe}
            style={{ marginBottom: '1.5rem' }}
          >
            New Recipe
          </button>
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
            <RecipeList recipes={recipes} />
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
