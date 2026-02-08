# Feature Specification: Authentication System (Better Auth + JWT)

**Feature Branch**: `002-auth`
**Created**: 2026-02-05
**Status**: Draft
**Input**: User description: "Authentication System (Better Auth + JWT) – Hackathon II Phase-2"

## Clarifications

### Session 2026-02-05

- Q: What mechanism should be used to store JWT tokens securely? → A: httpOnly cookie (prevents XSS attacks, automatically sent with requests)
- Q: What policy should be enforced for concurrent login sessions from different devices? → A: Allow unlimited concurrent sessions (best UX for multi-device usage, stateless implementation)
- Q: What should happen when a user's JWT token expires while they are actively using the application? → A: Redirect to login with session restoration (user returns to previous page after re-authentication)
- Q: What rate limiting should be applied to authentication attempts to prevent brute-force attacks? → A: 5 failed attempts per email per 15 minutes (industry standard, balances security and UX)
- Q: What claims should be included in the JWT token structure? → A: user_id, email, name, exp (expiration), iat (issued-at) - balances token size with functionality

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Registration (Priority: P1)

A new user visits the application and creates an account by providing their name, email, and password. The system validates the input, creates a user account, issues a JWT token, and automatically logs them in.

**Why this priority**: This is the foundation of the authentication system. Without user registration, no users can access the application. This is the most critical user journey as it enables all subsequent authenticated interactions.

**Independent Test**: Can be fully tested by navigating to the signup page, submitting valid registration details, and verifying that a JWT token is issued and the user is redirected to the dashboard. Delivers immediate value by allowing users to create accounts.

**Acceptance Scenarios**:

1. **Given** a new user on the signup page, **When** they enter valid name, email, and password and submit the form, **Then** their account is created, a JWT token is issued, and they are redirected to the dashboard
2. **Given** a user on the signup page, **When** they enter an email that already exists, **Then** they see an error message "Email already registered"
3. **Given** a user on the signup page, **When** they enter an invalid email format, **Then** they see an error message "Please enter a valid email address"
4. **Given** a user on the signup page, **When** they enter a password shorter than 8 characters, **Then** they see an error message "Password must be at least 8 characters"
5. **Given** a user on the signup page, **When** they leave required fields empty and submit, **Then** they see validation errors for each empty field
6. **Given** a user successfully signs up, **When** they check their browser storage, **Then** a valid JWT token is stored securely

---

### User Story 2 - User Login (Priority: P2)

An existing user visits the application and logs in using their email and password. The system validates their credentials, issues a JWT token, and grants access to protected routes.

**Why this priority**: This is the second most critical journey as it enables returning users to access their accounts. Without login, users cannot access their data after initial registration.

**Independent Test**: Can be fully tested by navigating to the login page, submitting valid credentials, and verifying that a JWT token is issued and the user gains access to protected routes. Delivers value by enabling returning user access.

**Acceptance Scenarios**:

1. **Given** an existing user on the login page, **When** they enter valid email and password and submit, **Then** a JWT token is issued and they are redirected to the dashboard
2. **Given** a user on the login page, **When** they enter an incorrect password, **Then** they see an error message "Invalid email or password"
3. **Given** a user on the login page, **When** they enter an email that doesn't exist, **Then** they see an error message "Invalid email or password"
4. **Given** a user on the login page, **When** they leave fields empty and submit, **Then** they see validation errors for each empty field
5. **Given** a user successfully logs in, **When** they check their browser storage, **Then** a valid JWT token is stored securely
6. **Given** a logged-in user, **When** they navigate to any protected route, **Then** their JWT token is automatically included in the Authorization header

---

### User Story 3 - Protected Route Access (Priority: P3)

An authenticated user navigates to protected routes (dashboard, tasks) and the system automatically includes their JWT token in all API requests. Unauthenticated users are redirected to the login page.

**Why this priority**: This ensures that only authenticated users can access protected resources and that their identity is automatically verified on every request. This is essential for security and user isolation.

**Independent Test**: Can be fully tested by attempting to access protected routes both with and without authentication, and verifying that JWT tokens are automatically attached to API requests. Delivers value by enforcing security boundaries.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they navigate to the dashboard, **Then** they see their personalized dashboard content
2. **Given** an unauthenticated user, **When** they attempt to access the dashboard directly, **Then** they are redirected to the login page
3. **Given** an authenticated user, **When** they make an API request, **Then** the JWT token is automatically included in the Authorization header
4. **Given** an authenticated user with an expired token, **When** they make an API request, **Then** they receive a 401 error and are redirected to login
5. **Given** an authenticated user with an invalid token, **When** they make an API request, **Then** they receive a 401 error and are redirected to login
6. **Given** an authenticated user, **When** the backend verifies their JWT token, **Then** the user_id is extracted from the token and used for all database queries

---

### User Story 4 - Session Persistence (Priority: P4)

An authenticated user closes their browser or refreshes the page, and their session persists. They remain logged in without needing to re-enter credentials.

**Why this priority**: This enhances user experience by maintaining authentication state across browser sessions. While not critical for core functionality, it significantly improves usability.

**Independent Test**: Can be fully tested by logging in, closing the browser, reopening it, and verifying that the user remains authenticated. Delivers value by reducing friction in the user experience.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they refresh the page, **Then** they remain logged in and see their authenticated content
2. **Given** an authenticated user, **When** they close and reopen their browser within the token expiration period, **Then** they remain logged in
3. **Given** an authenticated user, **When** they close and reopen their browser after the token has expired, **Then** they are redirected to the login page
4. **Given** an authenticated user, **When** they navigate directly to a protected route by URL, **Then** they see the protected content without being redirected to login

---

### User Story 5 - User Logout (Priority: P5)

An authenticated user clicks the logout button in the profile dropdown. The system clears their JWT token and redirects them to the landing page.

**Why this priority**: This is important for security, especially on shared devices, but is the lowest priority as users can still use the application without explicit logout (tokens expire automatically).

**Independent Test**: Can be fully tested by logging in, clicking logout, and verifying that the JWT token is cleared and the user is redirected to the landing page. Delivers value by allowing users to explicitly end their session.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they click the logout button in the profile dropdown, **Then** their JWT token is cleared and they are redirected to the landing page
2. **Given** a user who just logged out, **When** they attempt to access a protected route, **Then** they are redirected to the login page
3. **Given** a user who just logged out, **When** they check their browser storage, **Then** no JWT token is present
4. **Given** a user who just logged out, **When** they click the browser back button, **Then** they are redirected to the login page (not back to protected content)

---

### Edge Cases

- **Token expiration during active use**: User is redirected to login page with the original URL stored; after successful re-authentication, user is returned to their previous location
- **Concurrent login sessions**: System allows unlimited concurrent sessions from different devices; each device maintains its own JWT token in httpOnly cookies
- **Backend JWT verification failure**: System returns 401 Unauthorized and frontend redirects user to login page
- **Network failures during authentication**: System displays user-friendly error message and allows user to retry; no partial state is saved
- **Signup with previously deleted email**: System treats as new registration; no historical data is retained or exposed
- **Malformed JWT tokens**: Backend rejects with 401 Unauthorized; frontend redirects to login page
- **Browser blocks cookies**: System displays error message indicating that cookies are required for authentication; user cannot proceed without enabling cookies
- **Race conditions with expired token**: First request to fail with 401 triggers redirect to login; subsequent requests are cancelled or queued until re-authentication completes
- **Rate limit exceeded**: After 5 failed login attempts within 15 minutes, system returns 429 Too Many Requests with clear message indicating when user can retry

## Requirements *(mandatory)*

### Functional Requirements

#### Frontend Requirements

- **FR-001**: System MUST install and configure Better Auth library in the Next.js frontend
- **FR-002**: System MUST enable Better Auth JWT plugin for token-based authentication
- **FR-003**: System MUST provide a signup form that collects name, email, and password
- **FR-004**: System MUST validate email format on the client side before submission
- **FR-005**: System MUST validate password length (minimum 8 characters) on the client side before submission
- **FR-006**: System MUST display inline validation errors for invalid form inputs
- **FR-007**: System MUST provide a login form that collects email and password
- **FR-008**: System MUST call Better Auth signup API when user submits the signup form
- **FR-009**: System MUST call Better Auth login API when user submits the login form
- **FR-010**: System MUST store JWT token securely in httpOnly cookies after successful authentication
- **FR-011**: System MUST automatically attach JWT token to all API requests in the Authorization header
- **FR-012**: System MUST implement route guards that redirect unauthenticated users to the login page
- **FR-013**: System MUST protect dashboard and task routes from unauthenticated access
- **FR-014**: System MUST persist authentication state across page refreshes
- **FR-015**: System MUST provide a logout function that clears the JWT token
- **FR-016**: System MUST redirect users to the landing page after logout
- **FR-017**: System MUST handle 401 responses from the backend by redirecting to login and storing the original URL for post-authentication restoration
- **FR-018**: System MUST display user-friendly error messages for authentication failures
- **FR-019**: System MUST update the centralized API client to include JWT token in all requests
- **FR-020**: System MUST remove all mock authentication logic from the frontend
- **FR-021**: System MUST support unlimited concurrent sessions across multiple devices

#### Backend Requirements

- **FR-022**: System MUST implement JWT verification middleware for all protected API routes
- **FR-023**: System MUST verify JWT token signature using the shared BETTER_AUTH_SECRET
- **FR-024**: System MUST extract user_id from verified JWT token claims
- **FR-025**: System MUST reject requests with missing JWT tokens with 401 Unauthorized
- **FR-026**: System MUST reject requests with invalid JWT tokens with 401 Unauthorized
- **FR-027**: System MUST reject requests with expired JWT tokens with 401 Unauthorized
- **FR-028**: System MUST use extracted user_id for all database queries (never trust client-provided user_id)
- **FR-029**: System MUST enforce user isolation by filtering all queries by authenticated user_id
- **FR-030**: System MUST return 403 Forbidden when a user attempts to access another user's resources
- **FR-031**: System MUST be stateless (no server-side session storage)
- **FR-032**: System MUST implement rate limiting: maximum 5 failed login attempts per email address within a 15-minute window
- **FR-033**: System MUST return 429 Too Many Requests when rate limit is exceeded with a clear error message indicating when the user can retry

#### Security Requirements

- **FR-034**: System MUST sign JWT tokens using a strong shared secret (BETTER_AUTH_SECRET)
- **FR-035**: System MUST set JWT token expiration to 24 hours
- **FR-036**: System MUST include the following claims in JWT tokens: user_id (primary identifier), email (user email address), name (user display name), exp (expiration timestamp), iat (issued-at timestamp)
- **FR-037**: System MUST use HTTPS for all authentication requests in production
- **FR-038**: System MUST hash passwords before storing them in the database
- **FR-039**: System MUST never log or expose JWT tokens in error messages
- **FR-040**: System MUST never expose the BETTER_AUTH_SECRET in client-side code
- **FR-041**: System MUST validate that BETTER_AUTH_SECRET is set before starting the application

### Key Entities

- **User**: Represents an authenticated user with attributes including unique identifier, name, email, and hashed password. Related to tasks through user_id foreign key.
- **JWT Token**: Represents an authentication token stored in httpOnly cookies containing claims: user_id (primary identifier), email (user email address), name (user display name), exp (expiration timestamp), iat (issued-at timestamp), and signature. Issued by Better Auth on successful authentication and verified by backend middleware.
- **Session**: Represents the user's authentication state maintained by Better Auth, persisted across page refreshes until token expiration or explicit logout. Multiple concurrent sessions are supported across different devices.
- **Rate Limit Tracker**: Tracks failed authentication attempts per email address to enforce rate limiting (5 attempts per 15 minutes) and prevent brute-force attacks.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete account registration in under 60 seconds
- **SC-002**: Users can log in to their account in under 30 seconds
- **SC-003**: 100% of API requests from authenticated users include a valid JWT token
- **SC-004**: 100% of unauthenticated access attempts to protected routes are blocked
- **SC-005**: User sessions persist across page refreshes for the duration of the token lifetime (24 hours)
- **SC-006**: 100% of backend API requests verify JWT tokens before processing
- **SC-007**: Users can only access their own data (0% unauthorized data access)
- **SC-008**: Authentication errors are displayed to users within 2 seconds
- **SC-009**: Logout completes and redirects users within 1 second
- **SC-010**: System handles 100 concurrent authentication requests without degradation

## Scope *(mandatory)*

### In Scope

- Better Auth installation and configuration in Next.js frontend
- JWT plugin enablement and configuration
- Signup and login form implementation with validation
- JWT token issuance on successful authentication with claims: user_id, email, name, exp, iat
- JWT token storage in httpOnly cookies
- Automatic JWT token attachment to all API requests
- Route protection and authentication guards
- Session persistence across page refreshes
- Session restoration after token expiration (redirect back to original URL after re-login)
- Logout functionality
- Backend JWT verification middleware
- User_id extraction from JWT tokens
- 401/403 error handling for authentication failures
- User isolation enforcement in backend queries
- Rate limiting for authentication attempts (5 failed attempts per email per 15 minutes)
- Support for unlimited concurrent sessions across multiple devices
- Environment variable configuration for BETTER_AUTH_SECRET
- Integration with existing frontend API client
- Removal of all mock authentication logic

### Out of Scope

- Task CRUD API implementation (separate feature)
- Database schema design and migrations (separate feature)
- OAuth provider integration (Google, GitHub, etc.)
- Role-based access control (RBAC)
- Password reset functionality
- Email verification
- Two-factor authentication (2FA)
- Refresh token implementation
- Remember me functionality
- Account deletion
- Profile editing
- Phase-3 chatbot integration

## Assumptions *(optional)*

1. **Database**: A PostgreSQL database (Neon Serverless) is available and accessible from the backend
2. **User Table**: A users table exists or will be created with columns: id, name, email, password (hashed)
3. **Environment Variables**: Both frontend and backend can access environment variables for configuration
4. **HTTPS**: Production deployment will use HTTPS for secure token transmission
5. **Token Expiration**: 24-hour token expiration is acceptable for this application's use case
6. **Password Requirements**: Minimum 8 characters is sufficient for password security
7. **Browser Support**: Users have modern browsers that support local storage or cookies
8. **Network**: Users have stable internet connections for authentication requests
9. **Better Auth Compatibility**: Better Auth library is compatible with Next.js 16+ App Router
10. **JWT Standard**: Backend can decode and verify JWT tokens using standard libraries

## Dependencies *(optional)*

### External Dependencies

- **Better Auth**: NPM package for authentication in Next.js applications
- **JWT Library**: Backend library for JWT verification (e.g., PyJWT for Python/FastAPI)
- **PostgreSQL**: Database for storing user credentials
- **Neon Serverless**: PostgreSQL hosting service

### Internal Dependencies

- **Frontend Web Application**: Completed (specs/001-frontend-web-app)
- **Centralized API Client**: Exists in frontend/lib/api-client.ts and must be updated
- **Environment Configuration**: .env files must be created for both frontend and backend

### Blocking Dependencies

- **Database Connection**: Backend must be able to connect to PostgreSQL database
- **User Table**: Users table must exist before authentication can function
- **Shared Secret**: BETTER_AUTH_SECRET must be configured in both frontend and backend

## Non-Functional Requirements *(optional)*

### Performance

- Authentication requests (signup/login) must complete within 2 seconds under normal load
- JWT token verification must complete within 100ms
- Route guards must evaluate authentication state within 50ms

### Security

- All passwords must be hashed using bcrypt or equivalent with appropriate salt rounds
- JWT tokens must be signed with a cryptographically secure secret (minimum 32 characters)
- JWT tokens must be stored in httpOnly cookies to prevent XSS attacks
- JWT tokens must include standard claims: user_id, email, name, exp, iat
- Tokens must expire after 24 hours to limit exposure window
- Rate limiting must enforce maximum 5 failed login attempts per email address within 15 minutes
- Backend must be stateless to enable horizontal scaling
- System must support unlimited concurrent sessions across multiple devices

### Usability

- Authentication errors must be clear and actionable (e.g., "Invalid email or password" not "Error 401")
- Rate limit errors must indicate when the user can retry (e.g., "Too many failed attempts. Please try again in 10 minutes")
- Form validation must provide immediate feedback (client-side validation)
- Session persistence must be transparent to users (no manual re-authentication required)
- After token expiration, users must be redirected back to their original location after successful re-authentication

### Reliability

- Authentication system must have 99.9% uptime
- Failed authentication attempts must not crash the application
- System must gracefully handle network failures during authentication

### Maintainability

- Authentication logic must be centralized and reusable
- JWT verification middleware must be applied consistently to all protected routes
- Environment variables must be documented in .env.example files

## Open Questions *(optional)*

None. All requirements are sufficiently specified with reasonable defaults documented in the Assumptions section.

## References *(optional)*

- [Better Auth Documentation](https://www.better-auth.com/docs)
- [JWT.io - Introduction to JSON Web Tokens](https://jwt.io/introduction)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Next.js 16 App Router Documentation](https://nextjs.org/docs/app)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- Hackathon II Phase-2 CLAUDE.md (root project rules)
- Frontend Web Application Specification (specs/001-frontend-web-app/spec.md)
