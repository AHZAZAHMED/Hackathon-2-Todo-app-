# Backend API - Hackathon Phase-3 AI Chat System

FastAPI backend with JWT verification and AI-powered conversational task management.

## Tech Stack

- **Framework**: FastAPI 0.109.0
- **Authentication**: JWT verification (Better Auth tokens)
- **Database**: PostgreSQL (Neon Serverless)
- **ORM**: SQLModel 0.0.14
- **AI**: OpenAI SDK with Gemini 2.0 Flash
- **MCP**: Model Context Protocol for task tools
- **Python**: 3.11+

## Features

### Phase-2 (Authentication & Tasks)
- ✅ JWT token verification with Better Auth integration
- ✅ User authentication middleware
- ✅ CRUD endpoints for task management
- ✅ Database-backed persistence with user isolation
- ✅ CORS configuration for frontend

### Phase-3 (AI Chat)
- ✅ Conversational AI interface using Gemini 2.0 Flash
- ✅ MCP tools for task operations (add, list, complete, delete, update)
- ✅ Stateless backend with database-persisted conversations
- ✅ Function calling / tool invocation
- ✅ Conversation history with token-based truncation
- ✅ Comprehensive error handling
- ✅ Request timeout middleware (5 seconds)

## Prerequisites

- Python 3.11 or higher
- PostgreSQL database (Neon Serverless or local)
- BETTER_AUTH_SECRET (must match frontend)
- GEMINI_API_KEY (from Google AI Studio)

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
# JWT Verification (MUST match frontend BETTER_AUTH_SECRET)
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long

# Database (Neon Serverless or local PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/database

# CORS (Frontend URL)
FRONTEND_URL=http://localhost:3000

# Server
HOST=0.0.0.0
PORT=8001

# Phase-3: Gemini API Key (Get from Google AI Studio)
GEMINI_API_KEY=your-gemini-api-key-here
```

**Important**:
- Use the SAME `BETTER_AUTH_SECRET` as the frontend
- Get Gemini API key from: https://makersuite.google.com/app/apikey

### 4. Run Database Migrations

```bash
# Connect to your PostgreSQL database and run migrations in order:
psql "your-database-url" -f migrations/001_create_auth_tables.sql
psql "your-database-url" -f migrations/002_create_tasks_table.sql
psql "your-database-url" -f migrations/003_create_chat_tables.sql
```

Or use your preferred migration tool.

### 5. Start Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check

```
GET /
GET /api/health
```

Returns API status and version.

### Protected Endpoint (Example)

```
GET /api/protected
Authorization: Bearer <jwt_token>
```

Returns authenticated user information.

**Response**:
```json
{
  "message": "This is a protected route",
  "user": {
    "user_id": "clx1234567890",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

### Task Management (Phase-2)

#### List Tasks
```
GET /api/tasks
Authorization: Bearer <jwt_token>
```

Returns all tasks for authenticated user.

#### Create Task
```
POST /api/tasks
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

#### Get Task
```
GET /api/tasks/{task_id}
Authorization: Bearer <jwt_token>
```

#### Update Task
```
PUT /api/tasks/{task_id}
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "title": "Updated title",
  "description": "Updated description"
}
```

#### Toggle Task Completion
```
PATCH /api/tasks/{task_id}/complete
Authorization: Bearer <jwt_token>
```

#### Delete Task
```
DELETE /api/tasks/{task_id}
Authorization: Bearer <jwt_token>
```

### AI Chat (Phase-3)

#### Send Chat Message
```
POST /api/chat
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "message": "Add a task to buy milk",
  "conversation_id": "optional-uuid-here"
}
```

**Request**:
- `message` (required): User message (1-10,000 characters)
- `conversation_id` (optional): UUID of existing conversation

**Response**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "I've added a task to buy milk for you.",
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

**Features**:
- Conversational task management (natural language)
- Automatic tool invocation (add, list, complete, delete, update tasks)
- Conversation history maintained (up to 2000 tokens)
- Single conversation per user (auto-created)
- Stateless backend (all state in database)

**Example Conversations**:

```
User: "Add a task to buy groceries"
AI: "I've added a task to buy groceries for you."
[Tool: add_task invoked]

User: "Show me my tasks"
AI: "You have 3 tasks: 1. Buy groceries (incomplete), 2. Call dentist (complete), 3. Finish report (incomplete)"
[Tool: list_tasks invoked]

User: "Mark the first one as done"
AI: "I've marked 'Buy groceries' as complete."
[Tool: complete_task invoked]

User: "Delete the second task"
AI: "I've deleted the task 'Call dentist'."
[Tool: delete_task invoked]
```

## Architecture

### Phase-3 Chat Flow

```
User Message → Chat Endpoint → Fetch History → Store Message →
Invoke Agent → Agent Selects Tools → MCP Tools Execute →
Store Response → Return to User
```

**Key Principles**:
- **Stateless Backend**: All conversation state persists in database
- **MCP Architecture**: Only MCP tools can mutate task data
- **User Isolation**: JWT-based user_id filters all queries
- **Function Calling**: Agent decides which tools to invoke
- **Token Management**: Conversation history truncated to 2000 tokens

### MCP Tools (Model Context Protocol)

The AI agent can invoke these tools for task management:

1. **add_task(title, description)** - Creates new task
2. **list_tasks(completed)** - Lists tasks with optional filter
3. **complete_task(task_id)** - Toggles task completion
4. **delete_task(task_id)** - Deletes task
5. **update_task(task_id, title, description)** - Updates task

**Security**: All tools receive `user_id` from JWT, ensuring users can only access their own data.

## Authentication Flow

1. **User signs up/logs in** on frontend (Better Auth)
2. **Better Auth issues JWT token** stored in httpOnly cookie
3. **Frontend attaches JWT** to API requests in Authorization header
4. **Backend verifies JWT signature** using BETTER_AUTH_SECRET
5. **Backend extracts user_id** from JWT claims
6. **Backend uses user_id** for all database queries

## JWT Token Structure

**Claims**:
- `user_id`: Primary user identifier
- `email`: User email address
- `name`: User display name
- `exp`: Expiration timestamp (24 hours)
- `iat`: Issued-at timestamp

**Algorithm**: HS256 (HMAC with SHA-256)

## Rate Limiting

- **Limit**: 5 failed login attempts per email per 15 minutes
- **Storage**: PostgreSQL `rate_limits` table
- **Response**: 429 Too Many Requests with retry time

## Error Responses

### 401 Unauthorized

```json
{
  "detail": {
    "error": {
      "code": "TOKEN_EXPIRED",
      "message": "Token has expired. Please log in again."
    }
  }
}
```

**Error Codes**:
- `TOKEN_EXPIRED`: JWT token has expired
- `INVALID_TOKEN`: JWT signature invalid or malformed
- `UNAUTHORIZED`: No Authorization header provided

### 403 Forbidden

```json
{
  "error": "Access denied. You do not have permission to access this conversation."
}
```

Returned when user tries to access another user's conversation.

### 422 Unprocessable Entity

```json
{
  "error": "Invalid request: Message must be less than 10,000 characters"
}
```

Returned for validation errors (message too long, invalid format, etc.).

### 500 Internal Server Error

```json
{
  "error": "Unable to complete task operation. Please try again."
}
```

Returned when MCP tool execution fails or unexpected errors occur.

### 503 Service Unavailable

```json
{
  "error": "AI service temporarily unavailable. Please try again later."
}
```

Returned when Gemini API is unavailable or database connection fails.

### 504 Gateway Timeout

```json
{
  "error": "Request timeout. Please try again."
}
```

Returned when chat request exceeds 5 second timeout.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Environment configuration
│   ├── database.py          # Database connection with pooling
│   ├── exceptions.py        # Custom exception classes (Phase-3)
│   ├── auth/                # Authentication module
│   │   ├── __init__.py
│   │   ├── middleware.py    # JWT verification middleware
│   │   ├── dependencies.py  # FastAPI dependencies
│   │   └── utils.py         # JWT utilities
│   ├── models/              # SQLModel schemas
│   │   ├── __init__.py
│   │   ├── user.py          # User model
│   │   ├── task.py          # Task model (Phase-2)
│   │   ├── conversation.py  # Conversation model (Phase-3)
│   │   └── message.py       # Message model (Phase-3)
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── task.py          # Task schemas (Phase-2)
│   │   └── chat.py          # Chat schemas (Phase-3)
│   ├── routes/              # API routes
│   │   ├── __init__.py
│   │   ├── tasks.py         # Task CRUD endpoints (Phase-2)
│   │   └── chat.py          # Chat endpoint (Phase-3)
│   ├── services/            # Business logic (Phase-3)
│   │   ├── __init__.py
│   │   ├── conversation_service.py  # Conversation management
│   │   └── message_service.py       # Message storage & history
│   ├── ai/                  # AI agent logic (Phase-3)
│   │   ├── __init__.py
│   │   ├── agent.py         # OpenAI Agent with Gemini
│   │   ├── gemini_client.py # Gemini API client
│   │   └── prompts.py       # System prompts
│   ├── mcp/                 # MCP tools (Phase-3)
│   │   ├── __init__.py
│   │   ├── server.py        # MCP tool registration
│   │   └── tools.py         # Task management tools
│   └── middleware/          # Custom middleware (Phase-3)
│       ├── __init__.py
│       └── timeout.py       # Request timeout middleware
├── migrations/              # Database migrations
│   ├── 001_create_auth_tables.sql    # User tables (Phase-1)
│   ├── 002_create_tasks_table.sql    # Tasks table (Phase-2)
│   └── 003_create_chat_tables.sql    # Chat tables (Phase-3)
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

## Development

### Run with Auto-Reload

```bash
uvicorn app.main:app --reload
```

### View API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Testing Protected Endpoints

1. Get JWT token from frontend (login/signup)
2. Copy token from browser DevTools → Application → Cookies
3. Use token in Authorization header:

```bash
curl -X GET http://localhost:8000/api/protected \
  -H "Authorization: Bearer <your-jwt-token>"
```

## Security

- ✅ JWT tokens verified on every request
- ✅ Passwords hashed with bcrypt (managed by Better Auth)
- ✅ Rate limiting prevents brute-force attacks
- ✅ CORS configured for specific frontend origin
- ✅ httpOnly cookies prevent XSS attacks
- ✅ Stateless backend (horizontally scalable)

## Troubleshooting

### "BETTER_AUTH_SECRET is not set"

**Solution**: Create `.env` file with `BETTER_AUTH_SECRET` matching frontend.

### "GEMINI_API_KEY is not set"

**Solution**: Get API key from Google AI Studio (https://makersuite.google.com/app/apikey) and add to `.env`.

### "Database connection failed"

**Solution**: Verify `DATABASE_URL` is correct and database is accessible.

### "401 Unauthorized" on all requests

**Solution**: Verify `BETTER_AUTH_SECRET` is identical in frontend and backend.

### CORS errors

**Solution**: Verify `FRONTEND_URL` in `.env` matches frontend URL exactly.

### "503 AI service unavailable"

**Solution**:
- Verify `GEMINI_API_KEY` is valid
- Check Gemini API status
- Verify internet connectivity

### Chat requests timeout (504)

**Solution**:
- Requests exceeding 5 seconds are automatically terminated
- Check Gemini API response time
- Consider increasing timeout in `app/middleware/timeout.py` if needed

### Conversation history not loading

**Solution**:
- Verify migration 003 was applied successfully
- Check `conversations` and `messages` tables exist
- Verify foreign key constraints are in place

## Production Deployment

1. Set `BETTER_AUTH_SECRET` to a cryptographically secure value (32+ characters)
2. Use production PostgreSQL database URL
3. Set `FRONTEND_URL` to production frontend domain
4. Use HTTPS for all requests
5. Consider using a process manager (e.g., gunicorn, supervisor)

```bash
# Production server with gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## License

Hackathon II Phase-2 Project
