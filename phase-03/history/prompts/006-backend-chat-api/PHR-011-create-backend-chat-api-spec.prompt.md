---
id: PHR-011
title: Create Backend Chat API Spec
stage: spec
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: 006-backend-chat-api
branch: 006-backend-chat-api
user: system
command: /sp.specify
labels: [specification, backend, chat-api, openai-agent, gemini, mcp-tools]
links:
  spec: specs/006-backend-chat-api/spec.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - path: specs/006-backend-chat-api/spec.md
    status: created
    lines_added: 496
    lines_removed: 0
  - path: specs/006-backend-chat-api/checklists/requirements.md
    status: created
    lines_added: 60
    lines_removed: 0
tests:
  - name: Specification Quality Validation
    status: PASSED
---

## Prompt

User requested creation of a new specification for Backend Chat API + OpenAI Agent Orchestration using Gemini 2.0 Flash (free LLM).

**Command**: `/sp.specify`

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

**User Preferences**:
- Skip streaming implementation
- Use structured data (Task objects) from MCP tools
- Backend auto-creates and manages conversation_id
- Token-based history (2000 tokens)
- Hardcoded agent configuration
- Standard status codes for errors
- Errors visible in chat UI

## Response snapshot

Successfully created comprehensive specification for 006-backend-chat-api feature with 5 prioritized user stories, 34 functional requirements, and complete API contract.

### Specification Details

**Feature**: Backend Chat API + OpenAI Agent Orchestration
**Branch**: 006-backend-chat-api
**Status**: Draft - Ready for Planning

**User Stories** (5 total):
1. Send Chat Message and Receive AI Response (P1) - Core functionality
2. Maintain Conversation Context (P1) - History persistence
3. AI Agent Invokes MCP Tools for Task Operations (P1) - Tool integration
4. Handle Authentication and Authorization (P2) - Security
5. Handle Errors Gracefully (P2) - Error handling

**Requirements**:
- 34 Functional Requirements (FR-001 to FR-034)
- Organized by category: API Endpoint, Authentication, Conversation Management, AI Agent Integration, MCP Tool Integration, Error Handling, Performance
- All requirements testable and unambiguous

**Success Criteria**:
- 10 measurable outcomes (SC-001 to SC-010)
- All technology-agnostic and user-focused
- Performance targets: <5s response time, 50 concurrent requests, 85% intent accuracy

**Edge Cases**: 8 identified scenarios including token limits, rate limits, concurrency, timeouts, and error handling

**API Contract**: Complete request/response formats with all HTTP status codes and error messages

**Database Schema**: SQL definitions for conversations and messages tables with proper indexes and foreign keys

**MCP Tool Signatures**: Documented expected interface for 5 tools (add_task, list_tasks, complete_task, delete_task, update_task)

**Scope**: Backend API only - explicitly excludes frontend UI, MCP tool implementation, streaming, multi-modal, conversation branching

**Key Technical Decisions**:
- Use OpenAI Agents SDK with AsyncOpenAI client configured for Gemini API endpoint
- Gemini 2.0 Flash model (gemini-2.0-flash) for free LLM
- Stateless backend - all conversation state in database
- Single conversation per user (auto-created on first message)
- Last 2000 tokens of conversation history loaded for context
- No streaming - complete response returned
- Standard HTTP status codes (401, 422, 500, 503, 504)

### Quality Validation

All 16 checklist items passed:
- ✅ No implementation details
- ✅ Focused on user value
- ✅ Written for non-technical stakeholders
- ✅ All mandatory sections completed
- ✅ No clarifications needed
- ✅ Requirements testable and unambiguous
- ✅ Success criteria measurable and technology-agnostic
- ✅ All acceptance scenarios defined
- ✅ Edge cases identified
- ✅ Scope clearly bounded
- ✅ Dependencies and assumptions documented

## Outcome

- ✅ Impact: Created comprehensive specification for backend chat API with OpenAI Agent SDK + Gemini 2.0 Flash integration on branch 006-backend-chat-api, defining POST /api/chat endpoint with JWT authentication, conversation persistence, and MCP tool orchestration
- 🧪 Tests: Specification Quality Validation - PASSED (16/16 items)
- 📁 Files: 2 created (spec.md with 496 lines, checklists/requirements.md with 60 lines)
- 🔁 Next prompts: Run `/sp.plan` to generate implementation plan for backend chat API, agent configuration, and database schema
- 🧠 Reflection: Successfully created specification following spec-driven workflow. All 5 user stories prioritized (3 P1 critical, 2 P2 enhancements) with clear acceptance criteria. Key technical approach documented: OpenAI Agents SDK with Gemini 2.0 Flash via AsyncOpenAI client. API contract fully specified with request/response formats and all error codes. Database schema provided with proper constraints. MCP tool signatures documented for agent integration (to be implemented in next spec). No clarifications needed - all requirements testable and unambiguous. Ready for planning phase.

## Evaluation notes (flywheel)

- Failure modes observed: None - specification created successfully with all quality checks passing
- Graders run and results (PASS/FAIL): Specification Quality Validation - PASS (16/16 items)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed with `/sp.plan` to generate implementation plan focusing on FastAPI endpoint structure, OpenAI Agents SDK configuration with Gemini, conversation management, and database migrations
