# Tool Contract: list_tasks

**Feature**: 001-mcp-task-server
**Tool Name**: `list_tasks`
**Purpose**: Retrieve tasks for a user, optionally filtered by completion status
**Priority**: P2 (Essential for viewing tasks)

## Overview

The `list_tasks` tool retrieves all tasks belonging to a specific user, with optional filtering by completion status. It enforces user isolation by only returning tasks that belong to the authenticated user.

## Function Signature

```python
@mcp.tool()
async def list_tasks(
    user_id: str,
    status: str = "all"
) -> list[dict]:
    """
    Retrieve tasks for a user.

    Args:
        user_id: The authenticated user's identifier
        status: Filter by status - "all", "pending", or "completed"

    Returns:
        Array of task objects
    """
```

## Input Parameters

### user_id (Required)
- **Type**: `str`
- **Required**: Yes
- **Description**: The authenticated user's identifier (from JWT)
- **Validation**: Must not be empty
- **Example**: `"user123"`, `"ziakhan"`

### status (Optional)
- **Type**: `str`
- **Required**: No
- **Default**: `"all"`
- **Description**: Filter tasks by completion status
- **Valid Values**:
  - `"all"` - Return all tasks (pending and completed)
  - `"pending"` - Return only incomplete tasks (completed=false)
  - `"completed"` - Return only completed tasks (completed=true)
- **Validation**: Must be one of the three valid values
- **Example**: `"pending"`, `"completed"`, `"all"`

## Output Format

### Success Response

```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-02-09T10:00:00Z",
    "updated_at": "2026-02-09T10:00:00Z"
  },
  {
    "id": 2,
    "title": "Call mom",
    "description": null,
    "completed": false,
    "created_at": "2026-02-09T11:00:00Z",
    "updated_at": "2026-02-09T11:00:00Z"
  }
]
```

**Array of Task Objects**:
- `id` (integer): Task unique identifier
- `title` (string): Task title
- `description` (string | null): Task description (null if not provided)
- `completed` (boolean): Completion status
- `created_at` (string): ISO 8601 timestamp of creation
- `updated_at` (string): ISO 8601 timestamp of last update

**Empty Result**:
```json
[]
```

### Error Responses

#### Missing user_id
```json
{
  "error": "user_id is required"
}
```

#### Invalid status value
```json
{
  "error": "status must be 'all', 'pending', or 'completed'"
}
```

#### Database error
```json
{
  "error": "service unavailable"
}
```

## Usage Examples

### Example 1: List all tasks
**Input**:
```json
{
  "user_id": "ziakhan",
  "status": "all"
}
```

**Output**:
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-02-09T10:00:00Z",
    "updated_at": "2026-02-09T10:00:00Z"
  },
  {
    "id": 3,
    "title": "Finish report",
    "description": null,
    "completed": true,
    "created_at": "2026-02-09T09:00:00Z",
    "updated_at": "2026-02-09T12:00:00Z"
  }
]
```

### Example 2: List pending tasks only
**Input**:
```json
{
  "user_id": "user123",
  "status": "pending"
}
```

**Output**:
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-02-09T10:00:00Z",
    "updated_at": "2026-02-09T10:00:00Z"
  }
]
```

### Example 3: List completed tasks only
**Input**:
```json
{
  "user_id": "user123",
  "status": "completed"
}
```

**Output**:
```json
[
  {
    "id": 3,
    "title": "Finish report",
    "description": null,
    "completed": true,
    "created_at": "2026-02-09T09:00:00Z",
    "updated_at": "2026-02-09T12:00:00Z"
  }
]
```

### Example 4: No tasks found
**Input**:
```json
{
  "user_id": "newuser",
  "status": "all"
}
```

**Output**:
```json
[]
```

### Example 5: Error - invalid status
**Input**:
```json
{
  "user_id": "user123",
  "status": "active"
}
```

**Output**:
```json
{
  "error": "status must be 'all', 'pending', or 'completed'"
}
```

## Implementation Details

### Database Operations
1. Validate inputs (user_id, status)
2. Build query with user_id filter
3. Apply status filter if not "all":
   - "pending": `WHERE completed = FALSE`
   - "completed": `WHERE completed = TRUE`
4. Order by created_at descending (newest first)
5. Limit to 1000 results (performance cap)
6. Execute query
7. Convert results to dictionaries
8. Return array

### SQL Equivalent

**All tasks**:
```sql
SELECT id, title, description, completed, created_at, updated_at
FROM tasks
WHERE user_id = $1
ORDER BY created_at DESC
LIMIT 1000;
```

**Pending tasks**:
```sql
SELECT id, title, description, completed, created_at, updated_at
FROM tasks
WHERE user_id = $1 AND completed = FALSE
ORDER BY created_at DESC
LIMIT 1000;
```

**Completed tasks**:
```sql
SELECT id, title, description, completed, created_at, updated_at
FROM tasks
WHERE user_id = $1 AND completed = TRUE
ORDER BY created_at DESC
LIMIT 1000;
```

### Performance
- **Expected Time**: <100ms for up to 1000 tasks
- **Database Operations**: 1 SELECT
- **Indexes Used**: `idx_tasks_user_id`, `idx_tasks_completed`

## Edge Cases

### User with no tasks
**Input**: `{"user_id": "newuser", "status": "all"}`
**Behavior**: Return empty array
**Output**: `[]`

### User with 1000+ tasks
**Input**: `{"user_id": "poweruser", "status": "all"}`
**Behavior**: Return first 1000 tasks (newest first)
**Output**: Array with 1000 task objects

### Default status parameter
**Input**: `{"user_id": "user123"}`
**Behavior**: Defaults to "all"
**Output**: All tasks for user123

### Case sensitivity of status
**Input**: `{"user_id": "user123", "status": "PENDING"}`
**Behavior**: Case-sensitive validation fails
**Output**: `{"error": "status must be 'all', 'pending', or 'completed'"}`

## Security Considerations

### User Isolation
- **CRITICAL**: Query MUST filter by user_id
- User A cannot see User B's tasks
- Empty result if user has no tasks (not an error)

### Information Leakage Prevention
- Don't reveal if other users exist
- Don't reveal total task count across all users
- Only return tasks belonging to authenticated user

### Performance Protection
- Limit results to 1000 tasks
- Use indexed queries for fast retrieval
- Prevent unbounded result sets

## Testing Checklist

- [ ] List all tasks for user with multiple tasks
- [ ] List pending tasks only
- [ ] List completed tasks only
- [ ] List tasks for user with no tasks → empty array
- [ ] List tasks without user_id → error
- [ ] List tasks with invalid status value → error
- [ ] Verify user isolation (User A doesn't see User B's tasks)
- [ ] Verify ordering (newest first)
- [ ] Verify limit (max 1000 results)
- [ ] Test with user having 1000+ tasks
- [ ] Verify performance <100ms for 1000 tasks
- [ ] Test concurrent list operations (100 simultaneous)

## Related Tools

- **add_task**: Create tasks that will appear in list
- **update_task**: Modified tasks reflect in list
- **complete_task**: Changes task status (affects filtering)
- **delete_task**: Removed tasks disappear from list

## Acceptance Criteria

From spec User Story 2:

1. ✅ Given user "user123" has 3 pending tasks and 2 completed tasks, When the agent invokes `list_tasks` with status "pending", Then only the 3 pending tasks are returned

2. ✅ Given user "user123" has tasks and user "user456" has tasks, When the agent invokes `list_tasks` for "user123", Then only user123's tasks are returned (user isolation enforced)

3. ✅ Given a user with no tasks, When the agent invokes `list_tasks`, Then an empty array is returned

---

**Contract Status**: ✅ Complete
**Implementation File**: `backend/app/mcp/tools/list_tasks.py`
