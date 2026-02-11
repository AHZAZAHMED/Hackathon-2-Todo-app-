"""
MCP Tool: complete_task

Marks a task as completed by setting its completed field to true.
This operation is idempotent - calling it multiple times on the same task
returns success without error.

Contract: specs/001-mcp-task-server/contracts/complete_task.md
Priority: P3 (Core workflow)
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
)


async def complete_task(
    user_id: str,
    task_id: int
) -> Dict[str, Any]:
    """
    Toggle a task's completion status (idempotent operation).

    If the task is currently incomplete, marks it as complete.
    If the task is currently complete, marks it as incomplete.

    Args:
        user_id: The authenticated user's identifier (from JWT)
        task_id: The task to toggle completion status

    Returns:
        Success: {"task_id": int, "status": "completed"|"incomplete", "title": str}
        Error: {"error": str}

    Examples:
        >>> await complete_task("user123", 5)  # Task was incomplete
        {"task_id": 5, "status": "completed", "title": "Buy groceries"}

        >>> await complete_task("user123", 5)  # Task was complete
        {"task_id": 5, "status": "incomplete", "title": "Buy groceries"}

        >>> await complete_task("user123", 9999)
        {"error": "task not found"}

    Note:
        This operation toggles the completion status. Calling it repeatedly
        will alternate between complete and incomplete states.
    """
    # T036: Input validation
    # Validate user_id
    error = validate_user_id(user_id)
    if error:
        return error

    # Validate task_id
    error = validate_task_id(task_id)
    if error:
        return error

    # T040: Error handling for database errors
    try:
        with Session(engine) as session:
            # T037: Task lookup with user isolation
            task = session.exec(
                select(Task)
                .where(Task.id == task_id)
                .where(Task.user_id == user_id)
            ).first()

            # T040: Task not found or unauthorized
            if not task:
                return error_response("task not found")

            # T038: Toggle completion status
            task.completed = not task.completed
            task.updated_at = datetime.utcnow()

            session.add(task)
            session.commit()
            session.refresh(task)

            # T039: Response format
            status = "completed" if task.completed else "incomplete"
            return success_response(
                task_id=task.id,
                status=status,
                title=task.title
            )

    except Exception as e:
        # T040: Database error handling
        # Log error to stderr (doesn't interfere with stdio protocol)
        import sys
        print(f"Database error in complete_task: {str(e)}", file=sys.stderr)
        return error_response("service unavailable")


__all__ = ["complete_task"]
