import { useState, useEffect } from 'react';
import './IngredientList.css';

function IngredientList({ ingredients, onRemove, onClear }) {
  const [validationResults, setValidationResults] = useState({});

  // Validate ingredients when they change
  useEffect(() => {
    const validateIngredients = async () => {
      const results = {};
      
      for (const ingredient of ingredients) {
        try {
          const response = await fetch('http://localhost:5000/api/recipes/validate-ingredient', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ingredient }),
          });

          if (response.ok) {
            const data = await response.json();
            results[ingredient] = data.validation_result;
          }
        } catch (err) {
          // If validation fails, mark as unknown
          results[ingredient] = { is_valid: null, confidence: 0 };
        }
      }
      
      setValidationResults(results);
    };

    if (ingredients.length > 0) {
      validateIngredients();
    }
  }, [ingredients]);

  const getValidationIcon = (ingredient) => {
    const result = validationResults[ingredient];
    if (!result) return null;
    
    if (result.is_valid === true) {
      return <span className="valid-icon" title="Valid food item">✓</span>;
    } else if (result.is_valid === false) {
      return <span className="invalid-icon" title="Not a food item">✗</span>;
    } else {
      return <span className="unknown-icon" title="Validation unknown">?</span>;
    }
  };

  const getValidationClass = (ingredient) => {
    const result = validationResults[ingredient];
    if (!result) return '';
    
    if (result.is_valid === true) return 'valid';
    if (result.is_valid === false) return 'invalid';
    return 'unknown';
  };

  return (
    <div className="ingredients-list-card">
      <h3>Ingredients:</h3>
      {ingredients.length === 0 ? (
        <p className="empty">None yet.</p>
      ) : (
        <>
          <ul className="ingredient-list">
            {ingredients.map((ing, idx) => (
              <li key={idx} className={`ingredient-item ${getValidationClass(ing)}`}>
                <span className="ingredient-text">{ing}</span>
                <div className="ingredient-actions">
                  {getValidationIcon(ing)}
                  <button className="remove-btn" onClick={() => onRemove(ing)} title="Remove">&times;</button>
                </div>
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