# Tool Contract: complete_task

**Feature**: 001-mcp-task-server
**Tool Name**: `complete_task`
**Purpose**: Mark a task as completed
**Priority**: P3 (Core workflow)

## Overview

The `complete_task` tool updates a task's completion status to true. It enforces user isolation by only allowing users to complete their own tasks.

## Function Signature

```python
@mcp.tool()
async def complete_task(
    user_id: str,
    task_id: int
) -> dict:
    """
    Mark a task as completed.

    Args:
        user_id: The authenticated user's identifier
        task_id: The task to mark as complete

    Returns:
        Dictionary with task_id, status, and title
    """
```

## Input Parameters

### user_id (Required)
- **Type**: `str`
- **Required**: Yes
- **Description**: The authenticated user's identifier (from JWT)
- **Validation**: Must not be empty
- **Example**: `"user123"`, `"ziakhan"`

### task_id (Required)
- **Type**: `int`
- **Required**: Yes
- **Description**: The unique identifier of the task to complete
- **Validation**: Must be a valid integer
- **Example**: `5`, `123`

## Output Format

### Success Response

```json
{
  "task_id": 3,
  "status": "completed",
  "title": "Call mom"
}
```

**Fields**:
- `task_id` (integer): The task identifier
- `status` (string): Always `"completed"` for successful operations
- `title` (string): The task title

### Error Responses

#### Missing user_id
```json
{
  "error": "user_id is required"
}
```

#### Missing task_id
```json
{
  "error": "task_id is required"
}
```

#### Task not found or unauthorized
```json
{
  "error": "task not found"
}
```

**Note**: Returns same error whether task doesn't exist or belongs to another user (prevents information leakage)

#### Database error
```json
{
  "error": "service unavailable"
}
```

## Usage Examples

### Example 1: Complete a pending task
**Input**:
```json
{
  "user_id": "ziakhan",
  "task_id": 3
}
```

**Output**:
```json
{
  "task_id": 3,
  "status": "completed",
  "title": "Call mom"
}
```

### Example 2: Complete already completed task (idempotent)
**Input**:
```json
{
  "user_id": "user123",
  "task_id": 5
}
```

**Output**:
```json
{
  "task_id": 5,
  "status": "completed",
  "title": "Buy groceries"
}
```

**Note**: Operation is idempotent - completing an already completed task succeeds

### Example 3: Error - task doesn't exist
**Input**:
```json
{
  "user_id": "user123",
  "task_id": 9999
}
```

**Output**:
```json
{
  "error": "task not found"
}
```

### Example 4: Error - task belongs to another user
**Input**:
```json
{
  "user_id": "user123",
  "task_id": 10
}
```

**Output** (assuming task 10 belongs to user456):
```json
{
  "error": "task not found"
}
```

**Note**: Same error as non-existent task (security)

## Implementation Details

### Database Operations
1. Validate inputs (user_id, task_id)
2. Fetch task with user isolation:
   ```sql
   SELECT * FROM tasks WHERE id = $1 AND user_id = $2
   ```
3. If task not found → return error
4. Set `completed = TRUE`
5. Set `updated_at = NOW()`
6. Commit transaction
7. Return response

### SQL Equivalent
```sql
UPDATE tasks
SET completed = TRUE, updated_at = NOW()
WHERE id = $1 AND user_id = $2
RETURNING id, title;
```

### Performance
- **Expected Time**: <50ms
- **Database Operations**: 1 SELECT + 1 UPDATE
- **Indexes Used**: Primary key (id), `idx_tasks_user_id`

## Edge Cases

### Already completed task
**Input**: `{"user_id": "user123", "task_id": 5}` (task 5 already completed)
**Behavior**: Idempotent - succeeds without error
**Output**: `{"task_id": 5, "status": "completed", "title": "Task title"}`

### Task belongs to another user
**Input**: `{"user_id": "user123", "task_id": 10}` (task 10 belongs to user456)
**Behavior**: Return "task not found" (don't reveal ownership)
**Output**: `{"error": "task not found"}`

### Invalid task_id (non-integer)
**Input**: `{"user_id": "user123", "task_id": "abc"}`
**Behavior**: Type validation fails (Pydantic)
**Output**: Validation error from MCP SDK

### Negative task_id
**Input**: `{"user_id": "user123", "task_id": -1}`
**Behavior**: Query returns no results
**Output**: `{"error": "task not found"}`

## Security Considerations

### User Isolation
- **CRITICAL**: Query MUST filter by both task_id AND user_id
- User A cannot complete User B's tasks
- Return generic "task not found" for unauthorized access

### Idempotency
- Safe to call multiple times
- No side effects if task already completed
- Prevents race conditions in concurrent scenarios

### Information Leakage Prevention
```python
# ✅ CORRECT - Generic error
if not task:
    return {"error": "task not found"}

# ❌ WRONG - Reveals task exists
if task.user_id != user_id:
    return {"error": "unauthorized"}
```

## Testing Checklist

- [ ] Complete a pending task → success
- [ ] Complete an already completed task → success (idempotent)
- [ ] Complete task without user_id → error
- [ ] Complete task without task_id → error
- [ ] Complete non-existent task → error "task not found"
- [ ] Complete another user's task → error "task not found"
- [ ] Verify completed field set to true in database
- [ ] Verify updated_at timestamp updated
- [ ] Test concurrent completion of same task
- [ ] Verify performance <50ms for 95th percentile

## Related Tools

- **add_task**: Create tasks to be completed
- **list_tasks**: View completed vs pending tasks
- **update_task**: Modify task details (doesn't affect completion)
- **delete_task**: Remove completed tasks

## Acceptance Criteria

From spec User Story 3:

1. ✅ Given user "user123" has a pending task with task_id 5, When the agent invokes `complete_task` with task_id 5, Then the task's completed field is set to true and status "completed" is returned

2. ✅ Given user "user123" attempts to complete task_id 10 belonging to user "user456", When the agent invokes `complete_task`, Then an error is returned indicating task not found (user isolation enforced)

3. ✅ Given a task_id that doesn't exist, When the agent invokes `complete_task`, Then an error is returned indicating task not found

---

**Contract Status**: ✅ Complete
**Implementation File**: `backend/app/mcp/tools/complete_task.py`
