import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { useAuth } from '../contexts/AuthContext';
import config from '../config';
import './SavedRecipes.css';

function SavedRecipes({ onClose }) {
  const [savedRecipes, setSavedRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [deletingRecipe, setDeletingRecipe] = useState(null);
  
  const { isAuthenticated, getAuthHeaders, user } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      fetchSavedRecipes();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated]);

  const fetchSavedRecipes = async () => {
    try {
      const headers = {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      };

      const response = await fetch(`${config.API_BASE_URL}${config.ENDPOINTS.SAVED_RECIPES}`, {
        method: 'GET',
        headers
      });

      if (response.ok) {
        const data = await response.json();
        setSavedRecipes(data.recipes || []);
      } else {
        console.error('Failed to fetch saved recipes:', response.status);
      }
    } catch (error) {
      console.error('Error fetching saved recipes:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteRecipe = async (recipeId) => {
    if (!window.confirm('Are you sure you want to delete this recipe?')) {
      return;
    }

    setDeletingRecipe(recipeId);
    try {
      const headers = {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      };

      const response = await fetch(`${config.API_BASE_URL}${config.ENDPOINTS.SAVED_RECIPE}/${recipeId}`, {
        method: 'DELETE',
        headers
      });

      if (response.ok) {
        setSavedRecipes(prev => prev.filter(recipe => recipe.id !== recipeId));
        if (selectedRecipe && selectedRecipe.id === recipeId) {
          setSelectedRecipe(null);
        }
        alert('Recipe deleted successfully!');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to delete recipe');
      }
    } catch (error) {
      console.error('Error deleting recipe:', error);
      alert(`Failed to delete recipe: ${error.message}`);
    } finally {
      setDeletingRecipe(null);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (!isAuthenticated) {
  return (
    <div className="saved-recipes-container">
      <div className="saved-recipes-content">
        <div className="saved-recipes-header">
          <h2>📚 My Saved Recipes</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>
        <div className="saved-recipes-body">
          <div className="auth-required">
            <p>Please log in to view your saved recipes.</p>
          </div>
        </div>
      </div>
    </div>
  );
  }

  if (loading) {
    return (
      <div className="saved-recipes-container">
        <div className="saved-recipes-content">
          <div className="saved-recipes-header">
            <h2>📚 My Saved Recipes</h2>
            <button className="close-btn" onClick={onClose}>✕</button>
          </div>
          <div className="saved-recipes-body">
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Loading your saved recipes...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (selectedRecipe) {
    return (
      <div className="saved-recipes-container">
        <div className="saved-recipes-content">
          <div className="saved-recipes-header">
            <button className="back-btn" onClick={() => setSelectedRecipe(null)}>
              ← Back to Recipes
            </button>
            <button className="close-btn" onClick={onClose}>✕</button>
          </div>
          
          <div className="saved-recipes-body">
            <div className="recipe-detail">
              <div className="recipe-detail-header">
                <h2>{selectedRecipe.title}</h2>
                <div className="recipe-meta">
                  <span className="recipe-date">
                    Saved on {formatDate(selectedRecipe.created_at)}
                  </span>
                  {selectedRecipe.serving_size && (
                    <span className="serving-size">
                      Serves {selectedRecipe.serving_size}
                    </span>
                  )}
                </div>
              </div>
              
              <div className="recipe-content">
                {selectedRecipe.instructions ? (
                  <ReactMarkdown>{selectedRecipe.instructions}</ReactMarkdown>
                ) : (
                  <p>No recipe content available.</p>
                )}
              </div>
              
              <div className="recipe-actions">
                <button
                  className="delete-recipe-btn"
                  onClick={() => deleteRecipe(selectedRecipe.id)}
                  disabled={deletingRecipe === selectedRecipe.id}
                >
                  {deletingRecipe === selectedRecipe.id ? (
                    <>
                      <div className="btn-spinner"></div>
                      Deleting...
                    </>
                  ) : (
                    <>
                      🗑️ Delete Recipe
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="saved-recipes-container">
      <div className="saved-recipes-content">
        <div className="saved-recipes-header">
          <h2>📚 My Saved Recipes</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>
        
        <div className="saved-recipes-body">
          {savedRecipes.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📝</div>
              <h3>No saved recipes yet</h3>
              <p>Generate some recipes and save your favorites to see them here!</p>
            </div>
          ) : (
            <div className="recipes-grid">
              {savedRecipes.map((recipe) => (
                <div key={recipe.id} className="recipe-card" onClick={() => setSelectedRecipe(recipe)}>
                  <div className="recipe-card-header">
                    <h3>{recipe.title}</h3>
                    <span className="recipe-date">{formatDate(recipe.created_at)}</span>
                  </div>
                  
                  <div className="recipe-card-content">
                    {recipe.description && (
                      <p className="recipe-description">{recipe.description}</p>
                    )}
                    
                    {recipe.original_ingredients && recipe.original_ingredients.length > 0 && (
                      <div className="recipe-ingredients-preview">
                        <strong>Ingredients:</strong> {recipe.original_ingredients.slice(0, 3).join(', ')}
                        {recipe.original_ingredients.length > 3 && '...'}
                      </div>
                    )}
                    
                    {recipe.serving_size && (
                      <div className="recipe-serving">
                        Serves {recipe.serving_size}
                      </div>
                    )}
                  </div>
                  
                  <div className="recipe-card-footer">
                    <button
                      className="view-recipe-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedRecipe(recipe);
                      }}
                    >
                      View Recipe
                    </button>
                    <button
                      className="delete-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteRecipe(recipe.id);
                      }}
                      disabled={deletingRecipe === recipe.id}
                    >
                      {deletingRecipe === recipe.id ? (
                        <div className="btn-spinner small"></div>
                      ) : (
                        '🗑️'
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SavedRecipes;
