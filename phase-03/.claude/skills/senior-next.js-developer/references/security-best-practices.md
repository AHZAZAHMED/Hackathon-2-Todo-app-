# Next.js Security Best Practices

## Authentication Implementation

### NextAuth.js Setup

**Installation**
```bash
npm install next-auth
```

**Basic Configuration**
```typescript
// app/api/auth/[...nextauth]/route.ts
import NextAuth from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { compare } from 'bcrypt'

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        const user = await getUserByEmail(credentials.email)
        if (!user) {
          return null
        }

        const isPasswordValid = await compare(credentials.password, user.password)
        if (!isPasswordValid) {
          return null
        }

        return {
          id: user.id,
          email: user.email,
          name: user.name,
        }
      }
    })
  ],
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  pages: {
    signIn: '/login',
    error: '/auth/error',
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
      }
      return token
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string
      }
      return session
    }
  }
})

export { handler as GET, handler as POST }
```

**Session Provider**
```typescript
// app/providers.tsx
'use client'

import { SessionProvider } from 'next-auth/react'

export function Providers({ children }: { children: React.ReactNode }) {
  return <SessionProvider>{children}</SessionProvider>
}

// app/layout.tsx
import { Providers } from './providers'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
```

**Protected Routes (Server Component)**
```typescript
// app/dashboard/page.tsx
import { getServerSession } from 'next-auth'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const session = await getServerSession()

  if (!session) {
    redirect('/login')
  }

  return <Dashboard user={session.user} />
}
```

**Protected Routes (Client Component)**
```typescript
'use client'

import { useSession } from 'next-auth/react'
import { redirect } from 'next/navigation'

export default function DashboardPage() {
  const { data: session, status } = useSession({
    required: true,
    onUnauthenticated() {
      redirect('/login')
    }
  })

  if (status === 'loading') {
    return <Spinner />
  }

  return <Dashboard user={session.user} />
}
```

### Custom JWT Authentication

**Token Generation**
```typescript
// lib/auth/jwt.ts
import jwt from 'jsonwebtoken'

const JWT_SECRET = process.env.JWT_SECRET!
const JWT_EXPIRES_IN = '7d'

export function generateToken(payload: { userId: string; email: string }) {
  return jwt.sign(payload, JWT_SECRET, {
    expiresIn: JWT_EXPIRES_IN,
    issuer: 'your-app',
    audience: 'your-app-users',
  })
}

export function verifyToken(token: string) {
  try {
    return jwt.verify(token, JWT_SECRET, {
      issuer: 'your-app',
      audience: 'your-app-users',
    })
  } catch (error) {
    return null
  }
}
```

**Authentication Middleware**
```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { verifyToken } from '@/lib/auth/jwt'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token')?.value

  // Protected routes
  if (request.nextUrl.pathname.startsWith('/dashboard')) {
    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url))
    }

    const payload = verifyToken(token)
    if (!payload) {
      return NextResponse.redirect(new URL('/login', request.url))
    }

    // Add user info to headers for server components
    const requestHeaders = new Headers(request.headers)
    requestHeaders.set('x-user-id', payload.userId)

    return NextResponse.next({
      request: {
        headers: requestHeaders,
      }
    })
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/protected/:path*']
}
```

**API Route Protection**
```typescript
// lib/auth/api-auth.ts
import { NextRequest } from 'next/server'
import { verifyToken } from './jwt'

export async function authenticateRequest(request: NextRequest) {
  const authHeader = request.headers.get('authorization')

  if (!authHeader?.startsWith('Bearer ')) {
    return { authenticated: false, user: null }
  }

  const token = authHeader.substring(7)
  const payload = verifyToken(token)

  if (!payload) {
    return { authenticated: false, user: null }
  }

  return {
    authenticated: true,
    user: {
      id: payload.userId,
      email: payload.email,
    }
  }
}

// app/api/protected/route.ts
import { authenticateRequest } from '@/lib/auth/api-auth'

export async function GET(request: NextRequest) {
  const { authenticated, user } = await authenticateRequest(request)

  if (!authenticated) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  // User is authenticated
  return NextResponse.json({ data: 'Protected data', user })
}
```

## Authorization and Access Control

### Role-Based Access Control (RBAC)

```typescript
// types/auth.ts
export enum Role {
  USER = 'user',
  ADMIN = 'admin',
  MODERATOR = 'moderator',
}

export interface User {
  id: string
  email: string
  role: Role
}
```

**Authorization Middleware**
```typescript
// lib/auth/authorization.ts
import { Role } from '@/types/auth'

export function requireRole(allowedRoles: Role[]) {
  return (user: User) => {
    if (!allowedRoles.includes(user.role)) {
      throw new Error('Forbidden: Insufficient permissions')
    }
    return true
  }
}

// Usage in API route
export async function DELETE(request: NextRequest) {
  const { authenticated, user } = await authenticateRequest(request)

  if (!authenticated) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    requireRole([Role.ADMIN])(user)
  } catch (error) {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
  }

  // Admin-only logic
  await deleteResource()
  return NextResponse.json({ success: true })
}
```

**Component-Level Authorization**
```typescript
// components/AdminOnly.tsx
'use client'

import { useSession } from 'next-auth/react'
import { Role } from '@/types/auth'

export function AdminOnly({ children }: { children: React.ReactNode }) {
  const { data: session } = useSession()

  if (session?.user?.role !== Role.ADMIN) {
    return null
  }

  return <>{children}</>
}

// Usage
<AdminOnly>
  <DeleteButton />
</AdminOnly>
```

### Resource-Level Authorization

```typescript
// lib/auth/resource-auth.ts
export async function canAccessResource(userId: string, resourceId: string) {
  const resource = await getResource(resourceId)

  // Check ownership
  if (resource.ownerId === userId) {
    return true
  }

  // Check shared access
  const hasSharedAccess = await checkSharedAccess(userId, resourceId)
  if (hasSharedAccess) {
    return true
  }

  return false
}

// Usage in API route
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const { authenticated, user } = await authenticateRequest(request)

  if (!authenticated) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const canAccess = await canAccessResource(user.id, params.id)
  if (!canAccess) {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 })
  }

  const resource = await getResource(params.id)
  return NextResponse.json(resource)
}
```

## Input Validation and Sanitization

### Zod Validation

**Installation**
```bash
npm install zod
```

**Schema Definition**
```typescript
// lib/validations/task.ts
import { z } from 'zod'

export const createTaskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(255, 'Title too long'),
  description: z.string().max(10000, 'Description too long').optional(),
  dueDate: z.string().datetime().optional(),
  priority: z.enum(['low', 'medium', 'high']).default('medium'),
  tags: z.array(z.string()).max(10, 'Too many tags').optional(),
})

export type CreateTaskInput = z.infer<typeof createTaskSchema>
```

**API Route Validation**
```typescript
// app/api/tasks/route.ts
import { createTaskSchema } from '@/lib/validations/task'

export async function POST(request: NextRequest) {
  const { authenticated, user } = await authenticateRequest(request)

  if (!authenticated) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  try {
    const body = await request.json()
    const validatedData = createTaskSchema.parse(body)

    const task = await createTask({
      ...validatedData,
      userId: user.id,
    })

    return NextResponse.json(task, { status: 201 })
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation failed', details: error.errors },
        { status: 400 }
      )
    }

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

**Form Validation (Client-Side)**
```typescript
'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { createTaskSchema, CreateTaskInput } from '@/lib/validations/task'

export function CreateTaskForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateTaskInput>({
    resolver: zodResolver(createTaskSchema),
  })

  const onSubmit = async (data: CreateTaskInput) => {
    const response = await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })

    if (response.ok) {
      // Handle success
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('title')} />
      {errors.title && <span>{errors.title.message}</span>}

      <textarea {...register('description')} />
      {errors.description && <span>{errors.description.message}</span>}

      <button type="submit">Create Task</button>
    </form>
  )
}
```

### HTML Sanitization

```typescript
import DOMPurify from 'isomorphic-dompurify'

export function sanitizeHTML(dirty: string): string {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
    ALLOWED_ATTR: ['href', 'target'],
  })
}

// Usage
const cleanHTML = sanitizeHTML(userInput)
```

## Security Headers

### Content Security Policy (CSP)

```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval' 'unsafe-inline'", // Adjust for Next.js
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: https:",
      "font-src 'self' data:",
      "connect-src 'self' https://api.example.com",
      "frame-ancestors 'none'",
    ].join('; '),
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY',
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin',
  },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=()',
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=31536000; includeSubDomains',
  },
]

module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: securityHeaders,
      },
    ]
  },
}
```

### CORS Configuration

```typescript
// app/api/data/route.ts
export async function GET(request: NextRequest) {
  const origin = request.headers.get('origin')
  const allowedOrigins = [
    'https://yourdomain.com',
    'https://app.yourdomain.com',
  ]

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }

  if (origin && allowedOrigins.includes(origin)) {
    headers['Access-Control-Allow-Origin'] = origin
    headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
    headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    headers['Access-Control-Allow-Credentials'] = 'true'
  }

  const data = await fetchData()
  return NextResponse.json(data, { headers })
}

export async function OPTIONS(request: NextRequest) {
  // Handle preflight requests
  return new NextResponse(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}
```

## CSRF Protection

### Token-Based CSRF Protection

```typescript
// lib/csrf.ts
import { randomBytes } from 'crypto'

export function generateCSRFToken(): string {
  return randomBytes(32).toString('hex')
}

export function validateCSRFToken(token: string, storedToken: string): boolean {
  return token === storedToken
}

// middleware.ts
export function middleware(request: NextRequest) {
  // Generate CSRF token for GET requests
  if (request.method === 'GET') {
    const response = NextResponse.next()
    const csrfToken = generateCSRFToken()
    response.cookies.set('csrf-token', csrfToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
    })
    return response
  }

  // Validate CSRF token for state-changing requests
  if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(request.method)) {
    const csrfToken = request.headers.get('x-csrf-token')
    const storedToken = request.cookies.get('csrf-token')?.value

    if (!csrfToken || !storedToken || !validateCSRFToken(csrfToken, storedToken)) {
      return NextResponse.json(
        { error: 'Invalid CSRF token' },
        { status: 403 }
      )
    }
  }

  return NextResponse.next()
}
```

## Rate Limiting

### API Rate Limiting

```typescript
// lib/rate-limit.ts
import { LRUCache } from 'lru-cache'

type RateLimitOptions = {
  interval: number // Time window in milliseconds
  uniqueTokenPerInterval: number // Max number of unique tokens
}

export function rateLimit(options: RateLimitOptions) {
  const tokenCache = new LRUCache({
    max: options.uniqueTokenPerInterval || 500,
    ttl: options.interval || 60000,
  })

  return {
    check: (limit: number, token: string) =>
      new Promise<void>((resolve, reject) => {
        const tokenCount = (tokenCache.get(token) as number[]) || [0]
        if (tokenCount[0] === 0) {
          tokenCache.set(token, tokenCount)
        }
        tokenCount[0] += 1

        const currentUsage = tokenCount[0]
        const isRateLimited = currentUsage >= limit

        return isRateLimited ? reject() : resolve()
      }),
  }
}

// Usage in API route
const limiter = rateLimit({
  interval: 60 * 1000, // 1 minute
  uniqueTokenPerInterval: 500,
})

export async function POST(request: NextRequest) {
  const ip = request.ip ?? '127.0.0.1'

  try {
    await limiter.check(10, ip) // 10 requests per minute
  } catch {
    return NextResponse.json(
      { error: 'Rate limit exceeded' },
      { status: 429 }
    )
  }

  // Process request
}
```

## Environment Variables Security

### Secure Configuration

```typescript
// lib/env.ts
import { z } from 'zod'

const envSchema = z.object({
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  NEXTAUTH_SECRET: z.string().min(32),
  NEXTAUTH_URL: z.string().url(),
  API_KEY: z.string().min(20),
})

export const env = envSchema.parse(process.env)
```

**Environment Variable Best Practices:**
- Never commit `.env` files to version control
- Use different secrets for development and production
- Rotate secrets regularly
- Use environment-specific prefixes (e.g., `NEXT_PUBLIC_` for client-side vars)
- Validate environment variables at startup

## SQL Injection Prevention

### Parameterized Queries

```typescript
// ❌ Bad: String concatenation (SQL injection risk)
const userId = request.query.id
const query = `SELECT * FROM users WHERE id = '${userId}'`
await db.query(query)

// ✅ Good: Parameterized query
const userId = request.query.id
const query = 'SELECT * FROM users WHERE id = $1'
await db.query(query, [userId])
```

### ORM Usage

```typescript
// Using Prisma (safe by default)
const user = await prisma.user.findUnique({
  where: { id: userId }
})

// Using Drizzle (safe by default)
const user = await db.select().from(users).where(eq(users.id, userId))
```

## XSS Prevention

### React's Built-in Protection

```typescript
// ✅ Safe: React escapes by default
<div>{userInput}</div>

// ❌ Dangerous: Bypasses protection
<div dangerouslySetInnerHTML={{ __html: userInput }} />

// ✅ Safe: Sanitize before using dangerouslySetInnerHTML
import DOMPurify from 'isomorphic-dompurify'
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userInput) }} />
```

## Security Checklist

### Authentication & Authorization
- [ ] Implement secure authentication (NextAuth.js or custom JWT)
- [ ] Use strong password hashing (bcrypt, argon2)
- [ ] Implement session management with secure cookies
- [ ] Add role-based access control (RBAC)
- [ ] Protect API routes with authentication middleware
- [ ] Implement resource-level authorization
- [ ] Add rate limiting to authentication endpoints

### Input Validation
- [ ] Validate all user inputs with Zod or similar
- [ ] Sanitize HTML content from users
- [ ] Use parameterized queries for database operations
- [ ] Validate file uploads (type, size, content)
- [ ] Implement CSRF protection for state-changing operations

### Security Headers
- [ ] Configure Content Security Policy (CSP)
- [ ] Set X-Frame-Options to prevent clickjacking
- [ ] Enable X-Content-Type-Options
- [ ] Configure Strict-Transport-Security (HSTS)
- [ ] Set appropriate CORS headers

### Environment & Secrets
- [ ] Never commit secrets to version control
- [ ] Use environment variables for sensitive data
- [ ] Validate environment variables at startup
- [ ] Rotate secrets regularly
- [ ] Use different secrets for dev/staging/production

### API Security
- [ ] Implement rate limiting
- [ ] Add request size limits
- [ ] Validate Content-Type headers
- [ ] Log security events
- [ ] Handle errors securely (no stack traces in production)

### Dependencies
- [ ] Keep dependencies up to date
- [ ] Run `npm audit` regularly
- [ ] Use Dependabot or Renovate for automated updates
- [ ] Review security advisories
- [ ] Remove unused dependencies
