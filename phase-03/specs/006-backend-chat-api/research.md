# Research: Backend Chat API + OpenAI Agent Orchestration

**Feature**: 006-backend-chat-api
**Date**: 2026-02-08
**Status**: Complete

## Overview

This document resolves all technical unknowns identified in the implementation plan before proceeding to design phase. Each research area includes the decision made, rationale, alternatives considered, and implementation guidance.

---

## 1. OpenAI Agents SDK with Gemini Integration

### Research Question
How to configure AsyncOpenAI client with Gemini API endpoint and ensure OpenAI Agents SDK compatibility with non-OpenAI models?

### Decision: Use AsyncOpenAI with Custom Base URL

**Approach**:
```python
from openai import AsyncOpenAI

# Configure AsyncOpenAI client for Gemini API
gemini_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai"
)

# Use with OpenAI Agents SDK
from openai_agents import OpenAIChatCompletionsModel, Agent, Runner

model = OpenAIChatCompletionsModel(
    client=gemini_client,
    model="gemini-2.0-flash"
)

agent = Agent(
    name="TaskAssistant",
    instructions="You are a helpful task management assistant...",
    model=model,
    tools=[add_task_tool, list_tasks_tool, ...]
)

# Execute agent
result = Runner.run_sync(agent, messages=[...])
```

**Rationale**:
- Gemini API provides OpenAI-compatible endpoint at `/v1beta/openai`
- AsyncOpenAI client accepts custom `base_url` parameter
- OpenAI Agents SDK works with any OpenAI-compatible API
- Gemini 2.0 Flash is free tier (no API costs)
- Maintains compatibility with OpenAI Agents SDK interface

**Alternatives Considered**:
1. **Custom Agent Implementation**: Rejected - violates constitution (must use official SDK)
2. **OpenAI API with Paid Tier**: Rejected - requirement is free LLM only
3. **LangChain with Gemini**: Rejected - spec requires OpenAI Agents SDK

**Implementation Guidance**:
- Store Gemini API key in `.env` as `GEMINI_API_KEY`
- Create `backend/app/ai/gemini_client.py` module for client configuration
- Handle Gemini-specific error codes (different from OpenAI)
- Test with sample requests before full integration

**Agent Execution Mode Decision**: Use `Runner.run_sync` (synchronous)
- **Rationale**: Simpler implementation, easier error handling, sufficient for 5s timeout requirement
- **Trade-off**: Blocks request thread but acceptable for <5s response time
- **Alternative**: `Runner.run` (async) - adds complexity without significant benefit for current scale

---

## 2. MCP Tool Interface Design

### Research Question
How to implement MCP tools with proper signatures, user_id passing, and error handling compatible with OpenAI Agents SDK?

### Decision: Function-Based MCP Tools with Structured Returns

**Approach**:
```python
from typing import List, Optional
from pydantic import BaseModel

# Tool result models
class Task(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    created_at: str
    updated_at: str

# MCP Tool implementation
def add_task(user_id: str, title: str, description: str = "") -> Task:
    """
    Creates a new task for the user.

    Args:
        user_id: User ID from JWT (passed by agent context)
        title: Task title (required)
        description: Task description (optional)

    Returns:
        Task object with all fields

    Raises:
        ValueError: If title is empty or too long
        DatabaseError: If database operation fails
    """
    # Validate inputs
    if not title or len(title) > 500:
        raise ValueError("Title must be 1-500 characters")

    # Use SQLModel to create task
    from app.models.task import Task as TaskModel
    from app.database import get_session

    with get_session() as session:
        task = TaskModel(
            user_id=user_id,
            title=title,
            description=description,
            completed=False
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        # Return as Pydantic model for agent
        return Task(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat()
        )

# Register tool with agent
from openai_agents import Tool

add_task_tool = Tool(
    function=add_task,
    description="Creates a new task for the user"
)
```

**Rationale**:
- Functions are simpler than classes for tool implementation
- Pydantic models provide structured returns (not just strings)
- Type hints enable OpenAI Agents SDK to generate proper tool schemas
- user_id passed explicitly (not from global context)
- Errors propagate to agent for graceful handling

**Alternatives Considered**:
1. **Class-Based Tools**: Rejected - adds unnecessary complexity
2. **String Returns**: Rejected - agent needs structured data for context
3. **Global user_id Context**: Rejected - violates stateless principle

**Implementation Guidance**:
- Create `backend/app/mcp/tools.py` with all 5 tool functions
- Use Pydantic models for all return types
- Validate inputs before database operations
- Use SQLModel sessions with proper transaction management
- Raise descriptive errors (agent will handle them)

**Tool List**:
1. `add_task(user_id, title, description)` → Task
2. `list_tasks(user_id, completed)` → List[Task]
3. `complete_task(user_id, task_id)` → Task
4. `delete_task(user_id, task_id)` → bool
5. `update_task(user_id, task_id, title, description)` → Task

---

## 3. Conversation History Management

### Research Question
How to implement token counting for 2000 token limit and efficiently load conversation history?

### Decision: Use tiktoken for Token Counting with Message Truncation

**Approach**:
```python
import tiktoken

def load_conversation_history(conversation_id: str, max_tokens: int = 2000) -> List[dict]:
    """
    Loads conversation history up to max_tokens limit.

    Args:
        conversation_id: UUID of conversation
        max_tokens: Maximum tokens to load (default 2000)

    Returns:
        List of message dicts in chronological order
    """
    # Get encoding for model
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")  # Compatible with Gemini

    # Load messages from database (newest first)
    from app.models.message import Message
    from app.database import get_session

    with get_session() as session:
        messages = session.query(Message)\
            .filter(Message.conversation_id == conversation_id)\
            .order_by(Message.created_at.desc())\
            .all()

    # Build message list with token counting
    result = []
    total_tokens = 0

    for msg in messages:
        # Count tokens in message
        msg_tokens = len(encoding.encode(msg.content))

        # Stop if adding this message exceeds limit
        if total_tokens + msg_tokens > max_tokens:
            break

        result.insert(0, {  # Insert at beginning (chronological order)
            "role": msg.role,
            "content": msg.content
        })
        total_tokens += msg_tokens

    return result
```

**Rationale**:
- tiktoken is OpenAI's official token counting library
- Accurate token counting (not character approximation)
- Load messages newest-first, stop when limit reached
- Preserves most recent context (most relevant for agent)
- Efficient database query with ORDER BY and LIMIT

**Alternatives Considered**:
1. **Character Count Approximation**: Rejected - inaccurate (4 chars ≈ 1 token is rough)
2. **Fixed Message Count**: Rejected - messages vary in length
3. **Load All Messages**: Rejected - exceeds token limit for long conversations

**Implementation Guidance**:
- Install tiktoken: `pip install tiktoken`
- Use `gpt-3.5-turbo` encoding (compatible with Gemini)
- Create `backend/app/services/message_service.py` for history loading
- Cache encoding object (don't recreate on each request)
- Log token counts for monitoring

**Token Counting Strategy**:
- System prompt: ~100 tokens (reserved)
- User message: Variable (validated at <10,000 chars)
- History: Up to 1900 tokens (2000 - 100 system prompt)
- Agent response: Generated (not counted in input)

---

## 4. Stateless Backend Architecture

### Research Question
How to implement stateless FastAPI endpoints with proper database session management for concurrent requests?

### Decision: Per-Request Database Sessions with Dependency Injection

**Approach**:
```python
from sqlmodel import Session, create_engine
from contextlib import contextmanager
from fastapi import Depends

# Database engine (singleton)
engine = create_engine(
    os.getenv("DATABASE_URL"),
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Verify connections before use
)

# Dependency for FastAPI routes
def get_db_session():
    """Provides database session for request."""
    with Session(engine) as session:
        yield session

# Chat endpoint (stateless)
@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    session: Session = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id)  # From JWT
):
    """
    Stateless chat endpoint - all state in database.

    Flow:
    1. Load conversation history from DB
    2. Store user message in DB
    3. Invoke agent (stateless)
    4. Store assistant response in DB
    5. Return response
    """
    # Get or create conversation
    conversation = get_or_create_conversation(session, user_id, request.conversation_id)

    # Load history (up to 2000 tokens)
    history = load_conversation_history(conversation.id)

    # Store user message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    session.add(user_msg)
    session.commit()

    # Invoke agent (stateless - no memory)
    agent_response = invoke_agent(user_id, history, request.message)

    # Store assistant response
    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=agent_response.content
    )
    session.add(assistant_msg)
    session.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        response=agent_response.content,
        tool_calls=agent_response.tool_calls
    )
```

**Rationale**:
- FastAPI dependency injection provides clean session management
- Connection pooling handles concurrent requests efficiently
- Each request gets isolated database session
- No global state or class-level variables
- Server restarts don't lose data (all in database)

**Alternatives Considered**:
1. **Global Session**: Rejected - not thread-safe, violates stateless principle
2. **Per-Operation Sessions**: Rejected - too many connections, transaction issues
3. **Session Middleware**: Rejected - less explicit than dependency injection

**Implementation Guidance**:
- Configure connection pool size based on expected concurrency (10-20)
- Use `pool_pre_ping=True` to handle stale connections
- Commit after each database write (user message, assistant message)
- Use transactions for multi-step operations
- Test with concurrent requests (pytest-xdist)

**Stateless Verification**:
- No class-level state variables
- No global conversation cache
- No in-memory message storage
- Agent recreated on each request
- Server restart test: conversation persists

---

## 5. Error Handling and Timeouts

### Research Question
How to implement request timeouts and graceful error handling for Gemini API and MCP tool failures?

### Decision: FastAPI Middleware for Timeouts + Structured Error Responses

**Approach**:
```python
import asyncio
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

# Timeout middleware
class TimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/api/chat":
            try:
                # 5 second timeout for chat requests
                return await asyncio.wait_for(
                    call_next(request),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                raise HTTPException(
                    status_code=504,
                    detail="Request took too long to process. Please try again with a simpler message."
                )
        else:
            return await call_next(request)

# Error handling in chat endpoint
@router.post("/chat")
async def chat_endpoint(...):
    try:
        # ... chat logic ...

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed. Please log in again."
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid request. {str(e)}"
        )

    except GeminiAPIError as e:
        # Gemini API unavailable
        raise HTTPException(
            status_code=503,
            detail="AI service temporarily unavailable. Please try again."
        )

    except MCPToolError as e:
        # MCP tool failure
        logger.error(f"MCP tool error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Unable to complete task operation. Please try again."
        )

    except Exception as e:
        # Unexpected error
        logger.exception(f"Unexpected error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Unable to process your request. Please try again."
        )
```

**Rationale**:
- Middleware provides global timeout enforcement
- Structured error responses (no stack traces to user)
- Specific error codes for different failure modes
- Logging for debugging (not exposed to user)
- Graceful degradation (user-friendly messages)

**Alternatives Considered**:
1. **Per-Route Timeout Decorator**: Rejected - less consistent than middleware
2. **Generic Error Messages**: Rejected - users need actionable feedback
3. **Expose Stack Traces**: Rejected - security risk, poor UX

**Implementation Guidance**:
- Add TimeoutMiddleware to FastAPI app
- Create custom exception classes (GeminiAPIError, MCPToolError)
- Log all errors with context (user_id, conversation_id, timestamp)
- Test timeout behavior with slow mock responses
- Monitor error rates in production

**Error Code Mapping**:
- 401: JWT invalid/missing
- 422: Request validation failed
- 500: MCP tool failure, unexpected errors
- 503: Gemini API unavailable
- 504: Request timeout (>5 seconds)

**Gemini API Error Handling**:
- Rate limit (429): Retry with exponential backoff
- Invalid API key (401): Log error, return 503 to user
- Model unavailable (503): Return 503 to user
- Timeout: Caught by middleware, return 504

---

## Summary of Decisions

| Research Area | Decision | Key Rationale |
|---------------|----------|---------------|
| **Agent Execution** | Runner.run_sync (synchronous) | Simpler, sufficient for 5s timeout |
| **Gemini Integration** | AsyncOpenAI with custom base_url | OpenAI-compatible endpoint |
| **MCP Tools** | Function-based with Pydantic returns | Simple, structured, type-safe |
| **Token Counting** | tiktoken library | Accurate, official OpenAI library |
| **History Loading** | Newest-first with token limit | Preserves recent context |
| **Session Management** | FastAPI dependency injection | Clean, thread-safe, stateless |
| **Connection Pooling** | 10-20 connections | Handles 50 concurrent requests |
| **Timeout Implementation** | Middleware (5 seconds) | Global, consistent enforcement |
| **Error Handling** | Structured responses, no stack traces | User-friendly, secure |

---

## Implementation Checklist

### Dependencies to Install
- [ ] `openai` (AsyncOpenAI client)
- [ ] `openai-agents` (OpenAI Agents SDK)
- [ ] `tiktoken` (token counting)
- [ ] `pydantic` (already installed - for tool returns)
- [ ] `sqlmodel` (already installed - for database)

### Environment Variables to Add
- [ ] `GEMINI_API_KEY` - Gemini API key from Google AI Studio
- [ ] `DATABASE_URL` - PostgreSQL connection string (already exists)

### Files to Create
- [ ] `backend/app/ai/gemini_client.py` - Gemini client configuration
- [ ] `backend/app/ai/agent.py` - Agent setup and invocation
- [ ] `backend/app/ai/prompts.py` - System prompts
- [ ] `backend/app/mcp/server.py` - MCP server setup
- [ ] `backend/app/mcp/tools.py` - 5 task tools
- [ ] `backend/app/services/conversation_service.py` - Conversation management
- [ ] `backend/app/services/message_service.py` - Message persistence and history
- [ ] `backend/app/routes/chat.py` - Chat endpoint
- [ ] `backend/app/middleware/timeout.py` - Timeout middleware

### Configuration Changes
- [ ] Add TimeoutMiddleware to FastAPI app
- [ ] Configure database connection pool (size=10, max_overflow=20)
- [ ] Add structured logging configuration
- [ ] Update `.env.example` with GEMINI_API_KEY

---

## Risk Mitigation

### High Risk: Gemini API Compatibility
- **Mitigation**: Prototype integration in isolated test before full implementation
- **Test**: Create simple agent with one tool, verify tool invocation works
- **Fallback**: If incompatible, escalate to user for OpenAI API approval

### Medium Risk: Token Counting Accuracy
- **Mitigation**: Use tiktoken (official library) instead of approximation
- **Test**: Compare token counts with actual Gemini API usage
- **Fallback**: If inaccurate, reduce limit to 1500 tokens for safety margin

### Low Risk: Concurrent Request Handling
- **Mitigation**: Connection pooling + proper session management
- **Test**: Load test with 50 concurrent requests using pytest-xdist
- **Fallback**: Increase pool size if bottleneck detected

---

## Next Steps

1. ✅ Research complete - all technical unknowns resolved
2. ⏳ Generate data-model.md (Phase 1) - SQLModel schemas
3. ⏳ Generate contracts/chat-api.yaml (Phase 1) - OpenAPI spec
4. ⏳ Generate quickstart.md (Phase 1) - Setup instructions
5. ⏳ Update agent context (Phase 1) - Add new technologies
6. ⏳ Run /sp.tasks (Phase 2) - Generate implementation tasks

**Research Status**: ✅ COMPLETE
**Ready for**: Phase 1 Design & Contracts
