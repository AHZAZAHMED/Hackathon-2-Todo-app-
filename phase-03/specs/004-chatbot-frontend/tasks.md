---
description: "Task list for Phase-3 Chatbot Frontend implementation"
---

# Tasks: Phase-3 Chatbot Frontend

**Input**: Design documents from `/specs/004-chatbot-frontend/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chat-api.yaml, quickstart.md

**Tests**: No test tasks included (not requested in specification)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Implementation Approach**: Using OpenAI ChatKit as specified, with custom wrapper components for floating launcher functionality.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/` for all frontend code
- Paths follow Next.js 16+ App Router conventions
- TypeScript files use `.tsx` for components, `.ts` for utilities

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install ChatKit and configure environment

- [X] T001 Install OpenAI ChatKit package via npm (follow official documentation at https://platform.openai.com/docs/guides/chatkit)
- [X] T002 Configure environment variables in frontend/.env.local (NEXT_PUBLIC_API_BASE_URL, NEXT_PUBLIC_OPENAI_DOMAIN_KEY)
- [X] T003 [P] Create TypeScript type definitions in frontend/types/chat.ts (ChatUIState for launcher state: isOpen, isMinimized)
- [X] T004 [P] Verify TypeScript compilation with strict mode (run npx tsc --noEmit in frontend/)

**Checkpoint**: ChatKit installed, environment configured, type definitions ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Configure ChatKit and create UI state management for floating launcher

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Configure ChatKit provider in frontend/app/layout.tsx (wrap application with ChatKit provider, pass JWT token and API endpoint configuration)
- [X] T006 Create ChatUIContext for launcher state in frontend/lib/contexts/ChatUIContext.tsx (manages isOpen, isMinimized state for floating launcher)
- [X] T007 Implement useChatUI custom hook in frontend/lib/contexts/ChatUIContext.tsx (returns openChat, closeChat, minimizeChat actions)
- [X] T008 Configure ChatKit authentication with JWT (pass JWT token from existing Phase-2 auth to ChatKit configuration)
- [X] T009 Configure ChatKit API endpoint (set ChatKit to use POST /api/chat endpoint)

**Checkpoint**: Foundation ready - ChatKit configured with JWT and API endpoint, UI state management ready for launcher

---

## Phase 3: User Story 1 - Send and Receive Chat Messages (Priority: P1) 🎯 MVP

**Goal**: Enable users to send messages to the AI chatbot and receive responses for conversational todo management

**Independent Test**: Log in, type "Show me my tasks", send message, verify assistant response appears with clear visual distinction from user message

### Implementation for User Story 1

- [X] T010 [US1] Create ChatInterface wrapper component in frontend/components/chat/ChatInterface.tsx (container that wraps ChatKit components, includes basic header)
- [X] T011 [US1] Integrate ChatKit message display components in ChatInterface (use ChatKit's message list component for displaying conversation)
- [X] T012 [US1] Integrate ChatKit input component in ChatInterface (use ChatKit's input component for message sending)
- [X] T013 [US1] Configure ChatKit message styling (customize ChatKit theme to match Tailwind CSS design system, ensure visual distinction between user and assistant messages)
- [X] T014 [US1] Test message sending and receiving (verify messages sent via ChatKit reach POST /api/chat and responses display correctly)
- [X] T015 [US1] Add loading states (configure ChatKit loading indicators for message sending)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can send messages and receive responses via ChatKit

---

## Phase 4: User Story 2 - View Conversation History (Priority: P2)

**Goal**: Enable users to see conversation history for context and continuity

**Independent Test**: Send multiple messages, refresh page, verify all previous messages still visible in chronological order

### Implementation for User Story 2

- [X] T016 [US2] Configure ChatKit conversation history loading (ensure ChatKit loads conversation history from backend on mount)
- [X] T017 [US2] Verify ChatKit auto-scroll functionality (test that ChatKit automatically scrolls to latest message)
- [X] T018 [US2] Test conversation persistence across page refreshes (verify ChatKit loads history from backend after refresh)
- [X] T019 [US2] Configure ChatKit message ordering (ensure messages display in chronological order)
- [X] T020 [US2] Test long conversation handling (verify ChatKit handles 50+ messages without performance issues)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - conversation history loads and persists via ChatKit

---

## Phase 5: User Story 3 - Access Chatbot from Any Page (Priority: P2)

**Goal**: Enable users to access chatbot from any authenticated page via floating launcher icon

**Independent Test**: Navigate to different pages (dashboard, tasks), verify floating icon appears consistently, click to open chat interface

### Implementation for User Story 3

- [X] T021 [P] [US3] Create FloatingChatLauncher component in frontend/components/chat/FloatingChatLauncher.tsx (floating button fixed at bottom-right, conditionally renders ChatInterface when open)
- [X] T022 [P] [US3] Create ChatHeader component in frontend/components/chat/ChatHeader.tsx (title, close button, minimize button with icons from lucide-react)
- [X] T023 [US3] Update ChatInterface to include ChatHeader (add header with close/minimize controls at top, wrap ChatKit components below)
- [X] T024 [US3] Implement open/close/minimize functionality (connect buttons to ChatUIContext actions: openChat, closeChat, minimizeChat)
- [X] T025 [US3] Add floating icon styling (60px circle, blue background, MessageCircle icon, fixed positioning bottom-6 right-6, z-40)
- [X] T026 [US3] Add chat interface container styling (slide-in panel from right, 400px width on desktop, rounded corners, shadow, z-50, contains ChatKit components)
- [X] T027 [US3] Integrate FloatingChatLauncher in root layout (modify frontend/app/layout.tsx to wrap children with ChatUIProvider and render FloatingChatLauncher)
- [X] T028 [US3] Configure z-index hierarchy in Tailwind config (add z-40 for launcher, z-50 for interface in frontend/tailwind.config.js)
- [X] T029 [US3] Implement chat state persistence across page navigations (ChatUIProvider at root layout level maintains launcher state during navigation)
- [X] T030 [US3] Add responsive positioning for mobile (adjust icon size and position for mobile breakpoints, full-screen modal on mobile with ChatKit inside)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - floating icon accessible from all pages with ChatKit interface

---

## Phase 6: User Story 4 - Handle Errors Gracefully (Priority: P3)

**Goal**: Display clear error messages when issues occur so users understand what happened

**Independent Test**: Simulate network failure, invalid JWT, backend error - verify appropriate user-friendly error messages appear

### Implementation for User Story 4

- [X] T031 [US4] Configure ChatKit error handling (customize ChatKit error display to show user-friendly messages)
- [X] T032 [US4] Add custom error display wrapper in ChatInterface (conditional render error banner at top when ChatKit reports errors)
- [X] T033 [US4] Implement authentication error handling (detect 401 errors from ChatKit, redirect to login page using Next.js router)
- [X] T034 [US4] Configure ChatKit validation (ensure ChatKit prevents sending empty messages)
- [X] T035 [US4] Add network error detection (configure ChatKit to show "Unable to connect" message for network errors)
- [X] T036 [US4] Customize ChatKit error messages (replace technical error messages with user-friendly versions)
- [X] T037 [US4] Add error recovery actions (implement retry functionality for retryable errors)
- [X] T038 [US4] Test error scenarios (verify all error types display appropriate messages via ChatKit)

**Checkpoint**: All user stories should now be independently functional with comprehensive error handling via ChatKit

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [X] T039 [P] Customize ChatKit theme for responsive design (configure ChatKit responsive breakpoints for tablet and mobile)
- [X] T040 [P] Configure ChatKit mobile optimizations (full-screen modal on <640px, adjust ChatKit component sizing)
- [X] T041 [P] Optimize ChatKit performance (configure ChatKit virtual scrolling for long conversations if needed)
- [X] T042 [P] Add hover states for custom wrapper elements (floating icon, close/minimize buttons)
- [X] T043 [P] Add focus states for accessibility (keyboard navigation support for custom wrapper, ensure ChatKit accessibility features enabled)
- [X] T044 [P] Add ARIA labels for custom wrapper components (aria-label on launcher button, close/minimize buttons)
- [X] T045 Verify z-index hierarchy across all pages (test floating icon and ChatKit interface on dashboard, tasks, settings pages)
- [X] T046 Configure ChatKit timestamp formatting (customize how ChatKit displays message timestamps)
- [X] T047 Test ChatKit with 50+ messages (verify ChatKit performance with long conversations)
- [X] T048 Validate against quickstart.md checklist (run through all testing scenarios in quickstart.md)
- [X] T049 Browser compatibility testing (test ChatKit on Chrome 90+, Firefox 88+, Safari 14+, Edge 90+, iOS Safari 14+, Android Chrome 90+)
- [X] T050 Update frontend CLAUDE.md with ChatKit integration patterns (document ChatKit-specific rules and patterns)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P2 → P3)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 but independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Wraps US1+US2 with floating launcher but independently testable
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Adds error handling to ChatKit but independently testable

### Within Each User Story

- ChatKit configuration must be complete before using ChatKit components
- Custom wrapper components can be built in parallel with ChatKit integration
- Integration tasks depend on both ChatKit and wrapper components being complete

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- ChatKit configuration tasks in Foundational can run in parallel after installation
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Custom wrapper components marked [P] can run in parallel (FloatingChatLauncher + ChatHeader for US3)
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# After ChatKit is configured, integrate components:
Task: "Create ChatInterface wrapper component"
Task: "Integrate ChatKit message display components"
Task: "Integrate ChatKit input component"

# Then customize:
Task: "Configure ChatKit message styling"
Task: "Test message sending and receiving"
```

---

## Parallel Example: User Story 3

```bash
# Launch wrapper component creation in parallel:
Task: "Create FloatingChatLauncher component"
Task: "Create ChatHeader component"

# Then integration tasks:
Task: "Update ChatInterface to include ChatHeader"
Task: "Integrate FloatingChatLauncher in root layout"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004) - Install ChatKit
2. Complete Phase 2: Foundational (T005-T009) - Configure ChatKit with JWT and API endpoint - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T010-T015) - Basic ChatKit integration
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Log in, send message "Add a task to buy groceries"
   - Verify assistant response appears via ChatKit
   - Verify visual distinction between user and assistant messages
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → ChatKit configured and ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (conversation history via ChatKit)
4. Add User Story 3 → Test independently → Deploy/Demo (floating launcher with ChatKit)
5. Add User Story 4 → Test independently → Deploy/Demo (error handling)
6. Add Polish → Final validation → Production deploy
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T009)
2. Once Foundational is done:
   - Developer A: User Story 1 (T010-T015) - Basic ChatKit integration
   - Developer B: User Story 2 (T016-T020) - ChatKit history features
   - Developer C: User Story 3 (T021-T030) - Floating launcher wrapper
   - Developer D: User Story 4 (T031-T038) - ChatKit error handling
3. Stories complete and integrate independently
4. Team completes Polish together (T039-T050)

---

## Task Summary

**Total Tasks**: 50

**Tasks per Phase**:
- Phase 1 (Setup): 4 tasks (install ChatKit, configure environment)
- Phase 2 (Foundational): 5 tasks (configure ChatKit with JWT and API) - BLOCKING
- Phase 3 (User Story 1 - P1): 6 tasks (basic ChatKit integration)
- Phase 4 (User Story 2 - P2): 5 tasks (ChatKit history features)
- Phase 5 (User Story 3 - P2): 10 tasks (floating launcher wrapper)
- Phase 6 (User Story 4 - P3): 8 tasks (ChatKit error handling)
- Phase 7 (Polish): 12 tasks (ChatKit customization and validation)

**Parallel Opportunities**: 16 tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**:
- US1: Send message via ChatKit, receive response with visual distinction
- US2: Refresh page, ChatKit loads conversation history
- US3: Navigate pages, floating icon appears with ChatKit inside
- US4: Simulate errors, ChatKit displays user-friendly messages

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = 15 tasks

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Using OpenAI ChatKit as specified in requirements
- ChatKit handles message state, custom code handles floating launcher UI state
- JWT automatically configured in ChatKit via Phase 2 Foundational tasks
- TypeScript strict mode enforced throughout
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
