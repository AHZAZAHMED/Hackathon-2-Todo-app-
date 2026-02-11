"""
MCP Task Server

This module initializes the MCP (Model Context Protocol) server and registers
all task management tools. The server uses stdio transport for communication
with the OpenAI Agent.

Architecture:
- MCPServer with decorator-based tool registration
- Stdio transport for local process communication
- Async tools for database I/O operations
- Stateless operation (no in-memory state)

Tools are registered in their respective implementation files and imported here.
"""

from mcp.server.mcpserver import MCPServer

# Create MCP server instance
mcp = MCPServer("TaskServer")

# Import and register tools
from app.mcp.tools.add_task import add_task
from app.mcp.tools.list_tasks import list_tasks
from app.mcp.tools.complete_task import complete_task
from app.mcp.tools.update_task import update_task
from app.mcp.tools.delete_task import delete_task

# Register add_task tool (User Story 1 - MVP)
mcp.tool()(add_task)

# Register list_tasks tool (User Story 2)
mcp.tool()(list_tasks)

# Register complete_task tool (User Story 3)
mcp.tool()(complete_task)

# Register update_task tool (User Story 4)
mcp.tool()(update_task)

# Register delete_task tool (User Story 5)
mcp.tool()(delete_task)

def run_server():
    """
    Start the MCP server with stdio transport.

    The server listens on stdin/stdout for MCP protocol messages from the agent.
    This function blocks until the server is stopped.

    Transport: stdio (standard input/output)
    - Input: JSON-RPC messages on stdin
    - Output: JSON-RPC responses on stdout
    - Logging: stderr (to avoid interfering with protocol)
    """
    mcp.run(transport="stdio")

__all__ = ["mcp", "run_server"]
