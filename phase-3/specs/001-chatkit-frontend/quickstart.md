# Quickstart Guide: ChatKit Frontend Integration

**Feature**: 001-chatkit-frontend
**Date**: 2026-02-09
**Audience**: Developers implementing this feature

## Overview

This guide provides step-by-step instructions for setting up and implementing the ChatKit frontend integration. Follow these steps in order to ensure proper setup and avoid common pitfalls.

---

## Prerequisites

Before starting, ensure you have:

- ✅ Node.js 18+ installed
- ✅ npm or yarn package manager
- ✅ Access to the Phase-2 codebase (Next.js 16+ with Better Auth)
- ✅ Environment variables for backend API and OpenAI domain key
- ✅ Familiarity with React, TypeScript, and Tailwind CSS

---

## Step 1: Environment Setup

### 1.1 Clone and Navigate

```bash
cd frontend/
```

### 1.2 Configure Environment Variables

Create or update `.env.local`:

```bash
# Backend API base URL
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# OpenAI ChatKit domain key (obtain from OpenAI dashboard)
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your_domain_key_here
```

**Note**: Replace `your_domain_key_here` with actual OpenAI domain key during implementation.

### 1.3 Install Dependencies

```bash
npm install
# or
yarn install
```

**Note**: OpenAI ChatKit package will be installed in Phase 1.1 (package name TBD).

---

## Step 2: Verify Phase-2 Integration Points

Before implementing chat features, verify existing Phase-2 components are accessible:

### 2.1 Check API Client

```bash
# Verify centralized API client exists
ls lib/api-client.ts
```

**Expected**: File exists with JWT attachment logic.

### 2.2 Check Better Auth

```bash
# Verify Better Auth configuration
ls lib/auth.ts
# or check auth configuration location
```

**Expected**: Better Auth configured with JWT token management.

### 2.3 Run Development Server

```bash
npm run dev
```

**Expected**: Server starts on http://localhost:3000 without errors.

### 2.4 Test Existing Authentication

1. Navigate to http://localhost:3000
2. Log in with test credentials
3. Verify JWT token is issued (check browser dev tools → Application → Cookies/Storage)

**Expected**: JWT token present after login.

---

## Step 3: Implementation Phases

### Phase 1.1: Setup & Dependencies

**Goal**: Install ChatKit and configure environment.

```bash
# Install OpenAI ChatKit (package name TBD - check research.md)
npm install @openai/chatkit
# or the correct package name once confirmed

# Verify installation
npm list @openai/chatkit
```

**Create type definitions**:

```bash
# Create types directory if not exists
mkdir -p types

# Create chat types file
touch types/chat.ts
```

**Add to `types/chat.ts`**:

```typescript
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  status: 'sending' | 'sent' | 'failed';
  error: string | null;
}

export interface ChatSession {
  messages: ChatMessage[];
  isOpen: boolean;
  isLoading: boolean;
  error: string | null;
}
```

**Verify**: TypeScript compiles without errors (`npm run build` or `tsc --noEmit`).

---

### Phase 1.2: Chat State Management

**Goal**: Create storage utilities and hooks.

```bash
# Create lib files
touch lib/chat-storage.ts
touch lib/chat-client.ts

# Create hooks directory if not exists
mkdir -p hooks

# Create chat hooks
touch hooks/useChat.ts
touch hooks/useChatAuth.ts
```

**Implement `lib/chat-storage.ts`** (see research.md for full implementation):

```typescript
const CHAT_STATE_KEY = 'chatkit_state';
const CHAT_MESSAGES_KEY = 'chatkit_messages';

export function saveChatState(isOpen: boolean) {
  sessionStorage.setItem(CHAT_STATE_KEY, JSON.stringify({ isOpen }));
}

export function loadChatState(): { isOpen: boolean } | null {
  const data = sessionStorage.getItem(CHAT_STATE_KEY);
  return data ? JSON.parse(data) : null;
}

// ... additional functions
```

**Verify**: Import in a test component, call functions, check session storage in browser dev tools.

---

### Phase 1.3: Chat UI Components

**Goal**: Create chat icon and window components.

```bash
# Create components directory
mkdir -p components/chat

# Create component files
touch components/chat/ChatIcon.tsx
touch components/chat/ChatWindow.tsx
touch components/chat/ChatMessages.tsx
touch components/chat/ChatMessage.tsx
touch components/chat/ChatInput.tsx
touch components/chat/ChatRetryButton.tsx
touch components/chat/ChatProvider.tsx
```

**Implement `components/chat/ChatIcon.tsx`**:

```typescript
'use client';

export function ChatIcon({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-5 right-5 z-chat-icon w-14 h-14 bg-blue-600 rounded-full shadow-lg hover:bg-blue-700 transition-colors"
      aria-label="Open chat"
    >
      {/* Chat icon SVG */}
      <svg className="w-6 h-6 mx-auto text-white" /* ... */ />
    </button>
  );
}
```

**Verify**: Import in a page, render, check positioning in browser (bottom-right, 20px offset).

---

### Phase 1.4: Chat API Integration

**Goal**: Connect chat UI to backend API.

**Implement `lib/chat-client.ts`**:

```typescript
import { apiClient } from './api-client';

export async function sendChatMessage(message: string): Promise<string> {
  const response = await apiClient.post('/api/chat', { message });
  return response.data.response;
}
```

**Verify**:
1. Send test message
2. Check network tab in browser dev tools
3. Confirm POST to /api/chat with Authorization header

---

### Phase 1.5: Authentication Integration

**Goal**: Handle unauthenticated users and token expiry.

**Add ChatProvider to `app/layout.tsx`**:

```typescript
import { ChatProvider } from '@/components/chat/ChatProvider';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ChatProvider>
          {children}
        </ChatProvider>
      </body>
    </html>
  );
}
```

**Verify**:
1. Log out
2. Click chat icon
3. Confirm redirect to login page
4. Log in
5. Confirm return to original page with chat open

---

### Phase 1.6: State Persistence

**Goal**: Persist chat state across page navigations.

**Test**:
1. Open chat window
2. Navigate to different page (e.g., dashboard → settings)
3. Confirm chat window remains open
4. Close chat window
5. Navigate to another page
6. Confirm chat window remains closed

**Verify**: Check session storage in browser dev tools for `chatkit_state` key.

---

### Phase 1.7: Styling & Polish

**Goal**: Apply final styling and ensure responsive design.

**Update `tailwind.config.js`**:

```javascript
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
```

**Verify**:
1. Chat appears above all page content
2. Chat window has proper dimensions (400px × 600px)
3. Chat icon never covered by window
4. Scrollable message panel works
5. Character counter displays correctly

---

### Phase 1.8: Playwright Validation

**Goal**: Run automated tests to verify all requirements.

```bash
# Install Playwright if not already installed
npm install -D @playwright/test

# Run Playwright tests
npx playwright test
```

**Test Checklist**:
- [ ] Icon visibility on all pages
- [ ] Window open/close functionality
- [ ] Message send with JWT
- [ ] Error handling
- [ ] Phase-2 regression (existing tests pass)

**Verify**: All tests pass with 100% success rate (SC-007).

---

## Step 4: Testing Checklist

### Manual Testing

- [ ] **Icon Visibility**: Chat icon visible on dashboard, settings, profile pages
- [ ] **Icon Position**: Icon in bottom-right corner (20px from edges)
- [ ] **Window Open**: Click icon, window opens above icon
- [ ] **Window Dimensions**: Window approximately 400px × 600px
- [ ] **Window Close**: Click close button, window closes, icon remains visible
- [ ] **Message Send**: Type message, press Enter, message appears
- [ ] **Message Limit**: Type 500+ characters, send button disabled
- [ ] **Character Counter**: Counter updates as user types
- [ ] **Loading State**: Loading indicator displays while waiting for response
- [ ] **Error Handling**: Disconnect backend, error message displays
- [ ] **Retry Button**: Click retry on failed message, message resends
- [ ] **Unauthenticated**: Log out, click icon, redirected to login
- [ ] **Post-Login**: After login, returned to page with chat open
- [ ] **Token Expiry**: Expire token, send message, conversation preserved
- [ ] **State Persistence**: Navigate between pages, chat state persists
- [ ] **Phase-2 Regression**: Existing features (tasks, auth) still work

### Automated Testing (Playwright)

```bash
# Run all tests
npx playwright test

# Run specific test file
npx playwright test tests/chat.spec.ts

# Run with UI mode
npx playwright test --ui

# Generate test report
npx playwright show-report
```

---

## Step 5: Common Issues & Troubleshooting

### Issue: ChatKit Package Not Found

**Symptom**: `npm install @openai/chatkit` fails

**Solution**:
1. Check research.md for correct package name
2. Verify npm registry access
3. Consider fallback to custom UI if package unavailable

### Issue: JWT Not Attached to Requests

**Symptom**: Backend returns 401, but user is logged in

**Solution**:
1. Verify `lib/api-client.ts` is being used
2. Check Better Auth session in browser dev tools
3. Verify JWT token format matches backend expectations

### Issue: Chat Window Covered by Page Content

**Symptom**: Chat window appears behind modals or other elements

**Solution**:
1. Check z-index values in `tailwind.config.js`
2. Increase z-index if needed (e.g., 10000)
3. Verify fixed positioning is applied

### Issue: Session Storage Not Persisting

**Symptom**: Chat state lost on page navigation

**Solution**:
1. Verify session storage is enabled in browser
2. Check for incognito/private mode (session storage may behave differently)
3. Verify `saveChatState()` is called on state changes

### Issue: Character Counter Not Updating

**Symptom**: Counter shows incorrect value or doesn't update

**Solution**:
1. Verify `onChange` handler is attached to input
2. Check for controlled component pattern (value + onChange)
3. Verify state updates trigger re-renders

---

## Step 6: Deployment Checklist

Before deploying to production:

- [ ] Environment variables configured in production environment
- [ ] HTTPS enabled (JWT security requirement)
- [ ] Backend /api/chat endpoint deployed and accessible
- [ ] All Playwright tests passing
- [ ] Phase-2 regression tests passing
- [ ] Error messages user-friendly (no technical details)
- [ ] Performance targets met (< 1s open, < 300ms animations)
- [ ] Browser compatibility tested (Chrome, Firefox, Safari, Edge)

---

## Step 7: Next Steps

After completing implementation:

1. **Run `/sp.tasks`**: Generate detailed task breakdown
2. **Execute Tasks**: Implement in order (Phase 1.1 → 1.8)
3. **Validate**: Run Playwright tests after each phase
4. **Document**: Update this guide with any discoveries or changes
5. **Deploy**: Follow deployment checklist above

---

## Resources

- **Specification**: [spec.md](./spec.md)
- **Implementation Plan**: [plan.md](./plan.md)
- **Research**: [research.md](./research.md)
- **Data Model**: [data-model.md](./data-model.md)
- **API Contract**: [contracts/chat-api.md](./contracts/chat-api.md)
- **Phase-2 Docs**: `frontend/README.md` (existing)

---

## Support

For questions or issues:

1. Review specification and plan documents
2. Check research.md for technology decisions
3. Consult Phase-2 documentation for existing patterns
4. Test in isolation before integrating with full application

---

## Summary

- **Setup Time**: ~30 minutes (environment + dependencies)
- **Implementation Time**: Varies by phase (see plan.md)
- **Testing Time**: ~1 hour (manual + automated)
- **Total Phases**: 8 (1.1 → 1.8)
- **Key Files**: 15+ new files in components/chat/, lib/, hooks/
- **Dependencies**: OpenAI ChatKit, existing Phase-2 infrastructure
