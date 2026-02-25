/**
 * useAuth hook
 * Custom hook for authentication state management with Better Auth integration
 */

'use client';

import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { authClient } from '@/lib/auth-client';

interface User {
  id: string | number;
  name: string;
  email: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  loading: boolean;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

/**
 * AuthProvider component
 * Wraps the app to provide authentication context using Better Auth
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Check authentication status using Better Auth session
  const checkAuth = async () => {
    try {
      const session = await authClient.getSession();

      if (session?.data?.user) {
        setIsAuthenticated(true);
        setUser({
          id: session.data.user.id,
          name: session.data.user.name,
          email: session.data.user.email,
        });
      } else {
        setIsAuthenticated(false);
        setUser(null);
      }
    } catch (error) {
      console.error('Failed to check auth status:', error);
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  // Check authentication status on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const logout = async () => {
    try {
      // Call Better Auth signOut to clear JWT token from httpOnly cookie
      await authClient.signOut();

      setIsAuthenticated(false);
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
      // Even if logout fails, clear local state for security
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  const refreshSession = async () => {
    setLoading(true);
    await checkAuth();
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        user,
        loading,
        logout,
        refreshSession
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

/**
 * useAuth hook
 * Access authentication state and methods
 *
 * Note: Login and signup are handled directly in their respective forms
 * using Better Auth's signIn.email and signUp.email methods.
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
