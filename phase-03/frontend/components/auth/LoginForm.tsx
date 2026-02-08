/**
 * LoginForm component
 * Client component for user login with Better Auth integration
 */

'use client';

import { useState, FormEvent, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { isValidEmail } from '@/lib/utils';
import { authClient } from '@/lib/auth-client';

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Get redirect URL from query params for session restoration
  const redirectUrl = searchParams.get('redirect') || '/dashboard';

  // Check if there's a stored redirect URL from session restoration
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const storedRedirect = sessionStorage.getItem('redirectAfterLogin');
      if (storedRedirect) {
        sessionStorage.removeItem('redirectAfterLogin');
      }
    }
  }, []);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Email validation
    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!isValidEmail(email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!password) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      // Call Better Auth login API
      const result = await authClient.signIn.email({
        email,
        password,
      });

      if (result.error) {
        // Handle Better Auth errors
        const errorMessage = result.error.message || '';
        const errorCode = result.error.code || '';

        // Check for rate limiting (429)
        if (errorCode.includes('RATE_LIMIT') || errorCode.includes('429')) {
          setErrors({ form: errorMessage || 'Too many failed attempts. Please try again later.' });
        } else if (errorCode.includes('INVALID_CREDENTIALS') || errorMessage.includes('Invalid')) {
          setErrors({ form: 'Invalid email or password' });
        } else {
          setErrors({ form: errorMessage || 'Login failed. Please try again.' });
        }
        return;
      }

      // Successful login - JWT token is automatically stored in httpOnly cookie
      // Redirect to original URL or dashboard
      router.push(redirectUrl);
    } catch (error: any) {
      // Handle network or unexpected errors
      console.error('Login error:', error);
      setErrors({ form: 'An unexpected error occurred. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mt-8 space-y-6">
      <div className="space-y-4">
        <Input
          label="Email address"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={errors.email}
          placeholder="you@example.com"
          autoComplete="email"
          disabled={isSubmitting}
        />

        <Input
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={errors.password}
          placeholder="••••••••"
          autoComplete="current-password"
          disabled={isSubmitting}
        />
      </div>

      {errors.form && (
        <div className="rounded-md bg-red-50 p-4">
          <p className="text-sm text-red-800">{errors.form}</p>
        </div>
      )}

      <Button
        type="submit"
        variant="primary"
        size="lg"
        className="w-full"
        disabled={isSubmitting}
      >
        {isSubmitting ? 'Signing in...' : 'Sign in'}
      </Button>
    </form>
  );
}
