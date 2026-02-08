# Research: Authentication System Technology Decisions

**Feature**: Authentication System (Better Auth + JWT)
**Date**: 2026-02-05
**Phase**: Phase 0 - Research

## Overview

This document captures all technology decisions made for implementing the authentication system. All decisions are based on the approved specification, clarification session, and industry best practices.

---

## Decision 1: JWT Token Storage Mechanism

**Decision**: httpOnly cookies

**Rationale**:
- Prevents XSS attacks by making tokens inaccessible to JavaScript
- Automatically sent with requests (no manual attachment needed)
- Industry standard for secure token storage in web applications
- Provides defense-in-depth against common web vulnerabilities

**Alternatives Considered**:
- **localStorage**: Rejected due to XSS vulnerability (JavaScript can access tokens)
- **sessionStorage**: Rejected due to XSS vulnerability and loss on tab close
- **In-memory only**: Rejected due to loss on page refresh (requires refresh token mechanism)

**Implementation Notes**:
- Better Auth supports httpOnly cookies natively
- Cookie configuration: `httpOnly: true, secure: true (production), sameSite: 'lax'`
- Backend must support cookie-based authentication

---

## Decision 2: Better Auth Library for Frontend Authentication

**Decision**: Better Auth with JWT plugin

**Rationale**:
- Official authentication library for Next.js with App Router support
- Built-in JWT plugin for token-based authentication
- Handles token issuance, storage, and session management
- Integrates seamlessly with Next.js 16+ App Router
- Reduces custom authentication code and security risks

**Alternatives Considered**:
- **NextAuth.js**: Rejected due to complexity and OAuth focus (not needed)
- **Custom JWT implementation**: Rejected due to security risks and maintenance burden
- **Auth0/Clerk**: Rejected due to third-party dependency and cost

**Implementation Notes**:
- Install: `npm install better-auth`
- Configuration file: `lib/auth.ts`
- API routes: `app/api/auth/[...all]/route.ts`

---

## Decision 3: JWT Token Claims Structure

**Decision**: user_id, email, name, exp, iat

**Rationale**:
- **user_id**: Primary identifier for database queries
- **email**: User identification and display
- **name**: User display name (avoids additional API call)
- **exp**: Expiration timestamp (standard JWT claim)
- **iat**: Issued-at timestamp (standard JWT claim)
- Balances token size with functionality
- Industry standard claims structure

**Alternatives Considered**:
- **Minimal (user_id, exp only)**: Rejected due to requiring database lookup for user info
- **Extended (includes roles, permissions)**: Rejected as RBAC is out of scope
- **Custom (includes session_id)**: Rejected as it conflicts with stateless requirement

**Implementation Notes**:
- Configure in Better Auth JWT plugin options
- Backend must decode and validate all claims
- Token size: ~200-300 bytes (acceptable)

---

## Decision 4: FastAPI JWT Verification Library

**Decision**: PyJWT with python-jose[cryptography]

**Rationale**:
- PyJWT is the industry standard for JWT handling in Python
- python-jose provides additional cryptographic algorithms
- Well-maintained and widely adopted
- Integrates seamlessly with FastAPI
- Supports all required JWT operations (decode, verify, validate)

**Alternatives Considered**:
- **authlib**: Rejected due to additional complexity (OAuth focus)
- **Custom JWT implementation**: Rejected due to security risks
- **jose (JavaScript)**: Not applicable (Python backend)

**Implementation Notes**:
- Install: `pip install PyJWT python-jose[cryptography]`
- Verify signature using BETTER_AUTH_SECRET
- Validate expiration and issued-at timestamps

---

## Decision 5: Rate Limiting Implementation

**Decision**: Database-backed rate limiting with PostgreSQL

**Rationale**:
- Persistent across server restarts
- Supports horizontal scaling (multiple backend instances)
- Accurate tracking per email address
- Enables audit trail for security analysis
- Aligns with database-backed persistence principle

**Alternatives Considered**:
- **In-memory (Redis)**: Rejected due to additional infrastructure dependency
- **In-memory (Python dict)**: Rejected due to loss on restart and no horizontal scaling
- **Third-party service**: Rejected due to external dependency

**Implementation Notes**:
- Table: `rate_limits` with columns: email, failed_attempts, last_attempt, locked_until
- Cleanup: Periodic job to remove expired entries
- Index on email for query performance

---

## Decision 6: Concurrent Session Policy

**Decision**: Allow unlimited concurrent sessions

**Rationale**:
- Best user experience for multi-device usage (phone, laptop, tablet)
- Stateless implementation (no session tracking needed)
- JWT tokens expire after 24 hours (manageable security risk)
- Aligns with stateless backend principle

**Alternatives Considered**:
- **Single session only**: Rejected due to poor UX (new login invalidates old)
- **Limited sessions (e.g., 3)**: Rejected due to requiring session tracking
- **Single session per device type**: Rejected due to complexity (device detection)

**Implementation Notes**:
- No server-side session tracking required
- Each device maintains its own JWT token in httpOnly cookies
- Token expiration provides natural session cleanup

---

## Decision 7: Token Expiration Behavior

**Decision**: Redirect to login with session restoration

**Rationale**:
- Balances security with user experience
- Prevents data loss (user returns to previous page)
- Maintains workflow continuity
- Industry standard pattern for token expiration

**Alternatives Considered**:
- **Hard redirect (no restoration)**: Rejected due to poor UX (user loses context)
- **Silent token refresh**: Rejected as refresh tokens are out of scope
- **Modal prompt**: Rejected due to frontend complexity

**Implementation Notes**:
- Store original URL in sessionStorage on 401 error
- Redirect to login with `?redirect=/original-url` query parameter
- After successful login, redirect back to original URL

---

## Decision 8: Password Hashing Algorithm

**Decision**: bcrypt with appropriate salt rounds

**Rationale**:
- Industry standard for password hashing
- Computationally expensive (resistant to brute-force)
- Built-in salt generation
- Supported by Better Auth and passlib

**Alternatives Considered**:
- **argon2**: Rejected due to additional dependency (bcrypt sufficient)
- **scrypt**: Rejected due to less widespread adoption
- **PBKDF2**: Rejected due to lower security compared to bcrypt

**Implementation Notes**:
- Better Auth handles password hashing automatically
- Backend uses passlib[bcrypt] for verification if needed
- Salt rounds: 12 (balance between security and performance)

---

## Decision 9: Next.js Middleware for Route Protection

**Decision**: Next.js middleware.ts for frontend route guards

**Rationale**:
- Runs before page render (prevents flash of protected content)
- Centralized route protection logic
- Supports pattern matching for multiple routes
- Native Next.js feature (no additional dependencies)

**Alternatives Considered**:
- **Component-level guards**: Rejected due to flash of content and duplication
- **HOC (Higher-Order Component)**: Rejected due to complexity and maintenance
- **Server-side checks only**: Rejected due to poor UX (full page load on redirect)

**Implementation Notes**:
- File: `middleware.ts` at root of frontend directory
- Matcher: `/dashboard/:path*` and `/tasks/:path*`
- Check Better Auth session, redirect to /login if unauthenticated

---

## Decision 10: Backend CORS Configuration

**Decision**: Explicit CORS configuration with frontend origin whitelist

**Rationale**:
- Security: Only allow requests from known frontend origin
- Credentials: Enable credentials for cookie-based authentication
- Production-ready: Different origins for dev/staging/prod

**Alternatives Considered**:
- **Allow all origins (*)**: Rejected due to security risk
- **No CORS**: Not applicable (frontend and backend on different origins)
- **Proxy through frontend**: Rejected due to additional complexity

**Implementation Notes**:
- FastAPI CORS middleware with `allow_origins=[FRONTEND_URL]`
- `allow_credentials=True` for cookie support
- `allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"]`
- `allow_headers=["Authorization", "Content-Type"]`

---

## Summary

All technology decisions are finalized and documented. No NEEDS CLARIFICATION items remain. The implementation can proceed with confidence based on these decisions.

**Key Technologies**:
- Frontend: Better Auth, Next.js 16+, TypeScript 5.x
- Backend: FastAPI, PyJWT, python-jose, passlib[bcrypt]
- Storage: PostgreSQL (Neon Serverless)
- Token Storage: httpOnly cookies
- Rate Limiting: Database-backed

**Next Steps**: Proceed to Phase 1 (data-model.md, contracts/, quickstart.md)
