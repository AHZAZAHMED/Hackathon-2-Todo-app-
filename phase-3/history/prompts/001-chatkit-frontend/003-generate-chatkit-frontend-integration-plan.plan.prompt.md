---
id: PHR-003
title: Generate ChatKit frontend integration plan
stage: plan
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5
feature: 001-chatkit-frontend
branch: 001-chatkit-frontend
user: PMYLS
command: /sp.plan
labels: [plan, chatkit, frontend, phase-3, openai-chatkit, research, design]
links:
  spec: specs/001-chatkit-frontend/spec.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - path: specs/001-chatkit-frontend/plan.md
    status: created
    lines_changed: 450
  - path: specs/001-chatkit-frontend/research.md
    status: created
    lines_changed: 280
  - path: specs/001-chatkit-frontend/data-model.md
    status: created
    lines_changed: 320
  - path: specs/001-chatkit-frontend/contracts/chat-api.md
    status: created
    lines_changed: 380
  - path: specs/001-chatkit-frontend/quickstart.md
    status: created
    lines_changed: 420
tests:
  - name: Constitution Check
    status: PASS
---

## Prompt

```
/sp.plan

Scope:
Frontend ChatKit UI only.

Tasks:

1. Install and configure OpenAI ChatKit in existing frontend
2. Create floating chat icon component (fixed bottom-right position, always visible)
3. Implement chat window (opens above icon, fixed width ~360-420px, fixed height ~500-600px, rounded container, close button, never fullscreen)
4. Wire ChatKit message handler (send POST to ${NEXT_PUBLIC_API_BASE_URL}/api/chat, include Authorization: Bearer <JWT>)
5. Integrate Better Auth (extract JWT from existing auth system, attach automatically to chat requests)
6. Configure environment variables (NEXT_PUBLIC_API_BASE_URL, NEXT_PUBLIC_OPENAI_DOMAIN_KEY)
7. UI safeguards (prevent icon from being covered, prevent blank popup, display loading state, display backend errors)
8. Styling polish (z-index above page content, mobile responsive sizing, scrollable message panel)
9. Playwright validation (open app, click chat icon, send message, verify response)
```

## Response snapshot

Generated comprehensive implementation plan for ChatKit Frontend Integration with complete Phase 0 research and Phase 1 design artifacts.

**Planning Artifacts Created**:

1. **plan.md** (450 lines):
   - Technical context (TypeScript, Next.js 16+, OpenAI ChatKit, Better Auth JWT)
   - Constitution check (all applicable principles satisfied)
   - Project structure (web application, frontend-only)
   - 8 implementation phases (1.1 → 1.8)
   - Risk assessment and mitigation strategies
   - Success criteria mapping (10 criteria)
   - Dependencies and blockers analysis

2. **research.md** (280 lines):
   - 5 research questions resolved
   - Technology decisions documented
   - Implementation approaches defined
   - Alternatives considered and rejected
   - Risks identified with mitigations

3. **data-model.md** (320 lines):
   - 3 entities defined (ChatMessage, ChatSession, ChatStorageState)
   - Full TypeScript definitions
   - Validation rules and state transitions
   - Storage strategy (session storage)
   - Data flow diagrams

4. **contracts/chat-api.md** (380 lines):
   - POST /api/chat endpoint specification
   - Request/response formats
   - Error handling (401, 422, 500, 503)
   - Authentication flow
   - Security considerations
   - Mock response for development

5. **quickstart.md** (420 lines):
   - Step-by-step setup instructions
   - 8 implementation phases with verification steps
   - Testing checklist (manual + automated)
   - Troubleshooting guide
   - Deployment checklist

**Key Decisions**:

1. **ChatKit Integration**: Use OpenAI ChatKit with custom API endpoints (package name TBD)
2. **Session Storage**: Use sessionStorage API for state persistence across navigations
3. **JWT Extraction**: Reuse existing Phase-2 API client for consistency
4. **Error Handling**: Three-tier strategy (network, auth, server) with inline retry
5. **Z-Index Management**: Fixed positioning with z-9999 for chat components

**Implementation Phases**:

- Phase 1.1: Setup & Dependencies (ChatKit install, env vars, types)
- Phase 1.2: Chat State Management (storage utilities, hooks, context)
- Phase 1.3: Chat UI Components (icon, window, messages, input, retry)
- Phase 1.4: Chat API Integration (client, JWT, error handling, loading)
- Phase 1.5: Authentication Integration (provider, redirect, token expiry)
- Phase 1.6: State Persistence (window state, conversation preservation)
- Phase 1.7: Styling & Polish (Tailwind, z-index, responsive, scrolling)
- Phase 1.8: Playwright Validation (automated tests, regression)

**Constitution Check**: ✅ PASS
- Spec-first development: Specification approved, clarifications resolved
- JWT-only identity: Will use existing Better Auth JWT
- Production-grade quality: TypeScript strict, Tailwind, env vars, error handling
- Clear separation of layers: Frontend-only scope, no cross-layer bleeding
- No Phase-2 disruption: FR-012 preserves existing functionality

**Complexity**: Medium (frontend-only, well-defined scope, existing infrastructure)

**Ready for `/sp.tasks`**: ✅ Yes

## Outcome

- ✅ Impact: Complete implementation plan with 5 design artifacts (plan, research, data model, API contract, quickstart), 8 implementation phases, constitution compliance verified, ready for task breakdown
- 🧪 Tests: Constitution Check - PASS (all applicable principles satisfied)
- 📁 Files: Created 5 files (plan.md, research.md, data-model.md, contracts/chat-api.md, quickstart.md) totaling ~1850 lines
- 🔁 Next prompts: Run /sp.tasks to generate detailed task breakdown organized by user story (P1-P4)
- 🧠 Reflection: Planning phase complete with comprehensive research resolving all technical unknowns (ChatKit integration, session storage, JWT extraction, error handling, z-index). All design artifacts follow spec requirements and constitution principles. Frontend-only scope clearly bounded with no backend/MCP/agent implementation.

## Evaluation notes (flywheel)

- Failure modes observed: Agent context update script failed (template missing) - non-blocking, optional enhancement
- Graders run and results (PASS/FAIL): Constitution Check - PASS
- Prompt variant (if applicable): Standard /sp.plan workflow with Phase 0 research and Phase 1 design
- Next experiment (smallest change to try): Proceed to /sp.tasks to validate that plan provides sufficient detail for unambiguous task breakdown
