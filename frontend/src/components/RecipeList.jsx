import './RecipeList.css';

function RecipeList({ recipes }) {
  if (!recipes.length) return null;
  
  return (
    <div className="recipes-list-card">
      <h3>Recipe Suggestions:</h3>
      <div className="recipe-cards">
        {recipes.map((rec, idx) => (
          <div className={`recipe-card ${rec.is_error ? 'error-card' : ''}`} key={idx}>
            <div className={`recipe-title ${rec.is_error ? 'error-title' : ''}`}>
              {rec.is_error ? '⚠️ ' : ''}{rec.title}
            </div>
            {!rec.is_error && rec.ingredients.length > 0 && (
              <div className="recipe-ingredients">
                <b>Ingredients:</b> {rec.ingredients.join(', ')}
              </div>
            )}
            {rec.instructions && (
              <div className={`recipe-instructions ${rec.is_error ? 'error-instructions' : ''}`}>
                {!rec.is_error && <b>Instructions:</b>}
                <div className="instructions-text">{rec.instructions}</div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default RecipeList;