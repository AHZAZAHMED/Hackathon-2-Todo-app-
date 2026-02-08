# Feature Specification: Backend API + Database Persistence

**Feature Branch**: `003-tasks-crud-api`
**Created**: 2026-02-06
**Status**: Draft
**Input**: User description: "Backend API + Database Persistence (Hackathon II Phase-2) - FastAPI backend with PostgreSQL for Task CRUD operations with JWT authentication"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create New Task (Priority: P1) 🎯 MVP

An authenticated user clicks the "Add Task" button in the dashboard, enters a task title and optional description, and submits the form. The system validates the input, persists the task to the database with the user's ID from their JWT token, and displays the new task in their task list.

**Why this priority**: This is the foundational capability that enables users to add tasks to the system. Without the ability to create tasks, the application has no core functionality. This is the minimum viable product that delivers immediate value.

**Independent Test**: Can be fully tested by authenticating a user, submitting a task creation request via the API, and verifying the task appears in the database and is returned in subsequent GET requests. Delivers immediate value by allowing users to capture their tasks.

**Acceptance Scenarios**:

1. **Given** an authenticated user on the dashboard, **When** they submit a new task with title "Buy groceries" and description "Milk, eggs, bread", **Then** the task is created in the database with their user_id, a 201 response is returned with the task data, and the task appears in their task list
2. **Given** an authenticated user, **When** they submit a task with only a title "Call dentist" (no description), **Then** the task is created successfully with an empty description
3. **Given** an authenticated user, **When** they submit a task with an empty title, **Then** the system returns a 422 validation error with message "Title is required"
4. **Given** an unauthenticated user, **When** they attempt to create a task, **Then** the system returns a 401 Unauthorized error
5. **Given** an authenticated user, **When** they create a task, **Then** the task's user_id matches the user_id from their JWT token (not from request body)
6. **Given** an authenticated user, **When** they create a task, **Then** the task has completed=false by default and timestamps are set automatically

---

### User Story 2 - View All Tasks (Priority: P2)

An authenticated user navigates to the dashboard and the system automatically fetches and displays all tasks belonging to that user. Tasks are retrieved from the database filtered by the user's ID from their JWT token, ensuring complete user isolation.

**Why this priority**: After users can create tasks (P1), they need to view their task list. This is the second most critical feature as it provides visibility into what tasks exist and enables users to see the results of their task creation.

**Independent Test**: Can be fully tested by creating multiple tasks for a user, then making a GET request to retrieve all tasks and verifying only that user's tasks are returned. Delivers value by showing users their complete task list.

**Acceptance Scenarios**:

1. **Given** an authenticated user with 3 tasks in the database, **When** they request their task list, **Then** all 3 tasks are returned with complete data (id, title, description, completed, timestamps)
2. **Given** an authenticated user with no tasks, **When** they request their task list, **Then** an empty array is returned with 200 status
3. **Given** two authenticated users (User A and User B), **When** User A requests their task list, **Then** only User A's tasks are returned (User B's tasks are not visible)
4. **Given** an unauthenticated user, **When** they attempt to fetch tasks, **Then** the system returns a 401 Unauthorized error
5. **Given** an authenticated user with 10 tasks, **When** they request their task list, **Then** tasks are returned in reverse chronological order (newest first)

---

### User Story 3 - Update Existing Task (Priority: P3)

An authenticated user clicks the edit button on a task, modifies the title or description, and saves the changes. The system validates ownership (task belongs to the authenticated user), updates the task in the database, and displays the updated task.

**Why this priority**: After users can create and view tasks (P1, P2), they need the ability to edit tasks to correct mistakes or update information. This is important for usability but not critical for the MVP.

**Independent Test**: Can be fully tested by creating a task, then making a PUT request with updated data and verifying the changes persist in the database. Delivers value by allowing users to maintain accurate task information.

**Acceptance Scenarios**:

1. **Given** an authenticated user with a task "Buy milk", **When** they update the title to "Buy organic milk" and description to "From Whole Foods", **Then** the task is updated in the database and the updated data is returned
2. **Given** an authenticated user, **When** they attempt to update a task that belongs to another user, **Then** the system returns a 404 Not Found error (task doesn't exist in their scope)
3. **Given** an authenticated user, **When** they update a task with an empty title, **Then** the system returns a 422 validation error
4. **Given** an authenticated user, **When** they update a task, **Then** the updated_at timestamp is automatically updated to the current time
5. **Given** an unauthenticated user, **When** they attempt to update a task, **Then** the system returns a 401 Unauthorized error
6. **Given** an authenticated user, **When** they attempt to update a non-existent task ID, **Then** the system returns a 404 Not Found error

---

### User Story 4 - Delete Task (Priority: P4)

An authenticated user clicks the delete button on a task and confirms the deletion. The system validates ownership, removes the task from the database, and updates the task list to reflect the deletion.

**Why this priority**: After users can create, view, and edit tasks (P1-P3), they need the ability to remove tasks they no longer need. This is important for task management but less critical than the core CRUD operations.

**Independent Test**: Can be fully tested by creating a task, then making a DELETE request and verifying the task is removed from the database and no longer appears in GET requests. Delivers value by allowing users to maintain a clean task list.

**Acceptance Scenarios**:

1. **Given** an authenticated user with a task, **When** they delete the task, **Then** the task is removed from the database and a 204 No Content response is returned
2. **Given** an authenticated user, **When** they attempt to delete a task that belongs to another user, **Then** the system returns a 404 Not Found error
3. **Given** an authenticated user, **When** they delete a task and then attempt to fetch it, **Then** the system returns a 404 Not Found error
4. **Given** an authenticated user, **When** they attempt to delete a non-existent task ID, **Then** the system returns a 404 Not Found error
5. **Given** an unauthenticated user, **When** they attempt to delete a task, **Then** the system returns a 401 Unauthorized error

---

### User Story 5 - Toggle Task Completion (Priority: P5)

An authenticated user clicks the checkbox next to a task to mark it as complete or incomplete. The system validates ownership, toggles the completed status in the database, and updates the visual state of the task.

**Why this priority**: After all core CRUD operations are functional (P1-P4), users need a quick way to mark tasks as done. This is a convenience feature that enhances usability but the same result can be achieved through the update endpoint (P3).

**Independent Test**: Can be fully tested by creating a task (completed=false), making a PATCH request to toggle completion, and verifying the completed field is updated in the database. Delivers value by providing a streamlined way to track task completion.

**Acceptance Scenarios**:

1. **Given** an authenticated user with an incomplete task (completed=false), **When** they toggle completion, **Then** the task's completed field is set to true and the updated task is returned
2. **Given** an authenticated user with a completed task (completed=true), **When** they toggle completion, **Then** the task's completed field is set to false
3. **Given** an authenticated user, **When** they attempt to toggle completion on a task belonging to another user, **Then** the system returns a 404 Not Found error
4. **Given** an authenticated user, **When** they toggle completion, **Then** the updated_at timestamp is automatically updated
5. **Given** an unauthenticated user, **When** they attempt to toggle task completion, **Then** the system returns a 401 Unauthorized error

---

### Edge Cases

- **Concurrent updates**: When two requests attempt to update the same task simultaneously, the last write wins (database handles concurrency)
- **Invalid JWT token**: When a request includes an expired or malformed JWT, the system returns 401 Unauthorized with a clear error message
- **Database connection failure**: When the database is unavailable, the system returns 503 Service Unavailable with a retry-after header
- **Extremely long task titles**: When a task title exceeds 500 characters, the system returns 422 validation error
- **SQL injection attempts**: When malicious SQL is included in task data, the ORM parameterizes queries and prevents injection
- **Missing user_id in JWT**: When a JWT token is missing the user_id claim, the system returns 401 Unauthorized
- **Task ID type mismatch**: When a non-integer task ID is provided in the URL, the system returns 422 validation error
- **Orphaned tasks**: When a user is deleted from the users table, their tasks are automatically deleted via CASCADE foreign key constraint
- **Empty task list performance**: When a user has 0 tasks, the query completes instantly and returns an empty array
- **Large task lists**: When a user has 1000+ tasks, the system returns all tasks without pagination (pagination is out of scope for Phase-2)

## Requirements *(mandatory)*

### Functional Requirements

#### Backend API Requirements

- **FR-001**: System MUST provide a FastAPI application that starts successfully and listens on the configured HOST and PORT
- **FR-002**: System MUST establish a connection to PostgreSQL database using the DATABASE_URL environment variable
- **FR-003**: System MUST verify JWT tokens on every API request using the BETTER_AUTH_SECRET
- **FR-004**: System MUST extract user_id from verified JWT token claims for all authenticated requests
- **FR-005**: System MUST reject requests with missing JWT tokens with 401 Unauthorized status
- **FR-006**: System MUST reject requests with invalid or expired JWT tokens with 401 Unauthorized status
- **FR-007**: System MUST reject requests with malformed JWT tokens with 401 Unauthorized status
- **FR-008**: System MUST NEVER accept user_id from request body, query parameters, or URL path
- **FR-009**: System MUST be stateless (no server-side session storage)
- **FR-010**: System MUST configure CORS to allow requests from the frontend origin with credentials

#### Task CRUD Requirements

- **FR-011**: System MUST provide GET /api/tasks endpoint that returns all tasks for the authenticated user
- **FR-012**: System MUST provide POST /api/tasks endpoint that creates a new task for the authenticated user
- **FR-013**: System MUST provide GET /api/tasks/{id} endpoint that returns a single task if it belongs to the authenticated user
- **FR-014**: System MUST provide PUT /api/tasks/{id} endpoint that updates a task if it belongs to the authenticated user
- **FR-015**: System MUST provide DELETE /api/tasks/{id} endpoint that deletes a task if it belongs to the authenticated user
- **FR-016**: System MUST provide PATCH /api/tasks/{id}/complete endpoint that toggles task completion status
- **FR-017**: System MUST validate that task title is required and not empty
- **FR-018**: System MUST allow task description to be optional (can be null or empty)
- **FR-019**: System MUST set completed=false by default when creating new tasks
- **FR-020**: System MUST automatically set created_at timestamp when creating tasks
- **FR-021**: System MUST automatically update updated_at timestamp when modifying tasks

#### User Isolation Requirements

- **FR-022**: System MUST filter all task queries by the authenticated user's user_id from JWT
- **FR-023**: System MUST return 404 Not Found when a user attempts to access a task that doesn't belong to them
- **FR-024**: System MUST ensure users can only create tasks associated with their own user_id
- **FR-025**: System MUST ensure users can only update tasks that belong to them
- **FR-026**: System MUST ensure users can only delete tasks that belong to them
- **FR-027**: System MUST ensure users can only view tasks that belong to them

#### Database Requirements

- **FR-028**: System MUST create a tasks table with columns: id (primary key), user_id (foreign key), title, description, completed, created_at, updated_at
- **FR-029**: System MUST enforce foreign key constraint between tasks.user_id and users.id
- **FR-030**: System MUST create an index on tasks.user_id for query performance
- **FR-031**: System MUST create an index on tasks.completed for filtering performance
- **FR-032**: System MUST use CASCADE delete on the foreign key so tasks are deleted when a user is deleted
- **FR-033**: System MUST persist all task data in PostgreSQL (no in-memory storage)
- **FR-034**: System MUST use SQLModel ORM for database operations

#### Error Handling Requirements

- **FR-035**: System MUST return 401 Unauthorized for authentication failures with descriptive error messages
- **FR-036**: System MUST return 404 Not Found when a requested task doesn't exist or doesn't belong to the user
- **FR-037**: System MUST return 422 Unprocessable Entity for validation errors with field-specific error messages
- **FR-038**: System MUST return 500 Internal Server Error for unexpected server errors
- **FR-039**: System MUST return 503 Service Unavailable when the database is unreachable
- **FR-040**: System MUST include error codes and messages in all error responses

#### Integration Requirements

- **FR-041**: System MUST integrate with the existing frontend API client (lib/api-client.ts)
- **FR-042**: System MUST accept JWT tokens in the Authorization header as "Bearer {token}"
- **FR-043**: System MUST return JSON responses for all endpoints
- **FR-044**: System MUST use consistent response format: { "data": {...} } for success responses
- **FR-045**: System MUST use consistent error format: { "error": { "code": "...", "message": "..." } }

### Key Entities

- **Task**: Represents a user's task item with attributes including unique identifier, title (required text), description (optional text), completion status (boolean), creation timestamp, last update timestamp, and owner reference (user_id). Related to User entity through user_id foreign key with CASCADE delete.

- **User**: Represents an authenticated user account managed by Better Auth with attributes including unique identifier (string), email address, display name, and creation timestamp. Related to Task entity through one-to-many relationship (one user can have many tasks).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a new task in under 10 seconds from clicking "Add Task" to seeing it in their list
- **SC-002**: Users can view their complete task list in under 1 second after page load
- **SC-003**: Users can update a task in under 5 seconds from clicking "Edit" to seeing the updated data
- **SC-004**: Users can delete a task in under 3 seconds from clicking "Delete" to seeing it removed from the list
- **SC-005**: Users can toggle task completion in under 2 seconds from clicking the checkbox to seeing the visual update
- **SC-006**: System maintains 100% user isolation (0 instances of users accessing other users' tasks)
- **SC-007**: System handles 100 concurrent authenticated users without performance degradation
- **SC-008**: All frontend task management buttons become fully functional (no mock data remains)
- **SC-009**: System successfully persists all task operations to PostgreSQL database (verified by server restart)
- **SC-010**: System completes end-to-end task flow (create → view → update → complete → delete) without errors

## Scope *(mandatory)*

### In Scope

- FastAPI application initialization and configuration
- PostgreSQL database connection using DATABASE_URL environment variable
- SQLModel ORM integration for database operations
- Database migration script for tasks table creation
- JWT verification middleware using BETTER_AUTH_SECRET
- User_id extraction from JWT token claims
- GET /api/tasks endpoint (list all user's tasks)
- POST /api/tasks endpoint (create new task)
- GET /api/tasks/{id} endpoint (get single task)
- PUT /api/tasks/{id} endpoint (update task)
- DELETE /api/tasks/{id} endpoint (delete task)
- PATCH /api/tasks/{id}/complete endpoint (toggle completion)
- Pydantic request/response models for task data
- Input validation for task creation and updates
- User isolation enforcement (filter by JWT user_id)
- Error handling for 401, 404, 422, 500, 503 status codes
- CORS configuration for frontend origin
- Integration with existing frontend API client
- Database indexes for performance (user_id, completed)
- Foreign key constraints with CASCADE delete
- Automatic timestamp management (created_at, updated_at)
- Stateless backend design (no server-side sessions)

### Out of Scope

- Task pagination or infinite scroll (all tasks returned in single request)
- Task filtering by completion status (frontend handles filtering)
- Task sorting options (tasks returned in creation order)
- Task search functionality
- Task categories or tags
- Task priority levels
- Task due dates or reminders
- Task sharing or collaboration features
- Task attachments or file uploads
- Task comments or notes
- Task history or audit log
- Role-based access control (RBAC)
- Admin panel or dashboard
- Task analytics or statistics
- Bulk task operations (delete all, mark all complete)
- Task import/export functionality
- OAuth provider integration
- Refresh token implementation
- Rate limiting for API requests
- API versioning
- GraphQL API (REST only)
- WebSocket real-time updates
- Chatbot features (Phase-3)
- Email notifications
- Task templates
- Recurring tasks

## Assumptions *(optional)*

1. **Authentication Infrastructure**: The Better Auth JWT authentication system is fully functional and issuing valid JWT tokens with user_id, email, and name claims
2. **Database Availability**: A PostgreSQL database (Neon Serverless) is accessible and the DATABASE_URL environment variable is configured
3. **Environment Variables**: Both BETTER_AUTH_SECRET and DATABASE_URL are set in the backend .env file and match the frontend configuration
4. **User Table Exists**: The users table managed by Better Auth already exists in the database with id, email, name, and created_at columns
5. **Frontend API Client**: The frontend API client (lib/api-client.ts) is configured to attach JWT tokens automatically and handle error responses
6. **Network Connectivity**: The frontend and backend can communicate over HTTP/HTTPS with CORS properly configured
7. **Task Volume**: Users will have a reasonable number of tasks (< 1000) so pagination is not required for Phase-2
8. **Data Retention**: Tasks persist indefinitely until explicitly deleted by the user or cascade-deleted when the user is deleted
9. **Concurrent Users**: The system needs to support up to 100 concurrent users for Phase-2 (production scaling is out of scope)
10. **Error Recovery**: Users can retry failed operations manually (automatic retry logic is out of scope)

## Dependencies *(optional)*

### External Dependencies

- **FastAPI**: Python web framework for building the REST API
- **SQLModel**: ORM library for database operations (combines SQLAlchemy and Pydantic)
- **PostgreSQL**: Relational database for persistent storage
- **Neon Serverless**: PostgreSQL hosting service
- **PyJWT**: Library for JWT token verification
- **Uvicorn**: ASGI server for running the FastAPI application
- **python-dotenv**: Library for loading environment variables from .env file

### Internal Dependencies

- **Authentication System (002-auth)**: Completed - Provides JWT tokens with user_id claims
- **Frontend Web Application (001-frontend-web-app)**: Completed - Provides UI for task management
- **Frontend API Client**: Exists at frontend/lib/api-client.ts and needs backend endpoints to call
- **Database Connection**: Backend already has database.py with PostgreSQL connection setup
- **JWT Verification Middleware**: Backend already has auth/middleware.py and auth/dependencies.py for JWT verification

### Blocking Dependencies

- **Database Migration**: Tasks table must be created before any CRUD operations can function
- **Environment Configuration**: DATABASE_URL and BETTER_AUTH_SECRET must be set in backend .env file
- **Backend Server Running**: FastAPI application must be started before frontend can make API calls
- **User Authentication**: Users must be logged in with valid JWT tokens to access task endpoints

## Non-Functional Requirements *(optional)*

### Performance

- Task creation requests must complete within 500ms under normal load
- Task retrieval requests must complete within 200ms for lists up to 100 tasks
- Task update/delete requests must complete within 300ms
- Database queries must use indexes for user_id filtering to maintain performance
- System must handle 100 concurrent authenticated users without response time degradation

### Security

- All API endpoints must require valid JWT authentication (no public endpoints)
- JWT tokens must be verified using the shared BETTER_AUTH_SECRET
- User_id must be extracted exclusively from JWT claims (never from request data)
- Database queries must use parameterized statements to prevent SQL injection
- Foreign key constraints must enforce referential integrity
- CORS must be configured to allow only the specific frontend origin
- Error messages must not expose sensitive system information or stack traces

### Reliability

- System must gracefully handle database connection failures with 503 errors
- System must validate all input data before database operations
- System must use database transactions for data consistency
- System must automatically recover from transient database errors
- System must log errors for debugging without exposing details to users

### Maintainability

- Code must follow FastAPI best practices and conventions
- Database models must use SQLModel for type safety
- API endpoints must use Pydantic models for request/response validation
- Error handling must be centralized and consistent
- Database migrations must be version-controlled and repeatable

### Scalability

- Backend must be stateless to enable horizontal scaling
- Database connection pooling must be configured for efficient resource usage
- Indexes must be created on frequently queried columns (user_id, completed)
- System design must support adding pagination in future phases without breaking changes

## Open Questions *(optional)*

None. All requirements are sufficiently specified with reasonable defaults documented in the Assumptions section.

## References *(optional)*

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Neon Serverless PostgreSQL](https://neon.tech/docs)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- Hackathon II Phase-2 CLAUDE.md (root project rules)
- Backend CLAUDE.md (backend-specific rules)
- Authentication System Specification (specs/002-auth/spec.md)
- Frontend Web Application Specification (specs/001-frontend-web-app/spec.md)
