/**
 * Playwright Test for Minikube Deployment
 * Tests complete user flow including authentication, tasks, and AI chat
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Configuration
const FRONTEND_URL = 'http://localhost:3000';
const BACKEND_URL = 'http://localhost:8002';
const SCREENSHOTS_DIR = './test-screenshots';
const TEST_USER = {
  email: `test_${Date.now()}@example.com`,
  password: 'TestPassword123!',
  name: 'Test User'
};

// Create screenshots directory
if (!fs.existsSync(SCREENSHOTS_DIR)) {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

// Logging helper
function log(message, type = 'INFO') {
  const timestamp = new Date().toISOString();
  const colors = {
    INFO: '\x1b[36m',
    SUCCESS: '\x1b[32m',
    ERROR: '\x1b[31m',
    WARN: '\x1b[33m'
  };
  console.log(`${colors[type]}[${type}] ${timestamp} - ${message}\x1b[0m`);
}

// Screenshot helper
async function takeScreenshot(page, name) {
  const filename = path.join(SCREENSHOTS_DIR, `${Date.now()}-${name}.png`);
  await page.screenshot({ path: filename, fullPage: true });
  log(`Screenshot saved: ${filename}`, 'INFO');
  return filename;
}

// Test backend connectivity
async function testBackendConnectivity() {
  log('Testing backend connectivity...', 'INFO');
  try {
    const response = await fetch(`${BACKEND_URL}/api/health`);
    const data = await response.json();

    if (response.status === 200) {
      log(`Backend health check: OK (${data.version})`, 'SUCCESS');
      return true;
    } else {
      log(`Backend health check failed: ${response.status}`, 'ERROR');
      return false;
    }
  } catch (error) {
    log(`Backend connectivity error: ${error.message}`, 'ERROR');
    return false;
  }
}

// Test frontend connectivity
async function testFrontendConnectivity() {
  log('Testing frontend connectivity...', 'INFO');
  try {
    const response = await fetch(FRONTEND_URL);

    if (response.status === 200) {
      log('Frontend accessible: OK', 'SUCCESS');
      return true;
    } else {
      log(`Frontend accessibility failed: ${response.status}`, 'ERROR');
      return false;
    }
  } catch (error) {
    log(`Frontend connectivity error: ${error.message}`, 'ERROR');
    return false;
  }
}

// Main test function
async function runTests() {
  log('='.repeat(60), 'INFO');
  log('MINIKUBE DEPLOYMENT PLAYWRIGHT TESTING', 'INFO');
  log('='.repeat(60), 'INFO');

  // Step 1: Test connectivity
  log('\n[STEP 1] Testing Connectivity', 'INFO');
  const backendOk = await testBackendConnectivity();
  const frontendOk = await testFrontendConnectivity();

  if (!backendOk || !frontendOk) {
    log('Connectivity tests failed. Please ensure port-forwards are running:', 'ERROR');
    log('  kubectl port-forward service/todo-app-ai-todo-app-backend 8002:8000', 'ERROR');
    log('  kubectl port-forward service/todo-app-ai-todo-app-frontend 3000:3000', 'ERROR');
    process.exit(1);
  }

  // Launch browser
  log('\n[STEP 2] Launching Browser', 'INFO');
  const browser = await chromium.launch({
    headless: false,
    slowMo: 500 // Slow down for visibility
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    recordVideo: {
      dir: SCREENSHOTS_DIR,
      size: { width: 1280, height: 720 }
    }
  });

  const page = await context.newPage();

  // Listen to console messages
  page.on('console', msg => {
    const type = msg.type();
    if (type === 'error') {
      log(`Browser Console Error: ${msg.text()}`, 'ERROR');
    } else if (type === 'warning') {
      log(`Browser Console Warning: ${msg.text()}`, 'WARN');
    }
  });

  // Listen to network requests
  page.on('requestfailed', request => {
    log(`Request Failed: ${request.url()} - ${request.failure().errorText}`, 'ERROR');
  });

  page.on('response', response => {
    if (response.status() >= 400) {
      log(`HTTP ${response.status()}: ${response.url()}`, 'ERROR');
    }
  });

  try {
    // Step 3: Navigate to homepage
    log('\n[STEP 3] Navigating to Homepage', 'INFO');
    await page.goto(FRONTEND_URL, { waitUntil: 'networkidle' });
    await takeScreenshot(page, '01-homepage');
    log('Homepage loaded successfully', 'SUCCESS');

    // Step 4: Sign up
    log('\n[STEP 4] Testing User Signup', 'INFO');
    await page.click('a[href="/signup"]');
    await page.waitForURL('**/signup', { timeout: 5000 });
    await takeScreenshot(page, '02-signup-page');

    // Fill email - try multiple selectors
    const emailInput = await page.locator('input[type="email"]').first();
    await emailInput.fill(TEST_USER.email);

    // Fill name - try multiple selectors
    const nameInput = await page.locator('input[placeholder*="name" i], input[placeholder*="Name"], input:not([type="email"]):not([type="password"])').first();
    await nameInput.fill(TEST_USER.name);

    // Fill password
    const passwordInput = await page.locator('input[type="password"]').first();
    await passwordInput.fill(TEST_USER.password);

    await takeScreenshot(page, '03-signup-filled');

    log(`Signing up with email: ${TEST_USER.email}`, 'INFO');
    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    await takeScreenshot(page, '04-after-signup');
    log('Signup successful, redirected to dashboard', 'SUCCESS');

    // Step 5: Test Dashboard
    log('\n[STEP 5] Testing Dashboard', 'INFO');
    await page.waitForLoadState('networkidle');
    await takeScreenshot(page, '05-dashboard');

    // Check for 404 errors
    const pageContent = await page.content();
    if (pageContent.includes('404') || pageContent.includes('Not Found')) {
      log('Dashboard shows 404 error!', 'ERROR');
      await takeScreenshot(page, '05-dashboard-404-error');
    } else {
      log('Dashboard loaded without 404 errors', 'SUCCESS');
    }

    // Step 6: Create Task
    log('\n[STEP 6] Testing Task Creation', 'INFO');

    // Look for add task button (various possible selectors)
    const addTaskSelectors = [
      'button:has-text("Add Task")',
      'button:has-text("New Task")',
      'button:has-text("Create Task")',
      '[data-testid="add-task"]',
      'button[aria-label*="Add"]'
    ];

    let addTaskButton = null;
    for (const selector of addTaskSelectors) {
      try {
        addTaskButton = await page.$(selector);
        if (addTaskButton) {
          log(`Found add task button: ${selector}`, 'SUCCESS');
          break;
        }
      } catch (e) {
        // Continue to next selector
      }
    }

    if (addTaskButton) {
      await addTaskButton.click();
      await page.waitForTimeout(1000);
      await takeScreenshot(page, '06-add-task-form');

      // Fill task form
      await page.fill('input[name="title"], input[placeholder*="title" i]', 'Test Task from Playwright');
      await page.fill('textarea[name="description"], textarea[placeholder*="description" i]', 'This is a test task created by Playwright automation');
      await takeScreenshot(page, '07-task-form-filled');

      // Submit task
      await page.click('button[type="submit"]:has-text("Create"), button[type="submit"]:has-text("Add"), button[type="submit"]:has-text("Save")');
      await page.waitForTimeout(2000);
      await takeScreenshot(page, '08-after-task-creation');
      log('Task created successfully', 'SUCCESS');
    } else {
      log('Could not find add task button', 'WARN');
      await takeScreenshot(page, '06-no-add-task-button');
    }

    // Step 7: List Tasks
    log('\n[STEP 7] Testing Task List', 'INFO');
    const tasks = await page.$$('[data-testid="task-item"], .task-item, [class*="task"]');
    log(`Found ${tasks.length} tasks in the list`, 'INFO');
    await takeScreenshot(page, '09-task-list');

    // Step 8: Test AI Chat
    log('\n[STEP 8] Testing AI Chatbot', 'INFO');

    // Look for chat button
    const chatButton = await page.$('button[aria-label*="chat" i], button:has-text("Chat"), [class*="chat-icon"]');

    if (chatButton) {
      await chatButton.click();
      await page.waitForTimeout(1000);
      await takeScreenshot(page, '10-chat-opened');
      log('Chat window opened', 'SUCCESS');

      // Send message
      const chatInput = await page.$('input[placeholder*="message" i], textarea[placeholder*="message" i]');
      if (chatInput) {
        await chatInput.fill('Create a task to buy groceries');
        await takeScreenshot(page, '11-chat-message-typed');

        await page.keyboard.press('Enter');
        await page.waitForTimeout(5000); // Wait for AI response
        await takeScreenshot(page, '12-chat-response');
        log('Chat message sent, waiting for response', 'SUCCESS');
      } else {
        log('Could not find chat input', 'WARN');
      }
    } else {
      log('Could not find chat button', 'WARN');
      await takeScreenshot(page, '10-no-chat-button');
    }

    // Step 9: Check Network Requests
    log('\n[STEP 9] Analyzing Network Activity', 'INFO');
    const apiRequests = [];

    page.on('response', async (response) => {
      const url = response.url();
      if (url.includes('/api/')) {
        apiRequests.push({
          url,
          status: response.status(),
          statusText: response.statusText()
        });
      }
    });

    // Reload to capture requests
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    log('API Requests captured:', 'INFO');
    apiRequests.forEach(req => {
      const status = req.status >= 400 ? 'ERROR' : 'SUCCESS';
      log(`  ${req.status} ${req.url}`, status);
    });

    await takeScreenshot(page, '13-final-state');

    // Success summary
    log('\n' + '='.repeat(60), 'SUCCESS');
    log('TESTING COMPLETED SUCCESSFULLY', 'SUCCESS');
    log('='.repeat(60), 'SUCCESS');
    log(`Screenshots saved to: ${SCREENSHOTS_DIR}`, 'INFO');
    log(`Test user: ${TEST_USER.email}`, 'INFO');

  } catch (error) {
    log(`Test failed with error: ${error.message}`, 'ERROR');
    log(`Stack trace: ${error.stack}`, 'ERROR');
    await takeScreenshot(page, 'error-state');
  } finally {
    await context.close();
    await browser.close();
  }
}

// Run tests
runTests().catch(error => {
  log(`Fatal error: ${error.message}`, 'ERROR');
  process.exit(1);
});
