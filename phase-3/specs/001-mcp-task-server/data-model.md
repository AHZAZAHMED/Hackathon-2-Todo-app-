# Data Model: MCP Task Server

**Feature**: 001-mcp-task-server
**Date**: 2026-02-09
**Status**: Complete

## Overview

This document defines the data model for the MCP Task Server. The server operates on the existing `tasks` table from Phase-2, with no new tables required. All MCP tools interact with the Task entity through SQLModel ORM.

## Task Entity

### Database Table: `tasks`

**Table Name**: `tasks` (existing from Phase-2)

**Schema**:
```sql
CREATE TABLE tasks (
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

### SQLModel Definition

**File**: `backend/app/models/task.py` (existing)

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """
    Task model representing a todo item.

    Attributes:
        id: Unique task identifier (auto-generated)
        user_id: Owner of the task (foreign key to user table)
        title: Task title (max 500 characters)
        description: Optional task description
        completed: Task completion status (default: False)
        created_at: Task creation timestamp
        updated_at: Last modification timestamp
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=500)
    description: Optional[str] = None
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

## Field Specifications

### id (Primary Key)
- **Type**: Integer (SERIAL in PostgreSQL)
- **Constraints**: Primary key, auto-increment
- **Purpose**: Unique identifier for each task
- **Generated**: Automatically by database on insert
- **Used By**: All tools for task identification

### user_id (Foreign Key)
- **Type**: String (TEXT)
- **Constraints**: NOT NULL, foreign key to `user.id`, indexed
- **Purpose**: Associates task with owner, enforces user isolation
- **Validation**: Must be provided by all MCP tools
- **Cascade**: ON DELETE CASCADE (tasks deleted when user deleted)
- **Query Pattern**: All queries MUST filter by user_id

### title
- **Type**: String (VARCHAR 500)
- **Constraints**: NOT NULL, max 500 characters
- **Purpose**: Task name/summary
- **Validation**:
  - Required (cannot be empty after trimming whitespace)
  - Max length 500 characters
  - Trimmed of leading/trailing whitespace
- **Used By**: add_task (required), update_task (optional)

### description
- **Type**: String (TEXT)
- **Constraints**: Nullable, no length limit
- **Purpose**: Detailed task information
- **Validation**: Optional, no length restrictions
- **Used By**: add_task (optional), update_task (optional)

### completed
- **Type**: Boolean
- **Constraints**: NOT NULL, default FALSE, indexed
- **Purpose**: Task completion status
- **Values**:
  - `false` - Task is pending
  - `true` - Task is completed
- **Used By**:
  - list_tasks (filter by status)
  - complete_task (toggles to true)
- **Query Pattern**: Indexed for efficient filtering

### created_at
- **Type**: Timestamp
- **Constraints**: NOT NULL, default NOW()
- **Purpose**: Track when task was created
- **Generated**: Automatically on insert
- **Immutable**: Never updated after creation
- **Used By**: list_tasks (for ordering)

### updated_at
- **Type**: Timestamp
- **Constraints**: NOT NULL, default NOW()
- **Purpose**: Track last modification time
- **Updated**: On every update operation
- **Used By**: Audit trail, conflict detection
- **Pattern**: Set to current timestamp on update

## Relationships

### Task → User (Many-to-One)
- **Foreign Key**: `tasks.user_id` → `user.id`
- **Cascade**: ON DELETE CASCADE
- **Purpose**: User isolation and ownership
- **Enforcement**: All queries filter by user_id

**Query Pattern**:
```python
# Always filter by user_id
statement = select(Task).where(Task.user_id == user_id)
```

## Indexes

### Primary Index
- **Column**: `id`
- **Type**: Primary key (unique, clustered)
- **Purpose**: Fast lookup by task_id

### User Isolation Index
- **Name**: `idx_tasks_user_id`
- **Column**: `user_id`
- **Type**: B-tree
- **Purpose**: Fast filtering by user (all queries use this)
- **Performance**: Enables <200ms query times

### Status Filter Index
- **Name**: `idx_tasks_completed`
- **Column**: `completed`
- **Type**: B-tree
- **Purpose**: Fast filtering by completion status
- **Used By**: list_tasks with status filter

### Composite Index (Recommended for Optimization)
- **Name**: `idx_tasks_user_completed` (not yet created)
- **Columns**: `(user_id, completed)`
- **Purpose**: Optimize list_tasks queries with status filter
- **Query**: `WHERE user_id = ? AND completed = ?`

## Query Patterns

### Pattern 1: Create Task
```python
async with async_session_maker() as session:
    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        completed=False  # Default
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)  # Get generated id
```

### Pattern 2: List Tasks (All)
```python
statement = (
    select(Task)
    .where(Task.user_id == user_id)
    .order_by(Task.created_at.desc())
)
result = await session.execute(statement)
tasks = result.scalars().all()
```

### Pattern 3: List Tasks (Filtered by Status)
```python
statement = (
    select(Task)
    .where(Task.user_id == user_id)
    .where(Task.completed == (status == "completed"))
    .order_by(Task.created_at.desc())
)
```

### Pattern 4: Get Single Task (with User Isolation)
```python
statement = select(Task).where(
    Task.id == task_id,
    Task.user_id == user_id  # CRITICAL: User isolation
)
task = (await session.execute(statement)).scalar_one_or_none()

if not task:
    return {"error": "task not found"}  # Don't reveal if exists for other user
```

### Pattern 5: Update Task
```python
# Fetch with user isolation
task = await get_task_with_isolation(session, task_id, user_id)

if not task:
    return {"error": "task not found"}

# Update fields
if title is not None:
    task.title = title
if description is not None:
    task.description = description

task.updated_at = datetime.utcnow()  # Update timestamp

await session.commit()
await session.refresh(task)
```

### Pattern 6: Delete Task
```python
# Fetch with user isolation
task = await get_task_with_isolation(session, task_id, user_id)

if not task:
    return {"error": "task not found"}

await session.delete(task)
await session.commit()
```

## Data Validation Rules

### Title Validation
1. **Required**: Cannot be None or empty after trimming
2. **Max Length**: 500 characters
3. **Trimming**: Leading/trailing whitespace removed
4. **Error**: Return `{"error": "title cannot be empty"}` or `{"error": "title exceeds maximum length of 500 characters"}`

### Description Validation
1. **Optional**: Can be None
2. **No Length Limit**: TEXT field supports large content
3. **Trimming**: Not required (preserve formatting)

### User ID Validation
1. **Required**: Must be provided for all operations
2. **Format**: String (matches Better Auth user ID format)
3. **Validation**: Assumed to be authenticated upstream
4. **Error**: Return `{"error": "user_id is required"}`

### Task ID Validation
1. **Required**: For update, complete, delete operations
2. **Type**: Integer
3. **Existence**: Verified via database query
4. **Ownership**: Verified via user_id filter
5. **Error**: Return `{"error": "task not found"}`

## User Isolation Enforcement

### Critical Rule: ALWAYS Filter by user_id

**Every query MUST include user_id filter**:
```python
# ✅ CORRECT
statement = select(Task).where(
    Task.id == task_id,
    Task.user_id == user_id  # User isolation
)

# ❌ WRONG - Security vulnerability!
statement = select(Task).where(Task.id == task_id)
```

### Error Handling for Unauthorized Access

**Don't reveal if task exists for another user**:
```python
# ✅ CORRECT - Generic error
if not task:
    return {"error": "task not found"}

# ❌ WRONG - Information leakage
if task.user_id != user_id:
    return {"error": "unauthorized - task belongs to another user"}
```

## Performance Considerations

### Query Optimization
- **Use Indexes**: All queries leverage `idx_tasks_user_id`
- **Limit Results**: Cap list_tasks at 1000 results
- **Order By**: Use indexed columns when possible
- **Connection Pooling**: Reuse database connections (pool_size=10)

### Expected Performance
- **Single Task Operations**: <50ms (get, update, delete, complete)
- **List Operations**: <100ms for up to 1000 tasks
- **Create Operations**: <50ms
- **Target**: 95th percentile <200ms (per spec SC-003)

### Scalability
- **Concurrent Operations**: Support 100 concurrent tool calls (per spec SC-004)
- **Connection Pool**: 10 base + 20 overflow connections
- **Index Usage**: Ensures linear scaling with user count

## Data Lifecycle

### Creation
1. MCP tool receives parameters (user_id, title, description)
2. Validate inputs
3. Create Task instance with defaults (completed=False)
4. Insert into database
5. Commit transaction
6. Refresh to get generated id and timestamps
7. Return task_id, status, title

### Reading
1. MCP tool receives user_id and optional filters
2. Build query with user_id filter
3. Apply status filter if provided
4. Order by created_at descending
5. Execute query
6. Return array of task dictionaries

### Updating
1. MCP tool receives user_id, task_id, and fields to update
2. Fetch task with user isolation
3. Verify task exists and belongs to user
4. Update specified fields
5. Set updated_at to current timestamp
6. Commit transaction
7. Return task_id, status, title

### Deletion
1. MCP tool receives user_id and task_id
2. Fetch task with user isolation
3. Verify task exists and belongs to user
4. Delete task from database
5. Commit transaction
6. Return task_id, status, title

## Migration Notes

**No Migration Required**: The tasks table already exists from Phase-2 with the correct schema. MCP tools use the existing table without modifications.

**Existing Migration**: `backend/migrations/002_create_tasks_table.sql`

**Verification**:
```sql
-- Verify table exists
SELECT * FROM information_schema.tables WHERE table_name = 'tasks';

-- Verify indexes exist
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'tasks';

-- Verify foreign key constraint
SELECT conname, conrelid::regclass, confrelid::regclass
FROM pg_constraint
WHERE conname LIKE '%tasks%';
```

## Summary

- **Entity**: Task (existing from Phase-2)
- **Table**: `tasks` (no changes required)
- **Fields**: 7 fields (id, user_id, title, description, completed, created_at, updated_at)
- **Indexes**: 2 existing (user_id, completed)
- **Relationships**: Many-to-One with User
- **User Isolation**: Enforced via user_id filter on all queries
- **Performance**: Optimized for <200ms operations
- **Validation**: Title required (max 500 chars), description optional
- **Lifecycle**: Full CRUD support via 5 MCP tools

---

**Data Model Status**: ✅ Complete - Ready for tool contract specifications
