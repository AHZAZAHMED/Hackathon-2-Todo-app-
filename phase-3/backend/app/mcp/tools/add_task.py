"""
MCP Tool: add_task

Creates a new task for a user with the specified title and optional description.
This is the foundational tool that enables all other task management operations.

Contract: specs/001-mcp-task-server/contracts/add_task.md
Priority: P1 (MVP)
"""

from sqlmodel import Session
from datetime import datetime
from typing import Dict, Any, Optional

from app.database import engine
from app.models.task import Task
from app.mcp.utils import (
    success_response,
    error_response,
    validate_user_id,
    validate_title,
)


async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new task for a user.

    Args:
        user_id: The authenticated user's identifier (from JWT)
        title: Task title (max 500 characters)
        description: Optional task description

    Returns:
        Success: {"task_id": int, "status": "created", "title": str}
        Error: {"error": str}

    Examples:
        >>> await add_task("user123", "Buy groceries", "Milk, eggs, bread")
        {"task_id": 1, "status": "created", "title": "Buy groceries"}

        >>> await add_task("user123", "")
        {"error": "title cannot be empty"}
    """
    # T013: Input validation
    # Validate user_id
    error = validate_user_id(user_id)
    if error:
        return error

    # Validate title
    error = validate_title(title)
    if error:
        return error

    # Trim title whitespace
    title = title.strip()

    # T014: Database insert operation with user_id
    # T016: Error handling for database errors
    try:
        with Session(engine) as session:
            # Create new task with user isolation
            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Insert into database
            session.add(task)
            session.commit()
            session.refresh(task)

            # T015: Response format
            return success_response(
                task_id=task.id,
                status="created",
                title=task.title
            )

    except Exception as e:
        # T016: Database error handling
        # Log error to stderr (doesn't interfere with stdio protocol)
        import sys
        print(f"Database error in add_task: {str(e)}", file=sys.stderr)
        return error_response("service unavailable")


__all__ = ["add_task"]
