---
id: PHR-003-TASKS-CRUD-API-PLAN-001
title: Backend API Database Persistence Implementation Plan
stage: plan
date: 2026-02-06T23:00:00Z
surface: agent
model: claude-sonnet-4-5
feature: 003-tasks-crud-api
branch: 003-tasks-crud-api
user: PMYLS
command: /sp.plan
labels: [backend, api, database, fastapi, postgresql, crud, tasks, jwt, planning, sqlmodel, implementation-plan]
links:
  spec: specs/003-tasks-crud-api/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - path: specs/003-tasks-crud-api/plan.md
    action: created
    lines: 634
  - path: specs/003-tasks-crud-api/research.md
    action: created
    lines: 350
  - path: specs/003-tasks-crud-api/data-model.md
    action: created
    lines: 450
  - path: specs/003-tasks-crud-api/contracts/tasks-api.md
    action: created
    lines: 650
  - path: specs/003-tasks-crud-api/quickstart.md
    action: created
    lines: 500
tests: []
---

## Prompt

User invoked `/sp.plan` with detailed planning requirements:

```
Feature: Backend API + Database Persistence (Hackathon II Phase-2)

Input: Approved specification from specs/003-tasks-crud-api/spec.md

Purpose: Convert the backend specification into an executable implementation plan
that delivers a fully functional FastAPI backend with PostgreSQL persistence
and JWT-based authorization.

Scope: Backend only, Database only, No frontend changes, No mock logic

Plan Objectives:
1. Initialize backend folder and backend/CLAUDE.md
2. Configure FastAPI project structure
3. Configure DATABASE_URL with Neon
4. Initialize ORM and migrations
5. Define Task models
6. Implement JWT verification dependency
7. Implement CRUD endpoints
8. Enforce user isolation at query level
9. Integrate frontend with backend
10. Validate full end-to-end behavior

Required Sections: Summary, Technical Context, Constitution Check, Project Structure,
Execution Phases, Validation Criteria

Skills: backend-engineer(FastAPI), database-skill

Constraints: Must remain Phase-2 only, JWT derived identity, No user_id in URLs,
Claude Code only

Success Criteria: Backend production-ready, Database stable, Auth enforced,
Frontend fully operational
```

## Response snapshot

Created comprehensive implementation plan for Backend API + Database Persistence feature with complete Phase 0 (Research) and Phase 1 (Design) artifacts:

**Planning Documents Created (5 files, ~2,584 lines)**:

1. **plan.md** (634 lines) - Master implementation plan
   - Summary: Extends existing FastAPI backend with Task CRUD functionality
   - Technical Context: Python 3.11+, FastAPI, SQLModel, PostgreSQL, JWT
   - Constitution Check: All 6 principles passed (spec-driven, JWT-only, database-backed, production-grade, root-cause, layer separation)
   - Project Structure: Web application with backend/ and frontend/ directories
   - Phase 0: Research & Technology Decisions (5 key decisions documented)
   - Phase 1: Design & Contracts (data model, API contracts, quickstart guide)
   - Phase 2: Implementation Execution (6 steps: CLAUDE.md, Task model, migration, routes, registration, env config)
   - Phase 3: Integration & Validation (7 test categories)
   - Phase 4: Quality Gates & Acceptance (backend, database, integration, success criteria)
   - Risks & Mitigations: 6 risks identified with mitigation strategies
   - Dependencies: External, internal, and blocking prerequisites documented

2. **research.md** (350 lines) - Technology decisions and best practices
   - Decision 1: Extend existing backend structure (not microservice)
   - Decision 2: SQLModel for Task model (consistency with existing models)
   - Decision 3: User isolation via query filtering (return 404 not 403)
   - Decision 4: SQL migration files (explicit schema control)
   - Decision 5: Response format consistency (envelope with data/error)
   - Technology stack summary with rationale for each component
   - Best practices for FastAPI, SQLModel, security, and database patterns

3. **data-model.md** (450 lines) - Task entity definition
   - Complete field definitions with types, constraints, defaults
   - Relationships: Task → User (many-to-one with CASCADE delete)
   - Validation rules for title, description, completed, user_id, timestamps
   - State transitions: Created → Active → Completed → Deleted
   - Database schema (SQL) and SQLModel definition (Python)
   - Indexes: Primary key (id), user_id, completed
   - Performance considerations for 100 concurrent users, <1000 tasks per user
   - Security: User isolation enforced at query level
   - Migration strategy with rollback script

4. **contracts/tasks-api.md** (650 lines) - API endpoint specifications
   - 6 REST endpoints fully documented:
     - GET /api/tasks - List all tasks (200, 401)
     - POST /api/tasks - Create task (201, 401, 422)
     - GET /api/tasks/{id} - Get single task (200, 401, 404)
     - PUT /api/tasks/{id} - Update task (200, 401, 404, 422)
     - DELETE /api/tasks/{id} - Delete task (204, 401, 404)
     - PATCH /api/tasks/{id}/complete - Toggle completion (200, 401, 404)
   - Request/response examples for all endpoints
   - Error codes and formats (UNAUTHORIZED, NOT_FOUND, VALIDATION_ERROR)
   - Authentication requirements (JWT Bearer token)
   - Data types (Task object with TypeScript interface)
   - Security considerations (user isolation, input validation)
   - CORS configuration
   - Example usage with cURL commands

5. **quickstart.md** (500 lines) - Setup and run instructions
   - 5-step quick start guide (15-20 minute setup)
   - Environment configuration (backend/.env and frontend/.env.local)
   - Database setup (Neon Serverless or local PostgreSQL)
   - Migration execution with verification steps
   - Backend startup with uvicorn
   - Frontend integration testing
   - Troubleshooting guide (6 common problems with solutions)
   - Validation checklist (backend, database, auth, integration)
   - Development workflow (3 terminals: backend, frontend, database monitoring)
   - API testing with cURL and Swagger UI
   - Production deployment checklist

**Key Planning Decisions**:

1. **Extend Existing Backend**: Leverage existing FastAPI infrastructure (JWT verification, database connection, CORS) rather than creating separate microservice
2. **SQLModel Consistency**: Use SQLModel for Task model to match existing User and RateLimit models
3. **Query-Level User Isolation**: Filter all queries by user_id from JWT, return 404 (not 403) for unauthorized access
4. **SQL Migrations**: Use explicit SQL migration files for version control and reviewability
5. **Response Format**: Maintain consistent envelope format {"data": ...} for success, {"error": {...}} for errors

**Constitution Compliance**:
- ✅ Spec-Driven Development: Follows approved spec with 45 functional requirements
- ✅ JWT-Only Identity: All endpoints extract user_id from JWT, never from client
- ✅ Database-Backed Persistence: Tasks table with foreign key, indexes, CASCADE delete
- ✅ Production-Grade Architecture: Environment variables, CORS, error handling, connection pooling
- ✅ Root-Cause Engineering: Proper foreign keys, indexes, query filtering (no shortcuts)
- ✅ Clear Separation of Layers: Backend-only changes, frontend requires no modifications

**Implementation Approach**:
- Phase 0: Research completed inline (5 technology decisions documented)
- Phase 1: Design artifacts created (data model, API contracts, quickstart guide)
- Phase 2: Implementation sequence defined (6 steps from CLAUDE.md to env config)
- Phase 3: Integration tests specified (7 test categories)
- Phase 4: Quality gates defined (backend, database, integration, success criteria)

**Technical Stack**:
- FastAPI 0.104+ (existing backend framework)
- SQLModel 0.0.14+ (existing ORM)
- PostgreSQL 14+ (Neon Serverless)
- PyJWT 2.8+ (existing JWT verification)
- Uvicorn 0.24+ (existing ASGI server)

**Project Structure**:
- Backend: app/models/task.py (NEW), app/routes/tasks.py (NEW), migrations/002_create_tasks_table.sql (NEW), CLAUDE.md (NEW)
- Frontend: No changes required (API client already has task methods)

## Outcome

- ✅ Impact: Created production-ready implementation plan for Backend API + Database Persistence with 5 comprehensive planning documents (2,584 lines total). Plan extends existing backend infrastructure with Task model, migration, and 6 CRUD endpoints. All constitution principles satisfied. Ready for task generation via /sp.tasks.
- 🧪 Tests: No automated tests (planning phase) - validation criteria defined for implementation phase
- 📁 Files: 5 files created (plan.md 634 lines, research.md 350 lines, data-model.md 450 lines, contracts/tasks-api.md 650 lines, quickstart.md 500 lines)
- 🔁 Next prompts: Run /sp.tasks to generate atomic task breakdown for implementation
- 🧠 Reflection: Successfully created comprehensive implementation plan following spec-driven workflow. All Phase 0 (Research) and Phase 1 (Design) artifacts completed. Plan leverages existing backend infrastructure (JWT verification, database connection, CORS) rather than rebuilding from scratch. Key decisions documented with rationale and alternatives considered. Constitution check passed all 6 principles. Implementation approach clearly defined with 4 phases (setup, implementation, integration, validation). Ready for task generation and implementation execution.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning workflow completed successfully
- Graders run and results (PASS/FAIL): Constitution Check - PASS (all 6 principles satisfied)
- Prompt variant (if applicable): Standard /sp.plan workflow with comprehensive planning requirements
- Next experiment (smallest change to try): Proceed to /sp.tasks to generate atomic task breakdown for implementation
