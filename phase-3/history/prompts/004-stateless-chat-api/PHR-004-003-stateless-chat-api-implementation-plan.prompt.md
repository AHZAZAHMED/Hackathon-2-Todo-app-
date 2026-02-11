---
id: PHR-004-003
title: Stateless Chat API Implementation Plan
stage: plan
date: 2026-02-09T19:30:00Z
surface: agent
model: claude-sonnet-4-5
feature: 004-stateless-chat-api
branch: 004-stateless-chat-api
user: PMYLS
command: /sp.plan
labels: [planning, backend, chat-api, openai-agents, openrouter, architecture]
links:
  spec: specs/004-stateless-chat-api/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - path: specs/004-stateless-chat-api/plan.md
    status: created
    lines: 350
  - path: specs/004-stateless-chat-api/research.md
    status: created
    lines: 420
  - path: specs/004-stateless-chat-api/data-model.md
    status: created
    lines: 380
  - path: specs/004-stateless-chat-api/contracts/chat-api.md
    status: created
    lines: 520
  - path: specs/004-stateless-chat-api/quickstart.md
    status: created
    lines: 580
tests:
  - name: Constitution Check
    status: passed
    coverage: All Phase-2 and Phase-3 principles satisfied
---

## Prompt

User invoked `/sp.plan` with detailed implementation requirements:

```
Feature: Phase-3 Spec-2 — Backend Chat API + OpenAI Agent Orchestration

Objective:
Implement the FastAPI backend chat endpoint that authenticates users via Better Auth JWT, persists conversation history, runs OpenAI Agents SDK (using third-party LLM provider with OpenRouter API and Gemini model), and returns assistant responses. This spec does NOT include MCP or task CRUD.

Scope:
- FastAPI POST /api/chat
- JWT verification
- Conversation + Message persistence
- OpenAI Agents SDK orchestration
- Stateless request cycle

Explicitly Out of Scope:
- MCP server
- MCP tools
- Task CRUD
- Task database models
- Tool calling
(All deferred to Spec-3)
```

## Response snapshot

**Planning Complete**: Generated comprehensive implementation plan with 5 design artifacts

**Phase 0: Research (research.md)**
- Resolved 5 technical unknowns
- OpenRouter API integration: Use AsyncOpenAI with OpenRouter base URL
- OpenAI Agents SDK: Direct chat.completions.create() for tool-less conversation
- SQLModel async patterns: AsyncSession with connection pooling
- JWT verification: PyJWT with HS256 algorithm
- Database migrations: Raw SQL following existing project pattern

**Phase 1: Design & Contracts**
1. **Data Model (data-model.md)**:
   - Conversation entity: id, user_id, title, created_at, updated_at
   - Message entity: id, conversation_id, role, content, created_at
   - Foreign key constraints with CASCADE delete
   - Indexes for query performance
   - SQLModel class definitions

2. **API Contract (contracts/chat-api.md)**:
   - POST /api/chat specification
   - Request schema: message (required), conversation_id (optional)
   - Response schema: conversation_id, response, timestamp
   - Error responses: 401, 422, 500, 503
   - Authentication requirements and security considerations

3. **Quickstart Guide (quickstart.md)**:
   - 8-step implementation guide
   - Environment setup and dependencies
   - Database migration instructions
   - Model implementation examples
   - AI agent service setup
   - Chat endpoint implementation
   - Testing procedures
   - Troubleshooting guide

**Constitution Check**: ✅ PASS
- All Phase-2 principles satisfied
- All Phase-3 principles satisfied
- MCP deferral justified (chat-only scope)
- Stateless architecture enforced
- JWT-only identity maintained

**Technical Decisions**:
- Language: Python 3.11+
- Framework: FastAPI with async/await
- Database: PostgreSQL (Neon) with SQLModel ORM
- AI Provider: OpenRouter API with Gemini model
- Authentication: PyJWT for Better Auth token verification
- Migration: Raw SQL scripts (consistent with existing pattern)

**Risk Assessment**:
- 8 risks identified (3 high, 2 medium, 3 low)
- Mitigation strategies defined for each
- Fallback plans documented

## Outcome

- ✅ Impact: Complete implementation plan for stateless chat API with OpenAI Agents SDK integration. Includes research, data model, API contracts, and quickstart guide. Ready for task generation.
- 🧪 Tests: Constitution check passed. All principles satisfied. MCP deferral justified.
- 📁 Files: Created 5 artifacts - plan.md (350 lines), research.md (420 lines), data-model.md (380 lines), contracts/chat-api.md (520 lines), quickstart.md (580 lines)
- 🔁 Next prompts: `/sp.tasks` to generate task breakdown for implementation
- 🧠 Reflection: Planning successfully resolved all technical unknowns and established clear implementation path. OpenRouter integration provides cost-effective AI access. Stateless architecture ensures scalability. Ready for task-driven implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None. All research questions resolved successfully.
- Graders run and results (PASS/FAIL): Constitution Check - PASS (all principles satisfied)
- Prompt variant (if applicable): Standard /sp.plan workflow with Phase 0 research and Phase 1 design
- Next experiment (smallest change to try): Consider adding conversation title auto-generation in future iterations
