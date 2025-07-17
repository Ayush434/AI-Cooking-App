import './IngredientList.css';

function IngredientList({ ingredients, onRemove }) {
  return (
    <div className="ingredients-list-card">
      <h3>Ingredients:</h3>
      {ingredients.length === 0 ? (
        <p className="empty">None yet.</p>
      ) : (
        <ul className="ingredient-list">
          {ingredients.map((ing, idx) => (
            <li key={idx} className="ingredient-item">
              <span>{ing}</span>
              <button className="remove-btn" onClick={() => onRemove(ing)} title="Remove">&times;</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default IngredientList; 