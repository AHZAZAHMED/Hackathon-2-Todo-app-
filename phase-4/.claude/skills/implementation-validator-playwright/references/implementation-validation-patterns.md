# Implementation Validation Patterns

## Overview

This guide provides comprehensive patterns for validating implemented features across the full stack: frontend (Next.js), backend (FastAPI), database (PostgreSQL), and authentication (Better Auth). These patterns focus on post-implementation validation to ensure features work correctly end-to-end.

## Frontend Validation Patterns

### 1. UI Component Validation

**What to Validate**:
- Component renders correctly
- Props are passed and displayed
- User interactions trigger expected behavior
- State updates reflect in UI
- Error states display correctly

**Validation Pattern**:
```
1. Navigate to page containing component
2. Wait for component to render
3. Verify component visible
4. Verify initial state correct
5. Interact with component
6. Verify state change reflected in UI
7. Verify no console errors
```

**Example: Task List Component**
```
Step 1: Navigate to /tasks
Step 2: Wait for [data-testid="task-list"]
Step 3: Verify task list visible
Step 4: Count tasks displayed
Step 5: Verify each task has title, status, actions
Step 6: Click first task
Step 7: Verify task details displayed
Step 8: Check console for errors
```

### 2. Form Validation

**What to Validate**:
- Form fields render correctly
- Client-side validation works
- Error messages display for invalid input
- Success messages display on valid submission
- Form clears/resets after submission

**Validation Pattern**:
```
1. Navigate to form page
2. Verify all form fields present
3. Test invalid input:
   - Submit empty form
   - Verify validation errors displayed
   - Verify form not submitted
4. Test valid input:
   - Fill all required fields
   - Submit form
   - Verify success message
   - Verify form cleared or redirected
5. Verify backend received data
```

**Example: Task Creation Form**
```
INVALID INPUT TEST:
  Navigate to /tasks
  Click "Add Task" button
  Click submit without filling title
  Verify error: "Title is required"
  Verify task not created

VALID INPUT TEST:
  Fill input[name="title"] with "Buy groceries"
  Click submit
  Verify success message: "Task created"
  Verify "Buy groceries" appears in task list
  Verify form cleared
```

### 3. Navigation and Routing

**What to Validate**:
- Routes navigate correctly
- Protected routes redirect unauthenticated users
- URL parameters work correctly
- Back/forward navigation works
- 404 pages display for invalid routes

**Validation Pattern**:
```
1. Test public routes:
   - Navigate to each public route
   - Verify page loads
   - Verify correct content displayed

2. Test protected routes:
   - Navigate without authentication
   - Verify redirect to login
   - Login
   - Navigate to protected route
   - Verify access granted

3. Test dynamic routes:
   - Navigate to route with parameter (e.g., /tasks/123)
   - Verify correct data loaded
   - Verify 404 for invalid parameter
```

**Example: Next.js App Router Validation**
```
PUBLIC ROUTES:
  Navigate to /
  Verify landing page displayed
  Navigate to /login
  Verify login form displayed

PROTECTED ROUTES:
  Navigate to /tasks (not logged in)
  Verify redirect to /login
  Login with valid credentials
  Verify redirect to /tasks
  Verify task list displayed

DYNAMIC ROUTES:
  Navigate to /tasks/1
  Verify task #1 details displayed
  Navigate to /tasks/99999
  Verify 404 or "Task not found" message
```

### 4. State Management Validation

**What to Validate**:
- Global state updates correctly
- Local state updates correctly
- State persists across navigation (if expected)
- State clears when expected (e.g., logout)

**Validation Pattern**:
```
1. Perform action that updates state
2. Verify UI reflects state change
3. Navigate to different page
4. Navigate back
5. Verify state persisted (if expected) or cleared (if expected)
6. Check localStorage/sessionStorage if used
```

**Example: Authentication State**
```
Step 1: Login
Step 2: Verify user indicator displayed (e.g., username)
Step 3: Navigate to /tasks
Step 4: Verify still authenticated (user indicator visible)
Step 5: Refresh page
Step 6: Verify still authenticated (session persisted)
Step 7: Logout
Step 8: Verify user indicator removed
Step 9: Verify redirect to login
```

### 5. Error Boundary Validation

**What to Validate**:
- Error boundaries catch errors
- Fallback UI displays
- Error details logged (in dev mode)
- User can recover from error

**Validation Pattern**:
```
1. Trigger error condition
2. Verify error boundary catches error
3. Verify fallback UI displayed
4. Verify error logged to console
5. Verify user can navigate away or retry
```

## Backend API Validation Patterns

### 1. API Endpoint Validation

**What to Validate**:
- Endpoint responds with correct status code
- Response payload matches expected schema
- Error responses include proper error messages
- Authentication required for protected endpoints
- Authorization enforced (user isolation)

**Validation Pattern**:
```
1. Make API request via browser (fetch/axios)
2. Capture response status code
3. Capture response body
4. Verify status code correct
5. Verify response schema correct
6. Verify data correct
7. Test error cases (invalid input, unauthorized)
```

**Example: Task API Validation**
```
GET /api/{user_id}/tasks:
  Navigate to /tasks
  Open browser DevTools Network tab
  Capture GET request to /api/1/tasks
  Verify status: 200
  Verify response: array of tasks
  Verify each task has: id, title, completed, createdAt, userId

POST /api/{user_id}/tasks:
  Fill task creation form
  Submit
  Capture POST request to /api/1/tasks
  Verify status: 201
  Verify response: created task object
  Verify task has id assigned

ERROR CASE:
  Remove auth token from localStorage
  Try to create task
  Capture POST request
  Verify status: 401
  Verify error message: "Unauthorized"
```

### 2. Request/Response Validation

**What to Validate**:
- Request headers include authentication
- Request body formatted correctly
- Response headers correct (Content-Type, etc.)
- Response time acceptable
- CORS headers present (if needed)

**Validation Pattern**:
```
1. Perform action that triggers API call
2. Capture request in Network tab
3. Verify request headers:
   - Authorization: Bearer <token>
   - Content-Type: application/json
4. Verify request body (for POST/PUT)
5. Verify response headers
6. Verify response time < threshold
```

**Example: Authentication Header Validation**
```
Step 1: Login to get token
Step 2: Navigate to /tasks
Step 3: Open DevTools Network tab
Step 4: Refresh page
Step 5: Find GET /api/1/tasks request
Step 6: Verify request headers include:
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Step 7: Verify response status: 200
```

### 3. Error Handling Validation

**What to Validate**:
- 400 errors for invalid input
- 401 errors for missing authentication
- 403 errors for insufficient permissions
- 404 errors for not found resources
- 500 errors handled gracefully
- Error messages are user-friendly

**Validation Pattern**:
```
1. Test each error scenario:
   - Invalid input → 400
   - No auth token → 401
   - Wrong user → 403
   - Invalid ID → 404
   - Server error → 500

2. For each error:
   - Verify correct status code
   - Verify error message present
   - Verify error message helpful
   - Verify UI displays error to user
```

**Example: Error Scenario Testing**
```
400 BAD REQUEST:
  Fill task form with empty title
  Submit
  Verify status: 400
  Verify error: "Title is required"
  Verify error displayed in UI

401 UNAUTHORIZED:
  Clear localStorage (remove token)
  Try to create task
  Verify status: 401
  Verify redirect to login

403 FORBIDDEN:
  Login as User A
  Try to access User B's task
  Verify status: 403
  Verify error: "Access denied"

404 NOT FOUND:
  Navigate to /tasks/99999
  Verify status: 404
  Verify error: "Task not found"
```

### 4. Data Transformation Validation

**What to Validate**:
- Frontend sends data in correct format
- Backend receives and parses data correctly
- Backend transforms data as expected
- Frontend receives and displays data correctly

**Validation Pattern**:
```
1. Create data in frontend
2. Capture request payload
3. Verify payload format correct
4. Verify backend receives data
5. Verify backend transforms data (if needed)
6. Verify backend stores data correctly
7. Fetch data from backend
8. Verify frontend receives data
9. Verify frontend displays data correctly
```

**Example: Date Handling**
```
Step 1: Create task with current date
Step 2: Capture POST request payload
Step 3: Verify date format: ISO 8601 (e.g., "2024-01-15T10:30:00Z")
Step 4: Verify backend stores date in database
Step 5: Fetch task from API
Step 6: Verify response date format: ISO 8601
Step 7: Verify frontend displays date in user-friendly format (e.g., "Jan 15, 2024")
```

## Database Validation Patterns

### 1. Data Persistence Validation

**What to Validate**:
- Data saved to database after create operation
- Data updated in database after update operation
- Data removed from database after delete operation
- Data integrity maintained (foreign keys, constraints)

**Validation Pattern**:
```
1. Perform create operation in browser
2. Verify success in UI
3. Query database directly or via API
4. Verify data exists in database
5. Verify all fields saved correctly
6. Verify relationships correct (foreign keys)
```

**Example: Task Creation Persistence**
```
Step 1: Login as User A (user_id = 1)
Step 2: Create task "Buy groceries"
Step 3: Verify task appears in UI
Step 4: Query database:
  SELECT * FROM tasks WHERE user_id = 1 AND title = 'Buy groceries'
Step 5: Verify task exists
Step 6: Verify fields:
  - id: assigned
  - title: "Buy groceries"
  - completed: false
  - user_id: 1
  - created_at: recent timestamp
```

### 2. User Isolation Validation

**What to Validate**:
- Users can only see their own data
- Users cannot access other users' data
- Database queries filter by user_id
- Foreign key constraints enforced

**Validation Pattern**:
```
1. Login as User A
2. Create data for User A
3. Verify User A can see data
4. Logout
5. Login as User B
6. Verify User B cannot see User A's data
7. Try to access User A's data directly (via URL)
8. Verify access denied
9. Query database:
   - Verify User A's data has user_id = A
   - Verify User B's data has user_id = B
   - Verify no cross-contamination
```

**Example: Task Isolation**
```
USER A:
  Login as user_a@example.com (user_id = 1)
  Create task "User A Task"
  Verify task visible in /tasks
  Query DB: SELECT * FROM tasks WHERE user_id = 1
  Verify "User A Task" exists

USER B:
  Logout
  Login as user_b@example.com (user_id = 2)
  Navigate to /tasks
  Verify "User A Task" NOT visible
  Try to navigate to /tasks/1 (User A's task)
  Verify 403 or 404 error
  Query DB: SELECT * FROM tasks WHERE user_id = 2
  Verify "User A Task" NOT in results
```

### 3. Data Integrity Validation

**What to Validate**:
- Foreign key constraints enforced
- NOT NULL constraints enforced
- UNIQUE constraints enforced
- CHECK constraints enforced
- Cascading deletes work correctly

**Validation Pattern**:
```
1. Test constraint violations:
   - Try to insert NULL in NOT NULL field
   - Try to insert duplicate in UNIQUE field
   - Try to insert invalid foreign key
   - Try to violate CHECK constraint

2. For each violation:
   - Verify operation fails
   - Verify error message clear
   - Verify database unchanged

3. Test cascading operations:
   - Delete parent record
   - Verify child records deleted (if CASCADE)
   - OR verify deletion blocked (if RESTRICT)
```

**Example: Foreign Key Constraint**
```
Step 1: Try to create task with invalid user_id
  POST /api/999/tasks (user 999 doesn't exist)
Step 2: Verify error: 400 or 403
Step 3: Query database:
  SELECT * FROM tasks WHERE user_id = 999
Step 4: Verify no task created

Step 5: Delete user
  DELETE FROM users WHERE id = 1
Step 6: Verify tasks for user 1 also deleted (if CASCADE)
  SELECT * FROM tasks WHERE user_id = 1
Step 7: Verify no tasks remain
```

### 4. Transaction Validation

**What to Validate**:
- Transactions commit on success
- Transactions rollback on failure
- Data consistency maintained
- No partial updates

**Validation Pattern**:
```
1. Perform operation that should be atomic
2. Verify all changes committed together
3. Trigger error mid-operation
4. Verify all changes rolled back
5. Verify database in consistent state
```

**Example: Task Creation with Validation**
```
SUCCESS CASE:
  Create task with valid data
  Verify task created
  Verify all fields saved
  Verify transaction committed

FAILURE CASE:
  Create task with invalid data (e.g., title too long)
  Verify error returned
  Verify task NOT created
  Verify database unchanged
  Verify transaction rolled back
```

## Authentication Validation Patterns

### 1. Better Auth Signup Flow

**What to Validate**:
- Signup form accepts valid input
- User created in database
- Password hashed (not stored in plain text)
- Email verification sent (if enabled)
- User redirected after signup

**Validation Pattern**:
```
1. Navigate to /signup
2. Fill signup form:
   - Email
   - Password
   - Confirm password
3. Submit form
4. Verify success message or redirect
5. Query database:
   - Verify user exists
   - Verify email correct
   - Verify password hashed
6. Verify email sent (if enabled)
7. Verify user can login
```

**Example: Better Auth Signup**
```
Step 1: Navigate to /signup
Step 2: Fill form:
  - email: "newuser@example.com"
  - password: "SecurePass123!"
  - confirmPassword: "SecurePass123!"
Step 3: Click "Sign Up"
Step 4: Verify redirect to /login or /dashboard
Step 5: Query database:
  SELECT * FROM users WHERE email = 'newuser@example.com'
Step 6: Verify user exists
Step 7: Verify password_hash starts with "$2b$" (bcrypt)
Step 8: Login with credentials
Step 9: Verify login successful
```

### 2. Better Auth Login Flow

**What to Validate**:
- Login form accepts credentials
- JWT token issued on successful login
- Token stored in localStorage/cookies
- Token includes correct claims (user_id, exp)
- User redirected to dashboard
- Protected routes accessible after login

**Validation Pattern**:
```
1. Navigate to /login
2. Fill login form:
   - Email
   - Password
3. Submit form
4. Verify redirect to dashboard
5. Capture JWT token:
   - Check localStorage
   - OR check cookies
6. Decode JWT token
7. Verify claims:
   - sub: user_id
   - exp: expiration time
   - iat: issued at time
8. Navigate to protected route
9. Verify access granted
```

**Example: Better Auth Login**
```
Step 1: Navigate to /login
Step 2: Fill form:
  - email: "test@example.com"
  - password: "password123"
Step 3: Click "Login"
Step 4: Verify redirect to /dashboard
Step 5: Evaluate JavaScript:
  const token = localStorage.getItem('better-auth-token')
Step 6: Verify token exists
Step 7: Decode token (base64 decode middle part):
  {
    "sub": "1",
    "email": "test@example.com",
    "iat": 1705334400,
    "exp": 1705420800
  }
Step 8: Verify sub matches user_id
Step 9: Navigate to /tasks
Step 10: Verify tasks displayed (not redirected to login)
```

### 3. JWT Token Validation

**What to Validate**:
- Token attached to API requests
- Backend validates token signature
- Backend verifies token not expired
- Backend extracts user_id from token
- Invalid token returns 401
- Expired token returns 401

**Validation Pattern**:
```
1. Login to get valid token
2. Make API request
3. Verify token in Authorization header
4. Verify request succeeds (200)
5. Modify token (make invalid)
6. Make API request with invalid token
7. Verify request fails (401)
8. Use expired token
9. Make API request with expired token
10. Verify request fails (401)
```

**Example: JWT Validation**
```
VALID TOKEN:
  Login
  Capture token from localStorage
  Navigate to /tasks
  Open DevTools Network tab
  Find GET /api/1/tasks request
  Verify Authorization header: Bearer {token}
  Verify response: 200

INVALID TOKEN:
  Modify token in localStorage (change last character)
  Refresh /tasks page
  Verify redirect to /login
  OR verify error: "Invalid token"

EXPIRED TOKEN:
  Set token with past expiration
  Navigate to /tasks
  Verify redirect to /login
  OR verify error: "Token expired"
```

### 4. Session Management

**What to Validate**:
- Session persists across page refreshes
- Session persists across browser tabs
- Session expires after timeout (if configured)
- Logout clears session
- Logout invalidates token

**Validation Pattern**:
```
1. Login
2. Verify session active
3. Refresh page
4. Verify still logged in
5. Open new tab
6. Navigate to protected route
7. Verify still logged in
8. Logout in first tab
9. Verify logged out in both tabs
10. Try to use old token
11. Verify token invalid
```

**Example: Session Persistence**
```
Step 1: Login at /login
Step 2: Navigate to /tasks
Step 3: Verify tasks displayed
Step 4: Refresh page (F5)
Step 5: Verify still on /tasks (not redirected to login)
Step 6: Open new tab
Step 7: Navigate to /tasks in new tab
Step 8: Verify tasks displayed (session shared)
Step 9: Logout in first tab
Step 10: Refresh second tab
Step 11: Verify redirect to /login (session cleared)
```

## Cross-Layer Validation Patterns

### 1. End-to-End Flow Validation

**What to Validate**:
- Complete user journey works
- All layers integrate correctly
- Data flows through all layers
- No broken connections

**Validation Pattern**:
```
1. Start from user action in browser
2. Verify frontend handles action
3. Verify API request sent
4. Verify backend receives request
5. Verify backend processes request
6. Verify database updated
7. Verify response sent to frontend
8. Verify frontend updates UI
9. Verify user sees result
```

**Example: Task Creation E2E**
```
FRONTEND:
  Navigate to /tasks
  Click "Add Task"
  Fill title: "Buy groceries"
  Click "Submit"

API:
  Capture POST /api/1/tasks
  Verify request body: {"title": "Buy groceries"}
  Verify Authorization header present
  Verify response: 201 Created
  Verify response body: {id: 5, title: "Buy groceries", ...}

DATABASE:
  Query: SELECT * FROM tasks WHERE id = 5
  Verify task exists
  Verify title: "Buy groceries"
  Verify user_id: 1

FRONTEND:
  Verify "Buy groceries" appears in task list
  Verify success message displayed
  Verify form cleared
```

### 2. Error Propagation Validation

**What to Validate**:
- Errors propagate correctly through layers
- Error messages user-friendly
- Error details logged for debugging
- User can recover from errors

**Validation Pattern**:
```
1. Trigger error at each layer:
   - Frontend validation error
   - API error (400, 401, 403, 404, 500)
   - Database error (constraint violation)

2. For each error:
   - Verify error caught
   - Verify error message displayed to user
   - Verify error logged to console
   - Verify user can retry or navigate away
```

**Example: Error Propagation**
```
FRONTEND VALIDATION ERROR:
  Submit form with empty title
  Verify error message: "Title is required"
  Verify form not submitted
  Verify no API call made

API ERROR (401):
  Remove auth token
  Try to create task
  Verify API returns 401
  Verify frontend displays: "Please login"
  Verify redirect to /login

DATABASE ERROR:
  Try to create task with duplicate unique field
  Verify API returns 400
  Verify frontend displays: "Task already exists"
  Verify user can modify and retry
```

## Best Practices

### 1. Validation Checklist

For each implemented feature, validate:
- [ ] Frontend renders correctly
- [ ] User interactions work
- [ ] Form validation works
- [ ] API requests sent correctly
- [ ] API responses handled correctly
- [ ] Database persistence confirmed
- [ ] User isolation enforced
- [ ] Authentication required
- [ ] Error handling works
- [ ] Success messages displayed

### 2. Validation Order

Validate in this order:
1. Frontend (UI renders, interactions work)
2. API (requests sent, responses received)
3. Database (data persisted correctly)
4. Authentication (tokens valid, sessions work)
5. End-to-end (complete flow works)

### 3. Documentation

Document validation results:
- What was tested
- What passed
- What failed
- Screenshots of failures
- Steps to reproduce failures
- Suggested fixes

### 4. Automation

Automate repetitive validations:
- Login flow
- CRUD operations
- User isolation tests
- Error scenarios
- Regression tests
