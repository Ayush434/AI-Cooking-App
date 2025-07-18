import { useState } from 'react';
import './IngredientInput.css';

function IngredientInput({ onAdd, onDetect, loading }) {
  const [input, setInput] = useState('');
  const [image, setImage] = useState(null);

  const handleAdd = () => {
    if (input.trim()) {
      onAdd(input);
      setInput('');
    }
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

      <div className="input-row">
        <label className="input-label text-label">
          <span role="img" aria-label="edit" className="label-icon">✏️</span>
          Or manually add an ingredient:
        </label>
        <input
          className="text-input"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleAdd()}
          placeholder="e.g. tomato"
        />
        <button className="add-btn" onClick={handleAdd} disabled={!input.trim()}>Add</button>
      </div>
    </div>
  );
}

export default IngredientInput; 