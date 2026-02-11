# Data Model: Authentication System

**Feature**: Authentication System (Better Auth + JWT)
**Date**: 2026-02-05
**Phase**: Phase 1 - Data Model Definition

## Overview

This document defines all entities, their attributes, relationships, and constraints for the authentication system. The data model supports multi-user authentication with JWT tokens, session management, and rate limiting.

---

## Entity Definitions

### 1. User

**Purpose**: Represents an authenticated user account in the system.

**Managed By**: Better Auth (frontend) + PostgreSQL (backend)

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `id` | UUID or Integer | PRIMARY KEY, NOT NULL, AUTO-INCREMENT | Unique identifier for the user |
| `name` | String(255) | NOT NULL | User's display name |
| `email` | String(255) | NOT NULL, UNIQUE | User's email address (used for login) |
| `password` | String(255) | NOT NULL | Bcrypt-hashed password (never stored in plaintext) |
| `created_at` | Timestamp | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| `updated_at` | Timestamp | NOT NULL, DEFAULT NOW() | Last account update timestamp |

**Indexes**:
- Primary index on `id`
- Unique index on `email` (for login lookups)

**Relationships**:
- One-to-Many with `Task` entity (out of scope for this feature)
- One-to-Many with `Rate Limit Tracker` entity

**Validation Rules**:
- Email must be valid format (RFC 5322)
- Password must be at least 8 characters before hashing
- Email must be unique across all users
- Name cannot be empty

**Security Constraints**:
- Password field MUST be hashed using bcrypt with 12 salt rounds
- Password MUST NEVER be returned in API responses
- Email MUST be case-insensitive for uniqueness checks

**Database Schema** (PostgreSQL):
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

**Notes**:
- Better Auth manages user creation and password hashing automatically
- Backend only needs to read from this table for JWT verification
- User deletion is out of scope for this feature

---

### 2. JWT Token

**Purpose**: Represents an authentication token issued to users after successful login/signup.

**Managed By**: Better Auth (issuance) + Backend (verification)

**Storage Location**: httpOnly cookie in user's browser

**Token Structure**:

| Claim | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | UUID or Integer | YES | Primary identifier extracted from users.id |
| `email` | String | YES | User's email address |
| `name` | String | YES | User's display name |
| `exp` | Integer (Unix timestamp) | YES | Token expiration time (24 hours from issuance) |
| `iat` | Integer (Unix timestamp) | YES | Token issued-at time |

**Token Metadata**:
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Secret**: `BETTER_AUTH_SECRET` environment variable (minimum 32 characters)
- **Expiration**: 24 hours from issuance
- **Size**: ~200-300 bytes (acceptable for cookie storage)

**Validation Rules**:
- Signature MUST be verified using `BETTER_AUTH_SECRET`
- `exp` claim MUST be in the future (not expired)
- `iat` claim MUST be in the past (not issued in future)
- `user_id` MUST exist in users table
- All required claims MUST be present

**Security Constraints**:
- Token MUST be stored in httpOnly cookie (prevents XSS)
- Cookie MUST have `secure: true` in production (HTTPS only)
- Cookie MUST have `sameSite: 'lax'` (CSRF protection)
- Token MUST NOT be logged or exposed in error messages
- Secret MUST NOT be exposed in client-side code

**Example Token Payload**:
```json
{
  "user_id": 123,
  "email": "user@example.com",
  "name": "John Doe",
  "exp": 1738800000,
  "iat": 1738713600
}
```

**Cookie Configuration**:
```javascript
{
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'lax',
  maxAge: 86400000, // 24 hours in milliseconds
  path: '/'
}
```

**Notes**:
- Token is stateless (no server-side session storage)
- Multiple concurrent tokens are allowed (multi-device support)
- Token cannot be revoked before expiration (by design)
- Refresh tokens are out of scope

---

### 3. Session

**Purpose**: Represents the user's authentication state maintained by Better Auth.

**Managed By**: Better Auth (frontend)

**Storage Location**: Client-side (managed by Better Auth library)

**Attributes**:

| Attribute | Type | Description |
|-----------|------|-------------|
| `user` | Object | User information extracted from JWT token |
| `token` | String | JWT token string (stored in httpOnly cookie) |
| `isAuthenticated` | Boolean | Whether user is currently authenticated |
| `expiresAt` | Timestamp | Token expiration timestamp |

**Lifecycle**:
1. **Creation**: Session created on successful login/signup
2. **Persistence**: Session persists across page refreshes (token in cookie)
3. **Expiration**: Session expires after 24 hours (token expiration)
4. **Termination**: Session terminated on explicit logout (cookie cleared)

**State Transitions**:
```
[Unauthenticated] --login/signup--> [Authenticated]
[Authenticated] --logout--> [Unauthenticated]
[Authenticated] --token expires--> [Unauthenticated]
[Authenticated] --page refresh--> [Authenticated] (if token valid)
```

**Validation Rules**:
- Session is valid only if JWT token is valid
- Session MUST be checked before rendering protected routes
- Session MUST be refreshed on page load

**Notes**:
- Session is client-side only (no server-side session storage)
- Multiple concurrent sessions are supported (different devices)
- Session restoration after token expiration redirects to original URL

---

### 4. Rate Limit Tracker

**Purpose**: Tracks failed authentication attempts per email address to prevent brute-force attacks.

**Managed By**: Backend (FastAPI)

**Storage Location**: PostgreSQL database

**Attributes**:

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `id` | Integer | PRIMARY KEY, NOT NULL, AUTO-INCREMENT | Unique identifier |
| `email` | String(255) | NOT NULL, INDEX | Email address being tracked |
| `failed_attempts` | Integer | NOT NULL, DEFAULT 0 | Number of failed login attempts |
| `last_attempt` | Timestamp | NOT NULL | Timestamp of most recent failed attempt |
| `locked_until` | Timestamp | NULLABLE | Timestamp when rate limit expires (NULL if not locked) |
| `created_at` | Timestamp | NOT NULL, DEFAULT NOW() | First failed attempt timestamp |

**Indexes**:
- Primary index on `id`
- Index on `email` (for fast lookups during login)
- Index on `locked_until` (for cleanup queries)

**Relationships**:
- Conceptually related to `User` entity via email (no foreign key)

**Validation Rules**:
- `failed_attempts` MUST be between 0 and 5
- `locked_until` MUST be in the future if set
- `last_attempt` MUST be within 15 minutes of current time for active tracking

**Rate Limiting Logic**:
1. On failed login attempt:
   - Increment `failed_attempts`
   - Update `last_attempt` to NOW()
   - If `failed_attempts >= 5`, set `locked_until = NOW() + 15 minutes`

2. On successful login:
   - Delete rate limit record for that email

3. On login attempt:
   - Check if `locked_until > NOW()`
   - If locked, return 429 Too Many Requests
   - If not locked, proceed with authentication

4. Cleanup (periodic job):
   - Delete records where `locked_until < NOW() - 1 hour`

**Database Schema** (PostgreSQL):
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

**Security Constraints**:
- Rate limiting MUST be enforced before password verification (prevent timing attacks)
- Email MUST be normalized (lowercase) before lookup
- Rate limit records MUST be cleaned up periodically (prevent table bloat)

**Example Rate Limit Flow**:
```
Attempt 1: failed_attempts=1, locked_until=NULL → Allow retry
Attempt 2: failed_attempts=2, locked_until=NULL → Allow retry
Attempt 3: failed_attempts=3, locked_until=NULL → Allow retry
Attempt 4: failed_attempts=4, locked_until=NULL → Allow retry
Attempt 5: failed_attempts=5, locked_until=NOW()+15min → LOCKED
Attempt 6: Check locked_until > NOW() → Return 429
...
After 15 minutes: locked_until < NOW() → Allow retry, reset counter
```

**Notes**:
- Rate limiting is per email address (not per IP or device)
- Successful login clears the rate limit record
- Rate limit window is 15 minutes (sliding window)
- Maximum 5 failed attempts per window

---

## Entity Relationships

```
┌─────────────┐
│    User     │
│  (Better    │
│   Auth)     │
└──────┬──────┘
       │
       │ 1:N (conceptual)
       │
       ▼
┌─────────────┐
│ Rate Limit  │
│  Tracker    │
│ (Backend)   │
└─────────────┘

┌─────────────┐
│  JWT Token  │
│  (httpOnly  │
│   cookie)   │
└──────┬──────┘
       │
       │ contains
       │
       ▼
┌─────────────┐
│   Session   │
│  (Better    │
│   Auth)     │
└─────────────┘
```

**Relationship Notes**:
- User and Rate Limit Tracker are loosely coupled (no foreign key)
- JWT Token contains user_id that references User.id
- Session wraps JWT Token for client-side state management
- Tasks entity (out of scope) will have foreign key to User.id

---

## Data Flow

### Signup Flow:
```
1. User submits signup form (name, email, password)
2. Better Auth validates input
3. Better Auth hashes password (bcrypt)
4. Better Auth creates User record in database
5. Better Auth issues JWT token with claims (user_id, email, name, exp, iat)
6. JWT token stored in httpOnly cookie
7. Session created with user info
8. User redirected to dashboard
```

### Login Flow:
```
1. User submits login form (email, password)
2. Backend checks Rate Limit Tracker for email
3. If locked (locked_until > NOW()), return 429
4. Better Auth verifies email exists
5. Better Auth verifies password hash
6. If password incorrect, increment Rate Limit Tracker
7. If password correct, delete Rate Limit Tracker record
8. Better Auth issues JWT token with claims
9. JWT token stored in httpOnly cookie
10. Session created with user info
11. User redirected to dashboard
```

### Protected Route Access Flow:
```
1. User navigates to protected route
2. Frontend middleware checks Session.isAuthenticated
3. If not authenticated, redirect to /login
4. If authenticated, extract JWT token from cookie
5. Frontend attaches JWT to API request (Authorization header)
6. Backend JWT middleware verifies token signature
7. Backend extracts user_id from token claims
8. Backend uses user_id for database queries
9. Backend returns user-specific data
10. Frontend renders protected content
```

### Logout Flow:
```
1. User clicks logout button
2. Better Auth clears JWT token from cookie
3. Session destroyed
4. User redirected to landing page
```

---

## Validation Summary

### User Entity:
- ✅ Email format validation (RFC 5322)
- ✅ Password length validation (minimum 8 characters)
- ✅ Email uniqueness validation
- ✅ Password hashing (bcrypt, 12 rounds)

### JWT Token:
- ✅ Signature verification (HS256 with BETTER_AUTH_SECRET)
- ✅ Expiration validation (exp > NOW())
- ✅ Issued-at validation (iat < NOW())
- ✅ Required claims presence (user_id, email, name, exp, iat)

### Session:
- ✅ Token validity check on page load
- ✅ Authentication state check before protected routes
- ✅ Session restoration after token expiration

### Rate Limit Tracker:
- ✅ Failed attempts count validation (0-5)
- ✅ Lock expiration validation (locked_until > NOW())
- ✅ Email normalization (lowercase)

---

## Security Considerations

1. **Password Security**:
   - Passwords hashed with bcrypt (12 rounds)
   - Passwords never stored in plaintext
   - Passwords never returned in API responses

2. **Token Security**:
   - JWT stored in httpOnly cookie (XSS protection)
   - Cookie has secure flag in production (HTTPS only)
   - Cookie has sameSite flag (CSRF protection)
   - Token signature verified on every request

3. **Rate Limiting**:
   - Prevents brute-force attacks (5 attempts per 15 minutes)
   - Enforced before password verification (timing attack protection)
   - Database-backed (persistent across server restarts)

4. **User Isolation**:
   - Backend extracts user_id from JWT (never trusts client)
   - All queries filtered by authenticated user_id
   - Foreign key constraints enforce data integrity

---

## Next Steps

After data model approval:
1. Proceed to Phase 1 contracts (contracts/api-client.md)
2. Define API specifications for authentication endpoints
3. Create quickstart.md with setup instructions
4. Begin Phase 2 implementation (Better Auth integration)

---

**Status**: Ready for review
**Dependencies**: None (foundational document)
**Blockers**: None
