# Backend Rules - FastAPI Todo Application

**Context**: FastAPI backend for Hackathon II Phase-2 Todo Application

## Architecture

- **Framework**: FastAPI 0.109+
- **Language**: Python 3.11+
- **ORM**: SQLModel 0.0.14+ (SQLAlchemy-based)
- **Database**: PostgreSQL (Neon Serverless)
- **Authentication**: JWT verification (Better Auth tokens)
- **Server**: Uvicorn ASGI server

## Core Rules

### 1. JWT-Only Identity

**CRITICAL**: User identity derives EXCLUSIVELY from verified JWT claims.

```python
# ✅ CORRECT - Extract user_id from JWT
@app.post("/api/tasks")
async def create_task(
    task_data: TaskCreate,
    user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = user["user_id"]  # From JWT claims
    task = Task(user_id=user_id, **task_data.dict())
    # ...

# ❌ WRONG - NEVER accept user_id from request body
@app.post("/api/tasks")
async def create_task(task_data: TaskCreate):
    user_id = task_data.user_id  # SECURITY VIOLATION
    # ...
```

**Rules**:
- ✅ ALL endpoints MUST use `Depends(get_current_user)` for authentication
- ✅ Extract `user_id` from JWT claims dictionary
- ❌ NEVER accept `user_id` from request body, query params, or path params
- ❌ NEVER trust client-provided identity
- ✅ Return 401 for missing/invalid JWT
- ✅ Return 404 (not 403) for unauthorized resource access

### 2. Database-Backed Persistence

**CRITICAL**: All state MUST persist in PostgreSQL. NO mock data, NO in-memory storage.

```python
# ✅ CORRECT - Query database
async def get_tasks(user: Dict[str, Any] = Depends(get_current_user)):
    with Session(engine) as session:
        tasks = session.exec(
            select(Task).where(Task.user_id == user["user_id"])
        ).all()
        return {"data": tasks}

# ❌ WRONG - Mock data
async def get_tasks():
    return {"data": [{"id": 1, "title": "Mock task"}]}  # VIOLATION
```

**Rules**:
- ✅ Use SQLModel for all database models
- ✅ Use database sessions for all queries
- ✅ Enforce foreign key constraints in schema
- ❌ NEVER return hardcoded data
- ❌ NEVER use in-memory storage
- ✅ Handle database errors gracefully (503 Service Unavailable)

### 3. User Isolation at Query Level

**CRITICAL**: Filter ALL queries by authenticated `user_id` from JWT.

```python
# ✅ CORRECT - Filter by JWT user_id
async def get_task(
    task_id: int,
    user: Dict[str, Any] = Depends(get_current_user)
):
    with Session(engine) as session:
        task = session.exec(
            select(Task)
            .where(Task.id == task_id)
            .where(Task.user_id == user["user_id"])  # User isolation
        ).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        return {"data": task}

# ❌ WRONG - No user isolation
async def get_task(task_id: int):
    with Session(engine) as session:
        task = session.get(Task, task_id)  # SECURITY VIOLATION
        return {"data": task}
```

**Rules**:
- ✅ ALL queries MUST filter by `user_id` from JWT
- ✅ Return 404 if resource doesn't exist OR doesn't belong to user
- ❌ NEVER return 403 (reveals resource existence)
- ✅ Use `.where(Task.user_id == user["user_id"])` in all queries
- ✅ Verify user ownership before updates/deletes

### 4. Response Format Consistency

**Standard**: Use envelope format for all responses.

```python
# ✅ SUCCESS - Envelope with data
{"data": <resource or array>}

# ✅ ERROR - Envelope with error
{"error": {"code": "ERROR_CODE", "message": "Human-readable message"}}
```

**Status Codes**:
- `200 OK` - Successful GET/PUT/PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE (empty body)
- `401 Unauthorized` - Missing/invalid JWT
- `404 Not Found` - Resource not found or unauthorized
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Unexpected error
- `503 Service Unavailable` - Database connection failure

### 5. SQLModel Patterns

**Models**: Define database tables as SQLModel classes.

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """Task model with user isolation."""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=500)
    description: Optional[str] = None
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Pydantic Schemas**: Separate request/response models.

```python
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    """Request schema for creating tasks."""
    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = None

class TaskUpdate(BaseModel):
    """Request schema for updating tasks."""
    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = None

class TaskResponse(BaseModel):
    """Response schema for task data."""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
```

### 6. Database Session Management

**Pattern**: Use context manager for sessions.

```python
from sqlmodel import Session, create_engine, select
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)

# ✅ CORRECT - Context manager
async def get_tasks(user: Dict[str, Any] = Depends(get_current_user)):
    with Session(engine) as session:
        tasks = session.exec(
            select(Task).where(Task.user_id == user["user_id"])
        ).all()
        return {"data": tasks}

# ❌ WRONG - No session cleanup
async def get_tasks(user: Dict[str, Any] = Depends(get_current_user)):
    session = Session(engine)
    tasks = session.exec(select(Task)).all()  # Session never closed
    return {"data": tasks}
```

**Rules**:
- ✅ Use `with Session(engine) as session:` for automatic cleanup
- ✅ Handle database exceptions with try-except
- ✅ Return 503 if database connection fails
- ❌ NEVER leave sessions open

### 7. Validation and Error Handling

**Input Validation**: Use Pydantic models.

```python
from pydantic import BaseModel, Field, validator

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = None

    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
```

**Error Handling**: Catch and return proper status codes.

```python
from fastapi import HTTPException

@app.post("/api/tasks")
async def create_task(
    task_data: TaskCreate,
    user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        with Session(engine) as session:
            task = Task(
                user_id=user["user_id"],
                title=task_data.title,
                description=task_data.description
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            return {"data": task}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={"code": "SERVICE_UNAVAILABLE", "message": "Database error"}
        )
```

### 8. JWT Verification

**Dependency**: Use existing `get_current_user` from `app.auth.dependencies`.

```python
from app.auth.dependencies import get_current_user
from typing import Dict, Any

@app.get("/api/tasks")
async def list_tasks(user: Dict[str, Any] = Depends(get_current_user)):
    """
    List all tasks for authenticated user.

    Args:
        user: JWT claims dict with user_id, email, name

    Returns:
        {"data": [tasks]}
    """
    user_id = user["user_id"]
    # Query tasks filtered by user_id
```

**JWT Claims Structure**:
```python
{
    "user_id": "clx1234567890",  # User identifier
    "email": "user@example.com",
    "name": "John Doe",
    "exp": 1234567890,  # Expiration timestamp
    "iat": 1234567890   # Issued at timestamp
}
```

### 9. Database Migrations

**Format**: SQL files in `backend/migrations/` directory.

```sql
-- migrations/002_create_tasks_table.sql

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
```

**Execution**:
```bash
psql $DATABASE_URL -f backend/migrations/002_create_tasks_table.sql
```

**Rules**:
- ✅ Use explicit SQL migration files (not Alembic)
- ✅ Include rollback script in comments
- ✅ Test migrations on development database first
- ✅ Verify foreign key constraints after migration
- ❌ NEVER run migrations in production without backup

### 10. CORS Configuration

**Setup**: Already configured in `app/main.py`.

```python
from fastapi.middleware.cors import CORSMiddleware
from app.config import FRONTEND_URL

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # Explicit whitelist
    allow_credentials=True,  # Required for cookies
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**Rules**:
- ✅ Use explicit origin whitelist (no wildcards in production)
- ✅ Enable credentials for JWT cookies
- ✅ Whitelist only required methods and headers
- ❌ NEVER use `allow_origins=["*"]` with `allow_credentials=True`

## File Organization

```
backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, routes
│   ├── config.py            # Environment variables
│   ├── auth/
│   │   └── dependencies.py  # get_current_user JWT verification
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User model (Better Auth)
│   │   └── task.py          # Task model (NEW)
│   ├── routes/
│   │   ├── __init__.py
│   │   └── tasks.py         # Task CRUD endpoints (NEW)
│   └── schemas/
│       ├── __init__.py
│       └── task.py          # Pydantic request/response schemas (NEW)
├── migrations/
│   ├── 001_initial.sql      # User table (Better Auth)
│   └── 002_create_tasks_table.sql  # Tasks table (NEW)
├── .env                     # Environment variables (gitignored)
├── .env.example             # Template with placeholders
├── requirements.txt         # Python dependencies
└── CLAUDE.md               # This file
```

## Environment Variables

Required in `.env`:

```bash
# JWT Verification (MUST match frontend)
BETTER_AUTH_SECRET=your-64-character-hex-secret-here

# Database Connection
DATABASE_URL=postgresql://user:password@host:port/database

# CORS Configuration
FRONTEND_URL=http://localhost:3000

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

## Development Workflow

1. **Start server**: `uvicorn app.main:app --reload`
2. **Run migration**: `psql $DATABASE_URL -f migrations/002_create_tasks_table.sql`
3. **Check logs**: Watch console for errors
4. **Test endpoints**: Use Swagger UI at http://localhost:8000/docs

## Quality Standards

- No startup errors
- JWT verification rejects invalid tokens (401)
- All endpoints filter by JWT user_id
- Database queries use proper sessions
- Foreign key constraints enforced
- User isolation verified (User A ≠ User B tasks)
- Error responses follow envelope format

## Common Patterns

### Protected Endpoint with User Isolation

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Dict, Any
from app.auth.dependencies import get_current_user
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskResponse

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.post("/", response_model=Dict[str, TaskResponse], status_code=201)
async def create_task(
    task_data: TaskCreate,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create new task for authenticated user.

    - **title**: Task title (required, max 500 chars)
    - **description**: Task description (optional)

    Returns 201 with created task.
    Returns 401 if JWT invalid.
    Returns 422 if validation fails.
    """
    try:
        with Session(engine) as session:
            task = Task(
                user_id=user["user_id"],  # From JWT, not request
                title=task_data.title,
                description=task_data.description,
                completed=False
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            return {"data": task}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={"code": "SERVICE_UNAVAILABLE", "message": "Database error"}
        )

@router.get("/", response_model=Dict[str, list[TaskResponse]])
async def list_tasks(user: Dict[str, Any] = Depends(get_current_user)):
    """
    List all tasks for authenticated user.

    Returns tasks in reverse chronological order (newest first).
    Returns empty array if no tasks.
    Returns 401 if JWT invalid.
    """
    try:
        with Session(engine) as session:
            tasks = session.exec(
                select(Task)
                .where(Task.user_id == user["user_id"])
                .order_by(Task.created_at.desc())
            ).all()
            return {"data": tasks}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={"code": "SERVICE_UNAVAILABLE", "message": "Database error"}
        )

@router.get("/{task_id}", response_model=Dict[str, TaskResponse])
async def get_task(
    task_id: int,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get single task by ID.

    Returns 404 if task doesn't exist or doesn't belong to user.
    Returns 401 if JWT invalid.
    """
    try:
        with Session(engine) as session:
            task = session.exec(
                select(Task)
                .where(Task.id == task_id)
                .where(Task.user_id == user["user_id"])
            ).first()

            if not task:
                raise HTTPException(
                    status_code=404,
                    detail={"code": "NOT_FOUND", "message": "Task not found"}
                )

            return {"data": task}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={"code": "SERVICE_UNAVAILABLE", "message": "Database error"}
        )
```

### Update with Timestamp

```python
from datetime import datetime

@router.put("/{task_id}", response_model=Dict[str, TaskResponse])
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Update task title and description."""
    try:
        with Session(engine) as session:
            task = session.exec(
                select(Task)
                .where(Task.id == task_id)
                .where(Task.user_id == user["user_id"])
            ).first()

            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            task.title = task_data.title
            task.description = task_data.description
            task.updated_at = datetime.utcnow()  # Update timestamp

            session.add(task)
            session.commit()
            session.refresh(task)
            return {"data": task}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database error")
```

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- API Contracts: specs/003-tasks-crud-api/contracts/tasks-api.md
- Data Model: specs/003-tasks-crud-api/data-model.md

## Notes

- This is backend-only. Frontend implemented separately.
- JWT verification already implemented in `app/auth/dependencies.py`.
- Database connection already configured in `app/config.py`.
- CORS already configured in `app/main.py`.
- Focus on Task CRUD endpoints with user isolation.
