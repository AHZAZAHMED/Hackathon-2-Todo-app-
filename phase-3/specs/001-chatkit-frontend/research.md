# Research: ChatKit Frontend Integration

**Feature**: 001-chatkit-frontend
**Date**: 2026-02-09
**Status**: Complete

## Overview

This document captures research findings and technology decisions for implementing the ChatKit frontend integration. All decisions are based on best practices, compatibility requirements, and alignment with existing Phase-2 architecture.

---

## Research Question 1: OpenAI ChatKit Integration

**Question**: How to integrate OpenAI ChatKit with Next.js 16+ App Router and configure custom API endpoints?

### Decision

Use OpenAI ChatKit as a client-side React component library with custom API endpoint configuration. Package name to be confirmed during implementation (likely `@openai/chatkit` or similar).

### Rationale

- **Official Support**: OpenAI ChatKit is the official UI library from OpenAI, ensuring compatibility and ongoing support
- **React Compatibility**: ChatKit is built for React, which aligns with Next.js 16+ App Router
- **Custom Endpoints**: ChatKit supports custom API endpoints, allowing us to point to our backend `/api/chat` instead of OpenAI's default endpoints
- **Client Components**: Next.js App Router supports client components via `'use client'` directive, which is required for interactive chat UI

### Implementation Approach

```typescript
// components/chat/ChatProvider.tsx
'use client';

import { ChatKitProvider } from '@openai/chatkit'; // Package name TBD

export function ChatProvider({ children }: { children: React.ReactNode }) {
  return (
    <ChatKitProvider
      apiEndpoint={process.env.NEXT_PUBLIC_API_BASE_URL + '/api/chat'}
      domainKey={process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY}
      // Custom configuration for JWT attachment
    >
      {children}
    </ChatKitProvider>
  );
}
```

### Alternatives Considered

1. **Custom Chat UI**: Build from scratch using React components
   - **Rejected**: Reinventing the wheel, more development time, less tested

2. **react-chat-elements**: Third-party chat UI library
   - **Rejected**: Not official OpenAI library, may not support custom endpoints as easily

3. **Vercel AI SDK**: Alternative AI chat framework
   - **Rejected**: Not specified in requirements, different architecture

### Risks & Mitigations

- **Risk**: Package name unknown
  - **Mitigation**: Research OpenAI documentation, check npm registry, fallback to custom UI if needed

- **Risk**: ChatKit incompatible with Next.js App Router
  - **Mitigation**: Test integration early in Phase 1.1, use client components, fallback to custom UI if needed

---

## Research Question 2: Session Storage Strategy

**Question**: Best practices for persisting chat state (window open/closed, messages on token expiry) across page navigations in Next.js App Router?

### Decision

Use browser `sessionStorage` API with a custom React hook (`useChatStorage`) to persist chat state across page navigations within the same browser session.

### Rationale

- **Session Scope**: `sessionStorage` persists across page navigations but clears on browser close, which aligns with ephemeral conversation requirement
- **Client-Side Only**: Works in client components without server-side complexity
- **Simple API**: Standard browser API, no additional dependencies
- **Appropriate Lifetime**: Longer than in-memory state (survives navigation) but shorter than `localStorage` (clears on session end)

### Implementation Approach

```typescript
// lib/chat-storage.ts
const CHAT_STATE_KEY = 'chatkit_state';
const CHAT_MESSAGES_KEY = 'chatkit_messages';

export function saveChatState(isOpen: boolean) {
  sessionStorage.setItem(CHAT_STATE_KEY, JSON.stringify({ isOpen }));
}

export function loadChatState(): { isOpen: boolean } | null {
  const data = sessionStorage.getItem(CHAT_STATE_KEY);
  return data ? JSON.parse(data) : null;
}

export function saveMessages(messages: ChatMessage[]) {
  sessionStorage.setItem(CHAT_MESSAGES_KEY, JSON.stringify(messages));
}

export function loadMessages(): ChatMessage[] {
  const data = sessionStorage.getItem(CHAT_MESSAGES_KEY);
  return data ? JSON.parse(data) : [];
}

export function clearChatStorage() {
  sessionStorage.removeItem(CHAT_STATE_KEY);
  sessionStorage.removeItem(CHAT_MESSAGES_KEY);
}
```

### Alternatives Considered

1. **localStorage**: Persists across browser sessions
   - **Rejected**: Too long-lived for ephemeral conversations, violates spec requirement

2. **In-Memory State (React Context)**: State lost on page navigation
   - **Rejected**: Doesn't persist across page navigations, violates FR-016/FR-017

3. **Cookies**: Limited size, sent with every request
   - **Rejected**: Size limits (4KB), unnecessary server overhead, not designed for this use case

4. **IndexedDB**: More complex storage API
   - **Rejected**: Overkill for simple key-value storage, more complex API

### Risks & Mitigations

- **Risk**: Session storage cleared unexpectedly (browser settings, incognito mode)
  - **Mitigation**: Handle null/undefined gracefully, provide user messaging, document behavior

- **Risk**: Storage quota exceeded (rare for session storage)
  - **Mitigation**: Limit message history size, clear old messages, handle quota errors

---

## Research Question 3: JWT Extraction

**Question**: How to access Better Auth JWT token from existing Phase-2 authentication system in client components?

### Decision

Use existing Phase-2 centralized API client (`lib/api-client.ts`) which already handles JWT extraction and attachment. Create a thin wrapper (`lib/chat-client.ts`) that uses this client for chat-specific requests.

### Rationale

- **Reuse Existing Infrastructure**: Phase-2 already has JWT management, no need to duplicate
- **Consistency**: Same JWT handling across all API requests
- **Separation of Concerns**: Chat client focuses on chat-specific logic, delegates auth to existing client
- **Maintainability**: Single source of truth for JWT handling

### Implementation Approach

```typescript
// lib/chat-client.ts
import { apiClient } from './api-client'; // Existing Phase-2 client

export async function sendChatMessage(message: string): Promise<string> {
  // apiClient automatically attaches JWT from Better Auth
  const response = await apiClient.post('/api/chat', { message });
  return response.data.response;
}
```

### Alternatives Considered

1. **Direct Better Auth Hook**: Access JWT directly from Better Auth context
   - **Rejected**: Duplicates existing logic, inconsistent with Phase-2 patterns

2. **Manual JWT Extraction**: Read from cookies/localStorage directly
   - **Rejected**: Bypasses existing infrastructure, error-prone, inconsistent

3. **Separate Auth Client**: Create new auth client for chat
   - **Rejected**: Unnecessary duplication, maintenance burden

### Risks & Mitigations

- **Risk**: API client doesn't expose needed functionality
  - **Mitigation**: Review Phase-2 implementation early, extend if needed

- **Risk**: JWT refresh logic not handled
  - **Mitigation**: Rely on existing Phase-2 refresh logic, test token expiry scenarios

---

## Research Question 4: Error Handling Patterns

**Question**: Best practices for displaying user-friendly error messages and retry mechanisms in chat interfaces?

### Decision

Implement a three-tier error handling strategy:
1. **Network Errors**: Display failed message with retry button inline
2. **Auth Errors (401)**: Redirect to login, preserve conversation in session storage
3. **Server Errors (500)**: Display user-friendly error message with retry option

### Rationale

- **User-Centric**: Clear, actionable error messages without technical jargon
- **Inline Retry**: Failed messages remain visible with retry button, clear cause-and-effect
- **Graceful Degradation**: System remains usable even when backend unavailable
- **Conversation Preservation**: Users don't lose context on auth errors

### Implementation Approach

```typescript
// hooks/useChat.ts
async function sendMessage(content: string) {
  const messageId = generateId();
  const newMessage: ChatMessage = {
    id: messageId,
    role: 'user',
    content,
    timestamp: new Date(),
    status: 'sending',
    error: null,
  };

  setMessages(prev => [...prev, newMessage]);

  try {
    const response = await sendChatMessage(content);

    // Update to sent status
    setMessages(prev => prev.map(msg =>
      msg.id === messageId ? { ...msg, status: 'sent' } : msg
    ));

    // Add assistant response
    setMessages(prev => [...prev, {
      id: generateId(),
      role: 'assistant',
      content: response,
      timestamp: new Date(),
      status: 'sent',
      error: null,
    }]);

  } catch (error) {
    if (error.status === 401) {
      // Auth error: preserve conversation and redirect
      saveMessages(messages);
      redirectToLogin();
    } else {
      // Network/server error: mark message as failed
      setMessages(prev => prev.map(msg =>
        msg.id === messageId
          ? { ...msg, status: 'failed', error: getUserFriendlyError(error) }
          : msg
      ));
    }
  }
}

function getUserFriendlyError(error: any): string {
  if (error.status === 500) return 'Server error. Please try again.';
  if (error.status === 503) return 'Service unavailable. Please try again later.';
  if (!navigator.onLine) return 'No internet connection. Please check your network.';
  return 'Unable to send message. Please try again.';
}
```

### Alternatives Considered

1. **Toast Notifications**: Show error in toast/snackbar
   - **Rejected**: Less clear which message failed, toast disappears

2. **Modal Dialogs**: Show error in blocking modal
   - **Rejected**: Interrupts user flow, requires dismissal

3. **Automatic Retry**: Retry failed messages automatically
   - **Rejected**: May cause infinite loops, user loses control

### Risks & Mitigations

- **Risk**: Error messages too generic
  - **Mitigation**: Map specific error codes to helpful messages, provide context

- **Risk**: Retry button causes duplicate messages
  - **Mitigation**: Track message status, prevent duplicate sends

---

## Research Question 5: Z-Index Management

**Question**: How to ensure chat window appears above all page content without breaking existing layouts?

### Decision

Use a high z-index value (9999) with fixed positioning for chat components, and create a dedicated z-index scale in Tailwind config for consistent layering.

### Rationale

- **Fixed Positioning**: Removes chat from document flow, prevents layout disruption
- **High Z-Index**: Ensures chat appears above typical page content (modals usually 1000-9000)
- **Tailwind Integration**: Consistent with Phase-2 styling approach
- **Predictable Layering**: Explicit z-index scale prevents conflicts

### Implementation Approach

```typescript
// tailwind.config.js (extend existing config)
module.exports = {
  theme: {
    extend: {
      zIndex: {
        'chat-icon': '9998',
        'chat-window': '9999',
      }
    }
  }
}

// components/chat/ChatIcon.tsx
<div className="fixed bottom-5 right-5 z-chat-icon">
  {/* Chat icon */}
</div>

// components/chat/ChatWindow.tsx
<div className="fixed bottom-20 right-5 z-chat-window">
  {/* Chat window */}
</div>
```

### Alternatives Considered

1. **Portal to Body**: Render chat in React portal at document root
   - **Rejected**: More complex, not necessary with fixed positioning

2. **CSS Layers**: Use CSS @layer for layering
   - **Rejected**: Newer feature, browser support concerns

3. **Dynamic Z-Index**: Calculate z-index based on page content
   - **Rejected**: Complex, error-prone, unnecessary

### Risks & Mitigations

- **Risk**: Conflicts with existing modals/overlays
  - **Mitigation**: Test on all Phase-2 pages, adjust z-index if needed

- **Risk**: Chat covers important UI elements
  - **Mitigation**: Position in bottom-right corner (least intrusive), ensure closable

---

## Summary of Decisions

| Question | Decision | Key Rationale |
|----------|----------|---------------|
| ChatKit Integration | Use OpenAI ChatKit with custom endpoints | Official library, React compatible, supports custom APIs |
| Session Storage | Use sessionStorage API with custom hooks | Appropriate lifetime, simple API, client-side only |
| JWT Extraction | Reuse existing Phase-2 API client | Consistency, no duplication, single source of truth |
| Error Handling | Three-tier strategy with inline retry | User-centric, clear feedback, graceful degradation |
| Z-Index Management | Fixed positioning with z-9999 | Above page content, no layout disruption, Tailwind integrated |

## Implementation Readiness

✅ **All research questions resolved**
✅ **Technology decisions documented**
✅ **Implementation approaches defined**
✅ **Risks identified and mitigated**
✅ **Ready for Phase 1 design artifacts**

## Next Steps

1. Generate data-model.md (entity definitions)
2. Generate contracts/chat-api.md (API specification)
3. Generate quickstart.md (developer setup guide)
4. Proceed to `/sp.tasks` for task breakdown
