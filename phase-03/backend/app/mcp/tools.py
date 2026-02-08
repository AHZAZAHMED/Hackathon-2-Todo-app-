"""MCP tools for task management operations."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select
from app.database import engine
from app.models.task import Task as TaskModel


class Task(BaseModel):
    """Pydantic model for task data returned by MCP tools."""
    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: str
    updated_at: str

    class Config:
        schema_extra = {
            "example": {
                "id": 123,
                "title": "Buy milk",
                "description": "Get 2% milk from store",
                "completed": False,
                "created_at": "2026-02-08T10:30:00Z",
                "updated_at": "2026-02-08T10:30:00Z"
            }
        }


def add_task(user_id: str, title: str, description: str = "") -> Task:
    """
    Creates a new task for the user.

    MCP tool that performs database INSERT operation.
    Only this tool is allowed to create tasks.

    Args:
        user_id: User ID from JWT (passed by agent context)
        title: Task title (required, max 500 characters)
        description: Task description (optional)

    Returns:
        Task: Created task with all fields

    Raises:
        ValueError: If title is empty or too long
        Exception: If database operation fails
    """
    # Validate inputs
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")

    if len(title) > 500:
        raise ValueError("Title must be 500 characters or less")

    # Use SQLModel to create task
    with Session(engine) as session:
        task = TaskModel(
            user_id=user_id,
            title=title.strip(),
            description=description.strip() if description else "",
            completed=False
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        # Return as Pydantic model for agent
        return Task(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat()
        )


def list_tasks(user_id: str, completed: Optional[bool] = None) -> List[Task]:
    """
    Lists all tasks for the user.

    MCP tool that performs database SELECT operation.
    Filters by completion status if specified.

    Args:
        user_id: User ID from JWT
        completed: Optional filter by completion status

    Returns:
        List[Task]: List of tasks (empty if no tasks)
    """
    with Session(engine) as session:
        query = select(TaskModel).where(TaskModel.user_id == user_id)

        # Apply completion filter if specified
        if completed is not None:
            query = query.where(TaskModel.completed == completed)

        # Order by created_at descending (newest first)
        query = query.order_by(TaskModel.created_at.desc())

        tasks = session.exec(query).all()

        # Convert to Pydantic models
        return [
            Task(
                id=task.id,
                title=task.title,
                description=task.description,
                completed=task.completed,
                created_at=task.created_at.isoformat(),
                updated_at=task.updated_at.isoformat()
            )
            for task in tasks
        ]


def complete_task(user_id: str, task_id: int) -> Task:
    """
    Toggles task completion status.

    MCP tool that performs database UPDATE operation.
    Only this tool is allowed to update task completion.

    Args:
        user_id: User ID from JWT
        task_id: ID of task to toggle

    Returns:
        Task: Updated task object

    Raises:
        ValueError: If task not found or doesn't belong to user
    """
    with Session(engine) as session:
        task = session.exec(
            select(TaskModel)
            .where(TaskModel.id == task_id)
            .where(TaskModel.user_id == user_id)
        ).first()

        if not task:
            raise ValueError(f"Task {task_id} not found or access denied")

        # Toggle completion status
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

        return Task(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat()
        )


def delete_task(user_id: str, task_id: int) -> bool:
    """
    Deletes a task.

    MCP tool that performs database DELETE operation.
    Only this tool is allowed to delete tasks.

    Args:
        user_id: User ID from JWT
        task_id: ID of task to delete

    Returns:
        bool: True if deleted successfully

    Raises:
        ValueError: If task not found or doesn't belong to user
    """
    with Session(engine) as session:
        task = session.exec(
            select(TaskModel)
            .where(TaskModel.id == task_id)
            .where(TaskModel.user_id == user_id)
        ).first()

        if not task:
            raise ValueError(f"Task {task_id} not found or access denied")

        session.delete(task)
        session.commit()

        return True


def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Task:
    """
    Updates task title and/or description.

    MCP tool that performs database UPDATE operation.
    Only this tool is allowed to update task content.

    Args:
        user_id: User ID from JWT
        task_id: ID of task to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        Task: Updated task object

    Raises:
        ValueError: If task not found, doesn't belong to user, or no updates provided
    """
    if title is None and description is None:
        raise ValueError("Must provide at least one field to update")

    with Session(engine) as session:
        task = session.exec(
            select(TaskModel)
            .where(TaskModel.id == task_id)
            .where(TaskModel.user_id == user_id)
        ).first()

        if not task:
            raise ValueError(f"Task {task_id} not found or access denied")

        # Update fields if provided
        if title is not None:
            if not title.strip():
                raise ValueError("Title cannot be empty")
            if len(title) > 500:
                raise ValueError("Title must be 500 characters or less")
            task.title = title.strip()

        if description is not None:
            task.description = description.strip()

        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

        return Task(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat()
        )
