import React, { useState } from 'react';
import Login from './Login';
import Register from './Register';
import UserProfile from './UserProfile';
import { useAuth } from '../contexts/AuthContext';

const AuthModal = ({ isOpen, onClose }) => {
  const [authMode, setAuthMode] = useState('login'); // 'login', 'register', 'profile'
  const { user, login, register, logout, updateProfile, authLoading } = useAuth();

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
            {authMode === 'profile' && 'User Profile'}
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
            <UserProfile
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
