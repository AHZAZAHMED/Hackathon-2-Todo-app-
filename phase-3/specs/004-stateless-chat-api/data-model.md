# Data Model: Stateless Chat API

**Feature**: 004-stateless-chat-api
**Date**: 2026-02-09
**Status**: Complete

## Overview

This document defines the data entities for the chat feature, including database schema, SQLModel class definitions, relationships, and constraints.

---

## Entity Relationship Diagram

```
┌─────────────────────┐
│       User          │
│  (Better Auth)      │
│                     │
│  - id (TEXT, PK)    │
│  - email            │
│  - name             │
└──────────┬──────────┘
           │
           │ 1:N (one user has many conversations)
           │
           ▼
┌─────────────────────┐
│   Conversation      │
│                     │
│  - id (UUID, PK)    │
│  - user_id (FK)     │
│  - title            │
│  - created_at       │
│  - updated_at       │
└──────────┬──────────┘
           │
           │ 1:N (one conversation has many messages)
           │
           ▼
┌─────────────────────┐
│      Message        │
│                     │
│  - id (UUID, PK)    │
│  - conversation_id  │
│  - role             │
│  - content          │
│  - created_at       │
└─────────────────────┘
```

---

## Entity 1: Conversation

### Purpose
Represents a chat session between a user and the AI assistant. Groups related messages together and provides conversation-level metadata.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier for the conversation |
| user_id | TEXT | NOT NULL, FOREIGN KEY → user(id) | Owner of the conversation (from Better Auth) |
| title | VARCHAR(200) | NULLABLE | Optional human-readable title (can be auto-generated or null) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the conversation was created |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the conversation was last modified (auto-updated via trigger) |

### Relationships

- **User → Conversation**: One-to-Many
  - One user can have multiple conversations
  - Foreign key: `conversation.user_id` → `user.id`
  - Cascade: ON DELETE CASCADE (delete conversations when user deleted)

- **Conversation → Message**: One-to-Many
  - One conversation contains multiple messages
  - Foreign key: `message.conversation_id` → `conversation.id`
  - Cascade: ON DELETE CASCADE (delete messages when conversation deleted)

### Indexes

```sql
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);
```

**Rationale**:
- `user_id` index: Enables fast lookup of all conversations for a user
- `created_at` index: Supports ordering conversations by recency

### Validation Rules

- `user_id` MUST exist in the `user` table (enforced by foreign key)
- `title` is optional (can be NULL)
- `created_at` and `updated_at` are automatically managed by database

### SQLModel Class Definition

```python
# app/models/conversation.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class Conversation(SQLModel, table=True):
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
```

---

## Entity 2: Message

### Purpose
Represents a single message within a conversation. Can be from either the user or the AI assistant.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier for the message |
| conversation_id | UUID | NOT NULL, FOREIGN KEY → conversations(id) | The conversation this message belongs to |
| role | VARCHAR(20) | NOT NULL, CHECK (role IN ('user', 'assistant')) | Who sent the message |
| content | TEXT | NOT NULL | The actual message text |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the message was created |

### Relationships

- **Conversation → Message**: One-to-Many
  - One conversation contains multiple messages
  - Foreign key: `message.conversation_id` → `conversation.id`
  - Cascade: ON DELETE CASCADE (delete messages when conversation deleted)

### Indexes

```sql
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at DESC);
```

**Rationale**:
- `conversation_id` index: Enables fast lookup of all messages in a conversation
- `created_at` index: Supports ordering messages chronologically
- Composite index: Optimizes the common query pattern (get messages for conversation ordered by time)

### Validation Rules

- `conversation_id` MUST exist in the `conversations` table (enforced by foreign key)
- `role` MUST be either 'user' or 'assistant' (enforced by CHECK constraint)
- `content` MUST NOT be empty (enforced at application level)
- `content` length MUST be between 1 and 2000 characters (enforced at application level)

### State Transitions

Messages are immutable once created. No updates or deletions at the message level (only cascade delete when conversation is deleted).

### SQLModel Class Definition

```python
# app/models/message.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: MessageRole = Field(sa_column_kwargs={"nullable": False})
    content: str = Field(sa_column_kwargs={"nullable": False})
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440000",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "user",
                "content": "Hello, can you help me with my tasks?",
                "created_at": "2026-02-09T10:00:00Z"
            }
        }
```

---

## Database Schema (SQL)

### Complete Migration Script

```sql
-- backend/migrations/003_create_chat_tables.sql

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    title VARCHAR(200),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Foreign key to Better Auth user table
    CONSTRAINT fk_conversations_user
        FOREIGN KEY (user_id)
        REFERENCES "user"(id)
        ON DELETE CASCADE
);

-- Create indexes for conversations
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Foreign key to conversations table
    CONSTRAINT fk_messages_conversation
        FOREIGN KEY (conversation_id)
        REFERENCES conversations(id)
        ON DELETE CASCADE
);

-- Create indexes for messages
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created ON messages(conversation_id, created_at DESC);

-- Add updated_at trigger for conversations table
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## Query Patterns

### Common Queries

**1. Get all conversations for a user (ordered by most recent)**:
```sql
SELECT * FROM conversations
WHERE user_id = $1
ORDER BY updated_at DESC
LIMIT 20;
```

**2. Get last 50 messages for a conversation (oldest first)**:
```sql
SELECT * FROM messages
WHERE conversation_id = $1
ORDER BY created_at ASC
LIMIT 50;
```

**3. Create new conversation**:
```sql
INSERT INTO conversations (user_id, title)
VALUES ($1, $2)
RETURNING *;
```

**4. Create new message**:
```sql
INSERT INTO messages (conversation_id, role, content)
VALUES ($1, $2, $3)
RETURNING *;
```

**5. Check if conversation belongs to user**:
```sql
SELECT EXISTS(
    SELECT 1 FROM conversations
    WHERE id = $1 AND user_id = $2
);
```

---

## Data Integrity Rules

### Foreign Key Constraints

1. **conversations.user_id → user.id**
   - Ensures every conversation belongs to a valid user
   - CASCADE DELETE: When user deleted, all their conversations are deleted

2. **messages.conversation_id → conversations.id**
   - Ensures every message belongs to a valid conversation
   - CASCADE DELETE: When conversation deleted, all its messages are deleted

### Check Constraints

1. **messages.role CHECK (role IN ('user', 'assistant'))**
   - Ensures role is always one of the two valid values
   - Prevents invalid role values at database level

### Application-Level Validation

1. **Message content length**: 1-2000 characters (validated in FastAPI endpoint)
2. **User isolation**: Backend ensures user can only access their own conversations
3. **Conversation ownership**: Backend verifies conversation belongs to authenticated user

---

## Performance Considerations

### Index Strategy

- **Primary keys (id)**: Automatic B-tree index for fast lookups
- **Foreign keys**: Indexed for fast JOIN operations
- **Composite index (conversation_id, created_at)**: Optimizes the most common query pattern

### Query Optimization

- **LIMIT 50 on message queries**: Prevents loading excessive data
- **ORDER BY created_at DESC with index**: Efficient sorting using index
- **Connection pooling**: Reuses database connections for better performance

### Scalability

- **Stateless design**: No server-side caching, all data from database
- **Horizontal scaling**: Multiple backend instances can serve requests independently
- **Database connection pooling**: Configured for 10 connections with 20 overflow

---

## Migration Rollback

If migration needs to be rolled back:

```sql
-- Rollback script (use with caution)
DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
DROP FUNCTION IF EXISTS update_updated_at_column();
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
```

---

**Status**: ✅ Data model complete. Ready for API contract definition.
