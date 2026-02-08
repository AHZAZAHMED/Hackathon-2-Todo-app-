"""
Pydantic schemas for Task API requests and responses.
Separate from SQLModel for clear request/response validation.
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional


class TaskCreate(BaseModel):
    """
    Request schema for creating a new task.

    Fields:
        title: Task title (required, 1-500 characters)
        description: Task description (optional)
    """

    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = None

    @validator('title')
    def title_not_empty(cls, v):
        """Ensure title is not just whitespace."""
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread"
            }
        }


class TaskUpdate(BaseModel):
    """
    Request schema for updating an existing task.

    Fields:
        title: New task title (required, 1-500 characters)
        description: New task description (optional)
    """

    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = None

    @validator('title')
    def title_not_empty(cls, v):
        """Ensure title is not just whitespace."""
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy organic groceries",
                "description": "From Whole Foods"
            }
        }


class TaskResponse(BaseModel):
    """
    Response schema for task data.

    Matches Task SQLModel structure for consistency.
    """

    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode for SQLModel compatibility
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "clx1234567890",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "created_at": "2026-02-06T10:00:00Z",
                "updated_at": "2026-02-06T10:00:00Z"
            }
        }
