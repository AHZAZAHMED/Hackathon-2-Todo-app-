# Playwright Validation Contract

**Feature**: 005-chatbot-ui-fixes
**Date**: 2026-02-08
**Status**: Ready for Implementation

## Overview

This contract defines the automated browser validation tests required to verify all chatbot UI fixes. Tests will be implemented using Playwright via the `browsing-with-playwright` skill.

## Test Environment

**Base URL**: `http://localhost:3000`
**Authentication**: Tests assume user is already logged in (or perform login in beforeEach)
**Browser**: Chromium (primary), with mobile viewport tests
**Timeout**: 30 seconds per test
**Screenshots**: Capture on failure for debugging

## Test Suite: Chatbot UI Validation

### Test 1: Icon Visibility on Page Load

**Objective**: Verify floating chat icon is visible and positioned correctly on page load.

**Prerequisites**:
- User is authenticated
- Navigate to `/dashboard` or any authenticated page

**Test Steps**:
1. Navigate to `http://localhost:3000/dashboard`
2. Wait for page to load completely
3. Locate floating chat icon by selector: `[aria-label="Open chat"]` or `.chat-icon`

**Assertions**:
- ✅ Icon is visible (`toBeVisible()`)
- ✅ Icon has correct position (bottom-right corner)
- ✅ Icon bounding box: `x > viewport.width - 100` (right side)
- ✅ Icon bounding box: `y > viewport.height - 100` (bottom side)
- ✅ Icon z-index is 60 or higher (computed style check)

**Expected Outcome**: Floating chat icon appears at bottom-right corner, always visible.

---

### Test 2: Click Icon Opens Chat

**Objective**: Verify clicking the floating icon opens the chat window with correct size and position.

**Prerequisites**:
- User is authenticated
- Chat is initially closed

**Test Steps**:
1. Navigate to authenticated page
2. Locate floating chat icon
3. Click the icon
4. Wait for chat window to appear

**Assertions**:
- ✅ Chat window becomes visible within 500ms
- ✅ Chat window selector: `.chat-window` or `[role="dialog"]`
- ✅ Chat window width ≤ 420px
- ✅ Chat window height ≤ 70% of viewport height
- ✅ Chat window has bottom margin ≥ 24px (desktop)
- ✅ Chat window has right margin ≥ 24px (desktop)
- ✅ Chat window z-index is 50 (below icon)
- ✅ Chat window has rounded corners (border-radius > 0)

**Expected Outcome**: Chat window opens at correct size with proper positioning.

---

### Test 3: Chat Renders Content (Not Blank)

**Objective**: Verify ChatKit content renders correctly without blank/empty panels.

**Prerequisites**:
- User is authenticated
- Chat window is open

**Test Steps**:
1. Open chat window
2. Wait for ChatKit to load (max 500ms)
3. Locate ChatKit component: `openai-chatkit` or `.chatkit-container`

**Assertions**:
- ✅ ChatKit component is visible
- ✅ ChatKit component has non-zero dimensions (width > 0, height > 0)
- ✅ ChatKit contains child elements (message list, input field)
- ✅ No blank white/black panels visible
- ✅ Chat input field is present and enabled
- ✅ Chat header is visible with title

**Expected Outcome**: ChatKit renders with visible UI elements, no blank panels.

---

### Test 4: Icon Remains Clickable When Chat Open

**Objective**: Verify floating icon stays visible and clickable above the chat window.

**Prerequisites**:
- User is authenticated
- Chat window is open

**Test Steps**:
1. Open chat window
2. Locate floating chat icon
3. Verify icon is still visible
4. Click the icon
5. Verify chat window closes

**Assertions**:
- ✅ Icon is visible when chat is open
- ✅ Icon z-index (60) > chat window z-index (50)
- ✅ Icon is not obscured by chat window (computed style check)
- ✅ Icon is clickable (click succeeds)
- ✅ Clicking icon closes chat window
- ✅ Chat window disappears within 300ms

**Expected Outcome**: Icon remains accessible and toggles chat visibility.

---

### Test 5: Close Button Works

**Objective**: Verify close (X) button in chat header closes the chat window.

**Prerequisites**:
- User is authenticated
- Chat window is open

**Test Steps**:
1. Open chat window
2. Locate close button: `[aria-label="Close chat"]` or `.close-button`
3. Click the close button
4. Verify chat window closes

**Assertions**:
- ✅ Close button is visible in chat header
- ✅ Close button is clickable
- ✅ Clicking close button closes chat window
- ✅ Chat window disappears within 300ms
- ✅ Only floating icon remains visible
- ✅ No console errors during close

**Expected Outcome**: Close button successfully closes chat window.

---

### Test 6: Escape Key Closes Chat

**Objective**: Verify pressing Escape key closes the chat window.

**Prerequisites**:
- User is authenticated
- Chat window is open

**Test Steps**:
1. Open chat window
2. Press Escape key (`page.keyboard.press('Escape')`)
3. Verify chat window closes

**Assertions**:
- ✅ Chat window is open before Escape press
- ✅ Escape key press is registered
- ✅ Chat window closes within 300ms after Escape
- ✅ Only floating icon remains visible
- ✅ No console errors during close

**Expected Outcome**: Escape key successfully closes chat window.

---

### Test 7: Click Outside Closes Chat

**Objective**: Verify clicking outside the chat window closes it.

**Prerequisites**:
- User is authenticated
- Chat window is open

**Test Steps**:
1. Open chat window
2. Click on page background (outside chat window)
   - Use coordinates: `{ x: 10, y: 10 }` (top-left corner)
3. Verify chat window closes

**Assertions**:
- ✅ Chat window is open before click
- ✅ Click outside chat window is registered
- ✅ Chat window closes within 300ms after click
- ✅ Only floating icon remains visible
- ✅ Clicking inside chat window does NOT close it (negative test)

**Expected Outcome**: Click-outside successfully closes chat window.

---

### Test 8: Size Constraints Respected

**Objective**: Verify chat window respects maximum size constraints.

**Prerequisites**:
- User is authenticated
- Chat window is open

**Test Steps**:
1. Open chat window
2. Measure chat window dimensions using `boundingBox()`
3. Verify constraints

**Assertions**:
- ✅ Chat window width ≤ 420px
- ✅ Chat window height ≤ 70% of viewport height
- ✅ Chat window bottom margin ≥ 24px (distance from viewport bottom)
- ✅ Chat window right margin ≥ 24px (distance from viewport right)
- ✅ Chat window does not overflow viewport
- ✅ Chat window has `overflow: hidden` or `overflow: auto`

**Expected Outcome**: Chat window stays within defined size constraints.

---

### Test 9: Mobile Viewport Behavior

**Objective**: Verify chat appears as full-screen modal on mobile viewports.

**Prerequisites**:
- User is authenticated
- Viewport set to mobile size

**Test Steps**:
1. Set viewport to mobile size: `{ width: 375, height: 667 }` (iPhone size)
2. Navigate to authenticated page
3. Open chat window
4. Measure chat window dimensions

**Assertions**:
- ✅ Chat window width ≈ viewport width (within 10px)
- ✅ Chat window height ≈ viewport height (within 10px)
- ✅ Chat window covers entire screen (full-screen modal)
- ✅ Chat window has no border-radius on mobile
- ✅ Close button still works on mobile
- ✅ Escape key still works on mobile

**Expected Outcome**: Chat appears as full-screen modal on mobile devices.

---

### Test 10: No Console Errors

**Objective**: Verify no console errors occur during chat interactions.

**Prerequisites**:
- User is authenticated
- Console error listener attached

**Test Steps**:
1. Attach console error listener before test
2. Navigate to authenticated page
3. Open chat window
4. Wait for ChatKit to load (1 second)
5. Close chat window
6. Reopen chat window
7. Collect all console errors

**Assertions**:
- ✅ No console errors during page load
- ✅ No console errors during chat open
- ✅ No console errors during ChatKit load
- ✅ No console errors during chat close
- ✅ No console errors during chat reopen
- ✅ Console warnings are acceptable (not errors)

**Expected Outcome**: Zero console errors during all chat interactions.

---

## Test Configuration

### Playwright Config

**File**: `tests/playwright/playwright.config.ts`

**Configuration**:
```typescript
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

### Test File Structure

**File**: `tests/playwright/chatbot-ui.spec.ts`

**Structure**:
```typescript
import { test, expect } from '@playwright/test';

test.describe('Chatbot UI Validation', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to authenticated page
    await page.goto('http://localhost:3000/dashboard');
    // Assume user is already logged in (or perform login)
  });

  test('Icon visible on page load', async ({ page }) => {
    // Test implementation
  });

  // ... other tests
});
```

## Success Criteria

**All 10 tests MUST pass** before considering the UI fixes complete.

**Test Execution**:
- Run via `browsing-with-playwright` skill
- Capture screenshots on failure
- Generate HTML report
- Verify on both desktop and mobile viewports

**Acceptance**:
- ✅ 10/10 tests pass on desktop (Chromium)
- ✅ 6/10 tests pass on mobile (Tests 1-6, 9-10)
- ✅ No console errors in any test
- ✅ All screenshots show correct UI rendering

---

**Status**: ✅ Contract complete. Ready for implementation and validation.
