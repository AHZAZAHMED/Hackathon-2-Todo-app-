# Testing Guide - Phase-3 Chat Implementation

## 🧪 Comprehensive Testing Checklist

Follow this guide to thoroughly test the chat implementation.

---

## Pre-Test Setup

### 1. Verify Environment Variables

**Frontend** (`frontend/.env.local`):
```bash
# Check these are set:
NEXT_PUBLIC_API_BASE_URL=<your-backend-url>
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=<your-key>
```

**Backend** (`backend/.env`):
```bash
# Check these are set:
BETTER_AUTH_SECRET=<your-secret>
DATABASE_URL=<your-database-url>
FRONTEND_URL=<your-frontend-url>
```

### 2. Start Servers

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
[INFO] Hackathon Phase-3 API starting...
[INFO] CORS enabled for: http://localhost:3000
[INFO] Task CRUD endpoints registered at /api/tasks
[INFO] Chat endpoint registered at /api/chat
[SUCCESS] Application ready
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Expected Output:**
```
  ▲ Next.js 16.x.x
  - Local:        http://localhost:3000
  - Environments: .env.local, .env

✓ Starting...
✓ Ready in 2.5s
```

---

## Test Suite

### Test 1: Backend Health Check ✅

**Action:**
Open browser and navigate to: http://localhost:8000/api/health

**Expected Result:**
```json
{
  "status": "healthy",
  "service": "todo-api-with-ai-chat",
  "version": "2.0.0"
}
```

**Status:** [ ] PASS [ ] FAIL

---

### Test 2: Frontend Loads ✅

**Action:**
Navigate to: http://localhost:3000

**Expected Result:**
- Page loads without errors
- No console errors in browser dev tools (F12)
- Todo application UI visible

**Status:** [ ] PASS [ ] FAIL

---

### Test 3: Chat Icon Visibility ✅

**Action:**
Look at the bottom-right corner of the page

**Expected Result:**
- Blue circular chat icon visible
- Icon positioned 20px from bottom and right edges
- Icon has hover effect (darker blue on hover)

**Status:** [ ] PASS [ ] FAIL

---

### Test 4: Authentication Check ✅

**Action:**
If not logged in, click the chat icon

**Expected Result:**
- Redirected to login page
- URL includes `?returnUrl=` parameter

**Action (if logged in):**
Log out, then click chat icon

**Expected Result:**
- Redirected to login page
- Current page URL preserved in returnUrl

**Status:** [ ] PASS [ ] FAIL

---

### Test 5: Login and Return ✅

**Action:**
1. Log in with valid credentials
2. Should return to original page
3. Chat icon should still be visible

**Expected Result:**
- Successful login
- Returned to original page
- Chat icon visible

**Status:** [ ] PASS [ ] FAIL

---

### Test 6: Open Chat Window ✅

**Action:**
Click the chat icon

**Expected Result:**
- Chat window opens above the icon
- Window dimensions: approximately 400px wide × 600px tall
- Window has header "AI Assistant"
- Window has close button (X)
- Icon changes to X icon
- Empty state message: "No messages yet"

**Status:** [ ] PASS [ ] FAIL

---

### Test 7: Close Chat Window ✅

**Action:**
Click the close button (X) in chat header OR click the icon again

**Expected Result:**
- Chat window closes
- Icon remains visible
- Icon changes back to chat icon

**Status:** [ ] PASS [ ] FAIL

---

### Test 8: Send Message - Valid ✅

**Action:**
1. Open chat window
2. Type: "Hello AI assistant!"
3. Press Enter or click Send button

**Expected Result:**
- Message appears in chat with blue background (user message)
- Loading indicator appears (three animated dots)
- After ~1 second, assistant response appears with gray background
- Response includes your name and echoes your message
- Auto-scrolls to show latest message

**Status:** [ ] PASS [ ] FAIL

---

### Test 9: Character Counter ✅

**Action:**
1. Open chat window
2. Start typing in the input field
3. Watch the character counter

**Expected Result:**
- Counter shows "500 characters remaining" initially
- Counter updates in real-time as you type
- Counter turns orange when < 50 characters remaining
- Counter turns red when limit exceeded
- Send button disabled when > 500 characters

**Status:** [ ] PASS [ ] FAIL

---

### Test 10: Empty Message Validation ✅

**Action:**
1. Open chat window
2. Try to send empty message (just spaces)

**Expected Result:**
- Send button should be disabled
- Cannot send empty message

**Status:** [ ] PASS [ ] FAIL

---

### Test 11: Message Over Limit ✅

**Action:**
1. Open chat window
2. Type or paste 501+ characters
3. Try to send

**Expected Result:**
- Character counter shows negative number in red
- Send button disabled
- Cannot send message

**Status:** [ ] PASS [ ] FAIL

---

### Test 12: Multiple Messages ✅

**Action:**
1. Send message: "First message"
2. Wait for response
3. Send message: "Second message"
4. Wait for response
5. Send message: "Third message"

**Expected Result:**
- All messages appear in chronological order
- User messages on right (blue)
- Assistant messages on left (gray)
- Auto-scrolls to show latest message
- All messages remain visible

**Status:** [ ] PASS [ ] FAIL

---

### Test 13: State Persistence - Navigation ✅

**Action:**
1. Open chat window
2. Send a message
3. Navigate to different page (e.g., dashboard → settings)
4. Check chat window

**Expected Result:**
- Chat window remains open
- Messages still visible
- Can continue conversation

**Action:**
1. Close chat window
2. Navigate to different page
3. Check chat icon

**Expected Result:**
- Chat window remains closed
- Icon still visible

**Status:** [ ] PASS [ ] FAIL

---

### Test 14: State Persistence - Page Reload ✅

**Action:**
1. Open chat window
2. Send a message
3. Refresh page (F5)

**Expected Result:**
- Chat window state restored (open/closed)
- Messages restored from session storage
- Can continue conversation

**Status:** [ ] PASS [ ] FAIL

---

### Test 15: Error Handling - Backend Down ✅

**Action:**
1. Stop backend server (Ctrl+C in backend terminal)
2. Try to send a message in chat

**Expected Result:**
- Error message appears: "Unable to send message. Please try again."
- Message marked as failed (red border)
- Retry button appears

**Action:**
1. Restart backend server
2. Click retry button

**Expected Result:**
- Message resends successfully
- Response received

**Status:** [ ] PASS [ ] FAIL

---

### Test 16: Error Handling - Network Error ✅

**Action:**
1. Open browser dev tools (F12)
2. Go to Network tab
3. Set throttling to "Offline"
4. Try to send a message

**Expected Result:**
- Error message: "No internet connection. Please check your network."
- Message marked as failed
- Retry button appears

**Action:**
1. Set throttling back to "No throttling"
2. Click retry button

**Expected Result:**
- Message resends successfully

**Status:** [ ] PASS [ ] FAIL

---

### Test 17: Mobile Responsive ✅

**Action:**
1. Open browser dev tools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select mobile device (e.g., iPhone 12)
4. Test chat functionality

**Expected Result:**
- Chat icon visible and clickable
- Chat window adapts to screen size
- Window doesn't overflow screen
- All features still work
- Text readable
- Buttons clickable

**Status:** [ ] PASS [ ] FAIL

---

### Test 18: Z-Index Hierarchy ✅

**Action:**
1. Open chat window
2. Check if chat appears above all page content
3. Try scrolling page

**Expected Result:**
- Chat window stays fixed in position
- Chat appears above all page elements
- Icon always visible
- Window doesn't get covered by page content

**Status:** [ ] PASS [ ] FAIL

---

### Test 19: JWT Verification ✅

**Action:**
1. Open browser dev tools (F12)
2. Go to Network tab
3. Send a chat message
4. Find the POST request to `/api/chat`
5. Check request headers

**Expected Result:**
- Request has `Authorization: Bearer <token>` header
- Token is present and not empty
- Backend accepts the request (200 response)

**Status:** [ ] PASS [ ] FAIL

---

### Test 20: Backend Validation ✅

**Action:**
Open: http://localhost:8000/docs

**Expected Result:**
- Swagger UI loads
- `/api/chat` endpoint visible
- Can see request/response schemas
- Shows authentication required (lock icon)

**Action:**
Try the endpoint in Swagger UI without authentication

**Expected Result:**
- Returns 401 Unauthorized

**Status:** [ ] PASS [ ] FAIL

---

## Test Results Summary

**Total Tests:** 20
**Passed:** ___
**Failed:** ___
**Success Rate:** ___%

---

## Common Issues and Solutions

### Issue: Chat icon not visible
**Check:**
- [ ] Frontend server running
- [ ] No console errors
- [ ] ChatProvider in layout.tsx
- [ ] Z-index values in tailwind.config.js

### Issue: Cannot send messages
**Check:**
- [ ] Backend server running
- [ ] CORS configured correctly
- [ ] JWT token present
- [ ] Network tab shows request

### Issue: "Unauthorized" error
**Check:**
- [ ] Logged in successfully
- [ ] JWT token in cookies/storage
- [ ] BETTER_AUTH_SECRET matches
- [ ] Backend logs for errors

### Issue: State not persisting
**Check:**
- [ ] Session storage enabled
- [ ] Not in incognito mode
- [ ] No console errors
- [ ] Browser supports session storage

---

## Performance Checks

### Load Time
- [ ] Chat icon appears < 1 second after page load
- [ ] Chat window opens < 1 second after click
- [ ] Messages send < 5 seconds (with backend)

### Memory
- [ ] No memory leaks (check dev tools Memory tab)
- [ ] No excessive re-renders
- [ ] Smooth animations

### Network
- [ ] Minimal API calls
- [ ] Proper error handling
- [ ] No unnecessary requests

---

## Browser Compatibility

Test on multiple browsers:
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if available)

---

## Final Validation

If all tests pass:
✅ **Implementation is working correctly!**

The chat interface is fully functional and ready for AI integration.

---

## Next Steps After Testing

1. Document any issues found
2. Fix any failing tests
3. Consider creating Playwright automated tests
4. Prepare for AI integration (OpenAI + MCP)

---

**Testing Date:** _____________
**Tested By:** _____________
**Environment:** Development / Staging / Production
**Overall Status:** PASS / FAIL / PARTIAL
