/**
 * SignupForm component
 * Client component for user registration with Better Auth integration
 */

'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { isValidEmail, isValidPassword } from '@/lib/utils';
import { authClient } from '@/lib/auth-client';
import { useAuth } from '@/hooks/useAuth';

export function SignupForm() {
  const router = useRouter();
  const { refreshSession } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Name validation
    if (!name) {
      newErrors.name = 'Name is required';
    } else if (name.length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    }

    // Email validation
    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!isValidEmail(email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!password) {
      newErrors.password = 'Password is required';
    } else if (!isValidPassword(password)) {
      newErrors.password = 'Password must be at least 8 characters';
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
      // Call Better Auth signup API
      const result = await authClient.signUp.email({
        email,
        password,
        name,
      });

      if (result.error) {
        // Handle Better Auth errors
        const errorCode = result.error.code || result.error.message || '';

        if (errorCode.includes('email') || errorCode.includes('EMAIL_ALREADY_EXISTS')) {
          setErrors({ email: 'Email already registered' });
        } else if (errorCode.includes('VALIDATION_ERROR')) {
          setErrors({ form: 'Please check your input and try again.' });
        } else {
          setErrors({ form: result.error.message || 'Signup failed. Please try again.' });
        }
        return;
      }

      // Successful signup - JWT token is automatically stored in httpOnly cookie
      // Refresh session to update AuthProvider state with user data
      await refreshSession();

      // Redirect to dashboard
      router.push('/dashboard');
    } catch (error: any) {
      // Handle network or unexpected errors
      console.error('Signup error:', error);
      setErrors({ form: 'An unexpected error occurred. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mt-8 space-y-6">
      <div className="space-y-4">
        <Input
          label="Full name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          error={errors.name}
          placeholder="John Doe"
          autoComplete="name"
          disabled={isSubmitting}
        />

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
          autoComplete="new-password"
          disabled={isSubmitting}
        />
        {password && password.length > 0 && password.length < 8 && (
          <p className="text-xs text-gray-500 mt-1">
            Password strength: {password.length}/8 characters minimum
          </p>
        )}
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
        {isSubmitting ? 'Creating account...' : 'Create account'}
      </Button>
    </form>
  );
}
