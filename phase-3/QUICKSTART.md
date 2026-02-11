# Quick Start Guide - Phase-3 Chat Implementation

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ installed
- Python 3.11+ installed
- PostgreSQL database (Neon) configured
- Environment variables set up

---

## 📦 Installation

### Frontend Setup
```bash
cd frontend
npm install
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### Frontend Environment Variables
File: `frontend/.env.local`

```bash
# Better Auth Configuration
BETTER_AUTH_SECRET=your-secret-here
BETTER_AUTH_URL=https://your-frontend-url.vercel.app

# Database URL (for Better Auth)
DATABASE_URL=postgresql://user:password@host:port/database

# API Configuration (Backend URL)
NEXT_PUBLIC_API_URL=https://your-backend-url.vercel.app/api
NEXT_PUBLIC_API_BASE_URL=https://your-backend-url.vercel.app

# OpenAI ChatKit Configuration
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your_openai_domain_key_here

# Application Configuration
NEXT_PUBLIC_APP_NAME=Todo App
NEXT_PUBLIC_APP_URL=https://your-frontend-url.vercel.app
```

### Backend Environment Variables
File: `backend/.env`

```bash
# JWT Verification (MUST match frontend)
BETTER_AUTH_SECRET=your-secret-here

# Database Connection
DATABASE_URL=postgresql://user:password@host:port/database

# CORS Configuration
FRONTEND_URL=http://localhost:3000

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

---

## 🏃 Running the Application

### Option 1: Development Mode (Recommended for Testing)

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Production Build

**Frontend:**
```bash
cd frontend
npm run build
npm start
```

**Backend:**
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 🧪 Testing the Chat Feature

### Step-by-Step Test Flow

1. **Start Both Servers**
   - Backend running on port 8000
   - Frontend running on port 3000

2. **Open Application**
   - Navigate to http://localhost:3000
   - You should see the todo application

3. **Log In**
   - Click "Login" or navigate to login page
   - Enter your credentials
   - Successful login redirects to dashboard

4. **Find Chat Icon**
   - Look for blue circular icon in bottom-right corner
   - Icon should be visible on all pages

5. **Open Chat Window**
   - Click the chat icon
   - Chat window opens above the icon
   - Window dimensions: 400px × 600px
   - Header shows "AI Assistant"

6. **Send a Message**
   - Type a message in the input field
   - Watch character counter (500 max)
   - Press Enter or click "Send" button
   - Loading indicator appears (animated dots)
   - Mock AI response appears

7. **Test State Persistence**
   - Navigate to different pages (dashboard, settings, etc.)
   - Chat window state persists (open/closed)
   - Messages remain visible

8. **Test Error Handling**
   - Stop backend server
   - Try sending a message
   - Error message appears
   - Retry button shows
   - Restart backend and click retry

9. **Test Mobile Responsive**
   - Resize browser window to mobile size
   - Chat adapts to smaller screen
   - Still usable and functional

---

## 🔍 Verification Checklist

### Frontend Verification
- [ ] Chat icon visible on all pages
- [ ] Icon positioned bottom-right (20px from edges)
- [ ] Click icon opens chat window
- [ ] Chat window has proper dimensions (400px × 600px)
- [ ] Close button works
- [ ] Message input accepts text
- [ ] Character counter updates in real-time
- [ ] Send button disabled when empty or > 500 chars
- [ ] Loading indicator shows while waiting
- [ ] Messages display with correct styling (user=blue, assistant=gray)
- [ ] Auto-scroll to latest message
- [ ] State persists across page navigation
- [ ] Mobile responsive design works

### Backend Verification
- [ ] Backend starts without errors
- [ ] Chat endpoint registered at `/api/chat`
- [ ] Health check returns 200: http://localhost:8000/api/health
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Unauthenticated requests return 401
- [ ] Empty messages return 422
- [ ] Messages > 500 chars return 422
- [ ] Valid requests return mock response

### Integration Verification
- [ ] Frontend can reach backend
- [ ] JWT token attached to requests
- [ ] Backend verifies JWT correctly
- [ ] Messages sent successfully
- [ ] Responses displayed correctly
- [ ] Error handling works end-to-end

---

## 🐛 Troubleshooting

### Issue: Chat icon not visible
**Solution:**
- Check if ChatProvider is wrapped around app in `layout.tsx`
- Verify z-index values in `tailwind.config.js`
- Check browser console for errors

### Issue: "Cannot connect to backend"
**Solution:**
- Verify backend is running on port 8000
- Check `NEXT_PUBLIC_API_BASE_URL` in `.env.local`
- Verify CORS settings in backend `main.py`
- Check network tab in browser dev tools

### Issue: "Unauthorized" error
**Solution:**
- Verify you're logged in
- Check JWT token in browser dev tools (Application → Cookies)
- Verify `BETTER_AUTH_SECRET` matches between frontend and backend
- Check backend logs for JWT verification errors

### Issue: Messages not sending
**Solution:**
- Check backend logs for errors
- Verify database connection
- Check network tab for failed requests
- Verify message length (1-500 characters)

### Issue: State not persisting
**Solution:**
- Check browser console for session storage errors
- Verify session storage is enabled in browser
- Check if running in incognito mode (session storage behaves differently)

### Issue: TypeScript errors
**Solution:**
```bash
cd frontend
npx tsc --noEmit
```
- Fix any type errors shown
- Verify all imports are correct

### Issue: Backend import errors
**Solution:**
```bash
cd backend
python -c "from app.main import app; print('Success')"
```
- Install missing dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.11+)

---

## 📊 API Endpoints

### Chat Endpoint
**POST** `/api/chat`

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Hello AI assistant!"
}
```

**Success Response (200):**
```json
{
  "response": "Hello! I'm your AI assistant. I received your message..."
}
```

**Error Responses:**

**401 Unauthorized:**
```json
{
  "detail": "Could not validate credentials"
}
```

**422 Validation Error:**
```json
{
  "detail": {
    "error": "Validation Error",
    "message": "Message cannot be empty"
  }
}
```

**500 Internal Server Error:**
```json
{
  "detail": {
    "error": "Internal Server Error",
    "message": "An unexpected error occurred"
  }
}
```

---

## 🎯 Current Capabilities

### What Works Now
✅ Complete chat UI with all features
✅ JWT authentication integration
✅ Message sending and receiving
✅ State persistence across navigation
✅ Error handling with retry
✅ Loading states
✅ Mobile responsive design
✅ Character limit validation
✅ Real-time character counter
✅ Auto-scroll to latest message
✅ User/assistant visual distinction

### What's Mock/Placeholder
⚠️ AI responses (currently mock text)
⚠️ Conversation history (not persisted in database)
⚠️ Multi-turn context (each message independent)

### What's Not Yet Implemented
❌ OpenAI Agents SDK integration
❌ MCP server with task tools
❌ Database schema for conversations/messages
❌ Conversation history persistence
❌ Playwright test suite

---

## 🔮 Next Steps

### For Full AI Integration
1. Implement database schema (conversations, messages tables)
2. Install and configure OpenAI Agents SDK
3. Implement MCP server with task tools
4. Update chat endpoint to use real AI
5. Add conversation history loading
6. Implement multi-turn context

### For Testing
1. Create Playwright test files (Phase 8)
2. Run automated test suite
3. Verify all success criteria
4. Run regression tests

### For Production
1. Update environment variables with production values
2. Deploy frontend to Vercel
3. Deploy backend to production server
4. Configure production database
5. Set up monitoring and logging
6. Enable rate limiting
7. Add analytics

---

## 📚 Documentation References

- **Specification**: `specs/001-chatkit-frontend/spec.md`
- **Implementation Plan**: `specs/001-chatkit-frontend/plan.md`
- **Task Breakdown**: `specs/001-chatkit-frontend/tasks.md`
- **API Contract**: `specs/001-chatkit-frontend/contracts/chat-api.md`
- **Quick Start**: `specs/001-chatkit-frontend/quickstart.md`
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`

---

## 💡 Tips

- Use browser dev tools to inspect network requests
- Check backend logs for detailed error messages
- Use `/api/health` endpoint to verify backend is running
- Use Swagger UI at `/docs` to test API endpoints manually
- Session storage can be inspected in browser dev tools (Application → Session Storage)

---

## ✅ Success!

If you can:
1. See the chat icon
2. Open the chat window
3. Send a message
4. Receive a response
5. Navigate pages with state persisting

**Then the implementation is working correctly!** 🎉

The foundation is complete and ready for AI integration.
