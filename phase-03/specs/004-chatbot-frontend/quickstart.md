# Quickstart Guide: Phase-3 Chatbot Frontend

**Date**: 2026-02-08
**Feature**: 004-chatbot-frontend
**Audience**: Developers implementing the chatbot frontend

## Overview

This guide provides step-by-step instructions for implementing the Phase-3 chatbot frontend with OpenAI ChatKit and floating launcher icon. The implementation extends the existing Phase-2 Next.js frontend by integrating ChatKit and wrapping it in a custom floating launcher component.

## Prerequisites

- Phase-2 frontend complete and functional
- Next.js 16+ with App Router
- React 19+
- TypeScript with strict mode
- Tailwind CSS configured
- Better Auth JWT authentication working
- Centralized API client at `frontend/lib/api-client.ts`

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ App Layout (Root)                                           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ChatKit Provider (OpenAI ChatKit)                       │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ ChatUIProvider (Custom launcher state)              │ │ │
│ │ │ ┌─────────────────────────────────────────────────┐ │ │ │
│ │ │ │ Page Content (Dashboard, Tasks, etc.)           │ │ │ │
│ │ │ └─────────────────────────────────────────────────┘ │ │ │
│ │ │ ┌─────────────────────────────────────────────────┐ │ │ │
│ │ │ │ FloatingChatLauncher (Custom wrapper)           │ │ │ │
│ │ │ │   ┌───────────────────────────────────────────┐ │ │ │ │
│ │ │ │   │ ChatInterface (Custom wrapper)            │ │ │ │ │
│ │ │ │   │ ├─ ChatHeader (Custom close/minimize)     │ │ │ │ │
│ │ │ │   │ └─ ChatKit Components (OpenAI ChatKit)    │ │ │ │ │
│ │ │ │   └───────────────────────────────────────────┘ │ │ │ │
│ │ │ └─────────────────────────────────────────────────┘ │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Key Components**:
- **ChatKit Provider**: OpenAI ChatKit manages conversation state and message handling
- **ChatUIProvider**: Custom React context for floating launcher UI state (open/closed/minimized)
- **FloatingChatLauncher**: Custom wrapper component for floating icon
- **ChatInterface**: Custom wrapper that contains ChatKit components
- **ChatHeader**: Custom header with close/minimize buttons

## Implementation Steps

### Step 1: Install OpenAI ChatKit

**Installation**:
```bash
cd frontend
npm install @openai/chatkit
# or
yarn add @openai/chatkit
```

**Documentation**: Refer to https://platform.openai.com/docs/guides/chatkit for official installation and setup instructions.

**Validation**:
```bash
npm list @openai/chatkit  # Verify installation
```

---

### Step 2: Configure Environment Variables

**File**: `frontend/.env.local`

```bash
# Existing Phase-2 variables
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# New Phase-3 variables
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your_domain_allowlist_key_here
```

**Notes**:
- `NEXT_PUBLIC_API_BASE_URL`: Backend API base URL (existing from Phase-2)
- `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`: Required for production deployment, obtain from OpenAI platform

---

### Step 3: Create Type Definitions for Launcher State

**File**: `frontend/types/chat.ts`

```typescript
// UI state for floating launcher (separate from ChatKit state)
export interface ChatUIState {
  isOpen: boolean;        // Whether chat interface is open
  isMinimized: boolean;   // Whether chat interface is minimized
}

export interface ChatUIContextValue {
  uiState: ChatUIState;
  openChat: () => void;
  closeChat: () => void;
  minimizeChat: () => void;
}
```

**Validation**:
```bash
cd frontend
npx tsc --noEmit  # Should compile without errors
```

---

### Step 4: Configure ChatKit Provider

**File**: `frontend/app/layout.tsx` (modify existing)

```typescript
import { ChatKitProvider } from '@openai/chatkit';
import { getJWTToken } from '@/lib/auth'; // Your existing auth utility

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const jwtToken = getJWTToken(); // Get JWT from your Phase-2 auth

  return (
    <html lang="en">
      <body>
        <ChatKitProvider
          apiEndpoint={process.env.NEXT_PUBLIC_API_BASE_URL + '/api/chat'}
          authToken={jwtToken}
          domainKey={process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY}
        >
          {children}
        </ChatKitProvider>
      </body>
    </html>
  );
}
```

**Key Points**:
- ChatKit provider wraps entire application
- JWT token passed to ChatKit for authentication
- API endpoint configured to use POST /api/chat
- Domain key configured for production

---

### Step 5: Create ChatUI Context for Launcher State

**File**: `frontend/lib/contexts/ChatUIContext.tsx`

```typescript
'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';
import { ChatUIState, ChatUIContextValue } from '@/types/chat';

const ChatUIContext = createContext<ChatUIContextValue | undefined>(undefined);

export function ChatUIProvider({ children }: { children: React.ReactNode }) {
  const [uiState, setUiState] = useState<ChatUIState>({
    isOpen: false,
    isMinimized: false,
  });

  const openChat = useCallback(() => {
    setUiState({ isOpen: true, isMinimized: false });
  }, []);

  const closeChat = useCallback(() => {
    setUiState({ isOpen: false, isMinimized: false });
  }, []);

  const minimizeChat = useCallback(() => {
    setUiState({ isOpen: false, isMinimized: true });
  }, []);

  return (
    <ChatUIContext.Provider value={{ uiState, openChat, closeChat, minimizeChat }}>
      {children}
    </ChatUIContext.Provider>
  );
}

export function useChatUI() {
  const context = useContext(ChatUIContext);
  if (!context) {
    throw new Error('useChatUI must be used within ChatUIProvider');
  }
  return context;
}
```

---

### Step 6: Create ChatKit Wrapper Components

#### 6.1 ChatHeader Component

**File**: `frontend/components/chat/ChatHeader.tsx`

```typescript
'use client';

import { X, Minus } from 'lucide-react';
import { useChatUI } from '@/lib/contexts/ChatUIContext';

export function ChatHeader() {
  const { closeChat, minimizeChat } = useChatUI();

  return (
    <div className="flex items-center justify-between p-4 border-b bg-white">
      <h2 className="text-lg font-semibold">Chat Assistant</h2>
      <div className="flex gap-2">
        <button
          onClick={minimizeChat}
          className="p-1 hover:bg-gray-100 rounded"
          aria-label="Minimize chat"
        >
          <Minus className="h-5 w-5" />
        </button>
        <button
          onClick={closeChat}
          className="p-1 hover:bg-gray-100 rounded"
          aria-label="Close chat"
        >
          <X className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
}
```

#### 6.2 ChatInterface Component

**File**: `frontend/components/chat/ChatInterface.tsx`

```typescript
'use client';

import { ChatHeader } from './ChatHeader';
import { ChatKitMessages, ChatKitInput } from '@openai/chatkit'; // Import ChatKit components

export function ChatInterface() {
  return (
    <div className="fixed bottom-6 right-6 z-50 w-full max-w-md h-[600px] bg-white rounded-lg shadow-2xl flex flex-col md:w-96">
      {/* Custom Header */}
      <ChatHeader />

      {/* ChatKit Message Display */}
      <div className="flex-1 overflow-hidden">
        <ChatKitMessages
          className="h-full"
          theme={{
            // Customize ChatKit theme to match Tailwind design
            userMessageBg: '#3B82F6',
            assistantMessageBg: '#F3F4F6',
          }}
        />
      </div>

      {/* ChatKit Input */}
      <div className="border-t">
        <ChatKitInput
          placeholder="Type a message..."
          className="w-full"
        />
      </div>
    </div>
  );
}
```

**Note**: Replace `ChatKitMessages` and `ChatKitInput` with actual ChatKit component names from the official documentation.

#### 6.3 FloatingChatLauncher Component

**File**: `frontend/components/chat/FloatingChatLauncher.tsx`

```typescript
'use client';

import { MessageCircle } from 'lucide-react';
import { useChatUI } from '@/lib/contexts/ChatUIContext';
import { ChatInterface } from './ChatInterface';

export function FloatingChatLauncher() {
  const { uiState, openChat } = useChatUI();

  return (
    <>
      {/* Floating Icon */}
      {!uiState.isOpen && (
        <button
          onClick={openChat}
          className="fixed bottom-6 right-6 z-40 h-14 w-14 rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all md:h-16 md:w-16"
          aria-label="Open chat"
        >
          <MessageCircle className="h-6 w-6 mx-auto" />
        </button>
      )}

      {/* Chat Interface with ChatKit */}
      {uiState.isOpen && <ChatInterface />}
    </>
  );
}
```

---

### Step 7: Integrate into App Layout

**File**: `frontend/app/layout.tsx` (final version)

```typescript
import { ChatKitProvider } from '@openai/chatkit';
import { ChatUIProvider } from '@/lib/contexts/ChatUIContext';
import { FloatingChatLauncher } from '@/components/chat/FloatingChatLauncher';
import { getJWTToken } from '@/lib/auth';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const jwtToken = getJWTToken();

  return (
    <html lang="en">
      <body>
        <ChatKitProvider
          apiEndpoint={process.env.NEXT_PUBLIC_API_BASE_URL + '/api/chat'}
          authToken={jwtToken}
          domainKey={process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY}
        >
          <ChatUIProvider>
            {children}
            <FloatingChatLauncher />
          </ChatUIProvider>
        </ChatKitProvider>
      </body>
    </html>
  );
}
```

---

### Step 8: Configure Z-Index Hierarchy

**File**: `frontend/tailwind.config.js` (modify existing)

```javascript
module.exports = {
  theme: {
    extend: {
      zIndex: {
        '40': '40',  // Floating launcher icon
        '50': '50',  // Chat interface
      }
    }
  }
}
```

---

## Testing Checklist

### ChatKit Integration Testing
- [ ] ChatKit provider configured correctly
- [ ] JWT token passed to ChatKit
- [ ] Messages sent via ChatKit reach POST /api/chat
- [ ] Responses from backend display in ChatKit
- [ ] ChatKit loads conversation history on mount

### Floating Launcher Testing
- [ ] Floating icon visible on all authenticated pages
- [ ] Click icon opens chat interface
- [ ] Close button closes chat interface
- [ ] Minimize button minimizes to icon
- [ ] Chat state persists across page navigations

### Integration Testing
- [ ] Send message → receive response flow works
- [ ] JWT authentication enforced (401 redirects to login)
- [ ] Conversation history persists across page refreshes
- [ ] Error handling displays user-friendly messages

### Browser Testing
- [ ] Chrome 90+
- [ ] Firefox 88+
- [ ] Safari 14+
- [ ] Edge 90+
- [ ] iOS Safari 14+
- [ ] Android Chrome 90+

### Responsive Testing
- [ ] Desktop (1920x1080)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)
- [ ] Floating icon doesn't obstruct content

---

## Common Issues and Solutions

### Issue 1: ChatKit Not Rendering

**Symptom**: ChatKit components don't appear

**Solution**:
- Verify ChatKit provider is at root level
- Check that JWT token is valid and passed correctly
- Verify API endpoint configuration
- Check browser console for ChatKit errors

### Issue 2: JWT Not Attached to ChatKit Requests

**Symptom**: 401 Unauthorized errors from backend

**Solution**:
- Verify `authToken` prop passed to ChatKitProvider
- Ensure JWT token is retrieved correctly from Phase-2 auth
- Check that token is not expired

### Issue 3: Chat State Lost on Page Navigation

**Symptom**: Chat closes when navigating between pages

**Solution**:
- Ensure ChatUIProvider is in root layout
- Verify ChatKitProvider wraps entire application
- ChatKit manages conversation state internally

### Issue 4: Z-Index Conflicts

**Symptom**: Chat interface hidden behind modals or other elements

**Solution**:
- Review z-index hierarchy in Tailwind config
- Chat interface should be z-50
- Modals should be z-[100] or higher

### Issue 5: ChatKit Styling Conflicts

**Symptom**: ChatKit components don't match design system

**Solution**:
- Use ChatKit theming API to customize colors
- Pass theme object to ChatKit components
- Refer to ChatKit documentation for theming options

---

## ChatKit Customization

### Theme Configuration

Customize ChatKit to match your Tailwind CSS design:

```typescript
const chatKitTheme = {
  userMessageBg: '#3B82F6',      // Tailwind blue-600
  assistantMessageBg: '#F3F4F6', // Tailwind gray-100
  inputBg: '#FFFFFF',
  inputBorder: '#E5E7EB',
  primaryColor: '#3B82F6',
};

<ChatKitMessages theme={chatKitTheme} />
```

### Responsive Configuration

Configure ChatKit for mobile:

```typescript
<ChatKitMessages
  responsive={{
    mobile: { maxWidth: '100vw', height: '100vh' },
    tablet: { maxWidth: '360px', height: '600px' },
    desktop: { maxWidth: '400px', height: '600px' },
  }}
/>
```

---

## Performance Optimization

### ChatKit Performance
- ChatKit handles virtual scrolling for long conversations
- Configure ChatKit message limit if needed
- Use ChatKit's built-in optimization features

### Wrapper Performance
- Use `React.memo` for custom wrapper components if needed
- Minimize re-renders of FloatingChatLauncher
- Keep ChatUIContext state minimal (only UI state)

---

## Next Steps

1. ✅ Complete ChatKit installation and configuration
2. ✅ Create custom wrapper components
3. ✅ Integrate into root layout
4. ⏭️ Test all user stories independently
5. ⏭️ Customize ChatKit theme to match design system
6. ⏭️ Run browser compatibility testing
7. ⏭️ Deploy to staging for validation

---

## Additional Resources

- **ChatKit Documentation**: https://platform.openai.com/docs/guides/chatkit
- **ChatKit Examples**: Check official OpenAI examples repository
- **Phase-2 Architecture**: Refer to existing Phase-2 CLAUDE.md for auth patterns
- **API Contract**: See contracts/chat-api.yaml for backend API specification

---

**Quickstart Status**: ✅ COMPLETE
**Ready for Implementation**: ✅ YES (with OpenAI ChatKit)
