---

description: "Task list for Frontend Web Application implementation"
---

# Tasks: Frontend Web Application

**Input**: Design documents from `/specs/001-frontend-web-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, contracts/api-client.md

**Tests**: Tests are NOT included in this task list as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/` at repository root
- All paths relative to `frontend/` directory

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create `frontend/` directory in repository root
- [ ] T002 Initialize Next.js 16+ application with TypeScript using `npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*"`
- [ ] T003 Configure TypeScript strict mode in frontend/tsconfig.json
- [ ] T004 Configure Tailwind CSS custom theme in frontend/tailwind.config.js
- [ ] T005 [P] Create folder structure: frontend/components/{layout,landing,auth,dashboard,tasks,ui}
- [ ] T006 [P] Create folder structure: frontend/lib, frontend/hooks, frontend/types, frontend/public/images, frontend/styles
- [ ] T007 [P] Create frontend/CLAUDE.md with frontend-specific rules
- [ ] T008 [P] Create frontend/.env.example with NEXT_PUBLIC_API_URL and NEXT_PUBLIC_APP_NAME
- [ ] T009 Configure next.config.js for production settings in frontend/next.config.js
- [ ] T010 Verify `npm install` succeeds and `npm run dev` starts development server

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T011 [P] Create Task entity types in frontend/types/task.ts (Task, CreateTaskInput, UpdateTaskInput)
- [ ] T012 [P] Create User entity types in frontend/types/user.ts (User, SignupInput, LoginInput)
- [ ] T013 [P] Create Auth types in frontend/types/auth.ts (AuthState, AuthResponse)
- [ ] T014 [P] Create API response types in frontend/types/api.ts (ApiResponse, ApiError, PaginatedResponse)
- [ ] T015 [P] Create Button component in frontend/components/ui/Button.tsx
- [ ] T016 [P] Create Input component in frontend/components/ui/Input.tsx
- [ ] T017 [P] Create Card component in frontend/components/ui/Card.tsx
- [ ] T018 [P] Create Modal component in frontend/components/ui/Modal.tsx with portal rendering
- [ ] T019 [P] Create utility functions in frontend/lib/utils.ts
- [ ] T020 Create global styles in frontend/styles/globals.css with Tailwind directives

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Discover Product via Landing Page (Priority: P1) 🎯 MVP

**Goal**: Create marketing landing page with navigation, hero section, features showcase, and footer

**Independent Test**: Navigate to http://localhost:3000 and verify landing page renders with all sections, navigation works, and layout is responsive

### Implementation for User Story 1

- [ ] T021 [P] [US1] Create root layout in frontend/app/layout.tsx with global styles and metadata
- [ ] T022 [P] [US1] Create Navbar component in frontend/components/layout/Navbar.tsx with responsive navigation using next/link
- [ ] T023 [P] [US1] Create Footer component in frontend/components/layout/Footer.tsx
- [ ] T024 [US1] Create landing page in frontend/app/page.tsx
- [ ] T025 [P] [US1] Create Hero component in frontend/components/landing/Hero.tsx with tagline and CTA button
- [ ] T026 [P] [US1] Create Features component in frontend/components/landing/Features.tsx showcasing 4 features
- [ ] T027 [US1] Add responsive mobile menu to Navbar component
- [ ] T028 [US1] Style all US1 components with Tailwind CSS for responsive design (320px-1920px)
- [ ] T029 [US1] Verify navigation links use Link component (not <a> tags)
- [ ] T030 [US1] Test landing page on mobile (375px), tablet (768px), and desktop (1280px)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Access Authentication Pages and Maintain Session (Priority: P2)

**Goal**: Create login and signup pages with forms, validation, and session persistence preparation

**Independent Test**: Navigate to /login and /signup, verify forms render correctly, validation works, and navigation between pages functions

### Implementation for User Story 2

- [ ] T031 [P] [US2] Create login page in frontend/app/login/page.tsx
- [ ] T032 [P] [US2] Create signup page in frontend/app/signup/page.tsx
- [ ] T033 [P] [US2] Create LoginForm component (Client Component) in frontend/components/auth/LoginForm.tsx with email and password fields
- [ ] T034 [P] [US2] Create SignupForm component (Client Component) in frontend/components/auth/SignupForm.tsx with name, email, and password fields
- [ ] T035 [US2] Implement form validation in LoginForm (required fields, email format)
- [ ] T036 [US2] Implement form validation in SignupForm (required fields, email format, password strength)
- [ ] T037 [US2] Add navigation links between login and signup pages using Link component
- [ ] T038 [US2] Style authentication forms with Tailwind CSS
- [ ] T039 [US2] Add keyboard accessibility to forms (tab navigation, enter to submit)
- [ ] T040 [US2] Display validation error messages inline below form fields
- [ ] T041 [US2] Test forms on mobile, tablet, and desktop layouts

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - View Dashboard with Task Statistics and Profile Access (Priority: P3)

**Goal**: Create authenticated dashboard with task statistics cards, task list, and profile dropdown with logout

**Independent Test**: Navigate to /dashboard and verify statistics cards render, task list displays, profile button appears in top-right corner, and dropdown shows logout option

### Implementation for User Story 3

- [ ] T042 [US3] Create dashboard page in frontend/app/dashboard/page.tsx
- [ ] T043 [P] [US3] Create StatsCards component in frontend/components/dashboard/StatsCards.tsx displaying total, completed, and pending tasks
- [ ] T044 [P] [US3] Create TaskList component in frontend/components/dashboard/TaskList.tsx
- [ ] T045 [P] [US3] Create TaskItem component in frontend/components/dashboard/TaskItem.tsx with title, status, update/delete buttons, and completion toggle
- [ ] T046 [US3] Create ProfileDropdown component (Client Component) in frontend/components/layout/ProfileDropdown.tsx
- [ ] T047 [US3] Implement profile button in top-right corner of Navbar (update Navbar component)
- [ ] T048 [US3] Implement dropdown menu with user info and logout option in ProfileDropdown
- [ ] T049 [US3] Add dropdown close logic (click outside, Escape key)
- [ ] T050 [US3] Style dashboard components with Tailwind CSS
- [ ] T051 [US3] Implement responsive layout for dashboard (mobile, tablet, desktop)
- [ ] T052 [US3] Add empty state message for task list when no tasks exist
- [ ] T053 [US3] Test dashboard on mobile, tablet, and desktop layouts

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Manage Tasks (Priority: P4)

**Goal**: Create task CRUD functionality with modal overlays for creation and editing

**Independent Test**: Click "Add Task" button to open modal, create task, edit task, delete task, and toggle completion status

### Implementation for User Story 4

- [ ] T054 [P] [US4] Create AddTaskModal component (Client Component) in frontend/components/tasks/AddTaskModal.tsx with title and description fields
- [ ] T055 [P] [US4] Create EditTaskModal component (Client Component) in frontend/components/tasks/EditTaskModal.tsx with title and description fields
- [ ] T056 [US4] Implement modal open/close logic in AddTaskModal
- [ ] T057 [US4] Implement modal open/close logic in EditTaskModal
- [ ] T058 [US4] Add "Add Task" button to dashboard that opens AddTaskModal
- [ ] T059 [US4] Implement Save button in AddTaskModal (closes modal, adds task to list)
- [ ] T060 [US4] Implement Cancel button in AddTaskModal (closes modal without saving)
- [ ] T061 [US4] Implement Save button in EditTaskModal (closes modal, updates task)
- [ ] T062 [US4] Implement Cancel button in EditTaskModal (closes modal without saving)
- [ ] T063 [US4] Add Update button to TaskItem that opens EditTaskModal with task data
- [ ] T064 [US4] Add Delete button to TaskItem with confirmation
- [ ] T065 [US4] Implement completion toggle in TaskItem (updates task status visually)
- [ ] T066 [US4] Add form validation to AddTaskModal (title required, max lengths)
- [ ] T067 [US4] Add form validation to EditTaskModal (title required, max lengths)
- [ ] T068 [US4] Implement modal close on outside click
- [ ] T069 [US4] Implement modal close on Escape key press
- [ ] T070 [US4] Style modals with Tailwind CSS (semi-transparent overlay, centered card)
- [ ] T071 [US4] Test task management on mobile, tablet, and desktop layouts

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: API Client & Integration Preparation (Cross-Cutting)

**Purpose**: Create centralized API client and custom hooks for backend integration

- [ ] T072 [P] Create API client class in frontend/lib/api-client.ts with fetch wrapper
- [ ] T073 [P] Implement setToken method in API client for JWT attachment
- [ ] T074 [P] Implement request method in API client with error handling
- [ ] T075 [P] Define signup endpoint function in API client
- [ ] T076 [P] Define login endpoint function in API client
- [ ] T077 [P] Define logout endpoint function in API client
- [ ] T078 [P] Define getCurrentUser endpoint function in API client
- [ ] T079 [P] Define getTasks endpoint function in API client
- [ ] T080 [P] Define createTask endpoint function in API client
- [ ] T081 [P] Define updateTask endpoint function in API client
- [ ] T082 [P] Define deleteTask endpoint function in API client
- [ ] T083 [P] Create ApiError class in API client for error handling
- [ ] T084 [P] Create useAuth custom hook in frontend/hooks/useAuth.ts for authentication state management
- [ ] T085 [P] Create useTasks custom hook in frontend/hooks/useTasks.ts for task management
- [ ] T086 [P] Create useModal custom hook in frontend/hooks/useModal.ts for modal state management
- [ ] T087 Export apiClient singleton instance from frontend/lib/api-client.ts
- [ ] T088 Verify API client compiles without TypeScript errors
- [ ] T089 Verify all endpoint functions have proper TypeScript types

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation across all user stories

- [ ] T090 [P] Verify all navigation uses Link component (no <a> tags) across all pages
- [ ] T091 [P] Add loading states for page transitions
- [ ] T092 [P] Test keyboard navigation across all pages (Tab, Enter, Escape)
- [ ] T093 [P] Verify focus states visible on all interactive elements
- [ ] T094 [P] Test responsive design at 320px (mobile), 768px (tablet), 1920px (desktop)
- [ ] T095 [P] Verify color contrast meets WCAG 2.1 AA standards
- [ ] T096 [P] Run `npm run build` and verify successful production build
- [ ] T097 [P] Run `npm run lint` and fix any ESLint errors
- [ ] T098 [P] Verify TypeScript compilation with strict mode (no errors)
- [ ] T099 [P] Check for console errors in browser across all pages
- [ ] T100 Create frontend/README.md with setup instructions and architecture overview

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **API Client (Phase 7)**: Can proceed in parallel with user stories (different files)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (uses Navbar from US1 but can work independently)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories (uses Navbar from US1 but can work independently)
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Integrates with US3 dashboard but independently testable

### Within Each User Story

- Components marked [P] can be created in parallel (different files)
- Integration tasks must wait for component creation
- Styling and testing tasks come after component implementation

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T005-T008)
- All Foundational tasks marked [P] can run in parallel (T011-T019)
- Within User Story 1: T021-T023, T025-T026 can run in parallel
- Within User Story 2: T031-T034 can run in parallel
- Within User Story 3: T043-T045 can run in parallel
- Within User Story 4: T054-T055 can run in parallel
- All API Client endpoint functions (T075-T082) can run in parallel
- All custom hooks (T084-T086) can run in parallel
- All Polish tasks (T090-T099) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all parallel components for User Story 1 together:
Task T021: "Create root layout in frontend/app/layout.tsx"
Task T022: "Create Navbar component in frontend/components/layout/Navbar.tsx"
Task T023: "Create Footer component in frontend/components/layout/Footer.tsx"
Task T025: "Create Hero component in frontend/components/landing/Hero.tsx"
Task T026: "Create Features component in frontend/components/landing/Features.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Landing Page)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Run `implementation-validator-playwright` skill to validate
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Validate with Playwright → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Validate with Playwright → Deploy/Demo
4. Add User Story 3 → Test independently → Validate with Playwright → Deploy/Demo
5. Add User Story 4 → Test independently → Validate with Playwright → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Landing Page)
   - Developer B: User Story 2 (Auth Pages)
   - Developer C: User Story 3 (Dashboard)
   - Developer D: API Client (Phase 7)
3. Stories complete and integrate independently
4. User Story 4 can be added by any developer after their story completes

---

## Validation Checklist

### After Each User Story

- [ ] Story renders without console errors
- [ ] All navigation uses Link component
- [ ] Forms are keyboard accessible
- [ ] Layout responsive on mobile/tablet/desktop
- [ ] TypeScript compiles without errors
- [ ] No mock data in components

### After All Stories Complete

- [ ] `npm run dev` succeeds
- [ ] `npm run build` succeeds
- [ ] `npm run lint` passes
- [ ] All pages accessible via navigation
- [ ] Profile dropdown works
- [ ] Modals open and close correctly
- [ ] Responsive design verified at 320px, 768px, 1920px
- [ ] Keyboard navigation works throughout
- [ ] Color contrast meets WCAG 2.1 AA
- [ ] No TypeScript errors with strict mode
- [ ] Centralized API client in place
- [ ] Ready for authentication feature integration

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Tests not included as not explicitly requested in specification
- Session persistence implementation deferred to authentication feature spec
- Backend API integration deferred to backend feature spec
- All modern Next.js patterns used (Link component, App Router, Server Components)

---

## Total Task Count

- **Setup**: 10 tasks (T001-T010)
- **Foundational**: 10 tasks (T011-T020)
- **User Story 1**: 10 tasks (T021-T030)
- **User Story 2**: 11 tasks (T031-T041)
- **User Story 3**: 12 tasks (T042-T053)
- **User Story 4**: 18 tasks (T054-T071)
- **API Client**: 18 tasks (T072-T089)
- **Polish**: 11 tasks (T090-T100)

**Total**: 100 tasks

**Parallel Opportunities**: 45 tasks marked [P] can run in parallel within their phases

**MVP Scope**: Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (User Story 1) = 30 tasks
