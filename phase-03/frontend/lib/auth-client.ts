/**
 * Better Auth Client
 * Client-side authentication SDK for browser usage
 *
 * IMPORTANT: This is for CLIENT COMPONENTS only.
 * Server Components and API routes should use lib/auth.ts
 */

import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
});

export const { signIn, signUp, signOut, useSession } = authClient;
