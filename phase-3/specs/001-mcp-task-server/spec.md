# Feature Specification: MCP Task Server + Database Layer

**Feature Branch**: `001-mcp-task-server`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "Phase-3 Spec-3 MCP Server + Task Database Layer - MCP server with Official SDK exposing task CRUD operations persisted in Neon PostgreSQL via SQLModel"

## Overview

This specification defines the MCP (Model Context Protocol) server and database persistence layer that enables the OpenAI Agent to manage todo tasks. The MCP server exposes task operations as tools that the agent can invoke, with all data persisted in Neon PostgreSQL using SQLModel ORM.

**Core Principle**: The OpenAI Agent must never access the database directly. All task operations flow through stateless MCP tools that enforce user isolation and data persistence.

## User Scenarios & Testing

### User Story 1 - Agent Creates Tasks via MCP (Priority: P1)

An AI agent receives a user request to create a new task (e.g., "Add 'Buy groceries' to my todo list"). The agent invokes the `add_task` MCP tool with the task details, and the tool persists the task to the database, returning confirmation.

**Why this priority**: This is the foundational capability - without the ability to create tasks, no other operations are possible. This represents the minimum viable product.

**Independent Test**: Can be fully tested by invoking the `add_task` tool with valid parameters and verifying the task appears in the database with correct user_id, title, and default values.

**Acceptance Scenarios**:

1. **Given** an authenticated user with user_id "user123", **When** the agent invokes `add_task` with title "Buy groceries" and description "Milk, eggs, bread", **Then** a new task is created in the database with task_id returned, status "created", and all fields populated correctly
2. **Given** an authenticated user, **When** the agent invokes `add_task` with only a title (no description), **Then** a task is created with description as null and completed defaulting to false
3. **Given** an authenticated user, **When** the agent invokes `add_task` with an empty title, **Then** the tool returns an error indicating title is required

---

### User Story 2 - Agent Retrieves Task Lists (Priority: P2)

An AI agent needs to show the user their current tasks. The agent invokes the `list_tasks` MCP tool, optionally filtering by status (all/pending/completed), and receives an array of tasks belonging only to that user.

**Why this priority**: After creating tasks, users need to view them. This is essential for task management but depends on P1 (task creation) being functional.

**Independent Test**: Can be tested by pre-populating the database with tasks for multiple users, then invoking `list_tasks` for a specific user_id and verifying only that user's tasks are returned, with correct filtering by status.

**Acceptance Scenarios**:

1. **Given** user "user123" has 3 pending tasks and 2 completed tasks, **When** the agent invokes `list_tasks` with status "pending", **Then** only the 3 pending tasks are returned
2. **Given** user "user123" has tasks and user "user456" has tasks, **When** the agent invokes `list_tasks` for "user123", **Then** only user123's tasks are returned (user isolation enforced)
3. **Given** a user with no tasks, **When** the agent invokes `list_tasks`, **Then** an empty array is returned

---

### User Story 3 - Agent Marks Tasks Complete (Priority: P3)

An AI agent receives a user request to mark a task as done (e.g., "Mark 'Buy groceries' as complete"). The agent invokes the `complete_task` MCP tool with the task_id, and the tool updates the task's completed status to true.

**Why this priority**: Completing tasks is a core workflow but requires both task creation (P1) and task listing (P2) to identify which task to complete.

**Independent Test**: Can be tested by creating a task, then invoking `complete_task` with its task_id, and verifying the completed field is updated to true in the database.

**Acceptance Scenarios**:

1. **Given** user "user123" has a pending task with task_id 5, **When** the agent invokes `complete_task` with task_id 5, **Then** the task's completed field is set to true and status "completed" is returned
2. **Given** user "user123" attempts to complete task_id 10 belonging to user "user456", **When** the agent invokes `complete_task`, **Then** an error is returned indicating task not found (user isolation enforced)
3. **Given** a task_id that doesn't exist, **When** the agent invokes `complete_task`, **Then** an error is returned indicating task not found

---

### User Story 4 - Agent Updates Task Details (Priority: P4)

An AI agent receives a user request to modify a task (e.g., "Change 'Buy groceries' to 'Buy groceries and fruits'"). The agent invokes the `update_task` MCP tool with the task_id and new values, and the tool updates the task in the database.

**Why this priority**: Task editing is valuable but not essential for basic task management. Users can work around this by deleting and recreating tasks.

**Independent Test**: Can be tested by creating a task, then invoking `update_task` with modified title or description, and verifying the changes are persisted in the database.

**Acceptance Scenarios**:

1. **Given** user "user123" has task_id 1 with title "Buy groceries", **When** the agent invokes `update_task` with task_id 1 and title "Buy groceries and fruits", **Then** the task title is updated and status "updated" is returned
2. **Given** a task, **When** the agent invokes `update_task` with only description (no title), **Then** only the description is updated and title remains unchanged
3. **Given** user "user123" attempts to update task_id 10 belonging to user "user456", **When** the agent invokes `update_task`, **Then** an error is returned (user isolation enforced)

---

### User Story 5 - Agent Deletes Tasks (Priority: P5)

An AI agent receives a user request to remove a task (e.g., "Delete the 'Old task' item"). The agent invokes the `delete_task` MCP tool with the task_id, and the tool removes the task from the database.

**Why this priority**: Task deletion is useful for cleanup but is the least critical operation. Users can simply ignore completed or unwanted tasks.

**Independent Test**: Can be tested by creating a task, then invoking `delete_task` with its task_id, and verifying the task no longer exists in the database.

**Acceptance Scenarios**:

1. **Given** user "user123" has task_id 2, **When** the agent invokes `delete_task` with task_id 2, **Then** the task is removed from the database and status "deleted" is returned
2. **Given** user "user123" attempts to delete task_id 10 belonging to user "user456", **When** the agent invokes `delete_task`, **Then** an error is returned (user isolation enforced)
3. **Given** a task_id that doesn't exist, **When** the agent invokes `delete_task`, **Then** an error is returned indicating task not found

---

### Edge Cases

- What happens when a user_id is not provided to an MCP tool? → Tool returns error indicating user_id is required
- What happens when a task_id doesn't exist? → Tool returns error indicating task not found
- What happens when a user tries to access another user's task? → Tool returns error (appears as "not found" to prevent information leakage)
- What happens when database connection fails? → Tool returns error indicating service unavailable
- What happens when title exceeds reasonable length (e.g., 10,000 characters)? → Tool validates and returns error indicating title too long (max 500 characters)
- What happens when concurrent operations modify the same task? → Database handles with appropriate locking/transactions
- What happens when list_tasks is called with an invalid status value? → Tool returns error indicating invalid status parameter
- What happens when a user has more than the limit number of tasks? → list_tasks returns up to the limit (default 100, max 1000) ordered by created_at DESC. Agent can make multiple calls if needed.
- What happens when complete_task is called on an already-completed task? → Returns success (idempotent operation)
- What happens when delete_task is called on an already-deleted task? → Returns error "task not found" (non-idempotent operation)

## Requirements

### Functional Requirements

- **FR-001**: MCP server MUST be initialized using the Official MCP SDK
- **FR-002**: SQLModel Task table MUST be created with fields: id (integer, primary key), user_id (string, indexed), title (string, max 500 chars), description (text, optional), completed (boolean, default false), created_at (timestamp), updated_at (timestamp)
- **FR-003**: System MUST connect to Neon PostgreSQL via DATABASE_URL environment variable
- **FR-004**: `add_task` MCP tool MUST be implemented accepting user_id (required), title (required), description (optional) and returning task_id, status, title
- **FR-005**: `list_tasks` MCP tool MUST be implemented accepting user_id (required), status (optional: "all", "pending", "completed"), limit (optional: default 100, max 1000) and returning array of task objects ordered by created_at DESC
- **FR-006**: `update_task` MCP tool MUST be implemented accepting user_id (required), task_id (required), title (optional), description (optional) and returning task_id, status, title
- **FR-007**: `delete_task` MCP tool MUST be implemented accepting user_id (required), task_id (required) and returning task_id, status, title
- **FR-008**: `complete_task` MCP tool MUST be implemented accepting user_id (required), task_id (required) and returning task_id, status, title
- **FR-009**: All MCP tools MUST require user_id parameter and filter all database queries by user_id
- **FR-010**: System MUST prevent cross-user access - users can only access their own tasks
- **FR-011**: All MCP tools MUST be stateless - no in-memory state between invocations
- **FR-012**: System MUST validate required parameters and return descriptive errors for missing/invalid inputs
- **FR-013**: System MUST update the updated_at timestamp whenever a task is modified
- **FR-014**: System MUST use SQLModel ORM for all database operations (no raw SQL)
- **FR-015**: MCP tools MUST return consistent response format with task_id, status, and title fields

### Key Entities

- **Task**: Represents a todo item belonging to a user
  - Attributes: id (unique identifier), user_id (owner), title (task name), description (optional details), completed (done status), created_at (creation timestamp), updated_at (last modification timestamp)
  - Relationships: Belongs to a user (via user_id foreign key)
  - Constraints: title is required and limited to 500 characters, user_id is required and indexed for fast queries, completed defaults to false

## Success Criteria

### Measurable Outcomes

- **SC-001**: Agent can successfully create tasks via MCP tools with 100% of valid requests persisting to database
- **SC-002**: Users can only access their own tasks - 0% cross-user data leakage in all operations
- **SC-003**: Database operations complete in under 200ms for 95th percentile of requests
- **SC-004**: MCP tools handle 100 concurrent requests without data corruption or race conditions
- **SC-005**: System maintains zero in-memory state - server restarts do not lose any task data
- **SC-006**: All task operations (create, read, update, delete, complete) are functional and independently testable
- **SC-007**: Error handling provides clear, actionable messages for all failure scenarios (missing parameters, not found, unauthorized, etc.)
- **SC-008**: Task list queries return results in under 100ms for users with up to 1000 tasks

## Tool Specifications

### Tool: add_task

**Purpose**: Create a new task for a user

**Parameters**:
- `user_id` (string, required): The authenticated user's identifier
- `title` (string, required): Task title (max 500 characters)
- `description` (string, optional): Task description (no length limit)

**Returns**:
```json
{
  "task_id": 5,
  "status": "created",
  "title": "Buy groceries"
}
```

**Example Input**:
```json
{
  "user_id": "ziakhan",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Error Cases**:
- Missing user_id: `{"error": "user_id is required"}`
- Missing title: `{"error": "title is required"}`
- Title too long: `{"error": "title exceeds maximum length of 500 characters"}`
- Database error: `{"error": "service unavailable"}`

---

### Tool: list_tasks

**Purpose**: Retrieve tasks for a user, optionally filtered by completion status

**Parameters**:
- `user_id` (string, required): The authenticated user's identifier
- `status` (string, optional): Filter by status - "all" (default), "pending", or "completed"
- `limit` (integer, optional): Maximum number of tasks to return (default: 100, max: 1000)

**Returns**:
```json
[
  {
    "id": 2,
    "title": "Call mom",
    "description": null,
    "completed": false,
    "created_at": "2026-02-09T11:00:00Z",
    "updated_at": "2026-02-09T11:00:00Z"
  },
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

**Ordering**: Tasks are returned ordered by `created_at DESC` (newest first). This shows users their most recent tasks first.

**Example Input**:
```json
{
  "user_id": "ziakhan",
  "status": "pending"
}
```

**Error Cases**:
- Missing user_id: `{"error": "user_id is required"}`
- Invalid status: `{"error": "status must be 'all', 'pending', or 'completed'"}`
- Database error: `{"error": "service unavailable"}`

---

### Tool: complete_task

**Purpose**: Mark a task as completed (idempotent - safe to call multiple times)

**Parameters**:
- `user_id` (string, required): The authenticated user's identifier
- `task_id` (integer, required): The task to mark as complete

**Returns**:
```json
{
  "task_id": 3,
  "status": "completed",
  "title": "Call mom"
}
```

**Example Input**:
```json
{
  "user_id": "ziakhan",
  "task_id": 3
}
```

**Idempotency**: Calling complete_task on an already-completed task returns success (not an error). This makes the operation safe for retry scenarios.

**Error Cases**:
- Missing user_id: `{"error": "user_id is required"}`
- Missing task_id: `{"error": "task_id is required"}`
- Task not found or unauthorized: `{"error": "task not found"}`
- Database error: `{"error": "service unavailable"}`

---

### Tool: delete_task

**Purpose**: Remove a task from the database (non-idempotent - returns error if already deleted)

**Parameters**:
- `user_id` (string, required): The authenticated user's identifier
- `task_id` (integer, required): The task to delete

**Returns**:
```json
{
  "task_id": 2,
  "status": "deleted",
  "title": "Old task"
}
```

**Example Input**:
```json
{
  "user_id": "ziakhan",
  "task_id": 2
}
```

**Idempotency**: Calling delete_task on an already-deleted task returns an error (not success). This follows REST conventions where DELETE operations return 404 on subsequent calls.

**Error Cases**:
- Missing user_id: `{"error": "user_id is required"}`
- Missing task_id: `{"error": "task_id is required"}`
- Task not found or unauthorized: `{"error": "task not found"}`
- Database error: `{"error": "service unavailable"}`

---

### Tool: update_task

**Purpose**: Modify task title or description

**Parameters**:
- `user_id` (string, required): The authenticated user's identifier
- `task_id` (integer, required): The task to update
- `title` (string, optional): New task title (max 500 characters)
- `description` (string, optional): New task description

**Returns**:
```json
{
  "task_id": 1,
  "status": "updated",
  "title": "Buy groceries and fruits"
}
```

**Example Input**:
```json
{
  "user_id": "ziakhan",
  "task_id": 1,
  "title": "Buy groceries and fruits"
}
```

**Error Cases**:
- Missing user_id: `{"error": "user_id is required"}`
- Missing task_id: `{"error": "task_id is required"}`
- No fields to update: `{"error": "at least one of title or description must be provided"}`
- Title too long: `{"error": "title exceeds maximum length of 500 characters"}`
- Task not found or unauthorized: `{"error": "task not found"}`
- Database error: `{"error": "service unavailable"}`

## Behavior Rules

1. **Stateless Operation**: MCP tools must not maintain any in-memory state between invocations. All state is stored in the database.

2. **User Isolation**: Every database query must filter by user_id. Cross-user access is strictly forbidden.

3. **Single Responsibility**: Each tool performs exactly one operation. No tool should combine multiple actions.

4. **Agent Abstraction**: The OpenAI Agent never accesses the database directly. All database operations flow through MCP tools.

5. **Error Transparency**: Tools return clear, actionable error messages without exposing internal implementation details or security information.

6. **Data Validation**: All required parameters must be validated before database operations. Invalid inputs return errors immediately.

7. **Timestamp Management**: created_at is set once on creation; updated_at is updated on every modification.

## Assumptions

1. **Authentication Handled Upstream**: The user_id parameter is assumed to be authenticated and validated before reaching the MCP tools. The MCP layer does not perform authentication.

2. **Database Schema Exists**: The tasks table is assumed to exist in the database before MCP tools are invoked. Migration/schema creation is handled separately.

3. **Connection Pooling**: Database connection pooling is configured at the application level with pool_size=10 and max_overflow=20. This provides 10 persistent connections with up to 20 additional connections during traffic spikes.

4. **Concurrent Access**: PostgreSQL's default transaction isolation level (Read Committed) is sufficient for task operations. No explicit locking is required for the MVP.

5. **Error Logging**: Detailed error logging (for debugging) happens at the application level. MCP tools return user-friendly error messages.

6. **Title Length Limit**: 500 characters is a reasonable maximum for task titles based on typical todo application usage patterns.

7. **No Soft Deletes**: delete_task performs a hard delete (removes from database). Soft deletes (marking as deleted) are not required for the MVP.

## Out of Scope

The following are explicitly excluded from this specification:

- **Frontend UI**: No user interface components or web pages
- **Chat Endpoint**: No HTTP endpoints for chat functionality
- **Conversation Storage**: No conversation history or message persistence
- **OpenAI Agent Logic**: No agent decision-making, prompt engineering, or AI model integration
- **Authentication Implementation**: No JWT verification, session management, or user login flows
- **Task Sharing**: No ability to share tasks between users or assign tasks to others
- **Task Categories/Tags**: No categorization, tagging, or organization beyond completed status
- **Task Priorities**: No priority levels or ordering beyond creation time
- **Task Due Dates**: No deadline or reminder functionality
- **Task Attachments**: No file uploads or media attachments
- **Task Comments**: No commenting or collaboration features
- **Audit Logging**: No detailed audit trail of who changed what and when (beyond updated_at)
- **Bulk Operations**: No batch create/update/delete operations
- **Task Search**: No full-text search or advanced filtering beyond status

## Clarifications

### Session 2026-02-09

- Q: What version constraint should be used for the Official MCP SDK dependency? → A: Use latest version without version constraints (mcp[cli])
- Q: How should list_tasks handle users with more than 1000 tasks - is pagination needed? → A: Implement limit parameter only: list_tasks(user_id, status, limit=100)
- Q: Should complete_task and delete_task be idempotent (return success if already in target state)? → A: complete_task idempotent, delete_task non-idempotent
- Q: What order should list_tasks return tasks in? → A: Order by created_at DESC (newest first)
- Q: What connection pool configuration should be used for database operations? → A: pool_size=10, max_overflow=20

## Dependencies

- **Official MCP SDK**: Must be installed and available for MCP server initialization (use latest version: `mcp[cli]`)
- **SQLModel**: Required for ORM operations and database models
- **PostgreSQL Driver**: Required for database connectivity (e.g., psycopg2 or asyncpg)
- **Neon PostgreSQL**: Database must be provisioned and accessible via DATABASE_URL
- **Existing Task Table**: The tasks table from Phase-2 must exist with the correct schema
- **Environment Configuration**: DATABASE_URL must be configured in environment variables

## Constraints

- **Must comply with Hackathon Phase-3 architecture**: Follow established patterns from Phase-2 (SQLModel, Neon, user isolation)
- **Must use SQLModel + Neon**: No alternative ORMs or databases
- **Must use Official MCP SDK**: No custom MCP implementations or alternative protocols
- **No manual coding outside spec-driven workflow**: All implementation must follow `/sp.plan` → `/sp.tasks` → implementation workflow
- **Performance Target**: Database operations must complete in under 200ms (95th percentile)
- **Stateless Requirement**: No in-memory state allowed in MCP tools

## Next Steps

After this specification is approved:

1. Run `/sp.clarify` if any requirements need further clarification
2. Run `/sp.plan` to generate the implementation plan
3. Run `/sp.tasks` to break down into actionable tasks
4. Implement via Claude Code following the task breakdown
5. Validate with integration tests covering all user stories

---

**Specification Status**: ✅ Ready for review and planning
