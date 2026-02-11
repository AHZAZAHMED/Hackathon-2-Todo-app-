# Quickstart Guide: MCP Task Server

**Feature**: 001-mcp-task-server
**Date**: 2026-02-09
**Audience**: Developers implementing the MCP Task Server

## Overview

This guide provides step-by-step instructions for setting up, implementing, and testing the MCP Task Server. Follow these steps in order to get the MCP server running with all 5 task management tools.

---

## Prerequisites

Before starting, ensure you have:

- ✅ Python 3.11+ installed
- ✅ PostgreSQL database (Neon) accessible with existing `tasks` table from Phase-2
- ✅ DATABASE_URL environment variable configured
- ✅ Git repository cloned
- ✅ Phase-2 backend running successfully (FastAPI + SQLModel)

---

## Step 1: Install MCP SDK

### 1.1 Add Dependency to requirements.txt

Add the following to `backend/requirements.txt`:

```txt
# Existing dependencies
fastapi>=0.104.0
sqlmodel>=0.0.14
uvicorn>=0.24.0
pyjwt>=2.8.0
python-dotenv>=1.0.0
openai>=1.0.0
asyncpg>=0.29.0
httpx>=0.25.0

# New dependency for MCP server
mcp[cli]>=1.13.0
```

### 1.2 Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Expected Output**:
```
Successfully installed mcp-1.13.0 ...
```

### 1.3 Verify Installation

```bash
python -c "from mcp.server.mcpserver import MCPServer; print('MCP SDK installed successfully')"
```

**Expected Output**: `MCP SDK installed successfully`

---

## Step 2: Create MCP Server Structure

### 2.1 Create Directory Structure

```bash
cd backend/app
mkdir -p mcp/tools
touch mcp/__init__.py
touch mcp/server.py
touch mcp/tools/__init__.py
touch mcp/tools/add_task.py
touch mcp/tools/list_tasks.py
touch mcp/tools/update_task.py
touch mcp/tools/complete_task.py
touch mcp/tools/delete_task.py
```

### 2.2 Verify Structure

```bash
tree backend/app/mcp
```

**Expected Output**:
```
backend/app/mcp/
├── __init__.py
├── server.py
└── tools/
    ├── __init__.py
    ├── add_task.py
    ├── list_tasks.py
    ├── update_task.py
    ├── complete_task.py
    └── delete_task.py
```

---

## Step 3: Implement MCP Tools

### 3.1 Implement add_task Tool

Create `backend/app/mcp/tools/add_task.py`:

```python
from app.database import async_session_maker
from app.models.task import Task
from datetime import datetime

async def add_task(user_id: str, title: str, description: str = None) -> dict:
    """
    Create a new task for a user.

    Args:
        user_id: The authenticated user's identifier
        title: Task title (max 500 characters)
        description: Optional task description

    Returns:
        Dictionary with task_id, status, and title
    """
    # Validate inputs
    if not user_id:
        return {"error": "user_id is required"}

    title = title.strip()
    if not title:
        return {"error": "title cannot be empty"}

    if len(title) > 500:
        return {"error": "title exceeds maximum length of 500 characters"}

    try:
        async with async_session_maker() as session:
            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                completed=False
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)

            return {
                "task_id": task.id,
                "status": "created",
                "title": task.title
            }

    except Exception as e:
        print(f"Error creating task: {str(e)}")
        return {"error": "service unavailable"}
```

### 3.2 Implement Remaining Tools

Follow the same pattern for the other 4 tools. See `specs/001-mcp-task-server/contracts/` for detailed specifications.

**Key Points**:
- All tools are async functions
- All tools receive `user_id` as first parameter
- All tools filter queries by `user_id` (user isolation)
- All tools return dict with either success data or `{"error": "message"}`
- All tools handle exceptions and return generic errors

---

## Step 4: Create MCP Server

### 4.1 Implement Server Initialization

Create `backend/app/mcp/server.py`:

```python
from mcp.server.mcpserver import MCPServer
from app.mcp.tools.add_task import add_task
from app.mcp.tools.list_tasks import list_tasks
from app.mcp.tools.update_task import update_task
from app.mcp.tools.complete_task import complete_task
from app.mcp.tools.delete_task import delete_task

# Create MCP server instance
mcp = MCPServer("TaskServer")

# Register tools
mcp.tool()(add_task)
mcp.tool()(list_tasks)
mcp.tool()(update_task)
mcp.tool()(complete_task)
mcp.tool()(delete_task)

def run_server():
    """Start the MCP server with stdio transport."""
    mcp.run(transport="stdio")
```

### 4.2 Create Startup Script

Create `backend/scripts/run_mcp_server.py`:

```python
#!/usr/bin/env python
"""
MCP Task Server Startup Script

Starts the MCP server with stdio transport for agent communication.
"""

import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.mcp.server import run_server

if __name__ == "__main__":
    print("Starting MCP Task Server...", file=sys.stderr)
    run_server()
```

### 4.3 Make Script Executable

```bash
chmod +x backend/scripts/run_mcp_server.py
```

---

## Step 5: Test MCP Server

### 5.1 Start MCP Server

```bash
python backend/scripts/run_mcp_server.py
```

**Expected Output** (to stderr):
```
Starting MCP Task Server...
```

**Note**: Server runs in foreground and communicates via stdin/stdout. Keep terminal open.

### 5.2 Test with MCP Client (Python)

In a separate terminal, create `backend/tests/test_mcp_manual.py`:

```python
import asyncio
from mcp.client import Client
from mcp.client.stdio import stdio_client, ServerParameters

async def test_mcp_tools():
    """Test MCP server tools manually."""
    server_params = ServerParameters(
        command="python",
        args=["backend/scripts/run_mcp_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with Client(read, write) as client:
            # Initialize connection
            await client.initialize()

            # List available tools
            tools = await client.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")

            # Test add_task
            result = await client.call_tool(
                "add_task",
                arguments={
                    "user_id": "test_user",
                    "title": "Test Task",
                    "description": "This is a test"
                }
            )
            print(f"add_task result: {result.content[0].text}")

            # Test list_tasks
            result = await client.call_tool(
                "list_tasks",
                arguments={"user_id": "test_user", "status": "all"}
            )
            print(f"list_tasks result: {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
```

Run the test:
```bash
python backend/tests/test_mcp_manual.py
```

**Expected Output**:
```
Available tools: ['add_task', 'list_tasks', 'update_task', 'complete_task', 'delete_task']
add_task result: {"task_id": 1, "status": "created", "title": "Test Task"}
list_tasks result: [{"id": 1, "title": "Test Task", ...}]
```

---

## Step 6: Verify Database Persistence

### 6.1 Check Database

```bash
psql $DATABASE_URL -c "SELECT id, user_id, title, completed FROM tasks WHERE user_id = 'test_user';"
```

**Expected Output**:
```
 id | user_id   | title      | completed
----+-----------+------------+-----------
  1 | test_user | Test Task  | f
```

### 6.2 Verify User Isolation

Create tasks for multiple users and verify isolation:

```python
# Create task for user A
await client.call_tool("add_task", {"user_id": "user_a", "title": "Task A"})

# Create task for user B
await client.call_tool("add_task", {"user_id": "user_b", "title": "Task B"})

# List tasks for user A
result_a = await client.call_tool("list_tasks", {"user_id": "user_a"})
# Should only see Task A

# List tasks for user B
result_b = await client.call_tool("list_tasks", {"user_id": "user_b"})
# Should only see Task B
```

---

## Step 7: Run Automated Tests

### 7.1 Create Unit Tests

Create `backend/tests/test_mcp_tools.py`:

```python
import pytest
from app.mcp.tools.add_task import add_task
from app.mcp.tools.list_tasks import list_tasks

@pytest.mark.asyncio
async def test_add_task_creates_task():
    """Test add_task tool creates task in database."""
    result = await add_task("test_user", "Test Task", "Description")

    assert result["status"] == "created"
    assert result["title"] == "Test Task"
    assert "task_id" in result

@pytest.mark.asyncio
async def test_user_isolation():
    """Test that users only see their own tasks."""
    # Create task for user A
    await add_task("user_a", "Task A")

    # List tasks for user B
    tasks_b = await list_tasks("user_b", "all")

    # User B should not see user A's task
    assert len(tasks_b) == 0
```

### 7.2 Run Tests

```bash
cd backend
pytest tests/test_mcp_tools.py -v
```

**Expected Output**:
```
tests/test_mcp_tools.py::test_add_task_creates_task PASSED
tests/test_mcp_tools.py::test_user_isolation PASSED
```

---

## Step 8: Integration with OpenAI Agent

### 8.1 Agent Configuration

The OpenAI Agent (from Phase-3 Spec-2) will connect to the MCP server to invoke tools. The agent must:

1. Start MCP server as subprocess
2. Connect via stdio transport
3. Pass `user_id` from JWT when invoking tools
4. Handle tool responses

### 8.2 Example Agent Integration

```python
# In your AI agent service (backend/app/services/ai_agent.py)
from mcp.client import Client
from mcp.client.stdio import stdio_client, ServerParameters

class AIAgentService:
    async def invoke_mcp_tool(self, tool_name: str, user_id: str, **kwargs):
        """Invoke an MCP tool with user context."""
        server_params = ServerParameters(
            command="python",
            args=["backend/scripts/run_mcp_server.py"]
        )

        async with stdio_client(server_params) as (read, write):
            async with Client(read, write) as client:
                await client.initialize()

                # Add user_id to arguments
                arguments = {"user_id": user_id, **kwargs}

                # Call tool
                result = await client.call_tool(tool_name, arguments=arguments)

                return result.content[0].text
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'mcp'"

**Solution**:
- Verify MCP SDK installed: `pip list | grep mcp`
- Reinstall: `pip install "mcp[cli]>=1.13.0"`
- Check Python version: `python --version` (must be 3.11+)

### Issue: "Database connection failed"

**Solution**:
- Verify DATABASE_URL is set: `echo $DATABASE_URL`
- Test connection: `psql $DATABASE_URL -c "SELECT 1;"`
- Check if tasks table exists: `psql $DATABASE_URL -c "\dt tasks"`

### Issue: "MCP server not responding"

**Solution**:
- Check server is running: `ps aux | grep run_mcp_server`
- Check for errors in stderr output
- Verify stdio transport is configured correctly
- Try restarting server

### Issue: "User isolation not working"

**Solution**:
- Verify all queries filter by user_id
- Check database foreign key constraints
- Review tool implementation for missing user_id filters
- Run user isolation tests

### Issue: "Performance slower than 200ms"

**Solution**:
- Verify database indexes exist: `\di` in psql
- Check connection pool settings (pool_size=10, max_overflow=20)
- Profile slow queries with `EXPLAIN ANALYZE`
- Consider adding composite index on (user_id, completed)

---

## Performance Benchmarking

### Benchmark Tool Performance

Create `backend/tests/benchmark_mcp.py`:

```python
import asyncio
import time
from app.mcp.tools.add_task import add_task

async def benchmark_add_task():
    """Benchmark add_task performance."""
    iterations = 100
    start = time.time()

    tasks = [
        add_task(f"user_{i}", f"Task {i}")
        for i in range(iterations)
    ]

    results = await asyncio.gather(*tasks)

    elapsed = time.time() - start
    avg_time = (elapsed / iterations) * 1000  # Convert to ms

    print(f"Completed {iterations} add_task operations")
    print(f"Total time: {elapsed:.2f}s")
    print(f"Average time: {avg_time:.2f}ms")
    print(f"Target: <200ms (95th percentile)")

    assert avg_time < 200, f"Performance target not met: {avg_time}ms"

if __name__ == "__main__":
    asyncio.run(benchmark_add_task())
```

Run benchmark:
```bash
python backend/tests/benchmark_mcp.py
```

**Expected Output**:
```
Completed 100 add_task operations
Total time: 2.50s
Average time: 25.00ms
Target: <200ms (95th percentile)
```

---

## Next Steps

After completing this quickstart:

1. ✅ MCP server running with 5 tools
2. ✅ All tools tested and working
3. ✅ Database persistence verified
4. ✅ User isolation enforced
5. ⏳ Run `/sp.tasks` to generate task breakdown
6. ⏳ Integrate with OpenAI Agent (Phase-3 Spec-2)
7. ⏳ Deploy to staging environment

---

## Additional Resources

- [MCP SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- Tool Contracts: `specs/001-mcp-task-server/contracts/`
- Data Model: `specs/001-mcp-task-server/data-model.md`
- Research: `specs/001-mcp-task-server/research.md`

---

**Quickstart Status**: ✅ Complete - Ready for implementation
