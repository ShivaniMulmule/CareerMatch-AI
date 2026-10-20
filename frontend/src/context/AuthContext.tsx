import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';
import { authApi } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('careermatch_token'));
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem('careermatch_token');
      if (savedToken) {
        try {
          const currentUser = await authApi.getMe();
          setUser(currentUser);
          setToken(savedToken);
        } catch (err) {
          console.warn('Session expired or invalid token');
          localStorage.removeItem('careermatch_token');
          setUser(null);
          setToken(null);
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  const login = (newToken: string, newUser: User) => {
    localStorage.setItem('careermatch_token', newToken);
    setToken(newToken);
    setUser(newUser);
  };

  const logout = () => {
    localStorage.removeItem('careermatch_token');
    setToken(null);
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const updated = await authApi.getMe();
      setUser(updated);
    } catch (e) {
      console.error('Failed to refresh user:', e);
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
