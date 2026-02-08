---
name: implementation-validator-playwright
description: |
  Automates browser-based testing and validation of implemented features using Playwright MCP server via browsing-with-playwright skill, specializing in Next.js + Better Auth + FastAPI + PostgreSQL stack.
  This skill should be used when validating implemented features through browser automation, debugging implementation issues with screenshots and logs, testing authentication flows end-to-end, verifying database persistence after UI actions, capturing errors with actionable debugging information, or executing automated validation tests after implementation is complete.
---

# Implementation Validator (Playwright)

Automate post-implementation testing and debugging using browser automation via Playwright MCP server to validate frontend, backend, database, and authentication implementations.

## What This Skill Does

- Execute automated browser tests via Playwright MCP server using browsing-with-playwright skill
- Validate frontend implementations (UI components, user interactions, state management)
- Verify backend API integrations (API calls, response handling, error states)
- Confirm database persistence (data saved correctly, queries work)
- Test Better Auth authentication flows (signup, login, session management, JWT tokens)
- Debug implementation issues by capturing screenshots, console logs, network requests
- Identify and report errors with actionable debugging information
- Validate complete user flows end-to-end
- Generate test reports with pass/fail status and error details

## What This Skill Does NOT Do

- Write test code or test scripts (focuses on execution and validation)
- Design test strategies or test plans (use integration-testing-engineer skill)
- Unit testing or component testing in isolation
- Performance testing or load testing
- Security penetration testing
- Replace manual exploratory testing
- Direct Playwright API usage (must use browsing-with-playwright skill)

---

## Version Compatibility

This skill covers:
- **Playwright MCP Server**: Latest version
- **browsing-with-playwright skill**: Required for MCP server interaction
- **Next.js**: 14+ (App Router)
- **Better Auth**: 1.0+
- **FastAPI**: 0.100+
- **PostgreSQL**: 14+

For latest features and breaking changes, consult official documentation.

---

## Required Clarifications

Before implementation, clarify:

1. **Validation scope**: Which implemented features need validation? (e.g., login flow, task CRUD, user isolation)
2. **Current state**: Is the implementation complete? Are frontend, backend, and database all deployed?
3. **Test environment**: What is the application URL? (e.g., http://localhost:3000)

## Optional Clarifications

4. **Test data**: Should tests use existing data or create new test data?
5. **Error handling**: Should tests continue on failure or abort?
6. **Report format**: Preferred report format? (console, HTML, JSON, markdown)
7. **Debugging level**: How much debugging information to capture? (minimal, standard, verbose)

**If user doesn't provide clarifications**: Use sensible defaults (validate all implemented features, create test data, continue on failure, generate HTML report, standard debugging) and document assumptions made.

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Application URL, API endpoints, database schema, authentication setup |
| **Conversation** | User's specific validation requirements, implemented features, known issues |
| **Skill References** | Playwright MCP patterns from `references/` (automation, validation, debugging, execution) |
| **User Guidelines** | Project-specific test conventions, error handling preferences, report requirements |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

---

## Official Documentation

| Resource | URL | Use For |
|----------|-----|---------|
| Playwright Docs | https://playwright.dev/docs/intro | Browser automation, selectors, assertions |
| MCP Documentation | https://modelcontextprotocol.io/ | MCP server concepts, tool usage |
| Next.js Testing | https://nextjs.org/docs/app/building-your-application/testing | Next.js testing patterns |
| FastAPI Testing | https://fastapi.tiangolo.com/tutorial/testing/ | API testing patterns |
| Better Auth Docs | https://www.better-auth.com/docs | Authentication flow testing |

---

## Core Competencies

### 1. Playwright MCP Automation

- Use browsing-with-playwright skill to interact with Playwright MCP server
- Execute browser automation workflows (navigate, click, fill, wait, assert)
- Capture screenshots at key points
- Collect console logs and network requests
- Handle browser state and context

**Details**: See `references/playwright-mcp-automation.md`

### 2. Implementation Validation

- Validate frontend implementations (UI, interactions, state)
- Verify backend API integrations (requests, responses, errors)
- Confirm database persistence (data saved, queries work)
- Test authentication flows (signup, login, JWT tokens, sessions)
- Validate cross-layer integration (UI → API → DB)

**Details**: See `references/implementation-validation-patterns.md`

### 3. Debugging and Error Capture

- Capture screenshots on errors
- Collect console logs (errors, warnings, info)
- Inspect network requests (headers, payloads, status codes)
- Analyze DOM state on failures
- Generate actionable debugging information

**Details**: See `references/debugging-strategies.md`

### 4. Test Execution and Reporting

- Execute single tests and test suites
- Handle test failures gracefully
- Retry flaky tests
- Generate comprehensive test reports
- Archive test artifacts

**Details**: See `references/test-execution-workflows.md`

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Not Using browsing-with-playwright Skill
**Problem**: Attempting to use Playwright API directly instead of MCP server

**Solution**: Always use browsing-with-playwright skill
```
❌ Bad: Direct Playwright API call
  await page.goto('http://localhost:3000')

✅ Good: Use browsing-with-playwright skill
  "Use browsing-with-playwright to navigate to http://localhost:3000"
```

### ❌ Mistake 2: Not Capturing Debugging Information
**Problem**: Test fails but no screenshots or logs captured

**Solution**: Capture debugging info at key points
```
❌ Bad: No debugging info
  Test fails with "Element not found"
  No screenshot, no logs, no context

✅ Good: Comprehensive debugging
  Test fails with "Element not found"
  Screenshot: login-error.png
  Console logs: [ERROR] "Failed to load resource"
  Network: POST /api/auth/login - 401
  Suggested action: Check backend server running
```

### ❌ Mistake 3: Not Verifying Database State
**Problem**: Test checks UI but doesn't verify data persisted

**Solution**: Verify database after UI actions
```
❌ Bad: Only UI verification
  Create task in UI
  Verify task appears in list
  (But not checking database)

✅ Good: UI + Database verification
  Create task in UI
  Verify task appears in list
  Query database: SELECT * FROM tasks WHERE title = 'Test Task'
  Verify task exists in database
```

### ❌ Mistake 4: Not Testing Authentication State
**Problem**: Assumes authentication works without verifying token

**Solution**: Verify JWT token and session state
```
❌ Bad: Assume authentication works
  Login
  Navigate to protected page
  (Assume authenticated)

✅ Good: Verify authentication state
  Login
  Verify token in localStorage
  Decode token, check claims
  Navigate to protected page
  Verify Authorization header in API requests
```

### ❌ Mistake 5: Not Handling Errors Gracefully
**Problem**: Test aborts on first error, no recovery

**Solution**: Handle errors, retry, continue testing
```
❌ Bad: Abort on error
  Test 1: FAIL
  Abort entire suite

✅ Good: Graceful error handling
  Test 1: FAIL (captured error details)
  Test 2: PASS
  Test 3: PASS
  Report: 2 passed, 1 failed
```

**Details**: See `references/debugging-strategies.md` for comprehensive error handling

---

## Implementation Workflows

### 1. Single Feature Validation

```
1. Setup
   - Use browsing-with-playwright to initialize browser
   - Navigate to application URL
   - Authenticate if needed

2. Execute Validation
   - Perform user actions (click, fill, submit)
   - Capture screenshots at key points
   - Collect console logs
   - Monitor network requests

3. Verify Results
   - Check UI updates correctly
   - Verify API calls made
   - Confirm database persistence
   - Validate authentication state

4. Report
   - Generate test report
   - Include screenshots
   - Include error details (if any)
   - Provide debugging information
```

### 2. Authentication Flow Validation

```
1. Signup Flow
   - Navigate to /signup
   - Fill signup form
   - Submit
   - Verify user created in database
   - Verify redirect or success message

2. Login Flow
   - Navigate to /login
   - Fill credentials
   - Submit
   - Verify JWT token issued
   - Verify token stored (localStorage/cookies)
   - Verify redirect to dashboard

3. Session Persistence
   - Refresh page
   - Verify still authenticated
   - Open new tab
   - Verify session shared

4. Logout Flow
   - Click logout
   - Verify token cleared
   - Verify redirect to login
   - Verify cannot access protected routes
```

### 3. CRUD Operations Validation

```
1. Create
   - Navigate to creation page
   - Fill form
   - Submit
   - Verify item in UI
   - Verify item in database

2. Read
   - Navigate to list page
   - Verify items displayed
   - Click item
   - Verify details displayed

3. Update
   - Click edit
   - Modify fields
   - Submit
   - Verify changes in UI
   - Verify changes in database

4. Delete
   - Click delete
   - Confirm (if modal)
   - Verify item removed from UI
   - Verify item removed from database
```

### 4. Error Scenario Validation

```
1. Test Invalid Input
   - Submit form with invalid data
   - Verify error message displayed
   - Verify form not submitted
   - Verify database unchanged

2. Test Unauthorized Access
   - Remove authentication token
   - Try to access protected route
   - Verify redirect to login
   - Verify 401 error

3. Test User Isolation
   - Login as User A
   - Try to access User B's data
   - Verify access denied (403)
   - Verify data not displayed
```

**Detailed workflows**: See reference files for comprehensive guides

---

## Key Implementation Patterns

### Validation Checklist
- [ ] Frontend renders correctly
- [ ] User interactions work (click, fill, submit)
- [ ] Form validation works (client-side)
- [ ] API requests sent with correct headers
- [ ] API responses handled correctly
- [ ] Database persistence confirmed
- [ ] User isolation enforced
- [ ] Authentication required for protected routes
- [ ] JWT tokens valid and attached to requests
- [ ] Error handling works (error messages displayed)
- [ ] Success messages displayed
- [ ] Screenshots captured at key points
- [ ] Console logs collected
- [ ] Network requests monitored

### Debugging Checklist
- [ ] Screenshots captured on errors
- [ ] Console logs collected (errors, warnings)
- [ ] Network requests captured (failed requests highlighted)
- [ ] DOM state captured on failures
- [ ] Error messages clear and actionable
- [ ] Suggested fixes provided
- [ ] Reproduction steps documented

### Reporting Checklist
- [ ] Test name and description
- [ ] Pass/fail status
- [ ] Duration
- [ ] Steps executed
- [ ] Assertions checked
- [ ] Screenshots included
- [ ] Error details (if failed)
- [ ] Debugging information
- [ ] Suggested actions

---

## Reference Files

Search patterns for comprehensive guides:

| File | Lines | Search For |
|------|-------|------------|
| `playwright-mcp-automation.md` | 800+ | "MCP server", "browsing-with-playwright", "navigation", "interaction", "screenshot" |
| `implementation-validation-patterns.md` | 900+ | "frontend validation", "backend validation", "database validation", "authentication validation" |
| `debugging-strategies.md` | 800+ | "error capture", "console logs", "network inspection", "troubleshooting" |
| `test-execution-workflows.md` | 800+ | "test execution", "reporting", "failure handling", "retry logic" |

**Reference contents**:
- `playwright-mcp-automation.md` - MCP server usage, browser automation workflows, state management
- `implementation-validation-patterns.md` - Frontend, backend, database, auth validation patterns
- `debugging-strategies.md` - Error capture, log analysis, network inspection, systematic troubleshooting
- `test-execution-workflows.md` - Test execution, result collection, report generation, failure handling

---

## Best Practices

- Always use browsing-with-playwright skill for browser automation
- Capture screenshots at key points (before/after critical actions)
- Collect console logs continuously
- Monitor network requests (especially API calls)
- Verify database state after UI actions
- Test authentication flows completely (signup → login → protected routes)
- Handle errors gracefully (capture debugging info, continue testing)
- Generate comprehensive reports (pass/fail, duration, screenshots, errors)
- Provide actionable debugging information
- Test both happy paths and error scenarios
- Verify user isolation (users cannot access other users' data)
- Test JWT token flows (issuance, validation, expiry)
- Validate cross-layer integration (UI → API → DB)
- Document reproduction steps for failures

---

## Tools and Technologies

### Browser Automation
- Playwright MCP Server
- browsing-with-playwright skill
- Chromium/Firefox/WebKit browsers

### Validation Targets
- Next.js frontend (App Router)
- Better Auth authentication
- FastAPI backend
- PostgreSQL database

### Debugging Tools
- Screenshots
- Console logs
- Network request capture
- DOM state inspection

### Reporting
- Console reports
- HTML reports
- JSON reports
- Markdown reports

---

## Output Format

When providing validation results, structure responses as:

**Validation Summary**: Overall pass/fail status and key findings
**Test Results**: Detailed results for each test (pass/fail, duration, steps)
**Debugging Information**: Screenshots, logs, network requests for failures
**Database Verification**: Confirmation of data persistence
**Authentication Status**: JWT token validation, session state
**Recommendations**: Suggested fixes for failures, improvements for implementation
