"""
Task model for database persistence.
Represents a user's task item with title, description, and completion status.
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Task(SQLModel, table=True):
    """
    Task entity with user isolation.

    Each task belongs to exactly one user (enforced by foreign key).
    All queries MUST filter by user_id from JWT token.
    """

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(nullable=False, index=True)  # FK constraint exists in DB schema
    title: str = Field(max_length=500, nullable=False)
    description: Optional[str] = Field(default=None, nullable=True)
    completed: bool = Field(default=False, nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        """Pydantic configuration."""
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
