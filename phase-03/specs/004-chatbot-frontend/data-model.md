# Data Model: Phase-3 Chatbot Frontend

**Date**: 2026-02-08
**Feature**: 004-chatbot-frontend
**Status**: Complete

## Overview

This document defines the frontend data structures for the Phase-3 chatbot interface.

**Important Note**: OpenAI ChatKit manages conversation state (messages, loading, errors) internally. The types defined here are primarily for the **custom wrapper components** (floating launcher UI state). ChatKit handles message state through its provider and components.

## Core Entities

### 1. ChatUIState (Custom - Required)

Represents the UI state of the floating launcher wrapper (separate from ChatKit's internal state).

**TypeScript Definition**:
```typescript
interface ChatUIState {
  isOpen: boolean;        // Whether chat interface is open
  isMinimized: boolean;   // Whether chat interface is minimized
}
```

**Field Descriptions**:

- **isOpen**: Indicates whether the chat interface is currently visible
  - `true`: Chat interface is open and visible
  - `false`: Chat interface is closed (only floating launcher icon visible)

- **isMinimized**: Indicates whether the chat interface is minimized
  - `true`: Chat interface is minimized (collapsed to floating icon)
  - `false`: Chat interface is expanded (full size)

**Validation Rules**:
- `isOpen` and `isMinimized` cannot both be `true` (invalid state)
- If `isMinimized` is `true`, `isOpen` must be `false`

**State Transitions**:
```
Closed → Open:
  { isOpen: false, isMinimized: false } → { isOpen: true, isMinimized: false }

Open → Minimized:
  { isOpen: true, isMinimized: false } → { isOpen: false, isMinimized: true }

Minimized → Open:
  { isOpen: false, isMinimized: true } → { isOpen: true, isMinimized: false }

Open → Closed:
  { isOpen: true, isMinimized: false } → { isOpen: false, isMinimized: false }
```

**Usage**: Managed by ChatUIContext in custom wrapper components.

---

## State Management Structure

**Architecture**:
```
ChatKit Provider (OpenAI ChatKit)
  ├─ Manages: Conversation state, messages, loading, errors
  ├─ Provides: Message display, input handling, history loading
  └─ Configured with: API endpoint, JWT token, domain key

ChatUIContext (Custom)
  ├─ Manages: Launcher UI state (isOpen, isMinimized)
  └─ Provides: openChat(), closeChat(), minimizeChat()
```

**React Context Structure** (Custom):
```typescript
interface ChatUIContextValue {
  // UI State (custom wrapper)
  uiState: ChatUIState;

  // Actions (custom wrapper)
  openChat: () => void;
  closeChat: () => void;
  minimizeChat: () => void;
}
```

**ChatKit Configuration**:
```typescript
<ChatKitProvider
  apiEndpoint="/api/chat"
  authToken={jwtToken}
  domainKey={domainKey}
>
  {/* ChatKit manages conversation state internally */}
</ChatKitProvider>
```

---

## Persistence Strategy

**ChatKit State** (Managed by ChatKit):
- Conversation messages: Fetched from backend via ChatKit
- Message history: Loaded by ChatKit on mount
- Loading states: Managed by ChatKit internally
- Error states: Managed by ChatKit internally

**Custom Wrapper State**:
- **In-Memory**: Launcher UI state (isOpen, isMinimized) in React state
- **Session Storage** (optional): Persist launcher state across page refreshes
- **No Local Storage**: Conversation data managed by ChatKit and backend

**Rationale**:
- ChatKit handles all conversation state management
- Custom wrapper only manages launcher UI state
- Single source of truth: Backend database (accessed via ChatKit)
- No data synchronization issues
- Conversation survives browser refresh (ChatKit fetches from backend)

---

## TypeScript Type Definitions File

**Location**: `frontend/types/chat.ts`

**Required Type Definitions** (Custom wrapper only):
```typescript
// UI state for floating launcher wrapper
export interface ChatUIState {
  isOpen: boolean;
  isMinimized: boolean;
}

// Context value for launcher wrapper
export interface ChatUIContextValue {
  uiState: ChatUIState;
  openChat: () => void;
  closeChat: () => void;
  minimizeChat: () => void;
}
```

**Note**: ChatKit provides its own TypeScript types for message and conversation structures. Import ChatKit types from `@openai/chatkit` package as needed.

---

## Integration with ChatKit

**ChatKit Components** (from @openai/chatkit):
- `ChatKitProvider`: Root provider for ChatKit state
- `ChatKitMessages`: Message display component
- `ChatKitInput`: Message input component
- Additional components per ChatKit documentation at https://platform.openai.com/docs/guides/chatkit

**Custom Wrapper Components**:
- `FloatingChatLauncher`: Floating icon button
- `ChatInterface`: Container that wraps ChatKit components
- `ChatHeader`: Custom header with close/minimize buttons
- `ChatUIProvider`: Context provider for launcher state

**Data Flow**:
```
User types message
  ↓
ChatKit Input Component
  ↓
ChatKit sends to API endpoint (with JWT)
  ↓
Backend processes and responds
  ↓
ChatKit receives response
  ↓
ChatKit Messages Component displays
```

---

## Reference: ChatKit Internal Structures

**Note**: The following structures are managed internally by ChatKit. Documented here for reference only.

### ChatMessage (ChatKit Internal)

```typescript
// ChatKit manages this internally
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  // ChatKit may include additional fields
}
```

### Conversation (ChatKit Internal)

```typescript
// ChatKit manages this internally
interface Conversation {
  id: string;
  messages: ChatMessage[];
  // ChatKit may include additional fields
}
```

**Key Points**:
- Frontend does not directly manipulate these structures
- ChatKit components handle all message rendering and state management
- Configuration happens at ChatKit provider level
- Refer to official ChatKit documentation for complete API reference

---

**Data Model Status**: ✅ COMPLETE
**Implementation Note**: Simplified for ChatKit integration - ChatKit manages conversation state, custom code manages launcher UI state only
**Next Step**: Refer to quickstart.md for implementation guidance with ChatKit
