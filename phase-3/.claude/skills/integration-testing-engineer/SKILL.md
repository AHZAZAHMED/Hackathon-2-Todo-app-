---
name: integration-testing-engineer
description: |
  Expert in end-to-end validation for full-stack web applications with authentication, specializing in Next.js + Better Auth JWT + FastAPI + Neon PostgreSQL stack.
  This skill should be used when validating complete user flows (signup, login, task management), verifying JWT token flows, confirming database persistence, ensuring user isolation, testing CRUD operations across layers, or validating that frontend actions trigger real backend changes with proper authorization enforcement.
---

# Integration Testing Engineer

Validate full-stack integration for spec-driven web applications with real system testing across UI, API, authentication, and database layers.

## What This Skill Does

- Design integration test strategies for Next.js frontend, Better Auth JWT, FastAPI backend, and PostgreSQL database
- Validate real user flows: signup, login, create/update/delete/complete tasks
- Verify JWT token issuance, attachment, and backend validation
- Confirm database persistence and user isolation across all operations
- Detect cross-layer failures (UI → API → DB)
- Define acceptance tests based strictly on specifications
- Ensure frontend actions trigger real backend changes
- Produce clear pass/fail validation criteria
- Test authorization enforcement (users cannot access other users' data)

## What This Skill Does NOT Do

- Unit testing (test individual functions in isolation)
- Mock services or stub dependencies (only real system integration)
- Performance testing or load testing
- Security penetration testing
- UI/UX testing or visual regression testing
- Test code generation without understanding requirements
- Replace manual exploratory testing

---

## Version Compatibility

This skill covers:
- **Next.js**: 14+ (App Router)
- **Better Auth**: 1.0+
- **FastAPI**: 0.100+
- **PostgreSQL**: 14+
- **Playwright**: 1.40+
- **Pytest**: 7.0+
- **Jest**: 29+

For latest features and breaking changes, consult official documentation.

---

## Required Clarifications

Before implementation, clarify:

1. **Testing scope**: Which user flows need integration testing? (e.g., authentication, task CRUD, user isolation)
2. **Current test coverage**: What integration tests already exist? What gaps need to be filled?
3. **Test environment**: Is there a dedicated test database and test environment configured?

## Optional Clarifications

4. **CI/CD integration**: Should tests run in CI pipeline? Which CI platform (GitHub Actions, GitLab CI)?
5. **Test data strategy**: Should tests use factories, fixtures, or seed data?
6. **Performance requirements**: Any specific response time requirements for integration tests?
7. **Browser coverage**: Which browsers need E2E testing? (Chrome, Firefox, Safari, Edge)

**If user doesn't provide clarifications**: Use sensible defaults (test all critical flows, use fixtures for test data, run in GitHub Actions) and document assumptions made.

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing test structure, API endpoints, database models, authentication setup |
| **Conversation** | User's specific testing requirements, critical flows, acceptance criteria |
| **Skill References** | Testing patterns from `references/` (Playwright, Pytest, JWT validation, database testing) |
| **User Guidelines** | Project-specific test conventions, CI/CD setup, test data policies |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

---

## Official Documentation

| Resource | URL | Use For |
|----------|-----|---------|
| Playwright Docs | https://playwright.dev/docs/intro | E2E testing, browser automation, fixtures |
| Pytest Docs | https://docs.pytest.org/ | Backend testing, fixtures, parametrization |
| FastAPI Testing | https://fastapi.tiangolo.com/tutorial/testing/ | TestClient, dependency overrides, async tests |
| Jest Docs | https://jestjs.io/docs/getting-started | Frontend component testing, mocking |
| Testing Library | https://testing-library.com/docs/react-testing-library/intro | React component testing patterns |

---

## Core Competencies

### 1. Integration Testing Strategy

- Design test pyramid with appropriate distribution (70% unit, 20% integration, 10% E2E)
- Select appropriate testing approach (bottom-up, top-down, sandwich)
- Define test scope and boundaries
- Implement test isolation and independence
- Measure and track test coverage

**Details**: See `references/integration-testing-strategies.md`

### 2. Full-Stack Testing Patterns

- Test Next.js API routes with real database
- Test Server Components and Client Components
- Test FastAPI endpoints with TestClient
- Validate database persistence across layers
- Test JWT token flows (issuance, validation, expiry)
- Verify user isolation and authorization

**Details**: See `references/fullstack-testing-patterns.md`

### 3. Test Tools and Frameworks

- Configure Playwright for E2E testing
- Set up Pytest with FastAPI TestClient
- Configure Jest for frontend component testing
- Create database fixtures and cleanup strategies
- Implement test data factories and builders
- Set up CI/CD pipeline for automated testing

**Details**: See `references/test-tools-frameworks.md`

### 4. Acceptance Criteria Definition

- Define spec-based acceptance criteria
- Create clear pass/fail validation criteria
- Design test cases using equivalence partitioning
- Apply boundary value analysis
- Use decision tables for complex scenarios
- Implement traceability matrix (requirements → tests)

**Details**: See `references/acceptance-criteria.md`

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Using Mocks in Integration Tests
**Problem**: Mocking API or database defeats the purpose of integration testing

**Solution**: Use real components with test database
```python
# ❌ Bad: Mocking database in integration test
@patch('app.database.get_db')
def test_create_task(mock_db):
    mock_db.return_value = MagicMock()
    # This doesn't test real integration!

# ✅ Good: Real database with test fixture
def test_create_task(db_session, test_user, auth_token):
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={"title": "Test Task"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201

    # Verify in real database
    task = db_session.query(Task).filter_by(title="Test Task").first()
    assert task is not None
```

### ❌ Mistake 2: Not Cleaning Up Test Data
**Problem**: Tests leave data behind, causing failures in subsequent runs

**Solution**: Use fixtures with cleanup or transaction rollback
```python
# ❌ Bad: No cleanup
def test_create_task():
    user = User(username="test")
    db.add(user)
    db.commit()
    # User remains in database!

# ✅ Good: Fixture with cleanup
@pytest.fixture
def test_user(db_session):
    user = User(username="test")
    db_session.add(user)
    db_session.commit()

    yield user

    # Cleanup
    db_session.delete(user)
    db_session.commit()
```

### ❌ Mistake 3: Not Testing Authorization
**Problem**: Tests only verify happy path, miss authorization failures

**Solution**: Test both authorized and unauthorized access
```python
# ❌ Bad: Only tests happy path
def test_get_task(test_user, auth_token):
    response = client.get(
        f"/api/{test_user.id}/tasks/1",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200

# ✅ Good: Tests authorization enforcement
def test_user_cannot_access_other_users_tasks(test_user_a, test_user_b, auth_token_a):
    # Create task for user B
    task_b = create_task(test_user_b.id, "User B Task")

    # User A tries to access User B's task
    response = client.get(
        f"/api/{test_user_b.id}/tasks/{task_b.id}",
        headers={"Authorization": f"Bearer {auth_token_a}"}
    )
    assert response.status_code in [401, 403]
```

### ❌ Mistake 4: Not Verifying Database State
**Problem**: Tests only check API response, not actual persistence

**Solution**: Verify database state after operations
```python
# ❌ Bad: Only checks response
def test_create_task(test_user, auth_token):
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={"title": "Test Task"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201

# ✅ Good: Verifies database persistence
def test_create_task(db_session, test_user, auth_token):
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={"title": "Test Task"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201

    # Verify database state
    task = db_session.query(Task).filter_by(
        user_id=test_user.id,
        title="Test Task"
    ).first()
    assert task is not None
    assert task.completed == False
```

### ❌ Mistake 5: Shared State Between Tests
**Problem**: Tests depend on each other, causing flaky failures

**Solution**: Each test should be independent
```python
# ❌ Bad: Tests share state
task_id = None

def test_create_task():
    global task_id
    response = client.post("/api/1/tasks", json={"title": "Test"})
    task_id = response.json()["id"]

def test_update_task():
    # Depends on test_create_task running first!
    response = client.put(f"/api/1/tasks/{task_id}", json={"title": "Updated"})

# ✅ Good: Independent tests with fixtures
@pytest.fixture
def created_task(test_user, auth_token):
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={"title": "Test"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    return response.json()

def test_update_task(test_user, auth_token, created_task):
    response = client.put(
        f"/api/{test_user.id}/tasks/{created_task['id']}",
        json={"title": "Updated"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
```

### ❌ Mistake 6: Not Testing JWT Token Flow
**Problem**: Assumes JWT works without verifying token issuance and validation

**Solution**: Test complete JWT flow
```python
# ✅ Good: Test JWT token flow
def test_jwt_token_flow(db_session):
    # 1. User signs up
    signup_response = client.post("/api/auth/signup", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert signup_response.status_code == 201

    # 2. User logs in and receives JWT
    login_response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["token"]
    assert token is not None

    # 3. Decode JWT and verify claims
    decoded = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])
    assert "sub" in decoded  # User ID claim
    user_id = decoded["sub"]

    # 4. Use JWT to access protected endpoint
    response = client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # 5. Verify backend validates JWT
    response = client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": "Bearer invalid.token"}
    )
    assert response.status_code == 401
```

**Details**: See `references/fullstack-testing-patterns.md` for comprehensive patterns

---

## Implementation Workflows

### 1. Integration Test Setup
```
1. Configure test database (separate from production)
2. Set up test fixtures (users, authentication, database session)
3. Configure test client (FastAPI TestClient, Playwright)
4. Create test data factories and builders
5. Set up cleanup strategies (transaction rollback or explicit cleanup)
6. Verify test environment is isolated
```

### 2. Authentication Flow Testing
```
1. Test user signup (create account, verify database record)
2. Test user login (verify JWT token issuance)
3. Test JWT token validation (decode and verify claims)
4. Test protected endpoint access (with valid token)
5. Test unauthorized access (without token or invalid token)
6. Test user ID mismatch (token user_id ≠ URL user_id)
```

### 3. CRUD Operations Testing
```
1. Test Create: POST endpoint, verify 201, check database
2. Test Read: GET endpoint, verify 200, check response payload
3. Test Update: PUT endpoint, verify 200, check database changes
4. Test Delete: DELETE endpoint, verify 204, check database removal
5. Test user isolation for each operation
6. Test error paths (invalid data, unauthorized access)
```

### 4. End-to-End Flow Testing
```
1. Start with user signup/login (establish authentication)
2. Perform complete user journey (create → read → update → complete → delete)
3. Verify each step persists correctly to database
4. Verify frontend state updates reflect backend changes
5. Test error scenarios at each step
6. Verify cleanup and final state
```

**Detailed workflows**: See reference files for comprehensive guides

---

## Key Implementation Patterns

### Integration Test Checklist
- [ ] Test database configured and isolated from production
- [ ] Test fixtures created (users, auth tokens, database session)
- [ ] All API endpoints have integration tests
- [ ] JWT token flow tested (issuance, validation, expiry)
- [ ] User isolation tested (cannot access other users' data)
- [ ] Database persistence verified for all operations
- [ ] Authorization enforced (401/403 for unauthorized requests)
- [ ] Error paths tested (invalid data, missing auth, etc.)
- [ ] Test data cleanup implemented (no data leakage)
- [ ] Tests are independent (no shared state)

### Authentication Testing Checklist
- [ ] User signup creates database record
- [ ] User login returns valid JWT token
- [ ] JWT token contains correct claims (sub, exp, etc.)
- [ ] Protected endpoints require valid JWT
- [ ] Invalid JWT returns 401 Unauthorized
- [ ] Expired JWT returns 401 Unauthorized
- [ ] User ID in JWT matches user ID in URL
- [ ] Mismatched user ID returns 403 Forbidden

### Database Testing Checklist
- [ ] Test database separate from production
- [ ] Database fixtures create clean state for each test
- [ ] All CRUD operations persist correctly
- [ ] Foreign key constraints enforced
- [ ] User isolation enforced at database level
- [ ] Transactions rollback on test completion
- [ ] No test data leakage between tests

### E2E Testing Checklist
- [ ] Playwright configured with test user
- [ ] Authentication flow tested (signup → login)
- [ ] Complete user journey tested (create → update → delete)
- [ ] Frontend state updates verified
- [ ] API calls verified (network tab or mocking)
- [ ] Database state verified after E2E flow
- [ ] Error scenarios tested (network failures, invalid input)

---

## Reference Files

Search patterns for comprehensive guides:

| File | Lines | Search For |
|------|-------|------------|
| `integration-testing-strategies.md` | 578 | "test pyramid", "bottom-up", "top-down", "AAA pattern", "fixtures", "isolation" |
| `fullstack-testing-patterns.md` | 800+ | "Next.js", "FastAPI", "JWT", "TestClient", "Playwright", "user isolation" |
| `test-tools-frameworks.md` | 800+ | "Playwright", "Pytest", "Jest", "fixtures", "CI/CD", "GitHub Actions" |
| `acceptance-criteria.md` | 800+ | "Given-When-Then", "pass/fail", "equivalence partitioning", "traceability" |

**Reference contents**:
- `integration-testing-strategies.md` - Test pyramid, integration strategies, test design patterns, isolation
- `fullstack-testing-patterns.md` - Next.js + FastAPI testing, JWT validation, database testing, user isolation
- `test-tools-frameworks.md` - Playwright, Pytest, Jest, database fixtures, CI/CD setup
- `acceptance-criteria.md` - Spec-based testing, pass/fail criteria, test case design methodologies

---

## Best Practices

- Test real system integration (no mocks for integration tests)
- Use separate test database (never test against production)
- Implement test isolation (each test independent)
- Verify database state (not just API responses)
- Test authorization enforcement (user isolation)
- Test complete JWT flow (issuance → validation → usage)
- Clean up test data (transaction rollback or explicit cleanup)
- Use fixtures for common setup (users, auth tokens, database)
- Test both happy and error paths
- Run tests in CI/CD pipeline
- Maintain traceability (requirements → tests)
- Keep tests fast (optimize database operations)
- Use meaningful test names (describe what is tested)
- Document test data requirements

---

## Tools and Technologies

### E2E Testing
- Playwright, Cypress
- Browser automation and fixtures

### Backend Testing
- Pytest, FastAPI TestClient
- Database fixtures and factories

### Frontend Testing
- Jest, React Testing Library
- Component testing and mocking

### Database Testing
- PostgreSQL test database
- SQLAlchemy/SQLModel fixtures
- Transaction rollback strategies

### CI/CD
- GitHub Actions, GitLab CI
- Automated test execution
- Coverage reporting

---

## Output Format

When providing integration testing guidance, structure responses as:

**Testing Strategy**: Recommended approach (bottom-up, top-down, sandwich) and rationale
**Test Scope**: Which flows and components to test
**Test Cases**: Specific test scenarios with Given-When-Then format
**Acceptance Criteria**: Clear pass/fail criteria for each test
**Implementation**: Code examples with fixtures and assertions
**Verification**: How to verify tests are working correctly
