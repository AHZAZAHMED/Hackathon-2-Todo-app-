# Implementation Plan: Stateless Chat API + OpenAI Agent Orchestration

**Branch**: `004-stateless-chat-api` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-stateless-chat-api/spec.md`

## Summary

Implement a stateless FastAPI backend chat endpoint that authenticates users via Better Auth JWT, persists conversation history in PostgreSQL, and uses OpenAI Agents SDK (via OpenRouter API with Gemini model) to generate AI responses. This implementation focuses on the core conversational API without MCP tool integration (deferred to Spec-3).

**Primary Requirement**: Enable authenticated users to send messages and receive AI-generated responses with full conversation context persistence.

**Technical Approach**: Stateless request-response cycle where each request loads conversation history from database, invokes OpenAI Agent, stores the response, and returns to client. No in-memory state, no MCP tools, text-only conversational AI.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- FastAPI 0.104+
- SQLModel 0.0.14+
- OpenAI Agents SDK (latest)
- PyJWT 2.8+ (for Better Auth JWT verification)
- asyncpg 0.29+ (PostgreSQL async driver)
- httpx 0.25+ (for OpenRouter API calls)

**Storage**: PostgreSQL (Neon Serverless) - conversations and messages tables
**Testing**: pytest 7.4+, pytest-asyncio, httpx (for async testing)
**Target Platform**: Linux server (production), Windows/macOS (development)
**Project Type**: Web application (backend component)
**Performance Goals**:
- Chat response < 5 seconds for 95% of requests
- Support 100 concurrent requests
- Database query optimization for conversation history loading

**Constraints**:
- Response time < 5 seconds (p95)
- Stateless operation (no in-memory state)
- Last 50 messages loaded for AI context
- Message length: 1-2000 characters
- JWT verification on every request

**Scale/Scope**:
- Multi-user system (user isolation enforced)
- Conversation history persistence
- Horizontal scaling support
- Production-grade error handling

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase-2 Foundation Compliance

- ✅ **Spec-First Development**: Specification approved, proceeding to planning phase
- ✅ **JWT-Only Identity**: Backend extracts user_id from JWT claims only
- ✅ **Database as Single Source of Truth**: PostgreSQL for all state persistence
- ✅ **Production-Grade Quality**: No mocks, no placeholders, full error handling
- ✅ **Root-Cause Engineering**: All implementations address root causes
- ✅ **Clear Separation of Layers**: Backend orchestration, database persistence, AI agent separate
- ✅ **Deterministic Behavior**: Each request independent, fetches context from database

### Phase-3 Architecture Compliance

- ✅ **Stateless Backend Architecture**: No in-memory conversation state, all state in database
- ⚠️ **MCP-Only Task Mutations**: NOT APPLICABLE - MCP tools deferred to Spec-3, this spec is chat-only
- ✅ **AI Agent Orchestration**: OpenAI Agents SDK handles AI logic, no direct database access
- ✅ **Fixed Technology Stack**: FastAPI, OpenAI Agents SDK, SQLModel, PostgreSQL (Neon)
- ✅ **Chat Flow Sequence**: Follows mandatory 15-step flow (without MCP tool invocation steps)

### Gate Status: ✅ PASS

**Justification for MCP Deferral**: This specification intentionally excludes MCP tools and task operations. The chat endpoint provides conversational AI responses only. Task management via MCP tools will be implemented in Spec-3 as a separate feature. This aligns with the incremental delivery strategy and allows independent testing of the chat infrastructure.

## Project Structure

### Documentation (this feature)

```text
specs/004-stateless-chat-api/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (current)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (to be generated)
├── contracts/           # Phase 1 output (to be generated)
│   └── chat-api.md      # POST /api/chat contract
├── checklists/          # Quality validation
│   └── requirements.md  # Specification quality checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration and environment variables
│   ├── database.py                # SQLModel engine and session management
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── dependencies.py        # JWT verification dependency (existing)
│   │   └── jwt_utils.py           # JWT verification utilities (existing)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── conversation.py        # NEW: Conversation SQLModel
│   │   └── message.py             # NEW: Message SQLModel
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── tasks.py               # Existing: Task CRUD endpoints
│   │   └── chat.py                # NEW: Chat endpoint
│   ├── services/
│   │   ├── __init__.py
│   │   └── ai_agent.py            # NEW: OpenAI Agents SDK integration
│   └── schemas/
│       ├── __init__.py
│       └── chat.py                # NEW: Request/response schemas for chat
├── migrations/
│   ├── 001_create_auth_tables.sql    # Existing: Better Auth tables
│   ├── 002_create_tasks_table.sql    # Existing: Tasks table
│   └── 003_create_chat_tables.sql    # NEW: Conversations and messages tables
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest configuration
│   ├── test_chat_endpoint.py      # NEW: Chat endpoint tests
│   ├── test_ai_agent.py           # NEW: AI agent service tests
│   └── test_chat_models.py        # NEW: Conversation/message model tests
├── requirements.txt               # Python dependencies
└── .env.example                   # Environment variable template

frontend/
├── (existing Phase-2 structure)
└── (ChatKit UI already implemented in Phase-3 Spec-1)
```

**Structure Decision**: Web application structure with backend and frontend separation. Backend contains all chat API logic. Frontend (already implemented in Spec-1) consumes the chat API. This plan focuses exclusively on backend implementation.

## Complexity Tracking

> **No violations detected. All constitution principles satisfied.**

## Implementation Phases

### Phase 0: Research & Technology Decisions

**Objective**: Resolve all technical unknowns and establish implementation patterns.

**Research Tasks**:

1. **OpenRouter API Integration**
   - Research: How to configure OpenAI Agents SDK to use OpenRouter as provider
   - Research: OpenRouter API authentication and endpoint configuration
   - Research: Gemini model selection via OpenRouter (openai/gpt-3.5-turbo compatibility)
   - Decision needed: Base URL, API key format, model identifier

2. **OpenAI Agents SDK Usage Patterns**
   - Research: Basic agent initialization without tools
   - Research: Message array format for conversation history
   - Research: Async/await patterns with OpenAI Agents SDK
   - Research: Error handling for API failures
   - Decision needed: Agent configuration, runner setup, response extraction

3. **SQLModel Async Patterns**
   - Research: Async session management with SQLModel
   - Research: Transaction handling for message persistence
   - Research: Query optimization for loading last 50 messages
   - Decision needed: Session lifecycle, connection pooling

4. **JWT Verification with Better Auth**
   - Research: Better Auth JWT format and claims structure
   - Research: PyJWT verification with Better Auth secret
   - Research: Extracting user_id from JWT claims
   - Decision needed: Verification algorithm, claim names

5. **Database Migration Strategy**
   - Research: SQLModel table creation patterns
   - Research: Foreign key constraints with CASCADE delete
   - Research: Index creation for performance
   - Decision needed: Migration tool (Alembic vs raw SQL)

**Output**: `research.md` with all decisions documented

---

### Phase 1: Design & Contracts

**Objective**: Define data models, API contracts, and implementation patterns.

**Deliverables**:

1. **Data Model** (`data-model.md`)
   - Conversation entity with fields and relationships
   - Message entity with fields and relationships
   - Foreign key constraints
   - Indexes for query performance
   - SQLModel class definitions

2. **API Contracts** (`contracts/chat-api.md`)
   - POST /api/chat endpoint specification
   - Request schema (message, conversation_id)
   - Response schema (conversation_id, response, timestamp)
   - Error responses (401, 403, 422, 500, 503)
   - Authentication requirements

3. **Quickstart Guide** (`quickstart.md`)
   - Environment setup instructions
   - Database migration steps
   - Running the backend server
   - Testing the chat endpoint
   - Troubleshooting common issues

**Output**: Complete design artifacts ready for task generation

---

### Phase 2: Task Generation

**Objective**: Break down implementation into executable tasks.

**Note**: This phase is executed by `/sp.tasks` command, NOT by `/sp.plan`.

**Expected Task Categories**:
1. Environment and configuration setup
2. Database models and migrations
3. JWT authentication dependency
4. OpenAI Agents SDK service
5. Chat endpoint implementation
6. Error handling and validation
7. Testing and integration validation

---

## Risk Assessment

### High-Priority Risks

1. **OpenRouter API Reliability**
   - Risk: Third-party API downtime or rate limiting
   - Mitigation: Implement 503 error handling, retry logic with exponential backoff, circuit breaker pattern
   - Fallback: Clear error messages to users, log failures for monitoring

2. **JWT Verification Compatibility**
   - Risk: Better Auth JWT format may not match PyJWT expectations
   - Mitigation: Research Better Auth JWT structure in Phase 0, implement comprehensive tests
   - Fallback: Document exact JWT format requirements, provide clear error messages

3. **Database Connection Pool Exhaustion**
   - Risk: High concurrent load may exhaust database connections
   - Mitigation: Configure connection pooling with appropriate limits, implement connection timeout
   - Fallback: Return 503 with retry-after header, scale database connections

4. **Conversation History Performance**
   - Risk: Loading 50 messages per request may be slow for large conversations
   - Mitigation: Create index on (conversation_id, created_at), use LIMIT in query
   - Fallback: Reduce message limit if performance degrades, implement pagination

### Medium-Priority Risks

5. **OpenAI Agents SDK Learning Curve**
   - Risk: Unfamiliarity with OpenAI Agents SDK may cause implementation delays
   - Mitigation: Thorough research in Phase 0, reference official documentation
   - Fallback: Use direct OpenAI API calls if SDK proves too complex

6. **Stateless Architecture Validation**
   - Risk: Accidental introduction of in-memory state
   - Mitigation: Code review checklist, integration tests with server restart
   - Fallback: Refactor to remove state, add monitoring for state detection

### Low-Priority Risks

7. **Message Length Validation Edge Cases**
   - Risk: Unicode characters may cause length calculation issues
   - Mitigation: Use character count (not byte count), test with emoji and special characters
   - Fallback: Document character counting method, adjust limit if needed

8. **Concurrent Request Race Conditions**
   - Risk: Simultaneous messages to same conversation may cause ordering issues
   - Mitigation: Use Read Committed isolation with row locking (SELECT FOR UPDATE)
   - Fallback: Accept eventual consistency, rely on timestamp ordering

---

## Success Criteria

### Functional Success

- ✅ Authenticated users can send messages via POST /api/chat
- ✅ AI agent responds with contextually relevant messages
- ✅ Conversation history persists across requests
- ✅ Server restart does not lose conversation data
- ✅ User isolation enforced (users only access own conversations)
- ✅ Invalid JWT returns 401 Unauthorized
- ✅ Empty/too-long messages return 422 Unprocessable Entity
- ✅ AI service failure returns 503 Service Unavailable

### Non-Functional Success

- ✅ Response time < 5 seconds for 95% of requests
- ✅ System handles 100 concurrent requests without errors
- ✅ Backend operates statelessly (verified by restart test)
- ✅ Database queries optimized (indexed foreign keys)
- ✅ Comprehensive error logging (structured JSON format)
- ✅ All tests pass (unit, integration, end-to-end)

### Integration Success

- ✅ Frontend ChatKit UI successfully calls /api/chat
- ✅ JWT properly extracted and verified
- ✅ Conversation state persists across page reloads
- ✅ Multiple conversations per user supported
- ✅ No Phase-2 functionality broken (task CRUD still works)

---

## Next Steps

1. **Execute Phase 0**: Generate `research.md` by researching all technical unknowns
2. **Execute Phase 1**: Generate `data-model.md`, `contracts/`, and `quickstart.md`
3. **Run `/sp.tasks`**: Generate task breakdown for implementation
4. **Implement**: Execute tasks via Claude Code following Agentic Dev Stack workflow
5. **Validate**: Run integration tests to verify all success criteria

---

**Status**: ✅ Planning complete. Ready for Phase 0 research.
