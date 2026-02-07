/**
 * AuthProvider wrapper component
 * Client component wrapper for authentication context
 */

'use client';

import { AuthProvider as AuthContextProvider } from '@/hooks/useAuth';
import { ReactNode } from 'react';

export function AuthProvider({ children }: { children: ReactNode }) {
  return <AuthContextProvider>{children}</AuthContextProvider>;
}
