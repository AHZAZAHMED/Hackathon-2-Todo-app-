"""
MCP Tools Package

This package contains the individual MCP tool implementations for task management.

Each tool is a stateless async function that:
- Receives user_id as a parameter (from JWT)
- Performs database operations via SQLModel
- Enforces user isolation on all queries
- Returns structured responses (success or error)

Tools:
- add_task: Create new tasks
- list_tasks: Retrieve tasks with filtering and pagination
- update_task: Modify task details
- complete_task: Mark tasks as completed (idempotent)
- delete_task: Remove tasks (non-idempotent)
"""

__all__ = [
    "add_task",
    "list_tasks",
    "update_task",
    "complete_task",
    "delete_task",
]
