"""Conversation SQLModel for chat functionality."""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4


class Conversation(SQLModel, table=True):
    """
    Represents a chat conversation between user and AI agent.

    One conversation per user (auto-created on first message).
    Stores conversation metadata and relationships to messages.
    """
    __tablename__ = "conversations"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique conversation identifier"
    )

    # Foreign Key to User
    user_id: str = Field(
        foreign_key="user.id",
        nullable=False,
        index=True,
        description="User ID from Better Auth (TEXT/CUID format)"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Conversation creation timestamp"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="Last message timestamp"
    )

    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "clx1234567890abcdefghijk",
                "created_at": "2026-02-08T10:30:00Z",
                "updated_at": "2026-02-08T10:35:00Z"
            }
        }
