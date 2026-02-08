# Integration Testing Strategies

## Test Pyramid and Integration Testing

### The Test Pyramid

```
        /\
       /  \
      / E2E \
     /______\
    /        \
   /Integration\
  /____________\
 /              \
/  Unit Tests    \
/________________\
```

**Distribution**:
- **Unit Tests (70%)**: Fast, isolated, test individual functions/components
- **Integration Tests (20%)**: Test interactions between components/layers
- **E2E Tests (10%)**: Test complete user flows through the system

**Integration Testing Focus**:
- Verify components work together correctly
- Test real database interactions
- Validate API contracts between frontend and backend
- Confirm authentication flows across layers
- Ensure data persistence and retrieval

### Integration vs Unit vs E2E

| Aspect | Unit Tests | Integration Tests | E2E Tests |
|--------|-----------|-------------------|-----------|
| **Scope** | Single function/class | Multiple components/layers | Entire system |
| **Speed** | Very fast (ms) | Medium (seconds) | Slow (minutes) |
| **Isolation** | Fully isolated, mocked | Real dependencies | Real system |
| **Reliability** | Very stable | Moderately stable | Can be flaky |
| **Maintenance** | Low | Medium | High |
| **Value** | Catches logic bugs | Catches integration bugs | Catches user-facing bugs |

**When to Use Integration Tests**:
- ✅ Testing API endpoints with real database
- ✅ Validating authentication flows (JWT issuance and verification)
- ✅ Confirming data persistence across layers
- ✅ Testing user isolation and authorization
- ✅ Verifying frontend-backend contract compliance
- ❌ Testing individual function logic (use unit tests)
- ❌ Testing complete user journeys through UI (use E2E tests)

## Integration Testing Strategies

### 1. Bottom-Up Integration Testing

**Approach**: Test lower-level components first, then integrate upward

```
Database → API Layer → Frontend
```

**Example Flow**:
```python
# Step 1: Test database operations
def test_database_task_crud():
    task = create_task_in_db(user_id=1, title="Test")
    assert task.id is not None

    retrieved = get_task_from_db(task.id)
    assert retrieved.title == "Test"

# Step 2: Test API with database
def test_api_task_creation():
    response = client.post("/api/1/tasks", json={"title": "Test"})
    assert response.status_code == 201

    # Verify in database
    task = db.query(Task).filter_by(title="Test").first()
    assert task is not None

# Step 3: Test frontend with API
def test_frontend_task_creation():
    page.goto("/tasks")
    page.fill("input[name='title']", "Test")
    page.click("button[type='submit']")

    # Verify API was called and DB updated
    assert page.locator("text=Test").is_visible()
```

### 2. Top-Down Integration Testing

**Approach**: Test high-level flows first, stub lower layers initially

```
User Flow → API Calls → Database (stubbed initially)
```

**Example Flow**:
```python
# Step 1: Test user flow with stubbed backend
def test_task_creation_flow_stubbed():
    # Stub API responses
    mock_api.post("/api/1/tasks").returns({"id": 1, "title": "Test"})

    page.goto("/tasks")
    page.fill("input[name='title']", "Test")
    page.click("button[type='submit']")

    assert page.locator("text=Test").is_visible()

# Step 2: Replace stubs with real API
def test_task_creation_flow_real_api():
    page.goto("/tasks")
    page.fill("input[name='title']", "Test")
    page.click("button[type='submit']")

    # Verify real API was called
    response = requests.get(f"{API_URL}/api/1/tasks")
    assert any(task["title"] == "Test" for task in response.json())

# Step 3: Verify database persistence
def test_task_creation_flow_full_stack():
    page.goto("/tasks")
    page.fill("input[name='title']", "Test")
    page.click("button[type='submit']")

    # Verify in database
    task = db.query(Task).filter_by(title="Test").first()
    assert task is not None
```

### 3. Sandwich Integration Testing

**Approach**: Test from both ends simultaneously, meet in the middle

```
Frontend ←→ API Contract ←→ Backend
```

**Example Flow**:
```python
# Test frontend expectations
def test_frontend_expects_task_structure():
    # Frontend expects: {id, title, completed, createdAt}
    mock_response = {"id": 1, "title": "Test", "completed": false, "createdAt": "2024-01-01"}
    # Verify frontend can handle this structure

# Test backend provides correct structure
def test_backend_provides_task_structure():
    response = client.get("/api/1/tasks/1")
    data = response.json()

    # Verify backend returns expected structure
    assert "id" in data
    assert "title" in data
    assert "completed" in data
    assert "createdAt" in data
```

### 4. Big Bang Integration Testing

**Approach**: Integrate all components at once and test

**⚠️ Not Recommended**: Hard to debug, high risk

**Use Only When**:
- Very small system
- Components are well-tested individually
- Time constraints require rapid integration

## Test Design Patterns

### 1. Arrange-Act-Assert (AAA)

```python
def test_task_creation():
    # Arrange: Set up test data and state
    user = create_test_user()
    token = get_auth_token(user)

    # Act: Perform the action
    response = client.post(
        f"/api/{user.id}/tasks",
        json={"title": "Test Task"},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Assert: Verify the outcome
    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"

    # Verify database state
    task = db.query(Task).filter_by(user_id=user.id).first()
    assert task.title == "Test Task"
```

### 2. Given-When-Then (BDD Style)

```python
def test_user_can_create_task():
    # Given: A logged-in user
    user = create_test_user()
    token = authenticate_user(user)

    # When: User creates a task
    response = create_task(user.id, "Test Task", token)

    # Then: Task is created and persisted
    assert response.status_code == 201
    assert task_exists_in_database("Test Task", user.id)
```

### 3. Test Fixtures and Setup/Teardown

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    engine = create_engine("postgresql://test:test@localhost/test_db")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create tables
    Base.metadata.create_all(engine)

    yield session

    # Cleanup
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(username="testuser", email="test@example.com")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def auth_token(test_user):
    """Get authentication token for test user."""
    return generate_jwt_token(test_user.id)

def test_task_creation(db_session, test_user, auth_token):
    """Test task creation with fixtures."""
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={"title": "Test"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
```

### 4. Test Data Builders

```python
class UserBuilder:
    def __init__(self):
        self.username = "testuser"
        self.email = "test@example.com"
        self.password = "password123"

    def with_username(self, username):
        self.username = username
        return self

    def with_email(self, email):
        self.email = email
        return self

    def build(self):
        return User(
            username=self.username,
            email=self.email,
            password_hash=hash_password(self.password)
        )

# Usage
def test_user_isolation():
    user1 = UserBuilder().with_username("user1").build()
    user2 = UserBuilder().with_username("user2").build()

    # Create task for user1
    task = create_task(user1.id, "User 1 Task")

    # Verify user2 cannot access user1's task
    response = client.get(
        f"/api/{user2.id}/tasks/{task.id}",
        headers={"Authorization": f"Bearer {get_token(user2)}"}
    )
    assert response.status_code == 404
```

## Test Isolation and Independence

### Principles

1. **Each test should be independent**: Tests should not depend on other tests
2. **Clean state for each test**: Start with a known, clean state
3. **No shared mutable state**: Avoid global variables or shared test data
4. **Idempotent tests**: Running a test multiple times produces same result

### Database Isolation Strategies

**Strategy 1: Transaction Rollback**
```python
@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()  # Rollback all changes
    connection.close()
```

**Strategy 2: Separate Test Database**
```python
# Use separate database for tests
TEST_DATABASE_URL = "postgresql://test:test@localhost/test_db"

@pytest.fixture(scope="session")
def setup_test_database():
    # Create test database
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)

    yield

    # Drop test database
    Base.metadata.drop_all(engine)
```

**Strategy 3: Database Cleanup**
```python
@pytest.fixture(autouse=True)
def cleanup_database(db_session):
    yield

    # Delete all test data
    db_session.query(Task).delete()
    db_session.query(User).delete()
    db_session.commit()
```

## Test Coverage and Metrics

### What to Measure

1. **Code Coverage**: Percentage of code executed by tests
2. **Branch Coverage**: Percentage of decision branches tested
3. **Integration Points Coverage**: All API endpoints tested
4. **User Flow Coverage**: All critical user journeys tested

### Coverage Goals

```
Integration Tests Coverage Goals:
- API Endpoints: 100% (all endpoints tested)
- Database Operations: 100% (all CRUD operations tested)
- Authentication Flows: 100% (all auth paths tested)
- User Isolation: 100% (all access control tested)
- Error Paths: 80%+ (major error scenarios tested)
```

### Measuring Coverage

```bash
# Python: pytest with coverage
pytest --cov=app --cov-report=html tests/integration/

# JavaScript: Jest with coverage
npm test -- --coverage

# View coverage report
open htmlcov/index.html
```

## Continuous Integration Testing

### CI Pipeline for Integration Tests

```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests

on: [push, pull_request]

jobs:
  integration-tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
          BETTER_AUTH_SECRET: test-secret-key
        run: |
          pytest tests/integration/ -v --cov=app

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Test Organization

### Directory Structure

```
tests/
├── integration/
│   ├── test_auth_flow.py          # Authentication integration tests
│   ├── test_task_api.py           # Task API integration tests
│   ├── test_user_isolation.py     # User isolation tests
│   ├── test_database_persistence.py # Database persistence tests
│   └── conftest.py                # Shared fixtures
├── e2e/
│   ├── test_user_journey.py       # End-to-end user flows
│   └── playwright.config.ts       # E2E test configuration
└── fixtures/
    ├── users.py                   # User test data
    └── tasks.py                   # Task test data
```

### Naming Conventions

```python
# Test file naming
test_<feature>_<layer>.py
# Examples:
# test_auth_integration.py
# test_task_api_integration.py
# test_database_persistence.py

# Test function naming
def test_<action>_<expected_outcome>():
# Examples:
def test_create_task_persists_to_database():
def test_unauthorized_request_returns_401():
def test_user_cannot_access_other_users_tasks():
```

## Best Practices

### ✅ Do's

1. **Test real integrations**: Use real database, real API calls
2. **Clean up after tests**: Ensure tests don't leave data behind
3. **Use meaningful test names**: Describe what is being tested
4. **Test both happy and error paths**: Don't just test success cases
5. **Verify database state**: Check that data is actually persisted
6. **Test authorization**: Verify users can't access unauthorized resources
7. **Use fixtures for setup**: Reuse common setup code
8. **Run tests in CI**: Automate test execution on every commit

### ❌ Don'ts

1. **Don't use mocks for integration tests**: Test real components
2. **Don't share state between tests**: Each test should be independent
3. **Don't test implementation details**: Test behavior, not internals
4. **Don't skip cleanup**: Always clean up test data
5. **Don't hardcode test data**: Use factories or builders
6. **Don't ignore flaky tests**: Fix or remove unreliable tests
7. **Don't test everything in integration tests**: Use unit tests for logic
8. **Don't make tests too slow**: Optimize database operations

## Common Integration Testing Patterns

### Pattern 1: Test Database Transactions

```python
def test_task_creation_is_atomic():
    """Verify task creation is atomic (all or nothing)."""
    user = create_test_user()

    # Attempt to create task with invalid data
    with pytest.raises(ValidationError):
        create_task(user.id, title="", description="Invalid")

    # Verify no partial data was saved
    tasks = db.query(Task).filter_by(user_id=user.id).all()
    assert len(tasks) == 0
```

### Pattern 2: Test Concurrent Operations

```python
import threading

def test_concurrent_task_creation():
    """Verify concurrent task creation doesn't cause conflicts."""
    user = create_test_user()
    token = get_auth_token(user)

    def create_task_thread(title):
        response = client.post(
            f"/api/{user.id}/tasks",
            json={"title": title},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201

    # Create 10 tasks concurrently
    threads = [
        threading.Thread(target=create_task_thread, args=(f"Task {i}",))
        for i in range(10)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    # Verify all 10 tasks were created
    tasks = db.query(Task).filter_by(user_id=user.id).all()
    assert len(tasks) == 10
```

### Pattern 3: Test Data Consistency

```python
def test_task_update_maintains_consistency():
    """Verify task updates maintain data consistency."""
    user = create_test_user()
    task = create_task(user.id, "Original Title")

    # Update task
    response = client.put(
        f"/api/{user.id}/tasks/{task.id}",
        json={"title": "Updated Title", "completed": True},
        headers={"Authorization": f"Bearer {get_token(user)}"}
    )
    assert response.status_code == 200

    # Verify database reflects update
    updated_task = db.query(Task).get(task.id)
    assert updated_task.title == "Updated Title"
    assert updated_task.completed == True
    assert updated_task.user_id == user.id  # User ID unchanged
```
