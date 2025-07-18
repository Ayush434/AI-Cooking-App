import { useState } from 'react';
import './App.css';
import IngredientInput from './components/IngredientInput';
import IngredientList from './components/IngredientList';
import RecipeList from './components/RecipeList';
import Loader from './components/Loader';

function App() {
  const [ingredients, setIngredients] = useState([]);
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(false);

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

  // Detect ingredients from image
  const detectIngredients = async (imageFile) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('image', imageFile);
    try {
      console.log('🔍 Calling detect-ingredients API...');
      const res = await fetch('http://localhost:5000/api/recipes/detect-ingredients', {
        method: 'POST',
        body: formData,
      });
      console.log('📡 Response status:', res.status);
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      console.log('📦 Response data:', data);
      (data.ingredients || []).forEach(addIngredient);
    } catch (err) {
      console.error('❌ Error detecting ingredients:', err);
      alert(`Failed to detect ingredients: ${err.message}`);
    }
    setLoading(false);
  };

  // Get recipes from backend
  const getRecipes = async () => {
    setLoading(true);
    try {
      console.log('🍳 Calling get-recipes API with ingredients:', ingredients);
      const res = await fetch('http://localhost:5000/api/recipes/get-recipes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ingredients }),
      });
      console.log('📡 Response status:', res.status);
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      console.log('📦 Response data:', data);
      setRecipes(data.recipes || []);
    } catch (err) {
      console.error('❌ Error getting recipes:', err);
      alert(`Failed to get recipes: ${err.message}`);
    }
    setLoading(false);
  };

  return (
    <div className="main-bg">
      <div className="app-container">
        <h1 className="app-title">AI Cooking Assistant</h1>
        <p className="subtitle">Discover recipes with what you have!</p>
        <IngredientInput
          onAdd={addIngredient}
          onDetect={detectIngredients}
          loading={loading}
        />
        <IngredientList
          ingredients={ingredients}
          onRemove={removeIngredient}
        />
        <button
          className="get-recipes-btn"
          onClick={getRecipes}
          disabled={ingredients.length < 4 || loading}
        >
          Get Recipe Suggestions
        </button>
        {loading && <Loader />}
        <RecipeList recipes={recipes} />
      </div>
    </div>
  );
}

export default App;
