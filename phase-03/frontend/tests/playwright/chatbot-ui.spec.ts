import { test, expect } from '@playwright/test';

/**
 * Chatbot UI Validation Tests
 * Feature: 005-chatbot-ui-fixes
 *
 * These tests validate all UI fixes for the chatbot interface:
 * - Icon visibility and positioning
 * - Chat window sizing and constraints
 * - Z-index hierarchy
 * - Close/minimize functionality
 * - Keyboard shortcuts (Escape)
 * - Click-outside behavior
 * - Mobile responsiveness
 */

test.describe('Chatbot UI Validation', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to authenticated page
    await page.goto('http://localhost:3000/dashboard');
    // Wait for page to load
    await page.waitForLoadState('networkidle');
  });

  test('Test 1: Icon visible on page load', async ({ page }) => {
    // Locate floating chat icon
    const icon = page.locator('button[aria-label="Open chat"]');

    // Assert icon is visible
    await expect(icon).toBeVisible();

    // Check position (bottom-right corner)
    const box = await icon.boundingBox();
    expect(box).toBeTruthy();

    if (box) {
      const viewport = page.viewportSize();
      if (viewport) {
        // Icon should be on right side (x > viewport.width - 100)
        expect(box.x).toBeGreaterThan(viewport.width - 100);
        // Icon should be on bottom (y > viewport.height - 100)
        expect(box.y).toBeGreaterThan(viewport.height - 100);
      }
    }
  });

  test('Test 2: Click icon opens chat with correct size', async ({ page }) => {
    // Click floating icon
    await page.click('button[aria-label="Open chat"]');

    // Wait for chat window to appear
    const chatWindow = page.locator('[role="dialog"][aria-label="Chat window"]');
    await expect(chatWindow).toBeVisible({ timeout: 1000 });

    // Check size constraints
    const box = await chatWindow.boundingBox();
    expect(box).toBeTruthy();

    if (box) {
      // Width should be ≤ 420px (on desktop)
      expect(box.width).toBeLessThanOrEqual(420);

      // Height should be ≤ 70% of viewport height
      const viewport = page.viewportSize();
      if (viewport) {
        expect(box.height).toBeLessThanOrEqual(viewport.height * 0.7);
      }
    }
  });

  test('Test 3: Chat renders content (not blank)', async ({ page }) => {
    // Open chat window
    await page.click('button[aria-label="Open chat"]');

    // Wait for ChatKit to load
    await page.waitForTimeout(500);

    // Check for chat window
    const chatWindow = page.locator('[role="dialog"][aria-label="Chat window"]');
    await expect(chatWindow).toBeVisible();

    // Verify chat window has non-zero dimensions
    const box = await chatWindow.boundingBox();
    expect(box).toBeTruthy();
    if (box) {
      expect(box.width).toBeGreaterThan(0);
      expect(box.height).toBeGreaterThan(0);
    }

    // Check for chat header
    const header = page.locator('text=Chat Assistant');
    await expect(header).toBeVisible();
  });

  test('Test 4: Icon remains clickable when chat open', async ({ page }) => {
    // Open chat window
    await page.click('button[aria-label="Open chat"]');

    // Wait for chat to open
    await page.waitForTimeout(300);

    // Icon should still be visible
    const icon = page.locator('button[aria-label="Open chat"]');
    await expect(icon).toBeVisible();

    // Click icon to close
    await icon.click();

    // Chat window should close
    const chatWindow = page.locator('[role="dialog"][aria-label="Chat window"]');
    await expect(chatWindow).not.toBeVisible({ timeout: 1000 });
  });

  test('Test 5: Close button works', async ({ page }) => {
    // Open chat window
    await page.click('button[aria-label="Open chat"]');

    // Wait for chat to open
    await page.waitForTimeout(300);

    // Click close button
    await page.click('button[aria-label="Close chat"]');

    // Chat window should close
    const chatWindow = page.locator('[role="dialog"][aria-label="Chat window"]');
    await expect(chatWindow).not.toBeVisible({ timeout: 1000 });

    // Only floating icon should remain
    const icon = page.locator('button[aria-label="Open chat"]');
    await expect(icon).toBeVisible();
  });

  test('Test 6: Escape key closes chat', async ({ page }) => {
    // Open chat window
    await page.click('button[aria-label="Open chat"]');

    // Wait for chat to open
    await page.waitForTimeout(300);

    // Press Escape key
    await page.keyboard.press('Escape');

    // Chat window should close
    const chatWindow = page.locator('[role="dialog"][aria-label="Chat window"]');
    await expect(chatWindow).not.toBeVisible({ timeout: 1000 });
  });

  test('Test 7: Click outside closes chat', async ({ page }) => {
    // Open chat window
    await page.click('button[aria-label="Open chat"]');

    // Wait for chat to open
    await page.waitForTimeout(300);

    // Click outside chat window (top-left corner)
    await page.click('body', { position: { x: 10, y: 10 } });

    // Chat window should close
    const chatWindow = page.locator('[role="dialog"][aria-label="Chat window"]');
    await expect(chatWindow).not.toBeVisible({ timeout: 1000 });
  });

  test('Test 8: Size constraints respected', async ({ page }) => {
    // Open chat window
    await page.click('button[aria-label="Open chat"]');

    // Wait for chat to open
    await page.waitForTimeout(300);

    // Measure chat window dimensions
    const chatWindow = page.locator('[role="dialog"][aria-label="Chat window"]');
    const box = await chatWindow.boundingBox();

    expect(box).toBeTruthy();

    if (box) {
      // Width ≤ 420px
      expect(box.width).toBeLessThanOrEqual(420);

      // Height ≤ 70vh
      const viewport = page.viewportSize();
      if (viewport) {
        expect(box.height).toBeLessThanOrEqual(viewport.height * 0.7);

        // Bottom margin ≥ 24px (distance from viewport bottom)
        const bottomMargin = viewport.height - (box.y + box.height);
        expect(bottomMargin).toBeGreaterThanOrEqual(20); // Allow small tolerance

        // Right margin ≥ 24px (distance from viewport right)
        const rightMargin = viewport.width - (box.x + box.width);
        expect(rightMargin).toBeGreaterThanOrEqual(20); // Allow small tolerance
      }
    }
  });

  test('Test 9: Mobile viewport behavior', async ({ page }) => {
    // Set viewport to mobile size (iPhone 12)
    await page.setViewportSize({ width: 375, height: 667 });

    // Open chat window
    await page.click('button[aria-label="Open chat"]');

    // Wait for chat to open
    await page.waitForTimeout(300);

    // Measure chat window
    const chatWindow = page.locator('[role="dialog"][aria-label="Chat window"]');
    const box = await chatWindow.boundingBox();

    expect(box).toBeTruthy();

    if (box) {
      // Should be full-screen on mobile (within tolerance)
      expect(box.width).toBeCloseTo(375, 10);
      expect(box.height).toBeCloseTo(667, 10);
    }

    // Close button should still work
    await page.click('button[aria-label="Close chat"]');
    await expect(chatWindow).not.toBeVisible({ timeout: 1000 });
  });

  test('Test 10: No console errors', async ({ page }) => {
    const errors: string[] = [];

    // Attach console error listener
    page.on('console', msg => {
      if (msg.type() === 'error') {
        const text = msg.text();
        // Filter out expected authentication errors (401) - these are backend issues, not UI issues
        if (!text.includes('401') && !text.includes('Unauthorized')) {
          errors.push(text);
        }
      }
    });

    // Open chat window
    await page.click('button[aria-label="Open chat"]');

    // Wait for ChatKit to load
    await page.waitForTimeout(1000);

    // Close chat window
    await page.click('button[aria-label="Close chat"]');

    // Wait a bit more
    await page.waitForTimeout(500);

    // Assert no console errors (excluding auth errors)
    expect(errors).toHaveLength(0);
  });
});
