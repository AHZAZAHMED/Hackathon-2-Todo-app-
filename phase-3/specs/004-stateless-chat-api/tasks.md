# Tasks: Stateless Chat API + OpenAI Agent Orchestration

**Input**: Design documents from `/specs/004-stateless-chat-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chat-api.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with backend/frontend separation. All tasks focus on backend implementation.
- Backend: `backend/app/`, `backend/migrations/`, `backend/tests/`
- Frontend: Already implemented in Spec-1 (ChatKit UI)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment configuration

- [ ] T001 Update backend/requirements.txt with new dependencies (openai>=1.0.0, agents>=0.1.0, pyjwt>=2.8.0, asyncpg>=0.29.0, httpx>=0.25.0)
- [ ] T002 Install dependencies via pip install -r backend/requirements.txt
- [ ] T003 [P] Create backend/.env.example with required environment variables (DATABASE_URL, BETTER_AUTH_SECRET, OPENROUTER_API_KEY, AI_MODEL)
- [ ] T004 [P] Update backend/app/config.py to add OPENROUTER_API_KEY and AI_MODEL configuration variables

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create database migration script backend/migrations/003_create_chat_tables.sql with conversations and messages tables per data-model.md
- [ ] T006 Apply migration 003_create_chat_tables.sql to database (verify tables created with proper indexes and foreign keys)
- [ ] T007 [P] Create Conversation SQLModel in backend/app/models/conversation.py with fields (id, user_id, title, created_at, updated_at)
- [ ] T008 [P] Create Message SQLModel in backend/app/models/message.py with MessageRole enum and fields (id, conversation_id, role, content, created_at)
- [ ] T009 Update backend/app/models/__init__.py to export Conversation and Message models
- [ ] T010 Verify JWT verification dependency exists in backend/app/auth/dependencies.py (get_current_user function)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Send Chat Message (Priority: P1) 🎯 MVP

**Goal**: Enable authenticated users to send a message and receive an AI-generated response

**Independent Test**: Authenticate a user, send POST to /api/chat with a message, verify AI response is returned with conversation_id

### Implementation for User Story 1

- [ ] T011 [P] [US1] Create ChatRequest schema in backend/app/schemas/chat.py with message (str, 1-2000 chars) and conversation_id (Optional[UUID])
- [ ] T012 [P] [US1] Create ChatResponse schema in backend/app/schemas/chat.py with conversation_id (UUID), response (str), and timestamp (datetime)
- [ ] T013 [US1] Create AIAgentService class in backend/app/services/ai_agent.py with OpenAI Agents SDK integration per research.md (AsyncOpenAI + OpenAIChatCompletionsModel + Agent + Runner)
- [ ] T014 [US1] Implement generate_response method in AIAgentService that accepts conversation_history and returns AI response string
- [ ] T015 [US1] Create chat router in backend/app/routes/chat.py with POST /api/chat endpoint skeleton
- [ ] T016 [US1] Implement JWT verification in chat endpoint using get_current_user dependency to extract user_id
- [ ] T017 [US1] Implement conversation creation logic in chat endpoint (create new Conversation if conversation_id not provided)
- [ ] T018 [US1] Implement user message persistence in chat endpoint (store Message with role='user' before AI invocation)
- [ ] T019 [US1] Implement AI agent invocation in chat endpoint (call AIAgentService.generate_response with empty history for first message)
- [ ] T020 [US1] Implement assistant message persistence in chat endpoint (store Message with role='assistant' after AI response)
- [ ] T021 [US1] Implement response return logic in chat endpoint (return ChatResponse with conversation_id, response, timestamp)
- [ ] T022 [US1] Register chat router in backend/app/main.py (app.include_router(chat.router))

**Checkpoint**: At this point, User Story 1 should be fully functional - users can send a message and receive an AI response

---

## Phase 4: User Story 2 - Maintain Conversation Context (Priority: P2)

**Goal**: Enable multi-turn conversations where AI remembers previous exchanges

**Independent Test**: Send multiple messages with same conversation_id and verify later responses reference earlier messages

### Implementation for User Story 2

- [ ] T023 [US2] Implement conversation history loading in chat endpoint (query last 50 messages ordered by created_at ASC for given conversation_id)
- [ ] T024 [US2] Implement message array building in chat endpoint (convert Message objects to dict format with 'role' and 'content' for AI agent)
- [ ] T025 [US2] Update AI agent invocation in chat endpoint to pass full conversation_history to AIAgentService.generate_response
- [ ] T026 [US2] Implement conversation updated_at timestamp update in chat endpoint (trigger should handle this automatically per migration)
- [ ] T027 [US2] Add conversation_id validation in chat endpoint (verify conversation exists and belongs to authenticated user)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users can have multi-turn contextual conversations

---

## Phase 5: User Story 3 - Secure Access Control (Priority: P3)

**Goal**: Ensure only authenticated users can access chat API and users can only access their own conversations

**Independent Test**: Attempt access without JWT (should fail 401), with invalid JWT (should fail 401), with another user's conversation_id (should create new conversation)

### Implementation for User Story 3

- [ ] T028 [US3] Implement 401 Unauthorized error handling in chat endpoint for missing or invalid JWT tokens
- [ ] T029 [US3] Implement conversation ownership validation in chat endpoint (when conversation_id provided, verify it belongs to authenticated user)
- [ ] T030 [US3] Implement forgiving conversation_id handling in chat endpoint (if invalid or belongs to another user, create new conversation silently per spec clarification)
- [ ] T031 [US3] Add user_id extraction verification in chat endpoint (ensure user_id comes from JWT claims only, never from request body)
- [ ] T032 [US3] Implement database query filtering in chat endpoint (all Conversation and Message queries MUST filter by authenticated user_id)

**Checkpoint**: All security requirements should now be enforced - user isolation and authentication working correctly

---

## Phase 6: User Story 4 - Stateless Backend Operation (Priority: P4)

**Goal**: Ensure backend operates statelessly without in-memory conversation data

**Independent Test**: Send message, restart backend server, send another message with same conversation_id and verify full history is available

### Implementation for User Story 4

- [ ] T033 [US4] Verify no class-level or module-level conversation state in backend/app/routes/chat.py (all state from database)
- [ ] T034 [US4] Verify no class-level or module-level conversation state in backend/app/services/ai_agent.py (stateless service)
- [ ] T035 [US4] Verify database session management in chat endpoint uses async context manager (no persistent connections)
- [ ] T036 [US4] Add database connection pooling configuration in backend/app/database.py (pool_size=10, max_overflow=20, pool_pre_ping=True)
- [ ] T037 [US4] Verify conversation history is loaded from database on every request in chat endpoint (no caching)

**Checkpoint**: Backend should be fully stateless - server restarts should not affect conversation continuity

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, validation, logging, and documentation improvements

- [ ] T038 [P] Implement 422 Unprocessable Entity error handling in chat endpoint for empty messages (whitespace-only validation)
- [ ] T039 [P] Implement 422 Unprocessable Entity error handling in chat endpoint for messages exceeding 2000 characters
- [ ] T040 [P] Implement 500 Internal Server Error handling in chat endpoint for database failures (with rollback)
- [ ] T041 [P] Implement 503 Service Unavailable error handling in chat endpoint for OpenRouter API failures
- [ ] T042 [P] Add structured logging in chat endpoint (JSON format with request_id, hashed user_id, endpoint, error type per spec FR-015)
- [ ] T043 [P] Add structured logging in AIAgentService (exclude JWT tokens, message content, passwords per spec)
- [ ] T044 [P] Implement transaction handling in chat endpoint with Read Committed isolation and row locking (SELECT FOR UPDATE on conversation)
- [ ] T045 [P] Add input validation in chat endpoint (message length, conversation_id format)
- [ ] T046 [P] Update backend/.env.example with detailed comments for each environment variable
- [ ] T047 Verify quickstart.md instructions work end-to-end (environment setup through testing)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on User Story 1 completion - Extends US1 with conversation history
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent security layer
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Architectural verification

### Within Each User Story

- **US1**: Schemas → AI Service → Chat endpoint skeleton → Message persistence → AI invocation → Response return
- **US2**: History loading → Message array building → AI invocation with context
- **US3**: Auth error handling → Ownership validation → User isolation
- **US4**: State verification → Connection pooling → Database-driven state

### Parallel Opportunities

- **Phase 1**: T003 and T004 can run in parallel (different files)
- **Phase 2**: T007 and T008 can run in parallel (different model files)
- **Phase 3**: T011 and T012 can run in parallel (different schemas in same file, but independent)
- **Phase 7**: All tasks marked [P] can run in parallel (different concerns, different files)

---

## Parallel Example: User Story 1

```bash
# Launch schema creation tasks together:
Task T011: "Create ChatRequest schema in backend/app/schemas/chat.py"
Task T012: "Create ChatResponse schema in backend/app/schemas/chat.py"

# After schemas complete, launch service creation:
Task T013: "Create AIAgentService class in backend/app/services/ai_agent.py"
Task T015: "Create chat router in backend/app/routes/chat.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T010) - CRITICAL
3. Complete Phase 3: User Story 1 (T011-T022)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Send a message without conversation_id → Should create new conversation and return AI response
   - Verify conversation and messages persisted in database
   - Verify JWT authentication required
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
   - Users can send messages and receive AI responses
3. Add User Story 2 → Test independently → Deploy/Demo
   - Users can have multi-turn contextual conversations
4. Add User Story 3 → Test independently → Deploy/Demo
   - Security and user isolation enforced
5. Add User Story 4 → Test independently → Deploy/Demo
   - Stateless operation verified, horizontal scaling enabled
6. Add Polish (Phase 7) → Final validation → Production deployment

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T010)
2. Once Foundational is done:
   - Developer A: User Story 1 (T011-T022) - Core chat functionality
   - Developer B: User Story 3 (T028-T032) - Security layer (can start in parallel)
   - Developer C: User Story 4 (T033-T037) - Stateless verification (can start in parallel)
3. After US1 completes:
   - Developer A: User Story 2 (T023-T027) - Extends US1 with context
4. After all stories complete:
   - All developers: Polish tasks (T038-T047) in parallel

---

## Notes

- [P] tasks = different files or independent concerns, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- User Story 2 extends User Story 1, so US1 must complete first
- User Stories 3 and 4 are independent and can run in parallel with US1
- All tasks use exact file paths from plan.md structure
- No test tasks included (not requested in specification)
- Frontend ChatKit UI already implemented in Spec-1, this focuses on backend only

---

## Task Count Summary

- **Total Tasks**: 47
- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 6 tasks
- **Phase 3 (US1 - MVP)**: 12 tasks
- **Phase 4 (US2)**: 5 tasks
- **Phase 5 (US3)**: 5 tasks
- **Phase 6 (US4)**: 5 tasks
- **Phase 7 (Polish)**: 10 tasks

**Parallel Opportunities**: 15 tasks marked [P] can run in parallel within their phases

**MVP Scope**: Phases 1-3 (22 tasks) deliver the minimum viable product - users can send messages and receive AI responses

**Suggested First Milestone**: Complete through Phase 3 (User Story 1) for initial deployment and validation
