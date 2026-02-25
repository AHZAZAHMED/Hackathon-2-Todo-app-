# API Contracts: Task CRUD Endpoints

**Feature**: Backend API + Database Persistence (003-tasks-crud-api)
**Date**: 2026-02-06
**Base URL**: `http://localhost:8000` (development) | `https://api.example.com` (production)
**Authentication**: JWT Bearer token required for all endpoints

## Overview

This document defines the API contracts for Task CRUD operations. All endpoints require JWT authentication and enforce user isolation - users can only access their own tasks.

**Endpoint Summary**:
- `GET /api/tasks` - List all tasks for authenticated user
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get single task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/complete` - Toggle task completion

---

## Authentication

All endpoints require a valid JWT token in the Authorization header.

**Header Format**:
```
Authorization: Bearer <jwt_token>
```

**JWT Claims Required**:
- `user_id` (string): User identifier
- `email` (string): User email
- `name` (string): User display name
- `exp` (number): Token expiration timestamp
- `iat` (number): Token issued at timestamp

**Authentication Errors**:
- `401 Unauthorized`: Missing, invalid, or expired JWT token

---

## Endpoint 1: List All Tasks

**GET /api/tasks**

Retrieves all tasks belonging to the authenticated user.

### Request

**Method**: `GET`
**Path**: `/api/tasks`
**Query Parameters**: None (no filtering/pagination in Phase-2)
**Request Body**: None

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Response

**Success (200 OK)**:
```json
{
  "data": [
    {
      "id": 1,
      "user_id": "clx1234567890",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2026-02-06T10:00:00Z",
      "updated_at": "2026-02-06T10:00:00Z"
    },
    {
      "id": 2,
      "user_id": "clx1234567890",
      "title": "Call dentist",
      "description": null,
      "completed": true,
      "created_at": "2026-02-05T14:30:00Z",
      "updated_at": "2026-02-06T09:15:00Z"
    }
  ]
}
```

**Empty List (200 OK)**:
```json
{
  "data": []
}
```

**Error (401 Unauthorized)**:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing token"
  }
}
```

### Behavior
- Returns tasks in reverse chronological order (newest first)
- Only returns tasks belonging to authenticated user
- Empty array if user has no tasks
- Maximum ~1000 tasks per user (no pagination in Phase-2)

---

## Endpoint 2: Create Task

**POST /api/tasks**

Creates a new task for the authenticated user.

### Request

**Method**: `POST`
**Path**: `/api/tasks`
**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Field Requirements**:
- `title` (string, required): Task title (max 500 characters, non-empty)
- `description` (string, optional): Task description (can be null or omitted)

### Response

**Success (201 Created)**:
```json
{
  "data": {
    "id": 1,
    "user_id": "clx1234567890",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-02-06T10:00:00Z",
    "updated_at": "2026-02-06T10:00:00Z"
  }
}
```

**Error (401 Unauthorized)**:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing token"
  }
}
```

**Error (422 Validation Error)**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Title is required"
  }
}
```

**Error (422 Title Too Long)**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Title must be 500 characters or less"
  }
}
```

### Behavior
- `user_id` automatically set from JWT token (never from request body)
- `completed` defaults to `false`
- `created_at` and `updated_at` set to current UTC timestamp
- Returns 422 if title is empty or exceeds 500 characters
- Description is optional (can be null or omitted)

---

## Endpoint 3: Get Single Task

**GET /api/tasks/{id}**

Retrieves a specific task by ID if it belongs to the authenticated user.

### Request

**Method**: `GET`
**Path**: `/api/tasks/{id}`
**Path Parameters**:
- `id` (integer, required): Task ID

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Response

**Success (200 OK)**:
```json
{
  "data": {
    "id": 1,
    "user_id": "clx1234567890",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-02-06T10:00:00Z",
    "updated_at": "2026-02-06T10:00:00Z"
  }
}
```

**Error (401 Unauthorized)**:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing token"
  }
}
```

**Error (404 Not Found)**:
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Task not found"
  }
}
```

### Behavior
- Returns 404 if task doesn't exist OR doesn't belong to authenticated user
- Does NOT reveal whether task exists for security reasons
- Task ID must be a valid integer

---

## Endpoint 4: Update Task

**PUT /api/tasks/{id}**

Updates an existing task's title and/or description.

### Request

**Method**: `PUT`
**Path**: `/api/tasks/{id}`
**Path Parameters**:
- `id` (integer, required): Task ID

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Buy organic groceries",
  "description": "From Whole Foods"
}
```

**Field Requirements**:
- `title` (string, required): New task title (max 500 characters, non-empty)
- `description` (string, optional): New task description (can be null)

### Response

**Success (200 OK)**:
```json
{
  "data": {
    "id": 1,
    "user_id": "clx1234567890",
    "title": "Buy organic groceries",
    "description": "From Whole Foods",
    "completed": false,
    "created_at": "2026-02-06T10:00:00Z",
    "updated_at": "2026-02-06T11:30:00Z"
  }
}
```

**Error (401 Unauthorized)**:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing token"
  }
}
```

**Error (404 Not Found)**:
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Task not found"
  }
}
```

**Error (422 Validation Error)**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Title is required"
  }
}
```

### Behavior
- Only updates title and description (not completed status)
- `updated_at` automatically set to current UTC timestamp
- `completed` and `created_at` remain unchanged
- Returns 404 if task doesn't exist or doesn't belong to user
- Returns 422 if title is empty or exceeds 500 characters

---

## Endpoint 5: Delete Task

**DELETE /api/tasks/{id}**

Permanently deletes a task from the database.

### Request

**Method**: `DELETE`
**Path**: `/api/tasks/{id}`
**Path Parameters**:
- `id` (integer, required): Task ID

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Request Body**: None

### Response

**Success (204 No Content)**:
```
(empty response body)
```

**Error (401 Unauthorized)**:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing token"
  }
}
```

**Error (404 Not Found)**:
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Task not found"
  }
}
```

### Behavior
- Permanently removes task from database (no soft delete)
- Returns 204 with empty body on success
- Returns 404 if task doesn't exist or doesn't belong to user
- Task cannot be recovered after deletion

---

## Endpoint 6: Toggle Task Completion

**PATCH /api/tasks/{id}/complete**

Toggles the completion status of a task (true ↔ false).

### Request

**Method**: `PATCH`
**Path**: `/api/tasks/{id}/complete`
**Path Parameters**:
- `id` (integer, required): Task ID

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**: None (toggles current state)

### Response

**Success (200 OK) - Marked Complete**:
```json
{
  "data": {
    "id": 1,
    "user_id": "clx1234567890",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": true,
    "created_at": "2026-02-06T10:00:00Z",
    "updated_at": "2026-02-06T12:00:00Z"
  }
}
```

**Success (200 OK) - Marked Incomplete**:
```json
{
  "data": {
    "id": 1,
    "user_id": "clx1234567890",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-02-06T10:00:00Z",
    "updated_at": "2026-02-06T12:05:00Z"
  }
}
```

**Error (401 Unauthorized)**:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing token"
  }
}
```

**Error (404 Not Found)**:
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Task not found"
  }
}
```

### Behavior
- Flips `completed` boolean: `false` → `true` or `true` → `false`
- `updated_at` automatically set to current UTC timestamp
- Title, description, and created_at remain unchanged
- Returns 404 if task doesn't exist or doesn't belong to user
- Can be toggled multiple times

---

## Common Response Patterns

### Success Response Format
```json
{
  "data": <resource or array>
}
```

### Error Response Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Missing, invalid, or expired JWT token |
| `NOT_FOUND` | 404 | Task doesn't exist or doesn't belong to user |
| `VALIDATION_ERROR` | 422 | Invalid request data (empty title, too long, etc.) |
| `INTERNAL_ERROR` | 500 | Unexpected server error |
| `SERVICE_UNAVAILABLE` | 503 | Database connection failure |

---

## Data Types

### Task Object
```typescript
interface Task {
  id: number;                    // Unique task identifier
  user_id: string;               // Owner's user ID (from JWT)
  title: string;                 // Task title (max 500 chars)
  description: string | null;    // Optional description
  completed: boolean;            // Completion status
  created_at: string;            // ISO 8601 timestamp (UTC)
  updated_at: string;            // ISO 8601 timestamp (UTC)
}
```

### Timestamp Format
All timestamps use ISO 8601 format in UTC timezone:
```
2026-02-06T10:00:00Z
```

---

## Security Considerations

### User Isolation
- All endpoints filter by `user_id` from JWT token
- Users cannot access other users' tasks
- Returns 404 (not 403) to avoid information leakage

### Input Validation
- Title: Required, max 500 characters, non-empty
- Description: Optional, unlimited length
- Task ID: Must be valid integer

### Authentication
- JWT token required for all endpoints
- Token verified using BETTER_AUTH_SECRET
- Invalid/expired tokens return 401

---

## Rate Limiting

**Phase-2**: No rate limiting implemented
**Future**: May add rate limiting per user (e.g., 100 requests/minute)

---

## CORS Configuration

**Allowed Origins**: Frontend origin (e.g., `http://localhost:3000`)
**Allowed Methods**: GET, POST, PUT, DELETE, PATCH, OPTIONS
**Allowed Headers**: Authorization, Content-Type
**Credentials**: Allowed (for JWT cookies)

---

## Example Usage

### Create and Complete a Task

```bash
# 1. Create task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'

# Response: {"data": {"id": 1, "completed": false, ...}}

# 2. Mark complete
curl -X PATCH http://localhost:8000/api/tasks/1/complete \
  -H "Authorization: Bearer <jwt_token>"

# Response: {"data": {"id": 1, "completed": true, ...}}

# 3. Update title
curl -X PUT http://localhost:8000/api/tasks/1 \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy organic groceries", "description": "From Whole Foods"}'

# Response: {"data": {"id": 1, "title": "Buy organic groceries", ...}}

# 4. Delete task
curl -X DELETE http://localhost:8000/api/tasks/1 \
  -H "Authorization: Bearer <jwt_token>"

# Response: 204 No Content
```

---

## OpenAPI Specification

The FastAPI backend automatically generates OpenAPI documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [JWT Authentication](https://jwt.io/)
- Feature Specification: specs/003-tasks-crud-api/spec.md
- Data Model: specs/003-tasks-crud-api/data-model.md
