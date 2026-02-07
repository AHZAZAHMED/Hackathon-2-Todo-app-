# Data Model: Frontend Web Application

**Feature**: Frontend Web Application
**Branch**: 001-frontend-web-app
**Created**: 2026-02-05

## Overview

This document defines the frontend data models and TypeScript types for the Todo application. These models represent the structure of data as it flows through the frontend application, from API responses to component state.

## Core Entities

### Task

Represents a user's todo item with all associated metadata.

**TypeScript Definition** (`types/task.ts`):

```typescript
export interface Task {
  id: string;                    // Unique identifier (UUID or integer as string)
  title: string;                 // Task title (max 200 characters)
  description: string;           // Task description (max 1000 characters)
  completed: boolean;            // Completion status
  created_at: string;            // ISO 8601 timestamp
  updated_at: string;            // ISO 8601 timestamp
  user_id: string;               // Owner's user ID (foreign key)
}

export interface CreateTaskInput {
  title: string;
  description: string;
}

export interface UpdateTaskInput {
  title?: string;
  description?: string;
  completed?: boolean;
}
```

**Field Descriptions**:
- `id`: Unique identifier assigned by backend
- `title`: Short description of the task (required, 1-200 chars)
- `description`: Detailed description (optional, max 1000 chars)
- `completed`: Boolean flag indicating completion status
- `created_at`: Timestamp when task was created (ISO 8601 format)
- `updated_at`: Timestamp when task was last modified (ISO 8601 format)
- `user_id`: ID of the user who owns this task (set by backend from JWT)

**Validation Rules**:
- Title: Required, 1-200 characters, non-empty after trim
- Description: Optional, max 1000 characters
- Completed: Boolean, defaults to false on creation

**State Transitions**:
- Created → Pending (completed: false)
- Pending → Completed (completed: true)
- Completed → Pending (completed: false) - can be toggled back

---

### User

Represents an authenticated user in the system.

**TypeScript Definition** (`types/user.ts`):

```typescript
export interface User {
  id: string;                    // Unique identifier
  name: string;                  // User's display name
  email: string;                 // User's email address
}

export interface SignupInput {
  name: string;
  email: string;
  password: string;
}

export interface LoginInput {
  email: string;
  password: string;
}
```

**Field Descriptions**:
- `id`: Unique identifier assigned by backend
- `name`: User's display name (shown in profile dropdown)
- `email`: User's email address (used for login)

**Note**: Password is never stored or transmitted in the User object. It's only used in SignupInput and LoginInput for authentication.

---

### AuthState

Represents the current authentication state in the frontend.

**TypeScript Definition** (`types/auth.ts`):

```typescript
export interface AuthState {
  isAuthenticated: boolean;      // Whether user is logged in
  user: User | null;             // Current user data (null if not authenticated)
  token: string | null;          // JWT token (null if not authenticated)
}

export interface AuthResponse {
  user: User;
  token: string;
}
```

**Field Descriptions**:
- `isAuthenticated`: Boolean flag indicating if user is currently authenticated
- `user`: User object containing current user's data (null when not logged in)
- `token`: JWT token for API authentication (null when not logged in)

**State Management**:
- Stored in React Context or custom hook (useAuth)
- Updated on login, signup, logout
- Persisted across page refreshes (implementation in auth spec)

---

## API Response Types

### Standard API Response

**TypeScript Definition** (`types/api.ts`):

```typescript
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  error: string;
  message: string;
  statusCode: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
}
```

**Usage**:
- `ApiResponse<Task>`: Single task response
- `ApiResponse<Task[]>`: Multiple tasks response
- `ApiError`: Error response from API
- `PaginatedResponse<Task>`: Paginated task list (future enhancement)

---

## Component State Types

### Task List State

```typescript
export interface TaskListState {
  tasks: Task[];
  loading: boolean;
  error: string | null;
}
```

### Task Statistics

```typescript
export interface TaskStats {
  total: number;
  completed: number;
  pending: number;
}
```

### Modal State

```typescript
export interface ModalState {
  isOpen: boolean;
  mode: 'create' | 'edit';
  task: Task | null;
}
```

---

## Data Flow

### Task Creation Flow

1. User fills form in AddTaskModal
2. Form data → `CreateTaskInput`
3. API client sends POST request
4. Backend returns `ApiResponse<Task>`
5. New task added to local state
6. UI updates to show new task

### Task Update Flow

1. User clicks edit button
2. Task data loaded into EditTaskModal
3. User modifies fields → `UpdateTaskInput`
4. API client sends PATCH request
5. Backend returns `ApiResponse<Task>`
6. Local state updated with modified task
7. UI updates to reflect changes

### Authentication Flow

1. User submits login form → `LoginInput`
2. API client sends POST request
3. Backend returns `AuthResponse`
4. AuthState updated with user and token
5. Token stored for future requests
6. UI redirects to dashboard

---

## Validation

### Client-Side Validation

**Task Title**:
- Required: true
- Min length: 1 character
- Max length: 200 characters
- Pattern: Non-empty after trim

**Task Description**:
- Required: false
- Max length: 1000 characters

**Email**:
- Required: true
- Pattern: Valid email format (RFC 5322)

**Password**:
- Required: true
- Min length: 8 characters
- Pattern: At least one uppercase, one lowercase, one number

**Name**:
- Required: true
- Min length: 2 characters
- Max length: 100 characters

---

## Notes

- All timestamps use ISO 8601 format (e.g., "2026-02-05T10:30:00Z")
- All IDs are strings (supports both UUID and integer IDs from backend)
- User ID is never sent from frontend - backend extracts from JWT
- All API responses follow consistent structure with `data` and optional `message`
- Error responses include `error`, `message`, and `statusCode` fields
- Frontend does not store passwords - only used during authentication
- Session persistence handled by auth system (httpOnly cookies or secure storage)
