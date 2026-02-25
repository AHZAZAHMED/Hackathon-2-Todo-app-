---
id: PHR-002
title: Update constitution Phase-3 AI chatbot
stage: constitution
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5
feature: phase-3-ai-chatbot
branch: master
user: PMYLS
command: /sp.constitution
labels: [constitution, phase-3, ai-chatbot, mcp, stateless-backend]
links:
  spec: specs/004-ai-chatbot/spec.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - path: .specify/memory/constitution.md
    status: modified
    lines_changed: 574
tests:
  - name: N/A
    status: N/A
---

## Prompt

```
update the constitution.md file

Project: Phase-3 Todo AI Chatbot (Hackathon II – Spec-Driven Development)

Purpose:
Build an AI-powered Todo chatbot using OpenAI Agents SDK and MCP architecture on top of the existing Phase-2 system (Frontend + Auth + Backend + Database).

All development must strictly follow the Agentic Dev Stack:
Write spec → Generate plan → Break into tasks → Implement via Claude Code.
Manual coding is forbidden.

────────────────────────
CORE PRINCIPLES
────────────────────────

- Spec-first development (no implementation before /sp.specify and /sp.plan)
- Stateless backend architecture
- AI-driven task management through MCP tools only
- Database as the single source of truth
- Security by default (JWT everywhere)
- Production-grade quality (no placeholders, no mocks)
- Deterministic behavior (each request independent)

────────────────────────
ARCHITECTURAL RULES
────────────────────────

1. FastAPI server MUST be stateless
2. Conversation state MUST persist in Neon PostgreSQL
3. AI Agent MUST NOT access database directly
4. All task operations MUST go through MCP tools
5. MCP tools MUST be stateless and persist changes to database
6. user_id MUST ONLY come from Better Auth JWT
7. Frontend MUST communicate exclusively via POST /api/chat
8. No in-memory storage allowed
9. No global state
10. No Phase-4 features

────────────────────────
FIXED TECHNOLOGY STACK
────────────────────────

Frontend: OpenAI ChatKit
Backend: Python FastAPI
AI Framework: OpenAI Agents SDK
MCP Server: Official MCP SDK
ORM: SQLModel
Database: Neon Serverless PostgreSQL
Authentication: Better Auth JWT

No substitutions permitted.
```

## Response snapshot

Updated constitution.md from version 1.0.0 to 2.0.0 (MAJOR version bump).

**Key Changes**:

1. **New Principles Added**:
   - II. Stateless Backend Architecture (NON-NEGOTIABLE)
   - III. AI-Driven Task Management Through MCP Tools Only (NON-NEGOTIABLE)
   - IX. Deterministic Behavior (NON-NEGOTIABLE)

2. **Enhanced Existing Principles**:
   - I. Spec-First Development → Enhanced with Agentic Dev Stack enforcement and "Manual coding is forbidden"
   - VIII. Clear Separation of Layers → Expanded to include AI Agent and MCP layers

3. **New Architecture Section**:
   - Phase-3 Architecture (NEW - AI CHATBOT)
   - Complete system flow diagram (Frontend → Backend → AI Agent → MCP Tools → Database)
   - Chat flow with 15-step mandatory sequence
   - 10 critical architectural rules

4. **New Database Tables**:
   - `conversations` table (user_id FK, title, timestamps)
   - `messages` table (conversation_id FK, role, content, tool_calls, tool_results, timestamp)

5. **New Quality Gates**:
   - MCP Server Gates (9 checkpoints)
   - AI Agent Gates (7 checkpoints)
   - Chat Endpoint Gates (9 checkpoints)
   - Database Schema Gates (8 checkpoints)
   - Frontend Chat UI Gates (10 checkpoints)
   - Integration Gates Phase-3 (10 checkpoints)

6. **Technology Stack Enforcement**:
   - Fixed stack with NO SUBSTITUTIONS PERMITTED
   - OpenAI ChatKit, OpenAI Agents SDK, Official MCP SDK
   - SQLModel for Phase-3 (Prisma only for Better Auth)

**Version Bump Rationale**:
MAJOR (1.0.0 → 2.0.0) due to fundamental architectural changes:
- Introduction of stateless backend requirement (breaking change for any stateful implementations)
- MCP-only task mutations (breaking change for direct database access patterns)
- New AI agent layer with strict separation of concerns
- New database schema requirements

**Sync Impact**:
- ✅ plan-template.md: Constitution Check section aligns with new principles
- ✅ spec-template.md: User story prioritization aligns with spec-driven workflow
- ✅ tasks-template.md: Phase structure aligns with workflow law

## Outcome

- ✅ Impact: Constitution updated to version 2.0.0 with Phase-3 AI chatbot principles, stateless backend architecture, MCP-only task mutations, and comprehensive quality gates
- 🧪 Tests: N/A (constitution document)
- 📁 Files: Modified .specify/memory/constitution.md (574 lines)
- 🔁 Next prompts: Run /sp.specify to create Phase-3 AI chatbot specification following the updated constitution principles
- 🧠 Reflection: MAJOR version bump appropriate due to fundamental architectural constraints. Phase-2 principles retained as foundation while adding Phase-3 requirements. Clear separation between Phase-2 (stable) and Phase-3 (in progress) ensures backward compatibility.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate constitution compliance during /sp.specify execution
