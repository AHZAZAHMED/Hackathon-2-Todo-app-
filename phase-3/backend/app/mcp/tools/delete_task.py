"""
MCP Tool: delete_task

Removes a task from the database (hard delete). This operation is non-idempotent -
calling it on an already-deleted task returns an error.

Contract: specs/001-mcp-task-server/contracts/delete_task.md
Priority: P5 (Useful for cleanup, least critical)
"""

from sqlmodel import Session, select
from typing import Dict, Any

from app.database import engine
from app.models.task import Task
from app.mcp.utils import (
    success_response,
    error_response,
    validate_user_id,
    validate_task_id,
)


async def delete_task(
    user_id: str,
    task_id: int
) -> Dict[str, Any]:
    """
    Remove a task from the database (non-idempotent operation).

    Args:
        user_id: The authenticated user's identifier (from JWT)
        task_id: The task to delete

    Returns:
        Success: {"task_id": int, "status": "deleted", "title": str}
        Error: {"error": str}

    Examples:
        >>> await delete_task("user123", 2)
        {"task_id": 2, "status": "deleted", "title": "Old task"}

        >>> await delete_task("user123", 2)  # Second call
        {"error": "task not found"}

    Note:
        This operation is NOT idempotent. Calling it on an already-deleted
        task returns an error (not success). This follows REST conventions
        where DELETE operations return 404 on subsequent calls.
    """
    # T061: Input validation
    # Validate user_id
    error = validate_user_id(user_id)
    if error:
        return error

    # Validate task_id
    error = validate_task_id(task_id)
    if error:
        return error

    # T066: Error handling for database errors
    try:
        with Session(engine) as session:
            # T062: Task lookup with user isolation
            task = session.exec(
                select(Task)
                .where(Task.id == task_id)
                .where(Task.user_id == user_id)
            ).first()

            # T066: Task not found or unauthorized
            if not task:
                return error_response("task not found")

            # T063: Capture task title before deletion for response
            task_title = task.title
            task_id_value = task.id

            # T064: Hard delete operation
            session.delete(task)
            session.commit()

            # T065: Response format with captured title
            return success_response(
                task_id=task_id_value,
                status="deleted",
                title=task_title
            )

    except Exception as e:
        # T066: Database error handling
        # Log error to stderr (doesn't interfere with stdio protocol)
        import sys
        print(f"Database error in delete_task: {str(e)}", file=sys.stderr)
        return error_response("service unavailable")


__all__ = ["delete_task"]
