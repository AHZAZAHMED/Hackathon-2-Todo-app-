# Validation Checklist - Backend Chat API

**Feature**: 006-backend-chat-api
**Status**: Implementation Complete - Awaiting Manual Validation
**Date**: 2026-02-08

## Overview

All code implementation for Phase-3 Backend Chat API is complete. This checklist covers the manual validation steps required to verify the implementation works correctly.

---

## Prerequisites

Before starting validation:
- [ ] Backend server can start without errors
- [ ] Database migrations 001, 002, 003 applied successfully
- [ ] `.env` file configured with all required variables
- [ ] Frontend is running (for end-to-end testing)
- [ ] Valid JWT token available for testing

---

## T059: Quickstart Validation

Follow all 10 steps in `specs/006-backend-chat-api/quickstart.md`:

### Step 1: Get Gemini API Key
- [ ] Obtained API key from Google AI Studio
- [ ] API key starts with `AIza...`
- [ ] API key saved securely

### Step 2: Install Dependencies
- [ ] Ran `pip install openai tiktoken pydantic`
- [ ] Verified installation with test imports
- [ ] No import errors

### Step 3: Configure Environment Variables
- [ ] Added `GEMINI_API_KEY` to `.env`
- [ ] Verified all environment variables present
- [ ] `.env.example` updated with placeholders

### Step 4: Run Database Migration
- [ ] Ran `psql $DATABASE_URL -f migrations/003_create_chat_tables.sql`
- [ ] Migration completed without errors
- [ ] Saw expected output (CREATE TABLE, CREATE INDEX, etc.)

### Step 5: Verify Database Schema
- [ ] Ran `\dt conversations messages` - tables exist
- [ ] Ran `\d conversations` - schema correct
- [ ] Ran `\d messages` - schema correct
- [ ] Foreign keys present
- [ ] Indexes created

### Step 6: Start Backend Server
- [ ] Ran `uvicorn app.main:app --reload`
- [ ] Server started without errors
- [ ] Saw startup messages in console
- [ ] Health endpoint responds: `curl http://localhost:8000/api/health`

### Step 7: Get JWT Token
- [ ] Logged in via frontend or API
- [ ] Obtained valid JWT token
- [ ] Token saved for testing

### Step 8: Test Chat Endpoint

#### Test 1: First Message (New Conversation)
- [ ] Sent POST to `/api/chat` with message
- [ ] Received 200 response
- [ ] Response includes `conversation_id`
- [ ] Response includes `response` text
- [ ] Response includes `tool_calls` array (empty for greeting)

#### Test 2: Add Task (Tool Invocation)
- [ ] Sent message: "Add a task to buy milk"
- [ ] Received 200 response
- [ ] `tool_calls` array contains `add_task` invocation
- [ ] Tool result shows created task with ID
- [ ] Verified task exists in database

#### Test 3: List Tasks
- [ ] Sent message: "Show me my tasks"
- [ ] Received 200 response
- [ ] `tool_calls` array contains `list_tasks` invocation
- [ ] Tool result shows task list

#### Test 4: Complete Task
- [ ] Sent message: "Mark the milk task as done"
- [ ] Received 200 response
- [ ] `tool_calls` array contains `complete_task` invocation
- [ ] Verified task marked complete in database

### Step 9: Verify Database Persistence
- [ ] Ran `SELECT * FROM conversations` - conversation exists
- [ ] Ran `SELECT * FROM messages` - all messages stored
- [ ] User messages have role='user'
- [ ] Assistant messages have role='assistant'
- [ ] Timestamps are correct

### Step 10: Test Stateless Backend
- [ ] Stopped server (CTRL+C)
- [ ] Restarted server
- [ ] Sent new message with same conversation_id
- [ ] Agent has access to conversation history
- [ ] Response is contextually aware

---

## T062: Phase-2 CRUD Endpoints Regression Testing

Verify Phase-2 task CRUD endpoints still work:

### List Tasks
```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer JWT_TOKEN"
```
- [ ] Returns 200 OK
- [ ] Returns task list
- [ ] User isolation enforced

### Create Task
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "Test"}'
```
- [ ] Returns 201 Created
- [ ] Task created in database
- [ ] Task belongs to authenticated user

### Get Task
```bash
curl -X GET http://localhost:8000/api/tasks/{task_id} \
  -H "Authorization: Bearer JWT_TOKEN"
```
- [ ] Returns 200 OK
- [ ] Returns correct task
- [ ] Returns 404 for other user's tasks

### Update Task
```bash
curl -X PUT http://localhost:8000/api/tasks/{task_id} \
  -H "Authorization: Bearer JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated", "description": "Updated"}'
```
- [ ] Returns 200 OK
- [ ] Task updated in database
- [ ] Returns 404 for other user's tasks

### Toggle Task Completion
```bash
curl -X PATCH http://localhost:8000/api/tasks/{task_id}/complete \
  -H "Authorization: Bearer JWT_TOKEN"
```
- [ ] Returns 200 OK
- [ ] Task completion toggled
- [ ] Returns 404 for other user's tasks

### Delete Task
```bash
curl -X DELETE http://localhost:8000/api/tasks/{task_id} \
  -H "Authorization: Bearer JWT_TOKEN"
```
- [ ] Returns 204 No Content
- [ ] Task deleted from database
- [ ] Returns 404 for other user's tasks

---

## T064: Performance Testing

Test with 50 concurrent requests to verify no degradation:

### Setup
```bash
# Install Apache Bench (if not installed)
# Ubuntu/Debian: apt-get install apache2-utils
# macOS: brew install httpd (includes ab)
```

### Test 1: Health Endpoint (Baseline)
```bash
ab -n 100 -c 50 http://localhost:8000/api/health
```
- [ ] All requests successful (200 OK)
- [ ] No failed requests
- [ ] Average response time < 100ms
- [ ] No server errors in logs

### Test 2: Task List Endpoint
```bash
# Create file with JWT token: token.txt
# Content: Authorization: Bearer YOUR_JWT_TOKEN

ab -n 100 -c 50 -H @token.txt http://localhost:8000/api/tasks
```
- [ ] All requests successful (200 OK)
- [ ] No failed requests
- [ ] Average response time < 500ms
- [ ] No database connection errors

### Test 3: Chat Endpoint (Light Load)
```bash
# Create POST data file: chat.json
# Content: {"message": "Hello"}

ab -n 50 -c 10 -p chat.json -T application/json -H @token.txt http://localhost:8000/api/chat
```
- [ ] All requests successful (200 OK)
- [ ] No failed requests
- [ ] Average response time < 5000ms (timeout limit)
- [ ] No Gemini API rate limit errors
- [ ] No database connection pool exhaustion

### Performance Metrics
Record the following metrics:
- Requests per second: _______
- Average response time: _______
- 95th percentile response time: _______
- Failed requests: _______
- Database connection pool usage: _______

---

## T065: Stateless Backend Validation

Verify conversation persists after server restart:

### Test Procedure
1. **Start server and create conversation**
   - [ ] Started server
   - [ ] Sent chat message
   - [ ] Received conversation_id
   - [ ] Sent 2-3 more messages in same conversation

2. **Check database state**
   ```bash
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM messages WHERE conversation_id='YOUR_CONVERSATION_ID';"
   ```
   - [ ] Message count matches expected (user + assistant messages)

3. **Stop server**
   - [ ] Stopped server with CTRL+C
   - [ ] Server process terminated

4. **Verify no in-memory state**
   - [ ] Server logs show clean shutdown
   - [ ] No state files created

5. **Restart server**
   - [ ] Restarted server
   - [ ] Server started successfully
   - [ ] No errors in startup logs

6. **Send new message with same conversation_id**
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Authorization: Bearer JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "What did we talk about?", "conversation_id": "YOUR_CONVERSATION_ID"}'
   ```
   - [ ] Request successful (200 OK)
   - [ ] Agent response shows awareness of previous messages
   - [ ] Agent can reference earlier conversation context

7. **Verify conversation history loaded**
   - [ ] Check server logs for history loading
   - [ ] Verify token counting occurred
   - [ ] Verify messages loaded from database

### Expected Behavior
- ✅ Server holds NO state between restarts
- ✅ All conversation state loaded from database
- ✅ Agent has full conversation context
- ✅ No data loss after restart

---

## Error Handling Validation

Test error paths to ensure proper error handling:

### Authentication Errors

#### Missing JWT
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```
- [ ] Returns 401 Unauthorized
- [ ] Error message: "Invalid or missing token"

#### Invalid JWT
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer invalid-token" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```
- [ ] Returns 401 Unauthorized
- [ ] Error message indicates invalid token

#### Expired JWT
- [ ] Use expired token
- [ ] Returns 401 Unauthorized
- [ ] Error message: "Token has expired"

### Authorization Errors

#### Unauthorized Conversation Access
```bash
# Use User A's JWT with User B's conversation_id
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer USER_A_JWT" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "conversation_id": "USER_B_CONVERSATION_ID"}'
```
- [ ] Returns 403 Forbidden
- [ ] Error message: "Access denied"
- [ ] Logged in server logs

### Validation Errors

#### Message Too Long
```bash
# Create message > 10,000 characters
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "VERY_LONG_MESSAGE_HERE..."}'
```
- [ ] Returns 422 Unprocessable Entity
- [ ] Error message indicates message too long

### Service Errors

#### Invalid Gemini API Key
- [ ] Set invalid GEMINI_API_KEY in .env
- [ ] Restart server
- [ ] Send chat message
- [ ] Returns 503 Service Unavailable
- [ ] Error message: "AI service temporarily unavailable"

#### Database Connection Failure
- [ ] Stop database
- [ ] Send chat message
- [ ] Returns 503 Service Unavailable
- [ ] Error logged in server logs

### Timeout Errors

#### Request Timeout
- [ ] Send complex message that takes > 5 seconds
- [ ] Returns 504 Gateway Timeout
- [ ] Request terminated by middleware

---

## Integration Testing

Test complete end-to-end flows:

### Flow 1: New User First Chat
1. [ ] User signs up via frontend
2. [ ] User navigates to chat page
3. [ ] User sends first message
4. [ ] Conversation auto-created
5. [ ] Response displayed in UI
6. [ ] Conversation persists in database

### Flow 2: Task Management via Chat
1. [ ] User: "Add a task to buy groceries"
2. [ ] Agent invokes add_task tool
3. [ ] Task created in database
4. [ ] User: "Show me my tasks"
5. [ ] Agent invokes list_tasks tool
6. [ ] Task list displayed
7. [ ] User: "Mark it as done"
8. [ ] Agent invokes complete_task tool
9. [ ] Task marked complete in database

### Flow 3: Multi-Turn Conversation
1. [ ] User sends 10+ messages in conversation
2. [ ] Agent maintains context throughout
3. [ ] Agent can reference earlier messages
4. [ ] Conversation history truncated at 2000 tokens
5. [ ] No context loss for recent messages

### Flow 4: User Isolation
1. [ ] User A creates tasks via chat
2. [ ] User B logs in
3. [ ] User B sends "Show me my tasks"
4. [ ] User B sees only their own tasks
5. [ ] User B cannot access User A's conversation

---

## Sign-Off

### Implementation Complete
- [x] All Phase 1-5 tasks implemented (T001-T041)
- [x] All Phase 6 tasks implemented (T042-T046)
- [x] All Phase 7 tasks implemented (T047-T055)
- [x] All Phase 8 code tasks implemented (T056-T058, T060-T061, T063)

### Manual Validation Required
- [ ] T059: Quickstart validation (10 steps)
- [ ] T062: Phase-2 regression testing
- [ ] T064: Performance testing (50 concurrent requests)
- [ ] T065: Stateless backend validation

### Ready for Deployment
- [ ] All validation checklists completed
- [ ] No critical issues found
- [ ] Performance meets requirements
- [ ] Error handling verified
- [ ] User isolation confirmed
- [ ] Stateless backend confirmed

---

## Notes

**Implementation Status**: ✅ COMPLETE

**Next Steps**:
1. Execute manual validation checklist
2. Fix any issues discovered during validation
3. Run integration tests
4. Deploy to staging environment
5. Perform user acceptance testing

**Known Limitations**:
- Gemini API rate limits apply (free tier)
- 5 second timeout for chat requests
- 2000 token limit for conversation history
- Single conversation per user (by design)

**Documentation**:
- ✅ README.md updated with Phase-3 documentation
- ✅ Quickstart.md provides step-by-step setup guide
- ✅ Code comments added for complex logic
- ✅ Error handling documented
- ✅ Architecture documented

---

**Validation Checklist Status**: 📋 READY FOR EXECUTION
**Estimated Validation Time**: 2-3 hours
