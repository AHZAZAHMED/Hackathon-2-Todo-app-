import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import jwt from 'jsonwebtoken';

/**
 * API route to exchange Better Auth session for JWT token
 * GET /api/auth/token
 *
 * Returns a JWT token containing user claims from the current session
 */
export async function GET(request: NextRequest) {
  try {
    // Get current session from Better Auth
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    if (!session?.user) {
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      );
    }

    // Generate JWT token with user claims
    const token = jwt.sign(
      {
        user_id: session.user.id,
        email: session.user.email,
        name: session.user.name || session.user.email,
        iat: Math.floor(Date.now() / 1000),
        exp: Math.floor(Date.now() / 1000) + (60 * 60 * 24), // 24 hours
      },
      process.env.BETTER_AUTH_SECRET!,
      { algorithm: 'HS256' }
    );

    return NextResponse.json({ token });
  } catch (error) {
    console.error('Token generation error:', error);
    return NextResponse.json(
      { error: 'Failed to generate token' },
      { status: 500 }
    );
  }
}
