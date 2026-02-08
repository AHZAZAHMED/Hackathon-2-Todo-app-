"""
Task CRUD API routes.
Implements all task management endpoints with JWT authentication and user isolation.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, create_engine, select
from typing import Dict, Any, List
from datetime import datetime

from app.auth.dependencies import get_current_user
from app.models.task import Task
from app.models.user import User  # Import User model so SQLAlchemy can resolve FK
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.config import DATABASE_URL

# Create database engine
engine = create_engine(DATABASE_URL, echo=False)

# Create router
router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("/", response_model=Dict[str, TaskResponse], status_code=201)
async def create_task(
    task_data: TaskCreate,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new task for the authenticated user.

    **Authentication**: Requires valid JWT token in Authorization header.

    **Request Body**:
    - title (string, required): Task title (1-500 characters)
    - description (string, optional): Task description

    **Response**: 201 Created with task data

    **Errors**:
    - 401 Unauthorized: Missing or invalid JWT token
    - 422 Unprocessable Entity: Validation error (empty title, too long, etc.)
    - 503 Service Unavailable: Database connection error

    **Security**: user_id is extracted from JWT token, never from request body.
    """
    try:
        with Session(engine) as session:
            # Create task with user_id from JWT (NEVER from request body)
            task = Task(
                user_id=user["user_id"],  # From JWT claims
                title=task_data.title,
                description=task_data.description,
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            session.add(task)
            session.commit()
            session.refresh(task)

            return {"data": task}

    except Exception as e:
        # Log the actual error for debugging
        import traceback
        print(f"[ERROR] Database error: {type(e).__name__}: {e}")
        print(traceback.format_exc())

        raise HTTPException(
            status_code=503,
            detail={
                "code": "SERVICE_UNAVAILABLE",
                "message": "Database error occurred"
            }
        )


@router.get("/", response_model=Dict[str, List[TaskResponse]])
async def list_tasks(user: Dict[str, Any] = Depends(get_current_user)):
    """
    List all tasks for the authenticated user.

    **Authentication**: Requires valid JWT token in Authorization header.

    **Response**: 200 OK with array of tasks (newest first)

    **Errors**:
    - 401 Unauthorized: Missing or invalid JWT token
    - 503 Service Unavailable: Database connection error

    **Security**: Only returns tasks belonging to authenticated user.
    """
    try:
        with Session(engine) as session:
            # Filter by user_id from JWT for user isolation
            tasks = session.exec(
                select(Task)
                .where(Task.user_id == user["user_id"])
                .order_by(Task.created_at.desc())
            ).all()

            return {"data": tasks}

    except Exception as e:
        # Log the actual error for debugging
        import traceback
        print(f"[ERROR] Database error: {type(e).__name__}: {e}")
        print(traceback.format_exc())

        raise HTTPException(
            status_code=503,
            detail={
                "code": "SERVICE_UNAVAILABLE",
                "message": "Database error occurred"
            }
        )


@router.get("/{task_id}", response_model=Dict[str, TaskResponse])
async def get_task(
    task_id: int,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a single task by ID.

    **Authentication**: Requires valid JWT token in Authorization header.

    **Path Parameters**:
    - task_id (integer): Task ID

    **Response**: 200 OK with task data

    **Errors**:
    - 401 Unauthorized: Missing or invalid JWT token
    - 404 Not Found: Task doesn't exist or doesn't belong to user
    - 503 Service Unavailable: Database connection error

    **Security**: Returns 404 if task doesn't belong to user (not 403).
    """
    try:
        with Session(engine) as session:
            # Filter by both task_id AND user_id for user isolation
            task = session.exec(
                select(Task)
                .where(Task.id == task_id)
                .where(Task.user_id == user["user_id"])
            ).first()

            if not task:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "code": "NOT_FOUND",
                        "message": "Task not found"
                    }
                )

            return {"data": task}

    except HTTPException:
        raise
    except Exception as e:
        # Log the actual error for debugging
        import traceback
        print(f"[ERROR] Database error: {type(e).__name__}: {e}")
        print(traceback.format_exc())

        raise HTTPException(
            status_code=503,
            detail={
                "code": "SERVICE_UNAVAILABLE",
                "message": "Database error occurred"
            }
        )


@router.put("/{task_id}", response_model=Dict[str, TaskResponse])
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update an existing task's title and description.

    **Authentication**: Requires valid JWT token in Authorization header.

    **Path Parameters**:
    - task_id (integer): Task ID

    **Request Body**:
    - title (string, required): New task title (1-500 characters)
    - description (string, optional): New task description

    **Response**: 200 OK with updated task data

    **Errors**:
    - 401 Unauthorized: Missing or invalid JWT token
    - 404 Not Found: Task doesn't exist or doesn't belong to user
    - 422 Unprocessable Entity: Validation error
    - 503 Service Unavailable: Database connection error

    **Security**: Only updates tasks belonging to authenticated user.
    """
    try:
        with Session(engine) as session:
            # Filter by both task_id AND user_id for user isolation
            task = session.exec(
                select(Task)
                .where(Task.id == task_id)
                .where(Task.user_id == user["user_id"])
            ).first()

            if not task:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "code": "NOT_FOUND",
                        "message": "Task not found"
                    }
                )

            # Update fields
            task.title = task_data.title
            task.description = task_data.description
            task.updated_at = datetime.utcnow()

            session.add(task)
            session.commit()
            session.refresh(task)

            return {"data": task}

    except HTTPException:
        raise
    except Exception as e:
        # Log the actual error for debugging
        import traceback
        print(f"[ERROR] Database error: {type(e).__name__}: {e}")
        print(traceback.format_exc())

        raise HTTPException(
            status_code=503,
            detail={
                "code": "SERVICE_UNAVAILABLE",
                "message": "Database error occurred"
            }
        )


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Permanently delete a task.

    **Authentication**: Requires valid JWT token in Authorization header.

    **Path Parameters**:
    - task_id (integer): Task ID

    **Response**: 204 No Content (empty body)

    **Errors**:
    - 401 Unauthorized: Missing or invalid JWT token
    - 404 Not Found: Task doesn't exist or doesn't belong to user
    - 503 Service Unavailable: Database connection error

    **Security**: Only deletes tasks belonging to authenticated user.
    """
    try:
        with Session(engine) as session:
            # Filter by both task_id AND user_id for user isolation
            task = session.exec(
                select(Task)
                .where(Task.id == task_id)
                .where(Task.user_id == user["user_id"])
            ).first()

            if not task:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "code": "NOT_FOUND",
                        "message": "Task not found"
                    }
                )

            session.delete(task)
            session.commit()

            return None  # 204 No Content

    except HTTPException:
        raise
    except Exception as e:
        # Log the actual error for debugging
        import traceback
        print(f"[ERROR] Database error: {type(e).__name__}: {e}")
        print(traceback.format_exc())

        raise HTTPException(
            status_code=503,
            detail={
                "code": "SERVICE_UNAVAILABLE",
                "message": "Database error occurred"
            }
        )


@router.patch("/{task_id}/complete", response_model=Dict[str, TaskResponse])
async def toggle_task_completion(
    task_id: int,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Toggle task completion status (true ↔ false).

    **Authentication**: Requires valid JWT token in Authorization header.

    **Path Parameters**:
    - task_id (integer): Task ID

    **Response**: 200 OK with updated task data

    **Errors**:
    - 401 Unauthorized: Missing or invalid JWT token
    - 404 Not Found: Task doesn't exist or doesn't belong to user
    - 503 Service Unavailable: Database connection error

    **Security**: Only toggles tasks belonging to authenticated user.
    """
    try:
        with Session(engine) as session:
            # Filter by both task_id AND user_id for user isolation
            task = session.exec(
                select(Task)
                .where(Task.id == task_id)
                .where(Task.user_id == user["user_id"])
            ).first()

            if not task:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "code": "NOT_FOUND",
                        "message": "Task not found"
                    }
                )

            # Toggle completion status
            task.completed = not task.completed
            task.updated_at = datetime.utcnow()

            session.add(task)
            session.commit()
            session.refresh(task)

            return {"data": task}

    except HTTPException:
        raise
    except Exception as e:
        # Log the actual error for debugging
        import traceback
        print(f"[ERROR] Database error: {type(e).__name__}: {e}")
        print(traceback.format_exc())

        raise HTTPException(
            status_code=503,
            detail={
                "code": "SERVICE_UNAVAILABLE",
                "message": "Database error occurred"
            }
        )
