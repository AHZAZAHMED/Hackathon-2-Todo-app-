# Test Tools and Frameworks

## Playwright (E2E Testing)

### Setup and Configuration

**Installation**
```bash
npm install -D @playwright/test
npx playwright install
```

**Configuration**
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

### Basic Playwright Tests

**Authentication Flow Test**
```typescript
// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('should allow user to sign up', async ({ page }) => {
    await page.goto('/signup');

    // Fill signup form
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Should redirect to tasks page
    await expect(page).toHaveURL('/tasks');
    await expect(page.locator('h1')).toContainText('Tasks');
  });

  test('should allow user to log in', async ({ page }) => {
    await page.goto('/login');

    // Fill login form
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Should redirect to tasks page
    await expect(page).toHaveURL('/tasks');
  });

  test('should reject invalid credentials', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    // Should show error message
    await expect(page.locator('text=Invalid credentials')).toBeVisible();
  });
});
```

**Task Management Test**
```typescript
// tests/e2e/tasks.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Task Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/tasks');
  });

  test('should create a new task', async ({ page }) => {
    // Fill task form
    await page.fill('input[name="title"]', 'New Task');
    await page.fill('textarea[name="description"]', 'Task description');
    await page.click('button[type="submit"]');

    // Verify task appears in list
    await expect(page.locator('text=New Task')).toBeVisible();
  });

  test('should mark task as complete', async ({ page }) => {
    // Create a task first
    await page.fill('input[name="title"]', 'Task to Complete');
    await page.click('button[type="submit"]');

    // Find and click checkbox
    const taskRow = page.locator('text=Task to Complete').locator('..');
    await taskRow.locator('input[type="checkbox"]').check();

    // Verify task is marked complete
    await expect(taskRow).toHaveClass(/completed/);
  });

  test('should delete a task', async ({ page }) => {
    // Create a task first
    await page.fill('input[name="title"]', 'Task to Delete');
    await page.click('button[type="submit"]');

    // Find and click delete button
    const taskRow = page.locator('text=Task to Delete').locator('..');
    await taskRow.locator('button[aria-label="Delete"]').click();

    // Confirm deletion
    await page.locator('button:has-text("Confirm")').click();

    // Verify task is removed
    await expect(page.locator('text=Task to Delete')).not.toBeVisible();
  });
});
```

### Advanced Playwright Features

**Fixtures for Authentication**
```typescript
// tests/e2e/fixtures.ts
import { test as base } from '@playwright/test';

type AuthFixtures = {
  authenticatedPage: Page;
};

export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ page }, use) => {
    // Login
    await page.goto('/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/tasks');

    // Use authenticated page
    await use(page);

    // Logout after test
    await page.click('button[aria-label="Logout"]');
  },
});

// Usage
test('should create task with authenticated page', async ({ authenticatedPage }) => {
  await authenticatedPage.fill('input[name="title"]', 'New Task');
  await authenticatedPage.click('button[type="submit"]');
  await expect(authenticatedPage.locator('text=New Task')).toBeVisible();
});
```

**API Mocking**
```typescript
// tests/e2e/api-mocking.spec.ts
import { test, expect } from '@playwright/test';

test('should handle API errors gracefully', async ({ page }) => {
  // Mock API to return error
  await page.route('**/api/*/tasks', route => {
    route.fulfill({
      status: 500,
      body: JSON.stringify({ error: 'Internal Server Error' })
    });
  });

  await page.goto('/tasks');

  // Verify error message is displayed
  await expect(page.locator('text=Failed to load tasks')).toBeVisible();
});

test('should handle slow API responses', async ({ page }) => {
  // Mock API with delay
  await page.route('**/api/*/tasks', async route => {
    await new Promise(resolve => setTimeout(resolve, 3000));
    route.fulfill({
      status: 200,
      body: JSON.stringify([])
    });
  });

  await page.goto('/tasks');

  // Verify loading state is shown
  await expect(page.locator('text=Loading...')).toBeVisible();
});
```

## Pytest (Backend Testing)

### Setup and Configuration

**Installation**
```bash
pip install pytest pytest-asyncio pytest-cov
```

**Configuration**
```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --cov=app
    --cov-report=html
    --cov-report=term-missing
markers =
    integration: Integration tests
    slow: Slow tests
    auth: Authentication tests
```

### Pytest Fixtures

**Database Fixtures**
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User, Task

TEST_DATABASE_URL = "postgresql://test:test@localhost/test_db"

@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def db_session(engine):
    """Create database session with transaction rollback."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def test_user(db_session):
    """Create test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_token(test_user):
    """Generate JWT token for test user."""
    from app.auth import create_access_token
    return create_access_token({"sub": str(test_user.id)})
```

**FastAPI TestClient Fixture**
```python
# tests/conftest.py
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db

@pytest.fixture
def client(db_session):
    """Create FastAPI test client with test database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### Pytest Markers

**Using Markers**
```python
# tests/integration/test_tasks.py
import pytest

@pytest.mark.integration
def test_create_task(client, test_user, auth_token):
    """Test task creation."""
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={"title": "Test Task"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201

@pytest.mark.slow
@pytest.mark.integration
def test_bulk_task_creation(client, test_user, auth_token):
    """Test creating many tasks."""
    for i in range(100):
        response = client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": f"Task {i}"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 201

# Run only integration tests
# pytest -m integration

# Run all except slow tests
# pytest -m "not slow"
```

### Parametrized Tests

```python
# tests/integration/test_validation.py
import pytest

@pytest.mark.parametrize("title,expected_status", [
    ("Valid Title", 201),
    ("", 422),  # Empty title
    ("A" * 256, 422),  # Too long
    (None, 422),  # Missing title
])
def test_task_title_validation(client, test_user, auth_token, title, expected_status):
    """Test task title validation."""
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={"title": title},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == expected_status

@pytest.mark.parametrize("user_id,token_user_id,expected_status", [
    (1, 1, 200),  # Same user
    (1, 2, 403),  # Different user
    (1, None, 401),  # No token
])
def test_user_authorization(client, user_id, token_user_id, expected_status):
    """Test user authorization."""
    headers = {}
    if token_user_id:
        token = create_access_token({"sub": str(token_user_id)})
        headers["Authorization"] = f"Bearer {token}"

    response = client.get(f"/api/{user_id}/tasks", headers=headers)
    assert response.status_code == expected_status
```

## Jest (Frontend Testing)

### Setup and Configuration

**Installation**
```bash
npm install -D jest @testing-library/react @testing-library/jest-dom
```

**Configuration**
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
  ],
};
```

```javascript
// jest.setup.js
import '@testing-library/jest-dom';
```

### Testing React Components

**Component Test**
```typescript
// __tests__/components/TaskList.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { TaskList } from '@/components/TaskList';

describe('TaskList', () => {
  const mockTasks = [
    { id: 1, title: 'Task 1', completed: false },
    { id: 2, title: 'Task 2', completed: true },
  ];

  it('should render all tasks', () => {
    render(<TaskList tasks={mockTasks} />);

    expect(screen.getByText('Task 1')).toBeInTheDocument();
    expect(screen.getByText('Task 2')).toBeInTheDocument();
  });

  it('should call onToggle when checkbox is clicked', () => {
    const onToggle = jest.fn();
    render(<TaskList tasks={mockTasks} onToggle={onToggle} />);

    const checkbox = screen.getAllByRole('checkbox')[0];
    fireEvent.click(checkbox);

    expect(onToggle).toHaveBeenCalledWith(1);
  });

  it('should call onDelete when delete button is clicked', () => {
    const onDelete = jest.fn();
    render(<TaskList tasks={mockTasks} onDelete={onDelete} />);

    const deleteButton = screen.getAllByLabelText('Delete')[0];
    fireEvent.click(deleteButton);

    expect(onDelete).toHaveBeenCalledWith(1);
  });
});
```

## Database Testing Tools

### PostgreSQL Test Database

**Setup Test Database**
```bash
# Create test database
createdb test_db

# Run migrations
alembic upgrade head

# Seed test data (optional)
python scripts/seed_test_data.py
```

**Database Fixtures with Cleanup**
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def db_engine():
    """Create database engine for tests."""
    engine = create_engine("postgresql://test:test@localhost/test_db")

    # Enable foreign key constraints
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
        cursor.close()

    yield engine

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create database session with automatic cleanup."""
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(autouse=True)
def cleanup_database(db_session):
    """Automatically cleanup database after each test."""
    yield

    # Delete all data in reverse order of dependencies
    db_session.execute("DELETE FROM tasks")
    db_session.execute("DELETE FROM users")
    db_session.commit()
```

### Database Assertions

```python
# tests/helpers/db_assertions.py
from sqlalchemy.orm import Session
from app.models import Task, User

def assert_task_exists(db: Session, task_id: int):
    """Assert that task exists in database."""
    task = db.query(Task).get(task_id)
    assert task is not None, f"Task {task_id} not found in database"
    return task

def assert_task_not_exists(db: Session, task_id: int):
    """Assert that task does not exist in database."""
    task = db.query(Task).get(task_id)
    assert task is None, f"Task {task_id} should not exist in database"

def assert_user_has_tasks(db: Session, user_id: int, expected_count: int):
    """Assert that user has expected number of tasks."""
    count = db.query(Task).filter_by(user_id=user_id).count()
    assert count == expected_count, f"Expected {expected_count} tasks, found {count}"

def assert_task_belongs_to_user(db: Session, task_id: int, user_id: int):
    """Assert that task belongs to user."""
    task = db.query(Task).get(task_id)
    assert task is not None, f"Task {task_id} not found"
    assert task.user_id == user_id, f"Task {task_id} belongs to user {task.user_id}, not {user_id}"

# Usage
def test_task_creation(db_session, test_user):
    task = create_task(test_user.id, "Test Task")
    assert_task_exists(db_session, task.id)
    assert_task_belongs_to_user(db_session, task.id, test_user.id)
```

## API Testing Tools

### Requests Library (Python)

```python
# tests/integration/test_api_requests.py
import requests
import pytest

BASE_URL = "http://localhost:8000"

@pytest.fixture
def api_client():
    """Create API client."""
    return requests.Session()

def test_api_health_check(api_client):
    """Test API health check endpoint."""
    response = api_client.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_api_authentication_flow(api_client):
    """Test complete authentication flow."""
    # Register user
    response = api_client.post(
        f"{BASE_URL}/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 201

    # Login
    response = api_client.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Access protected endpoint
    response = api_client.get(
        f"{BASE_URL}/api/1/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

### HTTPie (CLI Testing)

```bash
# Test API endpoints from command line

# Health check
http GET http://localhost:8000/health

# Register user
http POST http://localhost:8000/auth/register \
  username=testuser \
  email=test@example.com \
  password=password123

# Login
http POST http://localhost:8000/auth/login \
  email=test@example.com \
  password=password123

# Get tasks (with token)
http GET http://localhost:8000/api/1/tasks \
  Authorization:"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Create task
http POST http://localhost:8000/api/1/tasks \
  Authorization:"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  title="New Task" \
  description="Task description"
```

## Test Data Management

### Factory Pattern

```python
# tests/factories.py
from app.models import User, Task
from datetime import datetime

class UserFactory:
    """Factory for creating test users."""

    @staticmethod
    def create(db, **kwargs):
        """Create user with default or custom attributes."""
        defaults = {
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "created_at": datetime.utcnow()
        }
        defaults.update(kwargs)

        user = User(**defaults)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

class TaskFactory:
    """Factory for creating test tasks."""

    @staticmethod
    def create(db, user_id, **kwargs):
        """Create task with default or custom attributes."""
        defaults = {
            "title": "Test Task",
            "description": "Test description",
            "completed": False,
            "created_at": datetime.utcnow()
        }
        defaults.update(kwargs)

        task = Task(user_id=user_id, **defaults)
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

# Usage
def test_with_factories(db_session):
    user = UserFactory.create(db_session, username="john")
    task = TaskFactory.create(db_session, user.id, title="Important Task")

    assert task.user_id == user.id
    assert task.title == "Important Task"
```

### Test Data Builders

```python
# tests/builders.py
class TaskBuilder:
    """Builder for creating test tasks."""

    def __init__(self, user_id):
        self.user_id = user_id
        self.title = "Test Task"
        self.description = None
        self.completed = False

    def with_title(self, title):
        self.title = title
        return self

    def with_description(self, description):
        self.description = description
        return self

    def completed(self):
        self.completed = True
        return self

    def build(self, db):
        task = Task(
            user_id=self.user_id,
            title=self.title,
            description=self.description,
            completed=self.completed
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

# Usage
def test_with_builder(db_session, test_user):
    task = (TaskBuilder(test_user.id)
            .with_title("Important Task")
            .with_description("Very important")
            .completed()
            .build(db_session))

    assert task.title == "Important Task"
    assert task.completed == True
```

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  backend-tests:
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
          pytest tests/integration/ -v --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test -- --coverage

  e2e-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright
        run: npx playwright install --with-deps

      - name: Start services
        run: |
          docker-compose up -d
          npm run dev &
          sleep 10

      - name: Run E2E tests
        run: npx playwright test

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```
