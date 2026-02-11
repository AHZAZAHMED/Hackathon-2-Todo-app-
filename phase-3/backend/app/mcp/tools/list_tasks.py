"""
MCP Tool: list_tasks

Retrieves tasks for a user with optional filtering by completion status,
pagination support, and ordering by creation date (newest first).

Contract: specs/001-mcp-task-server/contracts/list_tasks.md
Priority: P2 (Essential for viewing tasks)
"""

from sqlmodel import Session, select
from typing import Dict, Any, Optional, List

from app.database import engine
from app.models.task import Task
from app.mcp.utils import (
    error_response,
    validate_user_id,
    validate_status,
)


async def list_tasks(
    user_id: str,
    status: str = "all",
    limit: int = 100
) -> List[Dict[str, Any]] | Dict[str, str]:
    """
    Retrieve tasks for a user, optionally filtered by completion status.

    Args:
        user_id: The authenticated user's identifier (from JWT)
        status: Filter by status - "all", "pending", or "completed" (default: "all")
        limit: Maximum number of tasks to return (default: 100, max: 1000)

    Returns:
        Success: Array of task objects ordered by created_at DESC (newest first)
        Error: {"error": str}

    Examples:
        >>> await list_tasks("user123", "pending")
        [{"id": 1, "title": "Buy groceries", "completed": false, ...}]

        >>> await list_tasks("user123", "invalid")
        {"error": "status must be 'all', 'pending', or 'completed'"}
    """
    # T022: Input validation
    # Validate user_id
    error = validate_user_id(user_id)
    if error:
        return error

    # Validate status
    error = validate_status(status)
    if error:
        return error

    # T023: Validate and enforce pagination limit
    if limit is None:
        limit = 100  # Default limit

    if limit < 1:
        return error_response("limit must be at least 1")

    if limit > 1000:
        limit = 1000  # Enforce maximum limit

    # T028: Error handling for database errors
    try:
        with Session(engine) as session:
            # T026: User isolation filtering - base query
            query = select(Task).where(Task.user_id == user_id)

            # T025: Status filtering
            if status == "pending":
                query = query.where(Task.completed == False)
            elif status == "completed":
                query = query.where(Task.completed == True)
            # "all" - no additional filter needed

            # T024: Task ordering by created_at DESC (newest first)
            query = query.order_by(Task.created_at.desc())

            # T023: Apply pagination limit
            query = query.limit(limit)

            # Execute query
            result = session.exec(query)
            tasks = result.all()

            # T027: Response format - array of task objects
            return [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat() + "Z",
                    "updated_at": task.updated_at.isoformat() + "Z"
                }
                for task in tasks
            ]

    except Exception as e:
        # T028: Database error handling
        # Log error to stderr (doesn't interfere with stdio protocol)
        import sys
        print(f"Database error in list_tasks: {str(e)}", file=sys.stderr)
        return error_response("service unavailable")


__all__ = ["list_tasks"]
