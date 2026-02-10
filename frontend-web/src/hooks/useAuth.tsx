'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import {
  UserSession,
  getSession,
  saveSession,
  clearSession,
  getExpiryTimestamp,
} from '@/lib/utils/sessionStorage';
import { authApi } from '@/lib/api/auth';
import { ApiError } from '@/lib/api/errors';

interface AuthContextType {
  user: UserSession['user'] | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (formData: string, rememberMe: boolean) => Promise<any>;
  login2FA: (data: { pre_auth_token: string; code: string }, rememberMe: boolean) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserSession['user'] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check for existing session on mount
    const session = getSession();
    if (session) {
      setUser(session.user);
    }
    setIsLoading(false);
  }, []);

  const login = async (formData: string, rememberMe: boolean) => {
    setIsLoading(true);
    try {
      const result = await authApi.login(formData);

      if (result.pre_auth_token) {
        return result; // 2FA Required
      }

      const session: UserSession = {
        user: {
          id: 'current', // Ideally from a user profile API call
          email: '', // Map from result if available
          name: 'User',
        },
        token: result.access_token,
        expiresAt: getExpiryTimestamp(),
      };

      saveSession(session, rememberMe);
      setUser(session.user);
      router.push('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const login2FA = async (data: { pre_auth_token: string; code: string }, rememberMe: boolean) => {
    setIsLoading(true);
    try {
      const result = await authApi.login2FA(data);

      const session: UserSession = {
        user: {
          id: 'current',
          email: '',
          name: 'User',
        },
        token: result.access_token,
        expiresAt: getExpiryTimestamp(),
      };

      saveSession(session, rememberMe);
      setUser(session.user);
      router.push('/dashboard');
    } catch (error) {
      console.error('2FA verification failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    clearSession();
    setUser(null);
    router.push('/login');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        login2FA,
        logout,
      }}
    >
      {!isLoading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
