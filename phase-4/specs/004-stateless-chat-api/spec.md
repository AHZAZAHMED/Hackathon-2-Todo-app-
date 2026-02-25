# Feature Specification: Stateless Chat API + OpenAI Agent Orchestration

**Feature Branch**: `004-stateless-chat-api`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "Phase-3 Spec-2 — Stateless Chat API + OpenAI Agent Orchestration"

## Overview

This specification defines the backend conversational API for the Todo AI Chatbot. The FastAPI server exposes a POST /api/chat endpoint that integrates Better Auth JWT authentication, conversation persistence, and OpenAI Agents SDK for AI-powered responses. The backend operates statelessly, loading conversation history from the database on each request and storing all messages persistently.

**Key Architectural Principles**:
- Stateless operation: No in-memory conversation state between requests
- Database-driven: All conversation history persisted in PostgreSQL
- Security-first: JWT verification on every request, user_id derived server-side only
- Agent orchestration: OpenAI Agents SDK handles AI logic, not direct database access

**Out of Scope**:
- MCP (Model Context Protocol) tool integration for task operations (covered in Spec-3)
- Real-time streaming responses
- Multi-modal capabilities (images, voice)
- Conversation branching or editing
- Agent memory beyond conversation history

## User Scenarios & Testing

### User Story 1 - Send Chat Message (Priority: P1)

As an authenticated user, I want to send a natural language message to the AI assistant and receive an intelligent response, so that I can interact with my todo application conversationally.

**Why this priority**: This is the core functionality - without the ability to send and receive messages, the chat feature has no value. This is the minimum viable product.

**Independent Test**: Can be fully tested by authenticating a user, sending a POST request to /api/chat with a message, and verifying that an AI-generated response is returned. Delivers immediate value by enabling basic conversational interaction.

**Acceptance Scenarios**:

1. **Given** a user is authenticated with a valid JWT token, **When** they send their first message "Hello", **Then** the system creates a new conversation, stores the user message, invokes the AI agent, stores the assistant response, and returns the response with a conversation_id
2. **Given** a user has an existing conversation, **When** they send a follow-up message with the conversation_id, **Then** the system loads the conversation history, appends the new message, invokes the AI agent with full context, stores the response, and returns it
3. **Given** a user sends a message without providing conversation_id, **When** the request is processed, **Then** the system automatically creates a new conversation for that user
4. **Given** a user sends a valid message, **When** the AI agent processes it, **Then** the response is contextually relevant and acknowledges the conversation history

---

### User Story 2 - Maintain Conversation Context (Priority: P2)

As a user engaging in a multi-turn conversation, I want the AI assistant to remember our previous exchanges, so that I can have coherent, contextual conversations without repeating myself.

**Why this priority**: Context awareness is essential for a useful conversational experience. Without it, each message would be treated in isolation, making the assistant frustrating to use. This builds on P1 to create a truly conversational experience.

**Independent Test**: Can be tested by sending multiple messages in sequence with the same conversation_id and verifying that later responses reference earlier messages. Delivers value by enabling natural, flowing conversations.

**Acceptance Scenarios**:

1. **Given** a user has sent "My name is John" in message 1, **When** they ask "What's my name?" in message 2, **Then** the assistant's response references "John" from the conversation history
2. **Given** a conversation has 10 previous messages, **When** a user sends message 11, **Then** the AI agent receives all 10 previous messages as context
3. **Given** a user has multiple conversations, **When** they send a message with conversation_id A, **Then** only the history from conversation A is loaded, not from other conversations
4. **Given** a conversation was started yesterday, **When** the user continues it today, **Then** the full conversation history is still available and used for context

---

### User Story 3 - Secure Access Control (Priority: P3)

As a system administrator, I want to ensure that only authenticated users can access the chat API and that users can only access their own conversations, so that user data remains private and secure.

**Why this priority**: Security is critical but builds on the core functionality. Users must be able to chat (P1) with context (P2) before security becomes the limiting factor. However, this must be implemented before production deployment.

**Independent Test**: Can be tested by attempting to access the chat endpoint without authentication (should fail with 401), with an invalid JWT (should fail with 401), and by attempting to access another user's conversation_id (should fail with 403 or return empty). Delivers value by ensuring data privacy and compliance.

**Acceptance Scenarios**:

1. **Given** a request is sent without a JWT token, **When** the /api/chat endpoint is called, **Then** the system returns 401 Unauthorized
2. **Given** a request is sent with an expired JWT token, **When** the /api/chat endpoint is called, **Then** the system returns 401 Unauthorized
3. **Given** a request is sent with a valid JWT for User A, **When** they provide a conversation_id belonging to User B, **Then** the system returns 403 Forbidden or treats it as a new conversation for User A
4. **Given** a valid JWT token, **When** the backend processes the request, **Then** the user_id is extracted from the JWT claims only, never from the request body or query parameters

---

### User Story 4 - Stateless Backend Operation (Priority: P4)

As a DevOps engineer, I want the backend to operate statelessly without storing conversation data in memory, so that the application can scale horizontally and recover gracefully from server restarts.

**Why this priority**: Stateless operation is an architectural requirement that enables scalability and reliability. While important for production, it doesn't directly impact user-facing functionality. This can be validated after core features work.

**Independent Test**: Can be tested by sending a message, restarting the backend server, and verifying that the conversation can continue seamlessly. Delivers value by enabling horizontal scaling and fault tolerance.

**Acceptance Scenarios**:

1. **Given** a user sends message 1 and receives a response, **When** the backend server is restarted, **Then** the user can send message 2 with the same conversation_id and the full history is still available
2. **Given** multiple backend instances are running behind a load balancer, **When** a user's requests are routed to different instances, **Then** each instance loads the conversation from the database and provides consistent responses
3. **Given** a conversation is in progress, **When** the backend processes a request, **Then** no conversation state is stored in server memory (all state is in the database)
4. **Given** a high-traffic scenario, **When** new backend instances are added, **Then** they can immediately serve requests without any state synchronization

---

### Edge Cases

- **Empty message**: What happens when a user sends an empty string or whitespace-only message?
  - System should return 422 Unprocessable Entity with a clear error message
- **Very long message**: What happens when a message exceeds reasonable length (e.g., 10,000 characters)?
  - System should enforce a maximum message length (suggested: 2000 characters) and return 422 if exceeded
- **Invalid conversation_id**: What happens when a user provides a conversation_id that doesn't exist or belongs to another user?
  - System should create a new conversation silently and return success with the new conversation_id. This provides a forgiving user experience and handles stale/incorrect conversation_ids gracefully.
- **AI service unavailable**: What happens when the OpenAI API is down or rate-limited?
  - System should return 503 Service Unavailable with a user-friendly message and not store a partial/failed assistant message
- **Database connection failure**: What happens when the database is unreachable?
  - System should return 500 Internal Server Error and log the error for monitoring
- **Concurrent requests**: What happens when a user sends multiple messages to the same conversation simultaneously?
  - System should handle this gracefully using database transactions with Read Committed isolation level and explicit row locking (SELECT FOR UPDATE) on the conversation to ensure proper message ordering
- **Token expiry during request**: What happens when a JWT expires while a request is being processed?
  - System should validate JWT at the start of the request; if valid then, the request proceeds even if it expires during processing
- **Malformed JWT**: What happens when a JWT is syntactically invalid?
  - System should return 401 Unauthorized with a clear error message
- **Conversation history too large**: What happens when a conversation has hundreds of messages?
  - System should load the last 50 messages only to stay within AI context window limits. This ensures predictable performance and avoids API errors while maintaining sufficient context for most conversations.

## Requirements

### Functional Requirements

- **FR-001**: System MUST implement POST /api/chat endpoint that accepts JSON requests with message and optional conversation_id
- **FR-002**: System MUST validate JWT token on every request using Better Auth verification
- **FR-003**: System MUST extract user_id from JWT claims only, never accepting user_id from request body or query parameters
- **FR-004**: System MUST automatically create a new conversation if conversation_id is not provided or is invalid
- **FR-005**: System MUST persist user messages to the database before invoking the AI agent
- **FR-006**: System MUST persist assistant responses to the database after receiving them from the AI agent
- **FR-007**: System MUST use OpenAI Agents SDK for all AI logic and response generation
- **FR-008**: System MUST load the last 50 messages from conversation history and provide them to the AI agent for context
- **FR-009**: System MUST operate statelessly, storing no conversation data in server memory between requests
- **FR-010**: System MUST return user-friendly error messages for all error scenarios (401, 403, 422, 500, 503)
- **FR-011**: System MUST validate message length and reject messages exceeding 2000 characters with 422 error
- **FR-012**: System MUST validate message is non-empty and reject empty/whitespace-only messages with 422 error
- **FR-013**: System MUST ensure conversation isolation - users can only access their own conversations
- **FR-014**: System MUST handle database transaction failures gracefully and rollback partial changes
- **FR-015**: System MUST log all errors with sufficient context for debugging without exposing sensitive data to users. Logs should use structured format (JSON) and include: request_id, user_id (hashed), endpoint, error type, stack trace. Logs MUST exclude: JWT tokens, message content, passwords.

### Key Entities

- **Conversation**: Represents a chat session between a user and the AI assistant
  - id: Unique identifier for the conversation
  - user_id: Foreign key to the user who owns this conversation (from Better Auth user table)
  - title: Optional human-readable title (can be auto-generated from first message or left null)
  - created_at: Timestamp when conversation was created
  - updated_at: Timestamp when conversation was last modified

- **Message**: Represents a single message within a conversation
  - id: Unique identifier for the message
  - conversation_id: Foreign key to the conversation this message belongs to
  - role: Enum indicating message sender ('user' or 'assistant')
  - content: The actual message text
  - created_at: Timestamp when message was created
  - metadata: Optional JSON field for storing additional data (e.g., token count, model version)

**Entity Relationships**:
- One User has many Conversations (1:N)
- One Conversation has many Messages (1:N)
- Messages are ordered chronologically within a Conversation

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can send a message and receive an AI response in under 5 seconds for 95% of requests
- **SC-002**: System successfully handles 100 concurrent chat requests without errors or degradation
- **SC-003**: Conversation history is preserved across server restarts with 100% accuracy
- **SC-004**: Zero unauthorized access attempts succeed (100% of requests without valid JWT are rejected)
- **SC-005**: Users can continue conversations with full context after any time interval (minutes, hours, or days)
- **SC-006**: System maintains 99.9% uptime for the chat endpoint (excluding planned maintenance)
- **SC-007**: All error scenarios return appropriate HTTP status codes and user-friendly messages
- **SC-008**: Backend instances can be scaled horizontally without any state synchronization issues
- **SC-009**: 100% of user messages and assistant responses are persisted to the database
- **SC-010**: AI responses are contextually relevant to conversation history in 90% of multi-turn conversations (measured by user satisfaction or manual review)

## API Contract

### POST /api/chat

**Endpoint**: `/api/chat`
**Method**: POST
**Authentication**: Required (JWT Bearer token)

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "conversation_id": "uuid-string",  // Optional: omit for new conversation
  "message": "string"                // Required: user's message (1-2000 chars)
}
```

**Success Response (200 OK)**:
```json
{
  "conversation_id": "uuid-string",
  "response": "string",
  "timestamp": "ISO-8601 datetime"
}
```

**Error Responses**:

- **401 Unauthorized**: Missing, invalid, or expired JWT token
  ```json
  {
    "error": "Unauthorized",
    "message": "Valid authentication required"
  }
  ```

- **403 Forbidden**: User attempting to access another user's conversation
  ```json
  {
    "error": "Forbidden",
    "message": "You do not have access to this conversation"
  }
  ```

- **422 Unprocessable Entity**: Invalid request data (empty message, too long, etc.)
  ```json
  {
    "error": "Validation Error",
    "message": "Message must be between 1 and 2000 characters"
  }
  ```

- **500 Internal Server Error**: Database or server error
  ```json
  {
    "error": "Internal Server Error",
    "message": "An unexpected error occurred. Please try again."
  }
  ```

- **503 Service Unavailable**: AI service unavailable
  ```json
  {
    "error": "Service Unavailable",
    "message": "AI service is temporarily unavailable. Please try again later."
  }
  ```

## Assumptions

1. **OpenAI Agents SDK**: We assume the OpenAI Agents SDK is available and compatible with the FastAPI backend. The specific model (GPT-4, GPT-3.5, etc.) will be configured via environment variables.

2. **Database Schema**: We assume the database schema for conversations and messages tables will be created via migration scripts before this feature is deployed.

3. **Better Auth Integration**: We assume Better Auth is already configured and provides JWT verification utilities that can be imported and used in FastAPI dependencies.

4. **Message Length**: We assume 2000 characters is a reasonable maximum message length that balances user needs with API costs and performance.

5. **Conversation History**: We assume loading the full conversation history is acceptable for initial implementation. If conversations grow very large, pagination or truncation strategies can be added later.

6. **Error Handling**: We assume user-friendly error messages are sufficient and detailed error logs are captured server-side for debugging.

7. **Conversation Title**: We assume conversation titles are optional and can be auto-generated from the first message or left null. Title generation is not a core requirement.

8. **Rate Limiting**: We assume rate limiting will be handled at the infrastructure level (API gateway, load balancer) rather than in the application code.

9. **AI Response Time**: We assume the OpenAI API typically responds within 3-5 seconds, allowing us to meet the 5-second success criterion for 95% of requests.

10. **Concurrent Requests**: We assume the database supports proper transaction isolation to handle concurrent requests to the same conversation.

## Dependencies

- **Better Auth**: JWT verification and user authentication
- **OpenAI Agents SDK**: AI response generation
- **PostgreSQL Database**: Conversation and message persistence
- **FastAPI**: Web framework for the backend API
- **SQLModel**: ORM for database operations (as per Phase-2 architecture)

## Non-Functional Requirements

- **Performance**: Response time under 5 seconds for 95% of requests
- **Scalability**: Support horizontal scaling without state synchronization
- **Reliability**: 99.9% uptime for the chat endpoint
- **Security**: JWT verification on every request, user isolation enforced
- **Maintainability**: Stateless architecture for easier debugging and deployment
- **Observability**: Comprehensive error logging using structured format (JSON) with sanitized context (request_id, hashed user_id, endpoint, error type, stack trace) while excluding sensitive data (JWT tokens, message content, passwords)

## Future Enhancements (Out of Scope)

- Real-time streaming responses (Server-Sent Events or WebSockets)
- Conversation branching and editing
- Multi-modal support (images, voice, file attachments)
- Advanced agent memory beyond conversation history
- Conversation search and filtering
- Conversation export and sharing
- Agent personality customization
- Multi-language support
- Voice input/output integration

---

## Clarifications

### Session 2026-02-09

- Q: Which behavior should the system implement when a user provides an invalid or non-existent conversation_id? → A: Create a new conversation silently and return success with the new conversation_id (forgiving approach)
- Q: What transaction isolation level should be used to handle concurrent message requests to the same conversation? → A: Read Committed with explicit row locking on conversation (balanced approach, standard for web apps)
- Q: What specific information should be included in error logs to balance debugging capability with security/privacy? → A: Structured logging with sanitized context: request_id, user_id (hashed), endpoint, error type, stack trace, but exclude JWT tokens, message content, passwords (balanced approach, industry standard)

---

**Next Steps**: Run `/sp.clarify` to resolve any unclear requirements, then `/sp.plan` to generate the implementation plan.
