# Tasks: MCP Task Server + Database Layer

**Input**: Design documents from `/specs/001-mcp-task-server/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, clarifications applied

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and MCP server structure

- [X] T001 Create MCP server directory structure in backend/app/mcp/
- [X] T002 Create MCP tools directory structure in backend/app/mcp/tools/
- [X] T003 [P] Add mcp[cli] dependency to backend/requirements.txt
- [X] T004 [P] Create MCP server initialization file backend/app/mcp/__init__.py
- [X] T005 [P] Create MCP tools package file backend/app/mcp/tools/__init__.py
- [X] T006 Create MCP server startup script backend/scripts/run_mcp_server.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core MCP server infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Implement MCP server initialization in backend/app/mcp/server.py using MCPServer with stdio transport
- [X] T008 Configure database connection pooling with pool_size=10, max_overflow=20 in backend/app/database.py
- [X] T009 [P] Create base tool response format utilities in backend/app/mcp/utils.py
- [X] T010 [P] Implement user_id validation helper in backend/app/mcp/utils.py
- [X] T011 Verify existing Task model in backend/app/models/task.py supports all required operations

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Agent Creates Tasks via MCP (Priority: P1) 🎯 MVP

**Goal**: Enable AI agent to create new tasks via add_task MCP tool with database persistence

**Independent Test**: Invoke add_task tool with valid parameters and verify task appears in database with correct user_id, title, and default values

### Implementation for User Story 1

- [X] T012 [P] [US1] Create add_task tool implementation in backend/app/mcp/tools/add_task.py
- [X] T013 [US1] Implement input validation (user_id required, title required, title max 500 chars) in add_task
- [X] T014 [US1] Implement database insert operation using SQLModel with user_id filtering in add_task
- [X] T015 [US1] Implement response format (task_id, status="created", title) in add_task
- [X] T016 [US1] Implement error handling (missing user_id, empty title, title too long, database errors) in add_task
- [X] T017 [US1] Register add_task tool with MCP server in backend/app/mcp/server.py
- [ ] T018 [US1] Test add_task with valid inputs and verify database persistence
- [ ] T019 [US1] Test add_task error cases (empty title, missing user_id, title exceeds 500 chars)
- [ ] T020 [US1] Test add_task user isolation (verify user_id is enforced)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Agent Retrieves Task Lists (Priority: P2)

**Goal**: Enable AI agent to retrieve tasks via list_tasks MCP tool with filtering, pagination, and ordering

**Independent Test**: Pre-populate database with tasks for multiple users, invoke list_tasks for specific user_id, verify only that user's tasks returned with correct filtering and ordering

### Implementation for User Story 2

- [X] T021 [P] [US2] Create list_tasks tool implementation in backend/app/mcp/tools/list_tasks.py
- [X] T022 [US2] Implement input validation (user_id required, status optional with valid values) in list_tasks
- [X] T023 [US2] Implement pagination with limit parameter (default 100, max 1000) in list_tasks
- [X] T024 [US2] Implement task ordering by created_at DESC (newest first) in list_tasks
- [X] T025 [US2] Implement status filtering (all/pending/completed) using SQLModel queries in list_tasks
- [X] T026 [US2] Implement user isolation filtering (WHERE user_id = $1) in list_tasks
- [X] T027 [US2] Implement response format (array of task objects with all fields) in list_tasks
- [X] T028 [US2] Implement error handling (missing user_id, invalid status, database errors) in list_tasks
- [X] T029 [US2] Register list_tasks tool with MCP server in backend/app/mcp/server.py
- [ ] T030 [US2] Test list_tasks with status filtering (pending, completed, all)
- [ ] T031 [US2] Test list_tasks pagination (verify limit parameter works, default 100, max 1000)
- [ ] T032 [US2] Test list_tasks ordering (verify newest tasks appear first)
- [ ] T033 [US2] Test list_tasks user isolation (verify cross-user access prevented)
- [ ] T034 [US2] Test list_tasks with empty result set (user with no tasks)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Agent Marks Tasks Complete (Priority: P3)

**Goal**: Enable AI agent to mark tasks as completed via complete_task MCP tool with idempotent behavior

**Independent Test**: Create a task, invoke complete_task with its task_id, verify completed field updated to true in database

### Implementation for User Story 3

- [X] T035 [P] [US3] Create complete_task tool implementation in backend/app/mcp/tools/complete_task.py
- [X] T036 [US3] Implement input validation (user_id required, task_id required) in complete_task
- [X] T037 [US3] Implement task lookup with user isolation (WHERE id = $1 AND user_id = $2) in complete_task
- [X] T038 [US3] Implement idempotent update (set completed=true, update updated_at) in complete_task
- [X] T039 [US3] Implement response format (task_id, status="completed", title) in complete_task
- [X] T040 [US3] Implement error handling (missing params, task not found, database errors) in complete_task
- [X] T041 [US3] Register complete_task tool with MCP server in backend/app/mcp/server.py
- [ ] T042 [US3] Test complete_task on pending task (verify completed field set to true)
- [ ] T043 [US3] Test complete_task idempotency (call twice, verify both return success)
- [ ] T044 [US3] Test complete_task user isolation (attempt to complete another user's task)
- [ ] T045 [US3] Test complete_task with non-existent task_id (verify error returned)

**Checkpoint**: User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Agent Updates Task Details (Priority: P4)

**Goal**: Enable AI agent to modify task title/description via update_task MCP tool with partial update support

**Independent Test**: Create a task, invoke update_task with modified title or description, verify changes persisted in database

### Implementation for User Story 4

- [X] T046 [P] [US4] Create update_task tool implementation in backend/app/mcp/tools/update_task.py
- [X] T047 [US4] Implement input validation (user_id required, task_id required, at least one field to update) in update_task
- [X] T048 [US4] Implement task lookup with user isolation (WHERE id = $1 AND user_id = $2) in update_task
- [X] T049 [US4] Implement partial update logic (update only provided fields: title, description) in update_task
- [X] T050 [US4] Implement title validation (max 500 chars, not empty if provided) in update_task
- [X] T051 [US4] Implement updated_at timestamp update in update_task
- [X] T052 [US4] Implement response format (task_id, status="updated", title) in update_task
- [X] T053 [US4] Implement error handling (missing params, no fields to update, task not found, title too long) in update_task
- [X] T054 [US4] Register update_task tool with MCP server in backend/app/mcp/server.py
- [ ] T055 [US4] Test update_task with title only (verify description unchanged)
- [ ] T056 [US4] Test update_task with description only (verify title unchanged)
- [ ] T057 [US4] Test update_task with both title and description
- [ ] T058 [US4] Test update_task user isolation (attempt to update another user's task)
- [ ] T059 [US4] Test update_task error cases (no fields provided, empty title, title too long)

**Checkpoint**: User Stories 1-4 should all work independently

---

## Phase 7: User Story 5 - Agent Deletes Tasks (Priority: P5)

**Goal**: Enable AI agent to remove tasks via delete_task MCP tool with non-idempotent behavior

**Independent Test**: Create a task, invoke delete_task with its task_id, verify task no longer exists in database

### Implementation for User Story 5

- [X] T060 [P] [US5] Create delete_task tool implementation in backend/app/mcp/tools/delete_task.py
- [X] T061 [US5] Implement input validation (user_id required, task_id required) in delete_task
- [X] T062 [US5] Implement task lookup with user isolation (WHERE id = $1 AND user_id = $2) in delete_task
- [X] T063 [US5] Capture task title before deletion for response in delete_task
- [X] T064 [US5] Implement hard delete operation (DELETE FROM tasks WHERE...) in delete_task
- [X] T065 [US5] Implement response format (task_id, status="deleted", title) in delete_task
- [X] T066 [US5] Implement error handling (missing params, task not found, database errors) in delete_task
- [X] T067 [US5] Register delete_task tool with MCP server in backend/app/mcp/server.py
- [ ] T068 [US5] Test delete_task on existing task (verify task removed from database)
- [ ] T069 [US5] Test delete_task non-idempotency (call twice, verify second call returns error)
- [ ] T070 [US5] Test delete_task user isolation (attempt to delete another user's task)
- [ ] T071 [US5] Test delete_task with non-existent task_id (verify error returned)

**Checkpoint**: All 5 user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T072 [P] Add comprehensive logging for all MCP tool operations in backend/app/mcp/tools/
- [ ] T073 [P] Add performance monitoring for database operations (verify <200ms target)
- [ ] T074 [P] Create integration test suite in backend/tests/test_mcp_integration.py
- [ ] T075 [P] Create user isolation test suite in backend/tests/test_mcp_user_isolation.py
- [ ] T076 [P] Create performance test suite in backend/tests/test_mcp_performance.py
- [ ] T077 Validate quickstart.md instructions by following them end-to-end
- [ ] T078 [P] Add error message quality validation (verify all errors are clear and actionable)
- [ ] T079 [P] Verify stateless operation (restart server, verify no data loss)
- [ ] T080 Run concurrency tests (100 concurrent tool invocations)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1 (but benefits from having tasks to list)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent of US1/US2 (but needs tasks to complete)
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Independent of US1-US3 (but needs tasks to update)
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Independent of US1-US4 (but needs tasks to delete)

### Within Each User Story

- Tool implementation before registration
- Registration before testing
- Basic tests before edge case tests
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004, T005)
- All Foundational tasks marked [P] can run in parallel (T009, T010)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Tool implementations within different stories marked [P] can run in parallel (T012, T021, T035, T046, T060)
- All Polish tasks marked [P] can run in parallel (T072-T079)

---

## Parallel Example: After Foundational Phase

```bash
# Launch all tool implementations together (different files):
Task T012: "Create add_task tool implementation in backend/app/mcp/tools/add_task.py"
Task T021: "Create list_tasks tool implementation in backend/app/mcp/tools/list_tasks.py"
Task T035: "Create complete_task tool implementation in backend/app/mcp/tools/complete_task.py"
Task T046: "Create update_task tool implementation in backend/app/mcp/tools/update_task.py"
Task T060: "Create delete_task tool implementation in backend/app/mcp/tools/delete_task.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T011) - CRITICAL
3. Complete Phase 3: User Story 1 (T012-T020)
4. **STOP and VALIDATE**: Test add_task independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (add_task) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (list_tasks) → Test independently → Deploy/Demo
4. Add User Story 3 (complete_task) → Test independently → Deploy/Demo
5. Add User Story 4 (update_task) → Test independently → Deploy/Demo
6. Add User Story 5 (delete_task) → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T012-T020)
   - Developer B: User Story 2 (T021-T034)
   - Developer C: User Story 3 (T035-T045)
   - Developer D: User Story 4 (T046-T059)
   - Developer E: User Story 5 (T060-T071)
3. Stories complete and integrate independently

---

## Clarifications Applied

The following clarifications from `/sp.clarify` session are reflected in these tasks:

1. **MCP SDK Version**: Tasks use latest `mcp[cli]` without version constraints (T003)
2. **Pagination**: list_tasks implements limit parameter with default 100, max 1000 (T023, T031)
3. **Idempotency**: complete_task is idempotent (T038, T043), delete_task is non-idempotent (T069)
4. **Task Ordering**: list_tasks orders by created_at DESC (T024, T032)
5. **Connection Pooling**: Database configured with pool_size=10, max_overflow=20 (T008)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tasks follow clarified requirements from spec.md
- Performance targets: <200ms for operations, <100ms for list queries
- User isolation enforced on every database query
- Stateless operation required (no in-memory state)

---

**Total Tasks**: 80
**MVP Tasks** (Setup + Foundational + US1): 20 tasks
**Parallel Opportunities**: 15 tasks can run in parallel after foundational phase
**Estimated Completion**: MVP can be completed and validated independently before proceeding to additional user stories
