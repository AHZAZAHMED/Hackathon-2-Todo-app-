/**
 * Auth types
 * Represents authentication state and responses
 */

import { User } from './user';

/**
 * Authentication state
 */
export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
}

/**
 * Authentication response from API
 */
export interface AuthResponse {
  user: User;
  token: string;
}
