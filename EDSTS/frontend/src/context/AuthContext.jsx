import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('edsts_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('edsts_token') || null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          const freshUser = await api.getCurrentUser();
          setUser(freshUser);
          localStorage.setItem('edsts_user', JSON.stringify(freshUser));
        } catch (err) {
          logout();
        }
      }
      setLoading(false);
    };
    checkAuth();
  }, [token]);

  const login = async (email, password) => {
    const res = await api.login(email, password);
    setToken(res.access_token);
    setUser(res.user);
    localStorage.setItem('edsts_token', res.access_token);
    localStorage.setItem('edsts_user', JSON.stringify(res.user));
    return res.user;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('edsts_token');
    localStorage.removeItem('edsts_user');
  };

  const roles = user?.roles || [];
  const isAdmin = roles.includes('ADMIN');
  const isManager = roles.includes('MANAGER');
  const isEmployee = roles.includes('EMPLOYEE');

  const hasRole = (role) => {
    if (isAdmin) return true; // Superuser override
    return roles.includes(role);
  };

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    isAdmin,
    isManager,
    isEmployee,
    hasRole,
    roles,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
