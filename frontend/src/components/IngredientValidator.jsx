import React, { useState } from 'react';
import './IngredientValidator.css';
import config from '../config';

const IngredientValidator = () => {
  const [ingredient, setIngredient] = useState('');
  const [validationResult, setValidationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const validateIngredient = async () => {
    if (!ingredient.trim()) {
      setError('Please enter an ingredient');
      return;
    }

    setLoading(true);
    setError('');
    setValidationResult(null);

    try {
      const response = await fetch(`${config.API_BASE_URL}${config.ENDPOINTS.VALIDATE_INGREDIENT}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ingredient: ingredient.trim() }),
      });

      const data = await response.json();

      if (response.ok) {
        setValidationResult(data.validation_result);
      } else {
        setError(data.error || 'Validation failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setIngredient(suggestion);
    setValidationResult(null);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      validateIngredient();
    }
  };

  return (
    <div className="ingredient-validator">
      <h2>Ingredient Validator</h2>
      <p>Enter an ingredient to validate if it's a food item and get suggestions for corrections.</p>
      
      <div className="input-section">
        <div className="input-group">
          <input
            type="text"
            value={ingredient}
            onChange={(e) => setIngredient(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter an ingredient (e.g., 'appel', 'tomato', 'computer')"
            className="ingredient-input"
          />
          <button 
            onClick={validateIngredient} 
            disabled={loading}
            className="validate-btn"
          >
            {loading ? 'Validating...' : 'Validate'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {validationResult && (
        <div className="validation-result">
          <h3>Validation Result</h3>
          
          <div className={`result-card ${validationResult.is_valid ? 'valid' : 'invalid'}`}>
            <div className="result-header">
              <span className={`status ${validationResult.is_valid ? 'valid' : 'invalid'}`}>
                {validationResult.is_valid ? '✓ Valid Food Item' : '✗ Not a Food Item'}
              </span>
              {validationResult.confidence > 0 && (
                <span className="confidence">
                  Confidence: {(validationResult.confidence * 100).toFixed(0)}%
                </span>
              )}
            </div>
            
            <div className="result-details">
              <p><strong>Original:</strong> "{validationResult.original}"</p>
              
              {validationResult.corrected && validationResult.corrected !== validationResult.original && (
                <p><strong>Corrected:</strong> "{validationResult.corrected}"</p>
              )}
              
              {validationResult.source && (
                <p><strong>Source:</strong> {validationResult.source}</p>
              )}
            </div>

            {validationResult.suggestions && validationResult.suggestions.length > 0 && (
              <div className="suggestions">
                <h4>Did you mean?</h4>
                <div className="suggestion-buttons">
                  {validationResult.suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="suggestion-btn"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="examples">
        <h3>Try these examples:</h3>
        <div className="example-buttons">
          <button onClick={() => setIngredient('appel')} className="example-btn">appel</button>
          <button onClick={() => setIngredient('bananna')} className="example-btn">bananna</button>
          <button onClick={() => setIngredient('tomatos')} className="example-btn">tomatos</button>
          <button onClick={() => setIngredient('computer')} className="example-btn">computer</button>
          <button onClick={() => setIngredient('tomato')} className="example-btn">tomato</button>
          <button onClick={() => setIngredient('apple')} className="example-btn">apple</button>
        </div>
      </div>
    </div>
  );
};

export default IngredientValidator; 