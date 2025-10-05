import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import './Navbar.css';

const Navbar = ({ onNewRecipe, onOpenAuthModal, onGoHome, currentMode }) => {
  const { user, isAuthenticated } = useAuth();

  const handleHomeClick = () => {
    // Scroll to top and reset to home state
    window.scrollTo({ top: 0, behavior: 'smooth' });
    onGoHome();
  };

  const handleNewRecipeClick = () => {
    onNewRecipe();
  };

  const handleAuthClick = () => {
    if (isAuthenticated) {
      onOpenAuthModal('profile');
    } else {
      onOpenAuthModal('login');
    }
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Logo/Brand */}
        <div className="navbar-brand">
          <h2>🍳 SnackHack</h2>
        </div>

        {/* Navigation Links */}
        <div className="navbar-links">
          <button 
            className={`nav-link ${currentMode === 'initial' ? 'active' : ''}`}
            onClick={handleHomeClick}
          >
            🏠 Home
          </button>
          
          <button 
            className={`nav-link ${currentMode === 'adding' ? 'active' : ''}`}
            onClick={handleNewRecipeClick}
          >
            ➕ New Recipe
          </button>
          
          <button 
            className="nav-link auth-link"
            onClick={handleAuthClick}
          >
            {isAuthenticated ? (
              <>
                👤 {user?.username}
              </>
            ) : (
              <>
                🔐 Sign In
              </>
            )}
          </button>
        </div>

        {/* Mobile Menu Button */}
        <div className="navbar-mobile">
          <button className="mobile-menu-btn">
            ☰
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
