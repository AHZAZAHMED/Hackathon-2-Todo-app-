---
id: PHR-012
title: Generate Backend Chat API Implementation Plan
stage: plan
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: 006-backend-chat-api
branch: 006-backend-chat-api
user: system
command: /sp.plan
labels: [planning, backend, chat-api, openai-agents, gemini, mcp, stateless, conversation-management]
links:
  spec: specs/006-backend-chat-api/spec.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - path: specs/006-backend-chat-api/plan.md
    status: created
    lines_added: 350
    lines_removed: 0
  - path: specs/006-backend-chat-api/research.md
    status: created
    lines_added: 450
    lines_removed: 0
  - path: specs/006-backend-chat-api/data-model.md
    status: created
    lines_added: 520
    lines_removed: 0
  - path: specs/006-backend-chat-api/contracts/chat-api.yaml
    status: created
    lines_added: 280
    lines_removed: 0
  - path: specs/006-backend-chat-api/quickstart.md
    status: created
    lines_added: 480
    lines_removed: 0
  - path: specs/006-backend-chat-api/agent-context-update.md
    status: created
    lines_added: 180
    lines_removed: 0
tests:
  - name: Constitution Check - All Principles
    status: PASSED
---

## Prompt

User requested implementation plan generation using `/sp.plan` command for Backend Chat API + OpenAI Agent Orchestration feature.

**Command**: `/sp.plan`

**Feature Description**:
Backend Chat API + OpenAI Agent Orchestration using third party free LLM (Gemini 2.0 Flash). The system exposes POST /api/chat endpoint that authenticates users via Better Auth JWT, loads conversation history, invokes OpenAI Agents SDK with Gemini 2.0 Flash model, and returns assistant responses. The agent can invoke MCP tools to perform task management operations (CRUD) on behalf of users.

**Context Provided**:
- Integration approach using OpenAI Agent SDK with Gemini via AsyncOpenAI client
- Request/response format (message + optional conversation_id)
- Database schema (conversations and messages tables)
- MCP tool signatures (add_task, list_tasks, complete_task, delete_task, update_task)
- Stateless backend architecture
- Token-based conversation history (last 2000 tokens)
- No streaming responses
- Standard HTTP status codes for errors

**Implementation Plan Outline**:
1. Create POST /api/chat endpoint in FastAPI backend
2. Database integration (Conversation and Message tables)
3. Agent setup (OpenAI SDK with Gemini endpoint configuration)
4. Stateless request cycle (receive, fetch history, store, build messages, run agent, capture tools, store response)

## Response snapshot

Successfully generated comprehensive implementation plan for 006-backend-chat-api feature with complete Phase 0 research, Phase 1 design artifacts, and constitution validation.

### Planning Artifacts Generated

**Phase 0: Research (research.md)**
- Resolved 5 technical unknowns:
  1. OpenAI Agents SDK with Gemini Integration → Use AsyncOpenAI with custom base_url
  2. MCP Tool Interface Design → Function-based with Pydantic returns
  3. Conversation History Management → tiktoken for token counting, newest-first loading
  4. Stateless Backend Architecture → FastAPI dependency injection for sessions
  5. Error Handling and Timeouts → Middleware-based timeout (5s), structured error responses
- All decisions documented with rationale, alternatives considered, and implementation guidance

**Phase 1: Design & Contracts**
- **data-model.md**: SQLModel schemas for Conversation and Message entities
  - Conversation: id (UUID), user_id (FK), created_at, updated_at
  - Message: id (UUID), conversation_id (FK), role (enum), content, created_at
  - Migration 003 SQL with foreign keys, indexes, and triggers
  - Query patterns for get_or_create, load_history, store_message
- **contracts/chat-api.yaml**: OpenAPI 3.0 specification
  - POST /api/chat endpoint with JWT authentication
  - Request/response schemas with examples
  - Error responses (401, 422, 500, 503, 504)
  - Tool invocation format
- **quickstart.md**: Developer setup guide
  - 10-step setup process (prerequisites → testing)
  - Gemini API key setup
  - Database migration instructions
  - curl examples for testing
  - Troubleshooting section
- **agent-context-update.md**: New technologies documentation
  - 7 major technologies: OpenAI Agents SDK, Gemini API, AsyncOpenAI, MCP, Stateless Backend, tiktoken, Conversation Management
  - Implementation patterns and code examples
  - Architecture principles and data flow

**Constitution Check**: ✅ ALL 9 PRINCIPLES PASSED
- Principle I: Spec-Driven Development ✅
- Principle II: JWT-Only Identity ✅
- Principle III: Database-Backed Persistence ✅
- Principle IV: Production-Grade Architecture ✅
- Principle V: Root-Cause Engineering ✅
- Principle VI: Clear Separation of Layers ✅
- Principle VII: MCP-Only Database Mutations ✅
- Principle VIII: Stateless Backend Architecture ✅
- Principle IX: AI Agent Orchestration ✅

### Key Technical Decisions

1. **Agent Execution**: Runner.run_sync (synchronous) - simpler, sufficient for 5s timeout
2. **Gemini Integration**: AsyncOpenAI with base_url="https://generativelanguage.googleapis.com/v1beta/openai"
3. **MCP Tools**: Function-based with Pydantic returns for structured data
4. **Token Counting**: tiktoken library for accurate token counting (2000 token limit)
5. **Session Management**: FastAPI dependency injection for per-request sessions
6. **Timeout**: Middleware-based (5 seconds global timeout)
7. **Error Handling**: Structured responses with user-friendly messages (no stack traces)

### Project Structure

```
backend/
├── app/
│   ├── routes/chat.py          # NEW: Chat endpoint
│   ├── ai/                     # NEW: Agent logic
│   │   ├── agent.py
│   │   ├── prompts.py
│   │   └── gemini_client.py
│   ├── mcp/                    # NEW: MCP server and tools
│   │   ├── server.py
│   │   └── tools.py
│   ├── services/               # NEW: Business logic
│   │   ├── conversation_service.py
│   │   └── message_service.py
│   └── models/                 # NEW: SQLModel schemas
│       ├── conversation.py
│       └── message.py
└── migrations/
    └── 003_create_chat_tables.sql  # NEW: Chat tables migration
```

## Outcome

- ✅ Impact: Generated comprehensive implementation plan for Backend Chat API + OpenAI Agent Orchestration on branch 006-backend-chat-api, including Phase 0 research (5 technical decisions), Phase 1 design artifacts (data model, API contracts, quickstart guide), and agent context update documenting 7 new technologies
- 🧪 Tests: Constitution Check - PASSED (9/9 principles validated)
- 📁 Files: 6 created (plan.md 350 lines, research.md 450 lines, data-model.md 520 lines, chat-api.yaml 280 lines, quickstart.md 480 lines, agent-context-update.md 180 lines)
- 🔁 Next prompts: Run `/sp.tasks` to generate tasks.md with dependency-ordered implementation tasks for 9 implementation phases (database schema, MCP tools, agent integration, chat endpoint, service layer, integration testing, documentation, deployment)
- 🧠 Reflection: Successfully completed planning phase following spec-driven workflow. All technical unknowns resolved in Phase 0 research with clear decisions and rationale. Phase 1 design artifacts provide complete implementation guidance: SQLModel schemas with migration SQL, OpenAPI contract with all error codes, quickstart guide with 10-step setup process, and agent context documenting new technologies. Constitution check passed all 9 principles including Phase-3 specific principles (MCP-only mutations, stateless backend, AI agent orchestration). Key architectural decisions documented: synchronous agent execution, Gemini integration via AsyncOpenAI, function-based MCP tools, tiktoken for token counting, FastAPI dependency injection for sessions, middleware-based timeouts. Ready for task generation phase.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning phase completed successfully with all artifacts generated and constitution checks passing
- Graders run and results (PASS/FAIL): Constitution Check - PASS (9/9 principles), Research Completeness - PASS (5/5 unknowns resolved), Design Artifacts - PASS (4/4 artifacts generated)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed with `/sp.tasks` to generate implementation tasks breakdown, focusing on dependency ordering (database → MCP tools → agent → endpoint → services → tests) and ensuring each task is independently testable with clear acceptance criteria
