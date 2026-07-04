/**
 * AuthContext.jsx
 * Location: frontend/src/contexts/AuthContext.jsx
 *
 * Provides global authentication state to the entire app.
 * Features:
 * - Stores user, access token, refresh token
 * - Persists to localStorage (survives page reload)
 * - Role-based redirect after login (admin → /admin, teacher → /teacher, student → /student)
 * - Logout clears everything and redirects to /login
 */
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../api/services';

const AuthContext = createContext(null);

// Custom hook — components call useAuth() instead of useContext(AuthContext)
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used inside <AuthProvider>');
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // true while restoring session
  const navigate = useNavigate();

  // ── Restore session from localStorage on app start ──────────
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    const accessToken = localStorage.getItem('accessToken');

    if (storedUser && accessToken) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  // ── LOGIN ────────────────────────────────────────────────────
  const login = useCallback(async (email, password) => {
    const response = await authService.login({ email, password });
    const { access, refresh, user: userData } = response.data;

    // Persist tokens and user to localStorage
    localStorage.setItem('accessToken', access);
    localStorage.setItem('refreshToken', refresh);
    localStorage.setItem('user', JSON.stringify(userData));

    setUser(userData);

    // Role-based redirect
    const role = userData?.role;
    if (role === 'admin') navigate('/admin', { replace: true });
    else if (role === 'teacher') navigate('/teacher', { replace: true });
    else if (role === 'student') navigate('/student', { replace: true });
    else navigate('/', { replace: true });

    return userData;
  }, [navigate]);

  // ── LOGOUT ───────────────────────────────────────────────────
  const logout = useCallback(async () => {
    const refreshToken = localStorage.getItem('refreshToken');
    try {
      if (refreshToken) await authService.logout(refreshToken);
    } catch (_) {
      // Even if backend call fails, clear client state
    }
    localStorage.clear();
    setUser(null);
    navigate('/login', { replace: true });
  }, [navigate]);

  // ── UPDATE USER (after profile edit) ─────────────────────────
  const updateUser = useCallback((updatedData) => {
    const updated = { ...user, ...updatedData };
    setUser(updated);
    localStorage.setItem('user', JSON.stringify(updated));
  }, [user]);

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    logout,
    updateUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
