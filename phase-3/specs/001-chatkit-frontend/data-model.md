# Data Model: ChatKit Frontend Integration

**Feature**: 001-chatkit-frontend
**Date**: 2026-02-09
**Scope**: Frontend-only (ephemeral, no backend persistence)

## Overview

This document defines the data entities used in the ChatKit frontend integration. All entities are **frontend-only** and **ephemeral** - they exist only in browser memory and session storage during the user's session. No backend persistence is included in this spec.

---

## Entity: ChatMessage

Represents a single message in the conversation (user or assistant).

### Fields

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `id` | string | Yes | UUID format | Unique identifier for the message |
| `role` | "user" \| "assistant" | Yes | Enum | Who sent the message |
| `content` | string | Yes | 1-500 characters | Message text content |
| `timestamp` | Date | Yes | Valid date | When the message was created |
| `status` | "sending" \| "sent" \| "failed" | Yes | Enum | Current message status |
| `error` | string \| null | No | Max 200 chars | Error message if status is "failed" |

### Validation Rules

- **content**: Must be 1-500 characters (enforced by FR-018)
- **role**: Must be exactly "user" or "assistant"
- **status**: Must be one of the three valid states
- **error**: Only populated when status is "failed"

### State Transitions

```
sending → sent (success)
sending → failed (error)
failed → sending (retry)
```

### TypeScript Definition

```typescript
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  status: 'sending' | 'sent' | 'failed';
  error: string | null;
}
```

### Example

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "user",
  "content": "Hello, can you help me with my tasks?",
  "timestamp": "2026-02-09T10:30:00.000Z",
  "status": "sent",
  "error": null
}
```

---

## Entity: ChatSession

Represents the current chat interaction state.

### Fields

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `messages` | ChatMessage[] | Yes | Array | All messages in chronological order |
| `isOpen` | boolean | Yes | - | Whether chat window is currently open |
| `isLoading` | boolean | Yes | - | Whether waiting for assistant response |
| `error` | string \| null | No | Max 200 chars | Global error message (e.g., backend unreachable) |

### Validation Rules

- **messages**: Must be in chronological order (sorted by timestamp)
- **isOpen**: Persisted in session storage (FR-016)
- **isLoading**: True only when waiting for backend response
- **error**: User-friendly message, no technical details

### TypeScript Definition

```typescript
export interface ChatSession {
  messages: ChatMessage[];
  isOpen: boolean;
  isLoading: boolean;
  error: string | null;
}
```

### Example

```json
{
  "messages": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "role": "user",
      "content": "Hello",
      "timestamp": "2026-02-09T10:30:00.000Z",
      "status": "sent",
      "error": null
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "role": "assistant",
      "content": "Hi! How can I help you today?",
      "timestamp": "2026-02-09T10:30:02.000Z",
      "status": "sent",
      "error": null
    }
  ],
  "isOpen": true,
  "isLoading": false,
  "error": null
}
```

---

## Entity: ChatStorageState

Represents the persisted state in session storage.

### Fields

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `isOpen` | boolean | Yes | - | Chat window open/closed state |
| `messages` | ChatMessage[] | No | - | Preserved messages (only on token expiry) |

### Storage Keys

- **State Key**: `chatkit_state`
- **Messages Key**: `chatkit_messages`

### Lifecycle

- **Created**: When user first interacts with chat
- **Updated**: On every state change (window open/close, token expiry)
- **Cleared**: On browser session end, manual logout, or successful re-authentication

### TypeScript Definition

```typescript
export interface ChatStorageState {
  isOpen: boolean;
  messages?: ChatMessage[]; // Only present when preserving on token expiry
}
```

### Example (Session Storage)

```json
// sessionStorage.getItem('chatkit_state')
{
  "isOpen": true
}

// sessionStorage.getItem('chatkit_messages') - only on token expiry
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "role": "user",
    "content": "Hello",
    "timestamp": "2026-02-09T10:30:00.000Z",
    "status": "sent",
    "error": null
  }
]
```

---

## Relationships

```
ChatSession (1) ──> (0..*) ChatMessage
     │
     └──> ChatStorageState (persisted)
```

- **ChatSession** contains multiple **ChatMessage** entities
- **ChatSession** state is persisted as **ChatStorageState** in session storage
- No relationships with backend entities (frontend-only scope)

---

## Data Flow

### Message Send Flow

```
1. User types message (content validated: 1-500 chars)
2. Create ChatMessage with status="sending"
3. Add to ChatSession.messages[]
4. Send to backend via POST /api/chat
5. On success: Update status="sent", add assistant response
6. On failure: Update status="failed", set error message
```

### State Persistence Flow

```
1. User opens/closes chat window
2. Update ChatSession.isOpen
3. Save to sessionStorage (chatkit_state)
4. On page navigation: Load from sessionStorage
5. Restore ChatSession.isOpen state
```

### Token Expiry Flow

```
1. Message send fails with 401 error
2. Save ChatSession.messages to sessionStorage (chatkit_messages)
3. Redirect to login page
4. On successful re-authentication:
5. Load messages from sessionStorage
6. Restore ChatSession.messages
7. Clear sessionStorage (chatkit_messages)
```

---

## Storage Considerations

### Session Storage Limits

- **Typical Limit**: 5-10 MB per origin
- **Our Usage**: ~1-2 KB per message (500 chars + metadata)
- **Max Messages**: ~5000-10000 messages (far exceeds single session needs)

### Storage Strategy

- **State**: Always persisted (tiny: ~50 bytes)
- **Messages**: Only persisted on token expiry (temporary)
- **Cleanup**: Clear messages after successful re-authentication

### Error Handling

```typescript
try {
  sessionStorage.setItem(key, JSON.stringify(data));
} catch (error) {
  if (error.name === 'QuotaExceededError') {
    // Clear old messages, retry
    sessionStorage.removeItem('chatkit_messages');
    sessionStorage.setItem(key, JSON.stringify(data));
  }
}
```

---

## Validation Summary

| Entity | Validation | Enforcement |
|--------|------------|-------------|
| ChatMessage.content | 1-500 characters | Client-side (FR-018, FR-019, FR-020) |
| ChatMessage.role | "user" \| "assistant" | TypeScript type system |
| ChatMessage.status | Valid enum value | TypeScript type system |
| ChatSession.messages | Chronological order | Maintained by append-only pattern |
| ChatStorageState | Valid JSON | sessionStorage API + try/catch |

---

## Future Considerations (Out of Scope)

The following are **NOT** included in this spec but may be relevant for future phases:

- **Backend Persistence**: Storing conversations in database
- **Message History**: Loading previous conversations
- **Multi-Device Sync**: Syncing chat state across devices
- **Message Editing**: Allowing users to edit sent messages
- **Message Deletion**: Allowing users to delete messages
- **Rich Content**: Supporting markdown, code blocks, images
- **Conversation Threads**: Multiple parallel conversations

---

## Summary

- **2 Core Entities**: ChatMessage, ChatSession
- **1 Storage Entity**: ChatStorageState
- **Frontend-Only**: No backend persistence
- **Ephemeral**: Cleared on session end
- **Validated**: Client-side validation for all constraints
- **Type-Safe**: Full TypeScript definitions
