import './IngredientList.css';

function IngredientList({ ingredients, onRemove, onClear }) {
  return (
    <div className="ingredients-list-card">
      <h3>Ingredients:</h3>
      {ingredients.length === 0 ? (
        <p className="empty">None yet.</p>
      ) : (
        <>
          <ul className="ingredient-list">
            {ingredients.map((ing, idx) => (
              <li key={idx} className="ingredient-item">
                <span>{ing}</span>
                <button className="remove-btn" onClick={() => onRemove(ing)} title="Remove">&times;</button>
              </li>
            ))}
          </ul>
          <button className="clear-btn" onClick={onClear} style={{marginTop: '0.7rem'}}>Clear All</button>
        </>
      )}
    </div>
  );
}

export default IngredientList; 