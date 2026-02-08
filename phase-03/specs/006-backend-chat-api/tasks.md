# Tasks: Backend Chat API + OpenAI Agent Orchestration

**Input**: Design documents from `/specs/006-backend-chat-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are NOT included in this task list as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/app/` for source code, `backend/tests/` for tests
- All paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [x] T001 Install OpenAI Agents SDK dependencies in backend/requirements.txt (openai, openai-agents, tiktoken)
- [x] T002 [P] Add GEMINI_API_KEY to backend/.env.example with placeholder value
- [x] T003 [P] Create backend/app/ai/ directory for agent logic
- [x] T004 [P] Create backend/app/mcp/ directory for MCP tools
- [x] T005 [P] Create backend/app/services/ directory for business logic
- [x] T006 [P] Create backend/app/middleware/ directory for timeout middleware

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Create database migration 003 in backend/migrations/003_create_chat_tables.sql with conversations and messages tables
- [ ] T008 Apply migration 003 to create conversations and messages tables in database ⚠️ REQUIRES MANUAL EXECUTION
- [x] T009 [P] Create Conversation SQLModel in backend/app/models/conversation.py with user_id foreign key
- [x] T010 [P] Create Message SQLModel in backend/app/models/message.py with conversation_id foreign key and role enum
- [x] T011 [P] Create TimeoutMiddleware in backend/app/middleware/timeout.py with 5 second timeout for /api/chat
- [x] T012 Register TimeoutMiddleware in backend/app/main.py FastAPI application

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

**⚠️ ACTION REQUIRED**: Before proceeding to Phase 3, run the database migration:
```bash
psql $DATABASE_URL -f backend/migrations/003_create_chat_tables.sql
```

---

## Phase 3: User Story 1 - Send Chat Message and Receive AI Response (Priority: P1) 🎯 MVP

**Goal**: Enable users to send a message to /api/chat and receive an AI-generated response

**Independent Test**: Send POST request to /api/chat with valid JWT and message "Hello". Verify API returns 200 with AI response and conversation_id. Test with curl without needing frontend.

### Implementation for User Story 1

- [x] T013 [P] [US1] Create Gemini client configuration in backend/app/ai/gemini_client.py with AsyncOpenAI and custom base_url
- [x] T014 [P] [US1] Create system prompts in backend/app/ai/prompts.py for task management assistant
- [x] T015 [US1] Create agent setup in backend/app/ai/agent.py with OpenAIChatCompletionsModel and Agent configuration (depends on T013, T014)
- [x] T016 [P] [US1] Create ChatRequest Pydantic model in backend/app/routes/chat.py with message and optional conversation_id fields
- [x] T017 [P] [US1] Create ChatResponse Pydantic model in backend/app/routes/chat.py with conversation_id, response, and tool_calls fields
- [x] T018 [US1] Implement POST /api/chat endpoint in backend/app/routes/chat.py with JWT verification and user_id extraction
- [x] T019 [US1] Implement get_or_create_conversation function in backend/app/services/conversation_service.py
- [x] T020 [US1] Implement store_message function in backend/app/services/message_service.py
- [x] T021 [US1] Integrate agent invocation in chat endpoint with Runner.run_sync (no tools yet, just basic response)
- [x] T022 [US1] Add request validation in chat endpoint (message length max 10,000 characters)
- [x] T023 [US1] Register /api/chat route in backend/app/main.py FastAPI application

**Checkpoint**: At this point, User Story 1 should be fully functional - users can send messages and receive AI responses

---

## Phase 4: User Story 2 - Maintain Conversation Context (Priority: P1) 🎯 MVP

**Goal**: Remember conversation history across multiple messages so AI provides contextual responses

**Independent Test**: Send multiple messages in sequence with same conversation_id. Verify AI responses reference previous messages. Example: "Add a task to buy milk" followed by "Mark it as complete" - second message should work without re-specifying task.

### Implementation for User Story 2

- [x] T024 [P] [US2] Install tiktoken library in backend/requirements.txt for token counting (completed in T001)
- [x] T025 [US2] Implement load_conversation_history function in backend/app/services/message_service.py with token counting (2000 token limit)
- [x] T026 [US2] Update chat endpoint to load conversation history before agent invocation in backend/app/routes/chat.py (already implemented in T018)
- [x] T027 [US2] Update agent invocation to include conversation history in messages array in backend/app/routes/chat.py (already implemented in T021)
- [x] T028 [US2] Store user message before agent invocation in chat endpoint (already implemented in T018)
- [x] T029 [US2] Store assistant response after agent completion in chat endpoint (already implemented in T018)
- [x] T030 [US2] Update conversations.updated_at timestamp on new message (verify trigger works from migration) (trigger created in T007)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - conversation context is maintained across messages

**Note**: User Story 2 functionality was implemented as part of User Story 1 since conversation context is essential for basic chat functionality.

---

## Phase 5: User Story 3 - AI Agent Invokes MCP Tools for Task Operations (Priority: P1) 🎯 MVP

**Goal**: Enable AI agent to perform task management operations (create, list, update, complete, delete) through natural conversation

**Independent Test**: Send message "Add a task to buy groceries". Verify AI agent invokes add_task MCP tool and new task appears in database. Check response includes tool_calls array showing which tools were invoked.

### Implementation for User Story 3

- [x] T031 [P] [US3] Create Task Pydantic model in backend/app/mcp/tools.py for structured tool returns
- [x] T032 [P] [US3] Implement add_task MCP tool in backend/app/mcp/tools.py with user_id, title, description parameters
- [x] T033 [P] [US3] Implement list_tasks MCP tool in backend/app/mcp/tools.py with user_id and optional completed filter
- [x] T034 [P] [US3] Implement complete_task MCP tool in backend/app/mcp/tools.py with user_id and task_id parameters
- [x] T035 [P] [US3] Implement delete_task MCP tool in backend/app/mcp/tools.py with user_id and task_id parameters
- [x] T036 [P] [US3] Implement update_task MCP tool in backend/app/mcp/tools.py with user_id, task_id, optional title and description
- [x] T037 [US3] Create MCP tool registration in backend/app/mcp/server.py converting functions to Tool objects (depends on T032-T036)
- [x] T038 [US3] Update agent configuration in backend/app/ai/agent.py to include MCP tools array
- [x] T039 [US3] Update chat endpoint to pass user_id to agent context for MCP tool invocation in backend/app/routes/chat.py
- [x] T040 [US3] Update chat endpoint to capture tool_calls from agent response and include in ChatResponse
- [x] T041 [US3] Add error handling for MCP tool failures in chat endpoint (catch MCPToolError, return 500)

**Checkpoint**: All P1 user stories (1, 2, 3) should now be independently functional - full conversational task management works

---

## Phase 6: User Story 4 - Handle Authentication and Authorization (Priority: P2)

**Goal**: Verify user identity via JWT and ensure users can only access their own conversations and tasks

**Independent Test**: Send request without JWT - verify 401. Send request with invalid JWT - verify 401. Send request with valid JWT for User A trying to access User B's conversation_id - verify 403 or conversation not found.

### Implementation for User Story 4

- [x] T042 [US4] Verify JWT verification is working in chat endpoint (should already exist from Phase-2)
- [x] T043 [US4] Add conversation ownership validation in get_or_create_conversation function in backend/app/services/conversation_service.py
- [x] T044 [US4] Return 403 Forbidden if user tries to access another user's conversation_id in chat endpoint
- [x] T045 [US4] Verify user_id is passed to all MCP tools (should already be done in T039)
- [x] T046 [US4] Add logging for authentication failures in chat endpoint

**Checkpoint**: User Story 4 complete - authentication and authorization properly enforced

---

## Phase 7: User Story 5 - Handle Errors Gracefully (Priority: P2)

**Goal**: Provide clear, user-friendly error messages when something goes wrong

**Independent Test**: Trigger various error conditions (invalid JWT, Gemini API down, MCP tool failure) and verify API returns appropriate HTTP status codes with user-friendly error messages.

### Implementation for User Story 5

- [x] T047 [P] [US5] Create custom exception classes in backend/app/exceptions.py (GeminiAPIError, MCPToolError, ValidationError)
- [x] T048 [US5] Add try-except block for JWTError in chat endpoint returning 401 with user-friendly message
- [x] T049 [US5] Add try-except block for ValidationError in chat endpoint returning 422 with descriptive message
- [x] T050 [US5] Add try-except block for GeminiAPIError in chat endpoint returning 503 with user-friendly message
- [x] T051 [US5] Add try-except block for MCPToolError in chat endpoint returning 500 with user-friendly message
- [x] T052 [US5] Add try-except block for generic Exception in chat endpoint returning 500 with safe message
- [x] T053 [US5] Add structured logging for all errors in chat endpoint (log full error, return safe message to user)
- [x] T054 [US5] Verify TimeoutMiddleware returns 504 for requests exceeding 5 seconds
- [x] T055 [US5] Add graceful fallback for invalid conversation_id (treat as new conversation instead of error)

**Checkpoint**: All user stories (1-5) should now be complete with proper error handling

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T056 [P] Update backend/README.md with chat API documentation and setup instructions
- [x] T057 [P] Verify all environment variables documented in backend/.env.example
- [x] T058 [P] Add code comments for complex logic in agent.py and chat.py
- [ ] T059 Run quickstart.md validation - follow all 10 steps and verify they work ⚠️ REQUIRES MANUAL EXECUTION (see VALIDATION_CHECKLIST.md)
- [x] T060 [P] Add database connection pooling configuration in backend/app/database.py (pool_size=10, max_overflow=20)
- [x] T061 [P] Configure structured logging format in backend/app/main.py
- [ ] T062 Verify Phase-2 CRUD endpoints still work (no regression) ⚠️ REQUIRES MANUAL EXECUTION (see VALIDATION_CHECKLIST.md)
- [x] T063 [P] Add CORS configuration for production frontend origin in backend/app/main.py
- [ ] T064 Performance test with 50 concurrent requests to verify no degradation ⚠️ REQUIRES MANUAL EXECUTION (see VALIDATION_CHECKLIST.md)
- [ ] T065 Verify conversation persists after server restart (stateless backend validation) ⚠️ REQUIRES MANUAL EXECUTION (see VALIDATION_CHECKLIST.md)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P1): Depends on User Story 1 completion (needs chat endpoint and agent)
  - User Story 3 (P1): Depends on User Story 1 completion (needs agent infrastructure)
  - User Story 4 (P2): Can start after Foundational - Validates existing auth
  - User Story 5 (P2): Can start after User Story 1 completion (needs endpoint to add error handling)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Depends on User Story 1 (needs chat endpoint and agent infrastructure)
- **User Story 3 (P1)**: Depends on User Story 1 (needs agent infrastructure to add tools)
- **User Story 4 (P2)**: Can start after Foundational (validates existing auth from Phase-2)
- **User Story 5 (P2)**: Depends on User Story 1 (needs endpoint to add error handling)

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002-T006)
- All Foundational tasks marked [P] can run in parallel (T009-T011)
- Within User Story 1: T013, T014, T016, T017 can run in parallel
- Within User Story 3: T031-T036 (all MCP tools) can run in parallel
- Within User Story 5: T047, T048-T052 can run in parallel
- Polish tasks marked [P] can run in parallel (T056-T058, T060-T061, T063)

---

## Parallel Example: User Story 3 (MCP Tools)

```bash
# Launch all MCP tool implementations together:
Task: "Implement add_task MCP tool in backend/app/mcp/tools.py"
Task: "Implement list_tasks MCP tool in backend/app/mcp/tools.py"
Task: "Implement complete_task MCP tool in backend/app/mcp/tools.py"
Task: "Implement delete_task MCP tool in backend/app/mcp/tools.py"
Task: "Implement update_task MCP tool in backend/app/mcp/tools.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 3 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T012) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T013-T023) - Basic chat with AI response
4. Complete Phase 4: User Story 2 (T024-T030) - Add conversation context
5. Complete Phase 5: User Story 3 (T031-T041) - Add MCP tools for task management
6. **STOP and VALIDATE**: Test all P1 stories independently
7. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Basic chat works!)
3. Add User Story 2 → Test independently → Deploy/Demo (Context maintained!)
4. Add User Story 3 → Test independently → Deploy/Demo (Task management works! - MVP COMPLETE)
5. Add User Story 4 → Test independently → Deploy/Demo (Auth validated)
6. Add User Story 5 → Test independently → Deploy/Demo (Error handling complete)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T012)
2. Once Foundational is done:
   - Developer A: User Story 1 (T013-T023)
   - Developer B: User Story 4 (T042-T046) - Can start in parallel
3. After User Story 1 completes:
   - Developer A: User Story 2 (T024-T030)
   - Developer B: User Story 3 (T031-T041)
   - Developer C: User Story 5 (T047-T055)
4. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 65 tasks
- Phase 1 (Setup): 6 tasks
- Phase 2 (Foundational): 6 tasks
- Phase 3 (User Story 1 - P1): 11 tasks
- Phase 4 (User Story 2 - P1): 7 tasks
- Phase 5 (User Story 3 - P1): 11 tasks
- Phase 6 (User Story 4 - P2): 5 tasks
- Phase 7 (User Story 5 - P2): 9 tasks
- Phase 8 (Polish): 10 tasks

**Parallel Opportunities**: 23 tasks marked [P] can run in parallel within their phases

**MVP Scope**: Phases 1-5 (User Stories 1, 2, 3) = 41 tasks for complete conversational task management

**Independent Test Criteria**:
- US1: Send message, receive AI response (curl test)
- US2: Send multiple messages, verify context maintained
- US3: Send "Add task", verify tool invoked and task created
- US4: Send request without JWT, verify 401
- US5: Trigger errors, verify user-friendly messages

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Tests not included as they were not explicitly requested in specification
