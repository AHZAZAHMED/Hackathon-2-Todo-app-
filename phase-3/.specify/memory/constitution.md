<!--
Sync Impact Report:
- Version: 1.0.0 → 2.0.0 (MAJOR: Fundamental architectural changes for Phase-3)
- Modified principles:
  - I. Spec-Driven Development → Enhanced with Agentic Dev Stack enforcement
  - VI. Clear Separation of Layers → Expanded to include AI Agent and MCP layers
- Added sections:
  - VII. Stateless Backend Architecture (NEW)
  - VIII. MCP-Only Task Mutations (NEW)
  - IX. AI Agent Orchestration (NEW)
  - Phase-3 Architecture Law (NEW)
  - Phase-3 Quality Gates (NEW)
- Removed sections: None (Phase-2 principles retained as foundation)
- Templates requiring updates:
  ✅ plan-template.md: Constitution Check section aligns with new principles
  ✅ spec-template.md: User story prioritization aligns with spec-driven workflow
  ✅ tasks-template.md: Phase structure aligns with workflow law
- Follow-up TODOs: None
-->

# Hackathon II Phase-3 Todo AI Chatbot Constitution

## Core Principles

### I. Spec-First Development (NON-NEGOTIABLE)

Every behavior MUST originate from approved specifications. No coding is permitted before `/sp.specify` approval.

**Mandatory Workflow (Agentic Dev Stack)**:
1. `/sp.constitution` - Define project principles
2. `/sp.specify` - Create feature specification
3. `/sp.plan` - Generate architectural plan
4. `/sp.tasks` - Break down into testable tasks
5. Implementation - Execute tasks via Claude Code

**Manual coding is forbidden.**

**Rules**:
- No implementation before specification approval
- All features MUST have corresponding spec, plan, and tasks artifacts
- Implementation MUST reference task IDs for traceability
- Deviations from spec require explicit approval and spec update

**Rationale**: Prevents scope creep, ensures alignment, creates traceable decisions, eliminates ad-hoc implementations that violate architecture, and enforces disciplined development workflow.

### II. Stateless Backend Architecture (NON-NEGOTIABLE)

FastAPI server MUST be stateless. All conversation and application state MUST persist in Neon PostgreSQL.

**Rules**:
- NO in-memory conversation state
- NO global variables or class-level state
- Fetch conversation history from database on each request
- Store all messages (user and assistant) in database
- Server restarts MUST NOT lose data
- Each request MUST be independent and deterministic

**Rationale**: Ensures horizontal scalability, enables zero-downtime deployments, prevents data loss, and provides production-grade reliability.

### III. AI-Driven Task Management Through MCP Tools Only (NON-NEGOTIABLE)

All task database mutations MUST flow through MCP tools. The AI agent decides intent, MCP tools execute operations.

**Rules**:
- MCP tools are the ONLY components allowed to perform task database mutations
- AI Agent MUST NEVER access database directly
- Chat endpoint MUST NEVER write task data directly
- ALL task creation, updates, deletions, and status changes MUST occur inside MCP tools
- MCP tools MUST use SQLModel for database operations
- MCP tools MUST be stateless
- MCP tools MUST receive user_id as parameter (from JWT)

**Rationale**: Enforces clear separation of concerns, prevents data corruption, ensures consistent business logic, and provides single source of truth for task operations.

### IV. JWT-Only Identity (NON-NEGOTIABLE)

JWT is the SOLE authority for user identity. All other identity sources are prohibited.

**Rules**:
- Backend MUST extract `user_id` from verified JWT claims
- Frontend MUST NEVER send `user_id` manually in request body or parameters
- Backend MUST NEVER trust client-provided `user_id`
- All authentication state derives from JWT tokens issued by Better Auth
- MCP tools MUST receive user_id from JWT (never from client)

**Rationale**: Prevents identity spoofing, ensures consistent authentication across all endpoints, enforces security at the token level, and maintains user isolation.

### V. Database as Single Source of Truth (NON-NEGOTIABLE)

All application state MUST persist in PostgreSQL. Mock data and in-memory storage are prohibited.

**Rules**:
- PostgreSQL (Neon Serverless) is the single source of truth
- `user` table managed by Better Auth (Prisma)
- `tasks` table with `user_id` foreign key (SQLModel)
- `conversations` table with `user_id` foreign key (SQLModel)
- `messages` table with `conversation_id` foreign key (SQLModel)
- Foreign key constraints enforced (ON DELETE CASCADE)
- Indexes on foreign keys for query performance
- Migrations required for all schema changes
- No orphan records permitted

**Rationale**: Ensures data durability, enables multi-user isolation, prevents data loss, provides production-grade reliability, and supports stateless backend architecture.

### VI. Production-Grade Quality (NON-NEGOTIABLE)

All implementations MUST meet production standards. Shortcuts, partial implementations, placeholders, and mocks are prohibited.

**Rules**:
- TypeScript strict mode required
- Tailwind CSS officially configured (not CDN)
- Environment variables mandatory for all secrets
- Centralized API client for all backend communication
- Error handling for all failure paths (401, 403, 422, 500)
- CORS properly configured
- Connection pooling for database
- Structured logging for observability
- No TODO comments in production code
- No placeholder implementations

**Rationale**: Prevents technical debt accumulation, ensures maintainability, delivers reliable systems from day one, and maintains professional code quality.

### VII. Root-Cause Engineering (NON-NEGOTIABLE)

All fixes MUST address root causes, not symptoms. Patch fixes and workarounds are prohibited.

**Rules**:
- Identify the underlying issue before implementing a fix
- No temporary solutions that defer the real problem
- Document the root cause in commit messages
- Validate that the fix prevents recurrence
- No "quick fixes" that introduce technical debt

**Rationale**: Prevents bug accumulation, reduces maintenance burden, builds system understanding, and maintains code quality over time.

### VIII. Clear Separation of Layers (NON-NEGOTIABLE)

Frontend, authentication, backend, AI agent, MCP tools, and database layers MUST remain independent with well-defined contracts.

**Rules**:
- **Frontend**: Next.js 16+ App Router, TypeScript, Tailwind CSS, OpenAI ChatKit
- **Authentication**: Better Auth with JWT tokens
- **Backend**: FastAPI with Python (orchestration only)
- **AI Agent**: OpenAI Agents SDK (intent analysis and tool selection)
- **MCP Tools**: Official MCP SDK (database mutations only)
- **Database**: PostgreSQL (Neon Serverless)
- Each layer has its own CLAUDE.md with layer-specific rules
- No cross-layer logic bleeding
- API contracts define all inter-layer communication
- Agent NEVER accesses database directly
- Backend NEVER mutates task data directly

**Rationale**: Enables independent testing, parallel development, technology substitution, clear responsibility boundaries, and maintainable architecture.

### IX. Deterministic Behavior (NON-NEGOTIABLE)

Each request MUST be independent and produce consistent results given the same inputs.

**Rules**:
- No request-to-request state dependencies
- All context fetched from database on each request
- No side effects that affect subsequent requests
- Idempotent operations where possible
- Predictable error handling

**Rationale**: Enables reliable testing, simplifies debugging, supports horizontal scaling, and ensures production stability.

## Architecture Law

### Phase-2 Foundation (STABLE - DO NOT MODIFY)

**Stack Requirements**:
- **Frontend**: Next.js 16+ App Router + TypeScript + Tailwind CSS
- **Authentication**: Better Auth + JWT + Prisma (auth tables only)
- **Backend**: FastAPI + Python
- **Database**: PostgreSQL (Neon Serverless)
- **ORM**: Prisma (Better Auth only), SQLModel (application data)

**Component Interaction Flow**:
```
User → Frontend (Next.js) → Better Auth (JWT) → Backend (FastAPI) → PostgreSQL (Neon)
```

**Authentication Flow**:
1. Better Auth issues JWT on login
2. Frontend stores JWT securely (httpOnly cookie or secure storage)
3. Frontend API client attaches JWT to all requests automatically
4. Backend verifies JWT signature
5. Backend extracts `user_id` from JWT claims
6. Backend uses `user_id` for database queries

**User Isolation**:
- User identity derived ONLY from JWT claims
- Database enforces foreign key constraints: `tasks.user_id → users.id`
- All queries MUST filter by authenticated `user_id`
- Users can ONLY access their own resources

### Phase-3 Architecture (NEW - AI CHATBOT)

**Fixed Technology Stack (NO SUBSTITUTIONS PERMITTED)**:
- **Frontend**: OpenAI ChatKit (official UI library)
- **Backend**: Python FastAPI (existing)
- **AI Framework**: OpenAI Agents SDK (official SDK)
- **MCP Server**: Official MCP SDK
- **ORM**: SQLModel (Phase-3 does NOT use Prisma)
- **Database**: Neon Serverless PostgreSQL (existing)
- **Authentication**: Better Auth JWT (existing)

**Complete System Flow**:
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
│  - add_task(user_id, title, description)                     │
│  - list_tasks(user_id)                                       │
│  - complete_task(user_id, task_id)                           │
│  - delete_task(user_id, task_id)                             │
│  - update_task(user_id, task_id, title, description)         │
│                                                              │
│  ONLY layer allowed to mutate task data                      │
└────────────────────┬────────────────────────────────────────┘
                     │ SQLModel operations
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Database (PostgreSQL - Neon)                               │
│  Tables:                                                     │
│  - user (Better Auth - Prisma)                               │
│  - tasks (Phase-2 - SQLModel)                                │
│  - conversations (Phase-3 - SQLModel)                        │
│  - messages (Phase-3 - SQLModel)                             │
└─────────────────────────────────────────────────────────────┘
```

**Chat Flow (MANDATORY SEQUENCE)**:
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

**Critical Architectural Rules**:
1. FastAPI server MUST be stateless
2. Conversation state MUST persist in Neon PostgreSQL
3. AI Agent MUST NOT access database directly
4. All task operations MUST go through MCP tools
5. MCP tools MUST be stateless and persist changes to database
6. user_id MUST ONLY come from Better Auth JWT
7. Frontend MUST communicate exclusively via POST /api/chat
8. No in-memory storage allowed
9. No global state
10. No Phase-4 features

## Workflow Law

**Mandatory Sequence** (BLOCKING):

```
/sp.specify → /sp.plan → /sp.tasks → implementation
```

**No deviation permitted. Manual coding is forbidden.**

**Enforcement**:
- When coding is requested without approved specs, Claude MUST warn and ask for confirmation
- All features MUST have corresponding spec, plan, and tasks artifacts
- Implementation MUST reference task IDs for traceability
- Deviations from spec require explicit approval and spec update

**Agentic Dev Stack Workflow**:
1. **Specification** (`/sp.specify`) - Define what to build
2. **Planning** (`/sp.plan`) - Design how to build it
3. **Task Breakdown** (`/sp.tasks`) - Break into executable tasks
4. **Implementation** (Claude Code) - Execute tasks strictly per spec

## Database Rules

**Provider**: PostgreSQL (Neon Serverless)

**ORM Strategy (CRITICAL)**:
- **Prisma**: Used ONLY for Better Auth tables (user, session, account, verification)
  - Managed by Better Auth on frontend
  - Backend does NOT use Prisma
  - Phase-3 does NOT need Prisma
- **SQLModel**: Used for ALL application tables (tasks, conversations, messages)
  - SQLAlchemy-based ORM
  - Used in backend for all CRUD operations
  - Used by MCP tools for database mutations
  - Phase-3 uses SQLModel exclusively for new tables

**Schema Requirements**:

### Phase-2 Tables (EXISTING - DO NOT MODIFY)

**`user` table**:
- Managed by Better Auth via Prisma (frontend)
- Primary key: `id` (TEXT - CUID)
- Contains: email, name, emailVerified, createdAt, updatedAt
- ORM: Prisma (frontend only, read-only from backend perspective)

**`tasks` table**:
- Managed by backend via SQLModel
- Primary key: `id` (SERIAL - INTEGER)
- Foreign key: `user_id` references `user.id` (ON DELETE CASCADE)
- Fields: `title`, `description`, `completed`, `created_at`, `updated_at`
- Indexes: Primary key, user_id, completed
- ORM: SQLModel (backend only)

### Phase-3 Tables (NEW - TO BE CREATED)

**`conversations` table**:
- Managed by backend via SQLModel
- Primary key: `id` (SERIAL or UUID)
- Foreign key: `user_id` references `user.id` (ON DELETE CASCADE)
- Fields: `user_id`, `title`, `created_at`, `updated_at`
- Indexes: Primary key, user_id, created_at
- ORM: SQLModel (backend only)

**`messages` table**:
- Managed by backend via SQLModel
- Primary key: `id` (SERIAL or UUID)
- Foreign key: `conversation_id` references `conversations.id` (ON DELETE CASCADE)
- Fields: `conversation_id`, `role`, `content`, `tool_calls`, `tool_results`, `created_at`
- Indexes: Primary key, conversation_id, created_at
- ORM: SQLModel (backend only)

**Constraints**:
- NO orphan records (foreign key enforced)
- Migrations required for all schema changes
- NO in-memory storage
- All queries MUST filter by authenticated `user_id`
- Conversations belong to users (user_id FK)
- Messages belong to conversations (conversation_id FK)
- CASCADE delete: user deleted → conversations deleted → messages deleted

**MCP Tool Database Access**:
- MCP tools MUST use SQLModel for all database operations
- MCP tools MUST receive user_id as parameter
- MCP tools MUST filter queries by user_id
- MCP tools MUST NEVER trust client-provided user_id
- All task mutations MUST occur inside MCP tools
- Agent MUST NEVER access database directly

**Connection**:
- Use environment variable: `DATABASE_URL`
- Connection pooling recommended
- Handle connection errors gracefully
- Same database connection for Phase-2 and Phase-3 tables

## Quality Gates

**BLOCKING REQUIREMENTS**: All MUST pass before proceeding to next phase.

### Phase-2 Gates (COMPLETE - VERIFIED)

**Frontend Gates**:
- [x] `npm run dev` succeeds without errors
- [x] Tailwind styles render correctly
- [x] TypeScript compiles with strict mode
- [x] No console errors in browser
- [x] Centralized API client in place

**Authentication Gates**:
- [x] JWT issued on login
- [x] JWT stored securely
- [x] JWT attached to requests automatically
- [x] Auth state persists across reloads

**Backend Gates**:
- [x] Backend starts without errors
- [x] JWT verification rejects invalid tokens (401)
- [x] Endpoints extract `user_id` from JWT
- [x] Unauthorized requests return 403
- [x] CORS configured correctly

**Database Gates**:
- [x] Database connection succeeds
- [x] Migrations run successfully
- [x] Foreign key constraints enforced
- [x] Tasks persist in database
- [x] Users only see their own tasks
- [x] No orphan records

**Integration Gates**:
- [x] Signup → Login → Create Task flow works
- [x] JWT flow end-to-end (issuance → verification)
- [x] User isolation enforced (User A ≠ User B tasks)
- [x] Error paths handled (invalid JWT, unauthorized access)

### Phase-3 Gates (NEW - MUST PASS)

**MCP Server Gates**:
- [ ] Official MCP SDK installed
- [ ] MCP server starts without errors
- [ ] All 5 task tools implemented (add, list, complete, delete, update)
- [ ] Tools use SQLModel for database operations
- [ ] Tools receive user_id as parameter
- [ ] Tools filter queries by user_id
- [ ] Tools are stateless (no in-memory state)
- [ ] Tool invocations return proper responses
- [ ] Tool errors handled gracefully

**AI Agent Gates**:
- [ ] OpenAI Agents SDK installed
- [ ] Agent configured with system prompts
- [ ] Agent can invoke MCP tools
- [ ] Agent receives tool results correctly
- [ ] Agent formulates responses based on tool results
- [ ] Agent handles tool invocation errors
- [ ] Agent does NOT access database directly

**Chat Endpoint Gates**:
- [ ] POST `/api/chat` endpoint operational
- [ ] JWT verification enforced
- [ ] user_id extracted from JWT (not from request body)
- [ ] Conversation history fetched from database
- [ ] User messages stored in database before agent invocation
- [ ] Assistant responses stored in database after agent completion
- [ ] Response returned to client
- [ ] Backend remains stateless (no in-memory conversation state)
- [ ] Error handling (401, 422, 500)

**Database Schema Gates**:
- [ ] Migration 003 created (conversations and messages tables)
- [ ] Migration 003 applied successfully
- [ ] `conversations` table exists with proper schema
- [ ] `messages` table exists with proper schema
- [ ] Foreign keys enforced (user_id, conversation_id)
- [ ] Indexes created (user_id, conversation_id, created_at)
- [ ] CASCADE delete works (user → conversations → messages)
- [ ] No orphan records

**Frontend Chat UI Gates**:
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

**Integration Gates (Phase-3)**:
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

## Key Standards

### Configuration Standards

- **TypeScript**: Strict mode required (`"strict": true` in tsconfig.json)
- **Tailwind CSS**: Official configuration required (not CDN)
- **Environment Variables**: Mandatory for all secrets, API keys, database URLs
- **`.env` Files**: NEVER commit to version control; provide `.env.example` with placeholders

### API Standards

- **Centralized Client**: All API calls through `lib/api-client.ts` or equivalent
- **JWT Attachment**: Automatic via centralized client
- **Error Handling**: Backend MUST return proper HTTP status codes:
  - 401: Invalid/missing JWT
  - 403: Unauthorized resource access
  - 422: Validation errors
  - 500: Server errors
- **CORS**: Properly configured for frontend origin

### Code Quality Standards

- **No Partial Implementations**: Features MUST be complete before merging
- **No Patch Fixes**: Address root causes only
- **Smallest Viable Change**: No unrelated refactoring
- **Code References**: Use `file:line-start:line-end` format
- **Testability**: All changes MUST be testable
- **No Placeholders**: No TODO comments or mock implementations in production code

### Development Order Standards

**BLOCKING SEQUENCE**: Each phase MUST pass quality gates before proceeding.

**Phase-2 (COMPLETE)**:
1. Frontend Implementation
2. Authentication
3. Backend API
4. Database Schema + Integration
5. Full Integration Testing

**Phase-3 (IN PROGRESS)**:
1. Database Schema for Chat (conversations, messages tables)
2. MCP Server Implementation (5 task tools)
3. OpenAI Agent Integration
4. Chat Endpoint (POST /api/chat)
5. Frontend Chat UI (OpenAI ChatKit)
6. Integration Testing (complete chat flow)

## Governance

### Amendment Procedure

1. **Proposal**: Document proposed change with rationale and impact analysis
2. **Review**: Assess impact on existing specs, plans, and implementations
3. **Approval**: Explicit user approval required
4. **Migration**: Update all dependent templates and artifacts
5. **Version Bump**: Follow semantic versioning (MAJOR.MINOR.PATCH)

### Versioning Policy

- **MAJOR**: Backward-incompatible governance/principle removals or redefinitions
- **MINOR**: New principle/section added or materially expanded guidance
- **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements

### Compliance Requirements

- All PRs/reviews MUST verify compliance with constitution principles
- Violations MUST be justified in `Complexity Tracking` section of plan.md
- Constitution supersedes all other practices and conventions
- Claude Code MUST enforce constitution rules with warnings and confirmation prompts

### Runtime Guidance

- Root CLAUDE.md: Project-wide rules (this constitution + execution contract)
- `frontend/CLAUDE.md`: Next.js, Better Auth, UI-specific rules, ChatKit integration
- `backend/CLAUDE.md`: FastAPI, JWT verification, database-specific rules, AI/MCP integration
- Claude Code reads the **closest** CLAUDE.md first to prevent cross-stack confusion

**Version**: 2.0.0 | **Ratified**: 2026-02-05 | **Last Amended**: 2026-02-09
