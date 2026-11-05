import React, { createContext, useContext, useEffect, useState } from 'react';
import { AuthContextType, User } from '../types/auth';
import { AUTH_TOKEN_KEY, getCurrentUser } from '../lib/api';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const logout = () => {
    sessionStorage.removeItem(AUTH_TOKEN_KEY);
    setToken(null);
    setUser(null);
  };

  const login = (newToken: string, newUser: User) => {
    sessionStorage.setItem(AUTH_TOKEN_KEY, newToken);
    setToken(newToken);
    setUser(newUser);
  };

  const refreshUser = async () => {
    try {
      const currentUser = await getCurrentUser();
      setUser(currentUser);
    } catch {
      logout();
    }
  };

  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = sessionStorage.getItem(AUTH_TOKEN_KEY);
      if (storedToken) {
        setToken(storedToken);
        try {
          const currentUser = await getCurrentUser();
          setUser(currentUser);
        } catch {
          // Token expired or invalid
          sessionStorage.removeItem(AUTH_TOKEN_KEY);
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user && !!token,
        isLoading,
        login,
        logout,
        refreshUser,
      }}
    >
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
