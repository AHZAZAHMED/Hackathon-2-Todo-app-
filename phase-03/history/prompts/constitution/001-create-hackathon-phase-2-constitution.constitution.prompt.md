---
id: 001
title: Create Hackathon Phase-2 Constitution
stage: constitution
date: 2026-02-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: user
command: /sp.constitution
labels: ["constitution", "project-setup", "governance", "spec-driven-development"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

```text
Project: Hackathon II Phase-2 Todo Application

Core Principles:
- Spec-driven development
- Production-grade architecture
- Root-cause engineering
- No mock implementations
- JWT-only identity
- Database-backed persistence
- Clear separation of layers

Key Standards:
- Every behavior must originate from specs
- No coding before /sp.specify approval
- JWT is sole identity authority
- Frontend never sends user_id
- Backend extracts user_id from JWT
- Database enforces ownership
- Tailwind configured officially
- TypeScript strict enabled
- Central API client required
- Environment variables mandatory

Architecture Law:
- Frontend: Next.js 16+ App Router
- Auth: Better Auth JWT
- Backend: FastAPI
- Database: PostgreSQL (Neon)

Workflow Law:
spec → plan → tasks → implementation

No deviation allowed.

Database Rules:
- PostgreSQL required
- Persistent storage mandatory
- users table managed by auth
- tasks.user_id foreign key
- Indexes on user_id
- Migrations required
- No local memory DB

Constraints:
-
```

## Response snapshot

Created comprehensive constitution v1.0.0 for Hackathon II Phase-2 Todo Application with six core principles:

1. **Spec-Driven Development (NON-NEGOTIABLE)**: Mandatory workflow from /sp.constitution through implementation
2. **JWT-Only Identity (NON-NEGOTIABLE)**: Backend extracts user_id from JWT claims only
3. **Database-Backed Persistence (NON-NEGOTIABLE)**: PostgreSQL as single source of truth, no mocks
4. **Production-Grade Architecture**: TypeScript strict, Tailwind configured, centralized API client
5. **Root-Cause Engineering**: Fix underlying issues, not symptoms
6. **Clear Separation of Layers**: Independent frontend/auth/backend/database with defined contracts

Added sections:
- Architecture Law: Stack requirements and component interaction flow
- Workflow Law: Mandatory spec → plan → tasks → implementation sequence
- Database Rules: Schema requirements for users and tasks tables
- Key Standards: Configuration, API, code quality, development order
- Quality Gates: Blocking requirements for each development phase
- Governance: Amendment procedure, versioning policy, compliance requirements

Constitution enforces strict engineering discipline with blocking quality gates and explicit user isolation via JWT and database foreign keys.

## Outcome

- ✅ Impact: Established project governance and non-negotiable principles for Hackathon II Phase-2
- 🧪 Tests: No tests (governance document)
- 📁 Files: Created .specify/memory/constitution.md (v1.0.0)
- 🔁 Next prompts: Run /sp.specify to create first feature specification following the established workflow
- 🧠 Reflection: Constitution successfully captures all user requirements with clear NON-NEGOTIABLE markers, blocking quality gates, and explicit enforcement mechanisms. Templates (plan, spec, tasks) already align with constitution principles.

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution created successfully with all placeholders filled
- Graders run and results (PASS/FAIL): PASS - No unresolved placeholders, version 1.0.0 set, dates in ISO format, principles are declarative and testable
- Prompt variant (if applicable): Standard /sp.constitution workflow
- Next experiment (smallest change to try): Validate constitution enforcement by attempting to code without specs and observing Claude's warning behavior
