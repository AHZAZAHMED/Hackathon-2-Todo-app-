/**
 * User entity types
 * Represents a user in the application
 */

export interface User {
  id: string;
  name: string;
  email: string;
}

/**
 * Input type for user signup
 */
export interface SignupInput {
  name: string;
  email: string;
  password: string;
}

/**
 * Input type for user login
 */
export interface LoginInput {
  email: string;
  password: string;
}
