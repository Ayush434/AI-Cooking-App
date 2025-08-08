import React from 'react';
import ReactMarkdown from 'react-markdown';
import './RecipeList.css';

function RecipeList({ recipes }) {
  if (!recipes.length) return null;
  
  return (
    <div className="recipes-list-card">
      <h3>Recipe Suggestions:</h3>
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
    </div>
  );
}

export default RecipeList;