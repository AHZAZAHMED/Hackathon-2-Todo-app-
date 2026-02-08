# Claude Code Rules - Hackathon II Phase-3 Todo AI Chatbot

**Project Type:** Spec-Driven Full-Stack Web Application with AI Chatbot
**Current Phase:** Phase-3 (AI Chatbot Integration)
**Status:** Active Development
**Enforcement:** Strict - All rules are blocking requirements

---

## Project Overview

**Hackathon II Phase-3: AI-Powered Todo Chatbot**

Building on the completed Phase-2 foundation, Phase-3 introduces an AI-powered conversational interface for task management using OpenAI Agents SDK and MCP (Model Context Protocol).

**Phase-2 Foundation (✅ COMPLETE - DO NOT MODIFY):**
- Frontend: Next.js 16+ App Router + TypeScript + Tailwind CSS
- Authentication: Better Auth + JWT + Prisma (auth tables only)
- Backend: FastAPI with 6 CRUD endpoints + SQLModel ORM
- Database: PostgreSQL (Neon) with user and tasks tables
- User isolation and JWT-based authentication
- ORM Strategy: Prisma for Better Auth (frontend), SQLModel for application data (backend)

**Phase-3 Additions (🚧 IN PROGRESS):**
- AI Chatbot: OpenAI Agents SDK
- MCP Server: Official MCP SDK with task tools
- Chat UI: OpenAI ChatKit
- Chat Endpoint: POST /api/chat
- Conversation Persistence: conversations and messages tables (SQLModel)
- ORM: SQLModel only (no Prisma needed for Phase-3)

**Stack:**
- Frontend: Next.js 16+ + OpenAI ChatKit UI
- Authentication: Better Auth + JWT + Prisma (auth tables only)
- Backend: FastAPI + OpenAI Agents SDK + SQLModel ORM
- MCP Layer: Official MCP SDK (task tools)
- Database: PostgreSQL (Neon Serverless)
- Workflow: Spec-Kit Plus (Agentic Dev Stack)
- ORM Strategy: Prisma (Better Auth only), SQLModel (application data)

**Non-Negotiable Constraints:**
- NO mock data, NO hardcoded users, NO in-memory storage
- All state persists in PostgreSQL
- All identity derives from JWT
- Phase-2 code is STABLE FOUNDATION - do not modify unless absolutely necessary
- MCP tools are the ONLY components allowed to perform database mutations
- Agent NEVER accesses database directly
- FastAPI server MUST remain stateless

---

## Architecture

### Phase-2 Architecture (✅ STABLE FOUNDATION)

**Component Interaction:**
```
User → Frontend (Next.js) → Better Auth (JWT) → Backend (FastAPI) → PostgreSQL (Neon)
```

**Authentication Flow:**
1. Better Auth issues JWT on login
2. Frontend stores JWT (httpOnly cookie or secure storage)
3. Frontend API client attaches JWT to all requests automatically
4. Backend verifies JWT signature
5. Backend extracts `user_id` from JWT claims
6. Backend uses `user_id` for database queries

**User Isolation:**
- User identity derived ONLY from JWT claims
- Frontend NEVER sends `user_id` manually
- Backend NEVER trusts client-provided `user_id`
- Database enforces foreign key constraints: `tasks.user_id → users.id`
- All queries filter by authenticated `user_id`

**API Communication:**
- Centralized API client in frontend (`lib/api-client.ts` or similar)
- All backend calls go through this client
- Client handles JWT attachment automatically
- No direct fetch/axios calls scattered in components

### Phase-3 Architecture (🚧 NEW - AI CHATBOT)

**Complete System Flow:**
```
┌─────────────────────────────────────────────────────────────┐
│  Frontend (Next.js + OpenAI ChatKit)                        │
│  - Chat UI interface                                         │
│  - Sends messages to backend                                 │
│  - Displays AI responses                                     │
└────────────────────┬────────────────────────────────────────┘
                     │ POST /api/chat (with JWT)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend (FastAPI - STATELESS)                              │
│  1. Verify JWT → Extract user_id                            │
│  2. Fetch conversation history from DB                       │
│  3. Store user message in DB                                 │
│  4. Build agent message array                                │
│  5. Invoke OpenAI Agent                                      │
│  6. Store assistant response in DB                           │
│  7. Return response to client                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  AI Layer (OpenAI Agents SDK)                               │
│  - Analyzes user intent                                      │
│  - Decides which tools to invoke                             │
│  - NEVER accesses database directly                          │
│  - Returns tool invocation requests                          │
└────────────────────┬────────────────────────────────────────┘
                     │ Tool invocation
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  MCP Layer (Official MCP SDK - STATELESS)                   │
│  Tools:                                                      │
│  - add_task(title, description)                              │
│  - list_tasks()                                              │
│  - complete_task(task_id)                                    │
│  - delete_task(task_id)                                      │
│  - update_task(task_id, title, description)                  │
│                                                              │
│  ONLY layer allowed to mutate task data                      │
└────────────────────┬────────────────────────────────────────┘
                     │ SQLModel operations
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Database (PostgreSQL - Neon)                               │
│  Tables:                                                     │
│  - user (Better Auth)                                        │
│  - tasks (Phase-2)                                           │
│  - conversations (Phase-3)                                   │
│  - messages (Phase-3)                                        │
└─────────────────────────────────────────────────────────────┘
```

**Chat Flow (MANDATORY SEQUENCE):**
1. User sends message via ChatKit UI
2. Frontend sends POST to `/api/chat` with JWT
3. Backend verifies JWT and extracts `user_id`
4. Backend fetches conversation history from database
5. Backend stores user message in `messages` table
6. Backend builds message array for agent
7. Backend invokes OpenAI Agent with message array
8. Agent analyzes intent and decides tool usage
9. If tools needed, agent invokes MCP tools
10. MCP tools execute database operations via SQLModel
11. Agent receives tool results and formulates response
12. Backend stores assistant response in `messages` table
13. Backend returns response to frontend
14. Frontend displays response in ChatKit UI
15. **Server holds NO state** - all state in database

**Critical Constraints:**
- ❌ Agent NEVER accesses database directly
- ❌ Chat endpoint NEVER writes task data directly
- ✅ ALL task mutations flow through MCP tools
- ✅ MCP tools use SQLModel for database operations
- ✅ Backend remains stateless (no in-memory conversation state)
- ✅ Conversation state persists in database
- ✅ user_id from JWT used for all operations

---

## Mandatory Spec Workflow

**BLOCKING REQUIREMENT:** All development MUST follow this sequence. Coding outside this pipeline is prohibited.

1. **`/sp.constitution`** - Define project principles
2. **`/sp.specify`** - Create feature specification
3. **`/sp.spec.seed`** - Seed specification with examples
4. **`/sp.plan`** - Generate architectural plan
5. **`/sp.tasks`** - Break down into testable tasks
6. **Claude Code implementation** - Execute tasks

**Enforcement:**
When user requests coding without approved specs, Claude MUST:
1. Warn: "⚠️ No approved spec detected for this feature."
2. Ask: "Would you like to run the spec workflow first (`/sp.specify`), or proceed without specs?"
3. Wait for explicit confirmation before coding

---

## Core Rules

### Phase-2 Rules (✅ STABLE - CONTINUE ENFORCING)

**Identity & Authentication:**
- ✅ JWT is the ONLY source of user identity
- ❌ NEVER hardcode user IDs
- ❌ NEVER accept `user_id` from frontend request body/params
- ✅ Backend MUST extract `user_id` from verified JWT claims
- ✅ Frontend MUST attach JWT automatically via centralized client

**Data & State:**
- ❌ NEVER introduce mock data
- ❌ NEVER use in-memory storage
- ✅ All state MUST persist in PostgreSQL
- ✅ Database MUST enforce user isolation via foreign keys
- ✅ Migrations required for all schema changes

**API Design:**
- ✅ All API calls through centralized client
- ❌ NEVER scatter fetch/axios calls in components
- ✅ Backend MUST reject requests without valid JWT
- ✅ Backend MUST return 401 for invalid/missing tokens
- ✅ Backend MUST return 403 for unauthorized resource access

**Configuration:**
- ✅ Tailwind MUST be officially configured (not CDN)
- ✅ TypeScript strict mode required
- ✅ Environment variables mandatory for secrets
- ❌ NEVER commit `.env` files
- ✅ Provide `.env.example` with placeholder values

**Implementation Quality:**
- ❌ NEVER create partial implementations
- ❌ NEVER apply patch fixes to symptoms
- ✅ Always fix root causes
- ✅ All changes must be testable
- ✅ Code must pass quality gates before proceeding

### Phase-3 Rules (🚧 NEW - CRITICAL)

**MCP Architecture (NON-NEGOTIABLE):**
- ✅ MCP tools are the ONLY components allowed to perform task database mutations
- ❌ Agent MUST NEVER access database directly
- ❌ Chat endpoint MUST NEVER write task data directly
- ✅ ALL task creation, updates, deletions, and status changes MUST occur inside MCP tools
- ✅ MCP tools MUST use SQLModel for database operations
- ✅ MCP tools MUST be stateless
- ✅ MCP tools MUST receive user_id as parameter (from JWT)

**AI Agent Rules:**
- ✅ Agent decides intent and tool usage ONLY
- ❌ Agent NEVER performs database operations
- ✅ Agent invokes MCP tools for all task operations
- ✅ Agent receives tool results and formulates responses
- ✅ Use OpenAI Agents SDK (official SDK required)
- ❌ NO custom agent implementations

**Stateless Backend:**
- ✅ FastAPI server MUST remain stateless
- ❌ NO in-memory conversation state
- ✅ Conversation state MUST persist in database
- ✅ Fetch conversation history from DB on each request
- ✅ Store all messages (user and assistant) in database
- ✅ Server holds NO state between requests

**Chat Endpoint Rules:**
- ✅ POST `/api/chat` endpoint required
- ✅ JWT verification mandatory
- ✅ Extract user_id from JWT (never from request body)
- ✅ Fetch conversation history before agent invocation
- ✅ Store user message before agent invocation
- ✅ Store assistant response after agent completion
- ✅ Return response to client
- ✅ Handle tool invocation tracking

**Phase-2 Stability:**
- ❌ DO NOT modify Phase-2 CRUD endpoints unless absolutely necessary
- ❌ DO NOT change existing task model schema
- ❌ DO NOT alter authentication flow
- ✅ Phase-2 code is STABLE FOUNDATION
- ✅ Only add new Phase-3 features
- ✅ Maintain backward compatibility

**Technology Stack (FIXED - NO SUBSTITUTIONS):**
- ✅ Frontend: OpenAI ChatKit (official UI library)
- ✅ Backend: FastAPI (existing)
- ✅ AI: OpenAI Agents SDK (official SDK)
- ✅ MCP: Official MCP SDK
- ✅ ORM: Prisma (Better Auth only), SQLModel (application data)
- ✅ Database: PostgreSQL (Neon)
- ✅ Auth: Better Auth JWT (existing)
- ❌ NO alternative libraries or frameworks
- ❌ Phase-3 does NOT need Prisma (SQLModel only)

---

## Folder Structure

**Monorepo Layout:**
```
phase-03/
├── CLAUDE.md                 # This file (root rules - Phase-3)
├── specs/                    # Feature specifications
│   ├── 001-frontend-web-app/      # Phase-2 (✅ Complete)
│   ├── 002-auth/                  # Phase-2 (✅ Complete)
│   ├── 003-tasks-crud-api/        # Phase-2 (✅ Complete)
│   └── 004-ai-chatbot/            # Phase-3 (🚧 New)
│       ├── spec.md
│       ├── plan.md
│       └── tasks.md
├── frontend/
│   ├── CLAUDE.md            # Frontend-specific rules
│   ├── app/                 # Next.js App Router
│   │   ├── chat/            # 🚧 NEW: Chat page
│   │   ├── dashboard/       # ✅ Existing: Task dashboard
│   │   └── ...
│   ├── components/
│   │   ├── chat/            # 🚧 NEW: ChatKit components
│   │   ├── dashboard/       # ✅ Existing: Task components
│   │   └── ...
│   ├── lib/
│   │   ├── api-client.ts    # ✅ Existing: Centralized API client
│   │   └── chat-client.ts   # 🚧 NEW: Chat API client
│   └── ...
├── backend/
│   ├── CLAUDE.md            # Backend-specific rules
│   ├── app/
│   │   ├── main.py          # ✅ Existing: FastAPI app
│   │   ├── auth/            # ✅ Existing: JWT verification
│   │   ├── models/          # SQLModel schemas
│   │   │   ├── task.py      # ✅ Existing
│   │   │   ├── conversation.py  # 🚧 NEW
│   │   │   └── message.py   # 🚧 NEW
│   │   ├── routes/
│   │   │   ├── tasks.py     # ✅ Existing: CRUD endpoints
│   │   │   └── chat.py      # 🚧 NEW: Chat endpoint
│   │   ├── ai/              # 🚧 NEW: AI agent logic
│   │   │   ├── agent.py     # OpenAI Agents SDK integration
│   │   │   └── prompts.py   # System prompts
│   │   └── mcp/             # 🚧 NEW: MCP server
│   │       ├── server.py    # MCP server setup
│   │       └── tools.py     # Task tools (add, list, complete, etc.)
│   ├── migrations/
│   │   ├── 001_create_auth_tables.sql    # ✅ Existing
│   │   ├── 002_create_tasks_table.sql    # ✅ Existing
│   │   └── 003_create_chat_tables.sql    # 🚧 NEW
│   └── ...
├── history/
│   ├── prompts/            # Prompt History Records
│   │   ├── 001-frontend-web-app/  # ✅ Phase-2
│   │   ├── 002-auth/              # ✅ Phase-2
│   │   ├── 003-tasks-crud-api/    # ✅ Phase-2
│   │   └── 004-ai-chatbot/        # 🚧 Phase-3
│   └── adr/                # Architecture Decision Records
└── .specify/               # Spec-Kit Plus templates
```

**CLAUDE.md Hierarchy:**
- Claude Code reads the **closest** CLAUDE.md first
- Root CLAUDE.md: project-wide rules (this file - Phase-3 rules)
- `frontend/CLAUDE.md`: Next.js, Better Auth, UI rules (Phase-2 + ChatKit)
- `backend/CLAUDE.md`: FastAPI, JWT verification, database rules (Phase-2 + AI/MCP)

**Purpose of Separation:**
Prevents cross-stack confusion. Frontend rules don't leak into backend work, and vice versa.

**Phase-3 New Components:**
- 🚧 `backend/app/routes/chat.py` - Chat endpoint
- 🚧 `backend/app/ai/` - OpenAI Agents SDK integration
- 🚧 `backend/app/mcp/` - MCP server and tools
- 🚧 `backend/app/models/conversation.py` - Conversation model
- 🚧 `backend/app/models/message.py` - Message model
- 🚧 `backend/migrations/003_create_chat_tables.sql` - Chat tables migration
- 🚧 `frontend/app/chat/` - Chat page with ChatKit UI
- 🚧 `frontend/components/chat/` - Chat components
- 🚧 `frontend/lib/chat-client.ts` - Chat API client

---

## Skills

**Available Capabilities:**

### Phase-2 Skills (✅ EXISTING)

| Skill | Purpose | Invocation |
|-------|---------|------------|
| `senior-next.js-developer` | Next.js 16+ App Router, TypeScript, Tailwind | Permission-first |
| `better-auth-skill` | Better Auth + JWT integration | Permission-first |
| `backend-engineer(FastAPI)` | FastAPI, Python, API design | Permission-first |
| `database-skill` | PostgreSQL, SQLModel, migrations | Permission-first |
| `implementation-validator-playwright` | Browser-based validation after implementation | Permission-first |
| `integration-testing-engineer` | End-to-end flow validation | Permission-first |
| `doc-coauthoring` | Structured documentation workflow | Permission-first |
| `browsing-with-playwright` | Browser automation, screenshots | Permission-first |
| `fetch-library-docs` | Official library documentation | Permission-first |

### Phase-3 Skills (🚧 RELEVANT FOR AI CHATBOT)

| Skill | Purpose | Phase-3 Usage |
|-------|---------|---------------|
| `backend-engineer(FastAPI)` | FastAPI, Python, API design | Chat endpoint, MCP server, AI agent integration |
| `database-skill` | PostgreSQL, SQLModel, migrations | Conversations and messages tables, migration 003 |
| `senior-next.js-developer` | Next.js, TypeScript | ChatKit UI integration, chat page |
| `fetch-library-docs` | Official library documentation | OpenAI Agents SDK, MCP SDK, ChatKit docs |
| `integration-testing-engineer` | End-to-end flow validation | Complete chat flow testing |

**Invocation Policy:**
1. When a task matches a skill's domain, Claude MUST ask: "This task involves [domain]. Would you like me to invoke the `[skill-name]` skill?"
2. Wait for user confirmation before invoking
3. User can explicitly request skills: "Use the backend-engineer(FastAPI) skill"
4. Skills run with full context from this conversation

**Phase-3 Note:**
For AI chatbot implementation, the `backend-engineer(FastAPI)` skill is particularly relevant for:
- MCP server setup and tool implementation
- OpenAI Agents SDK integration
- Chat endpoint development
- Stateless backend architecture

---

## Development Order

**BLOCKING SEQUENCE:** Each phase must pass quality gates before proceeding to the next.

### Phase 1: Frontend Implementation (✅ COMPLETE)
**Tasks:**
- Next.js 16+ App Router setup
- TypeScript strict mode configuration
- Tailwind CSS official configuration
- Basic UI components (login, signup, todo list)
- Centralized API client (`lib/api-client.ts`)

**Quality Gate:**
- ✅ `npm run dev` succeeds without errors
- ✅ Tailwind styles render correctly
- ✅ TypeScript compiles with no errors
- ✅ API client structure in place

**Status:** ✅ Complete - Do not modify

---

### Phase 2: Authentication (✅ COMPLETE)
**Tasks:**
- Better Auth installation and configuration
- JWT issuance on login/signup
- JWT storage (httpOnly cookie or secure storage)
- API client JWT attachment logic
- Auth state management

**Quality Gate:**
- ✅ JWT issued on successful login
- ✅ JWT stored securely
- ✅ JWT attached to API requests automatically
- ✅ Auth state persists across page reloads

**Status:** ✅ Complete - Do not modify

---

### Phase 3: Backend API (✅ COMPLETE)
**Tasks:**
- FastAPI setup with CORS
- JWT verification middleware
- User extraction from JWT claims
- CRUD endpoints for tasks (`/tasks`)
- Error handling (401, 403, 422, 500)

**Quality Gate:**
- ✅ Backend starts without errors
- ✅ JWT verification rejects invalid tokens (401)
- ✅ Endpoints extract `user_id` from JWT
- ✅ Unauthorized requests return 403
- ✅ API returns proper error responses

**Status:** ✅ Complete - Do not modify

---

### Phase 4: Database Schema + Integration (✅ COMPLETE)
**Tasks:**
- Neon PostgreSQL connection
- SQLModel or equivalent ORM setup
- `users` table (managed by Better Auth)
- `tasks` table with `user_id` foreign key
- Database migrations
- User isolation enforcement

**Quality Gate:**
- ✅ Database connection succeeds
- ✅ Migrations run successfully
- ✅ Foreign key constraints enforced
- ✅ Tasks persist in database
- ✅ Users only see their own tasks
- ✅ No orphan records

**Status:** ✅ Complete - Do not modify

---

### Phase 5: Full Integration Testing (✅ COMPLETE)
**Tasks:**
- End-to-end user flows (signup → login → create task → logout)
- JWT flow validation (issuance → attachment → verification)
- User isolation verification (User A cannot see User B's tasks)
- Error path testing (invalid JWT, unauthorized access)

**Quality Gate:**
- ✅ All user flows complete successfully
- ✅ JWT flow works end-to-end
- ✅ User isolation enforced
- ✅ Error paths handled gracefully

**Status:** ✅ Complete - Phase-2 foundation stable

---

### Phase 6: AI Chatbot Integration (🚧 CURRENT PHASE)

**MANDATORY:** Follow Agentic Dev Stack workflow:
1. Run `/sp.specify` to create specification
2. Run `/sp.plan` to generate implementation plan
3. Run `/sp.tasks` to break down into tasks
4. Implement via Claude Code (no manual coding)

**Tasks:**

**6.1: Database Schema for Chat**
- Create `conversations` table (id, user_id, title, created_at, updated_at)
- Create `messages` table (id, conversation_id, role, content, tool_calls, created_at)
- Write migration script (003_create_chat_tables.sql)
- Apply migration
- Verify foreign key constraints

**6.2: MCP Server Implementation**
- Install Official MCP SDK
- Create MCP server setup (`backend/app/mcp/server.py`)
- Implement task tools (`backend/app/mcp/tools.py`):
  - `add_task(user_id, title, description)` → SQLModel insert
  - `list_tasks(user_id)` → SQLModel query
  - `complete_task(user_id, task_id)` → SQLModel update
  - `delete_task(user_id, task_id)` → SQLModel delete
  - `update_task(user_id, task_id, title, description)` → SQLModel update
- Ensure tools are stateless
- Ensure tools receive user_id as parameter
- Test tool invocations

**6.3: OpenAI Agent Integration**
- Install OpenAI Agents SDK
- Create agent setup (`backend/app/ai/agent.py`)
- Define system prompts (`backend/app/ai/prompts.py`)
- Configure agent to use MCP tools
- Implement agent invocation logic
- Handle tool invocation responses
- Test agent with sample messages

**6.4: Chat Endpoint**
- Create POST `/api/chat` endpoint (`backend/app/routes/chat.py`)
- Implement JWT verification
- Extract user_id from JWT
- Fetch conversation history from database
- Store user message in database
- Build agent message array
- Invoke OpenAI Agent
- Store assistant response in database
- Return response to client
- Handle errors (401, 422, 500)

**6.5: Frontend Chat UI**
- Install OpenAI ChatKit
- Create chat page (`frontend/app/chat/page.tsx`)
- Implement ChatKit UI components
- Create chat API client (`frontend/lib/chat-client.ts`)
- Integrate with JWT authentication
- Handle message sending
- Display conversation history
- Handle loading states
- Handle errors

**6.6: Integration Testing**
- Test complete chat flow (user message → agent → MCP tools → response)
- Verify conversation persistence
- Verify user isolation (User A cannot see User B's conversations)
- Test tool invocations (add task, list tasks, etc.)
- Test error paths (invalid JWT, tool failures)
- Verify stateless backend (no in-memory state)

**Quality Gate:**
- [ ] Chat endpoint operational
- [ ] MCP tools execute database operations
- [ ] Agent invokes tools correctly
- [ ] Conversations persist in database
- [ ] Messages persist in database
- [ ] User isolation enforced
- [ ] Backend remains stateless
- [ ] ChatKit UI renders correctly
- [ ] End-to-end chat flow works
- [ ] No Phase-2 code modified (unless necessary)

**Validation:**
After implementation, invoke `integration-testing-engineer` skill to validate complete AI chatbot integration.

---

## Database Rules

**Provider:** PostgreSQL (Neon Serverless)

**ORM Strategy (CRITICAL):**
- **Prisma**: Used ONLY for Better Auth tables (user, session, account, verification)
  - Managed by Better Auth on frontend
  - Backend does NOT use Prisma
  - Phase-3 does NOT need Prisma
- **SQLModel**: Used for ALL application tables (tasks, conversations, messages)
  - SQLAlchemy-based ORM
  - Used in backend for all CRUD operations
  - Used by MCP tools for database mutations
  - Phase-3 uses SQLModel exclusively for new tables

**Schema Requirements:**

### Phase-2 Tables (✅ EXISTING - DO NOT MODIFY)

**`user` table:**
- Managed by Better Auth via Prisma (frontend)
- Primary key: `id` (TEXT - CUID)
- Contains: email, name, emailVerified, createdAt, updatedAt
- Additional fields: image, banned, banReason, banExpires
- ORM: Prisma (frontend only, read-only from backend perspective)

**`session`, `account`, `verification` tables:**
- Managed by Better Auth via Prisma (frontend)
- Used for authentication flow
- ORM: Prisma (frontend only)
- Backend does NOT interact with these tables directly

**`tasks` table:**
- Managed by backend via SQLModel
- Primary key: `id` (SERIAL - INTEGER)
- Foreign key: `user_id` references `user.id` (ON DELETE CASCADE)
- Fields: `title` (VARCHAR 500), `description` (TEXT), `completed` (BOOLEAN), `created_at`, `updated_at`
- Indexes: Primary key, user_id, completed
- ORM: SQLModel (backend only)

### Phase-3 Tables (🚧 NEW - TO BE CREATED)

**`conversations` table:**
- Managed by backend via SQLModel
- Primary key: `id` (SERIAL or UUID)
- Foreign key: `user_id` references `user.id` (ON DELETE CASCADE)
- Fields:
  - `user_id` (TEXT, NOT NULL, indexed)
  - `title` (VARCHAR 200, optional - can be auto-generated from first message)
  - `created_at` (TIMESTAMP, NOT NULL, DEFAULT NOW())
  - `updated_at` (TIMESTAMP, NOT NULL, DEFAULT NOW())
- Indexes: Primary key, user_id, created_at
- Purpose: Store conversation threads for each user
- ORM: SQLModel (backend only)

**`messages` table:**
- Managed by backend via SQLModel
- Primary key: `id` (SERIAL or UUID)
- Foreign key: `conversation_id` references `conversations.id` (ON DELETE CASCADE)
- Fields:
  - `conversation_id` (INTEGER/UUID, NOT NULL, indexed)
  - `role` (VARCHAR 20, NOT NULL) - 'user' or 'assistant'
  - `content` (TEXT, NOT NULL) - message content
  - `tool_calls` (JSONB, optional) - tool invocations if any
  - `tool_results` (JSONB, optional) - tool results if any
  - `created_at` (TIMESTAMP, NOT NULL, DEFAULT NOW())
- Indexes: Primary key, conversation_id, created_at
- Purpose: Store individual messages within conversations
- ORM: SQLModel (backend only)

**Constraints:**
- ❌ NO orphan records (foreign key enforced)
- ✅ Migrations required for all schema changes
- ❌ NO in-memory storage
- ✅ All queries MUST filter by authenticated `user_id`
- ✅ Conversations belong to users (user_id FK)
- ✅ Messages belong to conversations (conversation_id FK)
- ✅ CASCADE delete: user deleted → conversations deleted → messages deleted

**MCP Tool Database Access:**
- ✅ MCP tools MUST use SQLModel for all database operations
- ✅ MCP tools MUST receive user_id as parameter
- ✅ MCP tools MUST filter queries by user_id
- ❌ MCP tools MUST NEVER trust client-provided user_id
- ✅ All task mutations MUST occur inside MCP tools
- ❌ Agent MUST NEVER access database directly

**Connection:**
- Use environment variable: `DATABASE_URL`
- Connection pooling recommended
- Handle connection errors gracefully
- Same database connection for Phase-2 and Phase-3 tables

---

## Quality Gates

**BLOCKING REQUIREMENTS:** All must pass before proceeding.

### Phase-2 Gates (✅ COMPLETE - VERIFIED)

**Frontend Gates:**
- ✅ `npm run dev` succeeds without errors
- ✅ Tailwind styles render correctly
- ✅ TypeScript compiles with strict mode
- ✅ No console errors in browser
- ✅ Centralized API client in place

**Authentication Gates:**
- ✅ JWT issued on login
- ✅ JWT stored securely
- ✅ JWT attached to requests automatically
- ✅ Auth state persists across reloads

**Backend Gates:**
- ✅ Backend starts without errors
- ✅ JWT verification rejects invalid tokens (401)
- ✅ Endpoints extract `user_id` from JWT
- ✅ Unauthorized requests return 403
- ✅ CORS configured correctly

**Database Gates:**
- ✅ Database connection succeeds
- ✅ Migrations run successfully
- ✅ Foreign key constraints enforced
- ✅ Tasks persist in database
- ✅ Users only see their own tasks
- ✅ No orphan records

**Integration Gates:**
- ✅ Signup → Login → Create Task flow works
- ✅ JWT flow end-to-end (issuance → verification)
- ✅ User isolation enforced (User A ≠ User B tasks)
- ✅ Error paths handled (invalid JWT, unauthorized access)

### Phase-3 Gates (🚧 NEW - MUST PASS)

**MCP Server Gates:**
- [ ] Official MCP SDK installed
- [ ] MCP server starts without errors
- [ ] All 5 task tools implemented (add, list, complete, delete, update)
- [ ] Tools use SQLModel for database operations
- [ ] Tools receive user_id as parameter
- [ ] Tools filter queries by user_id
- [ ] Tools are stateless (no in-memory state)
- [ ] Tool invocations return proper responses
- [ ] Tool errors handled gracefully

**AI Agent Gates:**
- [ ] OpenAI Agents SDK installed
- [ ] Agent configured with system prompts
- [ ] Agent can invoke MCP tools
- [ ] Agent receives tool results correctly
- [ ] Agent formulates responses based on tool results
- [ ] Agent handles tool invocation errors
- [ ] Agent does NOT access database directly

**Chat Endpoint Gates:**
- [ ] POST `/api/chat` endpoint operational
- [ ] JWT verification enforced
- [ ] user_id extracted from JWT (not from request body)
- [ ] Conversation history fetched from database
- [ ] User messages stored in database before agent invocation
- [ ] Assistant responses stored in database after agent completion
- [ ] Response returned to client
- [ ] Backend remains stateless (no in-memory conversation state)
- [ ] Error handling (401, 422, 500)

**Database Schema Gates:**
- [ ] Migration 003 created (conversations and messages tables)
- [ ] Migration 003 applied successfully
- [ ] `conversations` table exists with proper schema
- [ ] `messages` table exists with proper schema
- [ ] Foreign keys enforced (user_id, conversation_id)
- [ ] Indexes created (user_id, conversation_id, created_at)
- [ ] CASCADE delete works (user → conversations → messages)
- [ ] No orphan records

**Frontend Chat UI Gates:**
- [ ] OpenAI ChatKit installed
- [ ] Chat page renders without errors
- [ ] ChatKit UI displays correctly
- [ ] Chat API client integrated
- [ ] JWT attached to chat requests
- [ ] Messages sent successfully
- [ ] Responses displayed correctly
- [ ] Conversation history loads
- [ ] Loading states handled
- [ ] Error states handled

**Integration Gates (Phase-3):**
- [ ] Complete chat flow works (user message → agent → MCP tools → response)
- [ ] Conversations persist in database
- [ ] Messages persist in database
- [ ] User isolation enforced (User A cannot see User B's conversations)
- [ ] Tool invocations execute correctly (add task via chat)
- [ ] Tool results reflected in database (task created)
- [ ] Multiple tool invocations in single conversation work
- [ ] Error paths handled (invalid JWT, tool failures, agent errors)
- [ ] Backend stateless verified (restart server, conversation persists)
- [ ] Phase-2 functionality still works (CRUD endpoints unaffected)

---

## Phase-3 Deliverables

**MANDATORY DELIVERABLES FOR PHASE-3:**

### 1. MCP Server
- ✅ Official MCP SDK installed
- ✅ MCP server implementation (`backend/app/mcp/server.py`)
- ✅ Five task tools implemented (`backend/app/mcp/tools.py`):
  - `add_task(user_id, title, description)` - Creates task in database
  - `list_tasks(user_id)` - Retrieves all user's tasks
  - `complete_task(user_id, task_id)` - Toggles task completion
  - `delete_task(user_id, task_id)` - Deletes task from database
  - `update_task(user_id, task_id, title, description)` - Updates task
- ✅ All tools use SQLModel for database operations
- ✅ All tools are stateless
- ✅ Tool invocation tracking

### 2. OpenAI Agent
- ✅ OpenAI Agents SDK installed
- ✅ Agent setup (`backend/app/ai/agent.py`)
- ✅ System prompts (`backend/app/ai/prompts.py`)
- ✅ Agent configured to use MCP tools
- ✅ Agent invocation logic
- ✅ Tool result handling

### 3. Chat Endpoint
- ✅ POST `/api/chat` endpoint (`backend/app/routes/chat.py`)
- ✅ JWT verification
- ✅ Conversation history fetching
- ✅ Message persistence (user and assistant)
- ✅ Agent invocation
- ✅ Stateless implementation
- ✅ Error handling

### 4. Database Schema
- ✅ Migration 003 (`backend/migrations/003_create_chat_tables.sql`)
- ✅ `conversations` table with foreign key to `user`
- ✅ `messages` table with foreign key to `conversations`
- ✅ Proper indexes
- ✅ CASCADE delete constraints

### 5. Frontend Chat UI
- ✅ OpenAI ChatKit installed
- ✅ Chat page (`frontend/app/chat/page.tsx`)
- ✅ ChatKit components
- ✅ Chat API client (`frontend/lib/chat-client.ts`)
- ✅ JWT integration
- ✅ Message display
- ✅ Loading and error states

### 6. Documentation
- ✅ README with setup instructions
- ✅ Specification (`specs/004-ai-chatbot/spec.md`)
- ✅ Implementation plan (`specs/004-ai-chatbot/plan.md`)
- ✅ Task breakdown (`specs/004-ai-chatbot/tasks.md`)
- ✅ PHR records in `history/prompts/004-ai-chatbot/`

### 7. Testing
- ✅ Integration tests for chat flow
- ✅ MCP tool tests
- ✅ Agent invocation tests
- ✅ User isolation tests
- ✅ Stateless backend verification

**NON-DELIVERABLES (OUT OF SCOPE FOR PHASE-3):**
- ❌ Phase-4 features (not yet defined)
- ❌ Advanced agent capabilities (multi-turn reasoning, memory)
- ❌ Conversation branching or editing
- ❌ Real-time streaming responses
- ❌ Voice input/output
- ❌ File attachments
- ❌ Multi-modal capabilities

---

## Spec-Driven Development Rules (COMPREHENSIVE)

### Core Principle

**Spec is law. No coding without approved specifications.**

All development work MUST originate from approved specifications. This is a **BLOCKING REQUIREMENT** with no exceptions.

### When Specs Are Required

**ALWAYS Required:**
- ✅ New features (any size)
- ✅ Architecture changes
- ✅ API modifications
- ✅ Database schema changes
- ✅ Integration with new services
- ✅ Security-related changes
- ✅ Performance optimizations
- ✅ Refactoring that affects multiple files

**NOT Required:**
- ❌ Bug fixes that don't change behavior
- ❌ Typo corrections
- ❌ Documentation updates (non-code)
- ❌ Dependency version updates (patch versions)
- ❌ Code formatting changes

### Mandatory Workflow Sequence

**BLOCKING SEQUENCE - NO DEVIATIONS:**

```
1. /sp.constitution → Define project principles (if not exists)
2. /sp.specify      → Create feature specification
3. /sp.spec.seed    → Seed specification with examples (optional)
4. /sp.plan         → Generate architectural plan
5. /sp.tasks        → Break down into testable tasks
6. Implementation   → Execute tasks via Claude Code
```

**Each step MUST complete before proceeding to the next.**

### Spec Approval Process

**Before Implementation:**
1. Spec MUST be written to `specs/<feature-name>/spec.md`
2. User MUST review and approve the spec
3. Claude MUST wait for explicit approval
4. No coding until approval received

**Approval Indicators:**
- User says: "approved", "looks good", "proceed", "implement this"
- User runs: `/sp.plan` (implies spec approval)
- User explicitly confirms: "yes, go ahead"

**NOT Approval:**
- User asks questions about the spec
- User requests clarifications
- User suggests modifications
- Silence (no response)

### Enforcement Mechanisms

**When User Requests Coding Without Spec:**

Claude MUST:
1. **Stop immediately** - Do not proceed with coding
2. **Warn explicitly** with this message:
   ```
   ⚠️ SPEC-DRIVEN VIOLATION DETECTED

   No approved specification found for this feature.

   This project follows strict spec-driven development.
   All coding MUST originate from approved specifications.

   Required workflow:
   1. Run /sp.specify to create specification
   2. Review and approve the spec
   3. Run /sp.plan to generate implementation plan
   4. Run /sp.tasks to break down into tasks
   5. Then implement via Claude Code

   Would you like to:
   A) Run /sp.specify now (recommended)
   B) Proceed without spec (violates project rules)

   Please choose A or B.
   ```
3. **Wait for explicit choice** - Do not assume or proceed
4. **If user chooses B** - Warn again and document the violation

**When Spec Exists But Not Approved:**

Claude MUST:
1. Check if spec has been reviewed
2. If not reviewed, ask: "Please review the spec at `specs/<feature>/spec.md`. Should I proceed with planning?"
3. Wait for approval before running `/sp.plan`

**When Implementation Deviates from Spec:**

Claude MUST:
1. Stop immediately
2. Warn: "This implementation deviates from the approved spec"
3. Ask: "Should I update the spec first, or proceed with deviation?"
4. Document the deviation in PHR

### Spec Quality Requirements

**Every spec MUST include:**
- ✅ Clear problem statement
- ✅ Success criteria (measurable)
- ✅ User stories or use cases
- ✅ API contracts (if applicable)
- ✅ Data model (if applicable)
- ✅ Security considerations
- ✅ Error handling requirements
- ✅ Non-functional requirements
- ✅ Out-of-scope items (what NOT to build)

**Spec MUST NOT include:**
- ❌ Implementation details (that's for plan.md)
- ❌ Code snippets (that's for implementation)
- ❌ Technology choices (unless architecturally significant)

### Spec-to-Implementation Traceability

**Every implementation MUST:**
- ✅ Reference the spec it implements
- ✅ Reference specific user stories or requirements
- ✅ Include spec ID in commit messages
- ✅ Create PHR linking to spec

**Format:**
```
Implements: specs/004-ai-chatbot/spec.md
User Story: US-3 (Agent invokes MCP tools)
Task: T-012 (Implement MCP server)
```

### Spec Modification Rules

**When Requirements Change:**

1. **Stop implementation** if in progress
2. **Update spec first** - Never update code before spec
3. **Document changes** in spec with version/date
4. **Get approval** for modified spec
5. **Update plan and tasks** to reflect changes
6. **Resume implementation** with updated artifacts

**Spec Versioning:**
```markdown
## Version History
- v1.0.0 (2026-02-08): Initial specification
- v1.1.0 (2026-02-09): Added real-time streaming requirement
- v1.2.0 (2026-02-10): Removed voice input (out of scope)
```

### Deviation Handling

**If Implementation Must Deviate:**

1. **Document reason** - Why is deviation necessary?
2. **Get approval** - User must explicitly approve
3. **Update spec** - Reflect the deviation
4. **Create ADR** - If architecturally significant
5. **Update plan/tasks** - Keep artifacts in sync

**Acceptable Reasons for Deviation:**
- ✅ Technical constraint discovered during implementation
- ✅ Security vulnerability found in spec approach
- ✅ Performance issue with spec approach
- ✅ Library/API limitation discovered

**NOT Acceptable Reasons:**
- ❌ "Easier to implement differently"
- ❌ "I prefer this approach"
- ❌ "Forgot what the spec said"
- ❌ "Spec was too detailed"

### Spec Workflow Commands

**Available Commands:**

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/sp.constitution` | Define project principles | Once per project |
| `/sp.specify` | Create feature specification | Before every feature |
| `/sp.spec.seed` | Add examples to spec | After spec draft |
| `/sp.clarify` | Ask clarifying questions | When spec unclear |
| `/sp.plan` | Generate implementation plan | After spec approval |
| `/sp.tasks` | Break down into tasks | After plan approval |
| `/sp.analyze` | Check artifact consistency | After task generation |
| `/sp.adr` | Document architecture decision | When significant decision made |
| `/sp.phr` | Record prompt history | After implementation work |

### Compliance Verification

**Before Starting Implementation, Verify:**
- [ ] Spec exists in `specs/<feature-name>/spec.md`
- [ ] Spec has been reviewed by user
- [ ] User has explicitly approved spec
- [ ] Plan exists in `specs/<feature-name>/plan.md`
- [ ] Tasks exist in `specs/<feature-name>/tasks.md`
- [ ] All artifacts are consistent
- [ ] No unresolved questions in spec

**If ANY checkbox is unchecked, STOP and complete missing steps.**

### Consequences of Violations

**If Spec-Driven Rules Are Violated:**

1. **Implementation may be rejected** - User may request rewrite
2. **Technical debt accumulates** - Undocumented decisions
3. **Team confusion** - No single source of truth
4. **Maintenance burden** - Future developers don't know intent
5. **Scope creep** - Features added without planning
6. **Quality issues** - Missing requirements not caught

**Therefore: Spec-driven development is NON-NEGOTIABLE.**

### Integration with Phase-3

**For AI Chatbot (Phase-3):**

The spec-driven workflow is **MANDATORY** and called the "Agentic Dev Stack":

1. `/sp.specify` - Create AI chatbot specification
2. `/sp.plan` - Generate MCP + Agent + Chat endpoint plan
3. `/sp.tasks` - Break down into 6 sub-phases
4. Implement - Execute tasks strictly per spec

**No manual coding allowed. No deviations from spec.**

---

## PHR/ADR Workflow

### Prompt History Records (PHR)

**Purpose:** Record every user input and Claude's response for learning and traceability.

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**PHR Creation Process:**

1. **Detect stage:** constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2. **Generate title:** 3–7 words; create a slug for the filename

3. **Resolve route (all under `history/prompts/`):**
   - `constitution` → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/`
   - `general` → `history/prompts/general/`

4. **Read PHR template:**
   - `.specify/templates/phr-template.prompt.md`
   - `templates/phr-template.prompt.md`

5. **Fill ALL placeholders:**
   - ID, TITLE, STAGE, DATE_ISO, SURFACE="agent"
   - MODEL, FEATURE, BRANCH, USER
   - COMMAND, LABELS
   - LINKS: SPEC/TICKET/ADR/PR
   - FILES_YAML: created/modified files
   - TESTS_YAML: tests run/added
   - PROMPT_TEXT: full user input (verbatim)
   - RESPONSE_TEXT: key assistant output

6. **Write file:** Use agent file tools (Write/Edit)

7. **Validate:**
   - No unresolved placeholders
   - Title, stage, dates match
   - PROMPT_TEXT complete (not truncated)
   - File exists and readable

8. **Report:** ID, path, stage, title

**Skip PHR only for `/sp.phr` itself.**

---

### Architecture Decision Records (ADR)

**Purpose:** Document architecturally significant decisions with reasoning and tradeoffs.

**When to suggest ADRs:**

After design/architecture work, test for significance:
- **Impact:** Long-term consequences? (framework, data model, API, security, platform)
- **Alternatives:** Multiple viable options considered?
- **Scope:** Cross-cutting and influences system design?

**If ALL true, suggest:**
```
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`
```

**Wait for user consent. NEVER auto-create ADRs.**

**Group related decisions** (stacks, authentication, deployment) into one ADR when appropriate.

---

## Execution Contract

**For every user request, Claude MUST:**

1. **Confirm surface and success criteria** (one sentence)
   - Example: "Implementing JWT verification middleware in FastAPI backend. Success: backend rejects invalid tokens with 401."

2. **List constraints, invariants, non-goals**
   - Constraints: Must use Better Auth JWT format
   - Invariants: User isolation enforced
   - Non-goals: Not implementing refresh tokens yet

3. **Produce artifact with acceptance checks**
   - Code with inline comments for critical logic
   - Checkboxes for validation steps

4. **Add follow-ups and risks** (max 3 bullets)
   - Follow-up: Test with expired JWT
   - Risk: JWT secret must be in `.env`

5. **Create PHR** in appropriate subdirectory under `history/prompts/`

6. **Surface ADR suggestion** if architecturally significant decision detected

---

## Minimum Acceptance Criteria

**Every implementation MUST include:**
- ✅ Clear, testable acceptance criteria
- ✅ Explicit error paths and constraints stated
- ✅ Smallest viable change; no unrelated edits
- ✅ Code references to modified/inspected files (e.g., `app/main.py:45-67`)

---

## Philosophy

### Phase-2 Principles (✅ CONTINUE ENFORCING)

**Spec is law.**
No coding without approved specifications. The spec workflow is non-negotiable.

**JWT is truth.**
User identity derives exclusively from verified JWT claims. No other source is trusted.

**Database is source of state.**
All state persists in PostgreSQL. No mocks, no in-memory storage, no shortcuts.

**No shortcuts.**
Partial implementations and patch fixes are prohibited. Fix root causes only.

**No patch fixes.**
Address the underlying issue, not the symptom.

### Phase-3 Principles (🚧 NEW - CRITICAL)

**Agentic Dev Stack is mandatory.**
All Phase-3 development MUST follow the workflow:
1. `/sp.specify` - Write specification
2. `/sp.plan` - Generate implementation plan
3. `/sp.tasks` - Break down into tasks
4. Implement via Claude Code
5. No manual coding allowed
6. No deviations from specification

**MCP tools are the gatekeepers.**
All task database mutations MUST flow through MCP tools. The agent decides, MCP executes.

**Agent is the orchestrator, not the executor.**
The AI agent analyzes intent and selects tools. It NEVER performs database operations directly.

**Stateless backend is non-negotiable.**
The FastAPI server holds NO state. All conversation state persists in the database. Server restarts must not lose data.

**Phase-2 is sacred.**
Phase-2 code is the stable foundation. Modifications are prohibited unless absolutely necessary for Phase-3 integration.

**Official SDKs only.**
- OpenAI Agents SDK (official)
- MCP SDK (official)
- OpenAI ChatKit (official)
No custom implementations or alternative libraries.

**Separation of concerns.**
- Frontend: UI and user interaction
- Backend: Orchestration and JWT verification
- AI Agent: Intent analysis and tool selection
- MCP Tools: Database mutations only
- Database: State persistence

Each layer has a single responsibility. No layer crosses boundaries.

---

## Tone & Enforcement

**Strict engineering discipline.**

All rules in this document are **BLOCKING REQUIREMENTS**. When violations are detected, Claude MUST:
1. Warn the user with specific rule reference
2. Ask for confirmation to proceed
3. Wait for explicit approval before continuing

**Phase-2 Violation Example:**
```
⚠️ Rule violation detected: Core Rules > Identity & Authentication
   "Frontend MUST NEVER send user_id manually"

The current approach sends user_id in the request body.
This violates user isolation principles.

Correct approach: Backend extracts user_id from JWT claims.

Proceed with violation, or fix the approach?
```

**Phase-3 Violation Examples:**

**Example 1: Agent accessing database directly**
```
⚠️ Rule violation detected: Phase-3 Rules > MCP Architecture
   "Agent MUST NEVER access database directly"

The current implementation has the agent performing SQLModel queries.
This violates the MCP architecture principle.

Correct approach: Agent invokes MCP tools, which perform database operations.

Proceed with violation, or fix the approach?
```

**Example 2: Coding without specification**
```
⚠️ Rule violation detected: Mandatory Spec Workflow
   "All development MUST follow Agentic Dev Stack workflow"

No approved specification detected for AI chatbot feature.

Required workflow:
1. Run /sp.specify to create specification
2. Run /sp.plan to generate implementation plan
3. Run /sp.tasks to break down into tasks
4. Then implement via Claude Code

Proceed without specification, or run /sp.specify first?
```

**Example 3: Stateful backend implementation**
```
⚠️ Rule violation detected: Phase-3 Rules > Stateless Backend
   "FastAPI server MUST remain stateless"

The current implementation stores conversation state in memory.
This violates the stateless backend principle.

Correct approach: Store all conversation state in database.

Proceed with violation, or fix the approach?
```

**Example 4: Modifying Phase-2 code unnecessarily**
```
⚠️ Rule violation detected: Phase-3 Rules > Phase-2 Stability
   "DO NOT modify Phase-2 CRUD endpoints unless absolutely necessary"

The current change modifies the existing /api/tasks endpoint.
Phase-2 code is the stable foundation.

Is this modification absolutely necessary for Phase-3?
If not, implement Phase-3 features without modifying Phase-2 code.

Proceed with modification, or find alternative approach?
```

---

## Human as Tool Strategy

Claude is not expected to solve every problem autonomously. Claude MUST invoke the user for input when encountering situations requiring human judgment.

**Invocation Triggers:**

1. **Ambiguous Requirements:** Ask 2-3 targeted clarifying questions before proceeding
2. **Unforeseen Dependencies:** Surface dependencies and ask for prioritization
3. **Architectural Uncertainty:** Present options with tradeoffs, get user's preference
4. **Completion Checkpoint:** Summarize what was done, confirm next steps

---

## Default Policies

### General Policies (Phase-2 + Phase-3)

- Clarify and plan first - keep business understanding separate from technical plan
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing
- Never hardcode secrets or tokens; use `.env` and provide `.env.example`
- Prefer the smallest viable diff; do not refactor unrelated code
- Cite existing code with code references (`file:line-start:line-end`)
- Propose new code in fenced blocks
- Keep reasoning private; output only decisions, artifacts, and justifications

### Phase-3 Specific Policies

**Agentic Dev Stack Enforcement:**
- When user requests Phase-3 implementation without specs, MUST warn and suggest `/sp.specify`
- NEVER proceed with coding before specification approval
- ALWAYS follow the workflow: specify → plan → tasks → implement

**MCP Architecture Enforcement:**
- When implementing task operations, ALWAYS route through MCP tools
- NEVER allow agent to access database directly
- NEVER allow chat endpoint to mutate task data directly
- ALL task mutations MUST be in MCP tool functions

**Stateless Backend Enforcement:**
- When implementing chat logic, ALWAYS persist state in database
- NEVER store conversation state in memory
- NEVER use global variables or class-level state
- ALWAYS fetch conversation history from database on each request

**Phase-2 Protection:**
- When modifying existing code, ALWAYS check if it's Phase-2 code
- NEVER modify Phase-2 code unless absolutely necessary
- If modification needed, ask user for confirmation first
- ALWAYS maintain backward compatibility with Phase-2

**Technology Stack Enforcement:**
- When user suggests alternative libraries, MUST enforce official SDKs
- OpenAI Agents SDK (official) - no alternatives
- MCP SDK (official) - no alternatives
- OpenAI ChatKit (official) - no alternatives
- If user insists on alternatives, warn about violation and get explicit approval

---

## Phase-3 Quick Reference

**What is Phase-3?**
AI-powered conversational interface for task management using OpenAI Agents SDK and MCP.

**Key Components:**
1. **MCP Server** - Task tools (add, list, complete, delete, update)
2. **OpenAI Agent** - Intent analysis and tool selection
3. **Chat Endpoint** - POST `/api/chat` with JWT verification
4. **Database** - conversations and messages tables
5. **Frontend** - OpenAI ChatKit UI

**Critical Rules:**
- ✅ MCP tools are the ONLY components that mutate task data
- ❌ Agent NEVER accesses database directly
- ✅ Backend MUST remain stateless
- ❌ Phase-2 code is stable - do not modify
- ✅ Follow Agentic Dev Stack workflow (specify → plan → tasks → implement)

**Data Flow:**
```
User Message → Chat Endpoint → Fetch History → Store Message →
Invoke Agent → Agent Selects Tools → MCP Tools Execute →
Store Response → Return to User
```

**User Isolation:**
- user_id from JWT (never from request)
- All queries filter by user_id
- Conversations belong to users
- Messages belong to conversations

**Technology Stack:**
- Frontend: OpenAI ChatKit
- Backend: FastAPI + OpenAI Agents SDK + SQLModel ORM
- MCP: Official MCP SDK
- Database: PostgreSQL (Neon)
- Auth: Better Auth JWT + Prisma (auth tables only)
- ORM: Prisma (Better Auth), SQLModel (application data)

---

**End of Root CLAUDE.md (Phase-3)**

**Current Status:**
- Phase-2: ✅ Complete (Frontend, Auth, Backend API, Database)
- Phase-3: 🚧 In Progress (AI Chatbot)

**Next Steps:**
1. Run `/sp.specify` to create Phase-3 specification
2. Run `/sp.plan` to generate implementation plan
3. Run `/sp.tasks` to break down into tasks
4. Implement AI chatbot via Claude Code following Agentic Dev Stack
5. Test complete chat flow with integration tests
6. Verify Phase-2 functionality remains intact

**Remember:**
- Spec-driven development is mandatory
- MCP tools are the gatekeepers for task mutations
- Backend must remain stateless
- Phase-2 is the stable foundation - protect it
