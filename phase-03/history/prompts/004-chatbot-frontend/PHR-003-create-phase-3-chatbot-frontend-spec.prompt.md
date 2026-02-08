---
id: PHR-003
title: Create Phase-3 Chatbot Frontend Spec
stage: spec
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: 004-chatbot-frontend
branch: 004-chatbot-frontend
user: system
command: /sp.specify
labels: [spec, phase-3, chatbot, frontend, openai-chatkit]
links:
  spec: specs/004-chatbot-frontend/spec.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - path: specs/004-chatbot-frontend/spec.md
    status: created
    lines_added: 350
    lines_removed: 0
  - path: specs/004-chatbot-frontend/checklists/requirements.md
    status: created
    lines_added: 50
    lines_removed: 0
tests:
  - name: Specification Quality Validation
    status: PASSED
---

## Prompt

User requested specification for Phase-3 Chatbot Frontend (OpenAI ChatKit UI):

**Feature**: Phase-3 Chatbot Frontend (OpenAI ChatKit UI)

**Context**:
- Phase-2 frontend, authentication, backend API, and database are complete and stable
- Phase-3 introduces an AI-powered chatbot
- This specification defines ONLY the chatbot frontend using OpenAI ChatKit
- No backend, agent, MCP, or database logic belongs here

**Objective**:
Specify a production-ready ChatKit-based frontend that provides a conversational interface for managing todos via the Phase-3 chat API. The frontend must integrate with Better Auth JWT and communicate exclusively with POST /api/chat.

**Key Differences from Phase-2**:
- Phase-2: Frontend hits task APIs directly
- Phase-3: Frontend NEVER touches task APIs, only /api/chat
- Backend + agent + MCP handle everything

**In Scope**:
- ChatKit UI integration
- Chat input + message display
- POST /api/chat communication
- JWT attached to chat requests
- Loading and error states
- Conversation rendering
- OpenAI domain allowlist support
- NEXT_PUBLIC_OPENAI_DOMAIN_KEY usage

**Out of Scope**:
- AI logic, OpenAI Agents SDK
- MCP server, Task tools
- Database models, Conversation persistence
- Backend implementation

**Functional Requirements**:
- Single chatbot interface
- User message input, Assistant message display
- Streaming or progressive responses
- Clear visual separation of user/assistant messages
- Professional layout
- All messages sent via POST /api/chat
- JWT automatically included
- user_id never manually supplied
- Unauthenticated users redirected to login
- Environment variables: NEXT_PUBLIC_API_BASE_URL, NEXT_PUBLIC_OPENAI_DOMAIN_KEY
- Must work locally and in production

## Response snapshot

Created comprehensive Phase-3 Chatbot Frontend specification with:

**3 Prioritized User Stories**:
1. P1: Send and Receive Chat Messages (core functionality)
2. P2: View Conversation History (context and continuity)
3. P3: Handle Errors Gracefully (polish and UX)

**18 Functional Requirements** (FR-001 to FR-018):
- OpenAI ChatKit integration
- Message input/display with visual distinction
- POST /api/chat endpoint communication
- Automatic JWT attachment
- Loading indicators and error messages
- Authentication redirect
- Conversation history loading
- Auto-scroll to latest message
- Environment variable configuration
- Cross-environment support (local + production)
- Empty message prevention
- Streaming/progressive response support

**10 Success Criteria** (SC-001 to SC-010):
- Message send/receive under 5 seconds (95th percentile)
- 90% first-attempt success rate for todo tasks via chat
- Conversation history loads under 2 seconds
- Error messages appear within 1 second
- Support 50+ messages without performance degradation
- Cross-browser compatibility (desktop + mobile)
- 100% authentication enforcement
- 100% conversation persistence across refreshes
- Clear visual distinction between user/assistant messages
- Graceful error handling with no technical jargon

**Additional Sections**:
- Edge cases (6 scenarios)
- Non-functional requirements (performance, security, usability, compatibility)
- Assumptions (8 documented)
- Dependencies (external, internal, environment variables)
- Out of scope (13 explicit exclusions)
- Technical constraints (10 constraints)
- Risks & mitigations (5 risks with mitigation strategies)

**Validation**:
- Created specification quality checklist
- All 16 validation items PASSED
- No [NEEDS CLARIFICATION] markers
- All requirements testable and unambiguous
- Success criteria measurable and technology-agnostic
- Ready for /sp.plan

## Outcome

- ✅ Impact: Complete Phase-3 Chatbot Frontend specification created on branch 004-chatbot-frontend
- 🧪 Tests: Specification quality validation - PASSED (16/16 items)
- 📁 Files: 2 created (spec.md, checklists/requirements.md)
- 🔁 Next prompts: /sp.plan (generate implementation plan)
- 🧠 Reflection: Successfully separated frontend concerns from backend implementation. Clear scope boundaries prevent feature creep. All user stories independently testable with clear priorities. Specification is production-ready and aligns with Phase-3 constitution principles.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Specification Quality Checklist - PASS (16/16)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed with /sp.plan to generate implementation plan with ChatKit integration details
