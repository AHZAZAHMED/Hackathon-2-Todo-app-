# Implementation Plan: Authentication System (Better Auth + JWT)

**Branch**: `002-auth` | **Date**: 2026-02-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-auth/spec.md`

## Summary

Implement production-grade authentication system using Better Auth with JWT tokens for Hackathon II Phase-2 Todo Application. This feature enables secure user registration, login, session management, and user isolation across frontend (Next.js 16+) and backend (FastAPI). The system uses httpOnly cookies for token storage, implements rate limiting (5 attempts per 15 minutes), supports unlimited concurrent sessions, and enforces stateless JWT verification on all protected API routes.

**Primary Requirement**: Enable multi-user authentication with JWT-based identity verification, replacing all mock authentication logic with production-ready Better Auth integration.

**Technical Approach**:
- Frontend: Better Auth library with JWT plugin for Next.js 16+ App Router
- Backend: FastAPI JWT verification middleware using PyJWT
- Token Storage: httpOnly cookies (XSS protection)
- Token Claims: user_id, email, name, exp, iat
- Rate Limiting: Database-tracked failed attempts per email
- Session Policy: Unlimited concurrent sessions with session restoration on token expiration

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5.x (strict mode), Node.js 18+
- Backend: Python 3.11+

**Primary Dependencies**:
- Frontend: Better Auth (latest), Next.js 16+, React 18+, Tailwind CSS 3.x
- Backend: FastAPI, PyJWT, python-jose[cryptography], passlib[bcrypt]

**Storage**: PostgreSQL (Neon Serverless) for user credentials and rate limit tracking

**Testing**:
- Frontend: Playwright (browser automation)
- Backend: pytest with FastAPI TestClient
- Integration: Playwright end-to-end tests

**Target Platform**:
- Frontend: Modern browsers (Chrome, Firefox, Safari, Edge latest)
- Backend: Linux server (containerized deployment)

**Project Type**: Web application (frontend + backend)

**Performance Goals**:
- Authentication requests (signup/login): <2 seconds under normal load
- JWT verification: <100ms per request
- Route guards: <50ms evaluation time
- Support 100 concurrent authentication requests

**Constraints**:
- JWT tokens expire after 24 hours
- Rate limiting: 5 failed attempts per email per 15 minutes
- httpOnly cookies required (no localStorage/sessionStorage)
- Stateless backend (no server-side session storage)
- HTTPS required in production

**Scale/Scope**:
- Multi-user application (10-1000 users initially)
- 5 user stories (P1-P5 prioritized)
- 41 functional requirements
- 4 key entities (User, JWT Token, Session, Rate Limit Tracker)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅ PASS
- ✅ Specification approved: `specs/002-auth/spec.md`
- ✅ Clarifications completed: 5 critical ambiguities resolved
- ✅ Following mandatory workflow: constitution → specify → clarify → **plan** → tasks → implement

### Principle II: JWT-Only Identity ✅ PASS
- ✅ Backend extracts `user_id` from verified JWT claims (FR-024)
- ✅ Frontend never sends `user_id` manually (FR-011, FR-019)
- ✅ Backend never trusts client-provided `user_id` (FR-028)
- ✅ All authentication state derives from Better Auth JWT tokens (FR-002, FR-010)

### Principle III: Database-Backed Persistence ✅ PASS
- ✅ PostgreSQL (Neon Serverless) as single source of truth (Assumption #1)
- ✅ `users` table managed by Better Auth (Assumption #2)
- ✅ Rate limit tracking persists in database (FR-032, Rate Limit Tracker entity)
- ✅ No mock data or in-memory storage (FR-020)
- ⚠️ **DEFERRED**: `tasks` table and foreign key constraints (separate feature - out of scope)

### Principle IV: Production-Grade Architecture ✅ PASS
- ✅ TypeScript strict mode required (Technical Context)
- ✅ Tailwind CSS officially configured (existing from 001-frontend-web-app)
- ✅ Environment variables mandatory: BETTER_AUTH_SECRET (FR-041)
- ✅ Centralized API client updated (FR-019)
- ✅ Error handling for all failure paths: 401, 403, 429 (FR-025, FR-026, FR-030, FR-033)
- ✅ CORS properly configured (Non-Functional Requirements)

### Principle V: Root-Cause Engineering ✅ PASS
- ✅ No temporary solutions or workarounds
- ✅ All mock authentication logic removed (FR-020)
- ✅ Production-ready implementation from day one

### Principle VI: Clear Separation of Layers ✅ PASS
- ✅ Frontend: Next.js 16+ App Router + TypeScript + Tailwind CSS
- ✅ Authentication: Better Auth + JWT
- ✅ Backend: FastAPI + Python
- ✅ Database: PostgreSQL (Neon Serverless)
- ✅ API contracts define inter-layer communication (contracts/ directory)
- ✅ No cross-layer logic bleeding

**Constitution Compliance**: ✅ **ALL PRINCIPLES SATISFIED**

**Note on Deferred Item**: The `tasks` table and foreign key constraints are explicitly out of scope for this feature (see Scope section in spec.md). This will be addressed in a separate "Task CRUD API" feature that depends on this authentication system.

## Project Structure

### Documentation (this feature)

```text
specs/002-auth/
├── spec.md              # Feature specification (approved)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output: Technology decisions
├── data-model.md        # Phase 1 output: Entity definitions
├── quickstart.md        # Phase 1 output: Setup instructions
├── contracts/           # Phase 1 output: API specifications
│   └── api-client.md    # Updated API client interface
├── checklists/          # Quality validation
│   └── requirements.md  # Specification quality checklist (passed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application structure (frontend + backend)

backend/                 # FastAPI backend (TO BE CREATED)
├── app/
│   ├── __init__.py
│   ├── main.py         # FastAPI application entry point
│   ├── config.py       # Environment configuration
│   ├── auth/           # Authentication module
│   │   ├── __init__.py
│   │   ├── middleware.py    # JWT verification middleware
│   │   ├── dependencies.py  # FastAPI dependencies for auth
│   │   └── utils.py         # JWT decode/verify utilities
│   ├── models/         # SQLModel/Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py     # User model (Better Auth managed)
│   │   └── rate_limit.py    # Rate limit tracker model
│   ├── routes/         # API endpoints
│   │   ├── __init__.py
│   │   └── auth.py     # Auth status endpoint (if needed)
│   └── database.py     # Database connection
├── tests/
│   ├── __init__.py
│   ├── test_auth_middleware.py
│   └── test_rate_limiting.py
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
└── README.md           # Backend setup instructions

frontend/               # Next.js frontend (EXISTING - TO BE UPDATED)
├── app/
│   ├── layout.tsx      # Root layout (existing)
│   ├── page.tsx        # Landing page (existing)
│   ├── login/
│   │   └── page.tsx    # Login page (UPDATE: integrate Better Auth)
│   ├── signup/
│   │   └── page.tsx    # Signup page (UPDATE: integrate Better Auth)
│   └── dashboard/
│       └── page.tsx    # Dashboard (UPDATE: add auth protection)
├── components/
│   ├── auth/           # Authentication components (existing)
│   │   ├── LoginForm.tsx    # (UPDATE: integrate Better Auth)
│   │   └── SignupForm.tsx   # (UPDATE: integrate Better Auth)
│   ├── layout/
│   │   ├── Navbar.tsx       # (existing with ProfileDropdown)
│   │   └── ProfileDropdown.tsx  # (UPDATE: integrate logout)
│   └── ui/             # UI components (existing)
├── lib/
│   ├── auth.ts         # NEW: Better Auth configuration
│   ├── api-client.ts   # (UPDATE: JWT attachment logic)
│   └── utils.ts        # (existing)
├── hooks/
│   ├── useAuth.tsx     # (UPDATE: integrate Better Auth)
│   └── useModal.ts     # (existing)
├── middleware.ts       # NEW: Next.js middleware for route protection
├── types/
│   ├── auth.ts         # (UPDATE: Better Auth types)
│   └── user.ts         # (existing)
├── .env.example        # (UPDATE: add BETTER_AUTH_SECRET)
└── package.json        # (UPDATE: add Better Auth dependency)
```

**Structure Decision**: Web application structure selected based on frontend + backend detection. Frontend directory already exists from feature 001-frontend-web-app. Backend directory will be created for this feature. Both layers maintain clear separation with API contracts defining all communication.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution principles are satisfied.

## Execution Phases

### Phase 0: Skill Loading & Research

**Purpose**: Load better-auth-skill and resolve all technical unknowns before implementation.

**Prerequisites**: Constitution Check passed ✅

**Tasks**:
1. **Load better-auth-skill**: Invoke `.claude/skills/better-auth-skill` for Better Auth expertise
2. **Research Better Auth Configuration**: Document Better Auth setup for Next.js 16+ App Router
3. **Research JWT Plugin**: Document JWT plugin configuration and token customization
4. **Research httpOnly Cookie Setup**: Document cookie configuration for Better Auth
5. **Research FastAPI JWT Verification**: Document PyJWT integration patterns for FastAPI
6. **Research Rate Limiting Implementation**: Document database-backed rate limiting approach
7. **Research Session Restoration**: Document URL preservation and redirect patterns

**Deliverable**: `research.md` with 10 technology decisions documented

**Validation**:
- ✅ All NEEDS CLARIFICATION items resolved
- ✅ Technology choices documented with rationale
- ✅ Alternatives considered and rejected reasons documented

---

### Phase 1: Frontend Better Auth Integration

**Purpose**: Install and configure Better Auth with JWT plugin in Next.js frontend.

**Prerequisites**: Phase 0 complete, research.md exists

**Tasks**:
1. **Install Better Auth**: Add `better-auth` package to frontend/package.json
2. **Configure Better Auth**: Create `lib/auth.ts` with Better Auth configuration
3. **Enable JWT Plugin**: Configure JWT plugin with custom claims (user_id, email, name, exp, iat)
4. **Configure httpOnly Cookies**: Set cookie options for secure token storage
5. **Create Auth API Routes**: Set up Next.js API routes for Better Auth endpoints
6. **Update Environment Variables**: Add BETTER_AUTH_SECRET to .env.example and .env.local
7. **Update LoginForm**: Integrate Better Auth login API
8. **Update SignupForm**: Integrate Better Auth signup API
9. **Update useAuth Hook**: Replace mock logic with Better Auth session management
10. **Update ProfileDropdown**: Integrate Better Auth logout function

**Deliverable**: Better Auth fully integrated in frontend with JWT token issuance

**Validation**:
- ✅ `npm install` succeeds without errors
- ✅ Better Auth configuration loads without errors
- ✅ JWT tokens issued on successful login/signup
- ✅ JWT tokens stored in httpOnly cookies
- ✅ JWT tokens include all required claims (user_id, email, name, exp, iat)

---

### Phase 2: JWT Configuration & API Client Update

**Purpose**: Configure JWT token attachment to all API requests and implement session restoration.

**Prerequisites**: Phase 1 complete, Better Auth integrated

**Tasks**:
1. **Update API Client**: Modify `lib/api-client.ts` to automatically attach JWT from cookies
2. **Implement Session Restoration**: Store original URL on 401 and redirect back after re-login
3. **Add 401 Error Handler**: Detect token expiration and trigger re-authentication flow
4. **Add 429 Error Handler**: Display rate limit error with retry time
5. **Remove Mock Auth Logic**: Delete all temporary authentication code from frontend
6. **Test Token Attachment**: Verify JWT included in Authorization header for all requests
7. **Test Session Persistence**: Verify authentication state persists across page refreshes
8. **Test Session Restoration**: Verify user returns to original page after token expiration

**Deliverable**: JWT tokens automatically attached to all API requests with session restoration

**Validation**:
- ✅ All API requests include Authorization header with JWT
- ✅ 401 responses trigger redirect to login with URL preservation
- ✅ User redirected back to original page after successful re-login
- ✅ No mock authentication logic remains in codebase

---

### Phase 3: Backend JWT Verification

**Purpose**: Implement FastAPI JWT verification middleware and rate limiting.

**Prerequisites**: Phase 2 complete, frontend JWT attachment working

**Tasks**:
1. **Create Backend Directory**: Initialize FastAPI project structure
2. **Install Dependencies**: Add FastAPI, PyJWT, python-jose, passlib to requirements.txt
3. **Configure Environment**: Create .env.example with BETTER_AUTH_SECRET, DATABASE_URL
4. **Create JWT Middleware**: Implement JWT verification middleware in `app/auth/middleware.py`
5. **Implement Token Verification**: Verify JWT signature using BETTER_AUTH_SECRET
6. **Extract User Claims**: Extract user_id, email, name from verified JWT
7. **Create Rate Limit Model**: Define SQLModel for tracking failed login attempts
8. **Implement Rate Limiting**: Track failed attempts per email, enforce 5/15min limit
9. **Add Error Responses**: Return 401 for invalid tokens, 403 for unauthorized access, 429 for rate limits
10. **Create Auth Dependency**: FastAPI dependency to inject authenticated user into endpoints

**Deliverable**: Backend JWT verification middleware with rate limiting

**Validation**:
- ✅ Backend starts without errors
- ✅ JWT verification rejects invalid tokens with 401
- ✅ JWT verification rejects expired tokens with 401
- ✅ JWT verification rejects missing tokens with 401
- ✅ user_id extracted from JWT and available to endpoints
- ✅ Rate limiting enforces 5 attempts per email per 15 minutes
- ✅ Rate limit exceeded returns 429 with clear error message

---

### Phase 4: Route Protection

**Purpose**: Protect frontend routes and backend endpoints from unauthenticated access.

**Prerequisites**: Phase 3 complete, backend JWT verification working

**Tasks**:
1. **Create Next.js Middleware**: Implement `middleware.ts` for route protection
2. **Protect Dashboard Route**: Redirect unauthenticated users from /dashboard to /login
3. **Protect Task Routes**: Redirect unauthenticated users from /tasks/* to /login (if exists)
4. **Apply Backend Middleware**: Apply JWT middleware to all protected API routes
5. **Test Unauthenticated Access**: Verify redirect to login for protected routes
6. **Test Authenticated Access**: Verify access granted with valid JWT
7. **Test Concurrent Sessions**: Verify multiple devices can be logged in simultaneously
8. **Test Browser Back Button**: Verify logout prevents back button access to protected content

**Deliverable**: All protected routes enforce authentication

**Validation**:
- ✅ Unauthenticated users redirected to /login for protected routes
- ✅ Authenticated users can access protected routes
- ✅ Backend endpoints reject requests without valid JWT
- ✅ Multiple concurrent sessions work correctly
- ✅ Logout clears JWT and prevents access to protected content

---

### Phase 5: End-to-End Testing

**Purpose**: Validate complete authentication flow from signup to logout.

**Prerequisites**: Phase 4 complete, all routes protected

**Tasks**:
1. **Test User Registration Flow**: Signup → JWT issued → Redirect to dashboard
2. **Test User Login Flow**: Login → JWT issued → Redirect to dashboard
3. **Test Token Expiration**: Active use → Token expires → Redirect to login → Session restoration
4. **Test Rate Limiting**: 5 failed logins → 429 error → Wait 15 minutes → Success
5. **Test Concurrent Sessions**: Login on device A → Login on device B → Both work
6. **Test Logout Flow**: Logout → JWT cleared → Redirect to landing → Cannot access protected routes
7. **Test Invalid Token**: Malformed JWT → 401 → Redirect to login
8. **Test Network Failure**: Network error during auth → User-friendly error → Retry works
9. **Invoke implementation-validator-playwright**: Automated browser-based validation
10. **Invoke integration-testing-engineer**: End-to-end flow validation

**Deliverable**: Fully validated authentication system

**Validation**:
- ✅ All user stories (P1-P5) pass acceptance scenarios
- ✅ All edge cases handled correctly
- ✅ All success criteria met (SC-001 to SC-010)
- ✅ Playwright validation passes
- ✅ Integration tests pass
- ✅ No console errors in browser or backend logs

---

## Validation Criteria

### Functional Validation

**User Story 1 - User Registration (P1)**:
- ✅ Valid signup creates account and issues JWT
- ✅ Duplicate email shows "Email already registered" error
- ✅ Invalid email shows validation error
- ✅ Short password shows validation error
- ✅ Empty fields show validation errors
- ✅ JWT stored in httpOnly cookie

**User Story 2 - User Login (P2)**:
- ✅ Valid login issues JWT and redirects to dashboard
- ✅ Incorrect password shows "Invalid email or password" error
- ✅ Non-existent email shows "Invalid email or password" error
- ✅ Empty fields show validation errors
- ✅ JWT stored in httpOnly cookie
- ✅ JWT automatically included in Authorization header

**User Story 3 - Protected Route Access (P3)**:
- ✅ Authenticated users see personalized dashboard
- ✅ Unauthenticated users redirected to login
- ✅ JWT automatically included in API requests
- ✅ Expired token triggers 401 and redirect to login
- ✅ Invalid token triggers 401 and redirect to login
- ✅ Backend extracts user_id from JWT for queries

**User Story 4 - Session Persistence (P4)**:
- ✅ Page refresh maintains authentication state
- ✅ Browser close/reopen maintains authentication (within 24 hours)
- ✅ Token expiration redirects to login
- ✅ Direct URL navigation works for authenticated users

**User Story 5 - User Logout (P5)**:
- ✅ Logout clears JWT and redirects to landing page
- ✅ Post-logout access to protected routes redirects to login
- ✅ No JWT present in browser storage after logout
- ✅ Browser back button redirects to login (not protected content)

### Non-Functional Validation

**Performance**:
- ✅ Signup completes in <60 seconds
- ✅ Login completes in <30 seconds
- ✅ JWT verification completes in <100ms
- ✅ Route guards evaluate in <50ms
- ✅ System handles 100 concurrent auth requests

**Security**:
- ✅ JWT tokens stored in httpOnly cookies (XSS protection)
- ✅ JWT tokens include required claims: user_id, email, name, exp, iat
- ✅ JWT tokens expire after 24 hours
- ✅ Rate limiting enforces 5 attempts per email per 15 minutes
- ✅ Backend is stateless (no server-side sessions)
- ✅ Passwords hashed before storage
- ✅ BETTER_AUTH_SECRET validated on startup

**Usability**:
- ✅ Authentication errors are clear and actionable
- ✅ Rate limit errors indicate retry time
- ✅ Form validation provides immediate feedback
- ✅ Session persistence is transparent
- ✅ Session restoration returns user to original page

**Reliability**:
- ✅ Failed auth attempts don't crash application
- ✅ Network failures handled gracefully
- ✅ Malformed tokens handled gracefully

### Edge Case Validation

- ✅ Token expiration during active use → Session restoration works
- ✅ Concurrent login sessions → Unlimited sessions supported
- ✅ Backend JWT verification failure → 401 returned
- ✅ Network failures during auth → User-friendly error shown
- ✅ Signup with previously deleted email → Treated as new registration
- ✅ Malformed JWT tokens → 401 returned
- ✅ Browser blocks cookies → Error message shown
- ✅ Race conditions with expired token → First 401 triggers redirect
- ✅ Rate limit exceeded → 429 with retry time shown

### Quality Gates (from Constitution)

**Frontend Gates**:
- ✅ `npm run dev` succeeds without errors
- ✅ Tailwind styles render correctly
- ✅ TypeScript compiles with strict mode
- ✅ No console errors in browser
- ✅ Centralized API client updated

**Authentication Gates**:
- ✅ JWT issued on login
- ✅ JWT stored securely in httpOnly cookies
- ✅ JWT attached to requests automatically
- ✅ Auth state persists across reloads

**Backend Gates**:
- ✅ Backend starts without errors
- ✅ JWT verification rejects invalid tokens (401)
- ✅ Endpoints extract user_id from JWT
- ✅ Unauthorized requests return 403
- ✅ CORS configured correctly

**Integration Gates**:
- ✅ Signup → Login → Dashboard flow works
- ✅ JWT flow end-to-end (issuance → verification)
- ✅ User isolation enforced (separate user data)
- ✅ Error paths handled (invalid JWT, unauthorized access)

---

## Next Steps

After this plan is approved:

1. **Run `/sp.tasks`**: Generate detailed task breakdown from this plan
2. **Execute Phase 0**: Load better-auth-skill and complete research
3. **Execute Phase 1-5**: Implement authentication system following execution phases
4. **Validate**: Run implementation-validator-playwright and integration-testing-engineer skills
5. **Document**: Create PHR for implementation work

**Estimated Effort**:
- Phase 0 (Research): 1-2 hours
- Phase 1 (Frontend Integration): 3-4 hours
- Phase 2 (JWT Configuration): 2-3 hours
- Phase 3 (Backend Verification): 3-4 hours
- Phase 4 (Route Protection): 2-3 hours
- Phase 5 (Testing): 2-3 hours
- **Total**: 13-19 hours

**Dependencies**:
- Frontend Web Application (001-frontend-web-app) must be complete ✅
- PostgreSQL database must be accessible
- BETTER_AUTH_SECRET must be generated and configured

**Blocking Items**: None - all prerequisites satisfied
