"""Conversation service for managing chat conversations."""
from sqlmodel import Session, select
from typing import Optional
from uuid import UUID
from app.models.conversation import Conversation


def get_or_create_conversation(
    session: Session,
    user_id: str,
    conversation_id: Optional[UUID] = None
) -> Conversation:
    """
    Get existing conversation or create new one for user.

    Single conversation per user (auto-created on first message).
    If conversation_id provided, validates it belongs to user.

    Args:
        session: Database session
        user_id: User ID from JWT
        conversation_id: Optional UUID of existing conversation

    Returns:
        Conversation: Existing or newly created conversation

    Raises:
        ValueError: If conversation_id provided but doesn't belong to user
    """
    if conversation_id:
        # Try to get existing conversation
        conversation = session.get(Conversation, conversation_id)

        # Validate ownership
        if conversation and conversation.user_id == user_id:
            return conversation
        elif conversation:
            # Conversation exists but belongs to different user
            raise ValueError("Conversation not found or access denied")

    # Get or create user's conversation (single conversation per user)
    conversation = session.exec(
        select(Conversation).where(Conversation.user_id == user_id)
    ).first()

    if not conversation:
        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    return conversation
