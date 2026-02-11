"""
Conversation model for chat feature.
Represents a chat session between a user and the AI assistant.
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional


class Conversation(SQLModel, table=True):
    """
    Conversation entity - represents a chat session.

    Relationships:
    - One User has many Conversations (1:N)
    - One Conversation has many Messages (1:N)
    """
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user_123",
                "title": "Task Management Discussion",
                "created_at": "2026-02-09T10:00:00Z",
                "updated_at": "2026-02-09T10:30:00Z"
            }
        }
