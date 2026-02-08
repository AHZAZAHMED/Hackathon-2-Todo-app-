# Tasks: Chatbot Frontend UI Fixes + Playwright Validation

**Input**: Design documents from `/specs/005-chatbot-ui-fixes/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/playwright-validation.md, quickstart.md

**Tests**: Playwright validation tests are REQUIRED per specification (10 automated tests)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/` (Next.js 16+ App Router)
- **Components**: `frontend/components/chat/`
- **Styles**: `frontend/app/globals.css`
- **Tests**: `tests/playwright/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Playwright setup

- [ ] T001 Verify Next.js development server runs on http://localhost:3000
- [ ] T002 Verify existing ChatKit integration is functional
- [ ] T003 [P] Install Playwright dependencies: `npm install -D @playwright/test`
- [ ] T004 [P] Install Playwright browsers: `npx playwright install`
- [ ] T005 [P] Create Playwright config in tests/playwright/playwright.config.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core CSS infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Add z-index custom properties to frontend/app/globals.css (--z-50: 50, --z-60: 60)
- [ ] T007 [P] Add transition animations to frontend/app/globals.css (slideUp keyframe, 300ms duration)
- [ ] T008 [P] Verify ChatUIContext exports openChat, closeChat, toggleChat, minimizeChat functions

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Fix Chat Window Sizing and Positioning (Priority: P1) 🎯 MVP

**Goal**: Chat window opens at constrained size (max 420px width, max 70vh height) with proper 24px bottom margin

**Independent Test**: Open chat by clicking icon. Window should appear at bottom-right with width ≤ 420px, height ≤ 70vh, and 24px margin from bottom edge.

### Implementation for User Story 1

- [ ] T009 [US1] Update ChatInterface container in frontend/components/chat/ChatInterface.tsx with size constraints (max-w-[420px], max-h-[70vh])
- [ ] T010 [US1] Add positioning classes to ChatInterface: fixed bottom-6 right-6 for desktop
- [ ] T011 [US1] Add overflow-hidden to ChatInterface container to prevent content overflow
- [ ] T012 [US1] Add rounded-xl and shadow-2xl classes for visual polish
- [ ] T013 [US1] Add z-50 class to ChatInterface container
- [ ] T014 [US1] Add transition-all duration-300 ease-in-out for smooth animations
- [ ] T015 [US1] Add role="dialog" and aria-label="Chat window" for accessibility

**Checkpoint**: At this point, chat window should open at correct size with proper positioning

---

## Phase 4: User Story 2 - Fix Chat Icon Visibility and Z-Index (Priority: P1)

**Goal**: Floating icon remains visible and clickable above chat window at all times

**Independent Test**: Open chat window and verify icon is still visible at bottom-right. Click icon to close chat. Icon should always be accessible.

### Implementation for User Story 2

- [ ] T016 [US2] Update FloatingChatLauncher icon button in frontend/components/chat/FloatingChatLauncher.tsx with z-[60] class
- [ ] T017 [US2] Change icon onClick from openChat to toggleChat for proper toggle behavior
- [ ] T018 [US2] Add aria-label="Open chat" to icon button for accessibility
- [ ] T019 [US2] Add hover:scale-105 transition for better UX
- [ ] T020 [US2] Verify icon uses fixed positioning (fixed bottom-6 right-6)

**Checkpoint**: At this point, icon should remain visible above chat window and toggle chat on click

---

## Phase 5: User Story 3 - Fix Close and Minimize Functionality (Priority: P1)

**Goal**: Close (X) and minimize (-) buttons in chat header work correctly

**Independent Test**: Open chat, click close button - chat closes. Reopen, click minimize button - chat minimizes. Both should leave only the floating icon visible.

### Implementation for User Story 3

- [ ] T021 [US3] Import useChatUI hook in frontend/components/chat/ChatHeader.tsx
- [ ] T022 [US3] Extract closeChat and minimizeChat functions from useChatUI
- [ ] T023 [US3] Connect close button onClick to closeChat function
- [ ] T024 [US3] Connect minimize button onClick to minimizeChat function
- [ ] T025 [US3] Add aria-label="Close chat" to close button
- [ ] T026 [US3] Add aria-label="Minimize chat" to minimize button
- [ ] T027 [US3] Add hover:bg-gray-100 transition to both buttons for visual feedback

**Checkpoint**: At this point, close and minimize buttons should work correctly

---

## Phase 6: User Story 4 - Add Keyboard and Click-Outside Interactions (Priority: P2)

**Goal**: Users can close chat using Escape key or by clicking outside the chat window

**Independent Test**: Open chat, press Escape - chat closes. Reopen chat, click outside window - chat closes. Click inside window - chat stays open.

### Implementation for User Story 4

- [ ] T028 [US4] Add containerRef using useRef<HTMLDivElement>(null) in frontend/components/chat/ChatInterface.tsx
- [ ] T029 [US4] Attach containerRef to ChatInterface container div
- [ ] T030 [US4] Add useEffect hook for Escape key handler with keydown event listener
- [ ] T031 [US4] Implement handleEscape function that calls closeChat when e.key === 'Escape'
- [ ] T032 [US4] Add cleanup function to remove keydown listener on unmount
- [ ] T033 [US4] Add useEffect hook for click-outside handler with mousedown event listener
- [ ] T034 [US4] Implement handleClickOutside function that checks containerRef.contains and calls closeChat
- [ ] T035 [US4] Add cleanup function to remove mousedown listener on unmount
- [ ] T036 [US4] Add closeChat to dependency arrays for both useEffect hooks

**Checkpoint**: At this point, Escape key and click-outside should close chat

---

## Phase 7: User Story 5 - Playwright Automated Validation (Priority: P2)

**Goal**: Automated browser tests verify all chat UI behaviors work correctly

**Independent Test**: Run Playwright test suite. All 10 validation checks should pass.

### Playwright Test Implementation

- [ ] T037 [P] [US5] Create test file tests/playwright/chatbot-ui.spec.ts with test.describe block
- [ ] T038 [P] [US5] Add test.beforeEach hook to navigate to http://localhost:3000/dashboard
- [ ] T039 [P] [US5] Implement Test 1: Icon visible on page load (verify icon at bottom-right)
- [ ] T040 [P] [US5] Implement Test 2: Click icon opens chat (verify size ≤ 420px width, ≤ 70vh height)
- [ ] T041 [P] [US5] Implement Test 3: Chat renders content (verify ChatKit visible, not blank)
- [ ] T042 [P] [US5] Implement Test 4: Icon remains clickable when chat open (verify z-index, click to close)
- [ ] T043 [P] [US5] Implement Test 5: Close button works (click close button, verify chat closes)
- [ ] T044 [P] [US5] Implement Test 6: Escape key closes chat (press Escape, verify chat closes)
- [ ] T045 [P] [US5] Implement Test 7: Click outside closes chat (click at x:10 y:10, verify chat closes)
- [ ] T046 [P] [US5] Implement Test 8: Size constraints respected (measure boundingBox, verify constraints)
- [ ] T047 [P] [US5] Implement Test 9: Mobile viewport behavior (set viewport 375x667, verify full-screen)
- [ ] T048 [P] [US5] Implement Test 10: No console errors (attach console listener, verify zero errors)

**Checkpoint**: All 10 Playwright tests should pass

---

## Phase 8: Responsive Mobile Behavior (Cross-Cutting)

**Purpose**: Ensure chat works correctly on mobile viewports (<640px)

- [ ] T049 Add mobile-first responsive classes to ChatInterface in frontend/components/chat/ChatInterface.tsx
- [ ] T050 Set mobile default: bottom-0 right-0 left-0 top-0 (full-screen)
- [ ] T051 Add desktop overrides: md:bottom-6 md:right-6 md:left-auto md:top-auto
- [ ] T052 Add desktop size constraints: md:w-96 md:max-w-[420px] md:max-h-[70vh]
- [ ] T053 Add desktop border-radius: md:rounded-xl
- [ ] T054 Add desktop shadow: md:shadow-2xl
- [ ] T055 Test on mobile viewport (375x667) - verify full-screen modal
- [ ] T056 Test on desktop viewport (1920x1080) - verify fixed panel

**Checkpoint**: Chat should adapt between mobile full-screen and desktop panel

---

## Phase 9: ChatKit Rendering Fix (Cross-Cutting)

**Purpose**: Ensure ChatKit content renders immediately without blank panels

- [ ] T057 Add token state in frontend/components/chat/ChatInterface.tsx: useState<string | null>(null)
- [ ] T058 Add loading state: useState(true)
- [ ] T059 Add useEffect hook to fetch JWT token from /api/auth/token on mount
- [ ] T060 Store token in state and set loading to false after fetch
- [ ] T061 Add loading state UI: show "Loading chat..." while token is being fetched
- [ ] T062 Configure ChatKit with custom fetch function that adds Authorization header
- [ ] T063 Pass token to ChatKit fetch function: headers.set('Authorization', `Bearer ${token}`)
- [ ] T064 Verify ChatKit mounts only after token is available
- [ ] T065 Test: Open chat, verify ChatKit renders within 500ms (no blank panels)

**Checkpoint**: ChatKit should render immediately with no blank/empty panels

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [ ] T066 [P] Run TypeScript compiler: npm run build (verify no errors)
- [ ] T067 [P] Run ESLint: npm run lint (fix any issues)
- [ ] T068 [P] Test all user stories manually per quickstart.md checklist
- [ ] T069 [P] Run full Playwright test suite: npx playwright test
- [ ] T070 [P] Generate Playwright HTML report: npx playwright show-report
- [ ] T071 Verify all 10 Playwright tests pass (10/10)
- [ ] T072 Capture screenshots of working chat UI (open, closed, mobile, desktop)
- [ ] T073 [P] Update documentation if needed
- [ ] T074 [P] Code cleanup: remove console.logs, unused imports
- [ ] T075 Final validation: Test complete chat flow end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 3 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 4 (P2): Can start after Foundational - No dependencies on other stories
  - User Story 5 (P2): Can start after Foundational - Should run after US1-4 for validation
- **Responsive (Phase 8)**: Can start after User Story 1 (sizing) is complete
- **ChatKit Fix (Phase 9)**: Can start after Foundational - Independent of other stories
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P2)**: Should run after US1-4 for validation, but can be written in parallel

### Within Each User Story

- User Story 1: All tasks modify same file (ChatInterface.tsx) - must be sequential
- User Story 2: All tasks modify same file (FloatingChatLauncher.tsx) - must be sequential
- User Story 3: All tasks modify same file (ChatHeader.tsx) - must be sequential
- User Story 4: All tasks modify same file (ChatInterface.tsx) - must be sequential after US1
- User Story 5: All Playwright tests marked [P] can run in parallel

### Parallel Opportunities

- Phase 1: T003, T004, T005 can run in parallel (different operations)
- Phase 2: T007, T008 can run in parallel (different files)
- Phase 3-7: User Stories 1, 2, 3 can be worked on in parallel (different files)
- Phase 7: All Playwright tests (T039-T048) can run in parallel
- Phase 10: T066, T067, T068, T069, T070, T073, T074 can run in parallel

---

## Parallel Example: User Story 5 (Playwright Tests)

```bash
# Launch all Playwright tests together:
Task: "Implement Test 1: Icon visible on page load"
Task: "Implement Test 2: Click icon opens chat"
Task: "Implement Test 3: Chat renders content"
Task: "Implement Test 4: Icon remains clickable"
Task: "Implement Test 5: Close button works"
Task: "Implement Test 6: Escape key closes chat"
Task: "Implement Test 7: Click outside closes chat"
Task: "Implement Test 8: Size constraints respected"
Task: "Implement Test 9: Mobile viewport behavior"
Task: "Implement Test 10: No console errors"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Sizing)
4. Complete Phase 4: User Story 2 (Z-Index)
5. Complete Phase 5: User Story 3 (Close/Minimize)
6. **STOP and VALIDATE**: Test critical fixes manually
7. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Critical fix 1 complete
3. Add User Story 2 → Test independently → Critical fix 2 complete
4. Add User Story 3 → Test independently → Critical fix 3 complete (MVP!)
5. Add User Story 4 → Test independently → Enhancement 1 complete
6. Add User Story 5 → Test independently → Validation complete
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (ChatInterface sizing)
   - Developer B: User Story 2 (FloatingChatLauncher z-index)
   - Developer C: User Story 3 (ChatHeader buttons)
3. Then:
   - Developer A: User Story 4 (Event handlers in ChatInterface)
   - Developer B: User Story 5 (Playwright tests)
   - Developer C: Phase 8 (Responsive) + Phase 9 (ChatKit fix)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- User Stories 1-3 are P1 (critical) - must complete for MVP
- User Stories 4-5 are P2 (enhancements) - can defer if needed
- Playwright tests validate all fixes - 10/10 must pass
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Frontend-only scope - no backend, agent, MCP, or database changes
- Avoid: modifying Phase-2 code, adding new features beyond spec

---

## Task Summary

**Total Tasks**: 75
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 3 tasks
- Phase 3 (US1 - Sizing): 7 tasks
- Phase 4 (US2 - Z-Index): 5 tasks
- Phase 5 (US3 - Close/Minimize): 7 tasks
- Phase 6 (US4 - Keyboard/Click-Outside): 9 tasks
- Phase 7 (US5 - Playwright): 12 tasks
- Phase 8 (Responsive): 8 tasks
- Phase 9 (ChatKit Fix): 9 tasks
- Phase 10 (Polish): 10 tasks

**Parallel Opportunities**: 25 tasks marked [P]

**MVP Scope**: Phases 1-5 (User Stories 1-3) = 27 tasks

**Independent Test Criteria**:
- US1: Chat opens at correct size with proper positioning
- US2: Icon remains visible and clickable above window
- US3: Close and minimize buttons work correctly
- US4: Escape key and click-outside close chat
- US5: All 10 Playwright tests pass
