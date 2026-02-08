---
id: PHR-002
title: Update Constitution to Phase-3
stage: constitution
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: N/A
branch: master
user: system
command: /sp.constitution
labels: [constitution, phase-3, governance, mcp, ai-chatbot]
links:
  spec: specs/004-ai-chatbot/spec.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - path: .specify/memory/constitution.md
    status: modified
    lines_added: 250
    lines_removed: 0
tests:
  - name: N/A
    status: N/A
---

## Prompt

User requested constitution update for Phase-3 AI Chatbot with the following requirements:

**Core Principles:**
1. Specification precedes implementation
2. No manual coding by human
3. All features originate from /sp.specify
4. All execution plans originate from /sp.plan
5. No deviation from official Phase-3 requirements

**Architecture Rules:**
- Frontend: OpenAI ChatKit UI
- Backend: FastAPI, Stateless POST /api/chat
- AI Layer: OpenAI Agents SDK (intent analysis only, never accesses database)
- MCP Layer: Official MCP SDK with 5 tools (add_task, list_tasks, complete_task, delete_task, update_task)
- Database: SQLModel ORM, Neon PostgreSQL

**MCP Enforcement:**
- MCP tools are the ONLY components permitted to modify the database
- All task CRUD operations MUST be implemented inside MCP tools
- Chat endpoint orchestrates only
- Agent selects tools only
- Database writes occur ONLY inside MCP tools

**Database Tables:**
- tasks (user_id, id, title, description, completed, created_at, updated_at) - EXISTING
- conversations (user_id, id, created_at, updated_at) - NEW
- messages (user_id, id, conversation_id, role, content, created_at) - NEW

**Authentication:**
- Better Auth JWT
- user_id extracted from token only
- Frontend never provides user_id

**Conversation Flow (Stateless):**
1. Receive message
2. Load conversation from DB
3. Store user message
4. Run agent
5. Agent invokes MCP tools
6. MCP tools modify DB
7. Store assistant message
8. Return response
9. Server holds no state

**Forbidden:**
- Direct DB access by agent
- Direct task writes in chat endpoint
- In-memory storage
- Mock APIs
- Placeholder logic
- OAuth, Analytics, Phase-4 features

**Success Criteria:**
- Chatbot manages tasks via natural language
- MCP tools perform all task persistence
- Conversation resumes after restart
- Stateless server confirmed
- Full CRUD

## Response snapshot

Updated constitution from v1.0.0 to v1.1.0 (MINOR version bump).

**Added 3 New Principles:**
- Principle VII: MCP-Only Database Mutations (NON-NEGOTIABLE - PHASE-3)
- Principle VIII: Stateless Backend Architecture (NON-NEGOTIABLE - PHASE-3)
- Principle IX: AI Agent Orchestration (NON-NEGOTIABLE - PHASE-3)

**Modified Existing Principles:**
- Principle II (JWT-Only Identity): Added chat endpoint requirement
- Principle III (Database-Backed Persistence): Added conversations and messages tables, no in-memory conversation state
- Principle VI (Clear Separation of Layers): Expanded to include AI Agent and MCP layers

**Added New Sections:**
- Phase-3 Architecture Law (complete system flow, MCP tool architecture)
- Phase-3 Database tables (conversations, messages with SQLModel)
- Phase-3 Quality Gates (MCP Server, AI Agent, Chat Endpoint, Database Schema, Frontend Chat UI, Integration)
- Forbidden Practices section (comprehensive list of prohibited patterns)
- Success Criteria section (10 criteria for Phase-3 completion)

**Preserved Phase-2:**
- All Phase-2 principles remain intact
- Phase-2 architecture documented as "STABLE FOUNDATION"
- Phase-2 quality gates marked as COMPLETE
- No breaking changes to Phase-2 rules

**Version Bump Rationale:**
MINOR (1.0.0 → 1.1.0) because:
- New principles added (VII, VIII, IX)
- Materially expanded guidance (Phase-3 architecture, quality gates)
- No backward-incompatible changes
- Phase-2 foundation preserved

## Outcome

- ✅ Impact: Constitution updated to v1.1.0 with comprehensive Phase-3 AI Chatbot principles
- 🧪 Tests: N/A (constitution is governance document)
- 📁 Files: 1 modified (.specify/memory/constitution.md)
- 🔁 Next prompts: /sp.specify (create AI chatbot specification)
- 🧠 Reflection: Successfully integrated Phase-3 requirements while preserving Phase-2 as stable foundation. Clear separation between orchestration (agent), execution (MCP), and persistence (database) enforced through constitutional principles.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual review - PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed with /sp.specify to create Phase-3 AI chatbot specification following the updated constitution
