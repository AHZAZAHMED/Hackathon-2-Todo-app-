# API Contracts: Authentication System

**Feature**: Authentication System (Better Auth + JWT)
**Date**: 2026-02-05
**Phase**: Phase 1 - API Contract Definition

## Overview

This document defines the API contracts between the Next.js frontend and FastAPI backend for the authentication system. It specifies request/response formats, error handling, JWT token flow, and API client configuration.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
│                                                              │
│  ┌──────────────┐         ┌─────────────────┐              │
│  │  Better Auth │────────▶│  API Client     │              │
│  │  (JWT Issue) │         │  (lib/api-      │              │
│  └──────────────┘         │   client.ts)    │              │
│                           └────────┬─────────┘              │
│                                    │                         │
└────────────────────────────────────┼─────────────────────────┘
                                     │
                                     │ HTTPS + JWT
                                     │
┌────────────────────────────────────┼─────────────────────────┐
│                                    ▼                         │
│  ┌─────────────────┐      ┌──────────────┐                 │
│  │ JWT Middleware  │◀─────│  Protected   │                 │
│  │ (Verify Token)  │      │  Endpoints   │                 │
│  └─────────────────┘      └──────────────┘                 │
│                                                              │
│                    Backend (FastAPI)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Better Auth Endpoints

Better Auth provides built-in authentication endpoints. These are managed by Better Auth and do NOT require custom backend implementation.

### 1. Signup Endpoint

**Endpoint**: `POST /api/auth/signup`

**Managed By**: Better Auth (frontend)

**Request**:
```typescript
{
  name: string;      // User's display name
  email: string;     // User's email address
  password: string;  // User's password (minimum 8 characters)
}
```

**Response (Success - 201 Created)**:
```typescript
{
  user: {
    id: string | number;
    name: string;
    email: string;
    createdAt: string;  // ISO 8601 timestamp
  };
  session: {
    token: string;      // JWT token (also set in httpOnly cookie)
    expiresAt: string;  // ISO 8601 timestamp
  };
}
```

**Response (Error - 400 Bad Request)**:
```typescript
{
  error: {
    code: "VALIDATION_ERROR" | "EMAIL_ALREADY_EXISTS";
    message: string;
    fields?: {
      [key: string]: string;  // Field-specific error messages
    };
  };
}
```

**Error Scenarios**:
- `400 VALIDATION_ERROR`: Invalid email format, password too short, missing fields
- `400 EMAIL_ALREADY_EXISTS`: Email already registered
- `500 INTERNAL_SERVER_ERROR`: Database connection failure

**Client-Side Validation** (before request):
- Email format: RFC 5322 compliant
- Password length: minimum 8 characters
- All fields required (name, email, password)

**Example Request**:
```typescript
const response = await fetch('/api/auth/signup', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'John Doe',
    email: 'john@example.com',
    password: 'securepassword123'
  })
});
```

---

### 2. Login Endpoint

**Endpoint**: `POST /api/auth/login`

**Managed By**: Better Auth (frontend)

**Request**:
```typescript
{
  email: string;     // User's email address
  password: string;  // User's password
}
```

**Response (Success - 200 OK)**:
```typescript
{
  user: {
    id: string | number;
    name: string;
    email: string;
  };
  session: {
    token: string;      // JWT token (also set in httpOnly cookie)
    expiresAt: string;  // ISO 8601 timestamp
  };
}
```

**Response (Error - 401 Unauthorized)**:
```typescript
{
  error: {
    code: "INVALID_CREDENTIALS";
    message: "Invalid email or password";
  };
}
```

**Response (Error - 429 Too Many Requests)**:
```typescript
{
  error: {
    code: "RATE_LIMIT_EXCEEDED";
    message: "Too many failed login attempts. Please try again in X minutes.";
    retryAfter: number;  // Seconds until retry allowed
  };
}
```

**Error Scenarios**:
- `401 INVALID_CREDENTIALS`: Email not found or password incorrect
- `429 RATE_LIMIT_EXCEEDED`: 5 failed attempts within 15 minutes
- `500 INTERNAL_SERVER_ERROR`: Database connection failure

**Rate Limiting**:
- Maximum 5 failed attempts per email per 15 minutes
- Enforced by backend before password verification
- Successful login resets the counter

**Example Request**:
```typescript
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'john@example.com',
    password: 'securepassword123'
  })
});
```

---

### 3. Logout Endpoint

**Endpoint**: `POST /api/auth/logout`

**Managed By**: Better Auth (frontend)

**Request**: No body required

**Response (Success - 200 OK)**:
```typescript
{
  success: true;
}
```

**Side Effects**:
- JWT token cleared from httpOnly cookie
- Session destroyed on client side
- User redirected to landing page

**Example Request**:
```typescript
const response = await fetch('/api/auth/logout', {
  method: 'POST',
  credentials: 'include'  // Include cookies
});
```

---

### 4. Session Check Endpoint

**Endpoint**: `GET /api/auth/session`

**Managed By**: Better Auth (frontend)

**Request**: No body required (JWT token in cookie)

**Response (Success - 200 OK)**:
```typescript
{
  user: {
    id: string | number;
    name: string;
    email: string;
  };
  session: {
    expiresAt: string;  // ISO 8601 timestamp
  };
}
```

**Response (Error - 401 Unauthorized)**:
```typescript
{
  error: {
    code: "UNAUTHENTICATED";
    message: "No valid session found";
  };
}
```

**Usage**:
- Called on page load to restore session
- Called by route guards to check authentication
- Automatically includes JWT token from cookie

**Example Request**:
```typescript
const response = await fetch('/api/auth/session', {
  method: 'GET',
  credentials: 'include'  // Include cookies
});
```

---

## Backend Protected Endpoints

All backend endpoints (except health checks) require JWT authentication.

### JWT Token Flow

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Token Extraction**:
1. Frontend API client extracts JWT from httpOnly cookie
2. Frontend attaches JWT to `Authorization` header
3. Backend JWT middleware verifies token signature
4. Backend extracts `user_id` from token claims
5. Backend uses `user_id` for database queries

**Token Verification** (Backend Middleware):
```python
# Pseudocode for JWT verification
def verify_jwt(token: str) -> dict:
    try:
        # Verify signature using BETTER_AUTH_SECRET
        payload = jwt.decode(
            token,
            secret=BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )

        # Validate expiration
        if payload["exp"] < time.now():
            raise TokenExpiredError()

        # Validate issued-at
        if payload["iat"] > time.now():
            raise InvalidTokenError()

        # Extract user_id
        user_id = payload["user_id"]

        return {"user_id": user_id, "email": payload["email"]}

    except Exception as e:
        raise UnauthorizedError()
```

---

### Example Protected Endpoint: Get Tasks

**Endpoint**: `GET /api/tasks`

**Authentication**: Required (JWT token)

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request**: No body required

**Response (Success - 200 OK)**:
```typescript
{
  tasks: [
    {
      id: string | number;
      title: string;
      description: string;
      completed: boolean;
      userId: string | number;  // Always matches authenticated user
      createdAt: string;        // ISO 8601 timestamp
      updatedAt: string;        // ISO 8601 timestamp
    }
  ];
}
```

**Response (Error - 401 Unauthorized)**:
```typescript
{
  error: {
    code: "INVALID_TOKEN" | "TOKEN_EXPIRED" | "MISSING_TOKEN";
    message: string;
  };
}
```

**Backend Query** (User Isolation):
```python
# Backend MUST filter by authenticated user_id
user_id = extract_user_id_from_jwt(request)
tasks = db.query(Task).filter(Task.user_id == user_id).all()
```

**Security Constraints**:
- Backend MUST extract `user_id` from JWT (never trust client)
- Backend MUST filter all queries by authenticated `user_id`
- Backend MUST return 403 if user attempts to access another user's resources

---

## API Client Configuration

### Frontend API Client (lib/api-client.ts)

**Purpose**: Centralized HTTP client that automatically attaches JWT tokens to all requests.

**Configuration**:
```typescript
// lib/api-client.ts
import { auth } from '@/lib/auth';  // Better Auth instance

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
      credentials: 'include',  // Include cookies
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

  // Similar methods for PUT, PATCH, DELETE...

  private async handleResponse<T>(response: Response): Promise<T> {
    if (response.status === 401) {
      // Token expired or invalid - redirect to login
      const currentPath = window.location.pathname;
      sessionStorage.setItem('redirectAfterLogin', currentPath);
      window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`;
      throw new Error('Unauthorized');
    }

    if (response.status === 403) {
      throw new Error('Forbidden: You do not have access to this resource');
    }

    if (response.status === 429) {
      const data = await response.json();
      throw new Error(data.error.message);
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

**Usage in Components**:
```typescript
// app/dashboard/page.tsx
import { apiClient } from '@/lib/api-client';

export default async function DashboardPage() {
  try {
    const data = await apiClient.get('/api/tasks');
    return <TaskList tasks={data.tasks} />;
  } catch (error) {
    return <ErrorMessage error={error.message} />;
  }
}
```

**Key Features**:
- ✅ Automatically attaches JWT token to all requests
- ✅ Handles 401 errors with session restoration
- ✅ Handles 403 errors with clear messages
- ✅ Handles 429 rate limit errors
- ✅ Includes credentials (cookies) in all requests
- ✅ Centralized error handling

---

## Error Handling Contracts

### HTTP Status Codes

| Status Code | Meaning | When Used |
|-------------|---------|-----------|
| `200 OK` | Success | Successful GET, POST (login), DELETE |
| `201 Created` | Resource created | Successful signup, task creation |
| `400 Bad Request` | Validation error | Invalid input, missing fields |
| `401 Unauthorized` | Authentication failed | Invalid/missing/expired JWT token |
| `403 Forbidden` | Authorization failed | User accessing another user's resources |
| `404 Not Found` | Resource not found | Task ID doesn't exist |
| `429 Too Many Requests` | Rate limit exceeded | 5 failed login attempts within 15 minutes |
| `500 Internal Server Error` | Server error | Database connection failure, unexpected errors |

### Error Response Format

**Standard Error Response**:
```typescript
{
  error: {
    code: string;           // Machine-readable error code
    message: string;        // Human-readable error message
    details?: any;          // Optional additional context
    retryAfter?: number;    // For 429 errors (seconds)
    fields?: {              // For validation errors
      [key: string]: string;
    };
  };
}
```

**Error Codes**:

| Code | Status | Description |
|------|--------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid input format or missing required fields |
| `EMAIL_ALREADY_EXISTS` | 400 | Email already registered during signup |
| `INVALID_CREDENTIALS` | 401 | Email or password incorrect during login |
| `MISSING_TOKEN` | 401 | No JWT token provided in request |
| `INVALID_TOKEN` | 401 | JWT token signature invalid |
| `TOKEN_EXPIRED` | 401 | JWT token expired (> 24 hours old) |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many failed login attempts |
| `FORBIDDEN` | 403 | User attempting to access another user's resources |
| `NOT_FOUND` | 404 | Resource doesn't exist |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

### Frontend Error Handling

**Display User-Friendly Messages**:
```typescript
const ERROR_MESSAGES: Record<string, string> = {
  VALIDATION_ERROR: 'Please check your input and try again.',
  EMAIL_ALREADY_EXISTS: 'This email is already registered. Please log in instead.',
  INVALID_CREDENTIALS: 'Invalid email or password. Please try again.',
  MISSING_TOKEN: 'Please log in to continue.',
  INVALID_TOKEN: 'Your session is invalid. Please log in again.',
  TOKEN_EXPIRED: 'Your session has expired. Please log in again.',
  RATE_LIMIT_EXCEEDED: 'Too many failed attempts. Please try again later.',
  FORBIDDEN: 'You do not have permission to access this resource.',
  NOT_FOUND: 'The requested resource was not found.',
  INTERNAL_ERROR: 'An unexpected error occurred. Please try again later.',
};

function getErrorMessage(errorCode: string): string {
  return ERROR_MESSAGES[errorCode] || 'An error occurred. Please try again.';
}
```

---

## JWT Token Contract

### Token Structure

**Header**:
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload (Claims)**:
```json
{
  "user_id": 123,
  "email": "user@example.com",
  "name": "John Doe",
  "exp": 1738800000,
  "iat": 1738713600
}
```

**Signature**:
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  BETTER_AUTH_SECRET
)
```

### Token Validation Rules

**Frontend** (Better Auth):
- ✅ Issue token on successful signup/login
- ✅ Store token in httpOnly cookie
- ✅ Include token in Authorization header for API requests
- ✅ Check token expiration before requests
- ✅ Redirect to login if token expired

**Backend** (FastAPI):
- ✅ Verify token signature using BETTER_AUTH_SECRET
- ✅ Validate `exp` claim (must be in future)
- ✅ Validate `iat` claim (must be in past)
- ✅ Extract `user_id` from claims
- ✅ Use `user_id` for all database queries
- ✅ Return 401 if token invalid/expired/missing

### Token Lifecycle

```
[Signup/Login] → [Token Issued] → [Token Stored in Cookie]
                                          ↓
                                   [Token Attached to Requests]
                                          ↓
                                   [Backend Verifies Token]
                                          ↓
                                   [Extract user_id]
                                          ↓
                                   [Query Database]
                                          ↓
                                   [Return User-Specific Data]

[After 24 hours] → [Token Expires] → [401 Error] → [Redirect to Login]
```

---

## CORS Configuration

### Backend CORS Settings

**Required Configuration** (FastAPI):
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://yourdomain.com"  # Production
    ],
    allow_credentials=True,  # Required for cookies
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**Environment Variables**:
```bash
# .env
FRONTEND_URL=http://localhost:3000  # Development
# FRONTEND_URL=https://yourdomain.com  # Production
```

**Security Constraints**:
- ❌ NEVER use `allow_origins=["*"]` (wildcard not allowed with credentials)
- ✅ Explicitly whitelist frontend origin
- ✅ Enable credentials for cookie support
- ✅ Restrict methods to required HTTP verbs
- ✅ Restrict headers to Authorization and Content-Type

---

## Environment Variables

### Frontend (.env.local)

```bash
# Better Auth Configuration
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters
BETTER_AUTH_URL=http://localhost:3000

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Database URL (for Better Auth)
DATABASE_URL=postgresql://user:password@host:5432/database
```

### Backend (.env)

```bash
# JWT Verification
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters

# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# CORS
FRONTEND_URL=http://localhost:3000
```

**Security Requirements**:
- ✅ `BETTER_AUTH_SECRET` MUST be identical in frontend and backend
- ✅ `BETTER_AUTH_SECRET` MUST be minimum 32 characters
- ✅ `BETTER_AUTH_SECRET` MUST be cryptographically random
- ✅ Environment variables MUST NOT be committed to version control
- ✅ Provide `.env.example` with placeholder values

---

## Testing Contracts

### Manual Testing Checklist

**Signup Flow**:
- [ ] Valid signup creates user and issues JWT token
- [ ] Duplicate email returns 400 EMAIL_ALREADY_EXISTS
- [ ] Invalid email format returns 400 VALIDATION_ERROR
- [ ] Short password returns 400 VALIDATION_ERROR
- [ ] JWT token stored in httpOnly cookie
- [ ] User redirected to dashboard after signup

**Login Flow**:
- [ ] Valid login issues JWT token
- [ ] Invalid email returns 401 INVALID_CREDENTIALS
- [ ] Invalid password returns 401 INVALID_CREDENTIALS
- [ ] 5 failed attempts returns 429 RATE_LIMIT_EXCEEDED
- [ ] Successful login after failed attempts resets counter
- [ ] JWT token stored in httpOnly cookie
- [ ] User redirected to dashboard after login

**Protected Route Access**:
- [ ] Authenticated user can access protected routes
- [ ] Unauthenticated user redirected to login
- [ ] JWT token automatically attached to API requests
- [ ] Backend extracts user_id from JWT
- [ ] Backend returns only user's own data
- [ ] Expired token returns 401 and redirects to login

**Logout Flow**:
- [ ] Logout clears JWT token from cookie
- [ ] User redirected to landing page
- [ ] Subsequent protected route access redirected to login

---

## Next Steps

After contracts approval:
1. Proceed to Phase 1 quickstart (quickstart.md)
2. Begin Phase 2 implementation (Better Auth integration)
3. Implement API client with JWT attachment logic
4. Test end-to-end authentication flow

---

**Status**: Ready for review
**Dependencies**: data-model.md (completed)
**Blockers**: None
