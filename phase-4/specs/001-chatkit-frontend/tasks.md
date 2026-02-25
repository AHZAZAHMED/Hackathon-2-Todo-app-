# Tasks: ChatKit Frontend Integration

**Input**: Design documents from `/specs/001-chatkit-frontend/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete), data-model.md (complete), contracts/chat-api.md (complete)

**Tests**: Playwright validation included in final phase (FR-009 requirement)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/` for all new code
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and create foundational types

- [ ] T001 Install OpenAI ChatKit package (npm install @openai/chatkit or confirmed package name)
- [ ] T002 [P] Add environment variables to frontend/.env.local (NEXT_PUBLIC_API_BASE_URL, NEXT_PUBLIC_OPENAI_DOMAIN_KEY)
- [ ] T003 [P] Create TypeScript type definitions in frontend/types/chat.ts (ChatMessage, ChatSession interfaces)
- [ ] T004 [P] Update frontend/tailwind.config.js to add z-index values (z-chat-icon: 9998, z-chat-window: 9999)

**Checkpoint**: Dependencies installed, types defined, configuration ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create session storage utilities in frontend/lib/chat-storage.ts (saveChatState, loadChatState, saveMessages, loadMessages, clearChatStorage)
- [ ] T006 Create chat API client in frontend/lib/chat-client.ts (sendChatMessage function using existing api-client.ts)
- [ ] T007 Create useChat hook in frontend/hooks/useChat.ts (chat state management, message sending, error handling)
- [ ] T008 Create useChatAuth hook in frontend/hooks/useChatAuth.ts (JWT extraction, auth state detection)
- [ ] T009 Create ChatProvider context in frontend/components/chat/ChatProvider.tsx (wrap chat state and provide to components)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Access Chat Interface (Priority: P1) 🎯 MVP

**Goal**: Provide floating chat icon and window that users can open/close

**Independent Test**: Log in, navigate to any page, click chat icon, verify window opens with correct dimensions and positioning, close window, verify icon remains visible

### Implementation for User Story 1

- [ ] T010 [P] [US1] Create ChatIcon component in frontend/components/chat/ChatIcon.tsx (floating icon, bottom-right 20px offset, click handler)
- [ ] T011 [P] [US1] Create ChatWindow component in frontend/components/chat/ChatWindow.tsx (400px × 600px container, close button, fixed positioning above icon)
- [ ] T012 [P] [US1] Create ChatMessages component in frontend/components/chat/ChatMessages.tsx (scrollable message list container, empty state)
- [ ] T013 [P] [US1] Create ChatMessage component in frontend/components/chat/ChatMessage.tsx (individual message display, user/assistant styling)
- [ ] T014 [US1] Integrate ChatProvider into frontend/app/layout.tsx (wrap application with chat context)
- [ ] T015 [US1] Implement open/close logic in ChatProvider (toggle isOpen state, save to session storage)
- [ ] T016 [US1] Add Tailwind CSS styling to ChatIcon (blue-600 background, rounded-full, shadow-lg, hover effects)
- [ ] T017 [US1] Add Tailwind CSS styling to ChatWindow (white background, rounded-lg, shadow-xl, fixed positioning)

**Checkpoint**: At this point, User Story 1 should be fully functional - icon visible, window opens/closes, proper positioning

---

## Phase 4: User Story 2 - Send Messages to AI Assistant (Priority: P2)

**Goal**: Enable users to type messages, send to backend, and receive AI responses

**Independent Test**: Open chat window, type message, press Enter, verify message appears with "user" indicator, verify loading state, verify assistant response appears

### Implementation for User Story 2

- [ ] T018 [P] [US2] Create ChatInput component in frontend/components/chat/ChatInput.tsx (textarea, send button, Enter key handler)
- [ ] T019 [P] [US2] Implement 500-character limit in ChatInput (maxLength validation, disable send when exceeded)
- [ ] T020 [P] [US2] Add character counter to ChatInput (display remaining characters, update in real-time)
- [ ] T021 [US2] Implement message sending logic in useChat hook (create message with status="sending", call sendChatMessage, update status)
- [ ] T022 [US2] Add loading indicator to ChatMessages (display while waiting for backend response)
- [ ] T023 [US2] Implement assistant response handling in useChat hook (add assistant message to conversation on success)
- [ ] T024 [US2] Add user/assistant visual distinction in ChatMessage (different colors, alignment, or avatars)
- [ ] T025 [US2] Implement chronological message ordering in ChatMessages (sort by timestamp, scroll to bottom on new message)

**Checkpoint**: At this point, User Story 2 should be fully functional - messages sent, responses received, proper display

---

## Phase 5: User Story 3 - Secure Communication (Priority: P3)

**Goal**: Ensure all chat requests include JWT token, handle unauthenticated users, preserve conversation on token expiry

**Independent Test**: Inspect network requests to verify JWT in Authorization header, log out and click icon to verify redirect, expire token and verify conversation preservation

### Implementation for User Story 3

- [ ] T026 [US3] Verify JWT attachment in chat-client.ts (ensure api-client.ts automatically attaches Authorization header)
- [ ] T027 [US3] Implement unauthenticated user detection in ChatProvider (check auth state on icon click)
- [ ] T028 [US3] Implement login redirect in ChatProvider (redirect to login page, preserve current page URL)
- [ ] T029 [US3] Implement post-login return logic in ChatProvider (return to original page, auto-open chat window)
- [ ] T030 [US3] Implement 401 error detection in useChat hook (detect token expiry from backend response)
- [ ] T031 [US3] Implement conversation preservation on token expiry (save messages to session storage on 401)
- [ ] T032 [US3] Implement conversation restoration after re-auth (load messages from session storage, clear storage after restore)
- [ ] T033 [US3] Add error message for invalid/expired token (user-friendly message: "Please log in again")

**Checkpoint**: At this point, User Story 3 should be fully functional - JWT attached, unauthenticated users redirected, conversation preserved on token expiry

---

## Phase 6: User Story 4 - Optimal UI Experience (Priority: P4)

**Goal**: Ensure chat interface is well-positioned, properly sized, non-intrusive, and state persists across navigations

**Independent Test**: Open chat on different pages, verify positioning doesn't break layouts, navigate between pages with chat open/closed, verify state persists

### Implementation for User Story 4

- [ ] T034 [P] [US4] Implement chat window state persistence in ChatProvider (save isOpen to session storage on every change)
- [ ] T035 [P] [US4] Implement state restoration on page load in ChatProvider (load isOpen from session storage on mount)
- [ ] T036 [P] [US4] Verify chat window doesn't cover icon (adjust positioning if needed, ensure icon always visible)
- [ ] T037 [P] [US4] Implement fixed positioning for chat window (remains in place when page scrolls)
- [ ] T038 [P] [US4] Add scrollable message panel to ChatMessages (overflow-y-auto, max-height based on window size)
- [ ] T039 [P] [US4] Ensure chat window never opens fullscreen (enforce max dimensions 400px × 600px)
- [ ] T040 [P] [US4] Verify no blank black/white screens (add loading states, error boundaries)
- [ ] T041 [US4] Test chat on multiple Phase-2 pages (dashboard, settings, profile - verify no layout breaks)
- [ ] T042 [US4] Implement mobile responsive sizing (adapt to smaller screens while remaining usable)
- [ ] T043 [US4] Verify z-index hierarchy (chat appears above all page content, test with modals if any)

**Checkpoint**: At this point, User Story 4 should be fully functional - state persists, positioning optimal, no layout breaks

---

## Phase 7: Error Handling & Edge Cases

**Purpose**: Implement retry mechanism, error messages, and edge case handling

- [ ] T044 [P] Create ChatRetryButton component in frontend/components/chat/ChatRetryButton.tsx (retry button for failed messages)
- [ ] T045 [P] Implement failed message display in ChatMessage (red border or error icon for status="failed")
- [ ] T046 Implement error handling in useChat hook (catch network errors, set message status="failed", set error message)
- [ ] T047 Implement retry logic in useChat hook (resend failed message on retry button click)
- [ ] T048 Add user-friendly error messages (map error codes to friendly text: "Unable to connect", "Server error", etc.)
- [ ] T049 Implement backend unreachable handling (display error when /api/chat endpoint not available)
- [ ] T050 Implement network error detection (check navigator.onLine, display appropriate message)
- [ ] T051 Add error message for message send failure (display in ChatMessages or as toast)

**Checkpoint**: Error handling complete - failed messages show retry button, user-friendly error messages displayed

---

## Phase 8: Playwright Validation (Final Testing)

**Purpose**: Automated testing to verify all requirements (FR-009)

**⚠️ CRITICAL**: All previous phases must be complete before running these tests

- [ ] T052 [P] Write Playwright test for icon visibility in tests/chat/icon-visibility.spec.ts (verify icon on dashboard, settings, profile pages)
- [ ] T053 [P] Write Playwright test for window open/close in tests/chat/window-interaction.spec.ts (click icon, verify window opens, click close, verify window closes)
- [ ] T054 [P] Write Playwright test for message send in tests/chat/message-send.spec.ts (type message, send, verify appears in conversation)
- [ ] T055 [P] Write Playwright test for JWT attachment in tests/chat/jwt-auth.spec.ts (intercept network request, verify Authorization header)
- [ ] T056 [P] Write Playwright test for error handling in tests/chat/error-handling.spec.ts (mock backend failure, verify error message)
- [ ] T057 [P] Write Playwright test for character limit in tests/chat/character-limit.spec.ts (type 500+ chars, verify send disabled, verify counter)
- [ ] T058 [P] Write Playwright test for state persistence in tests/chat/state-persistence.spec.ts (open chat, navigate, verify still open)
- [ ] T059 [P] Write Playwright test for unauthenticated redirect in tests/chat/unauth-redirect.spec.ts (log out, click icon, verify redirect to login)
- [ ] T060 Run existing Phase-2 regression tests (verify task CRUD, authentication flows still work)
- [ ] T061 Run all Playwright tests and verify 100% pass rate (execute npx playwright test, review results)

**Checkpoint**: All tests passing - feature ready for deployment

---

## Dependencies & Execution Order

### User Story Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) → User Stories can be implemented in parallel
                                          ↓
                                    ┌─────┴─────┬─────────┬─────────┐
                                    ↓           ↓         ↓         ↓
                                  US1 (P1)   US2 (P2)  US3 (P3)  US4 (P4)
                                    ↓           ↓         ↓         ↓
                                    └─────┬─────┴─────────┴─────────┘
                                          ↓
                                    Phase 7 (Error Handling)
                                          ↓
                                    Phase 8 (Playwright Validation)
```

### Critical Path

1. **Setup** (T001-T004) - MUST complete first
2. **Foundational** (T005-T009) - MUST complete before user stories
3. **US1** (T010-T017) - MVP, should complete first for early validation
4. **US2** (T018-T025) - Builds on US1, can start after US1 complete
5. **US3** (T026-T033) - Can run parallel with US2 and US4
6. **US4** (T034-T043) - Can run parallel with US2 and US3
7. **Error Handling** (T044-T051) - After all user stories
8. **Playwright** (T052-T061) - Final validation

### Parallel Execution Opportunities

**Within Setup Phase**:
- T002, T003, T004 can run in parallel (different files)

**Within Foundational Phase**:
- T005, T006 can run in parallel (different files)
- T007, T008 can run in parallel (different hooks)

**Within US1**:
- T010, T011, T012, T013 can run in parallel (different components)
- T016, T017 can run in parallel (different styling tasks)

**Within US2**:
- T018, T019, T020 can run in parallel (all in ChatInput component)
- T024, T025 can run in parallel (different components)

**Within US3**:
- T027, T028 can run in parallel (different logic paths)

**Within US4**:
- T034, T035, T036, T037, T038, T039, T040, T042, T043 can run in parallel (different aspects)

**Within Error Handling**:
- T044, T045 can run in parallel (different components)

**Within Playwright**:
- T052-T059 can run in parallel (independent test files)

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Recommended MVP**: User Story 1 (P1) only
- Delivers: Floating chat icon, open/close window, basic UI
- Value: Users can access chat interface
- Testable: Icon visible, window opens/closes
- Tasks: T001-T017 (17 tasks)

### Incremental Delivery

1. **Sprint 1**: Setup + Foundational + US1 (T001-T017)
   - Deliverable: Chat icon and window (no messaging yet)
   - Demo: Show icon, open window, close window

2. **Sprint 2**: US2 (T018-T025)
   - Deliverable: Message sending and receiving
   - Demo: Send message, receive response

3. **Sprint 3**: US3 + US4 (T026-T043)
   - Deliverable: Security and UX polish
   - Demo: Auth flow, state persistence, styling

4. **Sprint 4**: Error Handling + Playwright (T044-T061)
   - Deliverable: Production-ready feature
   - Demo: Error scenarios, test results

### Testing Strategy

- **Manual Testing**: After each user story phase
- **Playwright Testing**: After all user stories complete (Phase 8)
- **Regression Testing**: After Phase 8 (T060)

---

## Task Summary

- **Total Tasks**: 61
- **Setup Phase**: 4 tasks (T001-T004)
- **Foundational Phase**: 5 tasks (T005-T009)
- **User Story 1 (P1)**: 8 tasks (T010-T017)
- **User Story 2 (P2)**: 8 tasks (T018-T025)
- **User Story 3 (P3)**: 8 tasks (T026-T033)
- **User Story 4 (P4)**: 10 tasks (T034-T043)
- **Error Handling**: 8 tasks (T044-T051)
- **Playwright Validation**: 10 tasks (T052-T061)

**Parallel Opportunities**: 35 tasks marked with [P] can run in parallel within their phase

**Independent Test Criteria**:
- US1: Icon visible, window opens/closes, proper positioning
- US2: Messages sent, responses received, proper display
- US3: JWT attached, auth flow works, conversation preserved
- US4: State persists, positioning optimal, no layout breaks

---

## Success Criteria Mapping

| Success Criterion | Tasks | Validation |
|-------------------|-------|------------|
| SC-001: Open < 1 second | T010-T017 | T053 (Playwright test) |
| SC-002: Icon on 100% pages | T010, T014 | T052 (Playwright test) |
| SC-003: Proper dimensions | T011, T017 | T053 (Playwright test) |
| SC-004: JWT attached | T026 | T055 (Playwright test) |
| SC-005: Send/receive < 5s | T018-T025 | T054 (Playwright test) |
| SC-006: User-friendly errors | T044-T051 | T056 (Playwright test) |
| SC-007: Playwright passes | T052-T061 | T061 (run all tests) |
| SC-008: Phase-2 regression | All tasks | T060 (regression tests) |
| SC-009: No degradation | T034-T043 | T053 (repeated open/close) |
| SC-010: No blank screens | T040 | T053 (visual check) |

---

## Ready for Implementation

✅ **All tasks defined with specific file paths**
✅ **Tasks organized by user story for independent implementation**
✅ **Parallel execution opportunities identified**
✅ **Dependencies clearly documented**
✅ **MVP scope defined (US1 only)**
✅ **Incremental delivery strategy provided**
✅ **Success criteria mapped to tasks**

**Next Step**: Begin implementation with Phase 1 (Setup) tasks T001-T004
