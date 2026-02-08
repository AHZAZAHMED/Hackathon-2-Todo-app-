# Research: FastAPI + SQLModel + JWT Integration

**Feature**: Backend API + Database Persistence (003-tasks-crud-api)
**Date**: 2026-02-06
**Purpose**: Document technology decisions and best practices for implementing Task CRUD API

## Overview

This research document captures key decisions for extending the existing FastAPI backend with Task CRUD functionality. The backend infrastructure already exists (JWT verification, database connection, CORS), so this research focuses on integrating new Task model and endpoints with existing patterns.

## Decision 1: Extend Existing Backend Structure

### Context
Backend infrastructure already exists with:
- FastAPI app initialization (app/main.py)
- Database connection with SQLModel (app/database.py)
- JWT verification middleware (app/auth/)
- CORS configuration
- Error handling patterns

### Decision
**Extend existing backend structure** by adding Task model to app/models/ and task routes to app/routes/. Reuse existing get_current_user dependency for authentication.

### Rationale
- **Consistency**: Maintains existing code organization and patterns
- **Efficiency**: Leverages existing infrastructure (no duplication)
- **Maintainability**: Single codebase easier to maintain than multiple services
- **Simplicity**: Appropriate for Phase-2 scope (100 concurrent users, <1000 tasks per user)

### Alternatives Considered
1. **Create separate microservice for tasks**
   - Rejected: Over-engineering for Phase-2 scope
   - Would require: separate deployment, inter-service communication, additional complexity
   - Not justified by current scale requirements

2. **Rebuild backend from scratch**
   - Rejected: Existing infrastructure is production-ready
   - Would waste existing work on JWT verification, database connection, CORS
   - No technical benefit

### Implementation Approach
- Add `backend/app/models/task.py` with Task SQLModel
- Add `backend/app/routes/tasks.py` with 6 CRUD endpoints
- Register routes in `backend/app/main.py`
- Create migration `backend/migrations/002_create_tasks_table.sql`

---

## Decision 2: SQLModel for Task Model

### Context
Existing backend uses SQLModel for User and RateLimit models. Need to define Task model with foreign key to User.

### Decision
**Use SQLModel** for Task model definition with foreign key constraint to user.id.

### Rationale
- **Consistency**: Matches existing User and RateLimit models
- **Type Safety**: SQLModel combines SQLAlchemy (database) + Pydantic (validation)
- **Automatic Validation**: Pydantic validates data before database operations
- **FastAPI Integration**: Seamless integration with FastAPI request/response models

### Pattern
```python
from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", nullable=False, index=True)
    title: str = Field(max_length=500, nullable=False)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Alternatives Considered
1. **Raw SQLAlchemy**
   - Rejected: Requires separate Pydantic models for validation
   - More boilerplate code
   - SQLModel provides same functionality with less code

2. **Prisma (like frontend)**
   - Rejected: Python backend uses SQLModel, not Prisma
   - Would require Node.js runtime for Prisma
   - Inconsistent with existing backend patterns

### Key Features
- **Foreign Key**: `user_id` references `user.id` with CASCADE delete
- **Indexes**: On `user_id` (query performance) and `completed` (filtering)
- **Validation**: Pydantic validates title (required, max 500 chars)
- **Timestamps**: Automatic `created_at` and `updated_at` management

---

## Decision 3: User Isolation via Query Filtering

### Context
Every task query MUST filter by authenticated user_id from JWT. Users should not be able to access other users' tasks.

### Decision
**Filter all queries by user_id from JWT** at the database query level. Return 404 (not 403) for unauthorized access.

### Rationale
- **Security**: Prevents information leakage (404 doesn't reveal task existence)
- **Performance**: Database indexes on user_id make filtering efficient
- **Simplicity**: Single WHERE clause in every query
- **Correctness**: Impossible to forget filtering (enforced at query level)

### Pattern
```python
from fastapi import Depends, HTTPException
from app.auth.dependencies import get_current_user
from sqlmodel import Session, select

@router.get("/api/tasks/{task_id}")
async def get_task(
    task_id: int,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Filter by user_id from JWT
    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user["user_id"]
        )
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"data": task}
```

### Alternatives Considered
1. **Return 403 for unauthorized access**
   - Rejected: Reveals task existence to unauthorized users
   - Specification requires 404 for security through obscurity

2. **Check ownership after fetching**
   - Rejected: Inefficient (fetches task then checks ownership)
   - Violates principle of filtering at query level
   - Risk of forgetting ownership check

3. **Client-side filtering**
   - Rejected: Insecure (client can manipulate requests)
   - Violates JWT-only identity principle

### Key Principles
- **Always filter by user_id**: Every query includes `Task.user_id == user["user_id"]`
- **Return 404 for unauthorized**: Don't reveal task existence
- **Extract user_id from JWT**: Use `get_current_user` dependency
- **Never trust client**: Don't accept user_id from request body/params

---

## Decision 4: Database Migration Strategy

### Context
Need to create tasks table with foreign key to users table. Must be version-controlled and repeatable.

### Decision
**Use SQL migration files** (like existing 001_create_auth_tables.sql) for explicit schema control.

### Rationale
- **Consistency**: Matches existing migration pattern
- **Explicitness**: SQL is explicit and reviewable
- **Version Control**: Migration files tracked in git
- **Rollback**: Easy to create rollback scripts
- **Production-Ready**: Standard practice for production databases

### Pattern
```sql
-- migrations/002_create_tasks_table.sql
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);

-- Verification
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_name = 'tasks'
ORDER BY ordinal_position;
```

### Alternatives Considered
1. **Alembic auto-migrations**
   - Rejected: Adds complexity (Alembic dependency, config files)
   - Auto-generated migrations less reviewable
   - SQL files are simpler and more explicit

2. **SQLModel create_all()**
   - Rejected: Not suitable for production
   - No version control or rollback capability
   - Can't track schema changes over time

### Migration Execution
```bash
# Run migration
psql $DATABASE_URL -f backend/migrations/002_create_tasks_table.sql

# Verify
psql $DATABASE_URL -c "\d tasks"
psql $DATABASE_URL -c "\di tasks*"
```

---

## Decision 5: Response Format Consistency

### Context
Need consistent response format across all endpoints for frontend API client compatibility.

### Decision
**Use envelope format** with `{"data": ...}` for success and `{"error": {...}}` for errors.

### Rationale
- **Consistency**: Matches existing auth endpoints
- **Predictability**: Frontend always knows response structure
- **Error Handling**: Structured error format with code and message
- **Future-Proof**: Easy to add metadata (pagination, etc.) later

### Pattern
```python
# Success responses
{"data": {...}}  # Single resource (GET /api/tasks/{id})
{"data": [...]}  # Collection (GET /api/tasks)

# Error responses
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable message"
    }
}
```

### Examples
```python
# Create task (201)
{
    "data": {
        "id": 1,
        "user_id": "user123",
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "completed": false,
        "created_at": "2026-02-06T10:00:00Z",
        "updated_at": "2026-02-06T10:00:00Z"
    }
}

# Validation error (422)
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Title is required"
    }
}

# Not found (404)
{
    "error": {
        "code": "NOT_FOUND",
        "message": "Task not found"
    }
}
```

### Alternatives Considered
1. **Bare responses (no wrapper)**
   - Rejected: Inconsistent with existing auth endpoints
   - Harder to distinguish success from error in frontend

2. **Envelope with metadata**
   - Rejected: Over-engineering for Phase-2
   - No pagination or metadata needed yet

---

## Technology Stack Summary

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Web Framework | FastAPI | 0.104+ | Existing backend framework, async support, automatic OpenAPI |
| ORM | SQLModel | 0.0.14+ | Existing ORM, combines SQLAlchemy + Pydantic |
| Database | PostgreSQL | 14+ | Existing database (Neon Serverless) |
| Auth | PyJWT | 2.8+ | Existing JWT verification library |
| Server | Uvicorn | 0.24+ | Existing ASGI server for FastAPI |
| Database Driver | psycopg2-binary | 2.9+ | Existing PostgreSQL driver |
| Environment | python-dotenv | 1.0+ | Existing env var management |

## Best Practices Applied

### FastAPI Patterns
- **Dependency Injection**: Use `Depends()` for auth and database session
- **Router Organization**: Separate router per resource (tasks.py)
- **Automatic Docs**: OpenAPI schema generated automatically
- **Async Support**: Use async/await for database operations

### SQLModel Patterns
- **Type Safety**: All fields typed with Python type hints
- **Validation**: Pydantic validates data automatically
- **Relationships**: Foreign keys defined in model
- **Indexes**: Performance indexes on frequently queried columns

### Security Patterns
- **JWT Verification**: Every endpoint requires valid JWT
- **User Isolation**: All queries filter by authenticated user_id
- **Error Obscurity**: Return 404 (not 403) for unauthorized access
- **Input Validation**: Pydantic validates all request data

### Database Patterns
- **Foreign Keys**: Enforce referential integrity
- **CASCADE Delete**: Orphan prevention
- **Indexes**: Performance optimization
- **Migrations**: Version-controlled schema changes

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [PostgreSQL Foreign Keys](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-FK)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLModel Relationships](https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/)

## Conclusion

All technology decisions leverage existing backend infrastructure and follow established patterns. The implementation extends (not replaces) existing code, maintaining consistency and simplicity. All decisions align with constitution principles: spec-driven development, JWT-only identity, database-backed persistence, production-grade architecture, and clear separation of layers.
