# Feature Specification: Backend Chat API + OpenAI Agent Orchestration

**Feature Branch**: `006-backend-chat-api`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Backend Chat API + OpenAI Agent Orchestration using third party free LLM (Gemini 2.0 Flash)"

## Context

This specification defines the backend conversational API that powers the Phase-3 ChatKit frontend. The system exposes a POST /api/chat endpoint that authenticates users via Better Auth JWT, manages conversation history, and orchestrates an AI agent using OpenAI Agents SDK with Gemini 2.0 Flash (free LLM). The agent can invoke MCP tools to perform task management operations (CRUD) on behalf of users.

**Architecture Overview:**
- **Frontend**: ChatKit UI (already implemented in 004-chatbot-frontend) sends chat messages
- **Backend API**: FastAPI endpoint receives messages, verifies JWT, manages conversations
- **AI Agent**: OpenAI Agents SDK configured with Gemini 2.0 Flash model
- **MCP Tools**: Task management tools (add, list, complete, delete, update) invoked by agent
- **Database**: PostgreSQL stores conversations and messages for context persistence

**Key Technical Approach:**
The backend uses OpenAI Agents SDK with a custom AsyncOpenAI client configured to use Google's Gemini API endpoint instead of OpenAI's API. This allows using the free Gemini 2.0 Flash model while maintaining compatibility with the OpenAI Agents SDK interface.

**Stateless Architecture:**
The backend is stateless - all conversation state persists in the database. Each request loads conversation history, invokes the agent, stores the response, and returns. The frontend can optionally provide conversation_id for continuity, or the backend auto-creates a new conversation on first message.

## User Scenarios & Testing

### User Story 1 - Send Chat Message and Receive AI Response (Priority: P1) 🎯 MVP

As an authenticated user, I want to send a message to the chat API and receive an AI-generated response so I can interact with my todo application conversationally.

**Why this priority**: This is the core functionality - without it, the chat feature doesn't work. This story delivers immediate value by enabling basic conversational interaction.

**Independent Test**: Send a POST request to /api/chat with a valid JWT and message. Verify the API returns a response from the AI agent. This can be tested with a simple curl command or Postman without needing the full frontend.

**Acceptance Scenarios**:

1. **Given** user is authenticated with valid JWT, **When** user sends message "Hello", **Then** API returns 200 with AI response and conversation_id
2. **Given** user is authenticated, **When** user sends first message, **Then** backend auto-creates new conversation and returns conversation_id
3. **Given** user has existing conversation, **When** user sends message with conversation_id, **Then** API loads conversation history and returns contextual response
4. **Given** user sends message, **When** AI agent processes request, **Then** response is returned within 5 seconds

---

### User Story 2 - Maintain Conversation Context (Priority: P1) 🎯 MVP

As a user, I want my conversation history to be remembered across multiple messages so the AI can provide contextual responses based on our previous interactions.

**Why this priority**: Without conversation context, the AI cannot provide meaningful assistance. Each message would be treated in isolation, making the chat experience poor and unusable for task management.

**Independent Test**: Send multiple messages in sequence with the same conversation_id. Verify the AI's responses reference previous messages in the conversation. For example, send "Add a task to buy milk" followed by "Mark it as complete" - the second message should work without re-specifying which task.

**Acceptance Scenarios**:

1. **Given** user has sent previous messages, **When** user sends new message with conversation_id, **Then** AI response demonstrates awareness of conversation history
2. **Given** conversation has 50 messages, **When** user sends new message, **Then** backend loads last 2000 tokens of history for context
3. **Given** user references "the task I just created", **When** AI processes message, **Then** AI correctly identifies the task from conversation history
4. **Given** conversation history is loaded, **When** AI generates response, **Then** response is contextually relevant to previous exchanges

---

### User Story 3 - AI Agent Invokes MCP Tools for Task Operations (Priority: P1) 🎯 MVP

As a user, I want the AI agent to perform task management operations (create, list, update, complete, delete tasks) when I ask it to, so I can manage my todos through natural conversation.

**Why this priority**: This is the primary value proposition - conversational task management. Without MCP tool integration, the AI can only chat but cannot actually help manage tasks.

**Independent Test**: Send a message like "Add a task to buy groceries". Verify the AI agent invokes the add_task MCP tool and a new task appears in the database. Check that the response includes tool_calls array showing which tools were invoked.

**Acceptance Scenarios**:

1. **Given** user says "Add a task to buy milk", **When** AI agent processes request, **Then** agent invokes add_task MCP tool with user_id, title, and description
2. **Given** user says "Show me my tasks", **When** AI agent processes request, **Then** agent invokes list_tasks MCP tool and returns formatted task list
3. **Given** user says "Mark the milk task as done", **When** AI agent processes request, **Then** agent invokes complete_task MCP tool with correct task_id
4. **Given** user says "Delete the milk task", **When** AI agent processes request, **Then** agent invokes delete_task MCP tool
5. **Given** user says "Change the milk task to buy bread", **When** AI agent processes request, **Then** agent invokes update_task MCP tool with new title
6. **Given** MCP tool executes successfully, **When** response is returned, **Then** response includes tool_calls array with tool name and result

---

### User Story 4 - Handle Authentication and Authorization (Priority: P2)

As a system, I must verify user identity via JWT and ensure users can only access their own conversations and tasks, so user data remains secure and isolated.

**Why this priority**: Security is critical but this is P2 because the JWT verification infrastructure already exists from Phase-2. This story ensures it's properly integrated into the chat endpoint.

**Independent Test**: Send a request without JWT - verify 401 response. Send a request with invalid JWT - verify 401 response. Send a request with valid JWT for User A trying to access User B's conversation_id - verify 403 response or conversation not found.

**Acceptance Scenarios**:

1. **Given** request has no JWT token, **When** request reaches /api/chat, **Then** API returns 401 Unauthorized
2. **Given** request has invalid/expired JWT, **When** request reaches /api/chat, **Then** API returns 401 Unauthorized with clear error message
3. **Given** request has valid JWT, **When** backend processes request, **Then** user_id is extracted from JWT claims (not from request body)
4. **Given** user_id is extracted, **When** MCP tools are invoked, **Then** user_id is passed to tools to ensure user isolation
5. **Given** user tries to access another user's conversation_id, **When** backend validates ownership, **Then** API returns 403 Forbidden or treats as new conversation

---

### User Story 5 - Handle Errors Gracefully (Priority: P2)

As a user, I want clear, user-friendly error messages when something goes wrong (authentication fails, AI agent errors, MCP tool failures) so I understand what happened and can take appropriate action.

**Why this priority**: Good error handling improves user experience but is P2 because basic functionality (P1 stories) must work first. Error handling can be refined after core features are validated.

**Independent Test**: Trigger various error conditions (invalid JWT, Gemini API down, MCP tool failure) and verify the API returns appropriate HTTP status codes with user-friendly error messages that appear in the chat UI.

**Acceptance Scenarios**:

1. **Given** JWT is invalid, **When** request is processed, **Then** API returns 401 with message "Authentication failed. Please log in again."
2. **Given** Gemini API is unavailable, **When** agent tries to generate response, **Then** API returns 503 with message "AI service temporarily unavailable. Please try again."
3. **Given** MCP tool fails (e.g., database error), **When** agent invokes tool, **Then** API returns 500 with message "Unable to complete task operation. Please try again."
4. **Given** request payload is malformed, **When** API validates request, **Then** API returns 422 with message describing what's wrong
5. **Given** conversation_id doesn't exist, **When** user provides it, **Then** backend treats as new conversation (graceful fallback)
6. **Given** any error occurs, **When** error is returned, **Then** error message is safe for display in chat UI (no stack traces or sensitive data)

---

### Edge Cases

- **What happens when conversation history exceeds 2000 tokens?** Backend loads only the most recent 2000 tokens. Older messages are still stored in database but not included in agent context.
- **What happens when user sends very long message (>10,000 characters)?** API validates message length and returns 422 error if too long.
- **What happens when Gemini API rate limit is hit?** API returns 429 Too Many Requests with retry-after header.
- **What happens when MCP tool returns error?** Agent receives error result and formulates user-friendly response explaining the failure.
- **What happens when user_id from JWT doesn't exist in database?** Backend treats as valid (user exists in auth system) and creates conversation normally.
- **What happens when multiple requests arrive simultaneously for same conversation?** Database handles concurrency - messages are appended in order received.
- **What happens when conversation_id is provided but belongs to different user?** Backend either returns 403 Forbidden or treats as new conversation (implementation choice for security).
- **What happens when agent takes longer than 5 seconds?** Request times out and returns 504 Gateway Timeout error.

## Requirements

### Functional Requirements

**API Endpoint:**
- **FR-001**: System MUST expose POST /api/chat endpoint
- **FR-002**: Endpoint MUST accept JSON payload with `message` (string, required) and `conversation_id` (string, optional)
- **FR-003**: Endpoint MUST return JSON response with `conversation_id` (string), `response` (string), and `tool_calls` (array)

**Authentication & Authorization:**
- **FR-004**: System MUST verify JWT token using Better Auth verification
- **FR-005**: System MUST extract user_id from JWT claims (never from request body)
- **FR-006**: System MUST return 401 Unauthorized for missing or invalid JWT
- **FR-007**: System MUST ensure users can only access their own conversations

**Conversation Management:**
- **FR-008**: System MUST auto-create new conversation on first message if no conversation_id provided
- **FR-009**: System MUST store conversations in database with user_id, id, created_at, updated_at
- **FR-010**: System MUST store messages in database with conversation_id, role (user/assistant), content, created_at
- **FR-011**: System MUST load last 2000 tokens of conversation history before invoking agent
- **FR-012**: System MUST append user message to conversation before invoking agent
- **FR-013**: System MUST append assistant response to conversation after agent completes

**AI Agent Integration:**
- **FR-014**: System MUST use OpenAI Agents SDK with AsyncOpenAI client
- **FR-015**: System MUST configure AsyncOpenAI client with Gemini API endpoint (https://generativelanguage.googleapis.com/v1beta/openai)
- **FR-016**: System MUST use Gemini 2.0 Flash model (gemini-2.0-flash)
- **FR-017**: System MUST configure agent with task management instructions
- **FR-018**: System MUST provide agent with access to MCP tools (add_task, list_tasks, complete_task, delete_task, update_task)
- **FR-019**: System MUST pass user_id to MCP tools for user isolation
- **FR-020**: System MUST execute agent using Runner.run_sync or async variant
- **FR-021**: System MUST return agent's final output as response

**MCP Tool Integration:**
- **FR-022**: System MUST define MCP tool signatures for agent to invoke
- **FR-023**: MCP tools MUST receive user_id as first parameter
- **FR-024**: MCP tools MUST return structured Task objects (not just success/failure messages)
- **FR-025**: System MUST include tool invocation details in response (tool_calls array)

**Error Handling:**
- **FR-026**: System MUST return 401 for authentication failures
- **FR-027**: System MUST return 422 for invalid request payloads
- **FR-028**: System MUST return 500 for agent or MCP tool failures
- **FR-029**: System MUST return 503 for Gemini API unavailability
- **FR-030**: System MUST return 504 for requests exceeding 5 second timeout
- **FR-031**: System MUST return user-safe error messages (no stack traces or sensitive data)
- **FR-032**: System MUST log errors for debugging (console or file)

**Performance:**
- **FR-033**: System MUST complete chat requests within 5 seconds (95th percentile)
- **FR-034**: System MUST handle concurrent requests without data corruption

### Key Entities

**Conversation:**
- Represents a chat session between user and AI agent
- Attributes: id (primary key), user_id (foreign key to user), created_at (timestamp), updated_at (timestamp)
- Relationships: Belongs to one user, has many messages
- One conversation per user (auto-created on first message)

**Message:**
- Represents a single message in a conversation (from user or assistant)
- Attributes: id (primary key), conversation_id (foreign key), role (enum: 'user' or 'assistant'), content (text), created_at (timestamp)
- Relationships: Belongs to one conversation
- Messages are append-only (never updated or deleted)

**Task (existing from Phase-2):**
- Represents a todo item
- Attributes: id, user_id, title, description, completed, created_at, updated_at
- Managed by MCP tools invoked by AI agent

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can send a chat message and receive AI response within 5 seconds in 95% of requests
- **SC-002**: AI agent successfully invokes MCP tools to perform task operations (create, list, update, complete, delete) in 100% of valid requests
- **SC-003**: Conversation history persists across multiple messages and AI responses demonstrate contextual awareness in 100% of multi-turn conversations
- **SC-004**: Unauthorized access attempts (missing/invalid JWT) are blocked with 401 response in 100% of cases
- **SC-005**: Users can complete common task management operations (add task, list tasks, mark complete) through natural conversation without errors in 90% of attempts
- **SC-006**: System handles 50 concurrent chat requests without performance degradation or data corruption
- **SC-007**: Error messages displayed in chat UI are user-friendly and actionable (no technical jargon or stack traces) in 100% of error cases
- **SC-008**: Conversation context is maintained for conversations up to 100 messages without loss of relevant history
- **SC-009**: AI agent correctly interprets user intent and invokes appropriate MCP tools in 85% of task management requests
- **SC-010**: System remains stateless - server restarts do not lose conversation data (all state in database)

## Out of Scope

**Explicitly NOT included in this specification:**

- **Frontend UI**: ChatKit interface already implemented in 004-chatbot-frontend
- **MCP Tool Implementation**: Task management tools (add_task, list_tasks, etc.) will be implemented in a separate specification
- **Database Schema for Tasks**: Task table already exists from Phase-2
- **Streaming Responses**: API returns complete response, not streamed chunks
- **Multi-modal Capabilities**: Text-only chat (no images, voice, files)
- **Conversation Branching**: Linear conversation history only
- **Conversation Editing**: Messages cannot be edited or deleted after creation
- **Multiple Conversations per User**: Single conversation per user (auto-created)
- **Conversation Sharing**: Users cannot share conversations with others
- **Agent Memory Across Conversations**: Agent only has access to current conversation history
- **Custom Agent Instructions per User**: Agent instructions are hardcoded for all users
- **Rate Limiting per User**: No per-user rate limits (rely on Gemini API limits)
- **Conversation Export**: No ability to export conversation history
- **Real-time Notifications**: No WebSocket or SSE for real-time updates

## Dependencies

**Required from Previous Phases:**
- **Phase-2 Authentication**: Better Auth JWT verification infrastructure
- **Phase-2 Database**: PostgreSQL database with user table
- **Phase-2 Backend**: FastAPI application structure
- **Phase-3 Frontend**: ChatKit UI (004-chatbot-frontend) that sends requests to /api/chat

**External Dependencies:**
- **OpenAI Agents SDK**: Python library for agent orchestration
- **Gemini API**: Google's Gemini 2.0 Flash model via API
- **AsyncOpenAI**: Python client for OpenAI-compatible APIs
- **SQLModel**: ORM for database operations (already used in Phase-2)

**To Be Implemented (Next Spec):**
- **MCP Tools**: Task management tools that agent will invoke

## Constraints

**Technical Constraints:**
- **Free LLM Only**: Must use Gemini 2.0 Flash (free tier) - no paid OpenAI models
- **Stateless Backend**: No in-memory conversation state - all state in database
- **Single Conversation per User**: One active conversation per user (simplifies implementation)
- **Token Limit**: Last 2000 tokens of conversation history loaded (Gemini context window constraint)
- **No Streaming**: Complete response returned (not streamed) to simplify implementation
- **Synchronous Processing**: Requests processed synchronously (no background jobs)

**Performance Constraints:**
- **Response Time**: 5 second timeout for chat requests
- **Concurrency**: Must handle 50 concurrent requests without degradation

**Security Constraints:**
- **JWT Required**: All requests must have valid JWT
- **User Isolation**: Users can only access their own conversations and tasks
- **Error Messages**: No sensitive data or stack traces in user-facing errors

**Integration Constraints:**
- **OpenAI Agents SDK Compatibility**: Must use OpenAI Agents SDK interface (no custom agent implementations)
- **MCP Tool Interface**: Agent must invoke MCP tools with expected signatures (to be defined in next spec)
- **Database Schema**: Must use existing user table from Phase-2

## Assumptions

**Technical Assumptions:**
- Gemini 2.0 Flash API is compatible with OpenAI Agents SDK via AsyncOpenAI client
- Gemini API has sufficient rate limits for development and testing (free tier)
- 2000 tokens is sufficient context for typical todo management conversations
- 5 second timeout is sufficient for Gemini API response time
- SQLModel ORM is already configured and working from Phase-2

**Business Assumptions:**
- Users will primarily use chat for task management (not general conversation)
- Single conversation per user is acceptable (no need for multiple conversation threads)
- Conversation history does not need to be exported or archived
- Users understand that conversation context is limited to recent messages (2000 tokens)

**Integration Assumptions:**
- MCP tools will be implemented in next specification with expected signatures
- Frontend (ChatKit) is already configured to send requests to /api/chat
- Better Auth JWT verification is working correctly from Phase-2
- Database migrations can be run to create conversations and messages tables

## API Contract

### Request Format

**Endpoint**: `POST /api/chat`

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "message": "Add a task to buy milk",
  "conversation_id": "optional-conversation-uuid"
}
```

**Fields**:
- `message` (string, required): User's chat message (max 10,000 characters)
- `conversation_id` (string, optional): UUID of existing conversation. If omitted, backend auto-creates new conversation.

### Response Format

**Success Response** (200 OK):
```json
{
  "conversation_id": "uuid-of-conversation",
  "response": "I've added a task to buy milk to your todo list.",
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": {
        "title": "Buy milk",
        "description": ""
      },
      "result": {
        "id": 123,
        "title": "Buy milk",
        "completed": false
      }
    }
  ]
}
```

**Fields**:
- `conversation_id` (string): UUID of conversation (newly created or existing)
- `response` (string): AI agent's response message
- `tool_calls` (array): List of MCP tools invoked during request (empty array if no tools used)

**Error Responses**:

**401 Unauthorized**:
```json
{
  "error": "Authentication failed. Please log in again."
}
```

**422 Unprocessable Entity**:
```json
{
  "error": "Invalid request. Message is required and must be less than 10,000 characters."
}
```

**500 Internal Server Error**:
```json
{
  "error": "Unable to process your request. Please try again."
}
```

**503 Service Unavailable**:
```json
{
  "error": "AI service temporarily unavailable. Please try again in a moment."
}
```

**504 Gateway Timeout**:
```json
{
  "error": "Request took too long to process. Please try again with a simpler message."
}
```

## Database Schema

### Conversations Table

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

### Messages Table

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

## MCP Tool Signatures (For Reference)

**Note**: These tools will be implemented in the next specification. This section documents the expected interface for the AI agent.

### add_task
```python
def add_task(user_id: str, title: str, description: str = "") -> Task:
    """
    Creates a new task for the user.

    Args:
        user_id: User ID from JWT
        title: Task title (required)
        description: Task description (optional)

    Returns:
        Task object with id, title, description, completed, created_at, updated_at
    """
```

### list_tasks
```python
def list_tasks(user_id: str, completed: bool = None) -> List[Task]:
    """
    Lists all tasks for the user.

    Args:
        user_id: User ID from JWT
        completed: Filter by completion status (optional)

    Returns:
        List of Task objects
    """
```

### complete_task
```python
def complete_task(user_id: str, task_id: int) -> Task:
    """
    Toggles task completion status.

    Args:
        user_id: User ID from JWT
        task_id: ID of task to toggle

    Returns:
        Updated Task object
    """
```

### delete_task
```python
def delete_task(user_id: str, task_id: int) -> bool:
    """
    Deletes a task.

    Args:
        user_id: User ID from JWT
        task_id: ID of task to delete

    Returns:
        True if deleted successfully
    """
```

### update_task
```python
def update_task(user_id: str, task_id: int, title: str = None, description: str = None) -> Task:
    """
    Updates task title and/or description.

    Args:
        user_id: User ID from JWT
        task_id: ID of task to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        Updated Task object
    """
```
