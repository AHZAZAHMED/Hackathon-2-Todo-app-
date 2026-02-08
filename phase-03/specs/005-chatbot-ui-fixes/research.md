# Research: Chatbot Frontend UI Fixes + Playwright Validation

**Feature**: 005-chatbot-ui-fixes
**Date**: 2026-02-08
**Status**: Complete

## Overview

This research document resolves all technical unknowns for fixing the Phase-3 Chatbot Frontend UI issues. The research focuses on CSS constraints, z-index management, event handlers, ChatKit rendering, and Playwright validation.

## Research Area 1: ChatKit Container Sizing Best Practices

### Decision

Use CSS `max-width`, `max-height`, and `overflow: hidden` on the parent container wrapping the ChatKit component. ChatKit respects parent container constraints when properly configured.

### Rationale

- ChatKit is a web component that adapts to its container size
- Setting constraints on the parent container is more reliable than trying to constrain ChatKit directly
- `overflow: hidden` prevents ChatKit from breaking out of the container
- `max-width: 420px` and `max-height: 70vh` provide reasonable constraints for desktop
- Using viewport units (vh) ensures the chat doesn't exceed screen height

### Implementation Guidance

```tsx
// ChatInterface.tsx
<div className="fixed bottom-6 right-6 z-50 w-full max-w-[420px] h-auto max-h-[70vh] overflow-hidden rounded-xl shadow-2xl bg-white flex flex-col">
  <ChatHeader />
  <div className="flex-1 overflow-hidden">
    <ChatKit control={chatKitHook.control} className="h-full w-full" />
  </div>
</div>
```

**Key Points**:
- Parent container has `max-w-[420px]` and `max-h-[70vh]`
- `overflow-hidden` prevents content overflow
- Inner ChatKit container has `flex-1` to fill available space
- ChatKit itself has `h-full w-full` to fill its container

### Alternatives Considered

- **Alternative 1**: Apply size constraints directly to ChatKit component
  - Rejected: ChatKit may not respect direct sizing, could cause rendering issues
- **Alternative 2**: Use fixed pixel heights instead of vh units
  - Rejected: Doesn't adapt to different screen sizes, could overflow on small screens

### Gotchas

- Must use `overflow-hidden` on parent to prevent ChatKit from expanding beyond constraints
- ChatKit needs explicit `h-full w-full` to fill the container properly
- Mobile requires different constraints (full-screen modal)

---

## Research Area 2: Z-Index Hierarchy Management

### Decision

Use z-index values: **icon = 60**, **chat window = 50**, **page content = default (0-10)**. Define these as CSS custom properties in globals.css for consistency.

### Rationale

- Icon must be above chat window to remain clickable when chat is open
- Gap of 10 between icon and window provides buffer for any intermediate elements
- Values 50-60 are high enough to be above most page content but not absurdly high
- Using CSS custom properties makes z-index hierarchy maintainable
- Tailwind's default z-index scale goes up to z-50, so z-60 requires custom config

### Implementation Guidance

```css
/* globals.css */
@theme inline {
  /* Z-index hierarchy for chat components */
  --z-50: 50;  /* Chat window */
  --z-60: 60;  /* Floating chat icon (above window) */
}
```

```tsx
// FloatingChatLauncher.tsx
<button
  className="fixed bottom-6 right-6 z-[60] h-14 w-14 rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-700"
  onClick={openChat}
>
  <MessageCircle className="h-6 w-6 mx-auto" />
</button>

// ChatInterface.tsx
<div className="fixed bottom-6 right-6 z-50 ...">
  {/* Chat window content */}
</div>
```

**Key Points**:
- Use `z-[60]` for icon (Tailwind arbitrary value)
- Use `z-50` for chat window (Tailwind default)
- Icon always renders above window due to higher z-index
- Both use `fixed` positioning to ensure z-index works correctly

### Alternatives Considered

- **Alternative 1**: Use z-index 9999 for icon
  - Rejected: Unnecessarily high, makes it hard to add elements above if needed
- **Alternative 2**: Use z-index 100 for icon, 90 for window
  - Rejected: Too high, conflicts with potential modal overlays (usually 100+)

### Gotchas

- Both icon and window must use `fixed` positioning for z-index to work
- If either uses `absolute` positioning, z-index behavior may be unpredictable
- Tailwind's z-50 is built-in, but z-60 requires arbitrary value syntax `z-[60]`

---

## Research Area 3: React Event Handlers for Close Behavior

### Decision

Use `useEffect` hooks to add/remove event listeners for Escape key and click-outside. Clean up listeners on component unmount to prevent memory leaks.

### Rationale

- `useEffect` is the React-recommended way to add event listeners
- Cleanup function ensures listeners are removed when component unmounts
- `useRef` for container element enables click-outside detection
- Event listeners don't interfere with ChatKit's internal events

### Implementation Guidance

```tsx
// ChatInterface.tsx
import { useEffect, useRef } from 'react';
import { useChatUI } from '@/lib/contexts/ChatUIContext';

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
    <div ref={containerRef} className="...">
      {/* Chat content */}
    </div>
  );
}
```

**Key Points**:
- Use `keydown` event for Escape key (more reliable than `keyup`)
- Use `mousedown` for click-outside (triggers before `click`)
- Use `useRef` to get reference to container element
- Check `contains()` to determine if click was outside
- Clean up listeners in return function

### Alternatives Considered

- **Alternative 1**: Use inline event handlers (onClick, onKeyDown)
  - Rejected: Doesn't work for document-level events like Escape key
- **Alternative 2**: Use third-party library (react-outside-click-handler)
  - Rejected: Adds unnecessary dependency, simple to implement natively

### Gotchas

- Must include `closeChat` in dependency array to avoid stale closures
- Use `mousedown` instead of `click` to prevent issues with drag events
- Ensure cleanup function removes listeners to prevent memory leaks
- Click-outside should not trigger if clicking on the floating icon itself

---

## Research Area 4: ChatKit Rendering Issues

### Decision

Ensure ChatKit component mounts immediately when chat opens by removing any conditional rendering that delays mount. Use proper loading state while JWT token is being fetched.

### Rationale

- Blank panels occur when ChatKit is conditionally rendered but not yet mounted
- ChatKit needs JWT token before it can render, so fetch token before mounting
- Loading state prevents blank panel while token is being fetched
- Once token is available, ChatKit mounts and renders immediately

### Implementation Guidance

```tsx
// ChatInterface.tsx
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

  // Configure ChatKit immediately when token is available
  const chatKitHook = useChatKit({
    api: {
      url: `${apiBaseUrl}/api/chat`,
      domainKey: domainKey,
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

  // Render ChatKit immediately once token is available
  return (
    <div className="...">
      <ChatHeader />
      <div className="flex-1 overflow-hidden">
        <ChatKit control={chatKitHook.control} className="h-full w-full" />
      </div>
    </div>
  );
}
```

**Key Points**:
- Fetch JWT token on component mount (not on demand)
- Show loading state while token is being fetched
- Mount ChatKit immediately once token is available
- No conditional rendering that delays ChatKit mount
- ChatKit renders within 500ms (token fetch + mount time)

### Alternatives Considered

- **Alternative 1**: Fetch token only when user sends first message
  - Rejected: Causes blank panel until first message sent
- **Alternative 2**: Pre-fetch token in parent component
  - Rejected: Adds complexity, token may expire before chat opens

### Gotchas

- Token must be fetched before ChatKit can render
- Loading state prevents blank panel during token fetch
- ChatKit may show its own loading state while connecting to backend
- Ensure token fetch doesn't block UI rendering

---

## Research Area 5: Playwright Browser Automation

### Decision

Use the `browsing-with-playwright` skill to create automated validation tests. Playwright can interact with floating UI elements, validate z-index, and check size constraints.

### Rationale

- `browsing-with-playwright` skill provides Playwright automation capabilities
- Playwright can navigate pages, click elements, measure dimensions, and capture screenshots
- Playwright supports mobile viewport emulation for responsive testing
- Playwright can detect console errors during test execution
- Automated tests prevent regression and validate all 10 requirements

### Implementation Guidance

**Test Structure**:
```typescript
// tests/playwright/chatbot-ui.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Chatbot UI Validation', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to authenticated page
    await page.goto('http://localhost:3000/dashboard');
    // Assume user is already logged in (or perform login)
  });

  test('Icon visible on page load', async ({ page }) => {
    const icon = page.locator('[aria-label="Open chat"]');
    await expect(icon).toBeVisible();

    // Check position
    const box = await icon.boundingBox();
    expect(box).toBeTruthy();
    expect(box!.x).toBeGreaterThan(0); // Right side
    expect(box!.y).toBeGreaterThan(0); // Bottom
  });

  test('Click icon opens chat with correct size', async ({ page }) => {
    await page.click('[aria-label="Open chat"]');

    const chatWindow = page.locator('.chat-window'); // Add class to identify
    await expect(chatWindow).toBeVisible();

    // Check size constraints
    const box = await chatWindow.boundingBox();
    expect(box!.width).toBeLessThanOrEqual(420);
    expect(box!.height).toBeLessThanOrEqual(window.innerHeight * 0.7);
  });

  test('Chat renders content (not blank)', async ({ page }) => {
    await page.click('[aria-label="Open chat"]');

    // Wait for ChatKit to load
    await page.waitForTimeout(500);

    // Check for ChatKit content
    const chatContent = page.locator('openai-chatkit');
    await expect(chatContent).toBeVisible();
  });

  test('Icon remains clickable when chat open', async ({ page }) => {
    await page.click('[aria-label="Open chat"]');

    const icon = page.locator('[aria-label="Open chat"]');
    await expect(icon).toBeVisible();

    // Click icon to close
    await icon.click();

    const chatWindow = page.locator('.chat-window');
    await expect(chatWindow).not.toBeVisible();
  });

  test('Close button works', async ({ page }) => {
    await page.click('[aria-label="Open chat"]');
    await page.click('[aria-label="Close chat"]');

    const chatWindow = page.locator('.chat-window');
    await expect(chatWindow).not.toBeVisible();
  });

  test('Escape key closes chat', async ({ page }) => {
    await page.click('[aria-label="Open chat"]');
    await page.keyboard.press('Escape');

    const chatWindow = page.locator('.chat-window');
    await expect(chatWindow).not.toBeVisible();
  });

  test('Click outside closes chat', async ({ page }) => {
    await page.click('[aria-label="Open chat"]');

    // Click on page background (outside chat)
    await page.click('body', { position: { x: 10, y: 10 } });

    const chatWindow = page.locator('.chat-window');
    await expect(chatWindow).not.toBeVisible();
  });

  test('Mobile viewport behavior', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone size

    await page.click('[aria-label="Open chat"]');

    const chatWindow = page.locator('.chat-window');
    const box = await chatWindow.boundingBox();

    // Should be full-screen on mobile
    expect(box!.width).toBeCloseTo(375, 10);
    expect(box!.height).toBeCloseTo(667, 10);
  });

  test('No console errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.click('[aria-label="Open chat"]');
    await page.waitForTimeout(1000);
    await page.click('[aria-label="Close chat"]');

    expect(errors).toHaveLength(0);
  });
});
```

**Playwright Configuration**:
```typescript
// tests/playwright/playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/playwright',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'mobile',
      use: { ...devices['iPhone 12'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

**Key Points**:
- Use `browsing-with-playwright` skill to execute tests
- Tests validate all 10 requirements from spec
- Capture screenshots on failure for debugging
- Test both desktop and mobile viewports
- Monitor console for errors during test execution

### Alternatives Considered

- **Alternative 1**: Manual testing only
  - Rejected: Time-consuming, error-prone, no regression prevention
- **Alternative 2**: Cypress instead of Playwright
  - Rejected: Playwright is more modern, better TypeScript support

### Gotchas

- Tests require frontend server to be running (localhost:3000)
- Authentication state must be set up before tests run
- Timing issues may require `waitForTimeout` or `waitForSelector`
- Mobile viewport tests require explicit viewport size setting

---

## Research Area 6: Responsive Mobile Behavior

### Decision

Use Tailwind CSS responsive breakpoints to switch between desktop panel (max-width: 420px) and mobile full-screen modal (<640px). Apply different styles at the `md:` breakpoint.

### Rationale

- Tailwind's `md:` breakpoint (640px) is appropriate for mobile/desktop split
- Full-screen modal on mobile provides better UX than small panel
- Desktop panel maintains floating chatbot aesthetic
- Responsive classes keep code clean and maintainable

### Implementation Guidance

```tsx
// ChatInterface.tsx
<div className="
  fixed
  bottom-0 right-0 left-0 top-0
  z-50
  bg-white
  flex flex-col
  md:bottom-6 md:right-6 md:left-auto md:top-auto
  md:w-96 md:max-w-[420px] md:h-auto md:max-h-[70vh]
  md:rounded-xl md:shadow-2xl
">
  <ChatHeader />
  <div className="flex-1 overflow-hidden">
    <ChatKit control={chatKitHook.control} className="h-full w-full" />
  </div>
</div>
```

**Breakdown**:
- **Mobile (<640px)**: `bottom-0 right-0 left-0 top-0` = full-screen
- **Desktop (≥640px)**: `md:bottom-6 md:right-6 md:left-auto md:top-auto` = fixed panel
- **Mobile**: No border-radius (full-screen)
- **Desktop**: `md:rounded-xl` = rounded corners
- **Mobile**: Full width/height
- **Desktop**: `md:w-96 md:max-w-[420px] md:max-h-[70vh]` = constrained size

**Key Points**:
- Use Tailwind responsive prefixes (`md:`) for desktop styles
- Mobile styles are default (no prefix)
- Transition between mobile and desktop is automatic
- Both modes maintain proper z-index hierarchy

### Alternatives Considered

- **Alternative 1**: Use JavaScript to detect screen size and render different components
  - Rejected: More complex, Tailwind responsive classes are simpler
- **Alternative 2**: Use `sm:` breakpoint (480px) instead of `md:` (640px)
  - Rejected: 640px is better split point for mobile/desktop

### Gotchas

- Must test on actual mobile devices, not just browser DevTools
- Transition between breakpoints should be smooth
- Icon positioning may need adjustment on mobile
- Full-screen modal on mobile should still allow close via icon or Escape

---

## Summary

All technical unknowns have been resolved:

1. ✅ **ChatKit Container Sizing**: Use parent container with `max-width: 420px`, `max-height: 70vh`, `overflow: hidden`
2. ✅ **Z-Index Hierarchy**: Icon = 60, Window = 50, both using `fixed` positioning
3. ✅ **Event Handlers**: Use `useEffect` hooks for Escape key and click-outside, with proper cleanup
4. ✅ **ChatKit Rendering**: Fetch JWT token on mount, show loading state, mount ChatKit immediately when token available
5. ✅ **Playwright Validation**: Use `browsing-with-playwright` skill with 10 automated tests
6. ✅ **Responsive Mobile**: Use Tailwind `md:` breakpoint to switch between full-screen mobile and panel desktop

## Implementation Readiness

All research is complete. No blocking technical unknowns remain. Ready to proceed with Phase 1: Design & Contracts.
