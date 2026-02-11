# Implementation Plan: MCP Task Server + Database Layer

**Branch**: `001-mcp-task-server` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-mcp-task-server/spec.md`

## Summary

Implement an MCP (Model Context Protocol) server that exposes 5 stateless task management tools (add, list, update, complete, delete) for the OpenAI Agent to invoke. All tools persist data to the existing Neon PostgreSQL tasks table using SQLModel ORM, enforcing user isolation on every query. The MCP server uses the Official MCP SDK and operates independently of the FastAPI chat endpoint.

**Technical Approach**: Create a standalone MCP server process using the Official MCP SDK that registers 5 tool functions. Each tool receives user_id as a parameter, performs SQLModel database operations on the tasks table, and returns structured responses. The agent invokes these tools through the MCP protocol, never accessing the database directly.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- Official MCP SDK (`mcp[cli]` - latest version per clarification) - NEEDS RESEARCH: initialization patterns and tool registration API
- SQLModel 0.0.14+ (existing from Phase-2)
- FastAPI 0.104+ (existing, for potential HTTP transport)
- psycopg2 or asyncpg (existing database driver)

**Storage**: PostgreSQL (Neon Serverless) - existing tasks table from Phase-2
**Testing**: pytest (existing test infrastructure)
**Target Platform**: Linux server (same as existing backend)
**Project Type**: Backend service (extends existing FastAPI backend)

**Performance Goals**:
- Database operations <200ms (95th percentile) per spec SC-003
- Support 100 concurrent tool invocations per spec SC-004
- Connection pooling configured with pool_size=10, max_overflow=20 (per clarification)
- list_tasks queries <100ms for up to 1000 tasks per spec SC-008

**Constraints**:
- Stateless operation (no in-memory state between tool calls)
- User isolation enforced on every database query
- MCP tools are the ONLY components that mutate task data
- Agent never accesses database directly
- Must use existing tasks table schema from Phase-2
- list_tasks must support pagination via limit parameter (default 100, max 1000) per clarification
- list_tasks must return tasks ordered by created_at DESC (newest first) per clarification
- complete_task must be idempotent (safe to call multiple times) per clarification
- delete_task must be non-idempotent (returns error if already deleted) per clarification

**Scale/Scope**:
- 5 MCP tools to implement
- Single Task entity (existing)
- Supports existing user base from Phase-2
- No new database tables required

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Spec-First Development
- **Status**: PASS
- **Evidence**: Specification approved at `specs/001-mcp-task-server/spec.md` with 5 prioritized user stories, 15 functional requirements, and quality checklist validation

### ✅ II. Stateless Backend Architecture
- **Status**: PASS
- **Evidence**: Spec FR-011 requires "All MCP tools MUST be stateless - no in-memory state between invocations". All state persists in database per FR-003.

### ✅ III. AI-Driven Task Management Through MCP Tools Only
- **Status**: PASS
- **Evidence**: This feature IS the MCP layer. Spec explicitly states "The OpenAI Agent must never access the database directly. All task operations flow through stateless MCP tools" (Overview section). FR-009 enforces user_id on all operations.

### ✅ IV. JWT-Only Identity
- **Status**: PASS
- **Evidence**: Spec Assumptions #1 states "The user_id parameter is assumed to be authenticated and validated before reaching the MCP tools." MCP tools receive user_id from upstream JWT verification. FR-009 requires user_id parameter on all tools.

### ✅ V. Database as Single Source of Truth
- **Status**: PASS
- **Evidence**: FR-003 requires Neon PostgreSQL connection. FR-014 mandates SQLModel ORM for all operations. Spec explicitly prohibits mock data in Success Criteria SC-005 "System maintains zero in-memory state".

### ✅ VI. User Isolation
- **Status**: PASS
- **Evidence**: FR-009 "All MCP tools MUST require user_id parameter and filter all database queries by user_id". FR-010 "System MUST prevent cross-user access". All 5 user stories include acceptance scenarios testing user isolation.

### ✅ VII. No Premature Abstraction
- **Status**: PASS
- **Evidence**: MCP tools are simple functions that perform single operations (FR-015 "Each tool performs exactly one responsibility"). No unnecessary layers or patterns introduced.

**Constitution Check Result**: ✅ ALL GATES PASSED - Proceed to Phase 0 Research

## Clarifications Applied

The following clarifications were made during `/sp.clarify` session (2026-02-09) and have been integrated into this plan:

1. **MCP SDK Version**: Use latest version without version constraints (`mcp[cli]`)
   - Rationale: Maximum flexibility for updates, access to latest features

2. **Pagination Strategy**: Implement limit parameter for list_tasks (default 100, max 1000)
   - Rationale: Prevents performance issues with large result sets, simple API

3. **Idempotency Behavior**:
   - complete_task is idempotent (returns success even if already completed)
   - delete_task is non-idempotent (returns error if already deleted)
   - Rationale: Follows REST conventions, safer for retries

4. **Task Ordering**: list_tasks returns tasks ordered by created_at DESC (newest first)
   - Rationale: Most intuitive for users, shows recent tasks first

5. **Connection Pooling**: Configure with pool_size=10, max_overflow=20
   - Rationale: Balances resource usage with concurrency needs

These clarifications resolve ambiguities in the specification and provide concrete implementation guidance.

## Project Structure

### Documentation (this feature)

```text
specs/001-mcp-task-server/
├── spec.md              # Feature specification (COMPLETE)
├── plan.md              # This file (IN PROGRESS)
├── research.md          # Phase 0 output (TO BE CREATED)
├── data-model.md        # Phase 1 output (TO BE CREATED)
├── quickstart.md        # Phase 1 output (TO BE CREATED)
├── contracts/           # Phase 1 output (TO BE CREATED)
│   ├── add_task.md
│   ├── list_tasks.md
│   ├── update_task.md
│   ├── complete_task.md
│   └── delete_task.md
├── checklists/
│   └── requirements.md  # Spec quality checklist (COMPLETE)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT YET)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py                    # Existing FastAPI app
│   ├── config.py                  # Existing config (DATABASE_URL)
│   ├── database.py                # Existing SQLModel engine
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py                # Existing Task model (Phase-2)
│   │   ├── conversation.py        # Existing (Phase-3 Spec-2)
│   │   └── message.py             # Existing (Phase-3 Spec-2)
│   ├── routes/
│   │   ├── tasks.py               # Existing CRUD endpoints (Phase-2)
│   │   └── chat.py                # Existing chat endpoint (Phase-3 Spec-2)
│   ├── services/
│   │   └── ai_agent.py            # Existing AI service (Phase-3 Spec-2)
│   └── mcp/                       # NEW: MCP server and tools
│       ├── __init__.py            # NEW: MCP exports
│       ├── server.py              # NEW: MCP server initialization
│       └── tools/                 # NEW: MCP tool implementations
│           ├── __init__.py
│           ├── add_task.py        # NEW: add_task tool
│           ├── list_tasks.py      # NEW: list_tasks tool
│           ├── update_task.py     # NEW: update_task tool
│           ├── complete_task.py   # NEW: complete_task tool
│           └── delete_task.py     # NEW: delete_task tool
├── tests/
│   ├── test_mcp_tools.py          # NEW: MCP tool unit tests
│   └── test_mcp_integration.py    # NEW: MCP integration tests
└── requirements.txt               # UPDATE: Add mcp SDK

scripts/
└── run_mcp_server.py              # NEW: MCP server startup script
```

**Structure Decision**: Backend-only extension to existing Phase-2/Phase-3 codebase. MCP server lives in `backend/app/mcp/` as a separate module from the FastAPI application. MCP tools are organized by operation in `backend/app/mcp/tools/` for clarity and maintainability. The MCP server can run as a standalone process or be integrated with the FastAPI app depending on MCP SDK architecture (to be determined in research phase).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution principles are satisfied by this design.

## Phase 0: Research & Technical Decisions

**Status**: TO BE COMPLETED

Research tasks to resolve NEEDS CLARIFICATION items:

1. **Official MCP SDK Research**
   - ✅ Package name and installation: `mcp[cli]` latest version (clarified)
   - Server initialization patterns
   - Tool registration API
   - Parameter and return value schemas
   - Error handling conventions
   - Transport mechanisms (stdio, HTTP, WebSocket)

2. **MCP Tool Implementation Patterns**
   - Function signature requirements
   - Parameter validation approaches
   - Response format standards
   - Error response structures
   - Async vs sync tool functions

3. **MCP Server Lifecycle**
   - How to start/stop the server
   - How agent connects to server
   - Process management (standalone vs embedded)
   - Configuration requirements

4. **Integration with Existing Backend**
   - Can MCP server share SQLModel engine with FastAPI?
   - Should MCP server run as separate process or embedded?
   - How to pass user_id from agent to tools?
   - ✅ Connection pooling: pool_size=10, max_overflow=20 (clarified)

5. **Testing Strategies**
   - How to unit test MCP tools
   - How to integration test with mock agent
   - How to verify user isolation
   - Performance testing approaches

**Output**: `research.md` with decisions and rationale for each area

## Phase 1: Design Artifacts

**Status**: TO BE COMPLETED AFTER RESEARCH

### 1. Data Model (`data-model.md`)

Document the existing Task entity structure and how MCP tools interact with it:

- Task entity fields (from Phase-2)
- SQLModel model definition
- Database constraints
- Query patterns for user isolation
- Index usage for performance

### 2. Tool Contracts (`contracts/`)

Create detailed specifications for each of the 5 MCP tools:

- **add_task.md**: Parameters, return value, error cases, examples
- **list_tasks.md**: Parameters (including limit for pagination), return value, filtering logic, ordering (created_at DESC), examples
- **update_task.md**: Parameters, return value, partial update handling, examples
- **complete_task.md**: Parameters, return value, idempotency behavior (safe to call multiple times), examples
- **delete_task.md**: Parameters, return value, non-idempotent behavior (error on re-delete), examples

Each contract includes:
- Tool name and purpose
- Input schema (JSON schema or equivalent)
- Output schema
- Error codes and messages
- Usage examples
- Edge case handling
- Idempotency behavior (for complete_task and delete_task)
- Pagination details (for list_tasks)

### 3. Quickstart Guide (`quickstart.md`)

Step-by-step instructions for:
- Installing MCP SDK
- Configuring MCP server
- Starting MCP server
- Testing tools with mock agent
- Verifying database persistence
- Troubleshooting common issues

### 4. Agent Context Update

Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude` to add:
- MCP SDK to technology stack
- MCP tool patterns to context
- User isolation requirements

## Phase 2: Task Breakdown

**Status**: NOT STARTED (requires `/sp.tasks` command)

After Phase 1 design is complete, run `/sp.tasks` to generate actionable task breakdown organized by user story priority (P1-P5).

## Implementation Strategy

### Incremental Delivery Approach

1. **Phase 1 (P1 - MVP)**: Implement `add_task` tool only
   - Validates MCP SDK integration
   - Proves database connectivity
   - Tests user isolation
   - Deliverable: Agent can create tasks

2. **Phase 2 (P2)**: Add `list_tasks` tool
   - Enables task retrieval
   - Tests filtering logic
   - Deliverable: Agent can view tasks

3. **Phase 3 (P3)**: Add `complete_task` tool
   - Enables task completion workflow
   - Tests update operations
   - Deliverable: Agent can mark tasks done

4. **Phase 4 (P4)**: Add `update_task` tool
   - Enables task editing
   - Tests partial updates
   - Deliverable: Agent can modify tasks

5. **Phase 5 (P5)**: Add `delete_task` tool
   - Enables task removal
   - Tests delete operations
   - Deliverable: Agent can remove tasks

Each phase is independently testable and deployable per spec user story design.

### Testing Strategy

1. **Unit Tests**: Test each tool function in isolation with mock database
2. **Integration Tests**: Test tools with real database and mock agent calls
3. **User Isolation Tests**: Verify cross-user access prevention
4. **Performance Tests**: Validate <200ms operation time
5. **Concurrency Tests**: Verify 100 concurrent operations

### Deployment Considerations

- MCP server runs as separate process from FastAPI (likely)
- Shares DATABASE_URL configuration with existing backend
- Connection pool configured with pool_size=10, max_overflow=20 (per clarification)
- Monitored separately from HTTP endpoints
- Logs to same logging infrastructure
- list_tasks pagination prevents memory issues with large result sets
- Idempotent complete_task enables safe retry logic in agent

## Risk Assessment

| Risk | Impact | Mitigation | Status |
|------|--------|------------|--------|
| MCP SDK documentation incomplete | High | Research multiple sources, check examples, ask community | Active |
| MCP server process management complexity | Medium | Start with simple standalone process, optimize later | Active |
| Performance degradation from separate process | Medium | Use pool_size=10, max_overflow=20; benchmark early | ✅ Mitigated by clarification |
| User_id passing mechanism unclear | High | Research MCP context/metadata patterns, document in research.md | Active |
| Existing tasks table schema incompatible | Low | Schema already validated in Phase-2, no changes needed | ✅ Resolved |
| Large task lists causing performance issues | Medium | Implement pagination with limit parameter (default 100, max 1000) | ✅ Mitigated by clarification |
| Retry logic complexity for operations | Low | complete_task is idempotent, safe for retries | ✅ Mitigated by clarification |

## Success Criteria Mapping

Mapping spec success criteria to implementation validation:

- **SC-001** (100% persistence): Integration tests verify all operations persist
- **SC-002** (0% cross-user leakage): User isolation tests with multiple users
- **SC-003** (<200ms operations): Performance tests with database profiling
- **SC-004** (100 concurrent requests): Load tests with concurrent tool calls
- **SC-005** (zero in-memory state): Server restart tests verify no data loss
- **SC-006** (all operations functional): Integration tests cover all 5 tools
- **SC-007** (clear error messages): Error case tests verify message quality
- **SC-008** (<100ms list queries): Performance tests for list_tasks with 1000 tasks

## Next Steps

1. ✅ Complete this plan document
2. ✅ Apply clarifications from `/sp.clarify` session (5 clarifications integrated)
3. ⏳ Execute Phase 0: Research MCP SDK and create `research.md`
4. ⏳ Execute Phase 1: Create `data-model.md`, `contracts/`, `quickstart.md`
5. ⏳ Update agent context with MCP patterns
6. ⏳ Run `/sp.tasks` to generate task breakdown
7. ⏳ Implement tasks following incremental delivery approach

---

**Plan Status**: ✅ Updated with clarifications from spec session (2026-02-09)
**Clarifications Applied**: 5 (MCP SDK version, pagination, idempotency, ordering, connection pooling)
**Ready for**: Phase 0 research execution or direct task generation via `/sp.tasks`
