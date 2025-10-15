import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './Navbar.css';

const Navbar = ({ onNewRecipe, onOpenAuthModal, onGoHome, currentMode }) => {
  const { user, isAuthenticated, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const dropdownRef = useRef(null);

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
      setDropdownOpen(!dropdownOpen);
    } else {
      onOpenAuthModal('login');
    }
  };

  const handleLogout = () => {
    logout();
    setDropdownOpen(false);
  };

  const handleProfileClick = () => {
    onOpenAuthModal('profile');
    setDropdownOpen(false);
    setMobileMenuOpen(false);
  };

  const handleMobileMenuToggle = () => {
    setMobileMenuOpen(!mobileMenuOpen);
    setDropdownOpen(false);
  };

  const handleMobileAuthClick = () => {
    if (isAuthenticated) {
      onOpenAuthModal('profile');
    } else {
      onOpenAuthModal('login');
    }
    setMobileMenuOpen(false);
  };

  const handleMobileLogout = () => {
    logout();
    setMobileMenuOpen(false);
  };

  // Close dropdown and mobile menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
      
      // Close mobile menu when clicking outside
      if (mobileMenuOpen && !event.target.closest('.navbar')) {
        setMobileMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [mobileMenuOpen]);

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
          
          <div className="dropdown-container" ref={dropdownRef}>
            <button 
              className="nav-link auth-link"
              onClick={handleAuthClick}
            >
              {isAuthenticated ? (
                <>
                  👤 {user?.username} {dropdownOpen ? '▲' : '▼'}
                </>
              ) : (
                <>
                  🔐 Sign In
                </>
              )}
            </button>
            
            {isAuthenticated && dropdownOpen && (
              <div className="dropdown-menu">
                <button 
                  className="dropdown-item"
                  onClick={handleProfileClick}
                >
                  ⚙️ Profile Settings
                </button>
                <button 
                  className="dropdown-item logout-item"
                  onClick={handleLogout}
                >
                  🚪 Logout
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Mobile Menu Button */}
        <div className="navbar-mobile">
          <button 
            className="mobile-menu-btn"
            onClick={handleMobileMenuToggle}
          >
            {mobileMenuOpen ? '✕' : '☰'}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="mobile-menu">
          <div className="mobile-menu-content">
            <button 
              className={`mobile-nav-link ${currentMode === 'initial' ? 'active' : ''}`}
              onClick={() => {
                handleHomeClick();
                setMobileMenuOpen(false);
              }}
            >
              🏠 Home
            </button>
            
            <button 
              className={`mobile-nav-link ${currentMode === 'adding' ? 'active' : ''}`}
              onClick={() => {
                handleNewRecipeClick();
                setMobileMenuOpen(false);
              }}
            >
              ➕ New Recipe
            </button>
            
            {isAuthenticated ? (
              <>
                <button 
                  className="mobile-nav-link"
                  onClick={handleMobileAuthClick}
                >
                  👤 {user?.username}
                </button>
                <button 
                  className="mobile-nav-link logout-link"
                  onClick={handleMobileLogout}
                >
                  🚪 Logout
                </button>
              </>
            ) : (
              <button 
                className="mobile-nav-link"
                onClick={handleMobileAuthClick}
              >
                🔐 Sign In
              </button>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
