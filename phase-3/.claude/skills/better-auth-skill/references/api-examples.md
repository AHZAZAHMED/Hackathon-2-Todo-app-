# API Examples for Better Auth Integration

## Complete FastAPI Backend Implementation

### Project Structure

```
backend/
├── main.py                      # Application entry point
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
└── src/
    ├── __init__.py
    ├── core/
    │   ├── __init__.py
    │   └── config.py           # Settings configuration
    ├── database/
    │   ├── __init__.py
    │   ├── engine.py           # Database engine
    │   └── session.py          # Session management
    ├── models/
    │   ├── __init__.py
    │   ├── user.py             # User model
    │   └── task.py             # Task model
    ├── auth/
    │   ├── __init__.py
    │   ├── jwt.py              # JWT utilities
    │   └── dependency.py       # Auth dependencies
    └── api/
        ├── __init__.py
        ├── auth_routes.py      # Authentication endpoints
        └── task_routes.py      # Task endpoints
```

### Configuration (src/core/config.py)

```python
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "Todo API"
    environment: str = "development"

    # Security
    better_auth_secret: str
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    # Database
    database_url: str

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
```

### Database Engine (src/database/engine.py)

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from ..core.config import settings


engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300,
)
```

### Database Session (src/database/session.py)

```python
from sqlmodel import Session
from .engine import engine


def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session
```

### User Model (src/models/user.py)

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid


class User(SQLModel, table=True):
    """User model."""

    __tablename__ = "users"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    email: str = Field(unique=True, index=True)
    password_hash: str
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(SQLModel):
    """User creation schema."""
    email: str
    password: str
    name: Optional[str] = None


class UserPublic(SQLModel):
    """Public user schema (no password)."""
    id: str
    email: str
    name: Optional[str]
```

### Task Model (src/models/task.py)

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Task(SQLModel, table=True):
    """Task model."""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, foreign_key="users.id")
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=10000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(SQLModel):
    """Task creation schema."""
    title: str
    description: Optional[str] = None


class TaskUpdate(SQLModel):
    """Task update schema."""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskPublic(SQLModel):
    """Public task schema."""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
```

### JWT Utilities (src/auth/jwt.py)

```python
import jwt
from datetime import datetime, timedelta
from typing import Dict
from ..core.config import settings
import uuid


def generate_access_token(user_id: str, email: str) -> str:
    """Generate JWT access token."""

    now = datetime.utcnow()
    expiration = now + timedelta(minutes=settings.access_token_expire_minutes)

    payload = {
        "sub": user_id,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(expiration.timestamp()),
        "jti": str(uuid.uuid4()),
        "type": "access"
    }

    token = jwt.encode(
        payload,
        settings.better_auth_secret,
        algorithm="HS256"
    )

    return token


def generate_refresh_token(user_id: str, email: str) -> str:
    """Generate JWT refresh token."""

    now = datetime.utcnow()
    expiration = now + timedelta(days=settings.refresh_token_expire_days)

    payload = {
        "sub": user_id,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(expiration.timestamp()),
        "jti": str(uuid.uuid4()),
        "type": "refresh"
    }

    token = jwt.encode(
        payload,
        settings.better_auth_secret,
        algorithm="HS256"
    )

    return token


def verify_token(token: str) -> Dict:
    """Verify and decode JWT token."""

    try:
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
```

### Authentication Dependency (src/auth/dependency.py)

```python
from fastapi import Depends, HTTPException, Header
from typing import Dict
from .jwt import verify_token


async def verify_jwt_token(
    authorization: str = Header(None)
) -> Dict:
    """Verify JWT token from Authorization header."""

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme"
        )

    token = authorization.replace("Bearer ", "")

    try:
        payload = verify_token(token)

        if "sub" not in payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload"
            )

        return payload

    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )


async def verify_user_access(
    user_id: str,
    current_user: Dict = Depends(verify_jwt_token)
) -> Dict:
    """Verify user can access resource."""

    if current_user["sub"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden"
        )

    return current_user
```

### Authentication Routes (src/api/auth_routes.py)

```python
from fastapi import APIRouter, HTTPException, Depends, Form
from sqlmodel import Session, select
from passlib.context import CryptContext
from ..database.session import get_session
from ..models.user import User, UserCreate, UserPublic
from ..auth.jwt import generate_access_token, generate_refresh_token


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/sign-up/email")
async def sign_up(
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(None),
    session: Session = Depends(get_session)
):
    """Register new user with email and password."""

    # Check if user already exists
    existing_user = session.exec(
        select(User).where(User.email == email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash password
    password_hash = pwd_context.hash(password)

    # Create user
    user = User(
        email=email,
        password_hash=password_hash,
        name=name or email.split('@')[0]
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # Generate tokens
    access_token = generate_access_token(user.id, user.email)
    refresh_token = generate_refresh_token(user.id, user.email)

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        },
        "token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/sign-in/email")
async def sign_in(
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    """Sign in with email and password."""

    # Find user
    user = session.exec(
        select(User).where(User.email == email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # Verify password
    if not pwd_context.verify(password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # Generate tokens
    access_token = generate_access_token(user.id, user.email)
    refresh_token = generate_refresh_token(user.id, user.email)

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        },
        "token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/sign-out")
async def sign_out():
    """Sign out user (client should clear tokens)."""
    return {"message": "Signed out successfully"}
```

### Task Routes (src/api/task_routes.py)

```python
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List
from ..database.session import get_session
from ..models.task import Task, TaskCreate, TaskUpdate, TaskPublic
from ..auth.dependency import verify_user_access
from datetime import datetime


router = APIRouter()


@router.get("/{user_id}/tasks", response_model=List[TaskPublic])
async def get_tasks(
    user_id: str,
    current_user: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """Get all tasks for authenticated user."""

    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()

    return tasks


@router.post("/{user_id}/tasks", response_model=TaskPublic, status_code=201)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """Create new task for authenticated user."""

    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskPublic)
async def get_task(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """Get specific task for authenticated user."""

    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskPublic)
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    current_user: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """Update task for authenticated user."""

    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # Update fields
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.completed is not None:
        task.completed = task_data.completed

    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.delete("/{user_id}/tasks/{task_id}", status_code=204)
async def delete_task(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """Delete task for authenticated user."""

    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    session.delete(task)
    session.commit()

    return None


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskPublic)
async def toggle_task_completion(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """Toggle task completion status."""

    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task
```

### Main Application (main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from src.core.config import settings
from src.database.engine import engine
from src.api.auth_routes import router as auth_router
from src.api.task_routes import router as task_router
from src.models import user, task  # Import models to register them


app = FastAPI(
    title=settings.app_name,
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Create database tables on startup."""
    SQLModel.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.app_name}"}


# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(task_router, prefix="/api", tags=["tasks"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Requirements (requirements.txt)

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlmodel==0.0.14
psycopg2-binary==2.9.9
pyjwt==2.8.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic-settings==2.1.0
```

### Environment Variables (.env)

```bash
# Application
APP_NAME=Todo API
ENVIRONMENT=development

# Security
BETTER_AUTH_SECRET=your-secret-key-here-generate-with-openssl-rand-hex-32
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

## Testing the API

### Using cURL

```bash
# Register user
curl -X POST http://localhost:8000/api/auth/sign-up/email \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=test@example.com&password=password123&name=Test User"

# Response:
# {
#   "user": {"id": "uuid", "email": "test@example.com", "name": "Test User"},
#   "token": "eyJhbGc...",
#   "refresh_token": "eyJhbGc...",
#   "token_type": "bearer"
# }

# Login
curl -X POST http://localhost:8000/api/auth/sign-in/email \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=test@example.com&password=password123"

# Get tasks (with authentication)
curl -X GET http://localhost:8000/api/user-uuid/tasks \
  -H "Authorization: Bearer eyJhbGc..."

# Create task
curl -X POST http://localhost:8000/api/user-uuid/tasks \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"title": "My first task", "description": "Task description"}'

# Update task
curl -X PUT http://localhost:8000/api/user-uuid/tasks/1 \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated task", "completed": true}'

# Delete task
curl -X DELETE http://localhost:8000/api/user-uuid/tasks/1 \
  -H "Authorization: Bearer eyJhbGc..."
```

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Register
response = requests.post(
    f"{BASE_URL}/api/auth/sign-up/email",
    data={
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User"
    }
)
data = response.json()
token = data["token"]
user_id = data["user"]["id"]

# Get tasks
response = requests.get(
    f"{BASE_URL}/api/{user_id}/tasks",
    headers={"Authorization": f"Bearer {token}"}
)
tasks = response.json()

# Create task
response = requests.post(
    f"{BASE_URL}/api/{user_id}/tasks",
    headers={"Authorization": f"Bearer {token}"},
    json={"title": "My task", "description": "Description"}
)
task = response.json()
```
