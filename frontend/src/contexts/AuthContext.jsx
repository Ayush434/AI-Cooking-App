import React, { createContext, useContext, useState, useEffect } from 'react';
import config from '../config';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authLoading, setAuthLoading] = useState(false);

  // Check if user is logged in on app start
  useEffect(() => {
    const checkAuthStatus = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const response = await fetch(`${config.API_BASE_URL}/api/auth/profile`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });

          if (response.ok) {
            const data = await response.json();
            setUser(data.user);
          } else {
            // Token is invalid, remove it
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
          }
        } catch (error) {
          console.error('Auth check failed:', error);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      setLoading(false);
    };

    checkAuthStatus();
  }, []);

  const login = async (credentials) => {
    setAuthLoading(true);
    try {
      const response = await fetch(`${config.API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(credentials)
      });

      const data = await response.json();

      if (response.ok) {
        const { tokens } = data;
        localStorage.setItem('access_token', tokens.access_token);
        localStorage.setItem('refresh_token', tokens.refresh_token);
        setUser(tokens.user);
        return { success: true, message: data.message };
      } else {
        throw new Error(data.error || 'Login failed');
      }
    } catch (error) {
      throw error;
    } finally {
      setAuthLoading(false);
    }
  };

  const register = async (userData) => {
    setAuthLoading(true);
    try {
      const response = await fetch(`${config.API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      });

      const data = await response.json();

      if (response.ok) {
        const { tokens } = data;
        localStorage.setItem('access_token', tokens.access_token);
        localStorage.setItem('refresh_token', tokens.refresh_token);
        setUser(tokens.user);
        return { success: true, message: data.message };
      } else {
        throw new Error(data.error || 'Registration failed');
      }
    } catch (error) {
      throw error;
    } finally {
      setAuthLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    // Clear app state on logout
    localStorage.removeItem('app_ingredients');
    localStorage.removeItem('app_recipes');
    localStorage.removeItem('app_mode');
    localStorage.removeItem('app_dietary_preferences');
    localStorage.removeItem('app_serving_size');
    localStorage.removeItem('app_random_ingredients');
    setUser(null);
  };

  const updateProfile = async (profileData) => {
    setAuthLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${config.API_BASE_URL}/api/auth/profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(profileData)
      });

      const data = await response.json();

      if (response.ok) {
        setUser(data.user);
        return { success: true, message: data.message };
      } else {
        throw new Error(data.error || 'Profile update failed');
      }
    } catch (error) {
      throw error;
    } finally {
      setAuthLoading(false);
    }
  };

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await fetch(`${config.API_BASE_URL}/api/auth/refresh`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${refreshToken}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('access_token', data.access_token);
        return data.access_token;
      } else {
        throw new Error('Token refresh failed');
      }
    } catch (error) {
      logout();
      throw error;
    }
  };

  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  };

  const value = {
    user,
    loading,
    authLoading,
    login,
    register,
    logout,
    updateProfile,
    refreshToken,
    getAuthHeaders,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
