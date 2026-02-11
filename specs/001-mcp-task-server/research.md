# Research: MCP SDK Implementation for Task Server

**Feature**: 001-mcp-task-server
**Date**: 2026-02-09
**Status**: Complete

## Overview

This document captures research findings for implementing the MCP (Model Context Protocol) Task Server using the Official MCP SDK for Python. All technical decisions are based on official documentation, code examples, and best practices.

## 1. Package Installation & Setup

### Decision: Use Official MCP SDK v1.13.0

**Package Name**: `mcp`

**Installation Command**:
```bash
pip install "mcp[cli]"
```

**Rationale**:
- v1.13.0 is the current stable release (v1.x branch)
- `[cli]` extra includes development tools for testing and debugging
- v2 is in pre-alpha (expected Q1 2026) - not suitable for production

**Python Requirements**: Python 3.11+ (matches existing backend)

**Key Dependencies** (automatically installed):
- `anyio` - Async I/O support
- `httpx` - HTTP client
- `pydantic` - Data validation (already in use)
- `starlette` - ASGI framework
- `uvicorn` - ASGI server (already in use)

**Alternatives Considered**:
- Custom MCP implementation: Rejected - reinventing the wheel, no community support
- v2 pre-alpha: Rejected - unstable, breaking changes expected

---

## 2. Server Initialization Pattern

### Decision: Use MCPServer with Decorator-Based Registration

**Pattern**:
```python
from mcp.server.mcpserver import MCPServer

# Create server instance
mcp = MCPServer("TaskServer")

# Register tools using decorators
@mcp.tool()
async def add_task(user_id: str, title: str, description: str = None) -> dict:
    """Create a new task for a user."""
    # Implementation
    return {"task_id": 123, "status": "created", "title": title}

# Run server
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

**Rationale**:
- Clean, declarative API
- Automatic schema generation from type hints
- Minimal boilerplate
- Matches official examples and best practices

**Alternatives Considered**:
- `FastMCP`: Alternative high-level API, functionally equivalent but less documented
- Low-level SDK: Rejected - too much boilerplate, harder to maintain

---

## 3. Tool Registration & Schema Generation

### Decision: Leverage Type Hints for Automatic Schema Generation

**Pattern**:
```python
@mcp.tool()
async def add_task(
    user_id: str,           # Required parameter
    title: str,             # Required parameter
    description: str = None # Optional parameter (default value)
) -> dict:
    """
    Create a new task for a user.

    Args:
        user_id: The authenticated user's identifier
        title: Task title (max 500 characters)
        description: Optional task description

    Returns:
        Dictionary with task_id, status, and title
    """
    # Implementation
```

**How It Works**:
- Type hints automatically generate JSON Schema
- `str` → `{"type": "string"}`
- `int` → `{"type": "number"}`
- `str = None` → optional parameter
- Docstrings become tool descriptions
- Pydantic validates inputs before function execution

**Rationale**:
- Zero boilerplate for schema definition
- Type safety enforced at runtime
- Self-documenting code
- Automatic validation

**Alternatives Considered**:
- Manual JSON Schema: Rejected - error-prone, duplicates type information
- Pydantic models for parameters: Possible but adds complexity for simple tools

---

## 4. Async vs Sync Tool Functions

### Decision: Use Async Functions for All Tools

**Pattern**:
```python
@mcp.tool()
async def list_tasks(user_id: str, status: str = "all") -> list[dict]:
    """Retrieve tasks for a user."""
    async with async_session_maker() as session:
        statement = select(Task).where(Task.user_id == user_id)
        result = await session.execute(statement)
        tasks = result.scalars().all()
        return [task.dict() for task in tasks]
```

**Rationale**:
- All tools perform database I/O (blocking operations)
- Async functions enable concurrent tool invocations
- Matches existing backend async patterns (FastAPI, SQLModel async)
- Better performance under load

**When to Use Sync**:
- Pure computation (no I/O)
- In-memory operations
- Quick calculations

**For This Project**: All 5 tools perform database operations → all async

---

## 5. Response Format & Error Handling

### Decision: Return Dicts with Error Field for Expected Errors

**Success Response**:
```python
return {
    "task_id": 123,
    "status": "created",
    "title": "Buy groceries"
}
```

**Error Response**:
```python
return {
    "error": "task not found"
}
```

**Exception Handling**:
```python
@mcp.tool()
async def delete_task(user_id: str, task_id: int) -> dict:
    try:
        # Database operation
        task = await get_task_by_id(session, task_id, user_id)

        if not task:
            return {"error": "task not found"}  # Expected error

        await session.delete(task)
        await session.commit()

        return {"task_id": task_id, "status": "deleted", "title": task.title}

    except Exception as e:
        # Unexpected error - log and return generic message
        logger.error(f"Database error: {str(e)}")
        return {"error": "service unavailable"}
```

**Rationale**:
- Consistent error format across all tools
- Distinguishes expected errors (validation, not found) from unexpected errors (database failure)
- Doesn't expose internal implementation details
- Agent can check for `"error"` key in response

**Alternatives Considered**:
- Raise exceptions: Rejected - harder for agent to handle, less predictable
- HTTP status codes: Not applicable - MCP uses its own protocol

---

## 6. Transport Mechanism

### Decision: Use Stdio Transport for Development, HTTP for Production (if needed)

**Stdio Transport** (Recommended for Phase-3):
```python
mcp.run(transport="stdio")
```

**Characteristics**:
- Local process-to-process communication
- Uses stdin/stdout streams
- Optimal performance (no network overhead)
- Single client (agent) per server instance
- Matches Claude Desktop integration pattern

**Streamable HTTP Transport** (Alternative):
```python
mcp.run(transport="streamable-http", json_response=True)
# Runs on http://localhost:8000/mcp
```

**Characteristics**:
- Remote communication over HTTP
- Supports multiple clients
- Enables authentication (Bearer tokens)
- Network latency applies

**Decision for Phase-3**: Start with **stdio** transport
- Agent and MCP server run on same machine
- Simpler setup and debugging
- Matches MCP best practices for local servers
- Can switch to HTTP later if remote access needed

**Alternatives Considered**:
- SSE transport: Legacy, not recommended
- WebSocket: Not supported by MCP SDK v1

---

## 7. User Context (user_id Passing)

### Decision: Pass user_id as Function Parameter

**Pattern**:
```python
@mcp.tool()
async def add_task(user_id: str, title: str, description: str = None) -> dict:
    """
    Create a new task.

    Args:
        user_id: The authenticated user's identifier (from JWT)
        title: Task title
        description: Optional description
    """
    # user_id is a regular parameter
    task = Task(user_id=user_id, title=title, description=description)
    # ... database operations
```

**How It Works**:
1. FastAPI chat endpoint verifies JWT and extracts `user_id`
2. Chat endpoint passes `user_id` to OpenAI Agent as context
3. Agent includes `user_id` when invoking MCP tools
4. MCP tool receives `user_id` as a parameter

**Rationale**:
- Explicit and clear - user_id is visible in tool signature
- No hidden context or magic
- Easy to test - just pass user_id as argument
- Enforces that agent must provide user_id
- Matches spec requirement (FR-009: "user_id required for all operations")

**Alternatives Considered**:
- Context object: More complex, less explicit, harder to test
- Global state: Violates stateless requirement
- Environment variables: Not request-specific

---

## 8. Database Integration

### Decision: Share SQLModel Engine with FastAPI

**Pattern**:
```python
# backend/app/database.py (shared by FastAPI and MCP)
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

# Shared async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# Shared session maker
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
```

```python
# backend/app/mcp/tools/add_task.py
from app.database import async_session_maker
from app.models.task import Task

@mcp.tool()
async def add_task(user_id: str, title: str, description: str = None) -> dict:
    async with async_session_maker() as session:
        task = Task(user_id=user_id, title=title, description=description)
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return {"task_id": task.id, "status": "created", "title": task.title}
```

**Rationale**:
- Reuses existing database configuration
- Shares connection pool (efficient resource usage)
- Consistent database access patterns
- No duplication of connection logic

**Alternatives Considered**:
- Separate database connection: Rejected - wastes resources, duplicates config
- Sync SQLModel: Rejected - blocks event loop, poor performance

---

## 9. Process Architecture

### Decision: Run MCP Server as Separate Process

**Pattern**:
```python
# backend/scripts/run_mcp_server.py
from mcp.server.mcpserver import MCPServer
from app.mcp.tools import register_tools

mcp = MCPServer("TaskServer")
register_tools(mcp)

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

**Startup**:
```bash
python backend/scripts/run_mcp_server.py
```

**Rationale**:
- Clean separation of concerns (MCP server vs FastAPI server)
- Independent scaling and monitoring
- Easier debugging (separate logs)
- Matches MCP architecture patterns
- Agent connects to MCP server via stdio

**Alternatives Considered**:
- Embedded in FastAPI: Rejected - tighter coupling, mixed concerns, harder to debug
- Separate Docker container: Overkill for Phase-3, can add later

---

## 10. Testing Strategy

### Decision: Three-Layer Testing Approach

**Layer 1: Unit Tests** (Test tool functions directly)
```python
@pytest.mark.asyncio
async def test_add_task_creates_task():
    result = await add_task("user123", "Test Task", "Description")

    assert result["status"] == "created"
    assert result["title"] == "Test Task"
    assert "task_id" in result

    # Verify in database
    async with async_session_maker() as session:
        task = await session.get(Task, result["task_id"])
        assert task.user_id == "user123"
```

**Layer 2: Integration Tests** (Test MCP server with mock client)
```python
@pytest.mark.asyncio
async def test_mcp_server_tool_invocation():
    server_params = ServerParameters(
        command="python",
        args=["backend/scripts/run_mcp_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with Client(read, write) as client:
            await client.initialize()

            result = await client.call_tool(
                "add_task",
                arguments={"user_id": "test", "title": "Test"}
            )

            assert "created" in result.content[0].text
```

**Layer 3: User Isolation Tests** (Verify security)
```python
@pytest.mark.asyncio
async def test_user_isolation():
    # Create task for user A
    result_a = await add_task("user_a", "Task A")

    # Try to access from user B
    tasks_b = await list_tasks("user_b")

    # Assert user B doesn't see user A's task
    assert len(tasks_b) == 0
```

**Rationale**:
- Unit tests: Fast, test business logic
- Integration tests: Verify MCP protocol works
- Isolation tests: Ensure security requirements

---

## 11. Performance Optimization

### Decision: Use Connection Pooling and Query Limits

**Connection Pooling** (already configured):
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,        # 10 concurrent connections
    max_overflow=20,     # 20 additional under load
    pool_pre_ping=True   # Verify before use
)
```

**Query Limits**:
```python
@mcp.tool()
async def list_tasks(user_id: str, status: str = "all", limit: int = 100) -> list[dict]:
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .limit(min(limit, 1000))  # Cap at 1000
        .order_by(Task.created_at.desc())
    )
    # ... execute
```

**Indexes** (already exist from Phase-2):
- `idx_tasks_user_id` on `tasks(user_id)`
- `idx_tasks_completed` on `tasks(completed)`

**Rationale**:
- Meets <200ms requirement (SC-003)
- Supports 100 concurrent operations (SC-004)
- Prevents unbounded queries

---

## 12. Security Best Practices

### Decision: Validate All Inputs and Enforce User Isolation

**Input Validation**:
```python
@mcp.tool()
async def add_task(user_id: str, title: str, description: str = None) -> dict:
    # Validate user_id
    if not user_id:
        return {"error": "user_id is required"}

    # Validate title
    title = title.strip()
    if not title:
        return {"error": "title cannot be empty"}

    if len(title) > 500:
        return {"error": "title exceeds maximum length of 500 characters"}

    # ... create task
```

**User Isolation**:
```python
@mcp.tool()
async def delete_task(user_id: str, task_id: int) -> dict:
    async with async_session_maker() as session:
        # ALWAYS filter by user_id
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id  # User isolation
        )
        task = (await session.execute(statement)).scalar_one_or_none()

        if not task:
            # Don't reveal if task exists for another user
            return {"error": "task not found"}

        # ... delete task
```

**Error Messages**:
```python
# ✅ GOOD: Generic error, doesn't leak info
return {"error": "task not found"}

# ❌ BAD: Reveals task exists for another user
return {"error": "task belongs to another user"}
```

**Rationale**:
- Prevents SQL injection (Pydantic + SQLModel)
- Enforces user isolation (FR-010)
- Doesn't leak information about other users' data
- Validates all inputs before database operations

---

## Summary of Technical Decisions

| Decision Area | Choice | Rationale |
|---------------|--------|-----------|
| **Package** | `mcp[cli]` v1.13.0 | Stable, official, well-documented |
| **Server API** | `MCPServer` with decorators | Clean, minimal boilerplate |
| **Tool Functions** | Async functions | Database I/O requires async |
| **Schema Generation** | Type hints + docstrings | Automatic, self-documenting |
| **Response Format** | Dict with `error` key | Consistent, agent-friendly |
| **Transport** | Stdio (development) | Local, fast, simple |
| **User Context** | Function parameter | Explicit, testable |
| **Database** | Shared SQLModel engine | Efficient, consistent |
| **Architecture** | Separate process | Clean separation, scalable |
| **Testing** | 3-layer (unit/integration/isolation) | Comprehensive coverage |
| **Performance** | Connection pooling + limits | Meets <200ms requirement |
| **Security** | Input validation + user isolation | Prevents unauthorized access |

---

## Implementation Readiness

**Status**: ✅ All technical decisions resolved

**Ready to Proceed With**:
1. Data model documentation
2. Tool contract specifications
3. Quickstart guide
4. Task breakdown

**No Blockers**: All NEEDS CLARIFICATION items from plan.md are resolved.

---

**Research Completed**: 2026-02-09
**Next Phase**: Design artifacts (data-model.md, contracts/, quickstart.md)
