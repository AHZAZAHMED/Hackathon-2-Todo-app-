# Full-Stack Testing Patterns

## Next.js Testing Patterns

### Testing API Routes

**API Route Structure**
```typescript
// app/api/[user_id]/tasks/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { user_id: string } }
) {
  const token = request.headers.get('authorization')?.replace('Bearer ', '');

  // Verify JWT and extract user
  const user = await verifyToken(token);

  // Verify user_id matches token
  if (user.id !== parseInt(params.user_id)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 403 });
  }

  // Fetch tasks from backend API
  const response = await fetch(`${BACKEND_URL}/api/${params.user_id}/tasks`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  return NextResponse.json(await response.json());
}
```

**Testing API Routes**
```typescript
// __tests__/api/tasks.test.ts
import { GET, POST } from '@/app/api/[user_id]/tasks/route';
import { NextRequest } from 'next/server';

describe('Tasks API Route', () => {
  let testUser: User;
  let authToken: string;

  beforeEach(async () => {
    // Create test user and get token
    testUser = await createTestUser();
    authToken = await getAuthToken(testUser);
  });

  afterEach(async () => {
    // Cleanup test data
    await cleanupTestUser(testUser.id);
  });

  it('should return tasks for authenticated user', async () => {
    // Create test task in backend
    await createTestTask(testUser.id, 'Test Task');

    // Create request
    const request = new NextRequest(
      `http://localhost:3000/api/${testUser.id}/tasks`,
      {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      }
    );

    // Call API route
    const response = await GET(request, { params: { user_id: testUser.id.toString() } });
    const data = await response.json();

    // Verify response
    expect(response.status).toBe(200);
    expect(data).toHaveLength(1);
    expect(data[0].title).toBe('Test Task');
  });

  it('should return 401 for missing token', async () => {
    const request = new NextRequest(
      `http://localhost:3000/api/${testUser.id}/tasks`
    );

    const response = await GET(request, { params: { user_id: testUser.id.toString() } });

    expect(response.status).toBe(401);
  });

  it('should return 403 for mismatched user_id', async () => {
    const otherUser = await createTestUser();
    const otherToken = await getAuthToken(otherUser);

    const request = new NextRequest(
      `http://localhost:3000/api/${testUser.id}/tasks`,
      {
        headers: {
          'Authorization': `Bearer ${otherToken}`
        }
      }
    );

    const response = await GET(request, { params: { user_id: testUser.id.toString() } });

    expect(response.status).toBe(403);

    await cleanupTestUser(otherUser.id);
  });
});
```

### Testing Server Components

**Server Component**
```typescript
// app/tasks/page.tsx
import { auth } from '@/lib/auth';
import { redirect } from 'next/navigation';

export default async function TasksPage() {
  const session = await auth();

  if (!session) {
    redirect('/login');
  }

  // Fetch tasks from API
  const response = await fetch(`${process.env.BACKEND_URL}/api/${session.user.id}/tasks`, {
    headers: {
      'Authorization': `Bearer ${session.token}`
    },
    cache: 'no-store'
  });

  const tasks = await response.json();

  return (
    <div>
      <h1>Tasks</h1>
      <TaskList tasks={tasks} />
    </div>
  );
}
```

**Testing Server Components**
```typescript
// __tests__/app/tasks/page.test.tsx
import { render, screen } from '@testing-library/react';
import TasksPage from '@/app/tasks/page';
import { auth } from '@/lib/auth';

jest.mock('@/lib/auth');
jest.mock('next/navigation', () => ({
  redirect: jest.fn()
}));

describe('TasksPage', () => {
  it('should redirect to login if not authenticated', async () => {
    (auth as jest.Mock).mockResolvedValue(null);

    await TasksPage();

    expect(redirect).toHaveBeenCalledWith('/login');
  });

  it('should fetch and display tasks for authenticated user', async () => {
    const mockSession = {
      user: { id: 1, username: 'testuser' },
      token: 'mock-token'
    };

    (auth as jest.Mock).mockResolvedValue(mockSession);

    // Mock fetch
    global.fetch = jest.fn().mockResolvedValue({
      json: async () => [
        { id: 1, title: 'Task 1', completed: false },
        { id: 2, title: 'Task 2', completed: true }
      ]
    });

    const component = await TasksPage();
    render(component);

    expect(screen.getByText('Task 1')).toBeInTheDocument();
    expect(screen.getByText('Task 2')).toBeInTheDocument();
  });
});
```

### Testing Client Components

**Client Component**
```typescript
// components/TaskForm.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export function TaskForm({ userId }: { userId: number }) {
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`/api/${userId}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
      });

      if (response.ok) {
        setTitle('');
        router.refresh();
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Task title"
        disabled={loading}
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Creating...' : 'Create Task'}
      </button>
    </form>
  );
}
```

**Testing Client Components**
```typescript
// __tests__/components/TaskForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { TaskForm } from '@/components/TaskForm';
import { useRouter } from 'next/navigation';

jest.mock('next/navigation', () => ({
  useRouter: jest.fn()
}));

describe('TaskForm', () => {
  const mockRefresh = jest.fn();

  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue({
      refresh: mockRefresh
    });
  });

  it('should create task and refresh on submit', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ id: 1, title: 'New Task' })
    });

    render(<TaskForm userId={1} />);

    const input = screen.getByPlaceholderText('Task title');
    const button = screen.getByRole('button');

    fireEvent.change(input, { target: { value: 'New Task' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/1/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: 'New Task' })
      });
      expect(mockRefresh).toHaveBeenCalled();
    });
  });

  it('should show loading state during submission', async () => {
    global.fetch = jest.fn().mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    );

    render(<TaskForm userId={1} />);

    const input = screen.getByPlaceholderText('Task title');
    const button = screen.getByRole('button');

    fireEvent.change(input, { target: { value: 'New Task' } });
    fireEvent.click(button);

    expect(button).toHaveTextContent('Creating...');
    expect(button).toBeDisabled();
    expect(input).toBeDisabled();
  });
});
```

## FastAPI Testing Patterns

### Testing with TestClient

**FastAPI Application**
```python
# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlmodel import Session, select

app = FastAPI()
security = HTTPBearer()

@app.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: int,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    # Verify JWT token
    payload = verify_jwt(token.credentials)
    token_user_id = payload.get("sub")

    # Verify user_id matches token
    if int(token_user_id) != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Query tasks
    tasks = db.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()

    return tasks
```

**Testing FastAPI with TestClient**
```python
# tests/integration/test_task_api.py
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.models import User, Task
import pytest

client = TestClient(app)

@pytest.fixture
def test_db():
    """Create test database session."""
    engine = create_engine("postgresql://test:test@localhost/test_db")
    Session = sessionmaker(bind=engine)
    session = Session()

    Base.metadata.create_all(engine)

    yield session

    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def test_user(test_db):
    """Create test user."""
    user = User(username="testuser", email="test@example.com")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def auth_token(test_user):
    """Generate JWT token for test user."""
    return create_jwt_token({"sub": str(test_user.id)})

def test_get_tasks_success(test_db, test_user, auth_token):
    """Test getting tasks for authenticated user."""
    # Create test tasks
    task1 = Task(user_id=test_user.id, title="Task 1", completed=False)
    task2 = Task(user_id=test_user.id, title="Task 2", completed=True)
    test_db.add_all([task1, task2])
    test_db.commit()

    # Make request
    response = client.get(
        f"/api/{test_user.id}/tasks",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Task 1"
    assert data[1]["title"] == "Task 2"

def test_get_tasks_unauthorized_no_token(test_user):
    """Test getting tasks without authentication token."""
    response = client.get(f"/api/{test_user.id}/tasks")

    assert response.status_code == 401

def test_get_tasks_forbidden_wrong_user(test_db, test_user, auth_token):
    """Test getting tasks for different user."""
    # Create another user
    other_user = User(username="otheruser", email="other@example.com")
    test_db.add(other_user)
    test_db.commit()
    test_db.refresh(other_user)

    # Try to access other user's tasks
    response = client.get(
        f"/api/{other_user.id}/tasks",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 403

def test_create_task_success(test_db, test_user, auth_token):
    """Test creating a task."""
    response = client.post(
        f"/api/{test_user.id}/tasks",
        json={"title": "New Task", "description": "Test description"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Task"
    assert data["user_id"] == test_user.id

    # Verify in database
    task = test_db.query(Task).filter_by(title="New Task").first()
    assert task is not None
    assert task.user_id == test_user.id
```

### Testing Database Operations

**Database CRUD Operations**
```python
# tests/integration/test_database_persistence.py
import pytest
from sqlmodel import Session, select
from app.models import User, Task
from app.database import engine

@pytest.fixture
def db_session():
    """Create database session with transaction rollback."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

def test_task_creation_persists(db_session):
    """Test that task creation persists to database."""
    # Create user
    user = User(username="testuser", email="test@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Create task
    task = Task(
        user_id=user.id,
        title="Test Task",
        description="Test Description",
        completed=False
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    # Verify task exists
    retrieved_task = db_session.get(Task, task.id)
    assert retrieved_task is not None
    assert retrieved_task.title == "Test Task"
    assert retrieved_task.user_id == user.id

def test_task_update_persists(db_session):
    """Test that task updates persist to database."""
    # Create user and task
    user = User(username="testuser", email="test@example.com")
    db_session.add(user)
    db_session.commit()

    task = Task(user_id=user.id, title="Original", completed=False)
    db_session.add(task)
    db_session.commit()
    task_id = task.id

    # Update task
    task.title = "Updated"
    task.completed = True
    db_session.commit()

    # Verify update persisted
    db_session.expire_all()  # Clear session cache
    updated_task = db_session.get(Task, task_id)
    assert updated_task.title == "Updated"
    assert updated_task.completed == True

def test_task_deletion_persists(db_session):
    """Test that task deletion persists to database."""
    # Create user and task
    user = User(username="testuser", email="test@example.com")
    db_session.add(user)
    db_session.commit()

    task = Task(user_id=user.id, title="To Delete", completed=False)
    db_session.add(task)
    db_session.commit()
    task_id = task.id

    # Delete task
    db_session.delete(task)
    db_session.commit()

    # Verify deletion persisted
    deleted_task = db_session.get(Task, task_id)
    assert deleted_task is None

def test_cascade_delete_user_deletes_tasks(db_session):
    """Test that deleting user cascades to tasks."""
    # Create user with tasks
    user = User(username="testuser", email="test@example.com")
    db_session.add(user)
    db_session.commit()

    task1 = Task(user_id=user.id, title="Task 1", completed=False)
    task2 = Task(user_id=user.id, title="Task 2", completed=False)
    db_session.add_all([task1, task2])
    db_session.commit()

    user_id = user.id

    # Delete user
    db_session.delete(user)
    db_session.commit()

    # Verify tasks were deleted
    tasks = db_session.exec(select(Task).where(Task.user_id == user_id)).all()
    assert len(tasks) == 0
```

## JWT Token Flow Testing

### Testing Token Issuance

```python
# tests/integration/test_jwt_issuance.py
import pytest
from datetime import datetime, timedelta
from jose import jwt
from app.auth import create_access_token, BETTER_AUTH_SECRET, ALGORITHM

def test_token_contains_user_id():
    """Test that JWT token contains user ID in sub claim."""
    user_id = 123
    token = create_access_token({"sub": str(user_id)})

    # Decode token
    payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=[ALGORITHM])

    assert payload["sub"] == str(user_id)

def test_token_has_expiration():
    """Test that JWT token has expiration time."""
    token = create_access_token({"sub": "123"})

    # Decode token
    payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=[ALGORITHM])

    assert "exp" in payload
    exp_time = datetime.fromtimestamp(payload["exp"])
    assert exp_time > datetime.utcnow()

def test_token_expires_after_configured_time():
    """Test that token expires after configured duration."""
    # Create token with 1 hour expiration
    expires_delta = timedelta(hours=1)
    token = create_access_token({"sub": "123"}, expires_delta=expires_delta)

    # Decode token
    payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=[ALGORITHM])

    exp_time = datetime.fromtimestamp(payload["exp"])
    expected_exp = datetime.utcnow() + expires_delta

    # Allow 5 second tolerance
    assert abs((exp_time - expected_exp).total_seconds()) < 5
```

### Testing Token Validation

```python
# tests/integration/test_jwt_validation.py
import pytest
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.auth import verify_jwt_token, BETTER_AUTH_SECRET, ALGORITHM

def test_valid_token_is_accepted():
    """Test that valid JWT token is accepted."""
    # Create valid token
    payload = {"sub": "123", "exp": datetime.utcnow() + timedelta(hours=1)}
    token = jwt.encode(payload, BETTER_AUTH_SECRET, algorithm=ALGORITHM)

    # Verify token
    decoded = verify_jwt_token(token)

    assert decoded["sub"] == "123"

def test_expired_token_is_rejected():
    """Test that expired JWT token is rejected."""
    # Create expired token
    payload = {"sub": "123", "exp": datetime.utcnow() - timedelta(hours=1)}
    token = jwt.encode(payload, BETTER_AUTH_SECRET, algorithm=ALGORITHM)

    # Verify token raises error
    with pytest.raises(JWTError):
        verify_jwt_token(token)

def test_invalid_signature_is_rejected():
    """Test that token with invalid signature is rejected."""
    # Create token with wrong secret
    payload = {"sub": "123", "exp": datetime.utcnow() + timedelta(hours=1)}
    token = jwt.encode(payload, "wrong-secret", algorithm=ALGORITHM)

    # Verify token raises error
    with pytest.raises(JWTError):
        verify_jwt_token(token)

def test_malformed_token_is_rejected():
    """Test that malformed token is rejected."""
    malformed_token = "not.a.valid.jwt.token"

    with pytest.raises(JWTError):
        verify_jwt_token(malformed_token)
```

### Testing Token in Request Flow

```python
# tests/integration/test_jwt_request_flow.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_request_with_valid_token_succeeds():
    """Test that request with valid token succeeds."""
    # Create user and token
    user = create_test_user()
    token = create_jwt_token({"sub": str(user.id)})

    # Make request with token
    response = client.get(
        f"/api/{user.id}/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

def test_request_without_token_fails():
    """Test that request without token fails."""
    user = create_test_user()

    # Make request without token
    response = client.get(f"/api/{user.id}/tasks")

    assert response.status_code == 401

def test_request_with_expired_token_fails():
    """Test that request with expired token fails."""
    user = create_test_user()

    # Create expired token
    expired_token = create_jwt_token(
        {"sub": str(user.id)},
        expires_delta=timedelta(seconds=-1)
    )

    # Make request with expired token
    response = client.get(
        f"/api/{user.id}/tasks",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401

def test_request_with_mismatched_user_id_fails():
    """Test that request with mismatched user_id fails."""
    user1 = create_test_user()
    user2 = create_test_user()

    # Create token for user1
    token = create_jwt_token({"sub": str(user1.id)})

    # Try to access user2's resources
    response = client.get(
        f"/api/{user2.id}/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
```

## User Isolation Testing

### Testing User Cannot Access Other Users' Data

```python
# tests/integration/test_user_isolation.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_user_cannot_read_other_users_tasks():
    """Test that user cannot read another user's tasks."""
    # Create two users
    user1 = create_test_user("user1")
    user2 = create_test_user("user2")

    # Create task for user1
    task = create_test_task(user1.id, "User 1 Task")

    # Try to access as user2
    token2 = create_jwt_token({"sub": str(user2.id)})
    response = client.get(
        f"/api/{user2.id}/tasks/{task.id}",
        headers={"Authorization": f"Bearer {token2}"}
    )

    # Should not find task (404) or forbidden (403)
    assert response.status_code in [403, 404]

def test_user_cannot_update_other_users_tasks():
    """Test that user cannot update another user's tasks."""
    user1 = create_test_user("user1")
    user2 = create_test_user("user2")

    # Create task for user1
    task = create_test_task(user1.id, "User 1 Task")

    # Try to update as user2
    token2 = create_jwt_token({"sub": str(user2.id)})
    response = client.put(
        f"/api/{user2.id}/tasks/{task.id}",
        json={"title": "Hacked", "completed": True},
        headers={"Authorization": f"Bearer {token2}"}
    )

    assert response.status_code in [403, 404]

    # Verify task was not modified
    db_task = get_task_from_db(task.id)
    assert db_task.title == "User 1 Task"
    assert db_task.completed == False

def test_user_cannot_delete_other_users_tasks():
    """Test that user cannot delete another user's tasks."""
    user1 = create_test_user("user1")
    user2 = create_test_user("user2")

    # Create task for user1
    task = create_test_task(user1.id, "User 1 Task")

    # Try to delete as user2
    token2 = create_jwt_token({"sub": str(user2.id)})
    response = client.delete(
        f"/api/{user2.id}/tasks/{task.id}",
        headers={"Authorization": f"Bearer {token2}"}
    )

    assert response.status_code in [403, 404]

    # Verify task still exists
    db_task = get_task_from_db(task.id)
    assert db_task is not None

def test_user_list_only_shows_own_tasks():
    """Test that task list only shows user's own tasks."""
    user1 = create_test_user("user1")
    user2 = create_test_user("user2")

    # Create tasks for both users
    task1 = create_test_task(user1.id, "User 1 Task")
    task2 = create_test_task(user2.id, "User 2 Task")

    # Get tasks as user1
    token1 = create_jwt_token({"sub": str(user1.id)})
    response = client.get(
        f"/api/{user1.id}/tasks",
        headers={"Authorization": f"Bearer {token1}"}
    )

    assert response.status_code == 200
    tasks = response.json()

    # Should only see user1's task
    assert len(tasks) == 1
    assert tasks[0]["id"] == task1.id
    assert tasks[0]["title"] == "User 1 Task"
```

## Cross-Layer Integration Testing

### Testing Complete Flow: Frontend → API → Backend → Database

```python
# tests/integration/test_full_stack_flow.py
import pytest
from playwright.sync_api import Page, expect

def test_complete_task_creation_flow(page: Page, test_user, auth_token):
    """Test complete task creation flow across all layers."""
    # 1. Frontend: Navigate to tasks page
    page.goto("http://localhost:3000/tasks")

    # 2. Frontend: Fill and submit form
    page.fill("input[name='title']", "Integration Test Task")
    page.click("button[type='submit']")

    # 3. Verify frontend shows new task
    expect(page.locator("text=Integration Test Task")).to_be_visible()

    # 4. Verify API returns task
    import requests
    response = requests.get(
        f"http://localhost:8000/api/{test_user.id}/tasks",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    tasks = response.json()
    assert any(task["title"] == "Integration Test Task" for task in tasks)

    # 5. Verify database contains task
    from app.database import SessionLocal
    from app.models import Task
    db = SessionLocal()
    task = db.query(Task).filter_by(
        user_id=test_user.id,
        title="Integration Test Task"
    ).first()
    assert task is not None
    assert task.completed == False
    db.close()
```
