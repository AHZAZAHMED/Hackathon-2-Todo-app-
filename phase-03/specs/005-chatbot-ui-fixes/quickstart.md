# Quickstart Guide: Chatbot Frontend UI Fixes

**Feature**: 005-chatbot-ui-fixes
**Date**: 2026-02-08
**For**: Developers implementing the UI fixes

## Overview

This guide provides step-by-step instructions for fixing critical UI defects in the Phase-3 Chatbot Frontend. The fixes address sizing, positioning, z-index, event handlers, and ChatKit rendering issues.

**What You'll Fix**:
- ❌ Chat window opens too large (covers entire viewport)
- ❌ Chat icon hidden behind window when open
- ❌ Close/minimize buttons non-functional
- ❌ Blank/empty ChatKit panels
- ❌ No keyboard shortcuts (Escape key)
- ❌ No click-outside-to-close behavior
- ❌ Poor mobile responsiveness

**What You'll Achieve**:
- ✅ Chat window constrained to 420px × 70vh
- ✅ Icon always visible above window (z-index: 60)
- ✅ Working close/minimize buttons
- ✅ ChatKit renders immediately
- ✅ Escape key closes chat
- ✅ Click-outside closes chat
- ✅ Full-screen modal on mobile

## Prerequisites

**Required Knowledge**:
- React 19+ with hooks (useState, useEffect, useRef)
- TypeScript strict mode
- Tailwind CSS responsive design
- Next.js 16+ App Router
- OpenAI ChatKit React library

**Environment Setup**:
```bash
# Ensure dependencies are installed
cd frontend
npm install

# Verify ChatKit is installed
npm list @openai/chatkit-react
# Should show: @openai/chatkit-react@1.4.3

# Start development server
npm run dev
# Frontend: http://localhost:3000
```

**Files You'll Modify**:
1. `frontend/components/chat/ChatInterface.tsx` (main fixes)
2. `frontend/components/chat/FloatingChatLauncher.tsx` (z-index fix)
3. `frontend/components/chat/ChatHeader.tsx` (close/minimize fix)
4. `frontend/app/globals.css` (z-index hierarchy, animations)

## Component Architecture

### Current Component Tree

```
App Layout
└── ChatUIProvider (existing)
    ├── Navbar (existing)
    ├── Main Content (existing)
    ├── Footer (existing)
    └── FloatingChatLauncher (MODIFY)
        ├── Floating Icon Button (MODIFY - z-index fix)
        └── ChatInterface (MODIFY - when open)
            ├── ChatHeader (MODIFY - close/minimize fix)
            └── ChatKit Component (existing - ensure renders)
```

### Component Responsibilities

**FloatingChatLauncher**:
- Renders floating icon button
- Toggles chat visibility on click
- Manages z-index (icon above window)

**ChatInterface**:
- Renders chat window with size constraints
- Manages event handlers (Escape, click-outside)
- Ensures ChatKit mounts correctly
- Handles responsive behavior

**ChatHeader**:
- Renders close (X) and minimize (-) buttons
- Connects buttons to ChatUIContext actions

## Step-by-Step Implementation

### Step 1: Fix Z-Index Hierarchy (globals.css)

**File**: `frontend/app/globals.css`

**Add z-index custom properties**:

```css
@theme inline {
  /* Z-index hierarchy for chat components */
  --z-50: 50;  /* Chat window */
  --z-60: 60;  /* Floating chat icon (above window) */
}
```

**Why**: Tailwind's default z-index scale goes up to z-50. We need z-60 for the icon to stay above the window.

**Add transition animations**:

```css
/* Chat window animations */
.chat-window-enter {
  animation: slideUp 300ms ease-in-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

### Step 2: Fix FloatingChatLauncher Z-Index

**File**: `frontend/components/chat/FloatingChatLauncher.tsx`

**Current Issue**: Icon has same or lower z-index than window, gets hidden.

**Fix**: Update icon button className to use z-[60]:

```tsx
// Before
<button
  className="fixed bottom-6 right-6 z-50 h-14 w-14 rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-700"
  onClick={openChat}
>
  <MessageCircle className="h-6 w-6 mx-auto" />
</button>

// After
<button
  className="fixed bottom-6 right-6 z-[60] h-14 w-14 rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-700 transition-transform hover:scale-105"
  onClick={toggleChat}  // Changed from openChat to toggleChat
  aria-label="Open chat"
>
  <MessageCircle className="h-6 w-6 mx-auto" />
</button>
```

**Key Changes**:
- `z-50` → `z-[60]` (Tailwind arbitrary value)
- `onClick={openChat}` → `onClick={toggleChat}` (toggle instead of always open)
- Added `aria-label` for Playwright tests
- Added `hover:scale-105` for better UX

---

### Step 3: Fix ChatInterface Container Sizing

**File**: `frontend/components/chat/ChatInterface.tsx`

**Current Issue**: No size constraints, window covers entire viewport.

**Fix**: Add proper container constraints with responsive behavior:

```tsx
import { useEffect, useRef } from 'react';
import { useChatUI } from '@/lib/contexts/ChatUIContext';
import { ChatKit } from '@openai/chatkit-react';
import { ChatHeader } from './ChatHeader';

export function ChatInterface() {
  const { closeChat } = useChatUI();
  const containerRef = useRef<HTMLDivElement>(null);

  // Escape key handler
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        closeChat();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [closeChat]);

  // Click-outside handler
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        closeChat();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [closeChat]);

  return (
    <div
      ref={containerRef}
      className="
        fixed
        bottom-0 right-0 left-0 top-0
        z-50
        bg-white
        flex flex-col
        md:bottom-6 md:right-6 md:left-auto md:top-auto
        md:w-96 md:max-w-[420px] md:h-auto md:max-h-[70vh]
        md:rounded-xl md:shadow-2xl
        overflow-hidden
        transition-all duration-300 ease-in-out
        chat-window
      "
      role="dialog"
      aria-label="Chat window"
    >
      <ChatHeader />
      <div className="flex-1 overflow-hidden">
        <ChatKit control={chatKitHook.control} className="h-full w-full" />
      </div>
    </div>
  );
}
```

**Key Changes**:
- Added `containerRef` for click-outside detection
- Added Escape key handler with cleanup
- Added click-outside handler with cleanup
- Mobile: `bottom-0 right-0 left-0 top-0` (full-screen)
- Desktop: `md:bottom-6 md:right-6 md:max-w-[420px] md:max-h-[70vh]`
- Added `overflow-hidden` to prevent content overflow
- Added `role="dialog"` and `aria-label` for accessibility
- Added `chat-window` class for Playwright tests

**Responsive Breakdown**:
- **Mobile (<640px)**: Full-screen modal, no margins, no border-radius
- **Desktop (≥640px)**: Fixed panel at bottom-right, 420px max width, 70vh max height

---

### Step 4: Fix ChatHeader Close/Minimize Buttons

**File**: `frontend/components/chat/ChatHeader.tsx`

**Current Issue**: Buttons don't call ChatUIContext actions.

**Fix**: Connect buttons to context:

```tsx
import { X, Minus } from 'lucide-react';
import { useChatUI } from '@/lib/contexts/ChatUIContext';

export function ChatHeader() {
  const { closeChat, minimizeChat } = useChatUI();

  return (
    <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-white">
      <h3 className="text-lg font-semibold text-gray-900">Chat Assistant</h3>
      <div className="flex items-center gap-2">
        <button
          onClick={minimizeChat}
          className="p-1 rounded hover:bg-gray-100 transition-colors"
          aria-label="Minimize chat"
        >
          <Minus className="h-5 w-5 text-gray-600" />
        </button>
        <button
          onClick={closeChat}
          className="p-1 rounded hover:bg-gray-100 transition-colors"
          aria-label="Close chat"
        >
          <X className="h-5 w-5 text-gray-600" />
        </button>
      </div>
    </div>
  );
}
```

**Key Changes**:
- Import `useChatUI` hook
- Connect `onClick={closeChat}` to close button
- Connect `onClick={minimizeChat}` to minimize button
- Added `aria-label` for accessibility and Playwright tests
- Added hover states for better UX

---

### Step 5: Ensure ChatKit Renders (No Blank Panels)

**File**: `frontend/components/chat/ChatInterface.tsx`

**Current Issue**: ChatKit shows blank/empty panel on initial load.

**Fix**: Fetch JWT token on mount and show loading state:

```tsx
import { useState, useEffect, useRef } from 'react';
import { useChatKit } from '@openai/chatkit-react';

export function ChatInterface() {
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Fetch JWT token immediately on mount
  useEffect(() => {
    const fetchToken = async () => {
      try {
        const response = await fetch('/api/auth/token', {
          credentials: 'include',
        });
        if (response.ok) {
          const data = await response.json();
          setToken(data.token);
        }
      } catch (error) {
        console.error('Failed to fetch JWT token:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchToken();
  }, []);

  // Configure ChatKit with JWT
  const chatKitHook = useChatKit({
    api: {
      url: `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/chat`,
      domainKey: process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || '',
      fetch: async (input, init) => {
        const headers = new Headers(init?.headers);
        if (token) {
          headers.set('Authorization', `Bearer ${token}`);
        }
        return fetch(input, { ...init, headers, credentials: 'include' });
      },
    },
  });

  // Show loading state while fetching token
  if (loading) {
    return (
      <div className="...">
        <ChatHeader />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-gray-500">Loading chat...</div>
        </div>
      </div>
    );
  }

  // Render ChatKit once token is available
  return (
    <div ref={containerRef} className="...">
      <ChatHeader />
      <div className="flex-1 overflow-hidden">
        <ChatKit control={chatKitHook.control} className="h-full w-full" />
      </div>
    </div>
  );
}
```

**Key Changes**:
- Fetch JWT token on component mount (not on demand)
- Show loading state while token is being fetched
- Mount ChatKit immediately once token is available
- No conditional rendering that delays ChatKit mount

---

## CSS Architecture

### Z-Index Hierarchy

**Purpose**: Ensure icon stays above window.

**Values**:
- Page content: 0-10 (default)
- Chat window: 50
- Floating icon: 60

**Implementation**:
```css
/* globals.css */
@theme inline {
  --z-50: 50;
  --z-60: 60;
}
```

**Usage**:
```tsx
// Icon
className="... z-[60] ..."

// Window
className="... z-50 ..."
```

### Responsive Breakpoints

**Tailwind Breakpoint**: `md:` (640px)

**Mobile (<640px)**:
```tsx
className="bottom-0 right-0 left-0 top-0"  // Full-screen
```

**Desktop (≥640px)**:
```tsx
className="md:bottom-6 md:right-6 md:left-auto md:top-auto md:max-w-[420px] md:max-h-[70vh] md:rounded-xl"
```

### Animations

**Slide-up animation** (optional enhancement):
```css
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

## Testing Approach

### Manual Testing Checklist

Before running Playwright tests, verify manually:

- [ ] Chat icon visible on page load
- [ ] Clicking icon opens chat
- [ ] Chat window ≤ 420px width
- [ ] Chat window ≤ 70vh height
- [ ] Chat has 24px bottom margin
- [ ] Icon visible when chat open
- [ ] Clicking icon closes chat
- [ ] Close (X) button works
- [ ] Minimize (-) button works
- [ ] Escape key closes chat
- [ ] Click outside closes chat
- [ ] ChatKit content renders (not blank)
- [ ] Mobile: full-screen modal
- [ ] No console errors

### Playwright Automated Tests

**Setup**:
```bash
# Install Playwright
npm install -D @playwright/test

# Install browsers
npx playwright install
```

**Run tests**:
```bash
# Run all tests
npx playwright test

# Run specific test file
npx playwright test tests/playwright/chatbot-ui.spec.ts

# Run with UI mode
npx playwright test --ui

# Generate HTML report
npx playwright show-report
```

**Test file location**: `tests/playwright/chatbot-ui.spec.ts`

**Expected results**: 10/10 tests pass

---

## Common Issues and Solutions

### Issue 1: Icon Still Hidden Behind Window

**Symptom**: Icon disappears when chat opens.

**Cause**: Z-index not applied correctly.

**Solution**:
1. Verify icon has `z-[60]` class
2. Verify window has `z-50` class
3. Ensure both use `fixed` positioning
4. Check browser DevTools computed styles

### Issue 2: Blank ChatKit Panel

**Symptom**: White/black empty panel instead of chat UI.

**Cause**: ChatKit mounting before JWT token available.

**Solution**:
1. Fetch JWT token on component mount
2. Show loading state while fetching
3. Mount ChatKit only after token available
4. Verify `/api/auth/token` endpoint works

### Issue 3: Click-Outside Not Working

**Symptom**: Clicking outside doesn't close chat.

**Cause**: Event listener not attached or containerRef not set.

**Solution**:
1. Verify `containerRef` is attached to container div
2. Check `useEffect` dependency array includes `closeChat`
3. Verify cleanup function removes listener
4. Use `mousedown` event (not `click`)

### Issue 4: Escape Key Not Working

**Symptom**: Pressing Escape doesn't close chat.

**Cause**: Event listener not attached or wrong event type.

**Solution**:
1. Use `keydown` event (not `keyup`)
2. Check `e.key === 'Escape'` (case-sensitive)
3. Verify cleanup function removes listener
4. Ensure no other component is capturing Escape

### Issue 5: Mobile Not Full-Screen

**Symptom**: Chat has margins on mobile.

**Cause**: Responsive classes not applied correctly.

**Solution**:
1. Mobile styles should have NO `md:` prefix
2. Desktop styles should have `md:` prefix
3. Verify breakpoint: `md:` = 640px
4. Test on actual mobile device or DevTools mobile emulation

---

## Validation

### Phase 1 Validation (Manual)

After implementing all fixes:

1. **Visual Inspection**:
   - Open chat, verify size and position
   - Check icon visibility
   - Test all close methods (button, icon, Escape, click-outside)
   - Verify ChatKit renders correctly

2. **Browser DevTools**:
   - Check computed z-index values
   - Verify no console errors
   - Inspect element dimensions
   - Test responsive behavior

3. **Cross-Browser Testing**:
   - Chrome 90+
   - Firefox 88+
   - Safari 14+
   - Edge 90+

### Phase 2 Validation (Automated)

Run Playwright test suite:

```bash
npx playwright test tests/playwright/chatbot-ui.spec.ts
```

**Success Criteria**: 10/10 tests pass

---

## Next Steps

After completing implementation:

1. ✅ Run manual testing checklist
2. ✅ Fix any issues found
3. ✅ Run Playwright test suite
4. ✅ Verify all 10 tests pass
5. ✅ Capture screenshots for documentation
6. ✅ Create PHR documenting implementation
7. ✅ Commit changes with proper message
8. ✅ Create pull request

---

**Status**: ✅ Quickstart guide complete. Ready for implementation.
