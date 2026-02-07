# Claude Code Rules - Hackathon II Phase-2 Todo Application

**Project Type:** Spec-Driven Full-Stack Web Application
**Status:** Active Development
**Enforcement:** Strict - All rules are blocking requirements

---

## Project Overview

**Hackathon II Phase-2 Todo Application**

Multi-user authenticated task management system with persistent PostgreSQL storage.

**Stack:**
- Frontend: Next.js 16+ App Router + TypeScript + Tailwind CSS
- Authentication: Better Auth + JWT
- Backend: FastAPI + Python
- Database: PostgreSQL (Neon Serverless)
- Workflow: Spec-Kit Plus

**Non-Negotiable Constraint:**
NO mock data, NO hardcoded users, NO in-memory storage. All state persists in PostgreSQL. All identity derives from JWT.

---

## Architecture

**Component Interaction:**
```
User → Frontend (Next.js) → Better Auth (JWT) → Backend (FastAPI) → PostgreSQL (Neon)
```

**Authentication Flow:**
1. Better Auth issues JWT on login
2. Frontend stores JWT (httpOnly cookie or secure storage)
3. Frontend API client attaches JWT to all requests automatically
4. Backend verifies JWT signature
5. Backend extracts `user_id` from JWT claims
6. Backend uses `user_id` for database queries

**User Isolation:**
- User identity derived ONLY from JWT claims
- Frontend NEVER sends `user_id` manually
- Backend NEVER trusts client-provided `user_id`
- Database enforces foreign key constraints: `tasks.user_id → users.id`
- All queries filter by authenticated `user_id`

**API Communication:**
- Centralized API client in frontend (`lib/api-client.ts` or similar)
- All backend calls go through this client
- Client handles JWT attachment automatically
- No direct fetch/axios calls scattered in components

---

## Mandatory Spec Workflow

**BLOCKING REQUIREMENT:** All development MUST follow this sequence. Coding outside this pipeline is prohibited.

1. **`/sp.constitution`** - Define project principles
2. **`/sp.specify`** - Create feature specification
3. **`/sp.spec.seed`** - Seed specification with examples
4. **`/sp.plan`** - Generate architectural plan
5. **`/sp.tasks`** - Break down into testable tasks
6. **Claude Code implementation** - Execute tasks

**Enforcement:**
When user requests coding without approved specs, Claude MUST:
1. Warn: "⚠️ No approved spec detected for this feature."
2. Ask: "Would you like to run the spec workflow first (`/sp.specify`), or proceed without specs?"
3. Wait for explicit confirmation before coding

---

## Core Rules

**Identity & Authentication:**
- ✅ JWT is the ONLY source of user identity
- ❌ NEVER hardcode user IDs
- ❌ NEVER accept `user_id` from frontend request body/params
- ✅ Backend MUST extract `user_id` from verified JWT claims
- ✅ Frontend MUST attach JWT automatically via centralized client

**Data & State:**
- ❌ NEVER introduce mock data
- ❌ NEVER use in-memory storage
- ✅ All state MUST persist in PostgreSQL
- ✅ Database MUST enforce user isolation via foreign keys
- ✅ Migrations required for all schema changes

**API Design:**
- ✅ All API calls through centralized client
- ❌ NEVER scatter fetch/axios calls in components
- ✅ Backend MUST reject requests without valid JWT
- ✅ Backend MUST return 401 for invalid/missing tokens
- ✅ Backend MUST return 403 for unauthorized resource access

**Configuration:**
- ✅ Tailwind MUST be officially configured (not CDN)
- ✅ TypeScript strict mode required
- ✅ Environment variables mandatory for secrets
- ❌ NEVER commit `.env` files
- ✅ Provide `.env.example` with placeholder values

**Implementation Quality:**
- ❌ NEVER create partial implementations
- ❌ NEVER apply patch fixes to symptoms
- ✅ Always fix root causes
- ✅ All changes must be testable
- ✅ Code must pass quality gates before proceeding

---

## Folder Structure

**Monorepo Layout:**
```
phase-02/
├── CLAUDE.md                 # This file (root rules)
├── specs/                    # Feature specifications
│   └── <feature-name>/
│       ├── spec.md
│       ├── plan.md
│       └── tasks.md
├── frontend/
│   ├── CLAUDE.md            # Frontend-specific rules
│   ├── app/                 # Next.js App Router
│   ├── components/
│   ├── lib/
│   │   └── api-client.ts   # Centralized API client
│   └── ...
├── backend/
│   ├── CLAUDE.md            # Backend-specific rules
│   ├── app/
│   │   ├── main.py
│   │   ├── auth.py         # JWT verification
│   │   ├── models.py       # SQLModel schemas
│   │   └── routes/
│   └── ...
├── history/
│   ├── prompts/            # Prompt History Records
│   └── adr/                # Architecture Decision Records
└── .specify/               # Spec-Kit Plus templates
```

**CLAUDE.md Hierarchy:**
- Claude Code reads the **closest** CLAUDE.md first
- Root CLAUDE.md: project-wide rules (this file)
- `frontend/CLAUDE.md`: Next.js, Better Auth, UI rules
- `backend/CLAUDE.md`: FastAPI, JWT verification, database rules

**Purpose of Separation:**
Prevents cross-stack confusion. Frontend rules don't leak into backend work, and vice versa.

---

## Skills

**Available Capabilities:**

| Skill | Purpose | Invocation |
|-------|---------|------------|
| `senior-next.js-developer` | Next.js 16+ App Router, TypeScript, Tailwind | Permission-first |
| `better-auth-skill` | Better Auth + JWT integration | Permission-first |
| `backend-engineer(FastAPI)` | FastAPI, Python, API design | Permission-first |
| `database-skill` | PostgreSQL, SQLModel, migrations | Permission-first |
| `implementation-validator-playwright` | Browser-based validation after implementation | Permission-first |
| `integration-testing-engineer` | End-to-end flow validation | Permission-first |
| `doc-coauthoring` | Structured documentation workflow | Permission-first |
| `browsing-with-playwright` | Browser automation, screenshots | Permission-first |
| `fetch-library-docs` | Official library documentation | Permission-first |

**Invocation Policy:**
1. When a task matches a skill's domain, Claude MUST ask: "This task involves [domain]. Would you like me to invoke the `[skill-name]` skill?"
2. Wait for user confirmation before invoking
3. User can explicitly request skills: "Use the better-auth-skill"
4. Skills run with full context from this conversation

---

## Development Order

**BLOCKING SEQUENCE:** Each phase must pass quality gates before proceeding to the next.

### Phase 1: Frontend Implementation
**Tasks:**
- Next.js 16+ App Router setup
- TypeScript strict mode configuration
- Tailwind CSS official configuration
- Basic UI components (login, signup, todo list)
- Centralized API client (`lib/api-client.ts`)

**Quality Gate:**
- `npm run dev` succeeds without errors
- Tailwind styles render correctly
- TypeScript compiles with no errors
- API client structure in place

**Validation:**
After implementation, invoke `implementation-validator-playwright` skill to verify UI renders and navigation works.

---

### Phase 2: Authentication
**Tasks:**
- Better Auth installation and configuration
- JWT issuance on login/signup
- JWT storage (httpOnly cookie or secure storage)
- API client JWT attachment logic
- Auth state management

**Quality Gate:**
- JWT issued on successful login
- JWT stored securely
- JWT attached to API requests automatically
- Auth state persists across page reloads

**Validation:**
After implementation, invoke `implementation-validator-playwright` skill to verify login flow and JWT attachment.

---

### Phase 3: Backend API
**Tasks:**
- FastAPI setup with CORS
- JWT verification middleware
- User extraction from JWT claims
- CRUD endpoints for tasks (`/tasks`)
- Error handling (401, 403, 422, 500)

**Quality Gate:**
- Backend starts without errors
- JWT verification rejects invalid tokens (401)
- Endpoints extract `user_id` from JWT
- Unauthorized requests return 403
- API returns proper error responses

**Validation:**
After implementation, invoke `implementation-validator-playwright` skill to verify API responses and error handling.

---

### Phase 4: Database Schema + Integration
**Tasks:**
- Neon PostgreSQL connection
- SQLModel or equivalent ORM setup
- `users` table (managed by Better Auth)
- `tasks` table with `user_id` foreign key
- Database migrations
- User isolation enforcement

**Quality Gate:**
- Database connection succeeds
- Migrations run successfully
- Foreign key constraints enforced
- Tasks persist in database
- Users only see their own tasks
- No orphan records

**Validation:**
After implementation, invoke `implementation-validator-playwright` skill to verify database persistence and user isolation.

---

### Phase 5: Full Integration Testing
**Tasks:**
- End-to-end user flows (signup → login → create task → logout)
- JWT flow validation (issuance → attachment → verification)
- User isolation verification (User A cannot see User B's tasks)
- Error path testing (invalid JWT, unauthorized access)

**Quality Gate:**
- All user flows complete successfully
- JWT flow works end-to-end
- User isolation enforced
- Error paths handled gracefully

**Validation:**
Invoke `integration-testing-engineer` skill to validate complete system integration.

---

## Database Rules

**Provider:** PostgreSQL (Neon Serverless)

**ORM:** SQLModel or equivalent (SQLAlchemy-based)

**Schema Requirements:**

**`users` table:**
- Managed by Better Auth
- Primary key: `id` (UUID or integer)
- Contains: email, hashed password, metadata

**`tasks` table:**
- Primary key: `id` (UUID or integer)
- Foreign key: `user_id` references `users.id` (ON DELETE CASCADE)
- Fields: `title`, `description`, `completed`, `created_at`, `updated_at`
- Index on `user_id` for query performance

**Constraints:**
- ❌ NO orphan records (foreign key enforced)
- ✅ Migrations required for all schema changes
- ❌ NO in-memory storage
- ✅ All queries MUST filter by authenticated `user_id`

**Connection:**
- Use environment variable: `DATABASE_URL`
- Connection pooling recommended
- Handle connection errors gracefully

---

## Quality Gates

**BLOCKING REQUIREMENTS:** All must pass before proceeding.

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

---

## PHR/ADR Workflow

### Prompt History Records (PHR)

**Purpose:** Record every user input and Claude's response for learning and traceability.

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**PHR Creation Process:**

1. **Detect stage:** constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2. **Generate title:** 3–7 words; create a slug for the filename

3. **Resolve route (all under `history/prompts/`):**
   - `constitution` → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/`
   - `general` → `history/prompts/general/`

4. **Read PHR template:**
   - `.specify/templates/phr-template.prompt.md`
   - `templates/phr-template.prompt.md`

5. **Fill ALL placeholders:**
   - ID, TITLE, STAGE, DATE_ISO, SURFACE="agent"
   - MODEL, FEATURE, BRANCH, USER
   - COMMAND, LABELS
   - LINKS: SPEC/TICKET/ADR/PR
   - FILES_YAML: created/modified files
   - TESTS_YAML: tests run/added
   - PROMPT_TEXT: full user input (verbatim)
   - RESPONSE_TEXT: key assistant output

6. **Write file:** Use agent file tools (Write/Edit)

7. **Validate:**
   - No unresolved placeholders
   - Title, stage, dates match
   - PROMPT_TEXT complete (not truncated)
   - File exists and readable

8. **Report:** ID, path, stage, title

**Skip PHR only for `/sp.phr` itself.**

---

### Architecture Decision Records (ADR)

**Purpose:** Document architecturally significant decisions with reasoning and tradeoffs.

**When to suggest ADRs:**

After design/architecture work, test for significance:
- **Impact:** Long-term consequences? (framework, data model, API, security, platform)
- **Alternatives:** Multiple viable options considered?
- **Scope:** Cross-cutting and influences system design?

**If ALL true, suggest:**
```
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`
```

**Wait for user consent. NEVER auto-create ADRs.**

**Group related decisions** (stacks, authentication, deployment) into one ADR when appropriate.

---

## Execution Contract

**For every user request, Claude MUST:**

1. **Confirm surface and success criteria** (one sentence)
   - Example: "Implementing JWT verification middleware in FastAPI backend. Success: backend rejects invalid tokens with 401."

2. **List constraints, invariants, non-goals**
   - Constraints: Must use Better Auth JWT format
   - Invariants: User isolation enforced
   - Non-goals: Not implementing refresh tokens yet

3. **Produce artifact with acceptance checks**
   - Code with inline comments for critical logic
   - Checkboxes for validation steps

4. **Add follow-ups and risks** (max 3 bullets)
   - Follow-up: Test with expired JWT
   - Risk: JWT secret must be in `.env`

5. **Create PHR** in appropriate subdirectory under `history/prompts/`

6. **Surface ADR suggestion** if architecturally significant decision detected

---

## Minimum Acceptance Criteria

**Every implementation MUST include:**
- ✅ Clear, testable acceptance criteria
- ✅ Explicit error paths and constraints stated
- ✅ Smallest viable change; no unrelated edits
- ✅ Code references to modified/inspected files (e.g., `app/main.py:45-67`)

---

## Philosophy

**Spec is law.**
No coding without approved specifications. The spec workflow is non-negotiable.

**JWT is truth.**
User identity derives exclusively from verified JWT claims. No other source is trusted.

**Database is source of state.**
All state persists in PostgreSQL. No mocks, no in-memory storage, no shortcuts.

**No shortcuts.**
Partial implementations and patch fixes are prohibited. Fix root causes only.

**No patch fixes.**
Address the underlying issue, not the symptom.

---

## Tone & Enforcement

**Strict engineering discipline.**

All rules in this document are **BLOCKING REQUIREMENTS**. When violations are detected, Claude MUST:
1. Warn the user with specific rule reference
2. Ask for confirmation to proceed
3. Wait for explicit approval before continuing

**Example:**
```
⚠️ Rule violation detected: Core Rules > Identity & Authentication
   "Frontend MUST NEVER send user_id manually"

The current approach sends user_id in the request body.
This violates user isolation principles.

Correct approach: Backend extracts user_id from JWT claims.

Proceed with violation, or fix the approach?
```

---

## Human as Tool Strategy

Claude is not expected to solve every problem autonomously. Claude MUST invoke the user for input when encountering situations requiring human judgment.

**Invocation Triggers:**

1. **Ambiguous Requirements:** Ask 2-3 targeted clarifying questions before proceeding
2. **Unforeseen Dependencies:** Surface dependencies and ask for prioritization
3. **Architectural Uncertainty:** Present options with tradeoffs, get user's preference
4. **Completion Checkpoint:** Summarize what was done, confirm next steps

---

## Default Policies

- Clarify and plan first - keep business understanding separate from technical plan
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing
- Never hardcode secrets or tokens; use `.env` and provide `.env.example`
- Prefer the smallest viable diff; do not refactor unrelated code
- Cite existing code with code references (`file:line-start:line-end`)
- Propose new code in fenced blocks
- Keep reasoning private; output only decisions, artifacts, and justifications

---

**End of Root CLAUDE.md**

**Next Steps:**
1. Create `frontend/CLAUDE.md` with Next.js + Better Auth specific rules
2. Create `backend/CLAUDE.md` with FastAPI + JWT verification specific rules
3. Run `/sp.constitution` to define project principles
4. Begin spec workflow for first feature
