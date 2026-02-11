# API Contract: POST /api/chat

**Feature**: 004-stateless-chat-api
**Date**: 2026-02-09
**Status**: Complete

## Overview

This document defines the complete API contract for the chat endpoint, including request/response formats, authentication requirements, error handling, and usage examples.

---

## Endpoint Specification

### POST /api/chat

**Purpose**: Send a message to the AI assistant and receive a response with full conversation context.

**URL**: `/api/chat`
**Method**: `POST`
**Authentication**: Required (JWT Bearer token)
**Content-Type**: `application/json`

---

## Authentication

### Required Headers

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**JWT Token Requirements**:
- Issued by Better Auth
- Algorithm: HS256
- Must contain `sub` or `user_id` claim
- Must not be expired
- Must have valid signature

**Authentication Flow**:
1. Frontend obtains JWT from Better Auth on login
2. Frontend includes JWT in Authorization header for all chat requests
3. Backend verifies JWT signature using BETTER_AUTH_SECRET
4. Backend extracts user_id from JWT claims
5. Backend uses user_id for conversation isolation

---

## Request Schema

### Request Body

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Hello, can you help me with my tasks?"
}
```

### Request Fields

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| conversation_id | UUID string | No | Valid UUID format | Existing conversation ID. Omit to start new conversation. |
| message | string | Yes | 1-2000 characters, non-empty | User's message to the AI assistant |

### Request Validation Rules

1. **message field**:
   - MUST be present in request body
   - MUST NOT be empty or whitespace-only
   - MUST be between 1 and 2000 characters
   - Whitespace is trimmed before validation

2. **conversation_id field**:
   - Optional (can be omitted or null)
   - If provided, MUST be valid UUID format
   - If invalid or doesn't exist, new conversation is created silently
   - If belongs to another user, new conversation is created silently (forgiving approach)

### Request Examples

**Example 1: Start new conversation**
```http
POST /api/chat HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "message": "Hello! What can you help me with?"
}
```

**Example 2: Continue existing conversation**
```http
POST /api/chat HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Can you remind me what we discussed earlier?"
}
```

---

## Response Schema

### Success Response (200 OK)

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "Hello! I'm your AI assistant for the todo application. I can help you manage your tasks, answer questions, and provide assistance. What would you like to do?",
  "timestamp": "2026-02-09T10:30:45.123Z"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| conversation_id | UUID string | The conversation ID (new or existing) |
| response | string | AI assistant's response message |
| timestamp | ISO-8601 datetime | When the response was generated |

### Response Characteristics

- **conversation_id**: Always returned, even for new conversations
- **response**: Contains the AI-generated text response
- **timestamp**: Server-side timestamp in UTC
- **Content-Type**: `application/json`
- **Status Code**: `200 OK`

---

## Error Responses

### 401 Unauthorized

**Trigger**: Missing, invalid, or expired JWT token

**Response**:
```json
{
  "error": "Unauthorized",
  "message": "Valid authentication required"
}
```

**HTTP Status**: `401 Unauthorized`

**Scenarios**:
- No Authorization header provided
- JWT token is malformed or invalid
- JWT token has expired
- JWT signature verification fails
- JWT missing user_id claim

---

### 422 Unprocessable Entity

**Trigger**: Invalid request data (validation failure)

**Response Examples**:

**Empty message**:
```json
{
  "error": "Validation Error",
  "message": "Message cannot be empty"
}
```

**Message too long**:
```json
{
  "error": "Validation Error",
  "message": "Message must be between 1 and 2000 characters"
}
```

**Missing message field**:
```json
{
  "error": "Validation Error",
  "message": "Message field is required"
}
```

**HTTP Status**: `422 Unprocessable Entity`

**Scenarios**:
- Message field missing from request body
- Message is empty or whitespace-only
- Message exceeds 2000 characters
- Invalid JSON in request body

---

### 500 Internal Server Error

**Trigger**: Database error or unexpected server error

**Response**:
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred. Please try again."
}
```

**HTTP Status**: `500 Internal Server Error`

**Scenarios**:
- Database connection failure
- Database query error
- Unexpected exception in server code
- Message persistence failure

**Note**: Detailed error information is logged server-side but not exposed to client for security reasons.

---

### 503 Service Unavailable

**Trigger**: AI service (OpenRouter) unavailable or rate-limited

**Response**:
```json
{
  "error": "Service Unavailable",
  "message": "AI service is temporarily unavailable. Please try again later."
}
```

**HTTP Status**: `503 Service Unavailable`

**Scenarios**:
- OpenRouter API is down
- OpenRouter API rate limit exceeded
- Network timeout connecting to OpenRouter
- OpenRouter API returns error response

**Retry Strategy**: Client should implement exponential backoff for 503 errors.

---

## Request Flow

### Successful Request Flow

```
1. Client sends POST /api/chat with JWT and message
2. Backend verifies JWT and extracts user_id
3. Backend validates message (length, non-empty)
4. Backend checks if conversation_id provided:
   - If yes: Load conversation (or create new if invalid)
   - If no: Create new conversation
5. Backend loads last 50 messages from conversation
6. Backend stores user message in database
7. Backend builds message array for AI agent
8. Backend invokes OpenAI Agent via OpenRouter
9. Backend receives AI response
10. Backend stores assistant message in database
11. Backend returns response with conversation_id
```

### Error Flow Examples

**Invalid JWT**:
```
1. Client sends POST /api/chat with invalid JWT
2. Backend attempts JWT verification
3. JWT verification fails
4. Backend returns 401 Unauthorized
5. Client redirects to login page
```

**AI Service Down**:
```
1. Client sends POST /api/chat with valid JWT
2. Backend verifies JWT successfully
3. Backend stores user message
4. Backend attempts to call OpenRouter API
5. OpenRouter API connection fails
6. Backend catches exception
7. Backend returns 503 Service Unavailable
8. Client displays error message with retry option
```

---

## Performance Characteristics

### Response Time

- **Target**: < 5 seconds for 95% of requests
- **Typical**: 2-4 seconds (includes AI generation time)
- **Factors**:
  - Database query time: ~50-100ms
  - OpenRouter API call: 1-3 seconds
  - Message persistence: ~50-100ms

### Concurrency

- **Supported**: 100 concurrent requests
- **Connection Pool**: 10 connections, 20 overflow
- **Rate Limiting**: Handled at infrastructure level (not in application)

### Payload Limits

- **Request Body**: Max 10KB (enforced by FastAPI)
- **Message Content**: Max 2000 characters (enforced by validation)
- **Response Body**: Typically 500-2000 characters

---

## Security Considerations

### Authentication

- JWT verification on every request (no session caching)
- User ID extracted from JWT claims only (never from request body)
- Expired tokens rejected immediately

### Authorization

- Users can only access their own conversations
- Conversation ownership verified before loading messages
- Invalid conversation_id creates new conversation (prevents enumeration attacks)

### Data Protection

- Message content stored in database (encrypted at rest by Neon)
- JWT tokens not logged
- User messages not logged (only metadata)
- Error messages sanitized (no sensitive data exposed)

### Input Validation

- Message length validated (prevents DoS via large payloads)
- JSON schema validation (prevents malformed requests)
- SQL injection prevented (parameterized queries via SQLModel)

---

## Usage Examples

### Example 1: Complete Conversation Flow

**Request 1: Start conversation**
```bash
curl -X POST https://api.example.com/api/chat \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Can you help me organize my tasks?"
  }'
```

**Response 1**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "Hello! I'd be happy to help you organize your tasks. What would you like to work on?",
  "timestamp": "2026-02-09T10:00:00.000Z"
}
```

**Request 2: Continue conversation**
```bash
curl -X POST https://api.example.com/api/chat \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "I need to prioritize my work tasks for this week."
  }'
```

**Response 2**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "Great! Let's prioritize your work tasks. Can you tell me what tasks you have for this week?",
  "timestamp": "2026-02-09T10:01:30.000Z"
}
```

---

### Example 2: Error Handling

**Request with expired token**:
```bash
curl -X POST https://api.example.com/api/chat \
  -H "Authorization: Bearer expired_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello"
  }'
```

**Response**:
```json
{
  "error": "Unauthorized",
  "message": "Token expired"
}
```
**HTTP Status**: 401

---

**Request with empty message**:
```bash
curl -X POST https://api.example.com/api/chat \
  -H "Authorization: Bearer valid_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "   "
  }'
```

**Response**:
```json
{
  "error": "Validation Error",
  "message": "Message cannot be empty"
}
```
**HTTP Status**: 422

---

## Testing Checklist

### Functional Tests

- [ ] Send message without conversation_id (creates new conversation)
- [ ] Send message with valid conversation_id (continues conversation)
- [ ] Send message with invalid conversation_id (creates new conversation)
- [ ] Verify conversation history loaded (last 50 messages)
- [ ] Verify user isolation (cannot access other user's conversations)

### Authentication Tests

- [ ] Request without Authorization header (returns 401)
- [ ] Request with invalid JWT (returns 401)
- [ ] Request with expired JWT (returns 401)
- [ ] Request with valid JWT (returns 200)

### Validation Tests

- [ ] Empty message (returns 422)
- [ ] Message with only whitespace (returns 422)
- [ ] Message exceeding 2000 characters (returns 422)
- [ ] Valid message (returns 200)

### Error Handling Tests

- [ ] Database connection failure (returns 500)
- [ ] OpenRouter API failure (returns 503)
- [ ] Malformed JSON request (returns 422)

### Performance Tests

- [ ] Response time < 5 seconds for 95% of requests
- [ ] 100 concurrent requests handled successfully
- [ ] No memory leaks after 1000 requests

---

**Status**: ✅ API contract complete. Ready for quickstart guide.
