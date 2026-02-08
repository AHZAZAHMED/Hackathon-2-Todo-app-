# Playwright MCP Automation Patterns

## Overview

This guide covers browser automation patterns using the Playwright MCP (Model Context Protocol) server through the browsing-with-playwright skill. The MCP server provides a structured interface for browser automation without requiring direct Playwright API access.

## MCP Server Architecture

### What is Playwright MCP Server?

The Playwright MCP server is a Model Context Protocol implementation that exposes Playwright browser automation capabilities through a standardized interface. It allows Claude Code to control browsers via the browsing-with-playwright skill.

**Key Components**:
- **MCP Server**: Runs Playwright and exposes automation tools
- **browsing-with-playwright skill**: Claude Code skill that communicates with MCP server
- **Browser Instance**: Chromium/Firefox/WebKit controlled by MCP server
- **Page Context**: Individual browser tabs/pages managed by server

### MCP vs Direct Playwright API

| Aspect | MCP Server | Direct Playwright API |
|--------|------------|----------------------|
| **Access** | Via browsing-with-playwright skill | Requires Playwright installation |
| **Interface** | Structured tool calls | JavaScript/Python API |
| **State Management** | Server manages browser state | Manual state management |
| **Error Handling** | Standardized error responses | Custom error handling |
| **Debugging** | Built-in screenshot/log capture | Manual debugging setup |

## Using browsing-with-playwright Skill

### Skill Invocation Pattern

```
User/Claude: "Use browsing-with-playwright to navigate to http://localhost:3000"
       ↓
Claude Code invokes browsing-with-playwright skill
       ↓
Skill sends tool call to Playwright MCP server
       ↓
MCP server executes browser action
       ↓
Result returned to Claude Code
```

### Available MCP Tools

The Playwright MCP server typically exposes these tools:

| Tool | Purpose | Example |
|------|---------|---------|
| `playwright_navigate` | Navigate to URL | Navigate to login page |
| `playwright_click` | Click element | Click submit button |
| `playwright_fill` | Fill input field | Enter username |
| `playwright_screenshot` | Capture screenshot | Debug visual issues |
| `playwright_evaluate` | Run JavaScript | Get page state |
| `playwright_wait_for_selector` | Wait for element | Wait for loading to complete |
| `playwright_get_text` | Extract text content | Verify displayed text |
| `playwright_get_attribute` | Get element attribute | Check input value |

**Note**: Exact tool names may vary based on MCP server implementation. Use browsing-with-playwright skill documentation for precise tool names.

## Browser Automation Workflows

### 1. Basic Navigation and Interaction

```
Workflow: Navigate → Wait → Interact → Verify

1. Navigate to page
   - Use: playwright_navigate
   - Input: URL (e.g., "http://localhost:3000")
   - Wait for: Page load complete

2. Wait for element
   - Use: playwright_wait_for_selector
   - Input: CSS selector (e.g., "button[type='submit']")
   - Timeout: 5000ms (default)

3. Interact with element
   - Use: playwright_click or playwright_fill
   - Input: Selector + value (for fill)
   - Wait for: Action complete

4. Verify result
   - Use: playwright_get_text or playwright_screenshot
   - Check: Expected outcome
```

**Example: Login Flow**
```
Step 1: Navigate to http://localhost:3000/login
Step 2: Wait for input[name="email"]
Step 3: Fill input[name="email"] with "test@example.com"
Step 4: Fill input[name="password"] with "password123"
Step 5: Click button[type="submit"]
Step 6: Wait for navigation to /dashboard
Step 7: Verify text "Welcome" is visible
```

### 2. Form Submission Pattern

```
Workflow: Fill Form → Submit → Wait → Verify

1. Fill all form fields
   - For each field:
     - Wait for selector
     - Fill with value
     - Verify value entered

2. Submit form
   - Click submit button
   - OR press Enter key
   - Wait for submission

3. Wait for response
   - Wait for navigation
   - OR wait for success message
   - OR wait for error message

4. Verify outcome
   - Check URL changed
   - Check success message displayed
   - Check error message if expected
```

**Example: Task Creation**
```
Step 1: Navigate to http://localhost:3000/tasks
Step 2: Wait for input[name="title"]
Step 3: Fill input[name="title"] with "Buy groceries"
Step 4: Click button:has-text("Add Task")
Step 5: Wait for text "Buy groceries" in task list
Step 6: Screenshot for verification
```

### 3. Authentication Flow Pattern

```
Workflow: Signup → Login → Verify Session → Test Protected Route

1. Signup
   - Navigate to /signup
   - Fill email, password, confirm password
   - Submit form
   - Verify success message or redirect

2. Login
   - Navigate to /login
   - Fill email, password
   - Submit form
   - Wait for redirect to dashboard

3. Verify session
   - Check for user indicator (e.g., username displayed)
   - Verify protected content visible
   - Check localStorage/cookies for token (via evaluate)

4. Test protected route
   - Navigate to protected page
   - Verify access granted (not redirected to login)
   - Verify user-specific content displayed
```

**Example: Better Auth Flow**
```
Step 1: Navigate to http://localhost:3000/signup
Step 2: Fill input[name="email"] with "newuser@example.com"
Step 3: Fill input[name="password"] with "SecurePass123!"
Step 4: Fill input[name="confirmPassword"] with "SecurePass123!"
Step 5: Click button:has-text("Sign Up")
Step 6: Wait for redirect to /login or /dashboard
Step 7: Evaluate: localStorage.getItem('better-auth-token')
Step 8: Verify token exists
Step 9: Navigate to /tasks (protected route)
Step 10: Verify not redirected to /login
```

### 4. CRUD Operations Pattern

```
Workflow: Create → Read → Update → Delete

1. Create
   - Navigate to creation page/form
   - Fill required fields
   - Submit
   - Verify item appears in list

2. Read
   - Navigate to list page
   - Verify item exists
   - Click to view details
   - Verify all fields displayed correctly

3. Update
   - Click edit button
   - Modify fields
   - Submit
   - Verify changes reflected

4. Delete
   - Click delete button
   - Confirm deletion (if modal)
   - Verify item removed from list
```

**Example: Task CRUD**
```
CREATE:
  Navigate to /tasks
  Fill input[name="title"] with "Test Task"
  Click button:has-text("Add")
  Wait for "Test Task" in list

READ:
  Click on "Test Task"
  Verify title displayed
  Verify created date displayed

UPDATE:
  Click button:has-text("Edit")
  Fill input[name="title"] with "Updated Task"
  Click button:has-text("Save")
  Verify "Updated Task" displayed

DELETE:
  Click button:has-text("Delete")
  Click button:has-text("Confirm") (if modal)
  Verify "Updated Task" not in list
```

## Error Handling and Debugging

### 1. Screenshot Capture

**When to Capture Screenshots**:
- Before and after critical actions
- When assertion fails
- When unexpected error occurs
- At end of test flow

**Pattern**:
```
1. Perform action
2. If error or assertion fails:
   - Capture screenshot
   - Include in error report
   - Name: {test-name}-{timestamp}-error.png
3. Continue or abort based on severity
```

### 2. Console Log Capture

**Pattern**:
```
1. Before test starts:
   - Enable console log capture
   - Listen for console.log, console.error, console.warn

2. During test:
   - Collect all console messages
   - Note timestamps

3. After test:
   - Include console logs in report
   - Highlight errors and warnings
```

**Using playwright_evaluate**:
```javascript
// Capture console errors
const errors = await page.evaluate(() => {
  return window.__consoleErrors || [];
});
```

### 3. Network Request Inspection

**Pattern**:
```
1. Before test:
   - Enable network request tracking
   - Listen for request/response events

2. During test:
   - Capture API calls
   - Note status codes
   - Capture request/response bodies

3. After test:
   - Verify expected API calls made
   - Check for failed requests (4xx, 5xx)
   - Include in report
```

**Key Requests to Track**:
- Authentication requests (login, signup)
- CRUD API calls (POST, GET, PUT, DELETE)
- Failed requests (status >= 400)

### 4. Element Not Found Handling

**Pattern**:
```
1. Wait for element with timeout
2. If timeout:
   - Capture screenshot
   - Log page HTML (via evaluate)
   - Check if page loaded correctly
   - Report specific selector that failed
3. Provide actionable error:
   - "Element 'button[type=submit]' not found on page /login"
   - "Screenshot: login-error-{timestamp}.png"
   - "Possible causes: Element not rendered, wrong selector, page not loaded"
```

## State Management

### 1. Browser Context Persistence

**Pattern**:
```
1. Create browser context at start
2. Reuse context across multiple pages
3. Maintain authentication state
4. Close context at end
```

**Benefits**:
- Faster test execution (no repeated login)
- Maintains cookies and localStorage
- Simulates real user session

### 2. Authentication State

**Pattern**:
```
1. Login once at test start
2. Store authentication token
3. Reuse token for subsequent tests
4. Verify token still valid before each test
5. Re-login if token expired
```

**Implementation**:
```
Step 1: Login and capture token
  - Navigate to /login
  - Fill credentials
  - Submit
  - Evaluate: localStorage.getItem('better-auth-token')
  - Store token

Step 2: Reuse token for next test
  - Navigate to page
  - Evaluate: localStorage.setItem('better-auth-token', storedToken)
  - Refresh page
  - Verify authenticated
```

### 3. Database State Verification

**Pattern**:
```
1. Perform browser action (e.g., create task)
2. Verify in UI (task appears in list)
3. Verify in database:
   - Query database directly
   - OR use API endpoint to fetch data
   - Confirm data persisted correctly
4. Report both UI and DB verification results
```

## Best Practices

### 1. Selector Strategies

**Priority Order**:
1. **Test IDs**: `[data-testid="submit-button"]` (most stable)
2. **Semantic selectors**: `button[type="submit"]`, `input[name="email"]`
3. **Text content**: `button:has-text("Submit")`
4. **CSS classes**: `.submit-btn` (least stable, avoid if possible)

**Why**:
- Test IDs don't change with styling
- Semantic selectors are meaningful
- Text content is user-facing
- CSS classes change frequently

### 2. Wait Strategies

**Always wait for**:
- Page navigation complete
- Element visible before interaction
- Network requests complete (for API-dependent content)
- Animations/transitions complete

**Timeout Guidelines**:
- Element appearance: 5000ms
- Page navigation: 10000ms
- API response: 15000ms
- Animation: 1000ms

### 3. Assertion Patterns

**Verify multiple aspects**:
```
After action:
1. Visual verification (screenshot)
2. Text content verification (get_text)
3. Element state verification (get_attribute)
4. URL verification (current URL)
5. Database verification (query DB)
```

### 4. Error Recovery

**Pattern**:
```
1. Try action
2. If fails:
   - Capture debugging info
   - Try recovery action (e.g., refresh page)
   - Retry original action
3. If still fails:
   - Report detailed error
   - Include all debugging info
   - Abort or continue based on severity
```

## Common Patterns

### Pattern 1: Login and Navigate

```
1. Navigate to /login
2. Wait for input[name="email"]
3. Fill email
4. Fill password
5. Click submit
6. Wait for redirect to /dashboard
7. Verify authenticated (check for user indicator)
8. Navigate to target page
```

### Pattern 2: Create Item and Verify

```
1. Navigate to creation page
2. Fill form fields
3. Submit form
4. Wait for success message or redirect
5. Verify item in list (UI verification)
6. Query database (DB verification)
7. Compare UI and DB data
```

### Pattern 3: Test Error Handling

```
1. Navigate to form
2. Submit with invalid data
3. Wait for error message
4. Verify error message displayed
5. Verify form not submitted (no redirect)
6. Verify database unchanged
```

### Pattern 4: Test Authorization

```
1. Login as User A
2. Create item for User A
3. Logout
4. Login as User B
5. Try to access User A's item
6. Verify access denied (redirect or error)
7. Verify User B cannot see User A's data
```

## Troubleshooting

### Issue 1: Element Not Found

**Symptoms**: Timeout waiting for selector

**Debugging Steps**:
1. Capture screenshot - is page loaded?
2. Evaluate page HTML - is element present?
3. Check selector syntax - is it correct?
4. Check timing - does element appear after delay?

**Solutions**:
- Increase timeout
- Wait for parent element first
- Use more specific selector
- Wait for network idle

### Issue 2: Click Not Working

**Symptoms**: Click action completes but nothing happens

**Debugging Steps**:
1. Verify element is visible
2. Verify element is not covered by another element
3. Check if element is disabled
4. Check if JavaScript event handler attached

**Solutions**:
- Wait for element to be clickable
- Scroll element into view
- Use force click option
- Try alternative interaction (keyboard)

### Issue 3: Form Submission Fails

**Symptoms**: Form submits but no response

**Debugging Steps**:
1. Check network requests - was API called?
2. Check console errors - JavaScript errors?
3. Check form validation - are all fields valid?
4. Check API response - what status code?

**Solutions**:
- Verify all required fields filled
- Check for client-side validation errors
- Verify API endpoint is correct
- Check authentication token included

### Issue 4: Authentication State Lost

**Symptoms**: User logged out unexpectedly

**Debugging Steps**:
1. Check localStorage/cookies - is token present?
2. Check token expiry - has token expired?
3. Check navigation - did page reload clear state?
4. Check API responses - 401 Unauthorized?

**Solutions**:
- Re-login before each test
- Use longer-lived tokens for testing
- Preserve browser context between tests
- Verify token refresh logic working
