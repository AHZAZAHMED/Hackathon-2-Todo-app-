"""
MCP Tool: update_task

Modifies task title and/or description. Supports partial updates where only
the provided fields are modified, leaving other fields unchanged.

Contract: specs/001-mcp-task-server/contracts/update_task.md
Priority: P4 (Valuable but not essential)
"""

from sqlmodel import Session, select
from datetime import datetime
from typing import Dict, Any, Optional

from app.database import engine
from app.models.task import Task
from app.mcp.utils import (
    success_response,
    error_response,
    validate_user_id,
    validate_task_id,
    validate_title,
)


async def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Modify task title or description (partial updates supported).

    Args:
        user_id: The authenticated user's identifier (from JWT)
        task_id: The task to update
        title: New task title (optional, max 500 characters)
        description: New task description (optional)

    Returns:
        Success: {"task_id": int, "status": "updated", "title": str}
        Error: {"error": str}

    Examples:
        >>> await update_task("user123", 1, title="New title")
        {"task_id": 1, "status": "updated", "title": "New title"}

        >>> await update_task("user123", 1, description="New description")
        {"task_id": 1, "status": "updated", "title": "Original title"}

        >>> await update_task("user123", 1)
        {"error": "at least one of title or description must be provided"}
    """
    # T047: Input validation
    # Validate user_id
    error = validate_user_id(user_id)
    if error:
        return error

    # Validate task_id
    error = validate_task_id(task_id)
    if error:
        return error

    # T047: At least one field must be provided
    if title is None and description is None:
        return error_response("at least one of title or description must be provided")

    # T050: Validate title if provided
    if title is not None:
        error = validate_title(title)
        if error:
            return error
        # Trim title whitespace
        title = title.strip()

    # T053: Error handling for database errors
    try:
        with Session(engine) as session:
            # T048: Task lookup with user isolation
            task = session.exec(
                select(Task)
                .where(Task.id == task_id)
                .where(Task.user_id == user_id)
            ).first()

            # T053: Task not found or unauthorized
            if not task:
                return error_response("task not found")

            # T049: Partial update logic - update only provided fields
            if title is not None:
                task.title = title

            if description is not None:
                task.description = description

            # T051: Update timestamp
            task.updated_at = datetime.utcnow()

            session.add(task)
            session.commit()
            session.refresh(task)

            # T052: Response format
            return success_response(
                task_id=task.id,
                status="updated",
                title=task.title
            )

    except Exception as e:
        # T053: Database error handling
        # Log error to stderr (doesn't interfere with stdio protocol)
        import sys
        print(f"Database error in update_task: {str(e)}", file=sys.stderr)
        return error_response("service unavailable")


__all__ = ["update_task"]
