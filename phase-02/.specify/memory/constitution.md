<!--
Sync Impact Report:
- Version: NEW → 1.0.0 (Initial constitution)
- Modified principles: N/A (new document)
- Added sections: All core principles, architecture law, workflow law, database rules
- Removed sections: N/A
- Templates requiring updates:
  ✅ plan-template.md: Constitution Check section aligns with principles
  ✅ spec-template.md: User story prioritization aligns with spec-driven workflow
  ✅ tasks-template.md: Phase structure aligns with workflow law
- Follow-up TODOs: None
-->

# Hackathon II Phase-2 Todo Application Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

Every behavior MUST originate from approved specifications. No coding is permitted before `/sp.specify` approval.

**Mandatory Workflow**:
1. `/sp.constitution` - Define project principles
2. `/sp.specify` - Create feature specification
3. `/sp.spec.seed` - Seed specification with examples
4. `/sp.plan` - Generate architectural plan
5. `/sp.tasks` - Break down into testable tasks
6. Implementation - Execute tasks

**Rationale**: Prevents scope creep, ensures alignment, creates traceable decisions, and eliminates ad-hoc implementations that violate architecture.

### II. JWT-Only Identity (NON-NEGOTIABLE)

JWT is the SOLE authority for user identity. All other identity sources are prohibited.

**Rules**:
- Backend MUST extract `user_id` from verified JWT claims
- Frontend MUST NEVER send `user_id` manually in request body or parameters
- Backend MUST NEVER trust client-provided `user_id`
- All authentication state derives from JWT tokens issued by Better Auth

**Rationale**: Prevents identity spoofing, ensures consistent authentication across all endpoints, and enforces security at the token level.

### III. Database-Backed Persistence (NON-NEGOTIABLE)

All application state MUST persist in PostgreSQL. Mock data and in-memory storage are prohibited.

**Rules**:
- PostgreSQL (Neon Serverless) is the single source of truth
- `users` table managed by Better Auth
- `tasks` table with `user_id` foreign key referencing `users.id`
- Foreign key constraints enforced (ON DELETE CASCADE)
- Indexes on `user_id` for query performance
- Migrations required for all schema changes
- No orphan records permitted

**Rationale**: Ensures data durability, enables multi-user isolation, prevents data loss, and provides production-grade reliability.

### IV. Production-Grade Architecture

All implementations MUST meet production standards. Shortcuts, partial implementations, and "good enough" solutions are prohibited.

**Rules**:
- TypeScript strict mode required
- Tailwind CSS officially configured (not CDN)
- Environment variables mandatory for all secrets
- Centralized API client for all backend communication
- Error handling for all failure paths (401, 403, 422, 500)
- CORS properly configured
- Connection pooling for database
- Structured logging for observability

**Rationale**: Prevents technical debt accumulation, ensures maintainability, and delivers reliable systems from day one.

### V. Root-Cause Engineering

All fixes MUST address root causes, not symptoms. Patch fixes and workarounds are prohibited.

**Rules**:
- Identify the underlying issue before implementing a fix
- No temporary solutions that defer the real problem
- Document the root cause in commit messages
- Validate that the fix prevents recurrence

**Rationale**: Prevents bug accumulation, reduces maintenance burden, and builds system understanding.

### VI. Clear Separation of Layers

Frontend, authentication, backend, and database layers MUST remain independent with well-defined contracts.

**Rules**:
- Frontend: Next.js 16+ App Router, TypeScript, Tailwind CSS
- Authentication: Better Auth with JWT tokens
- Backend: FastAPI with Python
- Database: PostgreSQL (Neon Serverless)
- Each layer has its own CLAUDE.md with layer-specific rules
- No cross-layer logic bleeding (e.g., database queries in frontend)
- API contracts define all inter-layer communication

**Rationale**: Enables independent testing, parallel development, technology substitution, and clear responsibility boundaries.

## Architecture Law

**Stack Requirements** (NON-NEGOTIABLE):

- **Frontend**: Next.js 16+ App Router + TypeScript + Tailwind CSS
- **Authentication**: Better Auth + JWT
- **Backend**: FastAPI + Python
- **Database**: PostgreSQL (Neon Serverless)
- **ORM**: SQLModel or SQLAlchemy-based equivalent

**Component Interaction Flow**:
```
User → Frontend (Next.js) → Better Auth (JWT) → Backend (FastAPI) → PostgreSQL (Neon)
```

**Authentication Flow**:
1. Better Auth issues JWT on login
2. Frontend stores JWT securely (httpOnly cookie or secure storage)
3. Frontend API client attaches JWT to all requests automatically
4. Backend verifies JWT signature
5. Backend extracts `user_id` from JWT claims
6. Backend uses `user_id` for database queries

**User Isolation**:
- User identity derived ONLY from JWT claims
- Database enforces foreign key constraints: `tasks.user_id → users.id`
- All queries MUST filter by authenticated `user_id`
- Users can ONLY access their own resources

## Workflow Law

**Mandatory Sequence** (BLOCKING):

```
spec → plan → tasks → implementation
```

**No deviation permitted.**

**Enforcement**:
- When coding is requested without approved specs, Claude MUST warn and ask for confirmation
- All features MUST have corresponding spec, plan, and tasks artifacts
- Implementation MUST reference task IDs for traceability

## Database Rules

**Provider**: PostgreSQL (Neon Serverless)

**Schema Requirements**:

**`users` table**:
- Managed by Better Auth
- Primary key: `id` (UUID or integer)
- Contains: email, hashed password, metadata

**`tasks` table**:
- Primary key: `id` (UUID or integer)
- Foreign key: `user_id` references `users.id` (ON DELETE CASCADE)
- Fields: `title`, `description`, `completed`, `created_at`, `updated_at`
- Index on `user_id` for query performance

**Constraints**:
- NO orphan records (foreign key enforced)
- Migrations required for all schema changes
- NO in-memory storage
- All queries MUST filter by authenticated `user_id`

**Connection**:
- Use environment variable: `DATABASE_URL`
- Connection pooling recommended
- Handle connection errors gracefully

## Key Standards

### Configuration Standards

- **TypeScript**: Strict mode required (`"strict": true` in tsconfig.json)
- **Tailwind CSS**: Official configuration required (not CDN)
- **Environment Variables**: Mandatory for all secrets, API keys, database URLs
- **`.env` Files**: NEVER commit to version control; provide `.env.example` with placeholders

### API Standards

- **Centralized Client**: All API calls through `lib/api-client.ts` or equivalent
- **JWT Attachment**: Automatic via centralized client
- **Error Handling**: Backend MUST return proper HTTP status codes:
  - 401: Invalid/missing JWT
  - 403: Unauthorized resource access
  - 422: Validation errors
  - 500: Server errors
- **CORS**: Properly configured for frontend origin

### Code Quality Standards

- **No Partial Implementations**: Features MUST be complete before merging
- **No Patch Fixes**: Address root causes only
- **Smallest Viable Change**: No unrelated refactoring
- **Code References**: Use `file:line-start:line-end` format
- **Testability**: All changes MUST be testable

### Development Order Standards

**BLOCKING SEQUENCE**: Each phase MUST pass quality gates before proceeding.

1. **Frontend Implementation** → Validate with `implementation-validator-playwright`
2. **Authentication** → Validate with `implementation-validator-playwright`
3. **Backend API** → Validate with `implementation-validator-playwright`
4. **Database Schema + Integration** → Validate with `implementation-validator-playwright`
5. **Full Integration Testing** → Validate with `integration-testing-engineer`

## Quality Gates

**BLOCKING REQUIREMENTS**: All MUST pass before proceeding to next phase.

### Frontend Gates:
- [ ] `npm run dev` succeeds without errors
- [ ] Tailwind styles render correctly
- [ ] TypeScript compiles with strict mode
- [ ] No console errors in browser
- [ ] Centralized API client in place

### Authentication Gates:
- [ ] JWT issued on login
- [ ] JWT stored securely
- [ ] JWT attached to requests automatically
- [ ] Auth state persists across reloads

### Backend Gates:
- [ ] Backend starts without errors
- [ ] JWT verification rejects invalid tokens (401)
- [ ] Endpoints extract `user_id` from JWT
- [ ] Unauthorized requests return 403
- [ ] CORS configured correctly

### Database Gates:
- [ ] Database connection succeeds
- [ ] Migrations run successfully
- [ ] Foreign key constraints enforced
- [ ] Tasks persist in database
- [ ] Users only see their own tasks
- [ ] No orphan records

### Integration Gates:
- [ ] Signup → Login → Create Task flow works
- [ ] JWT flow end-to-end (issuance → verification)
- [ ] User isolation enforced (User A ≠ User B tasks)
- [ ] Error paths handled (invalid JWT, unauthorized access)

## Governance

### Amendment Procedure

1. **Proposal**: Document proposed change with rationale and impact analysis
2. **Review**: Assess impact on existing specs, plans, and implementations
3. **Approval**: Explicit user approval required
4. **Migration**: Update all dependent templates and artifacts
5. **Version Bump**: Follow semantic versioning (MAJOR.MINOR.PATCH)

### Versioning Policy

- **MAJOR**: Backward-incompatible governance/principle removals or redefinitions
- **MINOR**: New principle/section added or materially expanded guidance
- **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements

### Compliance Requirements

- All PRs/reviews MUST verify compliance with constitution principles
- Violations MUST be justified in `Complexity Tracking` section of plan.md
- Constitution supersedes all other practices and conventions
- Claude Code MUST enforce constitution rules with warnings and confirmation prompts

### Runtime Guidance

- Root CLAUDE.md: Project-wide rules (this constitution + execution contract)
- `frontend/CLAUDE.md`: Next.js, Better Auth, UI-specific rules
- `backend/CLAUDE.md`: FastAPI, JWT verification, database-specific rules
- Claude Code reads the **closest** CLAUDE.md first to prevent cross-stack confusion

**Version**: 1.0.0 | **Ratified**: 2026-02-05 | **Last Amended**: 2026-02-05
