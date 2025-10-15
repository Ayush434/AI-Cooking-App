import React, { useState, useEffect } from 'react';
import Login from './Login';
import Register from './Register';
import ProfileSettings from './ProfileSettings';
import { useAuth } from '../contexts/AuthContext';

const AuthModal = ({ isOpen, onClose, authMode: initialAuthMode = 'login' }) => {
  const [authMode, setAuthMode] = useState(initialAuthMode); // 'login', 'register', 'profile'
  const { user, login, register, logout, updateProfile, authLoading } = useAuth();

  // Update authMode when prop changes
  useEffect(() => {
    setAuthMode(initialAuthMode);
  }, [initialAuthMode]);

  const handleLogin = async (credentials) => {
    try {
      await login(credentials);
      onClose();
    } catch (error) {
      throw error;
    }
  };

  const handleRegister = async (userData) => {
    try {
      await register(userData);
      onClose();
    } catch (error) {
      throw error;
    }
  };

  const handleUpdateProfile = async (profileData) => {
    try {
      await updateProfile(profileData);
    } catch (error) {
      throw error;
    }
  };

  const handleLogout = () => {
    logout();
    setAuthMode('login');
    onClose();
  };

  const switchToLogin = () => setAuthMode('login');
  const switchToRegister = () => setAuthMode('register');
  const switchToProfile = () => setAuthMode('profile');

  if (!isOpen) return null;

  return (
    <div className="auth-modal-overlay" onClick={onClose}>
      <div className="auth-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="auth-modal-header">
          <h2>
            {authMode === 'login' && 'Sign In'}
            {authMode === 'register' && 'Create Account'}
            {authMode === 'profile' && 'Profile Settings'}
          </h2>
          <button className="auth-modal-close" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="auth-modal-body">
          {authMode === 'login' && (
            <Login
              onLogin={handleLogin}
              onSwitchToRegister={switchToRegister}
              loading={authLoading}
            />
          )}

          {authMode === 'register' && (
            <Register
              onRegister={handleRegister}
              onSwitchToLogin={switchToLogin}
              loading={authLoading}
            />
          )}

          {authMode === 'profile' && user && (
            <ProfileSettings
              user={user}
              onUpdateProfile={handleUpdateProfile}
              onLogout={handleLogout}
              loading={authLoading}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthModal;
