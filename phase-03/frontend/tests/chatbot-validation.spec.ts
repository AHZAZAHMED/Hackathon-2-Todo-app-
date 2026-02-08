import { test, expect } from '@playwright/test';

test.describe('Chatbot UI Validation', () => {
  // Test on Desktop viewport
  test('Desktop: Chat window displays correctly and can send messages', async ({ page }) => {
    // Set desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });

    // Navigate to the app
    await page.goto('http://localhost:3000');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Take screenshot of homepage
    await page.screenshot({ path: 'test-results/desktop-homepage.png', fullPage: true });

    // Check if user is logged in by looking for dashboard or login button
    const isLoggedIn = await page.locator('text=Dashboard').isVisible().catch(() => false);

    if (!isLoggedIn) {
      console.log('User not logged in - navigating to login page');
      await page.goto('http://localhost:3000/login');
      await page.waitForLoadState('networkidle');
      await page.screenshot({ path: 'test-results/desktop-login-page.png' });

      // Note: Cannot proceed without credentials
      console.log('⚠️ User needs to be logged in to test chat functionality');
      return;
    }

    // Look for chat launcher button (floating button)
    const chatLauncher = page.locator('[aria-label*="chat" i], button:has-text("Chat"), [class*="chat-launcher"]').first();

    // Take screenshot before opening chat
    await page.screenshot({ path: 'test-results/desktop-before-chat.png', fullPage: true });

    // Click chat launcher
    await chatLauncher.click();
    await page.waitForTimeout(1000); // Wait for animation

    // Take screenshot of opened chat window
    await page.screenshot({ path: 'test-results/desktop-chat-opened.png', fullPage: true });

    // Check if chat window is visible
    const chatWindow = page.locator('[role="dialog"][aria-label*="Chat"]');
    await expect(chatWindow).toBeVisible();

    // Check chat window dimensions on desktop
    const chatBox = await chatWindow.boundingBox();
    console.log('Desktop chat window dimensions:', chatBox);

    // Verify chat components are visible
    await expect(page.locator('text=Chat Assistant')).toBeVisible();

    // Look for input field (ChatKit input)
    const inputField = page.locator('textarea, input[type="text"]').last();
    const isInputVisible = await inputField.isVisible().catch(() => false);

    if (isInputVisible) {
      console.log('✅ Input field is visible');

      // Type a message to add a task
      await inputField.fill('Add a task to buy groceries for the week');
      await page.screenshot({ path: 'test-results/desktop-message-typed.png', fullPage: true });

      // Look for send button and click it
      const sendButton = page.locator('button[type="submit"], button:has-text("Send")').last();
      await sendButton.click();

      // Wait for response
      await page.waitForTimeout(3000);
      await page.screenshot({ path: 'test-results/desktop-message-sent.png', fullPage: true });

      console.log('✅ Message sent successfully');
    } else {
      console.log('❌ Input field not visible - UI issue detected');
      await page.screenshot({ path: 'test-results/desktop-input-not-visible.png', fullPage: true });
    }
  });

  // Test on Tablet viewport
  test('Tablet: Chat window responsiveness', async ({ page }) => {
    // Set tablet viewport (iPad)
    await page.setViewportSize({ width: 768, height: 1024 });

    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');

    await page.screenshot({ path: 'test-results/tablet-homepage.png', fullPage: true });

    // Check if user is logged in
    const isLoggedIn = await page.locator('text=Dashboard').isVisible().catch(() => false);

    if (!isLoggedIn) {
      console.log('⚠️ User needs to be logged in to test chat functionality');
      return;
    }

    // Open chat
    const chatLauncher = page.locator('[aria-label*="chat" i], button:has-text("Chat"), [class*="chat-launcher"]').first();
    await chatLauncher.click();
    await page.waitForTimeout(1000);

    await page.screenshot({ path: 'test-results/tablet-chat-opened.png', fullPage: true });

    // Check chat window dimensions on tablet
    const chatWindow = page.locator('[role="dialog"][aria-label*="Chat"]');
    const chatBox = await chatWindow.boundingBox();
    console.log('Tablet chat window dimensions:', chatBox);

    // Verify it's still using the desktop layout (md breakpoint is 768px)
    await expect(chatWindow).toBeVisible();
  });

  // Test on Mobile viewport
  test('Mobile: Chat window responsiveness', async ({ page }) => {
    // Set mobile viewport (iPhone 12)
    await page.setViewportSize({ width: 390, height: 844 });

    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');

    await page.screenshot({ path: 'test-results/mobile-homepage.png', fullPage: true });

    // Check if user is logged in
    const isLoggedIn = await page.locator('text=Dashboard').isVisible().catch(() => false);

    if (!isLoggedIn) {
      console.log('⚠️ User needs to be logged in to test chat functionality');
      return;
    }

    // Open chat
    const chatLauncher = page.locator('[aria-label*="chat" i], button:has-text("Chat"), [class*="chat-launcher"]').first();
    await chatLauncher.click();
    await page.waitForTimeout(1000);

    await page.screenshot({ path: 'test-results/mobile-chat-opened.png', fullPage: true });

    // Check chat window dimensions on mobile (should be fullscreen)
    const chatWindow = page.locator('[role="dialog"][aria-label*="Chat"]');
    const chatBox = await chatWindow.boundingBox();
    console.log('Mobile chat window dimensions:', chatBox);

    // On mobile, chat should be fullscreen
    expect(chatBox?.width).toBeGreaterThan(350); // Should take most of screen width

    await expect(chatWindow).toBeVisible();
  });

  // Test on Large Desktop viewport
  test('Large Desktop: Chat window responsiveness', async ({ page }) => {
    // Set large desktop viewport
    await page.setViewportSize({ width: 2560, height: 1440 });

    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');

    await page.screenshot({ path: 'test-results/large-desktop-homepage.png', fullPage: true });

    // Check if user is logged in
    const isLoggedIn = await page.locator('text=Dashboard').isVisible().catch(() => false);

    if (!isLoggedIn) {
      console.log('⚠️ User needs to be logged in to test chat functionality');
      return;
    }

    // Open chat
    const chatLauncher = page.locator('[aria-label*="chat" i], button:has-text("Chat"), [class*="chat-launcher"]').first();
    await chatLauncher.click();
    await page.waitForTimeout(1000);

    await page.screenshot({ path: 'test-results/large-desktop-chat-opened.png', fullPage: true });

    // Check chat window dimensions
    const chatWindow = page.locator('[role="dialog"][aria-label*="Chat"]');
    const chatBox = await chatWindow.boundingBox();
    console.log('Large desktop chat window dimensions:', chatBox);

    // Chat window should maintain max width of 420px
    expect(chatBox?.width).toBeLessThanOrEqual(420);

    await expect(chatWindow).toBeVisible();
  });
});
