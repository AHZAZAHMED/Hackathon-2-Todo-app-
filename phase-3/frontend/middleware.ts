// import { NextResponse } from 'next/server';
// import type { NextRequest } from 'next/server';
// import { auth } from '@/lib/auth';

// // Force Node.js runtime (required for Better Auth with pg/Kysely database adapter)
// export const runtime = 'nodejs';

// export async function middleware(request: NextRequest) {
//   // Check authentication state using Better Auth
//   const session = await auth.api.getSession({
//     headers: request.headers,
//   });

//   const isAuthenticated = !!session?.user;
//   const isAuthPage = request.nextUrl.pathname.startsWith('/login') ||
//                      request.nextUrl.pathname.startsWith('/signup');
//   const isProtectedPage = request.nextUrl.pathname.startsWith('/dashboard') ||
//                           request.nextUrl.pathname.startsWith('/tasks');

//   // Redirect unauthenticated users to login for protected pages
//   if (isProtectedPage && !isAuthenticated) {
//     const redirectUrl = new URL('/login', request.url);
//     redirectUrl.searchParams.set('redirect', request.nextUrl.pathname);
//     return NextResponse.redirect(redirectUrl);
//   }

//   // Redirect authenticated users away from auth pages to dashboard
//   if (isAuthPage && isAuthenticated) {
//     return NextResponse.redirect(new URL('/dashboard', request.url));
//   }

//   return NextResponse.next();
// }

// // Configure which routes the middleware should run on
// export const config = {
//   matcher: [
//     '/dashboard/:path*',
//     '/tasks/:path*',
//     '/login',
//     '/signup',
//   ],
// };
