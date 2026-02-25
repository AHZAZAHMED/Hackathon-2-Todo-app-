"""
MCP Task Server Package

This package contains the MCP (Model Context Protocol) server implementation
for task management operations. The MCP server exposes 5 stateless tools that
the OpenAI Agent can invoke to manage tasks.

Tools:
- add_task: Create new tasks
- list_tasks: Retrieve tasks with filtering and pagination
- update_task: Modify task details
- complete_task: Mark tasks as completed
- delete_task: Remove tasks

All tools enforce user isolation and persist data to PostgreSQL via SQLModel.

Note: The MCP server (server.py) should only be imported when running the
standalone MCP server process, not when importing tool functions into the
FastAPI application.
"""

__all__ = []
