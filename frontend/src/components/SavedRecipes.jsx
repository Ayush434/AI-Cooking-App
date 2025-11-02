import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { useAuth } from '../contexts/AuthContext';
import config from '../config';
import './SavedRecipes.css';

function SavedRecipes({ onClose }) {
  const [allRecipes, setAllRecipes] = useState([]);
  const [savedRecipes, setSavedRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [deletingRecipe, setDeletingRecipe] = useState(null);
  const [activeTab, setActiveTab] = useState('all'); // 'all' or 'saved'
  const [favouritingRecipe, setFavouritingRecipe] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 6;
  
  const { isAuthenticated, getAuthHeaders, user } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      fetchAllRecipes();
      fetchSavedRecipes();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated]);

  const fetchAllRecipes = async () => {
    try {
      const headers = {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      };

      const response = await fetch(`${config.API_BASE_URL}${config.ENDPOINTS.MY_RECIPES}`, {
        method: 'GET',
        headers
      });

      if (response.ok) {
        const data = await response.json();
        setAllRecipes(data.recipes || []);
      } else {
        console.error('Failed to fetch all recipes:', response.status);
      }
    } catch (error) {
      console.error('Error fetching all recipes:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSavedRecipes = async () => {
    try {
      const headers = {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      };

      const response = await fetch(`${config.API_BASE_URL}${config.ENDPOINTS.FAVOURITE_RECIPES}`, {
        method: 'GET',
        headers
      });

      if (response.ok) {
        const data = await response.json();
        setSavedRecipes(data.recipes || []);
      } else {
        console.error('Failed to fetch favourite recipes:', response.status);
      }
    } catch (error) {
      console.error('Error fetching favourite recipes:', error);
    }
  };

  const toggleFavourite = async (recipe) => {
    if (!recipe.id) return;
    
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
        
        // Update recipe in both lists
        setAllRecipes(prev => prev.map(r => 
          r.id === recipe.id ? { ...r, is_saved: isNowFavourite } : r
        ));
        setSavedRecipes(prev => {
          if (isNowFavourite) {
            // Add to favourites if not already there
            if (!prev.find(r => r.id === recipe.id)) {
              return [...prev, { ...recipe, is_saved: true }];
            }
            return prev.map(r => r.id === recipe.id ? { ...r, is_saved: true } : r);
          } else {
            // Remove from favourites
            return prev.filter(r => r.id !== recipe.id);
          }
        });
        
        // Update selected recipe if it's the one being toggled
        if (selectedRecipe && selectedRecipe.id === recipe.id) {
          setSelectedRecipe({ ...selectedRecipe, is_saved: isNowFavourite });
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
        setAllRecipes(prev => prev.filter(recipe => recipe.id !== recipeId));
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

  // Format instructions for display
  const formatInstructions = (instructions) => {
    if (!instructions) return '';
    if (Array.isArray(instructions)) {
      return instructions.join('\n');
    }
    if (typeof instructions === 'string') {
      return instructions;
    }
    return '';
  };

  // Get current recipes based on active tab
  const currentRecipes = activeTab === 'all' ? allRecipes : savedRecipes;
  
  // Pagination logic
  const totalPages = Math.ceil(currentRecipes.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedRecipes = currentRecipes.slice(startIndex, endIndex);
  
  // Reset to page 1 when switching tabs
  useEffect(() => {
    setCurrentPage(1);
  }, [activeTab]);
  
  const handlePageChange = (page) => {
    setCurrentPage(page);
    // Scroll to top of recipes section
    const recipesBody = document.querySelector('.saved-recipes-body');
    if (recipesBody) {
      recipesBody.scrollTop = 0;
    }
  };

  if (!isAuthenticated) {
  return (
    <div className="saved-recipes-container">
      <div className="saved-recipes-content">
        <div className="saved-recipes-header">
          <h2>⭐ My Recipes</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>
        <div className="saved-recipes-body">
          <div className="auth-required">
            <p>Please log in to view your recipes.</p>
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
            <h2>⭐ My Recipes</h2>
            <button className="close-btn" onClick={onClose}>✕</button>
          </div>
          <div className="saved-recipes-body">
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Loading your recipes...</p>
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
                  <ReactMarkdown>{formatInstructions(selectedRecipe.instructions)}</ReactMarkdown>
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
          <h2>⭐ My Recipes</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>
        
        {/* Tabs */}
        <div className="recipes-tabs" style={{ display: 'flex', gap: '1rem', padding: '1rem', borderBottom: '1px solid #ddd' }}>
          <button 
            className={activeTab === 'all' ? 'active-tab' : ''}
            onClick={() => setActiveTab('all')}
            style={{ 
              padding: '0.5rem 1rem', 
              border: 'none', 
              background: activeTab === 'all' ? '#4CAF50' : '#f0f0f0',
              color: activeTab === 'all' ? 'white' : '#333',
              cursor: 'pointer',
              borderRadius: '4px'
            }}
          >
            All Recipes ({allRecipes.length})
          </button>
          <button 
            className={activeTab === 'saved' ? 'active-tab' : ''}
            onClick={() => setActiveTab('saved')}
            style={{ 
              padding: '0.5rem 1rem', 
              border: 'none', 
              background: activeTab === 'saved' ? '#4CAF50' : '#f0f0f0',
              color: activeTab === 'saved' ? 'white' : '#333',
              cursor: 'pointer',
              borderRadius: '4px'
            }}
          >
            Favourites ({savedRecipes.length})
          </button>
        </div>
        
        <div className="saved-recipes-body">
          {currentRecipes.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📝</div>
              <h3>
                {activeTab === 'all' 
                  ? 'No recipes yet' 
                  : 'No favourite recipes yet'}
              </h3>
              <p>
                {activeTab === 'all'
                  ? 'Generate some recipes while logged in to see them here!'
                  : 'Generate some recipes and favourite them to see them here!'}
              </p>
            </div>
          ) : (
            <>
            <div className="recipes-grid">
              {paginatedRecipes.map((recipe) => (
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
                      className={`favourite-btn-small ${recipe.is_saved ? 'favourited' : ''} ${favouritingRecipe === recipe.id ? 'loading' : ''}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleFavourite(recipe);
                      }}
                      disabled={favouritingRecipe === recipe.id}
                      title={recipe.is_saved ? 'Unfavourite' : 'Favourite'}
                    >
                      {favouritingRecipe === recipe.id ? (
                        <div className="btn-spinner small"></div>
                      ) : (
                        recipe.is_saved ? '⭐' : '☆'
                      )}
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
            
            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="pagination-container">
                <button
                  className="pagination-btn"
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  aria-label="Previous page"
                >
                  ← Previous
                </button>
                
                <div className="pagination-numbers">
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
                    // Show first page, last page, current page, and pages around current
                    const showPage = 
                      page === 1 || 
                      page === totalPages || 
                      (page >= currentPage - 1 && page <= currentPage + 1);
                    
                    if (!showPage && page === currentPage - 2 && currentPage > 3) {
                      return <span key={page} className="pagination-ellipsis">...</span>;
                    }
                    if (!showPage && page === currentPage + 2 && currentPage < totalPages - 2) {
                      return <span key={page} className="pagination-ellipsis">...</span>;
                    }
                    
                    if (!showPage) return null;
                    
                    return (
                      <button
                        key={page}
                        className={`pagination-number ${currentPage === page ? 'active' : ''}`}
                        onClick={() => handlePageChange(page)}
                        aria-label={`Go to page ${page}`}
                        aria-current={currentPage === page ? 'page' : undefined}
                      >
                        {page}
                      </button>
                    );
                  })}
                </div>
                
                <button
                  className="pagination-btn"
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  aria-label="Next page"
                >
                  Next →
                </button>
              </div>
            )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default SavedRecipes;
