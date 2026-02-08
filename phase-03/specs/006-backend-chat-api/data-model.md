# Data Model: Backend Chat API

**Feature**: 006-backend-chat-api
**Date**: 2026-02-08
**Status**: Complete

## Overview

This document defines the SQLModel schemas for conversation and message persistence. The data model supports stateless backend architecture with all conversation state stored in PostgreSQL.

---

## Entity Relationship Diagram

```
┌─────────────────┐
│      User       │ (Existing - Phase-2)
│  id: TEXT (PK)  │
└────────┬────────┘
         │
         │ 1:1 (one conversation per user)
         │
         ▼
┌─────────────────────────┐
│    Conversation         │
│  id: UUID (PK)          │
│  user_id: TEXT (FK)     │───┐
│  created_at: TIMESTAMP  │   │
│  updated_at: TIMESTAMP  │   │
└─────────────────────────┘   │
                              │ 1:N (many messages per conversation)
                              │
                              ▼
                    ┌──────────────────────────┐
                    │       Message            │
                    │  id: UUID (PK)           │
                    │  conversation_id: UUID   │
                    │  role: VARCHAR(20)       │
                    │  content: TEXT           │
                    │  created_at: TIMESTAMP   │
                    └──────────────────────────┘
```

---

## SQLModel Schemas

### Conversation Model

```python
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
```

### Message Model

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"

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
    role: MessageRole = Field(
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
```

---

## Database Migration (SQL)

### Migration 003: Create Chat Tables

```sql
-- Migration: 003_create_chat_tables.sql
-- Description: Creates conversations and messages tables for chat functionality
-- Date: 2026-02-08

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Foreign key constraint
    CONSTRAINT fk_conversations_user_id
        FOREIGN KEY (user_id)
        REFERENCES "user"(id)
        ON DELETE CASCADE
);

-- Create index on user_id for efficient lookups
CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- Create messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Foreign key constraint
    CONSTRAINT fk_messages_conversation_id
        FOREIGN KEY (conversation_id)
        REFERENCES conversations(id)
        ON DELETE CASCADE
);

-- Create indexes for efficient queries
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- Add trigger to update conversations.updated_at on new message
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations
    SET updated_at = NOW()
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_conversation_timestamp
    AFTER INSERT ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_timestamp();

-- Add comments for documentation
COMMENT ON TABLE conversations IS 'Stores chat conversations between users and AI agent';
COMMENT ON TABLE messages IS 'Stores individual messages within conversations';
COMMENT ON COLUMN conversations.user_id IS 'References user.id from Better Auth';
COMMENT ON COLUMN messages.role IS 'Message sender: user or assistant';
COMMENT ON COLUMN messages.content IS 'Message text content (max 10,000 characters)';
```

---

## Validation Rules

### Conversation Validation

| Field | Rule | Enforcement |
|-------|------|-------------|
| `id` | Must be valid UUID | Database (UUID type) |
| `user_id` | Must reference existing user | Database (foreign key) |
| `user_id` | Cannot be null | Database (NOT NULL) |
| `created_at` | Cannot be null | Database (NOT NULL) |
| `updated_at` | Cannot be null | Database (NOT NULL) |

### Message Validation

| Field | Rule | Enforcement |
|-------|------|-------------|
| `id` | Must be valid UUID | Database (UUID type) |
| `conversation_id` | Must reference existing conversation | Database (foreign key) |
| `conversation_id` | Cannot be null | Database (NOT NULL) |
| `role` | Must be 'user' or 'assistant' | Database (CHECK constraint) |
| `role` | Cannot be null | Database (NOT NULL) |
| `content` | Cannot be empty | Application (FastAPI validation) |
| `content` | Max 10,000 characters | Application (FastAPI validation) |
| `created_at` | Cannot be null | Database (NOT NULL) |

---

## Query Patterns

### Get or Create Conversation

```python
def get_or_create_conversation(
    session: Session,
    user_id: str,
    conversation_id: Optional[UUID] = None
) -> Conversation:
    """
    Gets existing conversation or creates new one.

    Single conversation per user (auto-created on first message).
    """
    if conversation_id:
        # Try to get existing conversation
        conversation = session.get(Conversation, conversation_id)
        if conversation and conversation.user_id == user_id:
            return conversation

    # Get or create user's conversation
    conversation = session.exec(
        select(Conversation).where(Conversation.user_id == user_id)
    ).first()

    if not conversation:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    return conversation
```

### Load Conversation History

```python
def load_conversation_history(
    session: Session,
    conversation_id: UUID,
    max_tokens: int = 2000
) -> List[dict]:
    """
    Loads conversation history up to max_tokens limit.

    Returns messages in chronological order (oldest first).
    Uses token counting to enforce limit.
    """
    import tiktoken

    # Get encoding for token counting
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
        msg_tokens = len(encoding.encode(msg.content))

        if total_tokens + msg_tokens > max_tokens:
            break

        result.insert(0, {  # Insert at beginning (chronological order)
            "role": msg.role.value,
            "content": msg.content
        })
        total_tokens += msg_tokens

    return result
```

### Store Message

```python
def store_message(
    session: Session,
    conversation_id: UUID,
    role: MessageRole,
    content: str
) -> Message:
    """
    Stores a new message in the conversation.

    Messages are append-only (never updated).
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
```

---

## Indexes and Performance

### Index Strategy

| Table | Index | Purpose | Type |
|-------|-------|---------|------|
| `conversations` | `idx_conversations_user_id` | Lookup user's conversation | B-tree |
| `messages` | `idx_messages_conversation_id` | Load conversation history | B-tree |
| `messages` | `idx_messages_created_at` | Order messages chronologically | B-tree |

### Query Performance Expectations

| Query | Expected Performance | Notes |
|-------|---------------------|-------|
| Get conversation by user_id | <10ms | Indexed lookup |
| Load 100 messages | <50ms | Indexed scan + ORDER BY |
| Insert message | <20ms | Single INSERT with trigger |
| Count conversation messages | <30ms | COUNT with indexed filter |

---

## Data Integrity

### Foreign Key Constraints

1. **conversations.user_id → user.id**
   - ON DELETE CASCADE: Deleting user deletes all conversations
   - Ensures no orphan conversations

2. **messages.conversation_id → conversations.id**
   - ON DELETE CASCADE: Deleting conversation deletes all messages
   - Ensures no orphan messages

### Cascade Behavior

```
User Deleted
    ↓
Conversations Deleted (CASCADE)
    ↓
Messages Deleted (CASCADE)
```

### Transaction Boundaries

- **Store user message + invoke agent + store assistant message**: Single transaction
- **Get or create conversation**: Separate transaction (committed before agent invocation)
- **Load history**: Read-only (no transaction needed)

---

## Testing Checklist

### Unit Tests
- [ ] Conversation model creation
- [ ] Message model creation
- [ ] Foreign key constraint enforcement
- [ ] CHECK constraint on message role
- [ ] Timestamp auto-population
- [ ] UUID generation

### Integration Tests
- [ ] Get or create conversation (new user)
- [ ] Get or create conversation (existing user)
- [ ] Store user message
- [ ] Store assistant message
- [ ] Load conversation history (empty)
- [ ] Load conversation history (100 messages)
- [ ] Load conversation history (token limit)
- [ ] Cascade delete (user → conversations → messages)

### Performance Tests
- [ ] Load 100 messages (<50ms)
- [ ] Insert message (<20ms)
- [ ] Concurrent message inserts (50 requests)

---

## Next Steps

1. ✅ Data model complete
2. ⏳ Generate contracts/chat-api.yaml (OpenAPI spec)
3. ⏳ Generate quickstart.md (setup instructions)
4. ⏳ Update agent context (add new technologies)
5. ⏳ Run /sp.tasks (generate implementation tasks)

**Data Model Status**: ✅ COMPLETE
**Ready for**: API Contract Design
