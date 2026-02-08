# Data Model: Task Entity

**Feature**: Backend API + Database Persistence (003-tasks-crud-api)
**Date**: 2026-02-06
**Purpose**: Define the Task entity structure, relationships, and validation rules

## Entity Overview

The **Task** entity represents a user's task item in the todo application. Each task belongs to exactly one user and contains a title, optional description, completion status, and timestamps.

## Entity Definition

### Task

**Table Name**: `tasks`

**Description**: Represents a single task item owned by a user. Tasks are isolated by user - each user can only access their own tasks.

### Fields

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `id` | Integer | PRIMARY KEY, AUTO INCREMENT | (auto) | Unique task identifier |
| `user_id` | String (TEXT) | NOT NULL, FOREIGN KEY → user.id, INDEXED | (from JWT) | Owner of the task |
| `title` | String (VARCHAR 500) | NOT NULL, MAX 500 chars | (required) | Task title |
| `description` | Text | NULLABLE | NULL | Optional task description |
| `completed` | Boolean | NOT NULL, INDEXED | FALSE | Completion status |
| `created_at` | Timestamp | NOT NULL | NOW() | Creation timestamp (UTC) |
| `updated_at` | Timestamp | NOT NULL | NOW() | Last update timestamp (UTC) |

### Field Details

#### id (Primary Key)
- **Type**: Integer (SERIAL in PostgreSQL)
- **Purpose**: Unique identifier for each task
- **Generation**: Auto-incremented by database
- **Usage**: Used in API endpoints (/api/tasks/{id})

#### user_id (Foreign Key)
- **Type**: String (TEXT) - matches user.id type from Better Auth
- **Purpose**: Links task to owning user
- **Constraint**: FOREIGN KEY REFERENCES user(id) ON DELETE CASCADE
- **Index**: Yes (for query performance)
- **Source**: Extracted from JWT token claims (never from client request)
- **Validation**: Must match authenticated user from JWT

#### title
- **Type**: String (VARCHAR 500)
- **Purpose**: Task title/summary
- **Constraints**:
  - NOT NULL (required)
  - Maximum 500 characters
  - Cannot be empty string
- **Validation**: Enforced by SQLModel and database
- **Example**: "Buy groceries", "Call dentist", "Finish project report"

#### description
- **Type**: Text (unlimited length)
- **Purpose**: Optional detailed description of the task
- **Constraints**: NULLABLE (optional)
- **Default**: NULL
- **Validation**: Can be null, empty string, or any text
- **Example**: "Milk, eggs, bread, coffee", "Schedule appointment for next week"

#### completed
- **Type**: Boolean
- **Purpose**: Tracks whether task is done
- **Constraints**: NOT NULL
- **Default**: FALSE (new tasks are incomplete)
- **Index**: Yes (for filtering completed/incomplete tasks)
- **Validation**: Must be true or false (no null)
- **Behavior**: Toggled by PATCH /api/tasks/{id}/complete endpoint

#### created_at
- **Type**: Timestamp (TIMESTAMP in PostgreSQL)
- **Purpose**: Records when task was created
- **Constraints**: NOT NULL
- **Default**: NOW() (current UTC timestamp)
- **Timezone**: UTC (all timestamps stored in UTC)
- **Immutable**: Never updated after creation
- **Usage**: For sorting tasks (newest first)

#### updated_at
- **Type**: Timestamp (TIMESTAMP in PostgreSQL)
- **Purpose**: Records last modification time
- **Constraints**: NOT NULL
- **Default**: NOW() (current UTC timestamp)
- **Timezone**: UTC
- **Behavior**: Automatically updated on PUT or PATCH operations
- **Usage**: For tracking recent changes, conflict detection

## Relationships

### Task → User (Many-to-One)

**Relationship**: Each task belongs to exactly one user. Each user can have many tasks.

**Foreign Key**: `tasks.user_id` → `user.id`

**Cascade Behavior**: ON DELETE CASCADE
- When a user is deleted, all their tasks are automatically deleted
- Prevents orphan tasks in the database
- Enforces referential integrity

**Query Pattern**:
```sql
-- Get all tasks for a user
SELECT * FROM tasks WHERE user_id = 'user123';

-- Get task with ownership check
SELECT * FROM tasks WHERE id = 1 AND user_id = 'user123';
```

**SQLModel Definition**:
```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", nullable=False, index=True)
    # ... other fields
```

## Indexes

### Primary Index
- **Column**: `id`
- **Type**: PRIMARY KEY (automatic)
- **Purpose**: Unique task identification
- **Performance**: O(log n) lookups by ID

### User Index
- **Column**: `user_id`
- **Type**: B-tree index
- **Purpose**: Fast filtering by user
- **Performance**: Critical for "get all user's tasks" query
- **Query Pattern**: `WHERE user_id = ?`

### Completion Index
- **Column**: `completed`
- **Type**: B-tree index
- **Purpose**: Fast filtering by completion status
- **Performance**: Useful for future filtering features
- **Query Pattern**: `WHERE completed = true/false`

### Composite Index (Future)
- **Columns**: `(user_id, completed)`
- **Status**: Not implemented in Phase-2
- **Purpose**: Would optimize filtered queries
- **Query Pattern**: `WHERE user_id = ? AND completed = ?`

## Validation Rules

### Title Validation
- **Required**: Yes (cannot be null or empty)
- **Max Length**: 500 characters
- **Min Length**: 1 character (implicit - not empty)
- **Allowed Characters**: Any UTF-8 characters
- **Trimming**: Frontend should trim whitespace
- **Error**: 422 VALIDATION_ERROR if empty or too long

### Description Validation
- **Required**: No (optional field)
- **Max Length**: Unlimited (TEXT type)
- **Allowed Values**: NULL, empty string, or any text
- **Trimming**: Optional (frontend decision)

### Completed Validation
- **Required**: Yes (boolean field)
- **Allowed Values**: true or false only
- **Default**: false (for new tasks)
- **Type Enforcement**: Database and SQLModel enforce boolean type

### User ID Validation
- **Source**: MUST come from JWT token claims
- **Client Input**: NEVER accepted from request body/params
- **Validation**: Must match authenticated user
- **Enforcement**: Query-level filtering (WHERE user_id = ?)

### Timestamp Validation
- **Format**: ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)
- **Timezone**: UTC only
- **Automatic**: Set by database (NOW())
- **Client Input**: Ignored (server-controlled)

## State Transitions

### Task Lifecycle

```
[Created] → completed = false
    ↓
[Active] → User can update title/description
    ↓
[Completed] → completed = true (via PATCH /api/tasks/{id}/complete)
    ↓
[Active] → completed = false (toggle back)
    ↓
[Deleted] → Removed from database (via DELETE /api/tasks/{id})
```

### State Rules
- **Creation**: Always starts with completed = false
- **Completion**: Can be toggled multiple times (true ↔ false)
- **Update**: Title/description can be updated in any state
- **Deletion**: Permanent (no soft delete in Phase-2)

## Database Schema (SQL)

```sql
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
```

## SQLModel Definition (Python)

```python
from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """
    Task entity representing a user's task item.

    Each task belongs to exactly one user (via user_id foreign key).
    Tasks are isolated by user - queries always filter by authenticated user_id.
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(
        foreign_key="user.id",
        nullable=False,
        index=True,
        description="Owner of the task (from JWT)"
    )
    title: str = Field(
        max_length=500,
        nullable=False,
        description="Task title (required, max 500 chars)"
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional task description"
    )
    completed: bool = Field(
        default=False,
        index=True,
        description="Completion status"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp (UTC)"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp (UTC)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user123",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "created_at": "2026-02-06T10:00:00Z",
                "updated_at": "2026-02-06T10:00:00Z"
            }
        }
```

## Example Data

### Sample Task (JSON)
```json
{
    "id": 1,
    "user_id": "clx1234567890",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread, coffee",
    "completed": false,
    "created_at": "2026-02-06T10:00:00Z",
    "updated_at": "2026-02-06T10:00:00Z"
}
```

### Sample Task (Completed)
```json
{
    "id": 2,
    "user_id": "clx1234567890",
    "title": "Call dentist",
    "description": null,
    "completed": true,
    "created_at": "2026-02-05T14:30:00Z",
    "updated_at": "2026-02-06T09:15:00Z"
}
```

## Data Integrity

### Constraints Enforced
- ✅ Primary key uniqueness (id)
- ✅ Foreign key referential integrity (user_id → user.id)
- ✅ NOT NULL constraints (user_id, title, completed, timestamps)
- ✅ Max length constraint (title ≤ 500 chars)
- ✅ Boolean type constraint (completed = true/false)
- ✅ CASCADE delete (orphan prevention)

### Constraints NOT Enforced (Application Level)
- Title cannot be empty string (validated by FastAPI/Pydantic)
- User can only access their own tasks (enforced by query filtering)
- Timestamps in UTC (enforced by application code)

## Performance Considerations

### Query Patterns
- **Most Common**: `SELECT * FROM tasks WHERE user_id = ?` (indexed)
- **Single Task**: `SELECT * FROM tasks WHERE id = ? AND user_id = ?` (indexed on id, user_id)
- **Filtered**: `SELECT * FROM tasks WHERE user_id = ? AND completed = ?` (both indexed)

### Expected Volume
- **Users**: ~100 concurrent users (Phase-2)
- **Tasks per User**: <1000 tasks (no pagination needed)
- **Total Tasks**: ~100,000 tasks maximum
- **Query Performance**: <200ms for list queries (with indexes)

### Optimization Strategy
- Indexes on user_id and completed ensure fast queries
- No pagination needed for Phase-2 (small task lists)
- Future optimization: composite index (user_id, completed) if needed

## Security Considerations

### User Isolation
- **Enforcement**: Query-level filtering (WHERE user_id = ?)
- **Source**: user_id from verified JWT token only
- **Protection**: Users cannot access other users' tasks (404 returned)
- **Validation**: Backend never trusts client-provided user_id

### Data Protection
- **Sensitive Data**: None (tasks are user-specific, not sensitive)
- **Encryption**: Database-level encryption (Neon Serverless)
- **Access Control**: JWT authentication required for all operations

## Migration Strategy

### Initial Migration
```sql
-- File: backend/migrations/002_create_tasks_table.sql
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
```

### Rollback Strategy
```sql
-- Rollback: Drop tasks table
DROP TABLE IF EXISTS tasks CASCADE;
```

## References

- [PostgreSQL Data Types](https://www.postgresql.org/docs/current/datatype.html)
- [PostgreSQL Foreign Keys](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-FK)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- Feature Specification: specs/003-tasks-crud-api/spec.md
