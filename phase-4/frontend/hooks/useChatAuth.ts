// frontend/hooks/useChatAuth.ts
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authClient } from '@/lib/auth-client';

export function useChatAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check authentication state using Better Auth client
    const checkAuth = async () => {
      try {
        const session = await authClient.getSession();
        setIsAuthenticated(!!session?.data?.user);
      } catch (error) {
        console.error('Chat auth check failed:', error);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  /**
   * Redirect to login page, preserving current URL for return
   */
  const redirectToLogin = () => {
    const currentPath = window.location.pathname;
    router.push(`/login?returnUrl=${encodeURIComponent(currentPath)}`);
  };

  /**
   * Handle post-login return
   */
  const handlePostLoginReturn = () => {
    const params = new URLSearchParams(window.location.search);
    const returnUrl = params.get('returnUrl');

    if (returnUrl) {
      router.push(returnUrl);
    }
  };

  return {
    isAuthenticated,
    isLoading,
    redirectToLogin,
    handlePostLoginReturn,
  };
}
