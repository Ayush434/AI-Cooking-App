import { useState, useEffect, useRef } from 'react';
import './IngredientInput.css';
import config from '../config';

function IngredientInput({ onAdd, onDetect, loading }) {
  const [input, setInput] = useState('');
  const [image, setImage] = useState(null);
  const [validationResult, setValidationResult] = useState(null);
  const [validating, setValidating] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [autocompleteResults, setAutocompleteResults] = useState([]);
  const [showAutocomplete, setShowAutocomplete] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);

  // Check screen size on mount and resize
  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth <= 600);
    };
    
    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  // Click outside handler for mobile
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target) && 
          inputRef.current && !inputRef.current.contains(event.target)) {
        setShowAutocomplete(false);
      }
    };

    // Add touchstart for mobile devices
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('touchstart', handleClickOutside);
    
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('touchstart', handleClickOutside);
    };
  }, []);

  // Handle body scroll prevention on mobile when dropdown is open
  useEffect(() => {
    if (showAutocomplete && window.innerWidth <= 600) {
      document.body.classList.add('dropdown-open');
    } else {
      document.body.classList.remove('dropdown-open');
    }

    return () => {
      document.body.classList.remove('dropdown-open');
    };
  }, [showAutocomplete]);

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
      const response = await fetch(`${config.API_BASE_URL}${config.ENDPOINTS.VALIDATE_INGREDIENT}`, {
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
      const response = await fetch(`${config.API_BASE_URL}${config.ENDPOINTS.AUTOCOMPLETE}?q=${encodeURIComponent(query)}&limit=8`);
      
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
        
        {/* Validation feedback above everything - completely separate */}
        {validationResult && (
          <div className="validation-above">
            <div className={`validation-box ${validationResult.is_valid ? 'valid' : 'invalid'}`}>
              {validationResult.is_valid ? (
                <span className="valid-icon">✓</span>
              ) : (
                <span className="invalid-icon">✗</span>
              )}
              {validationResult.corrected && validationResult.corrected !== validationResult.original && (
                <span className="correction">Did you mean: <strong>{validationResult.corrected}</strong>?</span>
              )}
            </div>
          </div>
        )}
        
        {/* Suggestions - moved above input */}
        {suggestions.length > 0 && (
          <div className="suggestions-above">
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
          </div>
        )}
        
        <div className="input-row">
          <div className="input-container">
            <input
              ref={inputRef}
              className={`text-input ${validationResult ? (validationResult.is_valid ? 'valid' : 'invalid') : ''}`}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleAdd()}
              onFocus={() => setShowAutocomplete(autocompleteResults.length > 0)}
              onBlur={() => setTimeout(() => setShowAutocomplete(false), 200)}
              placeholder="e.g. tomato, tofu, paneer"
            />
            {validating && <div className="validating-indicator">Validating...</div>}
            
            {/* Autocomplete Dropdown - below input */}
            {showAutocomplete && autocompleteResults.length > 0 && (
              <div ref={dropdownRef} className="autocomplete-dropdown">
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
          <button className="add-btn" onClick={handleAdd} disabled={!input.trim()}>
            {!isMobile ? 'Add' : ''}
          </button>
        </div>
      </div>
    </div>
  );
}

export default IngredientInput; 