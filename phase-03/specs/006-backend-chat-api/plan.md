# Implementation Plan: Backend Chat API + OpenAI Agent Orchestration

**Branch**: `006-backend-chat-api` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-backend-chat-api/spec.md`

## Summary

This plan implements a backend conversational API that authenticates users via Better Auth JWT, manages conversation history in PostgreSQL, and orchestrates an AI agent using OpenAI Agents SDK with Gemini 2.0 Flash (free LLM). The agent invokes MCP tools to perform task management operations (CRUD) on behalf of users. The backend is stateless - all conversation state persists in the database.

**Primary Requirement**: POST /api/chat endpoint that receives user messages, loads conversation history, invokes AI agent with MCP tools, stores responses, and returns AI-generated replies.

**Technical Approach**: Use OpenAI Agents SDK with AsyncOpenAI client configured to use Google's Gemini API endpoint (https://generativelanguage.googleapis.com/v1beta/openai) instead of OpenAI's API. This allows using the free Gemini 2.0 Flash model while maintaining compatibility with the OpenAI Agents SDK interface. MCP tools are the only components that perform database mutations for task data.

## Technical Context

**Language/Version**: Python 3.11+ (existing FastAPI backend)
**Primary Dependencies**:
- OpenAI Agents SDK (openai-agents)
- AsyncOpenAI (openai Python client)
- FastAPI (existing)
- SQLModel (existing)
- Better Auth JWT verification (existing)
- Gemini API (Google Generative AI)

**Storage**: PostgreSQL (Neon Serverless) - new tables: conversations, messages
**Testing**: pytest (existing from Phase-2)
**Target Platform**: Linux server (FastAPI backend)
**Project Type**: Web application (backend only - frontend already implemented)
**Performance Goals**: <5s response time (95th percentile), 50 concurrent requests without degradation
**Constraints**:
- Free LLM only (Gemini 2.0 Flash)
- Stateless backend (no in-memory conversation state)
- 2000 token conversation history limit
- No streaming responses
- Single conversation per user

**Scale/Scope**:
- Single conversation per user (auto-created)
- Up to 100 messages per conversation
- 5 MCP tools (add_task, list_tasks, complete_task, delete_task, update_task)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅ PASS
- Specification approved: specs/006-backend-chat-api/spec.md
- Following mandatory workflow: /sp.specify → /sp.plan → /sp.tasks → implementation
- No coding before spec approval

### Principle II: JWT-Only Identity ✅ PASS
- Backend extracts user_id from verified JWT claims (FR-005)
- Frontend never sends user_id manually
- All MCP tools receive user_id from JWT (FR-019)
- Chat endpoint verifies JWT before processing (FR-004)

### Principle III: Database-Backed Persistence ✅ PASS
- Conversations table with user_id foreign key (FR-009)
- Messages table with conversation_id foreign key (FR-010)
- No in-memory conversation state (stateless backend)
- All state persists in PostgreSQL
- Foreign key constraints enforced (ON DELETE CASCADE)

### Principle IV: Production-Grade Architecture ✅ PASS
- Environment variables for Gemini API key
- Proper error handling (401, 422, 500, 503, 504)
- Structured logging for observability
- Connection pooling for database
- No placeholder logic or mock APIs

### Principle V: Root-Cause Engineering ✅ PASS
- No patch fixes or workarounds
- All implementations address root causes
- Proper error propagation and handling

### Principle VI: Clear Separation of Layers ✅ PASS
- Backend: FastAPI endpoint (orchestration only)
- AI Agent: OpenAI Agents SDK (intent analysis and tool selection)
- MCP Layer: Task management tools (database mutations only)
- Database: PostgreSQL (state persistence)
- No cross-layer logic bleeding

### Principle VII: MCP-Only Database Mutations ✅ PASS
- All task CRUD operations in MCP tools (FR-022, FR-023, FR-024)
- Chat endpoint never writes task data directly
- AI agent never accesses database directly
- MCP tools use SQLModel for database operations

### Principle VIII: Stateless Backend Architecture ✅ PASS
- No in-memory conversation state
- Fetch conversation history from database on each request (FR-011)
- Store all messages in database (FR-012, FR-013)
- Server restarts do not lose conversation data

### Principle IX: AI Agent Orchestration ✅ PASS
- OpenAI Agents SDK (official SDK) (FR-014)
- Agent decides which MCP tools to invoke (FR-018)
- Agent never performs database operations directly
- Agent receives tool results and formulates responses (FR-021)

**Constitution Check Result**: ✅ ALL GATES PASSED

## Project Structure

### Documentation (this feature)

```text
specs/006-backend-chat-api/
├── spec.md              # Feature specification (COMPLETE)
├── plan.md              # This file (IN PROGRESS)
├── research.md          # Phase 0 output (TO BE GENERATED)
├── data-model.md        # Phase 1 output (TO BE GENERATED)
├── quickstart.md        # Phase 1 output (TO BE GENERATED)
├── contracts/           # Phase 1 output (TO BE GENERATED)
│   └── chat-api.yaml    # OpenAPI spec for POST /api/chat
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py                      # FastAPI app (EXISTING)
│   ├── auth/                        # JWT verification (EXISTING)
│   │   └── jwt_verify.py
│   ├── models/                      # SQLModel schemas
│   │   ├── task.py                  # EXISTING (Phase-2)
│   │   ├── conversation.py          # NEW (Phase-3)
│   │   └── message.py               # NEW (Phase-3)
│   ├── routes/
│   │   ├── tasks.py                 # EXISTING (Phase-2 CRUD endpoints)
│   │   └── chat.py                  # NEW (POST /api/chat endpoint)
│   ├── ai/                          # NEW (AI agent logic)
│   │   ├── __init__.py
│   │   ├── agent.py                 # OpenAI Agents SDK integration
│   │   ├── prompts.py               # System prompts for agent
│   │   └── gemini_client.py         # AsyncOpenAI client configured for Gemini
│   ├── mcp/                         # NEW (MCP server and tools)
│   │   ├── __init__.py
│   │   ├── server.py                # MCP server setup
│   │   └── tools.py                 # Task tools (add, list, complete, delete, update)
│   └── services/                    # NEW (Business logic)
│       ├── __init__.py
│       ├── conversation_service.py  # Conversation management
│       └── message_service.py       # Message persistence
├── migrations/
│   ├── 001_create_auth_tables.sql   # EXISTING (Phase-2)
│   ├── 002_create_tasks_table.sql   # EXISTING (Phase-2)
│   └── 003_create_chat_tables.sql   # NEW (conversations and messages)
├── tests/
│   ├── test_chat_endpoint.py        # NEW (chat endpoint tests)
│   ├── test_agent.py                # NEW (agent integration tests)
│   └── test_mcp_tools.py            # NEW (MCP tool tests)
└── requirements.txt                 # UPDATE (add OpenAI Agents SDK, openai)

frontend/
├── app/
│   └── chat/                        # EXISTING (004-chatbot-frontend)
└── lib/
    └── chat-client.ts               # EXISTING (sends requests to /api/chat)
```

**Structure Decision**: Web application structure with backend and frontend separation. This plan focuses on backend implementation only. Frontend (ChatKit UI) already implemented in 004-chatbot-frontend. Backend adds new routes/chat.py, ai/, mcp/, and services/ directories for chat functionality while preserving existing Phase-2 CRUD endpoints.

## Complexity Tracking

> **No violations detected - all constitution checks passed**

## Phase 0: Research & Technical Unknowns

**Goal**: Resolve all technical unknowns before design phase.

### Research Tasks

1. **OpenAI Agents SDK with Gemini Integration**
   - Research: How to configure AsyncOpenAI client with Gemini API endpoint
   - Research: OpenAI Agents SDK compatibility with non-OpenAI models
   - Research: Runner.run_sync vs async variants for agent execution
   - Research: Tool registration and invocation patterns in OpenAI Agents SDK
   - Decision needed: Synchronous vs asynchronous agent execution

2. **MCP Tool Interface Design**
   - Research: Official MCP SDK tool signature requirements
   - Research: How to pass user_id to MCP tools from agent context
   - Research: Tool result format expected by OpenAI Agents SDK
   - Research: Error handling in MCP tools (how to propagate errors to agent)
   - Decision needed: Tool implementation approach (functions vs classes)

3. **Conversation History Management**
   - Research: Token counting for conversation history (2000 token limit)
   - Research: Efficient database queries for loading recent messages
   - Research: Message truncation strategies when exceeding token limit
   - Decision needed: Token counting library (tiktoken or alternative)

4. **Stateless Backend Architecture**
   - Research: Best practices for stateless FastAPI endpoints
   - Research: Database connection pooling for concurrent requests
   - Research: Transaction management for message persistence
   - Decision needed: Database session management pattern

5. **Error Handling and Timeouts**
   - Research: FastAPI timeout configuration for long-running requests
   - Research: Gemini API error codes and retry strategies
   - Research: Graceful degradation when MCP tools fail
   - Decision needed: Timeout implementation approach (middleware vs per-route)

**Output**: research.md with decisions and rationale for all unknowns

## Phase 1: Design & Contracts

**Prerequisites**: research.md complete

### 1.1 Data Model Design

**Goal**: Define SQLModel schemas for conversations and messages tables.

**Entities to Model**:
- Conversation (id, user_id, created_at, updated_at)
- Message (id, conversation_id, role, content, created_at)

**Relationships**:
- Conversation belongs to User (user_id foreign key)
- Message belongs to Conversation (conversation_id foreign key)
- Conversation has many Messages (one-to-many)

**Validation Rules**:
- user_id must reference existing user (foreign key constraint)
- conversation_id must reference existing conversation (foreign key constraint)
- role must be 'user' or 'assistant' (CHECK constraint)
- content cannot be empty (NOT NULL)
- message length max 10,000 characters (application-level validation)

**Output**: data-model.md with SQLModel class definitions

### 1.2 API Contract Design

**Goal**: Define OpenAPI specification for POST /api/chat endpoint.

**Endpoint**: POST /api/chat
**Authentication**: Bearer JWT token (required)
**Request Body**: { message: string, conversation_id?: string }
**Response Body**: { conversation_id: string, response: string, tool_calls: array }
**Error Responses**: 401, 422, 500, 503, 504

**Output**: contracts/chat-api.yaml (OpenAPI 3.0 specification)

### 1.3 Quickstart Guide

**Goal**: Document setup and testing instructions for developers.

**Sections**:
1. Prerequisites (Python 3.11+, PostgreSQL, Gemini API key)
2. Installation (pip install dependencies)
3. Database Setup (run migration 003)
4. Environment Variables (GEMINI_API_KEY, DATABASE_URL)
5. Running the Server (uvicorn command)
6. Testing the Endpoint (curl examples)

**Output**: quickstart.md

### 1.4 Agent Context Update

**Goal**: Update agent-specific context file with new technologies.

**Run**: `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`

**Technologies to Add**:
- OpenAI Agents SDK
- Gemini 2.0 Flash API
- MCP (Model Context Protocol)
- Conversation management patterns

**Output**: Updated agent context file

## Phase 2: Task Breakdown

**Note**: This phase is handled by `/sp.tasks` command (NOT part of /sp.plan).

The tasks.md file will be generated after this plan is approved, breaking down the implementation into:
- Database migration (conversations and messages tables)
- SQLModel models (Conversation, Message)
- MCP server setup and tool implementation
- OpenAI Agents SDK integration with Gemini
- Chat endpoint implementation
- Service layer (conversation and message management)
- Error handling and validation
- Integration tests
- Documentation updates

## Implementation Phases (High-Level)

### Phase 3: Database Schema Implementation
- Create migration 003 (conversations and messages tables)
- Define SQLModel models (Conversation, Message)
- Apply migration to database
- Verify foreign key constraints

### Phase 4: MCP Server and Tools
- Install Official MCP SDK
- Implement MCP server setup
- Implement 5 task tools (add, list, complete, delete, update)
- Ensure tools use SQLModel for database operations
- Ensure tools receive user_id as parameter
- Test tool invocations

### Phase 5: AI Agent Integration
- Install OpenAI Agents SDK
- Configure AsyncOpenAI client with Gemini endpoint
- Implement agent setup with system prompts
- Register MCP tools with agent
- Implement agent invocation logic
- Test agent with sample messages

### Phase 6: Chat Endpoint Implementation
- Create POST /api/chat route
- Implement JWT verification
- Implement conversation history loading
- Implement message persistence (user and assistant)
- Implement agent invocation
- Implement response formatting
- Implement error handling (401, 422, 500, 503, 504)

### Phase 7: Service Layer
- Implement conversation_service.py (create, get, load history)
- Implement message_service.py (create, list, token counting)
- Implement token counting for 2000 token limit
- Implement transaction management

### Phase 8: Integration Testing
- Test complete chat flow (user message → agent → MCP tools → response)
- Test conversation persistence across requests
- Test user isolation (User A cannot see User B's conversations)
- Test tool invocations (add task via chat)
- Test error paths (invalid JWT, tool failures, agent errors)
- Test stateless backend (restart server, conversation persists)
- Verify Phase-2 functionality still works

### Phase 9: Documentation and Deployment
- Update README with chat API documentation
- Update .env.example with GEMINI_API_KEY
- Create deployment guide
- Create troubleshooting guide

## Key Technical Decisions (To Be Resolved in Phase 0)

1. **Agent Execution Mode**: Synchronous (Runner.run_sync) vs Asynchronous (Runner.run)
   - Trade-off: Simplicity vs performance
   - Impact: Request handling concurrency

2. **Token Counting Library**: tiktoken vs alternative
   - Trade-off: Accuracy vs performance
   - Impact: Conversation history truncation accuracy

3. **MCP Tool Implementation**: Functions vs Classes
   - Trade-off: Simplicity vs extensibility
   - Impact: Tool registration and testing

4. **Database Session Management**: Per-request vs per-operation
   - Trade-off: Connection overhead vs transaction isolation
   - Impact: Concurrent request handling

5. **Timeout Implementation**: Middleware vs per-route decorator
   - Trade-off: Global vs granular control
   - Impact: Error handling consistency

## Risk Assessment

### High Risk
- **Gemini API Compatibility**: OpenAI Agents SDK may not work seamlessly with Gemini API
  - Mitigation: Research and prototype in Phase 0
  - Fallback: Use OpenAI API with paid tier (requires user approval)

### Medium Risk
- **Token Counting Accuracy**: 2000 token limit may be difficult to enforce accurately
  - Mitigation: Use tiktoken library for accurate token counting
  - Fallback: Use character count approximation (4 chars ≈ 1 token)

- **MCP Tool Interface**: Tool signatures may not match agent expectations
  - Mitigation: Research official MCP SDK documentation in Phase 0
  - Fallback: Adjust tool signatures based on agent requirements

### Low Risk
- **Database Performance**: Concurrent requests may cause database bottlenecks
  - Mitigation: Use connection pooling and proper indexing
  - Fallback: Add database query optimization

- **Conversation History Size**: 100 messages may exceed 2000 token limit
  - Mitigation: Implement token-based truncation (not message count)
  - Fallback: Reduce message count limit

## Success Metrics

- ✅ All constitution checks passed
- ✅ Specification approved and complete
- ⏳ Research phase resolves all technical unknowns
- ⏳ Data model and contracts generated
- ⏳ Agent context updated with new technologies
- ⏳ Tasks.md generated with dependency-ordered implementation tasks

## Next Steps

1. **Generate research.md** (Phase 0) - Resolve all technical unknowns
2. **Generate data-model.md** (Phase 1) - Define SQLModel schemas
3. **Generate contracts/chat-api.yaml** (Phase 1) - Define OpenAPI spec
4. **Generate quickstart.md** (Phase 1) - Document setup instructions
5. **Update agent context** (Phase 1) - Add new technologies
6. **Run /sp.tasks** (Phase 2) - Generate tasks.md with implementation breakdown

---

**Plan Status**: ✅ COMPLETE - Ready for Phase 0 Research
**Branch**: 006-backend-chat-api
**Next Command**: Continue with Phase 0 research generation
