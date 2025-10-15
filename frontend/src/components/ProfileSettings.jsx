import React, { useState, useEffect } from 'react';
import './Auth.css';

const ProfileSettings = ({ user, onUpdateProfile, onLogout, loading }) => {
  const [activeTab, setActiveTab] = useState('account'); // 'account', 'password', 'preferences'
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    dietary_preferences: '',
    allergies: '',
    favorite_cuisines: ''
  });
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [errors, setErrors] = useState({});
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username || '',
        email: user.email || '',
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

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({
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

  const handleAccountUpdate = async (e) => {
    e.preventDefault();
    
    try {
      // Convert comma-separated strings to arrays for preferences
      const updateData = {
        username: formData.username,
        email: formData.email,
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
      setSuccessMessage('Account information updated successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (error) {
      setErrors({ general: error.message });
    }
  };

  const handlePasswordUpdate = async (e) => {
    e.preventDefault();
    
    // Validate passwords match
    if (passwordData.new_password !== passwordData.confirm_password) {
      setErrors({ confirm_password: 'Passwords do not match' });
      return;
    }

    // Validate password strength
    if (passwordData.new_password.length < 6) {
      setErrors({ new_password: 'Password must be at least 6 characters long' });
      return;
    }

    try {
      await onUpdateProfile({
        current_password: passwordData.current_password,
        new_password: passwordData.new_password
      });
      setSuccessMessage('Password updated successfully!');
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
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
      <div className="auth-card profile-settings-card">
        <div className="auth-header">
          <h2>Profile Settings</h2>
          <p>Manage your account information and preferences</p>
        </div>

        {/* Tab Navigation */}
        <div className="profile-tabs">
          <button 
            className={`tab-button ${activeTab === 'account' ? 'active' : ''}`}
            onClick={() => setActiveTab('account')}
          >
            👤 Account Info
          </button>
          <button 
            className={`tab-button ${activeTab === 'password' ? 'active' : ''}`}
            onClick={() => setActiveTab('password')}
          >
            🔒 Password
          </button>
          <button 
            className={`tab-button ${activeTab === 'preferences' ? 'active' : ''}`}
            onClick={() => setActiveTab('preferences')}
          >
            ⚙️ Preferences
          </button>
        </div>

        {/* Success/Error Messages */}
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

        {/* Account Information Tab */}
        {activeTab === 'account' && (
          <form onSubmit={handleAccountUpdate} className="auth-form">
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className={errors.username ? 'error' : ''}
                placeholder="Enter your username"
                disabled={loading}
                required
              />
              {errors.username && (
                <span className="error-message">{errors.username}</span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className={errors.email ? 'error' : ''}
                placeholder="Enter your email"
                disabled={loading}
                required
              />
              {errors.email && (
                <span className="error-message">{errors.email}</span>
              )}
            </div>

            <div className="profile-info">
              <div className="profile-field">
                <label>Member since:</label>
                <span>{new Date(user.created_at).toLocaleDateString()}</span>
              </div>
            </div>

            <div className="profile-actions">
              <button
                type="submit"
                className="auth-button primary"
                disabled={loading}
              >
                {loading ? 'Updating...' : 'Update Account'}
              </button>
            </div>
          </form>
        )}

        {/* Password Change Tab */}
        {activeTab === 'password' && (
          <form onSubmit={handlePasswordUpdate} className="auth-form">
            <div className="form-group">
              <label htmlFor="current_password">Current Password</label>
              <input
                type="password"
                id="current_password"
                name="current_password"
                value={passwordData.current_password}
                onChange={handlePasswordChange}
                className={errors.current_password ? 'error' : ''}
                placeholder="Enter your current password"
                disabled={loading}
                required
              />
              {errors.current_password && (
                <span className="error-message">{errors.current_password}</span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="new_password">New Password</label>
              <input
                type="password"
                id="new_password"
                name="new_password"
                value={passwordData.new_password}
                onChange={handlePasswordChange}
                className={errors.new_password ? 'error' : ''}
                placeholder="Enter your new password"
                disabled={loading}
                required
              />
              <small className="form-help">
                Password must be at least 6 characters long
              </small>
              {errors.new_password && (
                <span className="error-message">{errors.new_password}</span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="confirm_password">Confirm New Password</label>
              <input
                type="password"
                id="confirm_password"
                name="confirm_password"
                value={passwordData.confirm_password}
                onChange={handlePasswordChange}
                className={errors.confirm_password ? 'error' : ''}
                placeholder="Confirm your new password"
                disabled={loading}
                required
              />
              {errors.confirm_password && (
                <span className="error-message">{errors.confirm_password}</span>
              )}
            </div>

            <div className="profile-actions">
              <button
                type="submit"
                className="auth-button primary"
                disabled={loading}
              >
                {loading ? 'Updating...' : 'Change Password'}
              </button>
            </div>
          </form>
        )}

        {/* Preferences Tab */}
        {activeTab === 'preferences' && (
          <form onSubmit={handleAccountUpdate} className="auth-form">
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
                {loading ? 'Updating...' : 'Update Preferences'}
              </button>
            </div>
          </form>
        )}

        {/* Logout Button */}
        <div className="profile-actions logout-section">
          <button
            type="button"
            className="auth-button secondary logout-button"
            onClick={onLogout}
            disabled={loading}
          >
            🚪 Logout
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProfileSettings;
