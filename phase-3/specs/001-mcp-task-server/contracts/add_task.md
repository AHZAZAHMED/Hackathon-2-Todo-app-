# Tool Contract: add_task

**Feature**: 001-mcp-task-server
**Tool Name**: `add_task`
**Purpose**: Create a new task for a user
**Priority**: P1 (MVP - foundational capability)

## Overview

The `add_task` tool creates a new task in the database for the specified user. It is the foundational tool that enables all other task management operations.

## Function Signature

```python
@mcp.tool()
async def add_task(
    user_id: str,
    title: str,
    description: str = None
) -> dict:
    """
    Create a new task for a user.

    Args:
        user_id: The authenticated user's identifier
        title: Task title (max 500 characters)
        description: Optional task description

    Returns:
        Dictionary with task_id, status, and title
    """
```

## Input Parameters

### user_id (Required)
- **Type**: `str`
- **Required**: Yes
- **Description**: The authenticated user's identifier (from JWT)
- **Validation**:
  - Must not be empty
  - Assumed to be authenticated upstream
- **Example**: `"user123"`, `"clx1234567890"`

### title (Required)
- **Type**: `str`
- **Required**: Yes
- **Description**: Task title/name
- **Validation**:
  - Must not be empty after trimming whitespace
  - Maximum 500 characters
  - Leading/trailing whitespace will be trimmed
- **Example**: `"Buy groceries"`, `"Call mom"`

### description (Optional)
- **Type**: `str`
- **Required**: No
- **Default**: `None`
- **Description**: Detailed task information
- **Validation**: No length restrictions
- **Example**: `"Milk, eggs, bread"`, `None`

## Output Format

### Success Response

```json
{
  "task_id": 123,
  "status": "created",
  "title": "Buy groceries"
}
```

**Fields**:
- `task_id` (integer): The unique identifier of the created task
- `status` (string): Always `"created"` for successful operations
- `title` (string): The task title (as stored in database)

### Error Responses

#### Missing user_id
```json
{
  "error": "user_id is required"
}
```

#### Empty title
```json
{
  "error": "title cannot be empty"
}
```

#### Title too long
```json
{
  "error": "title exceeds maximum length of 500 characters"
}
```

#### Database error
```json
{
  "error": "service unavailable"
}
```

## Usage Examples

### Example 1: Create task with description
**Input**:
```json
{
  "user_id": "ziakhan",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Output**:
```json
{
  "task_id": 5,
  "status": "created",
  "title": "Buy groceries"
}
```

### Example 2: Create task without description
**Input**:
```json
{
  "user_id": "user123",
  "title": "Call mom"
}
```

**Output**:
```json
{
  "task_id": 6,
  "status": "created",
  "title": "Call mom"
}
```

### Example 3: Error - empty title
**Input**:
```json
{
  "user_id": "user123",
  "title": "   "
}
```

**Output**:
```json
{
  "error": "title cannot be empty"
}
```

### Example 4: Error - title too long
**Input**:
```json
{
  "user_id": "user123",
  "title": "A".repeat(501)
}
```

**Output**:
```json
{
  "error": "title exceeds maximum length of 500 characters"
}
```

## Implementation Details

### Database Operations
1. Validate inputs (user_id, title)
2. Trim whitespace from title
3. Create Task instance with:
   - `user_id` from parameter
   - `title` from parameter (trimmed)
   - `description` from parameter (or None)
   - `completed` = False (default)
   - `created_at` = current timestamp (auto)
   - `updated_at` = current timestamp (auto)
4. Insert into database
5. Commit transaction
6. Refresh to get generated `id`
7. Return response

### SQL Equivalent
```sql
INSERT INTO tasks (user_id, title, description, completed, created_at, updated_at)
VALUES ($1, $2, $3, FALSE, NOW(), NOW())
RETURNING id, title;
```

### Performance
- **Expected Time**: <50ms
- **Database Operations**: 1 INSERT
- **Indexes Used**: None (insert operation)

## Edge Cases

### Whitespace-only title
**Input**: `{"user_id": "user123", "title": "   \n\t  "}`
**Behavior**: After trimming, title is empty → return error
**Output**: `{"error": "title cannot be empty"}`

### Very long description
**Input**: `{"user_id": "user123", "title": "Task", "description": "A".repeat(100000)}`
**Behavior**: Accepted (TEXT field has no practical limit)
**Output**: `{"task_id": 7, "status": "created", "title": "Task"}`

### Special characters in title
**Input**: `{"user_id": "user123", "title": "Buy 🥛 & 🥚"}`
**Behavior**: Accepted (UTF-8 supported)
**Output**: `{"task_id": 8, "status": "created", "title": "Buy 🥛 & 🥚"}`

### Null description
**Input**: `{"user_id": "user123", "title": "Task", "description": null}`
**Behavior**: Accepted (description is optional)
**Output**: `{"task_id": 9, "status": "created", "title": "Task"}`

## Security Considerations

### User Isolation
- Task is associated with provided `user_id`
- No cross-user validation needed (user_id from JWT is trusted)
- Each user can only see/modify their own tasks

### Input Sanitization
- Title is trimmed of whitespace
- No SQL injection risk (SQLModel handles escaping)
- No XSS risk (server-side only, no HTML rendering)

### Error Messages
- Don't expose internal database errors
- Return generic "service unavailable" for unexpected errors
- Log detailed errors server-side for debugging

## Testing Checklist

- [ ] Create task with valid title and description
- [ ] Create task with title only (no description)
- [ ] Create task with empty title (after trimming) → error
- [ ] Create task with title exceeding 500 characters → error
- [ ] Create task without user_id → error
- [ ] Create task with special characters in title
- [ ] Create task with very long description (>10KB)
- [ ] Verify task appears in database with correct user_id
- [ ] Verify completed defaults to false
- [ ] Verify timestamps are set correctly
- [ ] Test concurrent task creation (100 simultaneous)
- [ ] Verify performance <50ms for 95th percentile

## Related Tools

- **list_tasks**: Retrieve created tasks
- **update_task**: Modify task title or description
- **complete_task**: Mark task as done
- **delete_task**: Remove task

## Acceptance Criteria

From spec User Story 1:

1. ✅ Given an authenticated user with user_id "user123", When the agent invokes `add_task` with title "Buy groceries" and description "Milk, eggs, bread", Then a new task is created in the database with task_id returned, status "created", and all fields populated correctly

2. ✅ Given an authenticated user, When the agent invokes `add_task` with only a title (no description), Then a task is created with description as null and completed defaulting to false

3. ✅ Given an authenticated user, When the agent invokes `add_task` with an empty title, Then the tool returns an error indicating title is required

---

**Contract Status**: ✅ Complete
**Implementation File**: `backend/app/mcp/tools/add_task.py`
