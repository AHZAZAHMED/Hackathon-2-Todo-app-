# Tool Contract: update_task

**Feature**: 001-mcp-task-server
**Tool Name**: `update_task`
**Purpose**: Modify task title or description
**Priority**: P4 (Valuable but not essential)

## Overview

The `update_task` tool allows modification of a task's title and/or description. It supports partial updates (updating only title or only description) and enforces user isolation.

## Function Signature

```python
@mcp.tool()
async def update_task(
    user_id: str,
    task_id: int,
    title: str = None,
    description: str = None
) -> dict:
    """
    Modify task title or description.

    Args:
        user_id: The authenticated user's identifier
        task_id: The task to update
        title: New task title (optional, max 500 characters)
        description: New task description (optional)

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
- **Description**: The unique identifier of the task to update
- **Validation**: Must be a valid integer
- **Example**: `1`, `123`

### title (Optional)
- **Type**: `str`
- **Required**: No
- **Default**: `None`
- **Description**: New task title
- **Validation**:
  - If provided, must not be empty after trimming
  - Maximum 500 characters
  - Leading/trailing whitespace will be trimmed
- **Example**: `"Buy groceries and fruits"`

### description (Optional)
- **Type**: `str`
- **Required**: No
- **Default**: `None`
- **Description**: New task description
- **Validation**: No length restrictions
- **Example**: `"Milk, eggs, bread, apples, oranges"`

**Note**: At least one of `title` or `description` must be provided

## Output Format

### Success Response

```json
{
  "task_id": 1,
  "status": "updated",
  "title": "Buy groceries and fruits"
}
```

**Fields**:
- `task_id` (integer): The task identifier
- `status` (string): Always `"updated"` for successful operations
- `title` (string): The updated task title (current value after update)

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

#### No fields to update
```json
{
  "error": "at least one of title or description must be provided"
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

#### Task not found or unauthorized
```json
{
  "error": "task not found"
}
```

#### Database error
```json
{
  "error": "service unavailable"
}
```

## Usage Examples

### Example 1: Update title only
**Input**:
```json
{
  "user_id": "ziakhan",
  "task_id": 1,
  "title": "Buy groceries and fruits"
}
```

**Output**:
```json
{
  "task_id": 1,
  "status": "updated",
  "title": "Buy groceries and fruits"
}
```

### Example 2: Update description only
**Input**:
```json
{
  "user_id": "user123",
  "task_id": 2,
  "description": "Updated description with more details"
}
```

**Output**:
```json
{
  "task_id": 2,
  "status": "updated",
  "title": "Original Title"
}
```

### Example 3: Update both title and description
**Input**:
```json
{
  "user_id": "user123",
  "task_id": 3,
  "title": "New Title",
  "description": "New Description"
}
```

**Output**:
```json
{
  "task_id": 3,
  "status": "updated",
  "title": "New Title"
}
```

### Example 4: Error - no fields provided
**Input**:
```json
{
  "user_id": "user123",
  "task_id": 1
}
```

**Output**:
```json
{
  "error": "at least one of title or description must be provided"
}
```

### Example 5: Error - empty title
**Input**:
```json
{
  "user_id": "user123",
  "task_id": 1,
  "title": "   "
}
```

**Output**:
```json
{
  "error": "title cannot be empty"
}
```

### Example 6: Error - unauthorized access
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

## Implementation Details

### Database Operations
1. Validate inputs (user_id, task_id, at least one field)
2. Fetch task with user isolation
3. If task not found → return error
4. Validate new values (title length, empty check)
5. Update specified fields:
   - If title provided: `task.title = title.strip()`
   - If description provided: `task.description = description`
6. Set `updated_at = NOW()`
7. Commit transaction
8. Return response

### SQL Equivalent

**Update title only**:
```sql
UPDATE tasks
SET title = $3, updated_at = NOW()
WHERE id = $1 AND user_id = $2
RETURNING id, title;
```

**Update description only**:
```sql
UPDATE tasks
SET description = $3, updated_at = NOW()
WHERE id = $1 AND user_id = $2
RETURNING id, title;
```

**Update both**:
```sql
UPDATE tasks
SET title = $3, description = $4, updated_at = NOW()
WHERE id = $1 AND user_id = $2
RETURNING id, title;
```

### Performance
- **Expected Time**: <50ms
- **Database Operations**: 1 SELECT + 1 UPDATE
- **Indexes Used**: Primary key (id), `idx_tasks_user_id`

## Edge Cases

### Update with same values
**Input**: `{"user_id": "user123", "task_id": 1, "title": "Current Title"}`
**Behavior**: Update succeeds even if value unchanged
**Output**: `{"task_id": 1, "status": "updated", "title": "Current Title"}`

### Clear description (set to null)
**Input**: `{"user_id": "user123", "task_id": 1, "description": null}`
**Behavior**: Description set to null
**Output**: `{"task_id": 1, "status": "updated", "title": "Task Title"}`

### Update completed task
**Input**: `{"user_id": "user123", "task_id": 5, "title": "New Title"}` (task 5 is completed)
**Behavior**: Update succeeds (doesn't affect completion status)
**Output**: `{"task_id": 5, "status": "updated", "title": "New Title"}`

### Very long description
**Input**: `{"user_id": "user123", "task_id": 1, "description": "A".repeat(100000)}`
**Behavior**: Accepted (TEXT field has no practical limit)
**Output**: `{"task_id": 1, "status": "updated", "title": "Task Title"}`

## Security Considerations

### User Isolation
- **CRITICAL**: Query MUST filter by both task_id AND user_id
- User A cannot update User B's tasks
- Return generic "task not found" for unauthorized access

### Input Validation
- Title trimmed of whitespace
- Title length validated (max 500 chars)
- Empty title rejected
- At least one field required

### Partial Updates
- Only specified fields are updated
- Unspecified fields remain unchanged
- Prevents accidental data loss

## Testing Checklist

- [ ] Update title only
- [ ] Update description only
- [ ] Update both title and description
- [ ] Update with no fields provided → error
- [ ] Update with empty title → error
- [ ] Update with title exceeding 500 chars → error
- [ ] Update non-existent task → error
- [ ] Update another user's task → error
- [ ] Update completed task (should succeed)
- [ ] Verify updated_at timestamp changed
- [ ] Verify unspecified fields unchanged
- [ ] Test concurrent updates to same task
- [ ] Verify performance <50ms for 95th percentile

## Related Tools

- **add_task**: Create tasks to be updated
- **list_tasks**: View updated tasks
- **complete_task**: Mark tasks done (doesn't affect title/description)
- **delete_task**: Remove tasks

## Acceptance Criteria

From spec User Story 4:

1. ✅ Given user "user123" has task_id 1 with title "Buy groceries", When the agent invokes `update_task` with task_id 1 and title "Buy groceries and fruits", Then the task title is updated and status "updated" is returned

2. ✅ Given a task, When the agent invokes `update_task` with only description (no title), Then only the description is updated and title remains unchanged

3. ✅ Given user "user123" attempts to update task_id 10 belonging to user "user456", When the agent invokes `update_task`, Then an error is returned (user isolation enforced)

---

**Contract Status**: ✅ Complete
**Implementation File**: `backend/app/mcp/tools/update_task.py`
