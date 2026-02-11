# Debugging Strategies for Browser Automation

## Overview

This guide provides comprehensive debugging strategies for identifying and resolving issues during browser-based implementation validation. It covers error capture, log analysis, network inspection, and systematic troubleshooting approaches.

## Error Capture Strategies

### 1. Screenshot Capture

**When to Capture Screenshots**:
- Before critical actions (baseline)
- After critical actions (verification)
- When assertions fail
- When unexpected errors occur
- At test completion (final state)

**Screenshot Naming Convention**:
```
{test-name}-{step}-{timestamp}-{status}.png

Examples:
- login-flow-01-before-submit-20240115-103045-baseline.png
- login-flow-02-after-submit-20240115-103046-success.png
- task-creation-03-error-20240115-103047-failure.png
```

**Screenshot Capture Pattern**:
```
1. Define screenshot points in test flow
2. Capture screenshot at each point
3. Name screenshot descriptively
4. Store in organized directory structure
5. Include screenshots in test report
6. Compare before/after screenshots for visual debugging
```

**Example: Login Flow Screenshots**
```
Step 1: Navigate to /login
  Screenshot: login-01-page-loaded.png

Step 2: Fill email field
  Screenshot: login-02-email-filled.png

Step 3: Fill password field
  Screenshot: login-03-password-filled.png

Step 4: Click submit button
  Screenshot: login-04-before-submit.png

Step 5: Wait for redirect
  Screenshot: login-05-after-submit.png

If error occurs:
  Screenshot: login-error-{error-type}.png
```

### 2. Console Log Capture

**What to Capture**:
- console.log messages
- console.error messages
- console.warn messages
- console.info messages
- Uncaught exceptions
- Promise rejections

**Console Log Pattern**:
```
1. Enable console log capture before test
2. Collect all console messages during test
3. Categorize by level (log, error, warn, info)
4. Include timestamps
5. Include stack traces for errors
6. Report in test results
```

**Implementation via Playwright**:
```javascript
// Capture console messages
page.on('console', msg => {
  const type = msg.type();
  const text = msg.text();
  const timestamp = new Date().toISOString();

  consoleLogs.push({
    type,
    text,
    timestamp,
    location: msg.location()
  });
});

// Capture uncaught exceptions
page.on('pageerror', error => {
  consoleErrors.push({
    message: error.message,
    stack: error.stack,
    timestamp: new Date().toISOString()
  });
});
```

**Example: Console Log Analysis**
```
CAPTURED LOGS:
[2024-01-15 10:30:45] [LOG] "User logged in successfully"
[2024-01-15 10:30:46] [LOG] "Fetching tasks for user 1"
[2024-01-15 10:30:47] [ERROR] "Failed to fetch tasks: 401 Unauthorized"
[2024-01-15 10:30:47] [WARN] "Token may be expired, redirecting to login"

ANALYSIS:
- Login succeeded (log message)
- Task fetch attempted (log message)
- Task fetch failed with 401 (error message)
- Token expiration suspected (warning message)
- ACTION: Check token expiration time and refresh logic
```

### 3. Network Request Capture

**What to Capture**:
- Request URL
- Request method (GET, POST, PUT, DELETE)
- Request headers (especially Authorization)
- Request body (for POST/PUT)
- Response status code
- Response headers
- Response body
- Response time
- Failed requests (4xx, 5xx)

**Network Capture Pattern**:
```
1. Enable network request tracking
2. Capture all requests during test
3. Filter relevant requests (API calls)
4. Store request/response details
5. Identify failed requests
6. Include in test report
```

**Implementation via Playwright**:
```javascript
// Capture network requests
page.on('request', request => {
  if (request.url().includes('/api/')) {
    networkRequests.push({
      url: request.url(),
      method: request.method(),
      headers: request.headers(),
      postData: request.postData(),
      timestamp: new Date().toISOString()
    });
  }
});

// Capture network responses
page.on('response', response => {
  if (response.url().includes('/api/')) {
    networkResponses.push({
      url: response.url(),
      status: response.status(),
      headers: response.headers(),
      timestamp: new Date().toISOString()
    });
  }
});
```

**Example: Network Request Analysis**
```
REQUEST:
  URL: POST http://localhost:3000/api/1/tasks
  Headers:
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    Content-Type: application/json
  Body: {"title": "Buy groceries"}
  Time: 2024-01-15 10:30:45

RESPONSE:
  Status: 401 Unauthorized
  Headers:
    Content-Type: application/json
  Body: {"error": "Invalid token"}
  Time: 2024-01-15 10:30:46
  Duration: 1000ms

ANALYSIS:
- Request sent with Authorization header
- Token present but invalid
- Backend rejected request with 401
- ACTION: Check token validity, verify BETTER_AUTH_SECRET matches
```

### 4. DOM State Capture

**What to Capture**:
- Page HTML at error point
- Element attributes
- Element visibility state
- Element position
- Computed styles
- JavaScript state (via evaluate)

**DOM Capture Pattern**:
```
1. When error occurs, capture page HTML
2. Capture specific element details
3. Capture JavaScript state variables
4. Store in error report
5. Use for post-mortem analysis
```

**Example: Element Not Found Debugging**
```
ERROR: Element 'button[type="submit"]' not found

CAPTURED DOM STATE:
  Page HTML: <html>...</html>

  Search for submit button:
    - Found: <button type="button">Submit</button>
    - Issue: type="button" instead of type="submit"

  JavaScript State:
    - formValid: false
    - submitDisabled: true

ANALYSIS:
- Button exists but with wrong type attribute
- Button is disabled due to form validation
- ACTION: Update selector to button:has-text("Submit")
- OR: Fix form validation to enable button
```

## Log Analysis Strategies

### 1. Error Pattern Recognition

**Common Error Patterns**:

| Error Pattern | Likely Cause | Debugging Steps |
|---------------|--------------|-----------------|
| "401 Unauthorized" | Missing or invalid token | Check token in localStorage, verify BETTER_AUTH_SECRET |
| "403 Forbidden" | User accessing wrong resource | Check user_id in URL vs token, verify authorization |
| "404 Not Found" | Invalid route or resource ID | Check URL, verify resource exists in database |
| "Network request failed" | Backend not running | Check backend server status, verify port |
| "Element not found" | Wrong selector or timing | Check selector, increase timeout, verify element renders |
| "CORS error" | CORS not configured | Check backend CORS settings, verify origin allowed |

**Pattern Recognition Process**:
```
1. Collect all error messages
2. Identify common patterns
3. Group similar errors
4. Prioritize by frequency
5. Investigate root cause
6. Apply fix
7. Verify fix resolves all instances
```

### 2. Timeline Analysis

**Timeline Construction**:
```
1. Collect all events with timestamps:
   - User actions
   - Network requests
   - Console logs
   - State changes
   - Errors

2. Sort chronologically

3. Identify sequence of events leading to error

4. Find deviation from expected flow

5. Pinpoint exact failure point
```

**Example: Login Failure Timeline**
```
10:30:45.000 - User navigates to /login
10:30:45.100 - Page loaded
10:30:45.200 - User fills email: "test@example.com"
10:30:45.300 - User fills password: "password123"
10:30:45.400 - User clicks submit button
10:30:45.500 - POST /api/auth/login sent
10:30:45.600 - Response: 401 Unauthorized
10:30:45.700 - Error displayed: "Invalid credentials"
10:30:45.800 - User remains on /login page

ANALYSIS:
- All steps executed correctly
- Backend rejected credentials
- Possible causes:
  1. Wrong password in test data
  2. User doesn't exist in database
  3. Password hashing mismatch
- ACTION: Verify test user exists, verify password correct
```

### 3. Correlation Analysis

**Correlate Multiple Data Sources**:
```
1. Console logs
2. Network requests
3. Database queries
4. User actions
5. State changes

Find relationships:
- Which user action triggered which API call?
- Which API call caused which error?
- Which state change caused which UI update?
```

**Example: Task Creation Failure**
```
USER ACTION:
  10:30:45 - Click "Add Task" button

CONSOLE LOG:
  10:30:45 - "Creating task: Buy groceries"

NETWORK REQUEST:
  10:30:45 - POST /api/1/tasks
  Body: {"title": "Buy groceries"}

NETWORK RESPONSE:
  10:30:46 - 400 Bad Request
  Body: {"error": "Title too long"}

CONSOLE ERROR:
  10:30:46 - "Task creation failed: Title too long"

UI STATE:
  10:30:46 - Error message displayed

ANALYSIS:
- User action triggered task creation
- Frontend sent request with title "Buy groceries" (14 chars)
- Backend rejected with "Title too long"
- Inconsistency: 14 chars should not be too long
- ACTION: Check backend validation logic, may have bug
```

## Network Inspection Strategies

### 1. Request Header Analysis

**What to Check**:
- Authorization header present
- Authorization header format correct
- Content-Type header correct
- Custom headers present (if needed)

**Debugging Pattern**:
```
1. Capture request headers
2. Verify Authorization header:
   - Format: "Bearer <token>"
   - Token not empty
   - Token not expired
3. Verify Content-Type:
   - "application/json" for JSON payloads
4. Check for missing headers
```

**Example: Missing Authorization Header**
```
REQUEST:
  POST /api/1/tasks
  Headers:
    Content-Type: application/json
  Body: {"title": "Buy groceries"}

RESPONSE:
  401 Unauthorized

ANALYSIS:
- Authorization header missing
- Backend requires authentication
- ACTION: Check if token stored in localStorage
- ACTION: Verify token attached to request
```

### 2. Response Analysis

**What to Check**:
- Status code matches expectation
- Response body format correct
- Error messages clear
- Response time acceptable

**Debugging Pattern**:
```
1. Check status code:
   - 2xx: Success
   - 4xx: Client error
   - 5xx: Server error

2. Parse response body:
   - JSON format valid?
   - Expected fields present?
   - Error message clear?

3. Check response time:
   - < 200ms: Fast
   - 200-1000ms: Acceptable
   - > 1000ms: Slow (investigate)
```

**Example: Unexpected Response Format**
```
REQUEST:
  GET /api/1/tasks

RESPONSE:
  Status: 200 OK
  Body: "<!DOCTYPE html><html>..."

EXPECTED:
  Status: 200 OK
  Body: [{"id": 1, "title": "Task 1", ...}]

ANALYSIS:
- Status code correct (200)
- But response is HTML, not JSON
- Backend returning error page instead of JSON
- ACTION: Check backend route, verify JSON response configured
```

### 3. Failed Request Debugging

**Debugging Steps for Failed Requests**:
```
1. Identify failed request (4xx or 5xx)
2. Capture full request details
3. Capture full response details
4. Reproduce request manually (curl or Postman)
5. Compare with working request
6. Identify difference
7. Fix issue
```

**Example: 403 Forbidden Debugging**
```
FAILED REQUEST:
  GET /api/2/tasks/1
  Headers:
    Authorization: Bearer {user1_token}
  Response: 403 Forbidden

ANALYSIS:
- User 1 trying to access User 2's tasks
- Token valid but for wrong user
- Backend correctly enforcing user isolation

WORKING REQUEST:
  GET /api/1/tasks/1
  Headers:
    Authorization: Bearer {user1_token}
  Response: 200 OK

DIFFERENCE:
- URL user_id: 2 vs 1
- Token user_id: 1 (same in both)
- ACTION: Frontend should use user_id from token, not hardcoded
```

## Systematic Troubleshooting

### 1. Binary Search Debugging

**When to Use**: Complex flows with many steps

**Process**:
```
1. Identify failing test with N steps
2. Test first N/2 steps
3. If pass: Issue in second half
4. If fail: Issue in first half
5. Repeat until issue isolated to single step
```

**Example: Login → Create Task Flow Fails**
```
Full flow (10 steps):
  1. Navigate to /login
  2. Fill email
  3. Fill password
  4. Submit login
  5. Wait for redirect
  6. Navigate to /tasks
  7. Click "Add Task"
  8. Fill task title
  9. Submit task
  10. Verify task created

Test first 5 steps:
  Result: PASS

Test steps 6-10:
  Result: FAIL

Test steps 6-8:
  Result: PASS

Test steps 9-10:
  Result: FAIL

Test step 9:
  Result: FAIL

ISOLATED: Step 9 (Submit task) is failing
```

### 2. Differential Debugging

**When to Use**: Feature works in one environment but not another

**Process**:
```
1. Identify working environment
2. Identify failing environment
3. List differences:
   - Browser version
   - Backend version
   - Database state
   - Environment variables
   - Network conditions
4. Test each difference
5. Identify root cause
```

**Example: Works Locally, Fails in CI**
```
LOCAL (WORKS):
  - Browser: Chrome 120
  - Backend: localhost:8000
  - Database: Local PostgreSQL
  - Token: Never expires
  - Network: Fast

CI (FAILS):
  - Browser: Chrome 120 (same)
  - Backend: CI server
  - Database: CI PostgreSQL
  - Token: Expires in 1 hour
  - Network: Slower

DIFFERENCE TESTING:
  Test with 1-hour token locally: FAILS

ROOT CAUSE:
  - Token expires during test execution
  - Local tests use non-expiring token
  - CI tests use expiring token
  - ACTION: Refresh token during long tests
```

### 3. Isolation Testing

**When to Use**: Multiple features failing

**Process**:
```
1. Test each feature independently
2. Identify which features fail in isolation
3. Identify which features fail only when combined
4. Focus on interaction between combined features
```

**Example: Login + Task Creation Both Fail**
```
Test Login alone:
  Result: PASS

Test Task Creation alone (with pre-authenticated user):
  Result: PASS

Test Login → Task Creation:
  Result: FAIL

ANALYSIS:
- Both features work independently
- Combination fails
- Possible causes:
  1. Token not persisted after login
  2. State not shared between pages
  3. Redirect clears authentication
- ACTION: Check token persistence, verify state management
```

## Debugging Workflows

### 1. Frontend Issue Debugging

```
1. Verify page loads
   - Screenshot page
   - Check console for errors
   - Verify no network errors

2. Verify element renders
   - Check element exists in DOM
   - Check element visible
   - Check element not covered

3. Verify interaction works
   - Try manual interaction
   - Check event handlers attached
   - Check JavaScript errors

4. Verify state updates
   - Check state before action
   - Perform action
   - Check state after action
   - Verify UI reflects state
```

### 2. Backend Issue Debugging

```
1. Verify backend running
   - Check server logs
   - Try health check endpoint
   - Verify port accessible

2. Verify request received
   - Check backend logs for request
   - Verify request format correct
   - Verify authentication present

3. Verify request processed
   - Check backend processing logs
   - Verify database query executed
   - Check for errors in processing

4. Verify response sent
   - Check response format
   - Verify status code
   - Check response body
```

### 3. Database Issue Debugging

```
1. Verify database accessible
   - Check connection
   - Try simple query
   - Verify credentials correct

2. Verify data exists
   - Query for expected data
   - Check data format
   - Verify relationships

3. Verify constraints
   - Check foreign keys
   - Check unique constraints
   - Check NOT NULL constraints

4. Verify permissions
   - Check user permissions
   - Verify row-level security
   - Check access policies
```

### 4. Authentication Issue Debugging

```
1. Verify token issued
   - Check login response
   - Verify token in localStorage/cookies
   - Decode token, check claims

2. Verify token valid
   - Check expiration time
   - Verify signature
   - Check issuer

3. Verify token sent
   - Check Authorization header
   - Verify format: "Bearer <token>"
   - Check token not empty

4. Verify token accepted
   - Check backend validation
   - Verify BETTER_AUTH_SECRET matches
   - Check user_id extraction
```

## Debugging Tools and Techniques

### 1. Browser DevTools

**Console Tab**:
- View console logs
- Execute JavaScript
- Check for errors

**Network Tab**:
- View all requests
- Filter by type (XHR, Fetch)
- Check request/response details
- Check timing

**Elements Tab**:
- Inspect DOM
- Check element styles
- Modify elements live
- Check event listeners

**Application Tab**:
- View localStorage
- View cookies
- View session storage
- Clear storage

### 2. Playwright Inspector

**Features**:
- Step through test
- Pause on error
- Inspect page state
- View selector
- Record actions

**Usage**:
```
1. Run test with inspector
2. Pause at failure point
3. Inspect page state
4. Try different selectors
5. Modify test
6. Continue execution
```

### 3. Logging Strategies

**Strategic Logging**:
```
1. Log before critical actions
2. Log after critical actions
3. Log state changes
4. Log API calls
5. Log errors with context
```

**Example: Comprehensive Logging**
```
[INFO] Starting login flow
[DEBUG] Navigating to /login
[DEBUG] Page loaded: /login
[DEBUG] Filling email: test@example.com
[DEBUG] Filling password: ********
[DEBUG] Clicking submit button
[INFO] Login request sent
[DEBUG] Request: POST /api/auth/login
[DEBUG] Response: 200 OK
[DEBUG] Token received: eyJhbGci...
[DEBUG] Token stored in localStorage
[INFO] Login successful
[DEBUG] Redirecting to /dashboard
[INFO] Login flow completed
```

## Best Practices

### 1. Capture Everything

- Screenshots at every step
- Console logs continuously
- Network requests all
- DOM state on errors
- Timestamps for all events

### 2. Organize Debug Data

```
debug-output/
├── screenshots/
│   ├── login-01-page-loaded.png
│   ├── login-02-email-filled.png
│   └── login-error.png
├── logs/
│   ├── console.log
│   ├── network.log
│   └── errors.log
├── reports/
│   ├── test-report.html
│   └── debug-report.json
└── artifacts/
    ├── page-html.html
    └── dom-state.json
```

### 3. Reproduce Reliably

- Document exact steps to reproduce
- Include environment details
- Note timing/race conditions
- Provide minimal reproduction case

### 4. Fix and Verify

- Apply fix
- Run failing test
- Verify test passes
- Run related tests
- Verify no regressions
- Document fix
