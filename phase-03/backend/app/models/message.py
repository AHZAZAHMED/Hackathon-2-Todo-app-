"""Message SQLModel for chat functionality."""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"

    def __str__(self):
        """Return lowercase value for database storage."""
        return self.value


class Message(SQLModel, table=True):
    """
    Represents a single message in a conversation.

    Messages are append-only (never updated or deleted).
    Stores message content and metadata for conversation history.
    """
    __tablename__ = "messages"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique message identifier"
    )

    # Foreign Key to Conversation
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True,
        description="Parent conversation ID"
    )

    # Message Data
    role: str = Field(
        nullable=False,
        description="Message sender: 'user' or 'assistant'"
    )

    content: str = Field(
        nullable=False,
        description="Message text content (max 10,000 characters)"
    )

    # Timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Message creation timestamp"
    )

    # Relationships
    conversation: Optional["Conversation"] = Relationship(
        back_populates="messages"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "user",
                "content": "Add a task to buy milk",
                "created_at": "2026-02-08T10:30:00Z"
            }
        }
