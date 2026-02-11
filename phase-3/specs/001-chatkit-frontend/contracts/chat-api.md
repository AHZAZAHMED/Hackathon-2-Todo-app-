# API Contract: Chat Endpoint

**Feature**: 001-chatkit-frontend
**Date**: 2026-02-09
**Endpoint**: POST /api/chat
**Scope**: Frontend contract definition (backend implementation out of scope)

## Overview

This document defines the API contract for the chat endpoint that the frontend will communicate with. The backend implementation is out of scope for this spec but will be implemented in a separate Phase-3 backend spec.

---

## Endpoint: POST /api/chat

Send a user message to the AI assistant and receive a response.

### Request

**Method**: `POST`
**Path**: `/api/chat`
**Content-Type**: `application/json`

#### Headers

| Header | Required | Value | Description |
|--------|----------|-------|-------------|
| `Authorization` | Yes | `Bearer <JWT>` | Better Auth JWT token for user authentication |
| `Content-Type` | Yes | `application/json` | Request body format |

#### Body

```json
{
  "message": "string"
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `message` | string | Yes | 1-500 characters | User's message to the AI assistant |

#### Example Request

```http
POST /api/chat HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "message": "Can you help me create a new task?"
}
```

### Response

#### Success Response (200 OK)

**Content-Type**: `application/json`

```json
{
  "response": "string"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `response` | string | AI assistant's response message |

**Example**:

```json
{
  "response": "Of course! I can help you create a new task. What would you like the task to be?"
}
```

#### Error Responses

##### 401 Unauthorized

JWT token is missing, invalid, or expired.

```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired authentication token"
}
```

**Frontend Handling**:
- Preserve conversation in session storage (FR-021)
- Redirect to login page (FR-014)
- Restore conversation after re-authentication (FR-022)

##### 422 Unprocessable Entity

Request validation failed (e.g., message too long, missing fields).

```json
{
  "error": "Validation Error",
  "message": "Message must be between 1 and 500 characters"
}
```

**Frontend Handling**:
- Display user-friendly error message
- Do not mark message as failed (validation should prevent this)

##### 500 Internal Server Error

Backend processing error.

```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
```

**Frontend Handling**:
- Display user-friendly error: "Server error. Please try again."
- Mark message as failed with retry button (FR-023, FR-024)

##### 503 Service Unavailable

Backend service is temporarily unavailable.

```json
{
  "error": "Service Unavailable",
  "message": "Service is temporarily unavailable"
}
```

**Frontend Handling**:
- Display user-friendly error: "Service unavailable. Please try again later."
- Mark message as failed with retry button (FR-023, FR-024)

---

## Authentication Flow

### JWT Token Extraction

The frontend uses the existing Phase-2 centralized API client (`lib/api-client.ts`) which automatically:

1. Extracts JWT token from Better Auth session
2. Attaches token to `Authorization` header
3. Handles token refresh if needed

### Token Expiry Handling

When backend returns 401:

1. Frontend detects 401 response
2. Saves current conversation to session storage
3. Redirects user to login page
4. After successful re-authentication:
   - Returns user to original page
   - Restores conversation from session storage
   - Opens chat window automatically

---

## Request/Response Examples

### Example 1: Simple Question

**Request**:
```json
{
  "message": "What tasks do I have today?"
}
```

**Response**:
```json
{
  "response": "Let me check your tasks for today. You have 3 tasks: 1) Complete project proposal, 2) Review pull request, 3) Team meeting at 2pm."
}
```

### Example 2: Task Creation

**Request**:
```json
{
  "message": "Create a task to buy groceries"
}
```

**Response**:
```json
{
  "response": "I've created a new task: 'Buy groceries'. Would you like to add any details or set a due date?"
}
```

### Example 3: Error - Token Expired

**Request**:
```json
{
  "message": "Show my tasks"
}
```

**Response** (401):
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired authentication token"
}
```

**Frontend Action**: Redirect to login, preserve conversation

---

## Performance Expectations

| Metric | Target | Measurement |
|--------|--------|-------------|
| Response Time (p50) | < 1 second | Time from request to response |
| Response Time (p95) | < 3 seconds | 95th percentile response time |
| Timeout | 30 seconds | Frontend request timeout |
| Rate Limit | 10 req/min | Client-side rate limiting (FR-220 security consideration) |

---

## Security Considerations

### JWT Token Security

- **Transmission**: HTTPS only in production
- **Storage**: Managed by Better Auth (httpOnly cookies or secure storage)
- **Exposure**: Never log JWT tokens in client-side console or error messages
- **Validation**: Backend must verify JWT signature and expiry

### Input Validation

- **Client-Side**: Enforce 500 character limit (FR-018, FR-019, FR-020)
- **Server-Side**: Backend should also validate (defense in depth)
- **Sanitization**: Backend must sanitize input to prevent injection attacks

### XSS Prevention

- **User Input**: All user messages must be sanitized before rendering
- **AI Responses**: All assistant responses must be sanitized before rendering
- **React**: Use React's built-in XSS protection (avoid dangerouslySetInnerHTML)

---

## Error Handling Strategy

### Network Errors

**Scenario**: Request fails due to network issues (no response from backend)

**Frontend Handling**:
```typescript
try {
  const response = await sendChatMessage(message);
  // Handle success
} catch (error) {
  if (!navigator.onLine) {
    // No internet connection
    displayError("No internet connection. Please check your network.");
  } else {
    // Network error
    displayError("Unable to connect to chat service. Please try again later.");
  }
  markMessageAsFailed(messageId);
}
```

### Timeout Errors

**Scenario**: Request takes longer than 30 seconds

**Frontend Handling**:
```typescript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 30000);

try {
  const response = await fetch('/api/chat', {
    signal: controller.signal,
    // ... other options
  });
} catch (error) {
  if (error.name === 'AbortError') {
    displayError("Request timed out. Please try again.");
    markMessageAsFailed(messageId);
  }
} finally {
  clearTimeout(timeoutId);
}
```

---

## Mock Response (Development)

For frontend development before backend is ready:

```typescript
// lib/chat-client.ts (development mode)
export async function sendChatMessage(message: string): Promise<string> {
  if (process.env.NODE_ENV === 'development' && !process.env.NEXT_PUBLIC_API_BASE_URL) {
    // Mock response for development
    await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate network delay
    return `Mock response to: "${message}"`;
  }

  // Real implementation
  const response = await apiClient.post('/api/chat', { message });
  return response.data.response;
}
```

---

## Future Considerations (Out of Scope)

The following are **NOT** included in this spec:

- **Streaming Responses**: Real-time streaming of AI responses (WebSocket/SSE)
- **Conversation History**: Loading previous conversations from backend
- **Multi-Turn Context**: Backend maintaining conversation context across requests
- **File Attachments**: Uploading files with messages
- **Rich Content**: Markdown rendering, code syntax highlighting
- **Typing Indicators**: Real-time indication that AI is typing

---

## Summary

- **Endpoint**: POST /api/chat
- **Authentication**: JWT Bearer token (Better Auth)
- **Request**: `{ message: string }`
- **Response**: `{ response: string }`
- **Error Codes**: 401 (auth), 422 (validation), 500 (server), 503 (unavailable)
- **Frontend Handling**: Retry mechanism, token expiry preservation, user-friendly errors
- **Security**: HTTPS, JWT validation, input sanitization, XSS prevention
