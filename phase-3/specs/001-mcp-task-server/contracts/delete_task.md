# Tool Contract: delete_task

**Feature**: 001-mcp-task-server
**Tool Name**: `delete_task`
**Purpose**: Remove a task from the database
**Priority**: P5 (Useful for cleanup, least critical)

## Overview

The `delete_task` tool permanently removes a task from the database. It enforces user isolation by only allowing users to delete their own tasks. This is a hard delete (not a soft delete).

## Function Signature

```python
@mcp.tool()
async def delete_task(
    user_id: str,
    task_id: int
) -> dict:
    """
    Remove a task from the database.

    Args:
        user_id: The authenticated user's identifier
        task_id: The task to delete

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
- **Description**: The unique identifier of the task to delete
- **Validation**: Must be a valid integer
- **Example**: `2`, `123`

## Output Format

### Success Response

```json
{
  "task_id": 2,
  "status": "deleted",
  "title": "Old task"
}
```

**Fields**:
- `task_id` (integer): The deleted task identifier
- `status` (string): Always `"deleted"` for successful operations
- `title` (string): The title of the deleted task (captured before deletion)

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

### Example 1: Delete a task
**Input**:
```json
{
  "user_id": "ziakhan",
  "task_id": 2
}
```

**Output**:
```json
{
  "task_id": 2,
  "status": "deleted",
  "title": "Old task"
}
```

### Example 2: Error - task doesn't exist
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

### Example 3: Error - task belongs to another user
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

### Example 4: Delete already deleted task
**Input**:
```json
{
  "user_id": "user123",
  "task_id": 5
}
```

**Output** (if task 5 was already deleted):
```json
{
  "error": "task not found"
}
```

**Note**: Not idempotent - second delete returns error

## Implementation Details

### Database Operations
1. Validate inputs (user_id, task_id)
2. Fetch task with user isolation:
   ```sql
   SELECT * FROM tasks WHERE id = $1 AND user_id = $2
   ```
3. If task not found → return error
4. Capture task title for response
5. Delete task from database
6. Commit transaction
7. Return response with captured title

### SQL Equivalent
```sql
DELETE FROM tasks
WHERE id = $1 AND user_id = $2
RETURNING id, title;
```

### Performance
- **Expected Time**: <50ms
- **Database Operations**: 1 SELECT + 1 DELETE (or combined DELETE...RETURNING)
- **Indexes Used**: Primary key (id), `idx_tasks_user_id`

## Edge Cases

### Delete non-existent task
**Input**: `{"user_id": "user123", "task_id": 9999}`
**Behavior**: Return "task not found"
**Output**: `{"error": "task not found"}`

### Delete another user's task
**Input**: `{"user_id": "user123", "task_id": 10}` (task 10 belongs to user456)
**Behavior**: Return "task not found" (don't reveal ownership)
**Output**: `{"error": "task not found"}`

### Delete already deleted task
**Input**: `{"user_id": "user123", "task_id": 5}` (task 5 was deleted previously)
**Behavior**: Return "task not found" (not idempotent)
**Output**: `{"error": "task not found"}`

### Delete completed task
**Input**: `{"user_id": "user123", "task_id": 3}` (task 3 is completed)
**Behavior**: Delete succeeds (completion status doesn't matter)
**Output**: `{"task_id": 3, "status": "deleted", "title": "Completed task"}`

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
- User A cannot delete User B's tasks
- Return generic "task not found" for unauthorized access

### Hard Delete
- Task is permanently removed from database
- No soft delete or trash functionality
- Cannot be recovered after deletion
- Consider implications for audit trails

### Information Leakage Prevention
```python
# ✅ CORRECT - Generic error
if not task:
    return {"error": "task not found"}

# ❌ WRONG - Reveals task exists
if task.user_id != user_id:
    return {"error": "unauthorized - task belongs to another user"}
```

### Cascade Behavior
- No cascade needed (tasks have no dependent records)
- If future features add task dependencies, consider cascade implications

## Testing Checklist

- [ ] Delete an existing task → success
- [ ] Delete task without user_id → error
- [ ] Delete task without task_id → error
- [ ] Delete non-existent task → error "task not found"
- [ ] Delete another user's task → error "task not found"
- [ ] Delete already deleted task → error "task not found"
- [ ] Delete completed task → success
- [ ] Verify task removed from database
- [ ] Verify task no longer appears in list_tasks
- [ ] Test concurrent deletion of same task
- [ ] Verify performance <50ms for 95th percentile

## Related Tools

- **add_task**: Create tasks to be deleted
- **list_tasks**: Deleted tasks no longer appear
- **update_task**: Cannot update deleted tasks
- **complete_task**: Cannot complete deleted tasks

## Acceptance Criteria

From spec User Story 5:

1. ✅ Given user "user123" has task_id 2, When the agent invokes `delete_task` with task_id 2, Then the task is removed from the database and status "deleted" is returned

2. ✅ Given user "user123" attempts to delete task_id 10 belonging to user "user456", When the agent invokes `delete_task`, Then an error is returned (user isolation enforced)

3. ✅ Given a task_id that doesn't exist, When the agent invokes `delete_task`, Then an error is returned indicating task not found

## Idempotency Considerations

**Not Idempotent**: Unlike `complete_task`, `delete_task` is NOT idempotent:
- First call: Returns success with task details
- Second call: Returns error "task not found"

**Rationale**:
- Task no longer exists after deletion
- Cannot return success for non-existent task
- Agent should track deletion state if idempotency needed

**Alternative Design** (not implemented):
- Could make idempotent by returning success for already-deleted tasks
- Would require tracking deleted task IDs or accepting "not found" as success
- Current design is simpler and more explicit

## Comparison with Soft Delete

**Hard Delete** (implemented):
- Task permanently removed from database
- Cannot be recovered
- Simpler implementation
- Better for privacy (data truly deleted)

**Soft Delete** (not implemented):
- Task marked as deleted but remains in database
- Can be recovered
- Requires additional `deleted` field
- Complicates queries (must filter out deleted tasks)
- Better for audit trails

**Decision**: Hard delete chosen for MVP simplicity. Soft delete can be added later if needed.

---

**Contract Status**: ✅ Complete
**Implementation File**: `backend/app/mcp/tools/delete_task.py`
