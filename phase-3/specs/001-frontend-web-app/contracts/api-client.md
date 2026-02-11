# API Client Contract: Frontend Web Application

**Feature**: Frontend Web Application
**Branch**: 001-frontend-web-app
**Created**: 2026-02-05

## Overview

This document defines the API client interface for the frontend application. The centralized API client (`lib/api-client.ts`) provides a consistent interface for all backend communication, handles JWT attachment, error handling, and request/response transformation.

## Base Configuration

### API Client Setup

```typescript
// lib/api-client.ts

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface RequestConfig {
  method: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  headers?: Record<string, string>;
  body?: any;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  setToken(token: string | null) {
    this.token = token;
  }

  private async request<T>(endpoint: string, config: RequestConfig): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...config.headers,
    };

    // Attach JWT token if available
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: config.method,
      headers,
      body: config.body ? JSON.stringify(config.body) : undefined,
      credentials: 'include', // Include cookies for session persistence
    });

    if (!response.ok) {
      const error = await response.json();
      throw new ApiError(error.message, response.status, error);
    }

    return response.json();
  }

  // Public methods for each endpoint...
}

export const apiClient = new ApiClient(API_BASE_URL);
```

---

## Authentication Endpoints

### POST /auth/signup

**Purpose**: Create a new user account

**Request**:
```typescript
interface SignupRequest {
  name: string;
  email: string;
  password: string;
}
```

**Response**:
```typescript
interface SignupResponse {
  data: {
    user: User;
    token: string;
  };
  message: string;
}
```

**Client Method**:
```typescript
async signup(data: SignupInput): Promise<AuthResponse> {
  return this.request<ApiResponse<AuthResponse>>('/auth/signup', {
    method: 'POST',
    body: data,
  }).then(res => res.data);
}
```

**Error Responses**:
- 400: Validation error (invalid email, weak password, missing fields)
- 409: Email already exists
- 500: Server error

---

### POST /auth/login

**Purpose**: Authenticate user and receive JWT token

**Request**:
```typescript
interface LoginRequest {
  email: string;
  password: string;
}
```

**Response**:
```typescript
interface LoginResponse {
  data: {
    user: User;
    token: string;
  };
  message: string;
}
```

**Client Method**:
```typescript
async login(data: LoginInput): Promise<AuthResponse> {
  return this.request<ApiResponse<AuthResponse>>('/auth/login', {
    method: 'POST',
    body: data,
  }).then(res => res.data);
}
```

**Error Responses**:
- 400: Validation error (invalid email format, missing fields)
- 401: Invalid credentials
- 500: Server error

---

### POST /auth/logout

**Purpose**: Invalidate current session and clear authentication

**Request**: No body required (token in header)

**Response**:
```typescript
interface LogoutResponse {
  message: string;
}
```

**Client Method**:
```typescript
async logout(): Promise<void> {
  await this.request<ApiResponse<void>>('/auth/logout', {
    method: 'POST',
  });
  this.setToken(null);
}
```

**Error Responses**:
- 401: Not authenticated
- 500: Server error

---

### GET /auth/me

**Purpose**: Get current authenticated user's information

**Request**: No body required (token in header)

**Response**:
```typescript
interface MeResponse {
  data: User;
}
```

**Client Method**:
```typescript
async getCurrentUser(): Promise<User> {
  return this.request<ApiResponse<User>>('/auth/me', {
    method: 'GET',
  }).then(res => res.data);
}
```

**Error Responses**:
- 401: Not authenticated or invalid token
- 500: Server error

---

## Task Endpoints

### GET /tasks

**Purpose**: Retrieve all tasks for authenticated user

**Request**: No body required (token in header, user_id extracted from JWT)

**Response**:
```typescript
interface TasksResponse {
  data: Task[];
}
```

**Client Method**:
```typescript
async getTasks(): Promise<Task[]> {
  return this.request<ApiResponse<Task[]>>('/tasks', {
    method: 'GET',
  }).then(res => res.data);
}
```

**Error Responses**:
- 401: Not authenticated
- 500: Server error

---

### POST /tasks

**Purpose**: Create a new task for authenticated user

**Request**:
```typescript
interface CreateTaskRequest {
  title: string;
  description: string;
}
```

**Response**:
```typescript
interface CreateTaskResponse {
  data: Task;
  message: string;
}
```

**Client Method**:
```typescript
async createTask(data: CreateTaskInput): Promise<Task> {
  return this.request<ApiResponse<Task>>('/tasks', {
    method: 'POST',
    body: data,
  }).then(res => res.data);
}
```

**Error Responses**:
- 400: Validation error (title too long, missing required fields)
- 401: Not authenticated
- 422: Unprocessable entity (validation failed)
- 500: Server error

**Note**: `user_id` is NOT sent in request body. Backend extracts it from JWT claims.

---

### PATCH /tasks/:id

**Purpose**: Update an existing task

**Request**:
```typescript
interface UpdateTaskRequest {
  title?: string;
  description?: string;
  completed?: boolean;
}
```

**Response**:
```typescript
interface UpdateTaskResponse {
  data: Task;
  message: string;
}
```

**Client Method**:
```typescript
async updateTask(id: string, data: UpdateTaskInput): Promise<Task> {
  return this.request<ApiResponse<Task>>(`/tasks/${id}`, {
    method: 'PATCH',
    body: data,
  }).then(res => res.data);
}
```

**Error Responses**:
- 400: Validation error
- 401: Not authenticated
- 403: Forbidden (task belongs to different user)
- 404: Task not found
- 422: Unprocessable entity
- 500: Server error

---

### DELETE /tasks/:id

**Purpose**: Delete a task

**Request**: No body required (token in header)

**Response**:
```typescript
interface DeleteTaskResponse {
  message: string;
}
```

**Client Method**:
```typescript
async deleteTask(id: string): Promise<void> {
  await this.request<ApiResponse<void>>(`/tasks/${id}`, {
    method: 'DELETE',
  });
}
```

**Error Responses**:
- 401: Not authenticated
- 403: Forbidden (task belongs to different user)
- 404: Task not found
- 500: Server error

---

## Error Handling

### ApiError Class

```typescript
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}
```

### Error Response Format

All error responses follow this structure:

```typescript
interface ErrorResponse {
  error: string;           // Error type (e.g., "ValidationError", "AuthenticationError")
  message: string;         // Human-readable error message
  statusCode: number;      // HTTP status code
  details?: any;           // Additional error details (e.g., validation errors)
}
```

### Common HTTP Status Codes

- **200 OK**: Request succeeded
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required or invalid token
- **403 Forbidden**: Authenticated but not authorized for this resource
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation failed
- **500 Internal Server Error**: Server error

---

## Request/Response Flow

### Successful Request Flow

1. Component calls API client method (e.g., `apiClient.getTasks()`)
2. API client constructs request with:
   - Base URL + endpoint
   - HTTP method
   - Headers (Content-Type, Authorization with JWT)
   - Body (if applicable)
3. Fetch API sends request to backend
4. Backend processes request and returns response
5. API client parses JSON response
6. API client extracts `data` field and returns to component
7. Component updates state with response data

### Error Request Flow

1. Component calls API client method
2. API client sends request
3. Backend returns error response (4xx or 5xx)
4. API client detects `!response.ok`
5. API client parses error JSON
6. API client throws `ApiError` with message and status code
7. Component catches error and displays to user

---

## JWT Token Management

### Token Storage

- Token received from `/auth/login` or `/auth/signup`
- Stored in API client instance via `setToken(token)`
- Also stored in secure storage (implementation in auth spec)
- Automatically attached to all subsequent requests

### Token Attachment

```typescript
if (this.token) {
  headers['Authorization'] = `Bearer ${this.token}`;
}
```

### Token Refresh

- Token refresh logic will be implemented in authentication feature
- API client will support token refresh via interceptor pattern
- Expired tokens will trigger automatic refresh before retry

---

## Session Persistence

### Cookie-Based Sessions

```typescript
credentials: 'include'  // Include httpOnly cookies in requests
```

- Backend sets httpOnly cookie on login
- Browser automatically includes cookie in subsequent requests
- Cookie persists across page refreshes and browser sessions
- Cookie cleared on logout

---

## Usage Examples

### Authentication Example

```typescript
// Login
try {
  const { user, token } = await apiClient.login({
    email: 'user@example.com',
    password: 'password123'
  });

  apiClient.setToken(token);
  // Store token in secure storage
  // Update auth state
  // Redirect to dashboard
} catch (error) {
  if (error instanceof ApiError) {
    if (error.statusCode === 401) {
      // Show "Invalid credentials" message
    } else {
      // Show generic error message
    }
  }
}
```

### Task Management Example

```typescript
// Get all tasks
const tasks = await apiClient.getTasks();

// Create task
const newTask = await apiClient.createTask({
  title: 'Buy groceries',
  description: 'Milk, eggs, bread'
});

// Update task
const updatedTask = await apiClient.updateTask(taskId, {
  completed: true
});

// Delete task
await apiClient.deleteTask(taskId);
```

---

## Environment Variables

### Required Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Production Configuration

```bash
# .env.production
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api
```

---

## Notes

- All endpoints require JWT token except `/auth/signup` and `/auth/login`
- User ID is NEVER sent from frontend - backend extracts from JWT
- All requests include `credentials: 'include'` for cookie-based sessions
- API client is a singleton instance exported from `lib/api-client.ts`
- Error handling is centralized in the API client
- All responses follow consistent structure with `data` field
- TypeScript types ensure type safety across API boundaries
