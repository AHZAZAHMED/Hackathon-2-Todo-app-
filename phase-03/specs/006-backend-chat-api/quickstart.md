# Quickstart Guide: Backend Chat API

**Feature**: 006-backend-chat-api
**Date**: 2026-02-08
**Audience**: Developers implementing or testing the chat API

## Overview

This guide walks you through setting up and testing the Backend Chat API with OpenAI Agents SDK and Gemini 2.0 Flash integration.

**What you'll build**:
- POST /api/chat endpoint with JWT authentication
- AI agent using Gemini 2.0 Flash (free LLM)
- MCP tools for task management
- Stateless backend with PostgreSQL persistence

**Time to complete**: ~30 minutes

---

## Prerequisites

### Required Software
- Python 3.11+ installed
- PostgreSQL database (Neon Serverless or local)
- Git (for cloning repository)
- curl or Postman (for testing)

### Required Accounts
- Google AI Studio account (for Gemini API key)
- Better Auth setup (from Phase-2)

### Existing Phase-2 Components
- ✅ FastAPI backend running
- ✅ Better Auth JWT authentication
- ✅ PostgreSQL database with user and tasks tables
- ✅ Frontend with ChatKit UI (004-chatbot-frontend)

---

## Step 1: Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key (starts with `AIza...`)
5. Save it securely (you'll add it to `.env` in Step 3)

**Note**: Gemini 2.0 Flash is free tier with generous rate limits for development.

---

## Step 2: Install Dependencies

Navigate to the backend directory and install new dependencies:

```bash
cd backend

# Install OpenAI Agents SDK and related packages
pip install openai openai-agents tiktoken pydantic

# Verify installation
python -c "import openai; print(openai.__version__)"
python -c "import tiktoken; print('tiktoken installed')"
```

**Expected output**:
```
1.x.x
tiktoken installed
```

---

## Step 3: Configure Environment Variables

Add Gemini API key to your `.env` file:

```bash
# backend/.env

# Existing variables (from Phase-2)
DATABASE_URL=postgresql://user:password@host:5432/dbname
JWT_SECRET=your-jwt-secret-here

# New variables (Phase-3)
GEMINI_API_KEY=AIza...your-gemini-api-key-here
```

**Security Note**: Never commit `.env` to version control. Update `.env.example` with placeholder:

```bash
# backend/.env.example
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
JWT_SECRET=your-jwt-secret-here
GEMINI_API_KEY=your-gemini-api-key-here
```

---

## Step 4: Run Database Migration

Apply migration 003 to create conversations and messages tables:

```bash
# From backend directory
psql $DATABASE_URL -f migrations/003_create_chat_tables.sql
```

**Expected output**:
```
CREATE EXTENSION
CREATE TABLE
CREATE INDEX
CREATE TABLE
CREATE INDEX
CREATE INDEX
CREATE FUNCTION
CREATE TRIGGER
COMMENT
COMMENT
COMMENT
COMMENT
COMMENT
```

**Verify tables created**:
```bash
psql $DATABASE_URL -c "\dt conversations messages"
```

**Expected output**:
```
              List of relations
 Schema |      Name       | Type  |  Owner
--------+-----------------+-------+---------
 public | conversations   | table | user
 public | messages        | table | user
```

---

## Step 5: Verify Database Schema

Check that foreign keys and indexes are properly created:

```bash
# Check conversations table
psql $DATABASE_URL -c "\d conversations"

# Check messages table
psql $DATABASE_URL -c "\d messages"
```

**Expected**: Foreign key constraints on `user_id` and `conversation_id`, indexes on key columns.

---

## Step 6: Start the Backend Server

Start the FastAPI server:

```bash
# From backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify server is running**:
```bash
curl http://localhost:8000/health
```

**Expected**: `{"status": "ok"}`

---

## Step 7: Get JWT Token

You need a valid JWT token to test the chat endpoint. Use one of these methods:

### Method 1: Login via Frontend (Recommended)
1. Open frontend: `http://localhost:3000`
2. Login with existing user credentials
3. Open browser DevTools → Application → Cookies
4. Copy the `better-auth.session_token` value

### Method 2: Login via API
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your-password"
  }'
```

**Expected response**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": { ... }
}
```

Save the token for testing.

---

## Step 8: Test the Chat Endpoint

### Test 1: Send First Message (New Conversation)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "message": "Hello! Can you help me manage my tasks?"
  }'
```

**Expected response**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "Hello! I'm your task management assistant. I can help you add, list, update, complete, and delete tasks. What would you like to do?",
  "tool_calls": []
}
```

**What happened**:
1. Backend verified JWT and extracted user_id
2. Backend auto-created new conversation
3. Backend stored user message in database
4. AI agent generated response (no tools needed)
5. Backend stored assistant response in database
6. Backend returned response with conversation_id

### Test 2: Add a Task (Tool Invocation)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "message": "Add a task to buy milk",
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Expected response**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "I've added a task to buy milk to your todo list.",
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": {
        "title": "Buy milk",
        "description": ""
      },
      "result": {
        "id": 123,
        "title": "Buy milk",
        "description": "",
        "completed": false,
        "created_at": "2026-02-08T10:30:00Z",
        "updated_at": "2026-02-08T10:30:00Z"
      }
    }
  ]
}
```

**What happened**:
1. Backend loaded conversation history (previous message)
2. Backend stored user message
3. AI agent analyzed intent → decided to invoke add_task tool
4. MCP tool executed database INSERT
5. Agent received tool result and formulated response
6. Backend stored assistant response
7. Backend returned response with tool_calls array

### Test 3: List Tasks

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "message": "Show me my tasks",
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Expected**: Response with list_tasks tool invocation and task list.

### Test 4: Complete Task

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "message": "Mark the milk task as done",
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Expected**: Response with complete_task tool invocation.

---

## Step 9: Verify Database Persistence

Check that conversations and messages are stored in database:

```bash
# Check conversations
psql $DATABASE_URL -c "SELECT id, user_id, created_at FROM conversations;"

# Check messages
psql $DATABASE_URL -c "SELECT conversation_id, role, LEFT(content, 50) as content FROM messages ORDER BY created_at;"
```

**Expected**: You should see your conversation and all messages (user and assistant) stored in the database.

---

## Step 10: Test Stateless Backend

Verify that conversation persists after server restart:

1. **Stop the server**: Press CTRL+C in the terminal running uvicorn
2. **Restart the server**: Run `uvicorn app.main:app --reload` again
3. **Send another message** with the same conversation_id:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "message": "What tasks do I have?",
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Expected**: Agent should have access to full conversation history (loaded from database) and respond contextually.

**This proves**: Backend is stateless - all state persists in database.

---

## Troubleshooting

### Error: "Authentication failed"
- **Cause**: JWT token is invalid or expired
- **Fix**: Get a new JWT token (Step 7)

### Error: "AI service temporarily unavailable"
- **Cause**: Gemini API key is invalid or rate limit exceeded
- **Fix**: Verify GEMINI_API_KEY in .env, check Google AI Studio dashboard

### Error: "Unable to complete task operation"
- **Cause**: MCP tool failed (database error)
- **Fix**: Check database connection, verify migrations applied

### Error: "Request took too long to process"
- **Cause**: Request exceeded 5 second timeout
- **Fix**: Check Gemini API response time, verify network connectivity

### Database Connection Error
- **Cause**: DATABASE_URL is incorrect or database is down
- **Fix**: Verify DATABASE_URL in .env, check database is running

### Import Error: "No module named 'openai'"
- **Cause**: Dependencies not installed
- **Fix**: Run `pip install openai openai-agents tiktoken`

---

## Testing with Frontend

Once the backend is working, test with the ChatKit frontend:

1. Open frontend: `http://localhost:3000`
2. Login with your credentials
3. Navigate to chat page: `http://localhost:3000/chat`
4. Send messages in the chat UI
5. Verify responses appear correctly
6. Verify tool invocations work (add task, list tasks, etc.)

---

## Next Steps

### Development
- [ ] Implement all 5 MCP tools (add, list, complete, delete, update)
- [ ] Add comprehensive error handling
- [ ] Write integration tests
- [ ] Add logging and monitoring

### Testing
- [ ] Test all MCP tool invocations
- [ ] Test error paths (invalid JWT, tool failures)
- [ ] Test concurrent requests (50+ simultaneous)
- [ ] Test conversation history with 100+ messages

### Deployment
- [ ] Configure production environment variables
- [ ] Set up database connection pooling
- [ ] Configure CORS for production frontend
- [ ] Set up logging and monitoring
- [ ] Deploy to production server

---

## Useful Commands

### Database
```bash
# Connect to database
psql $DATABASE_URL

# List all tables
\dt

# Describe table schema
\d conversations
\d messages

# Count conversations
SELECT COUNT(*) FROM conversations;

# Count messages
SELECT COUNT(*) FROM messages;

# View recent messages
SELECT * FROM messages ORDER BY created_at DESC LIMIT 10;
```

### Backend
```bash
# Start server
uvicorn app.main:app --reload

# Start server with custom port
uvicorn app.main:app --reload --port 8080

# Run tests
pytest

# Run specific test
pytest tests/test_chat_endpoint.py

# Check Python version
python --version
```

### API Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test chat endpoint (replace JWT_TOKEN)
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

---

## Resources

- [OpenAI Agents SDK Documentation](https://github.com/openai/openai-agents-python)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Better Auth Documentation](https://www.better-auth.com/)

---

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review server logs for error messages
3. Verify all prerequisites are met
4. Check that Phase-2 components are working

**Quickstart Status**: ✅ COMPLETE
**Ready for**: Implementation
