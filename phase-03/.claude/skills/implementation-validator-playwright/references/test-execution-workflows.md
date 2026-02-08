# Test Execution Workflows

## Overview

This guide provides comprehensive workflows for executing browser-based validation tests, reporting results, and handling failures. It covers test orchestration, result collection, report generation, and failure recovery strategies.

## Test Execution Patterns

### 1. Single Test Execution

**Workflow**:
```
1. Setup
   - Initialize browser context
   - Navigate to starting page
   - Authenticate if needed
   - Prepare test data

2. Execute
   - Run test steps sequentially
   - Capture screenshots at key points
   - Log actions and results
   - Handle errors gracefully

3. Verify
   - Check expected outcomes
   - Verify database state
   - Validate API responses
   - Confirm UI updates

4. Cleanup
   - Clear test data
   - Close browser context
   - Save artifacts
   - Generate report

5. Report
   - Test name
   - Status (pass/fail)
   - Duration
   - Screenshots
   - Logs
   - Error details (if failed)
```

**Example: Login Test Execution**
```
SETUP:
  - Initialize browser
  - Navigate to http://localhost:3000
  - Clear localStorage
  - Prepare test user credentials

EXECUTE:
  Step 1: Navigate to /login
  Step 2: Fill email: "test@example.com"
  Step 3: Fill password: "password123"
  Step 4: Click submit
  Step 5: Wait for redirect

VERIFY:
  - Current URL: /dashboard
  - Token in localStorage: present
  - User indicator visible: "test@example.com"
  - No console errors

CLEANUP:
  - Logout
  - Clear localStorage
  - Close browser

REPORT:
  Test: "User can login with valid credentials"
  Status: PASS
  Duration: 3.2s
  Screenshots: 5
  Errors: 0
```

### 2. Test Suite Execution

**Workflow**:
```
1. Suite Setup
   - Initialize test environment
   - Start backend server (if needed)
   - Connect to database
   - Prepare shared fixtures

2. Execute Tests
   - Run tests in order
   - OR run tests in parallel (if independent)
   - Collect results for each test
   - Continue on failure (don't abort suite)

3. Suite Teardown
   - Clean up shared resources
   - Close database connections
   - Stop backend server (if started)
   - Archive artifacts

4. Generate Suite Report
   - Total tests
   - Passed/Failed/Skipped
   - Total duration
   - Coverage metrics
   - Failure summary
```

**Example: Authentication Suite**
```
SUITE: Authentication Tests

SETUP:
  - Start backend server
  - Initialize test database
  - Create test users
  - Initialize browser

TESTS:
  1. User can signup with valid data - PASS (2.5s)
  2. User cannot signup with existing email - PASS (1.8s)
  3. User can login with valid credentials - PASS (3.2s)
  4. User cannot login with invalid password - PASS (2.1s)
  5. User session persists across page refresh - PASS (2.8s)
  6. User can logout successfully - PASS (1.5s)

TEARDOWN:
  - Delete test users
  - Close browser
  - Stop backend server

REPORT:
  Suite: Authentication Tests
  Total: 6 tests
  Passed: 6
  Failed: 0
  Duration: 14.0s
  Coverage: 100%
```

### 3. Parallel Test Execution

**When to Use**:
- Tests are independent
- No shared state between tests
- Faster execution needed

**Workflow**:
```
1. Identify independent tests
2. Group tests by dependency
3. Execute independent groups in parallel
4. Execute dependent tests sequentially within group
5. Collect results from all parallel executions
6. Generate combined report
```

**Example: CRUD Operations (Parallel)**
```
PARALLEL GROUP 1 (Independent):
  - Test: Create task - PASS (2.0s)
  - Test: List tasks - PASS (1.5s)
  - Test: Search tasks - PASS (1.8s)

PARALLEL GROUP 2 (Independent):
  - Test: Update task - PASS (2.2s)
  - Test: Complete task - PASS (1.9s)
  - Test: Delete task - PASS (1.7s)

SEQUENTIAL (Dependent):
  - Test: Create → Update → Delete flow - PASS (5.5s)

Total Duration: 7.0s (vs 16.6s sequential)
Speedup: 2.4x
```

### 4. Smoke Test Execution

**Purpose**: Quick validation that critical paths work

**Workflow**:
```
1. Select critical tests:
   - Login
   - Main feature (e.g., create task)
   - Logout

2. Execute quickly (minimal waits)

3. Report pass/fail only (no detailed logs)

4. If any fail, abort and report
```

**Example: Smoke Test**
```
SMOKE TESTS:
  1. Can access homepage - PASS (0.5s)
  2. Can login - PASS (1.2s)
  3. Can create task - PASS (1.5s)
  4. Can logout - PASS (0.8s)

Result: ALL PASS
Duration: 4.0s
Status: ✓ System operational
```

## Result Collection Strategies

### 1. Test Result Structure

**Standard Test Result**:
```json
{
  "testName": "User can login with valid credentials",
  "status": "pass",
  "duration": 3200,
  "startTime": "2024-01-15T10:30:45.000Z",
  "endTime": "2024-01-15T10:30:48.200Z",
  "steps": [
    {
      "step": 1,
      "action": "Navigate to /login",
      "status": "pass",
      "duration": 500,
      "screenshot": "login-01-page-loaded.png"
    },
    {
      "step": 2,
      "action": "Fill email",
      "status": "pass",
      "duration": 200
    }
  ],
  "assertions": [
    {
      "description": "URL should be /dashboard",
      "expected": "/dashboard",
      "actual": "/dashboard",
      "status": "pass"
    },
    {
      "description": "Token should be present",
      "expected": "present",
      "actual": "present",
      "status": "pass"
    }
  ],
  "artifacts": {
    "screenshots": ["login-01.png", "login-02.png"],
    "logs": "console.log",
    "network": "network.har"
  },
  "errors": []
}
```

### 2. Aggregated Results

**Suite Result Structure**:
```json
{
  "suiteName": "Authentication Tests",
  "totalTests": 6,
  "passed": 5,
  "failed": 1,
  "skipped": 0,
  "duration": 14000,
  "startTime": "2024-01-15T10:30:00.000Z",
  "endTime": "2024-01-15T10:30:14.000Z",
  "tests": [
    {
      "testName": "User can signup",
      "status": "pass",
      "duration": 2500
    },
    {
      "testName": "User can login",
      "status": "fail",
      "duration": 3200,
      "error": "Element not found: button[type='submit']"
    }
  ],
  "coverage": {
    "frontend": "85%",
    "backend": "90%",
    "database": "100%"
  },
  "summary": {
    "passRate": "83%",
    "avgDuration": 2333,
    "criticalFailures": 1
  }
}
```

### 3. Real-Time Result Streaming

**Pattern**:
```
1. Start test execution
2. Stream results as tests complete
3. Update dashboard/UI in real-time
4. Allow early termination if critical test fails
```

**Example: Real-Time Output**
```
[10:30:00] Starting Authentication Suite...
[10:30:02] ✓ User can signup (2.5s)
[10:30:04] ✓ User cannot signup with existing email (1.8s)
[10:30:07] ✗ User can login (3.2s)
           Error: Element not found: button[type='submit']
           Screenshot: login-error.png
[10:30:09] ⊘ Skipping remaining tests due to critical failure
[10:30:09] Suite completed: 2 passed, 1 failed, 3 skipped
```

## Report Generation

### 1. Console Report

**Format**:
```
================================
Test Execution Report
================================

Suite: Authentication Tests
Duration: 14.0s
Started: 2024-01-15 10:30:00
Ended: 2024-01-15 10:30:14

Results:
--------
✓ User can signup (2.5s)
✓ User cannot signup with existing email (1.8s)
✓ User can login (3.2s)
✓ User cannot login with invalid password (2.1s)
✓ User session persists (2.8s)
✓ User can logout (1.5s)

Summary:
--------
Total: 6 tests
Passed: 6 (100%)
Failed: 0 (0%)
Skipped: 0 (0%)

Status: ✓ ALL TESTS PASSED
```

### 2. HTML Report

**Structure**:
```html
<!DOCTYPE html>
<html>
<head>
  <title>Test Report - Authentication Suite</title>
  <style>
    .pass { color: green; }
    .fail { color: red; }
    .screenshot { max-width: 800px; }
  </style>
</head>
<body>
  <h1>Test Execution Report</h1>

  <div class="summary">
    <h2>Summary</h2>
    <p>Total: 6 tests</p>
    <p class="pass">Passed: 6 (100%)</p>
    <p class="fail">Failed: 0 (0%)</p>
    <p>Duration: 14.0s</p>
  </div>

  <div class="tests">
    <h2>Test Results</h2>

    <div class="test pass">
      <h3>✓ User can login</h3>
      <p>Duration: 3.2s</p>
      <details>
        <summary>Steps</summary>
        <ol>
          <li>Navigate to /login</li>
          <li>Fill email</li>
          <li>Fill password</li>
          <li>Click submit</li>
          <li>Verify redirect</li>
        </ol>
      </details>
      <details>
        <summary>Screenshots</summary>
        <img src="login-01.png" class="screenshot">
        <img src="login-02.png" class="screenshot">
      </details>
    </div>
  </div>
</body>
</html>
```

### 3. JSON Report

**Use Cases**:
- CI/CD integration
- Automated analysis
- Trend tracking
- Dashboard integration

**Format**: See "Aggregated Results" structure above

### 4. Markdown Report

**Format**:
```markdown
# Test Execution Report

## Authentication Tests

**Duration**: 14.0s
**Date**: 2024-01-15 10:30:00

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | 6 |
| Passed | 6 (100%) |
| Failed | 0 (0%) |
| Skipped | 0 (0%) |
| Duration | 14.0s |

## Test Results

### ✓ User can login

**Duration**: 3.2s
**Status**: PASS

**Steps**:
1. Navigate to /login
2. Fill email: test@example.com
3. Fill password: ********
4. Click submit
5. Verify redirect to /dashboard

**Assertions**:
- ✓ URL is /dashboard
- ✓ Token present in localStorage
- ✓ User indicator visible

**Screenshots**:
- ![Login page](login-01.png)
- ![Dashboard](login-02.png)
```

## Failure Handling Strategies

### 1. Retry on Failure

**When to Retry**:
- Flaky tests (timing issues)
- Network timeouts
- Element not found (may appear after delay)

**Retry Pattern**:
```
1. Execute test
2. If fails:
   - Wait brief delay (e.g., 1s)
   - Retry test
   - If passes: Mark as "pass (retried)"
   - If fails again: Mark as "fail"
3. Limit retries (max 3)
```

**Example: Retry Logic**
```
Attempt 1: FAIL (Element not found)
  Wait 1s
Attempt 2: FAIL (Element not found)
  Wait 2s
Attempt 3: PASS

Result: PASS (retried 2 times)
Note: Consider fixing flaky test
```

### 2. Graceful Degradation

**Pattern**:
```
1. Execute test
2. If critical step fails:
   - Skip remaining steps
   - Mark test as failed
   - Continue to next test
3. If non-critical step fails:
   - Log warning
   - Continue test
   - Mark test as "pass with warnings"
```

**Example: Non-Critical Failure**
```
Test: User can create task

Steps:
  1. Navigate to /tasks - PASS
  2. Click "Add Task" - PASS
  3. Fill title - PASS
  4. Take screenshot - FAIL (non-critical)
  5. Submit form - PASS
  6. Verify task created - PASS

Result: PASS (with warnings)
Warning: Screenshot capture failed
```

### 3. Error Recovery

**Recovery Strategies**:

| Error Type | Recovery Action |
|------------|-----------------|
| Element not found | Refresh page, retry |
| Network timeout | Retry request |
| Authentication expired | Re-login, retry |
| Database locked | Wait, retry |
| Browser crashed | Restart browser, retry test |

**Example: Authentication Recovery**
```
Test: Create task

Step 1: Navigate to /tasks
Step 2: Click "Add Task"
Step 3: Fill form
Step 4: Submit
  Error: 401 Unauthorized

RECOVERY:
  Detect: Authentication expired
  Action: Re-login
  Step 4a: Navigate to /login
  Step 4b: Login with credentials
  Step 4c: Navigate back to /tasks
  Step 4d: Retry submit
  Result: PASS

Final Result: PASS (with recovery)
```

### 4. Failure Reporting

**Comprehensive Failure Report**:
```
Test: User can login
Status: FAIL
Duration: 3.2s
Error: Element not found: button[type='submit']

Context:
  - URL: http://localhost:3000/login
  - Step: 4 of 5
  - Action: Click submit button
  - Selector: button[type='submit']

Debugging Information:
  - Screenshot: login-error.png
  - Page HTML: login-page.html
  - Console Logs:
    [ERROR] "Failed to load resource: net::ERR_CONNECTION_REFUSED"
  - Network Requests:
    POST /api/auth/login - FAILED (Connection refused)

Possible Causes:
  1. Backend server not running
  2. Wrong selector (button type changed)
  3. Button not rendered (JavaScript error)

Suggested Actions:
  1. Verify backend server running on port 8000
  2. Check button element in page HTML
  3. Review console errors for JavaScript issues
```

## Test Orchestration

### 1. Test Dependencies

**Handling Dependencies**:
```
1. Identify test dependencies
2. Create dependency graph
3. Execute in topological order
4. If dependency fails, skip dependent tests
```

**Example: Dependency Chain**
```
Test A: User signup (no dependencies)
Test B: User login (depends on A)
Test C: Create task (depends on B)
Test D: Update task (depends on C)

Execution Order: A → B → C → D

If B fails:
  - Skip C (depends on B)
  - Skip D (depends on C)
  - Report: 1 failed, 2 skipped
```

### 2. Test Prioritization

**Priority Levels**:
- **P0 (Critical)**: Must pass for system to be functional
- **P1 (High)**: Important features, should pass
- **P2 (Medium)**: Nice-to-have features
- **P3 (Low)**: Edge cases, minor features

**Execution Strategy**:
```
1. Run P0 tests first
2. If any P0 fails, abort and report
3. Run P1 tests
4. Run P2 tests
5. Run P3 tests (optional, time permitting)
```

**Example: Prioritized Execution**
```
P0 (Critical):
  ✓ User can login (3.2s)
  ✓ User can create task (2.5s)

P1 (High):
  ✓ User can update task (2.2s)
  ✓ User can delete task (1.7s)

P2 (Medium):
  ✓ User can search tasks (1.8s)
  ✓ User can filter tasks (1.9s)

P3 (Low):
  ⊘ Skipped (time limit reached)

Result: All critical and high priority tests passed
```

### 3. Test Scheduling

**Scheduling Strategies**:

| Strategy | When to Use |
|----------|-------------|
| **On Commit** | Run smoke tests |
| **On PR** | Run full test suite |
| **Nightly** | Run extended tests |
| **On Demand** | Run specific tests |

**Example: CI/CD Integration**
```
On Commit:
  - Run smoke tests (4 tests, ~4s)
  - If pass: Allow commit
  - If fail: Block commit

On Pull Request:
  - Run full test suite (50 tests, ~2min)
  - If pass: Allow merge
  - If fail: Block merge, report failures

Nightly:
  - Run extended tests (200 tests, ~30min)
  - Run performance tests
  - Run security tests
  - Email report to team
```

## Best Practices

### 1. Test Execution Checklist

Before running tests:
- [ ] Backend server running
- [ ] Database accessible
- [ ] Test data prepared
- [ ] Environment variables set
- [ ] Browser installed
- [ ] Network accessible

During test execution:
- [ ] Monitor progress
- [ ] Capture artifacts
- [ ] Log errors
- [ ] Handle failures gracefully

After test execution:
- [ ] Generate report
- [ ] Archive artifacts
- [ ] Clean up test data
- [ ] Notify stakeholders

### 2. Performance Optimization

**Optimization Strategies**:
- Reuse browser context
- Parallelize independent tests
- Cache authentication tokens
- Minimize waits (use smart waits)
- Batch database operations

**Example: Optimized Execution**
```
BEFORE (Sequential):
  - Login (3s)
  - Test 1 (2s)
  - Logout (1s)
  - Login (3s)
  - Test 2 (2s)
  - Logout (1s)
  Total: 12s

AFTER (Optimized):
  - Login once (3s)
  - Test 1 (2s)
  - Test 2 (2s)
  - Logout once (1s)
  Total: 8s
  Speedup: 1.5x
```

### 3. Artifact Management

**Artifact Organization**:
```
test-results/
├── 2024-01-15-103000/
│   ├── screenshots/
│   │   ├── login-01.png
│   │   └── login-02.png
│   ├── logs/
│   │   ├── console.log
│   │   └── network.har
│   ├── reports/
│   │   ├── report.html
│   │   ├── report.json
│   │   └── report.md
│   └── artifacts/
│       ├── page-html.html
│       └── dom-state.json
└── latest -> 2024-01-15-103000/
```

**Retention Policy**:
- Keep last 10 test runs
- Keep all failed test artifacts
- Archive old artifacts (>30 days)
- Delete artifacts for passed tests (>7 days)

### 4. Continuous Improvement

**Metrics to Track**:
- Test execution time (trend)
- Test pass rate (trend)
- Flaky test count
- Test coverage
- Time to fix failures

**Example: Trend Analysis**
```
Week 1: 45 tests, 95% pass rate, 12min duration
Week 2: 50 tests, 93% pass rate, 15min duration
Week 3: 50 tests, 96% pass rate, 10min duration (optimized)
Week 4: 55 tests, 97% pass rate, 11min duration

Insights:
- Test count growing (good)
- Pass rate improving (good)
- Duration optimized in Week 3 (good)
- Trend: Positive
```
