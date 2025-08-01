import { useState, useEffect } from 'react';
import './IngredientInput.css';

function IngredientInput({ onAdd, onDetect, loading }) {
  const [input, setInput] = useState('');
  const [image, setImage] = useState(null);
  const [validationResult, setValidationResult] = useState(null);
  const [validating, setValidating] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [autocompleteResults, setAutocompleteResults] = useState([]);
  const [showAutocomplete, setShowAutocomplete] = useState(false);

  // Debounced validation and autocomplete
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (input.trim() && input.trim().length >= 2) {
        validateIngredient(input.trim());
        getAutocompleteSuggestions(input.trim());
      } else {
        setValidationResult(null);
        setSuggestions([]);
        setAutocompleteResults([]);
        setShowAutocomplete(false);
      }
    }, 300); // 300ms delay for faster response

    return () => clearTimeout(timeoutId);
  }, [input]);

  const validateIngredient = async (ingredient) => {
    setValidating(true);
    try {
      const response = await fetch('http://localhost:5000/api/recipes/validate-ingredient', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ingredient }),
      });

      const data = await response.json();
      
      if (response.ok) {
        setValidationResult(data.validation_result);
        setSuggestions(data.validation_result.suggestions || []);
      } else {
        setValidationResult(null);
        setSuggestions([]);
      }
    } catch (err) {
      setValidationResult(null);
      setSuggestions([]);
    } finally {
      setValidating(false);
    }
  };

  const handleAdd = () => {
    if (input.trim()) {
      // Use corrected ingredient if available, otherwise use original
      const ingredientToAdd = validationResult?.corrected || input.trim();
      onAdd(ingredientToAdd);
      setInput('');
      setValidationResult(null);
      setSuggestions([]);
    }
  };

  const getAutocompleteSuggestions = async (query) => {
    try {
      const response = await fetch(`http://localhost:5000/api/recipes/autocomplete?q=${encodeURIComponent(query)}&limit=8`);
      
      if (response.ok) {
        const data = await response.json();
        setAutocompleteResults(data.suggestions || []);
        setShowAutocomplete(data.suggestions && data.suggestions.length > 0);
      }
    } catch (err) {
      console.error('Autocomplete error:', err);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
    setValidationResult(null);
    setSuggestions([]);
    setAutocompleteResults([]);
    setShowAutocomplete(false);
  };

  const handleAutocompleteClick = (suggestion) => {
    setInput(suggestion.name);
    setValidationResult(null);
    setSuggestions([]);
    setAutocompleteResults([]);
    setShowAutocomplete(false);
  };

  const handleImageChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setImage(e.target.files[0]);
    }
  };

  const handleDetect = () => {
    if (image) onDetect(image);
  };

  return (
    <div className="ingredient-input-card">
      <div className="input-row">
        <label className="input-label image-label">
          <span role="img" aria-label="camera" className="label-icon">📷</span>
          Upload a photo of your fridge or pantry:
        </label>
        <input type="file" accept="image/*" onChange={handleImageChange} className="file-input" />
        <button className="detect-btn" onClick={handleDetect} disabled={!image || loading}>
          Detect Ingredients
        </button>
      </div>

            <div className="input-section">
        <label className="input-label text-label">
          <span role="img" aria-label="edit" className="label-icon">✏️</span>
          Or manually add an ingredient:
        </label>
        
        {/* Validation feedback above input - completely separate */}
        {validationResult && (
          <div className={`validation-feedback-above ${validationResult.is_valid ? 'valid' : 'invalid'}`}>
            {validationResult.is_valid ? (
              <span className="valid-icon">✓</span>
            ) : (
              <span className="invalid-icon">✗</span>
            )}
            {validationResult.corrected && validationResult.corrected !== validationResult.original && (
              <span className="correction">Did you mean: <strong>{validationResult.corrected}</strong>?</span>
            )}
            {autocompleteResults.length > 0 && (
              <span className="more-suggestions">(More suggestions available)</span>
            )}
          </div>
        )}
        
        <div className="input-row">
          <div className="input-container">
            <input
              className={`text-input ${validationResult ? (validationResult.is_valid ? 'valid' : 'invalid') : ''}`}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleAdd()}
              onFocus={() => setShowAutocomplete(autocompleteResults.length > 0)}
              onBlur={() => setTimeout(() => setShowAutocomplete(false), 200)}
              placeholder="e.g. tomato, tofu, paneer"
            />
            {validating && <div className="validating-indicator">Validating...</div>}
            
            {/* Autocomplete Dropdown */}
            {showAutocomplete && autocompleteResults.length > 0 && (
              <div className="autocomplete-dropdown">
                {autocompleteResults.map((suggestion, index) => (
                  <div
                    key={index}
                    className="autocomplete-item"
                    onClick={() => handleAutocompleteClick(suggestion)}
                  >
                    <span className="suggestion-name">{suggestion.name}</span>
                    {suggestion.category && suggestion.category !== 'unknown' && (
                      <span className="suggestion-category">{suggestion.category}</span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
          <button className="add-btn" onClick={handleAdd} disabled={!input.trim()}>Add</button>
        </div>
      </div>
      
      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="suggestions-container">
          <div className="suggestions-label">Did you mean:</div>
          <div className="suggestions-list">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                className="suggestion-btn"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default IngredientInput; 