---
id: PHR-001
title: Create ChatKit frontend integration spec
stage: spec
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5
feature: 001-chatkit-frontend
branch: 001-chatkit-frontend
user: PMYLS
command: /sp.specify
labels: [spec, chatkit, frontend, phase-3, openai-chatkit]
links:
  spec: specs/001-chatkit-frontend/spec.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - path: specs/001-chatkit-frontend/spec.md
    status: created
    lines_changed: 280
  - path: specs/001-chatkit-frontend/checklists/requirements.md
    status: created
    lines_changed: 60
tests:
  - name: Specification Quality Validation
    status: PASS
---

## Prompt

```
Feature: Phase-3 Spec-1 — ChatKit Frontend Integration

Context:
This spec implements the frontend chatbot interface using OpenAI ChatKit. It provides a floating chat icon that opens a properly sized chat window and allows authenticated users to send messages to the backend POST /api/chat endpoint.

Phase-2 frontend and Better Auth are already implemented and must remain unchanged.

This spec is frontend-only and must not implement backend, MCP, agent logic, or database features.

User Stories:

P1 — Open chatbot UI
As an authenticated user, I want to click a chat icon and open a properly positioned chatbot window so I can talk to the AI assistant.

P2 — Send message to backend
As an authenticated user, I want to send chat messages to POST /api/chat and receive AI responses.

P3 — Secure requests
All chat requests must include Better Auth JWT automatically.

P4 — UI usability
The chat window must:
- Appear above the chat icon
- Have reasonable width/height
- Be closable
- Never hide the chat icon
- Never open full screen
- Never show blank black/white screens

Functional Requirements:

FR-001 Integrate OpenAI ChatKit UI
FR-002 Floating chat icon visible on all pages
FR-003 Chat window opens above icon with fixed size
FR-004 Close button always accessible
FR-005 POST requests sent only to /api/chat
FR-006 JWT automatically attached to requests
FR-007 Environment variables supported:
- NEXT_PUBLIC_API_BASE_URL
- NEXT_PUBLIC_OPENAI_DOMAIN_KEY
FR-008 Graceful UI error display when backend unreachable
FR-009 Playwright validation via browsing-with-playwright skill

Constraints:
- Frontend only
- No MCP
- No Agents SDK
- No database
- No task logic
- No conversation persistence
- No mock data
- No layout breaking
- No fullscreen popup

Success Criteria:
- Chat opens cleanly
- Icon remains visible
- Window properly sized
- Messages reach backend
- JWT included
- Responses displayed
- UI verified using Playwright

Out of Scope:
- Backend logic
- Agent orchestration
- MCP tools
```

## Response snapshot

Created comprehensive feature specification for ChatKit Frontend Integration on branch `001-chatkit-frontend`.

**Specification Structure**:
- 4 prioritized user stories (P1-P4) with acceptance scenarios
- 17 functional requirements (FR-001 through FR-017)
- 10 measurable success criteria (SC-001 through SC-010)
- Edge cases, assumptions, dependencies, and security considerations
- Clear out-of-scope boundaries

**Clarification Process**:
Identified 2 critical questions requiring user input:

1. **Unauthenticated User Behavior**: Should chat icon be hidden or prompt login?
   - **Resolution**: Show icon but prompt login when clicked (Option B)
   - **Impact**: Added FR-013, FR-014, FR-015

2. **Cross-Page Chat Persistence**: Should chat window state persist across navigation?
   - **Resolution**: Remember last state using session storage (Option C)
   - **Impact**: Added FR-016, FR-017

**Validation Results**:
- Content Quality: 4/4 passed
- Requirement Completeness: 8/8 passed
- Feature Readiness: 4/4 passed
- **Total: 16/16 items passed (100%)**

**Key Features**:
- Floating chat icon visible on all pages (authenticated and unauthenticated)
- Chat window with fixed dimensions (400px × 600px)
- JWT-secured communication with POST /api/chat
- State persistence across page navigations
- Login prompt for unauthenticated users
- Playwright validation for UI testing
- No Phase-2 functionality disruption

**Files Created**:
- `specs/001-chatkit-frontend/spec.md` (280 lines)
- `specs/001-chatkit-frontend/checklists/requirements.md` (60 lines)

**Branch**: `001-chatkit-frontend` (created and checked out)

## Outcome

- ✅ Impact: Complete, validated specification ready for planning phase with 17 functional requirements, 10 success criteria, and 4 prioritized user stories
- 🧪 Tests: Specification quality validation passed 16/16 checks (100%)
- 📁 Files: Created spec.md (280 lines) and requirements checklist (60 lines)
- 🔁 Next prompts: Run /sp.plan to generate implementation plan for ChatKit frontend integration
- 🧠 Reflection: Specification follows Agentic Dev Stack workflow with clear separation between frontend-only scope and out-of-scope backend/MCP/agent features. Clarification questions resolved efficiently (2 questions, both answered). Ready for planning phase.

## Evaluation notes (flywheel)

- Failure modes observed: None - specification process completed successfully
- Graders run and results (PASS/FAIL): Specification Quality Validation - PASS (16/16 checks)
- Prompt variant (if applicable): Standard /sp.specify workflow with clarification resolution
- Next experiment (smallest change to try): Proceed to /sp.plan to validate specification completeness through planning phase
