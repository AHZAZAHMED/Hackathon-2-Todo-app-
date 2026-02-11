# Tasks: Backend API + Database Persistence

**Input**: Design documents from `/specs/003-tasks-crud-api/`
**Prerequisites**: spec.md, research.md, data-model.md, contracts/tasks-api.md, quickstart.md

**Feature**: Backend API + Database Persistence (003-tasks-crud-api)
**Branch**: 003-tasks-crud-api
**Date**: 2026-02-06

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/app/`, `frontend/` (no frontend changes in this feature)
- All backend tasks in `backend/` directory
- Database migrations in `backend/migrations/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Backend-specific documentation and environment setup

**Prerequisites**: None - can start immediately

- [ ] T001 Create backend/CLAUDE.md with FastAPI, SQLModel, JWT, and database rules
- [ ] T002 Verify backend/.env has DATABASE_URL and BETTER_AUTH_SECRET (matches frontend)
- [ ] T003 [P] Verify backend/requirements.txt has all dependencies (fastapi, sqlmodel, pyjwt, uvicorn, psycopg2-binary, python-dotenv)

**Checkpoint**: Backend documentation and environment ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database schema and core infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**Prerequisites**: Phase 1 complete

- [ ] T004 Create backend/migrations/002_create_tasks_table.sql with tasks table, foreign key to user.id (CASCADE), and indexes on user_id and completed
- [ ] T005 Run database migration: `psql $DATABASE_URL -f backend/migrations/002_create_tasks_table.sql`
- [ ] T006 Verify migration: Check tasks table exists, indexes created, foreign key constraint enforced
- [ ] T007 [P] Create backend/app/models/task.py with Task SQLModel (id, user_id FK, title, description, completed, created_at, updated_at)
- [ ] T008 [P] Verify existing backend/app/auth/dependencies.py has get_current_user dependency that extracts user_id from JWT

**Checkpoint**: Foundation ready - database schema exists, Task model defined, JWT verification available. User story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Create New Task (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can create new tasks with title and optional description. Tasks persist in database with user_id from JWT.

**Independent Test**: Login as user, create task via POST /api/tasks, verify task appears in database and has correct user_id from JWT (not from request body).

**Prerequisites**: Phase 2 complete (Task model and database schema ready)

### Implementation for User Story 1

- [ ] T009 [US1] Create backend/app/routes/tasks.py with FastAPI router
- [ ] T010 [US1] Implement POST /api/tasks endpoint in backend/app/routes/tasks.py:
  - Accept JSON body with title (required, max 500 chars) and description (optional)
  - Use Depends(get_current_user) to get authenticated user
  - Extract user_id from user dict (from JWT)
  - Create Task with user_id from JWT (NEVER from request body)
  - Set completed=false, created_at=now(), updated_at=now()
  - Save to database
  - Return 201 with {"data": task}
  - Return 422 if title empty or >500 chars
  - Return 401 if JWT missing/invalid
- [ ] T011 [US1] Register tasks router in backend/app/main.py with app.include_router(tasks.router)
- [ ] T012 [US1] Test POST /api/tasks: Create task with valid JWT, verify task in database with correct user_id
- [ ] T013 [US1] Test POST /api/tasks validation: Empty title returns 422, title >500 chars returns 422
- [ ] T014 [US1] Test POST /api/tasks auth: Missing JWT returns 401, invalid JWT returns 401

**Checkpoint**: User Story 1 complete - users can create tasks that persist in database with JWT-derived user_id

---

## Phase 4: User Story 2 - View All Tasks (Priority: P2)

**Goal**: Authenticated users can retrieve all their tasks. Tasks are filtered by user_id from JWT (user isolation enforced).

**Independent Test**: Login as User A, create 3 tasks, call GET /api/tasks, verify only User A's tasks returned. Login as User B, verify User B sees empty list (not User A's tasks).

**Prerequisites**: Phase 2 complete, User Story 1 complete (for test data creation)

### Implementation for User Story 2

- [ ] T015 [US2] Implement GET /api/tasks endpoint in backend/app/routes/tasks.py:
  - Use Depends(get_current_user) to get authenticated user
  - Extract user_id from user dict
  - Query tasks filtered by user_id: `select(Task).where(Task.user_id == user["user_id"])`
  - Order by created_at DESC (newest first)
  - Return 200 with {"data": [tasks]}
  - Return empty array if no tasks
  - Return 401 if JWT missing/invalid
- [ ] T016 [US2] Test GET /api/tasks: Create 3 tasks, verify all 3 returned in reverse chronological order
- [ ] T017 [US2] Test GET /api/tasks empty: New user with no tasks gets empty array
- [ ] T018 [US2] Test GET /api/tasks isolation: User A cannot see User B's tasks
- [ ] T019 [US2] Test GET /api/tasks auth: Missing JWT returns 401

**Checkpoint**: User Story 2 complete - users can view their task list with proper isolation

---

## Phase 5: User Story 3 - Update Existing Task (Priority: P3)

**Goal**: Authenticated users can update title and description of their own tasks. Returns 404 if task doesn't exist or doesn't belong to user.

**Independent Test**: Create task as User A, update title/description, verify changes persist. Attempt to update as User B, verify 404 returned (not 403).

**Prerequisites**: Phase 2 complete, User Story 1 complete (for test data creation)

### Implementation for User Story 3

- [ ] T020 [US3] Implement PUT /api/tasks/{id} endpoint in backend/app/routes/tasks.py:
  - Accept path param id (integer) and JSON body with title and description
  - Use Depends(get_current_user) to get authenticated user
  - Query task filtered by id AND user_id: `select(Task).where(Task.id == id, Task.user_id == user["user_id"])`
  - Return 404 if task not found (don't reveal if task exists for other user)
  - Validate title (required, max 500 chars)
  - Update task.title, task.description, task.updated_at = now()
  - Save to database
  - Return 200 with {"data": task}
  - Return 422 if title empty or >500 chars
  - Return 401 if JWT missing/invalid
- [ ] T021 [US3] Implement GET /api/tasks/{id} endpoint in backend/app/routes/tasks.py:
  - Accept path param id (integer)
  - Use Depends(get_current_user) to get authenticated user
  - Query task filtered by id AND user_id
  - Return 404 if task not found
  - Return 200 with {"data": task}
  - Return 401 if JWT missing/invalid
- [ ] T022 [US3] Test PUT /api/tasks/{id}: Update task title and description, verify changes persist
- [ ] T023 [US3] Test PUT /api/tasks/{id} validation: Empty title returns 422
- [ ] T024 [US3] Test PUT /api/tasks/{id} isolation: User A cannot update User B's task (404 returned)
- [ ] T025 [US3] Test PUT /api/tasks/{id} not found: Non-existent task ID returns 404
- [ ] T026 [US3] Test GET /api/tasks/{id}: Retrieve single task, verify correct data
- [ ] T027 [US3] Test GET /api/tasks/{id} isolation: User A cannot get User B's task (404 returned)

**Checkpoint**: User Story 3 complete - users can update and retrieve individual tasks with proper isolation

---

## Phase 6: User Story 4 - Delete Task (Priority: P4)

**Goal**: Authenticated users can permanently delete their own tasks. Returns 404 if task doesn't exist or doesn't belong to user.

**Independent Test**: Create task as User A, delete it, verify task removed from database. Attempt to delete as User B, verify 404 returned.

**Prerequisites**: Phase 2 complete, User Story 1 complete (for test data creation)

### Implementation for User Story 4

- [ ] T028 [US4] Implement DELETE /api/tasks/{id} endpoint in backend/app/routes/tasks.py:
  - Accept path param id (integer)
  - Use Depends(get_current_user) to get authenticated user
  - Query task filtered by id AND user_id
  - Return 404 if task not found
  - Delete task from database
  - Return 204 No Content (empty response body)
  - Return 401 if JWT missing/invalid
- [ ] T029 [US4] Test DELETE /api/tasks/{id}: Delete task, verify removed from database
- [ ] T030 [US4] Test DELETE /api/tasks/{id} isolation: User A cannot delete User B's task (404 returned)
- [ ] T031 [US4] Test DELETE /api/tasks/{id} not found: Non-existent task ID returns 404
- [ ] T032 [US4] Test DELETE /api/tasks/{id} permanence: Deleted task cannot be retrieved (404 on GET)

**Checkpoint**: User Story 4 complete - users can delete tasks with proper isolation

---

## Phase 7: User Story 5 - Toggle Task Completion (Priority: P5)

**Goal**: Authenticated users can toggle completion status of their own tasks (true ↔ false). Returns 404 if task doesn't exist or doesn't belong to user.

**Independent Test**: Create incomplete task, toggle to complete, verify completed=true. Toggle again, verify completed=false.

**Prerequisites**: Phase 2 complete, User Story 1 complete (for test data creation)

### Implementation for User Story 5

- [ ] T033 [US5] Implement PATCH /api/tasks/{id}/complete endpoint in backend/app/routes/tasks.py:
  - Accept path param id (integer)
  - Use Depends(get_current_user) to get authenticated user
  - Query task filtered by id AND user_id
  - Return 404 if task not found
  - Toggle task.completed: `task.completed = not task.completed`
  - Update task.updated_at = now()
  - Save to database
  - Return 200 with {"data": task}
  - Return 401 if JWT missing/invalid
- [ ] T034 [US5] Test PATCH /api/tasks/{id}/complete: Toggle incomplete task to complete, verify completed=true
- [ ] T035 [US5] Test PATCH /api/tasks/{id}/complete: Toggle complete task to incomplete, verify completed=false
- [ ] T036 [US5] Test PATCH /api/tasks/{id}/complete isolation: User A cannot toggle User B's task (404 returned)
- [ ] T037 [US5] Test PATCH /api/tasks/{id}/complete not found: Non-existent task ID returns 404

**Checkpoint**: User Story 5 complete - users can toggle task completion with proper isolation

---

## Phase 8: Integration & Validation

**Purpose**: End-to-end validation with frontend integration

**Prerequisites**: All user stories (US1-US5) complete

- [ ] T038 Start backend server: `cd backend && uvicorn app.main:app --reload`
- [ ] T039 Verify backend health: `curl http://localhost:8000/` returns 200
- [ ] T040 Verify OpenAPI docs: Navigate to http://localhost:8000/docs, verify all 6 task endpoints visible
- [ ] T041 [P] Start frontend: `cd frontend && npm run dev`
- [ ] T042 Test frontend integration: Login, create task via UI, verify task appears in database
- [ ] T043 Test frontend integration: View task list, verify tasks from database displayed
- [ ] T044 Test frontend integration: Update task via UI, verify changes persist in database
- [ ] T045 Test frontend integration: Delete task via UI, verify task removed from database
- [ ] T046 Test frontend integration: Toggle task completion via UI, verify completed status updates in database
- [ ] T047 Test frontend integration: Refresh page, verify tasks persist (not mock data)
- [ ] T048 Test user isolation: Login as User A, create tasks, logout, login as User B, verify User B sees empty list

**Checkpoint**: All integration tests pass - frontend fully functional with backend

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

**Prerequisites**: Phase 8 complete

- [ ] T049 [P] Verify all constitution gates pass: JWT-only identity, database-backed persistence, user isolation, production-grade architecture
- [ ] T050 [P] Verify all success criteria from spec.md: Users can create/view/update/delete/complete tasks, 100% user isolation, tasks persist in database
- [ ] T051 [P] Run quickstart.md validation: Follow setup steps, verify all checkpoints pass
- [ ] T052 [P] Verify error handling: Test 401 (missing JWT), 404 (not found), 422 (validation), 503 (database down)
- [ ] T053 [P] Verify CORS configuration: Frontend can call backend without CORS errors
- [ ] T054 [P] Verify database constraints: Foreign key CASCADE delete works (delete user, verify tasks deleted)
- [ ] T055 [P] Verify indexes exist: `psql $DATABASE_URL -c "\di tasks*"` shows idx_tasks_user_id and idx_tasks_completed
- [ ] T056 Create PHR for implementation work in history/prompts/003-tasks-crud-api/

**Checkpoint**: Feature complete and validated - ready for production

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed) OR sequentially in priority order (P1 → P2 → P3 → P4 → P5)
  - Each user story is independently testable
- **Integration (Phase 8)**: Depends on all user stories being complete
- **Polish (Phase 9)**: Depends on Integration phase completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Uses US1 for test data but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses US1 for test data but independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Uses US1 for test data but independently testable
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Uses US1 for test data but independently testable

### Within Each User Story

- Implementation tasks before test tasks
- Core endpoint implementation before edge case tests
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1**: All 3 setup tasks can run in parallel
- **Phase 2**: T007 (Task model) and T008 (verify auth dependency) can run in parallel after T006 (migration verification)
- **Phase 3-7**: Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- **Phase 9**: All polish tasks marked [P] can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (3 tasks)
2. Complete Phase 2: Foundational (5 tasks) - CRITICAL
3. Complete Phase 3: User Story 1 (6 tasks)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready - users can create tasks!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (8 tasks)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! - 6 tasks)
3. Add User Story 2 → Test independently → Deploy/Demo (5 tasks)
4. Add User Story 3 → Test independently → Deploy/Demo (8 tasks)
5. Add User Story 4 → Test independently → Deploy/Demo (5 tasks)
6. Add User Story 5 → Test independently → Deploy/Demo (5 tasks)
7. Integration & Polish → Final validation (19 tasks)

**Total**: 56 tasks organized into 9 phases

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (8 tasks)
2. Once Foundational is done:
   - Developer A: User Story 1 (P1) - 6 tasks
   - Developer B: User Story 2 (P2) - 5 tasks
   - Developer C: User Story 3 (P3) - 8 tasks
3. Then:
   - Developer A: User Story 4 (P4) - 5 tasks
   - Developer B: User Story 5 (P5) - 5 tasks
4. Team completes Integration & Polish together (19 tasks)

---

## Task Summary

**Total Tasks**: 56

**By Phase**:
- Phase 1 (Setup): 3 tasks
- Phase 2 (Foundational): 5 tasks
- Phase 3 (US1 - Create Task): 6 tasks
- Phase 4 (US2 - View Tasks): 5 tasks
- Phase 5 (US3 - Update Task): 8 tasks
- Phase 6 (US4 - Delete Task): 5 tasks
- Phase 7 (US5 - Toggle Completion): 5 tasks
- Phase 8 (Integration): 11 tasks
- Phase 9 (Polish): 8 tasks

**By Priority**:
- P1 (MVP): 14 tasks (Setup + Foundational + US1)
- P2: 5 tasks (US2)
- P3: 8 tasks (US3)
- P4: 5 tasks (US4)
- P5: 5 tasks (US5)
- Integration: 11 tasks
- Polish: 8 tasks

**Critical Path**: Setup → Foundational → US1 → US2 → US3 → US4 → US5 → Integration → Polish

**Estimated Effort**:
- MVP (P1): ~4-6 hours
- Full Feature: ~12-16 hours
- With Testing: ~16-20 hours

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All endpoints filter by user_id from JWT (NEVER from request body)
- Return 404 (not 403) for unauthorized access to maintain security through obscurity
- Frontend requires NO changes - API client already has task methods
