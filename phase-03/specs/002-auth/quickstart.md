# Quickstart Guide: Authentication System

**Feature**: Authentication System (Better Auth + JWT)
**Date**: 2026-02-05
**Phase**: Phase 1 - Setup Instructions

## Overview

This guide provides step-by-step instructions to set up and run the authentication system for Hackathon II Phase-2. Follow these instructions to configure Better Auth on the frontend, implement JWT verification on the backend, and test the complete authentication flow.

**Estimated Setup Time**: 30-45 minutes

---

## Prerequisites

### Required Software

- **Node.js**: v18.17.0 or higher
- **npm**: v9.0.0 or higher (or yarn/pnpm)
- **Python**: v3.11 or higher
- **PostgreSQL**: v14 or higher (or Neon Serverless account)
- **Git**: Latest version

### Required Accounts

- **Neon Serverless**: Free account at [neon.tech](https://neon.tech) (or local PostgreSQL)
- **GitHub**: For version control (optional but recommended)

### Knowledge Requirements

- Basic understanding of Next.js App Router
- Basic understanding of FastAPI
- Familiarity with JWT authentication concepts
- Basic SQL knowledge

---

## Project Structure

```
phase-02/
├── frontend/                    # Next.js 16+ App Router
│   ├── app/
│   │   ├── api/
│   │   │   └── auth/
│   │   │       └── [...all]/
│   │   │           └── route.ts  # Better Auth API routes
│   │   ├── login/
│   │   │   └── page.tsx         # Login page
│   │   ├── signup/
│   │   │   └── page.tsx         # Signup page
│   │   └── dashboard/
│   │       └── page.tsx         # Protected route
│   ├── lib/
│   │   ├── auth.ts              # Better Auth configuration
│   │   └── api-client.ts        # Centralized API client
│   ├── middleware.ts            # Route protection
│   ├── .env.local               # Environment variables
│   └── package.json
│
├── backend/                     # FastAPI
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── auth.py              # JWT verification middleware
│   │   ├── models.py            # SQLModel schemas
│   │   └── routes/
│   │       └── tasks.py         # Protected endpoints
│   ├── .env                     # Environment variables
│   └── requirements.txt
│
└── specs/
    └── 002-auth/
        ├── spec.md              # Feature specification
        ├── plan.md              # Implementation plan
        ├── data-model.md        # Entity definitions
        └── contracts/
            └── api-client.md    # API contracts
```

---

## Step 1: Database Setup

### Option A: Neon Serverless (Recommended)

1. **Create Neon Account**:
   - Visit [neon.tech](https://neon.tech)
   - Sign up for free account
   - Create new project: "hackathon-phase2"

2. **Get Connection String**:
   - Navigate to project dashboard
   - Copy connection string (format: `postgresql://user:password@host/database`)
   - Save for later use in environment variables

3. **Create Users Table**:
   ```sql
   CREATE TABLE users (
       id SERIAL PRIMARY KEY,
       name VARCHAR(255) NOT NULL,
       email VARCHAR(255) NOT NULL UNIQUE,
       password VARCHAR(255) NOT NULL,
       created_at TIMESTAMP NOT NULL DEFAULT NOW(),
       updated_at TIMESTAMP NOT NULL DEFAULT NOW()
   );

   CREATE UNIQUE INDEX idx_users_email ON users(LOWER(email));
   ```

4. **Create Rate Limits Table**:
   ```sql
   CREATE TABLE rate_limits (
       id SERIAL PRIMARY KEY,
       email VARCHAR(255) NOT NULL,
       failed_attempts INTEGER NOT NULL DEFAULT 0,
       last_attempt TIMESTAMP NOT NULL,
       locked_until TIMESTAMP,
       created_at TIMESTAMP NOT NULL DEFAULT NOW()
   );

   CREATE INDEX idx_rate_limits_email ON rate_limits(email);
   CREATE INDEX idx_rate_limits_locked_until ON rate_limits(locked_until);
   ```

### Option B: Local PostgreSQL

1. **Install PostgreSQL**:
   ```bash
   # macOS (Homebrew)
   brew install postgresql@14
   brew services start postgresql@14

   # Ubuntu/Debian
   sudo apt-get install postgresql-14
   sudo systemctl start postgresql

   # Windows
   # Download installer from postgresql.org
   ```

2. **Create Database**:
   ```bash
   psql postgres
   CREATE DATABASE hackathon_phase2;
   CREATE USER hackathon_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE hackathon_phase2 TO hackathon_user;
   \q
   ```

3. **Run SQL Scripts** (same as Neon Option A, steps 3-4)

---

## Step 2: Frontend Setup

### 2.1 Install Dependencies

```bash
cd frontend

# Install Next.js dependencies
npm install

# Install Better Auth
npm install better-auth

# Install additional dependencies
npm install jose  # For JWT handling
```

### 2.2 Configure Environment Variables

Create `frontend/.env.local`:

```bash
# Better Auth Configuration
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long-random-string
BETTER_AUTH_URL=http://localhost:3000

# Database URL (for Better Auth)
DATABASE_URL=postgresql://user:password@host:5432/database

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Generate Secure Secret**:
```bash
# Option 1: Using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

# Option 2: Using OpenSSL
openssl rand -hex 32

# Option 3: Using Python
python -c "import secrets; print(secrets.token_hex(32))"
```

**Important**:
- Replace `your-secret-key-...` with generated secret
- Replace `DATABASE_URL` with your Neon or local PostgreSQL connection string
- Keep `.env.local` out of version control (add to `.gitignore`)

### 2.3 Create Better Auth Configuration

Create `frontend/lib/auth.ts`:

```typescript
import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";

export const auth = betterAuth({
  database: {
    provider: "postgresql",
    url: process.env.DATABASE_URL!,
  },
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
  session: {
    expiresIn: 60 * 60 * 24, // 24 hours
    updateAge: 60 * 60 * 24, // 24 hours
    cookieCache: {
      enabled: true,
      maxAge: 60 * 60 * 24, // 24 hours
    },
  },
  plugins: [nextCookies()],
  secret: process.env.BETTER_AUTH_SECRET!,
  baseURL: process.env.BETTER_AUTH_URL!,
});
```

### 2.4 Create Better Auth API Routes

Create `frontend/app/api/auth/[...all]/route.ts`:

```typescript
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

### 2.5 Create API Client

Create `frontend/lib/api-client.ts`:

```typescript
import { auth } from '@/lib/auth';

class ApiClient {
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  private async getAuthHeaders(): Promise<HeadersInit> {
    const session = await auth.api.getSession();

    if (!session?.session?.token) {
      return {
        'Content-Type': 'application/json',
      };
    }

    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.session.token}`,
    };
  }

  async get<T>(endpoint: string): Promise<T> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'GET',
      headers,
      credentials: 'include',
    });

    return this.handleResponse<T>(response);
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers,
      credentials: 'include',
      body: JSON.stringify(data),
    });

    return this.handleResponse<T>(response);
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (response.status === 401) {
      const currentPath = window.location.pathname;
      sessionStorage.setItem('redirectAfterLogin', currentPath);
      window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`;
      throw new Error('Unauthorized');
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'An error occurred');
    }

    return response.json();
  }
}

export const apiClient = new ApiClient();
```

### 2.6 Create Route Protection Middleware

Create `frontend/middleware.ts`:

```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { auth } from '@/lib/auth';

export async function middleware(request: NextRequest) {
  const session = await auth.api.getSession({
    headers: request.headers,
  });

  const isAuthenticated = !!session?.user;
  const isAuthPage = request.nextUrl.pathname.startsWith('/login') ||
                     request.nextUrl.pathname.startsWith('/signup');
  const isProtectedPage = request.nextUrl.pathname.startsWith('/dashboard') ||
                          request.nextUrl.pathname.startsWith('/tasks');

  if (isProtectedPage && !isAuthenticated) {
    const redirectUrl = new URL('/login', request.url);
    redirectUrl.searchParams.set('redirect', request.nextUrl.pathname);
    return NextResponse.redirect(redirectUrl);
  }

  if (isAuthPage && isAuthenticated) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/tasks/:path*', '/login', '/signup'],
};
```

### 2.7 Verify Frontend Setup

```bash
# Start development server
npm run dev

# Expected output:
# ▲ Next.js 16.x.x
# - Local:        http://localhost:3000
# - Ready in X.Xs
```

**Verify**:
- Navigate to `http://localhost:3000`
- No errors in terminal
- No errors in browser console

---

## Step 3: Backend Setup

### 3.1 Install Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn[standard] pyjwt python-jose[cryptography] passlib[bcrypt] sqlmodel psycopg2-binary python-dotenv
```

### 3.2 Create Requirements File

Create `backend/requirements.txt`:

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pyjwt==2.8.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
sqlmodel==0.0.14
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

### 3.3 Configure Environment Variables

Create `backend/.env`:

```bash
# JWT Verification
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long-random-string

# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# CORS
FRONTEND_URL=http://localhost:3000

# Server
HOST=0.0.0.0
PORT=8000
```

**Important**:
- Use the SAME `BETTER_AUTH_SECRET` as frontend
- Use the SAME `DATABASE_URL` as frontend
- Keep `.env` out of version control (add to `.gitignore`)

### 3.4 Create JWT Verification Middleware

Create `backend/app/auth.py`:

```python
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from datetime import datetime

security = HTTPBearer()

BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable is not set")

def verify_jwt(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Verify JWT token and extract user_id.

    Returns:
        dict: {"user_id": int, "email": str, "name": str}

    Raises:
        HTTPException: 401 if token is invalid, expired, or missing
    """
    token = credentials.credentials

    try:
        # Verify signature and decode token
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )

        # Validate expiration
        exp = payload.get("exp")
        if not exp or datetime.fromtimestamp(exp) < datetime.now():
            raise HTTPException(
                status_code=401,
                detail={"error": {"code": "TOKEN_EXPIRED", "message": "Token has expired"}}
            )

        # Validate issued-at
        iat = payload.get("iat")
        if not iat or datetime.fromtimestamp(iat) > datetime.now():
            raise HTTPException(
                status_code=401,
                detail={"error": {"code": "INVALID_TOKEN", "message": "Invalid token"}}
            )

        # Extract required claims
        user_id = payload.get("user_id")
        email = payload.get("email")
        name = payload.get("name")

        if not user_id or not email:
            raise HTTPException(
                status_code=401,
                detail={"error": {"code": "INVALID_TOKEN", "message": "Missing required claims"}}
            )

        return {
            "user_id": user_id,
            "email": email,
            "name": name
        }

    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "INVALID_TOKEN", "message": "Invalid token signature"}}
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "INVALID_TOKEN", "message": "Token decode error"}}
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "INVALID_TOKEN", "message": str(e)}}
        )
```

### 3.5 Create FastAPI Application

Create `backend/app/main.py`:

```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.auth import verify_jwt
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Hackathon Phase-2 API")

# CORS Configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Hackathon Phase-2 API"}

@app.get("/api/protected")
async def protected_route(user: dict = Depends(verify_jwt)):
    """Example protected endpoint"""
    return {
        "message": "This is a protected route",
        "user": user
    }
```

### 3.6 Verify Backend Setup

```bash
# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.
```

**Verify**:
- Navigate to `http://localhost:8000`
- Should see: `{"status": "ok", "message": "Hackathon Phase-2 API"}`
- Navigate to `http://localhost:8000/docs`
- Should see FastAPI Swagger UI

---

## Step 4: Test Authentication Flow

### 4.1 Test Signup

1. **Start both servers**:
   ```bash
   # Terminal 1 (Frontend)
   cd frontend && npm run dev

   # Terminal 2 (Backend)
   cd backend && source venv/bin/activate && uvicorn app.main:app --reload
   ```

2. **Navigate to signup page**:
   - Open browser: `http://localhost:3000/signup`

3. **Create test account**:
   - Name: "Test User"
   - Email: "test@example.com"
   - Password: "password123"
   - Click "Sign Up"

4. **Verify**:
   - ✅ Redirected to dashboard
   - ✅ JWT token stored in cookie (check browser DevTools → Application → Cookies)
   - ✅ User record created in database

### 4.2 Test Login

1. **Logout** (if logged in)

2. **Navigate to login page**:
   - Open browser: `http://localhost:3000/login`

3. **Login with test account**:
   - Email: "test@example.com"
   - Password: "password123"
   - Click "Log In"

4. **Verify**:
   - ✅ Redirected to dashboard
   - ✅ JWT token stored in cookie
   - ✅ No errors in console

### 4.3 Test Protected Route Access

1. **While logged in**:
   - Navigate to `http://localhost:3000/dashboard`
   - Should see dashboard content

2. **Logout**

3. **Try accessing dashboard**:
   - Navigate to `http://localhost:3000/dashboard`
   - Should redirect to `/login?redirect=/dashboard`

4. **Login again**:
   - Should redirect back to `/dashboard`

### 4.4 Test Backend JWT Verification

1. **Get JWT token**:
   - Login to frontend
   - Open browser DevTools → Application → Cookies
   - Copy JWT token value

2. **Test protected endpoint**:
   ```bash
   curl -X GET http://localhost:8000/api/protected \
     -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
   ```

3. **Expected response**:
   ```json
   {
     "message": "This is a protected route",
     "user": {
       "user_id": 1,
       "email": "test@example.com",
       "name": "Test User"
     }
   }
   ```

4. **Test without token**:
   ```bash
   curl -X GET http://localhost:8000/api/protected
   ```

5. **Expected response**:
   ```json
   {
     "detail": "Not authenticated"
   }
   ```

### 4.5 Test Rate Limiting

1. **Attempt 5 failed logins**:
   - Navigate to `http://localhost:3000/login`
   - Enter correct email, wrong password
   - Submit 5 times

2. **Verify**:
   - ✅ After 5th attempt, see "Too many failed attempts" error
   - ✅ Cannot login for 15 minutes
   - ✅ Rate limit record created in database

3. **Verify database**:
   ```sql
   SELECT * FROM rate_limits WHERE email = 'test@example.com';
   ```

---

## Step 5: Verify Complete Setup

### Checklist

**Frontend**:
- [ ] `npm run dev` starts without errors
- [ ] Better Auth configured in `lib/auth.ts`
- [ ] API routes created at `app/api/auth/[...all]/route.ts`
- [ ] API client created in `lib/api-client.ts`
- [ ] Middleware created in `middleware.ts`
- [ ] Environment variables configured in `.env.local`
- [ ] JWT token stored in httpOnly cookie after login

**Backend**:
- [ ] `uvicorn app.main:app --reload` starts without errors
- [ ] JWT verification middleware created in `app/auth.py`
- [ ] CORS configured with frontend origin
- [ ] Environment variables configured in `.env`
- [ ] Protected endpoint returns 401 without token
- [ ] Protected endpoint returns user data with valid token

**Database**:
- [ ] `users` table exists with correct schema
- [ ] `rate_limits` table exists with correct schema
- [ ] Connection string works from both frontend and backend
- [ ] User records created on signup

**Authentication Flow**:
- [ ] Signup creates user and issues JWT token
- [ ] Login issues JWT token
- [ ] JWT token automatically attached to API requests
- [ ] Backend verifies JWT and extracts user_id
- [ ] Protected routes redirect unauthenticated users to login
- [ ] Logout clears JWT token and redirects to landing page
- [ ] Rate limiting enforced after 5 failed attempts

---

## Troubleshooting

### Issue: "BETTER_AUTH_SECRET is not set"

**Solution**:
- Verify `.env.local` (frontend) and `.env` (backend) exist
- Verify `BETTER_AUTH_SECRET` is set in both files
- Verify secret is at least 32 characters
- Restart both servers after changing environment variables

### Issue: "Database connection failed"

**Solution**:
- Verify `DATABASE_URL` is correct
- Test connection: `psql "postgresql://user:password@host:5432/database"`
- For Neon: Check project is active and connection string is correct
- Verify database tables exist (run SQL scripts from Step 1)

### Issue: "CORS error in browser console"

**Solution**:
- Verify `FRONTEND_URL` in backend `.env` matches frontend URL
- Verify `allow_credentials=True` in CORS middleware
- Verify frontend uses `credentials: 'include'` in fetch requests
- Restart backend server after changing CORS configuration

### Issue: "JWT token not attached to requests"

**Solution**:
- Verify API client uses `await auth.api.getSession()`
- Verify `Authorization` header is set in API client
- Verify JWT token exists in cookie (DevTools → Application → Cookies)
- Check browser console for errors

### Issue: "401 Unauthorized from backend"

**Solution**:
- Verify `BETTER_AUTH_SECRET` is identical in frontend and backend
- Verify JWT token is not expired (check `exp` claim)
- Verify JWT token signature is valid
- Check backend logs for specific error message

### Issue: "Rate limiting not working"

**Solution**:
- Verify `rate_limits` table exists
- Verify backend increments `failed_attempts` on wrong password
- Check database: `SELECT * FROM rate_limits;`
- Verify rate limiting logic runs before password verification

---

## Next Steps

After completing this quickstart:

1. **Run `/sp.tasks`**: Generate detailed task breakdown
2. **Implement remaining features**: Task CRUD, user isolation, error handling
3. **Run validation**: Use `implementation-validator-playwright` skill
4. **Run integration tests**: Use `integration-testing-engineer` skill
5. **Deploy to production**: Configure production environment variables

---

## Additional Resources

- [Better Auth Documentation](https://www.better-auth.com/docs)
- [Next.js 16 App Router](https://nextjs.org/docs/app)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [JWT.io](https://jwt.io) - JWT debugger
- [Neon Documentation](https://neon.tech/docs)

---

**Status**: Ready for use
**Last Updated**: 2026-02-05
**Estimated Setup Time**: 30-45 minutes
