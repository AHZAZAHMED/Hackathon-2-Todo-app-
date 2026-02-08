# Data Model: Chatbot Frontend UI Fixes + Playwright Validation

**Feature**: 005-chatbot-ui-fixes
**Date**: 2026-02-08
**Status**: Complete

## Overview

This feature modifies existing UI components and does not introduce new data structures. The existing ChatUIState from Phase-3 (004-chatbot-frontend) is sufficient for managing chat visibility and state.

## Existing Data Structures (No Changes Required)

### ChatUIState (Existing - No Modifications)

**Location**: `frontend/lib/contexts/ChatUIContext.tsx`

**Structure**:
```typescript
interface ChatUIState {
  isOpen: boolean;      // Whether chat window is visible
  isMinimized: boolean; // Whether chat is minimized (currently unused)
}
```

**Purpose**: Manages the visibility state of the floating chat interface.

**Usage**:
- `isOpen: true` - Chat window is visible
- `isOpen: false` - Only floating icon is visible
- `isMinimized` - Reserved for future minimize functionality

**State Management**:
- Managed by ChatUIContext (React Context API)
- Provides `openChat()`, `closeChat()`, `toggleChat()` functions
- State persists during component lifecycle
- Does NOT persist across page reloads (intentional - chat closes on navigation)

### ChatKit Configuration (Existing - No Modifications)

**Location**: `frontend/components/chat/ChatInterface.tsx`

**Structure**:
```typescript
interface ChatKitConfig {
  api: {
    url: string;           // Backend chat endpoint
    domainKey: string;     // OpenAI domain key
    fetch: FetchFunction;  // Custom fetch with JWT
  };
}
```

**Purpose**: Configures ChatKit component with backend API and authentication.

**No changes required** - existing configuration is correct.

## CSS Class Structure (New - For UI Fixes)

### Z-Index Hierarchy

**Purpose**: Define stacking order for chat components.

**Structure**:
```css
/* globals.css */
@theme inline {
  --z-50: 50;  /* Chat window */
  --z-60: 60;  /* Floating chat icon (above window) */
}
```

**Usage**:
- Floating icon: `z-[60]` (Tailwind arbitrary value)
- Chat window: `z-50` (Tailwind default)
- Page content: default (0-10)

**Rationale**: Icon must be above window to remain clickable when chat is open.

### Component Class Structure

**FloatingChatLauncher** (Icon Button):
```typescript
className="fixed bottom-6 right-6 z-[60] h-14 w-14 rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-700 transition-transform hover:scale-105"
```

**ChatInterface** (Chat Window - Desktop):
```typescript
className="fixed bottom-6 right-6 z-50 w-full max-w-[420px] h-auto max-h-[70vh] overflow-hidden rounded-xl shadow-2xl bg-white flex flex-col transition-all duration-300 ease-in-out"
```

**ChatInterface** (Chat Window - Mobile):
```typescript
className="fixed bottom-0 right-0 left-0 top-0 z-50 bg-white flex flex-col md:bottom-6 md:right-6 md:left-auto md:top-auto md:w-96 md:max-w-[420px] md:h-auto md:max-h-[70vh] md:rounded-xl md:shadow-2xl"
```

**ChatHeader** (Header with Close/Minimize):
```typescript
className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-white"
```

**ChatKit Container** (Inner Container):
```typescript
className="flex-1 overflow-hidden"
```

## Event Handler Data

### Escape Key Handler

**Type**: Keyboard Event Listener

**Structure**:
```typescript
useEffect(() => {
  const handleEscape = (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      closeChat();
    }
  };

  document.addEventListener('keydown', handleEscape);
  return () => document.removeEventListener('keydown', handleEscape);
}, [closeChat]);
```

**Data Flow**:
1. User presses Escape key
2. Browser fires `keydown` event
3. Handler checks if key is 'Escape'
4. Calls `closeChat()` from ChatUIContext
5. ChatUIState updates: `isOpen: false`
6. Chat window unmounts

### Click-Outside Handler

**Type**: Mouse Event Listener

**Structure**:
```typescript
const containerRef = useRef<HTMLDivElement>(null);

useEffect(() => {
  const handleClickOutside = (e: MouseEvent) => {
    if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
      closeChat();
    }
  };

  document.addEventListener('mousedown', handleClickOutside);
  return () => document.removeEventListener('mousedown', handleClickOutside);
}, [closeChat]);
```

**Data Flow**:
1. User clicks anywhere on page
2. Browser fires `mousedown` event
3. Handler checks if click target is outside chat container
4. If outside, calls `closeChat()`
5. ChatUIState updates: `isOpen: false`
6. Chat window unmounts

## Responsive Breakpoint Data

**Tailwind Breakpoint**: `md:` (640px)

**Mobile (<640px)**:
- Full-screen modal
- No border-radius
- No margins
- Covers entire viewport

**Desktop (≥640px)**:
- Fixed panel at bottom-right
- Border-radius: 12px
- Max-width: 420px
- Max-height: 70vh
- Bottom margin: 24px
- Right margin: 24px

## JWT Token State (Existing - No Changes)

**Location**: `frontend/components/chat/ChatInterface.tsx`

**Structure**:
```typescript
const [token, setToken] = useState<string | null>(null);
const [loading, setLoading] = useState(true);
```

**Purpose**: Store JWT token for ChatKit authentication.

**Data Flow**:
1. Component mounts
2. Fetch JWT from `/api/auth/token`
3. Store in `token` state
4. Pass to ChatKit via custom fetch function
5. ChatKit attaches to all API requests

**No changes required** - existing token management is correct.

## Summary

**New Data Structures**: None

**Modified Data Structures**: None

**New CSS Classes**: Yes (z-index hierarchy, responsive classes)

**New Event Handlers**: Yes (Escape key, click-outside)

**Existing Structures Preserved**:
- ✅ ChatUIState (no changes)
- ✅ ChatKitConfig (no changes)
- ✅ JWT token state (no changes)

**Data Model Complexity**: Minimal - this is a UI-only fix with no new data entities.

**Database Impact**: None - no database changes required.

**API Impact**: None - no API changes required.

**State Management Impact**: None - existing ChatUIContext is sufficient.

---

**Status**: ✅ Data model analysis complete. No new data structures required. Ready for contracts phase.
