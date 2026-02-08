"""Message service for managing chat messages."""
from sqlmodel import Session, select
from typing import List, Dict
from uuid import UUID
from app.models.message import Message, MessageRole


def store_message(
    session: Session,
    conversation_id: UUID,
    role: str,
    content: str
) -> Message:
    """
    Store a new message in the conversation.

    Messages are append-only (never updated).
    Automatically updates conversation.updated_at via database trigger.

    Args:
        session: Database session
        conversation_id: UUID of parent conversation
        role: Message role (user or assistant)
        content: Message text content

    Returns:
        Message: Created message with ID and timestamp
    """
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )

    session.add(message)
    session.commit()
    session.refresh(message)

    return message


def load_conversation_history(
    session: Session,
    conversation_id: UUID,
    max_tokens: int = 2000
) -> List[Dict[str, str]]:
    """
    Load conversation history up to max_tokens limit.

    Uses tiktoken for accurate token counting.
    Returns messages in chronological order (oldest first).
    Loads newest messages first, stops when token limit reached.

    Args:
        session: Database session
        conversation_id: UUID of conversation
        max_tokens: Maximum tokens to load (default 2000)

    Returns:
        List[Dict]: Messages in format [{"role": "user/assistant", "content": "..."}]
    """
    import tiktoken

    # Get encoding for token counting (compatible with Gemini)
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    # Load messages (newest first)
    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
    ).all()

    # Build message list with token counting
    result = []
    total_tokens = 0

    for msg in messages:
        # Count tokens in message
        msg_tokens = len(encoding.encode(msg.content))

        # Stop if adding this message exceeds limit
        if total_tokens + msg_tokens > max_tokens:
            break

        # Insert at beginning (chronological order)
        result.insert(0, {
            "role": msg.role,
            "content": msg.content
        })
        total_tokens += msg_tokens

    return result
