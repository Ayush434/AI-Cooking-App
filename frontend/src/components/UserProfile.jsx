import React, { useState, useEffect } from 'react';
import './Auth.css';

const UserProfile = ({ user, onUpdateProfile, onLogout, loading }) => {
  const [formData, setFormData] = useState({
    dietary_preferences: '',
    allergies: '',
    favorite_cuisines: ''
  });
  const [errors, setErrors] = useState({});
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    if (user) {
      setFormData({
        dietary_preferences: (user.dietary_preferences || []).join(', '),
        allergies: (user.allergies || []).join(', '),
        favorite_cuisines: (user.favorite_cuisines || []).join(', ')
      });
    }
  }, [user]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
    // Clear success message
    if (successMessage) {
      setSuccessMessage('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // Convert comma-separated strings to arrays
      const updateData = {
        dietary_preferences: formData.dietary_preferences
          .split(',')
          .map(item => item.trim())
          .filter(item => item.length > 0),
        allergies: formData.allergies
          .split(',')
          .map(item => item.trim())
          .filter(item => item.length > 0),
        favorite_cuisines: formData.favorite_cuisines
          .split(',')
          .map(item => item.trim())
          .filter(item => item.length > 0)
      };

      await onUpdateProfile(updateData);
      setSuccessMessage('Profile updated successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (error) {
      setErrors({ general: error.message });
    }
  };

  if (!user) {
    return null;
  }

  return (
    <div className="auth-container">
      <div className="auth-card profile-card">
        <div className="auth-header">
          <h2>User Profile</h2>
          <p>Manage your preferences and settings</p>
        </div>

        <div className="profile-info">
          <div className="profile-field">
            <label>Username:</label>
            <span>{user.username}</span>
          </div>
          <div className="profile-field">
            <label>Email:</label>
            <span>{user.email}</span>
          </div>
          <div className="profile-field">
            <label>Member since:</label>
            <span>{new Date(user.created_at).toLocaleDateString()}</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {errors.general && (
            <div className="error-message general-error">
              {errors.general}
            </div>
          )}

          {successMessage && (
            <div className="success-message">
              {successMessage}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="dietary_preferences">Dietary Preferences</label>
            <textarea
              id="dietary_preferences"
              name="dietary_preferences"
              value={formData.dietary_preferences}
              onChange={handleChange}
              className={errors.dietary_preferences ? 'error' : ''}
              placeholder="e.g., vegetarian, gluten-free, low-carb"
              rows="3"
              disabled={loading}
            />
            <small className="form-help">
              Separate multiple preferences with commas
            </small>
            {errors.dietary_preferences && (
              <span className="error-message">{errors.dietary_preferences}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="allergies">Allergies</label>
            <textarea
              id="allergies"
              name="allergies"
              value={formData.allergies}
              onChange={handleChange}
              className={errors.allergies ? 'error' : ''}
              placeholder="e.g., nuts, dairy, shellfish"
              rows="3"
              disabled={loading}
            />
            <small className="form-help">
              Separate multiple allergies with commas
            </small>
            {errors.allergies && (
              <span className="error-message">{errors.allergies}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="favorite_cuisines">Favorite Cuisines</label>
            <textarea
              id="favorite_cuisines"
              name="favorite_cuisines"
              value={formData.favorite_cuisines}
              onChange={handleChange}
              className={errors.favorite_cuisines ? 'error' : ''}
              placeholder="e.g., Italian, Asian, Mexican, Mediterranean"
              rows="3"
              disabled={loading}
            />
            <small className="form-help">
              Separate multiple cuisines with commas
            </small>
            {errors.favorite_cuisines && (
              <span className="error-message">{errors.favorite_cuisines}</span>
            )}
          </div>

          <div className="profile-actions">
            <button
              type="submit"
              className="auth-button primary"
              disabled={loading}
            >
              {loading ? 'Updating...' : 'Update Profile'}
            </button>
            
            <button
              type="button"
              className="auth-button secondary"
              onClick={onLogout}
              disabled={loading}
            >
              Logout
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UserProfile;
