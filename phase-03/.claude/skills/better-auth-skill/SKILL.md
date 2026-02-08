---
name: better-auth-integration-skill
description: |
  Better Auth integration skills for implementing secure authentication in full-stack applications with Next.js frontend and FastAPI backend using JWT tokens.
  This skill should be used when setting up Better Auth authentication, integrating JWT verification between frontend and backend, troubleshooting authentication state persistence, implementing user isolation, or fixing authentication-related issues in Next.js + FastAPI applications.
---

# Better Auth Integration Skill

Implement production-ready authentication using Better Auth in full-stack applications with Next.js (frontend) and FastAPI (backend), with JWT-based token management and proper user isolation.

## What This Skill Does

- Guide Better Auth setup in Next.js and FastAPI applications
- Implement JWT token generation, storage, and verification
- Fix authentication state persistence issues
- Enforce user isolation and authorization
- Troubleshoot common authentication problems
- Provide security best practices and checklists

## What This Skill Does NOT Do

- Implement OAuth providers (focus is on email/password)
- Handle password reset flows (basic auth only)
- Set up multi-factor authentication
- Manage session storage in databases

---

## Version Compatibility

This skill is tested with:
- **Next.js**: 14.x
- **FastAPI**: 0.104+
- **Better Auth**: 1.4+
- **Python**: 3.11+
- **Node.js**: 18+

For latest patterns and updates, consult official documentation.

---

## Required Clarifications

Before implementation, clarify:

1. **Deployment environment**: Development, staging, or production?
2. **Database type**: PostgreSQL, MySQL, or SQLite?
3. **Token storage preference**: localStorage, httpOnly cookies, or sessionStorage?

## Optional Clarifications

4. **Token expiration**: Custom duration? (default: 60 minutes)
5. **Refresh tokens**: Needed? (recommended for production)
6. **CORS origins**: Specific domains? (default: localhost:3000)

**If user doesn't provide clarifications**: Use sensible defaults (PostgreSQL, localStorage, 60min tokens) and document assumptions made.

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing auth setup, database models, API structure, environment configuration |
| **Conversation** | User's specific requirements, tech stack versions, deployment environment |
| **Skill References** | Better Auth patterns, JWT best practices, security standards |
| **User Guidelines** | Project-specific security policies, compliance requirements |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

---

## Official Documentation

| Resource | URL | Use For |
|----------|-----|---------|
| Better Auth | https://better-auth.com | Core authentication patterns |
| FastAPI Security | https://fastapi.tiangolo.com/tutorial/security/ | Backend JWT implementation |
| Next.js Auth | https://nextjs.org/docs/authentication | Frontend integration |
| JWT.io | https://jwt.io | Token debugging and validation |
| PyJWT Docs | https://pyjwt.readthedocs.io/ | Python JWT library |

---

## Core Competencies

### 1. Better Auth Architecture
- JWT-based authentication flow
- Token generation with proper claims
- Token expiration and refresh strategies
- Authentication state management
- Secure token storage

### 2. Frontend Integration (Next.js)
- Authentication context provider
- Login and registration forms
- Token storage and retrieval
- State restoration on page load
- Route protection
- Error handling

### 3. Backend Integration (FastAPI)
- JWT token verification
- Authentication middleware
- User isolation enforcement
- Token generation and signing
- Endpoint protection

### 4. Database Integration
- Table initialization on startup
- Secure credential storage
- Database models
- User data isolation

### 5. Security Implementation
- Environment variable management
- CORS configuration
- HTTPS enforcement
- JWT signature validation
- Rate limiting

---

## Critical Mistakes to Avoid

### ❌ Mistake 1: Not Creating Database Tables on Startup

**Problem**: Application starts but tables don't exist → "relation does not exist" errors

**Solution**: Add startup event to create tables
```python
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(bind=engine)
```

**Details**: See `troubleshooting.md` → "Database table does not exist"

### ❌ Mistake 2: Authentication State Not Persisting

**Problem**: User logs in but gets redirected to login on page refresh

**Solution**: Restore session from localStorage on app initialization

**Details**: See `troubleshooting.md` → "Authentication state not persisting"

### ❌ Mistake 3: Mismatched BETTER_AUTH_SECRET

**Problem**: JWT verification fails with "Invalid token"

**Solution**: Use same secret in frontend and backend
```bash
openssl rand -hex 32  # Generate once, use everywhere
```

**Details**: See `troubleshooting.md` → "Token verification fails"

### ❌ Mistake 4: Not Enforcing User Isolation

**Problem**: Users can access other users' data

**Solution**: Verify user_id in URL matches JWT token claims

**Details**: See `troubleshooting.md` → "User can access other users' data"

### ❌ Mistake 5: Missing CORS Configuration

**Problem**: Frontend gets CORS errors when calling backend

**Solution**: Add CORS middleware with proper origins

**Details**: See `troubleshooting.md` → "CORS errors"

### ❌ Mistake 6: Not Handling Token Expiration

**Problem**: Using expired tokens causes 401 errors

**Solution**: Check token validity before using

**Details**: See `jwt-patterns.md` → "Token validation"

### ❌ Mistake 7: Implementing Custom Auth

**Problem**: Reinventing authentication logic

**Solution**: Use Better Auth's built-in functionality

**Details**: See `api-examples.md` → "Authentication routes"

### ❌ Mistake 8: Not Testing End-to-End

**Problem**: Unit tests pass but integration fails

**Solution**: Test complete authentication flow

**Details**: See `troubleshooting.md` → "Testing issues"

---

## Implementation Workflows

### 1. Initial Setup
```
1. Install dependencies (frontend: better-auth, backend: pyjwt passlib)
2. Generate shared secret (openssl rand -hex 32)
3. Configure environment variables
4. Verify secrets match
```

### 2. Frontend Setup
```
1. Create authentication context
2. Wrap app with AuthProvider
3. Create login/registration pages
4. Implement protected routes
5. Add token to API requests
```

### 3. Backend Setup
```
1. Create JWT utilities
2. Implement auth dependency
3. Create auth routes
4. Protect API routes
5. Add CORS middleware
6. Initialize database on startup
```

### 4. Database Setup
```
1. Create user model
2. Create task model
3. Add startup event
4. Verify tables created
```

**Detailed workflows**: See `api-examples.md` and `frontend-examples.md`

---

## Security Checklist

### Environment Variables
- [ ] BETTER_AUTH_SECRET generated securely
- [ ] Same secret in frontend and backend
- [ ] .env files in .gitignore
- [ ] No hardcoded secrets

### Token Management
- [ ] JWT tokens properly signed
- [ ] Tokens include user_id in `sub` claim
- [ ] Token expiration set
- [ ] Token validation checks expiration

### API Security
- [ ] All protected routes verify JWT
- [ ] User isolation enforced
- [ ] CORS configured properly
- [ ] HTTPS in production
- [ ] Rate limiting on auth endpoints

### Database Security
- [ ] Passwords hashed (bcrypt/argon2)
- [ ] User data isolated by user_id
- [ ] Database credentials in env vars
- [ ] SSL for database connections

**Complete checklist**: See `security-checklist.md`

---

## Implementation Checklist

### Frontend (Next.js)
- [ ] Install dependencies
- [ ] Configure environment variables
- [ ] Set up authentication context
- [ ] Implement login/registration pages
- [ ] Create protected routes
- [ ] Add token to API requests
- [ ] Test state persistence

### Backend (FastAPI)
- [ ] Install dependencies
- [ ] Configure environment variables
- [ ] Implement JWT utilities
- [ ] Create auth routes
- [ ] Protect API routes
- [ ] Add CORS middleware
- [ ] Initialize database tables
- [ ] Test token verification

### Database
- [ ] Design schemas
- [ ] Add indexes
- [ ] Implement password hashing
- [ ] Test data isolation

### Testing
- [ ] Test registration flow
- [ ] Test login flow
- [ ] Test authenticated requests
- [ ] Test user isolation
- [ ] Test token expiration
- [ ] Test CORS

**Detailed checklists**: See main sections in SKILL.md

---

## Quick Troubleshooting

### "Not authenticated" errors
- Verify BETTER_AUTH_SECRET matches
- Check token expiration
- Ensure Authorization header format

### State not persisting
- Check localStorage restoration
- Verify useEffect runs on mount
- Validate token before using

### Database errors
- Import models before create_all()
- Add startup event
- Verify database connection

### CORS errors
- Add CORS middleware
- Include frontend URL in origins
- Enable credentials

**Extended troubleshooting**: See `troubleshooting.md`

---

## Reference Files

Search patterns for large reference files:

| File | Lines | Search For |
|------|-------|------------|
| `jwt-patterns.md` | 514 | "generate_jwt_token", "verify_token", "token expiration" |
| `security-checklist.md` | 681 | "BETTER_AUTH_SECRET", "CORS", "password hashing" |
| `api-examples.md` | 767 | "FastAPI", "auth_routes", "JWT verification" |
| `frontend-examples.md` | 969 | "AuthContext", "login page", "protected routes" |
| `troubleshooting.md` | 819 | "authentication state", "CORS errors", "user isolation" |

**Reference contents**:
- `jwt-patterns.md` - JWT token structure, generation, verification patterns
- `security-checklist.md` - Comprehensive security requirements (50+ items)
- `api-examples.md` - Complete FastAPI backend implementation
- `frontend-examples.md` - Complete Next.js frontend implementation
- `troubleshooting.md` - Extended troubleshooting with diagnosis steps

---

## Best Practices

### Token Management
- Short-lived access tokens (15-60 minutes)
- Long-lived refresh tokens (7-30 days)
- Secure storage (httpOnly cookies preferred)
- Validate expiration before use

### Error Handling
- Generic error messages to users
- Detailed logging server-side
- Proper error boundaries
- Graceful network error handling

### Security
- Never commit .env files
- Use HTTPS in production
- Implement rate limiting
- Validate all inputs
- Use prepared statements

### Performance
- Cache decoded JWT payloads
- Use connection pooling
- Optimize database queries
- Implement pagination

### Monitoring
- Log authentication attempts
- Monitor token generation rates
- Track error rates
- Set up security alerts

---

## Summary

Better Auth integration requires:

1. **Proper initialization** - Database tables, environment variables, middleware
2. **Secure token handling** - Generation, storage, verification, expiration
3. **State management** - Persistence across page refreshes
4. **User isolation** - Authorization enforcement
5. **Error handling** - Graceful degradation
6. **Testing** - Comprehensive flow coverage

By following this skill guide and avoiding documented mistakes, you can implement secure, production-ready authentication using Better Auth in Next.js + FastAPI applications.
