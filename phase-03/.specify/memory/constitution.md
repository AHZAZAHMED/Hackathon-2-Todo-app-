<!--
Sync Impact Report:
- Version: 1.0.0 → 1.1.0 (Phase-3 AI Chatbot principles added)
- Modified principles:
  - Principle VI: Expanded to include Phase-3 layers (AI Agent, MCP)
- Added sections:
  - Principle VII: MCP-Only Database Mutations (NEW)
  - Principle VIII: Stateless Backend Architecture (NEW)
  - Principle IX: AI Agent Orchestration (NEW)
  - Phase-3 Architecture Law section
  - Phase-3 Database tables (conversations, messages)
  - Phase-3 Quality Gates
  - Forbidden Practices section
- Removed sections: None (Phase-2 preserved)
- Templates requiring updates:
  ✅ plan-template.md: Add Phase-3 MCP architecture checks
  ✅ spec-template.md: Add Phase-3 success criteria templates
  ✅ tasks-template.md: Add Phase-3 task categories (MCP, Agent, Chat)
  ✅ CLAUDE.md: Already updated with Phase-3 rules
- Follow-up TODOs: None
-->

# Hackathon II Phase-3 Todo AI Chatbot Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

Every behavior MUST originate from approved specifications. No coding is permitted before `/sp.specify` approval.

**Mandatory Workflow**:
1. `/sp.constitution` - Define project principles
2. `/sp.specify` - Create feature specification
3. `/sp.spec.seed` - Seed specification with examples
4. `/sp.plan` - Generate architectural plan
5. `/sp.tasks` - Break down into testable tasks
6. Implementation - Execute tasks via Claude Code only

**Rationale**: Prevents scope creep, ensures alignment, creates traceable decisions, and eliminates ad-hoc implementations that violate architecture.

### II. JWT-Only Identity (NON-NEGOTIABLE)

JWT is the SOLE authority for user identity. All other identity sources are prohibited.

**Rules**:
- Backend MUST extract `user_id` from verified JWT claims
- Frontend MUST NEVER send `user_id` manually in request body or parameters
- Backend MUST NEVER trust client-provided `user_id`
- All authentication state derives from JWT tokens issued by Better Auth
- Chat endpoint MUST extract `user_id` from JWT for conversation isolation

**Rationale**: Prevents identity spoofing, ensures consistent authentication across all endpoints, and enforces security at the token level.

### III. Database-Backed Persistence (NON-NEGOTIABLE)

All application state MUST persist in PostgreSQL. Mock data and in-memory storage are prohibited.

**Rules**:
- PostgreSQL (Neon Serverless) is the single source of truth
- `user` table managed by Better Auth via Prisma
- `tasks` table with `user_id` foreign key (SQLModel)
- `conversations` table with `user_id` foreign key (SQLModel)
- `messages` table with `conversation_id` foreign key (SQLModel)
- Foreign key constraints enforced (ON DELETE CASCADE)
- Indexes on `user_id` and `conversation_id` for query performance
- Migrations required for all schema changes
- No orphan records permitted
- No in-memory conversation state

**Rationale**: Ensures data durability, enables multi-user isolation, prevents data loss, provides production-grade reliability, and enables stateless backend architecture.

### IV. Production-Grade Architecture

All implementations MUST meet production standards. Shortcuts, partial implementations, and "good enough" solutions are prohibited.

**Rules**:
- TypeScript strict mode required
- Tailwind CSS officially configured (not CDN)
- Environment variables mandatory for all secrets
- Centralized API client for all backend communication
- Error handling for all failure paths (401, 403, 422, 500)
- CORS properly configured
- Connection pooling for database
- Structured logging for observability
- No placeholder logic or mock APIs

**Rationale**: Prevents technical debt accumulation, ensures maintainability, and delivers reliable systems from day one.

### V. Root-Cause Engineering

All fixes MUST address root causes, not symptoms. Patch fixes and workarounds are prohibited.

**Rules**:
- Identify the underlying issue before implementing a fix
- No temporary solutions that defer the real problem
- Document the root cause in commit messages
- Validate that the fix prevents recurrence

**Rationale**: Prevents bug accumulation, reduces maintenance burden, and builds system understanding.

### VI. Clear Separation of Layers

Frontend, authentication, backend, AI agent, MCP, and database layers MUST remain independent with well-defined contracts.

**Rules**:
- **Frontend**: Next.js 16+ App Router, TypeScript, Tailwind CSS, OpenAI ChatKit
- **Authentication**: Better Auth with JWT tokens, Prisma (auth tables only)
- **Backend**: FastAPI with Python, SQLModel ORM (application data)
- **AI Layer**: OpenAI Agents SDK (intent analysis and tool selection only)
- **MCP Layer**: Official MCP SDK (database mutations only)
- **Database**: PostgreSQL (Neon Serverless)
- Each layer has its own CLAUDE.md with layer-specific rules
- No cross-layer logic bleeding (e.g., agent accessing database directly)
- API contracts define all inter-layer communication

**Rationale**: Enables independent testing, parallel development, technology substitution, and clear responsibility boundaries.

### VII. MCP-Only Database Mutations (NON-NEGOTIABLE - PHASE-3)

MCP tools are the ONLY components permitted to perform database mutations for task data. All other components are prohibited from direct database writes.

**Rules**:
- ALL task CRUD operations (create, read, update, delete, complete) MUST be implemented inside MCP tools
- MCP tools MUST use SQLModel for database operations
- MCP tools MUST receive `user_id` as parameter (from JWT)
- MCP tools MUST filter all queries by `user_id`
- MCP tools MUST be stateless (no in-memory state)
- Chat endpoint MUST NEVER write task data directly
- AI Agent MUST NEVER access database directly
- Only MCP tools execute: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`

**Rationale**: Enforces single responsibility principle, prevents data corruption, ensures consistent validation, enables centralized security enforcement, and maintains clear architectural boundaries.

### VIII. Stateless Backend Architecture (NON-NEGOTIABLE - PHASE-3)

The FastAPI backend MUST remain completely stateless. All conversation state MUST persist in the database.

**Rules**:
- NO in-memory conversation state
- NO global variables or class-level state
- NO session storage on server
- MUST fetch conversation history from database on each request
- MUST store all messages (user and assistant) in database
- Server restarts MUST NOT lose conversation data
- Chat endpoint orchestrates only (load, store, invoke agent, return)

**Rationale**: Enables horizontal scaling, simplifies deployment, prevents data loss on restart, supports distributed systems, and ensures conversation persistence.

### IX. AI Agent Orchestration (NON-NEGOTIABLE - PHASE-3)

The AI agent analyzes user intent and selects tools. It NEVER performs database operations or business logic directly.

**Rules**:
- Agent MUST use OpenAI Agents SDK (official SDK only)
- Agent decides which MCP tools to invoke based on user intent
- Agent MUST NEVER access database directly
- Agent MUST NEVER perform task CRUD operations directly
- Agent receives tool results and formulates natural language responses
- Agent handles tool invocation errors gracefully
- No custom agent implementations (use official SDK)

**Rationale**: Separates intent analysis from execution, enables tool reusability, maintains security boundaries, and leverages official SDK capabilities.

## Architecture Law

### Phase-2 Stack (STABLE FOUNDATION)

**Stack Requirements** (NON-NEGOTIABLE):
- **Frontend**: Next.js 16+ App Router + TypeScript + Tailwind CSS
- **Authentication**: Better Auth + JWT + Prisma (auth tables only)
- **Backend**: FastAPI + Python + SQLModel ORM (application data)
- **Database**: PostgreSQL (Neon Serverless)

**Component Interaction Flow**:
```
User → Frontend (Next.js) → Better Auth (JWT) → Backend (FastAPI) → PostgreSQL (Neon)
```

**Authentication Flow**:
1. Better Auth issues JWT on login
2. Frontend stores JWT securely (httpOnly cookie)
3. Frontend API client attaches JWT to all requests automatically
4. Backend verifies JWT signature
5. Backend extracts `user_id` from JWT claims
6. Backend uses `user_id` for database queries

**User Isolation**:
- User identity derived ONLY from JWT claims
- Database enforces foreign key constraints: `tasks.user_id → user.id`
- All queries MUST filter by authenticated `user_id`
- Users can ONLY access their own resources

### Phase-3 Stack (AI CHATBOT)

**Additional Stack Requirements** (NON-NEGOTIABLE):
- **Chat UI**: OpenAI ChatKit (official UI library)
- **AI Layer**: OpenAI Agents SDK (official SDK)
- **MCP Layer**: Official MCP SDK
- **Chat Endpoint**: POST `/api/chat` (stateless)

**Complete System Flow**:
```
User → ChatKit UI → POST /api/chat (JWT) → FastAPI Backend
  ↓
  1. Verify JWT → Extract user_id
  2. Fetch conversation history from DB
  3. Store user message in DB
  4. Invoke OpenAI Agent
  ↓
OpenAI Agent → Analyze Intent → Select MCP Tools
  ↓
MCP Tools → Execute Database Operations (SQLModel)
  ↓
Agent → Formulate Response
  ↓
Backend → Store assistant message in DB → Return response
```

**Conversation Flow (Stateless)**:
1. Receive user message via POST `/api/chat`
2. Load conversation history from database
3. Store user message in `messages` table
4. Build agent message array
5. Invoke OpenAI Agent with message array
6. Agent invokes MCP tools if needed
7. MCP tools execute database operations
8. Agent receives tool results
9. Store assistant response in `messages` table
10. Return response to client
11. Server holds NO state

**MCP Tool Architecture**:
- `add_task(user_id, title, description)` → SQLModel INSERT
- `list_tasks(user_id)` → SQLModel SELECT with user_id filter
- `complete_task(user_id, task_id)` → SQLModel UPDATE with user_id filter
- `delete_task(user_id, task_id)` → SQLModel DELETE with user_id filter
- `update_task(user_id, task_id, title, description)` → SQLModel UPDATE with user_id filter

## Workflow Law

**Mandatory Sequence** (BLOCKING):

```
spec → plan → tasks → implementation
```

**No deviation permitted.**

**Enforcement**:
- When coding is requested without approved specs, Claude MUST warn and ask for confirmation
- All features MUST have corresponding spec, plan, and tasks artifacts
- Implementation MUST reference task IDs for traceability
- Phase-3 follows "Agentic Dev Stack" workflow (same sequence)

## Database Rules

**Provider**: PostgreSQL (Neon Serverless)

**ORM Strategy**:
- **Prisma**: Better Auth tables only (user, session, account, verification) - Frontend
- **SQLModel**: Application tables (tasks, conversations, messages) - Backend

**Schema Requirements**:

### Phase-2 Tables (Existing)

**`user` table**:
- Managed by Better Auth via Prisma
- Primary key: `id` (TEXT - CUID)
- Contains: email, name, emailVerified, createdAt, updatedAt

**`tasks` table**:
- Managed by backend via SQLModel
- Primary key: `id` (SERIAL - INTEGER)
- Foreign key: `user_id` references `user.id` (ON DELETE CASCADE)
- Fields: `title` (VARCHAR 500), `description` (TEXT), `completed` (BOOLEAN), `created_at`, `updated_at`
- Index on `user_id` for query performance

### Phase-3 Tables (NEW)

**`conversations` table**:
- Managed by backend via SQLModel
- Primary key: `id` (SERIAL - INTEGER)
- Foreign key: `user_id` references `user.id` (ON DELETE CASCADE)
- Fields: `user_id` (TEXT), `title` (VARCHAR 200, optional), `created_at`, `updated_at`
- Index on `user_id` for query performance

**`messages` table**:
- Managed by backend via SQLModel
- Primary key: `id` (SERIAL - INTEGER)
- Foreign key: `conversation_id` references `conversations.id` (ON DELETE CASCADE)
- Fields: `conversation_id` (INTEGER), `role` (VARCHAR 20: 'user' or 'assistant'), `content` (TEXT), `tool_calls` (JSONB, optional), `tool_results` (JSONB, optional), `created_at`
- Index on `conversation_id` for query performance

**Constraints**:
- NO orphan records (foreign key enforced)
- Migrations required for all schema changes
- NO in-memory storage
- All queries MUST filter by authenticated `user_id`
- CASCADE delete: user deleted → conversations deleted → messages deleted

**Connection**:
- Use environment variable: `DATABASE_URL`
- Connection pooling recommended
- Handle connection errors gracefully

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
- **No Manual Coding**: All implementation via Claude Code following spec workflow

### Development Order Standards

**BLOCKING SEQUENCE**: Each phase MUST pass quality gates before proceeding.

**Phase-2 (COMPLETE)**:
1. Frontend Implementation → Validate with `implementation-validator-playwright`
2. Authentication → Validate with `implementation-validator-playwright`
3. Backend API → Validate with `implementation-validator-playwright`
4. Database Schema + Integration → Validate with `implementation-validator-playwright`
5. Full Integration Testing → Validate with `integration-testing-engineer`

**Phase-3 (CURRENT)**:
6. AI Chatbot Integration:
   - 6.1: Database Schema (conversations, messages)
   - 6.2: MCP Server Implementation (5 tools)
   - 6.3: OpenAI Agent Integration
   - 6.4: Chat Endpoint (stateless)
   - 6.5: Frontend Chat UI (ChatKit)
   - 6.6: Integration Testing

## Quality Gates

**BLOCKING REQUIREMENTS**: All MUST pass before proceeding to next phase.

### Phase-2 Gates (COMPLETE)

**Frontend Gates**:
- ✅ `npm run dev` succeeds without errors
- ✅ Tailwind styles render correctly
- ✅ TypeScript compiles with strict mode
- ✅ No console errors in browser
- ✅ Centralized API client in place

**Authentication Gates**:
- ✅ JWT issued on login
- ✅ JWT stored securely
- ✅ JWT attached to requests automatically
- ✅ Auth state persists across reloads

**Backend Gates**:
- ✅ Backend starts without errors
- ✅ JWT verification rejects invalid tokens (401)
- ✅ Endpoints extract `user_id` from JWT
- ✅ Unauthorized requests return 403
- ✅ CORS configured correctly

**Database Gates**:
- ✅ Database connection succeeds
- ✅ Migrations run successfully
- ✅ Foreign key constraints enforced
- ✅ Tasks persist in database
- ✅ Users only see their own tasks
- ✅ No orphan records

**Integration Gates**:
- ✅ Signup → Login → Create Task flow works
- ✅ JWT flow end-to-end (issuance → verification)
- ✅ User isolation enforced (User A ≠ User B tasks)
- ✅ Error paths handled (invalid JWT, unauthorized access)

### Phase-3 Gates (CURRENT)

**MCP Server Gates**:
- [ ] Official MCP SDK installed
- [ ] MCP server starts without errors
- [ ] All 5 task tools implemented (add, list, complete, delete, update)
- [ ] Tools use SQLModel for database operations
- [ ] Tools receive `user_id` as parameter
- [ ] Tools filter queries by `user_id`
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
- [ ] `user_id` extracted from JWT (not from request body)
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

## Forbidden Practices

**The following are STRICTLY PROHIBITED in Phase-3**:

- ❌ Direct database access by AI agent
- ❌ Direct task writes in chat endpoint (must use MCP tools)
- ❌ In-memory conversation storage
- ❌ Mock APIs or placeholder logic
- ❌ Stateful backend implementation
- ❌ Custom agent implementations (use official OpenAI Agents SDK)
- ❌ Custom MCP implementations (use official MCP SDK)
- ❌ Manual coding by human (all via Claude Code)
- ❌ Implementation without approved specification
- ❌ OAuth integration (out of scope)
- ❌ Analytics or telemetry (out of scope)
- ❌ Phase-4 features (not yet defined)
- ❌ Real-time streaming responses (out of scope)
- ❌ Voice input/output (out of scope)
- ❌ File attachments (out of scope)
- ❌ Multi-modal capabilities (out of scope)

## Success Criteria

**Phase-3 is considered complete when**:

1. ✅ Chatbot manages tasks via natural language
2. ✅ MCP tools perform all task persistence operations
3. ✅ Conversations persist in database and resume after server restart
4. ✅ Backend stateless verified (no in-memory state)
5. ✅ Full CRUD operations work via chat interface
6. ✅ User isolation enforced (User A cannot see User B's conversations or tasks)
7. ✅ JWT authentication enforced on all chat requests
8. ✅ Agent invokes MCP tools correctly
9. ✅ Tool results reflected in database
10. ✅ Phase-2 functionality remains intact and operational

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
- Phase-3 implementations MUST comply with ALL Phase-2 and Phase-3 principles

### Runtime Guidance

- Root CLAUDE.md: Project-wide rules (Phase-2 + Phase-3)
- `frontend/CLAUDE.md`: Next.js, Better Auth, ChatKit UI-specific rules
- `backend/CLAUDE.md`: FastAPI, JWT verification, MCP, Agent-specific rules
- Claude Code reads the **closest** CLAUDE.md first to prevent cross-stack confusion

**Version**: 1.1.0 | **Ratified**: 2026-02-05 | **Last Amended**: 2026-02-08
