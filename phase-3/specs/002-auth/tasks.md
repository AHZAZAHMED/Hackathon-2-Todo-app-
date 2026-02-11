# Tasks: Authentication System (Better Auth + JWT)

**Input**: Design documents from `/specs/002-auth/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are NOT included in this task list. Validation will be performed using implementation-validator-playwright and integration-testing-engineer skills after implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/`, `frontend/`
- Frontend paths: `frontend/app/`, `frontend/lib/`, `frontend/components/`
- Backend paths: `backend/app/`, `backend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment configuration

- [ ] T001 Generate BETTER_AUTH_SECRET using cryptographically secure method (32+ characters)
- [ ] T002 Create frontend/.env.example with BETTER_AUTH_SECRET, BETTER_AUTH_URL, DATABASE_URL, NEXT_PUBLIC_API_URL placeholders
- [ ] T003 [P] Create backend/.env.example with BETTER_AUTH_SECRET, DATABASE_URL, FRONTEND_URL, HOST, PORT placeholders
- [ ] T004 [P] Create backend/requirements.txt with fastapi, uvicorn, pyjwt, python-jose, passlib, sqlmodel, psycopg2-binary, python-dotenv
- [ ] T005 Verify PostgreSQL database connection (Neon Serverless or local)
- [ ] T006 Create users table in database with schema from data-model.md (id, name, email, password, created_at, updated_at)
- [ ] T007 [P] Create rate_limits table in database with schema from data-model.md (id, email, failed_attempts, last_attempt, locked_until, created_at)
- [ ] T008 [P] Add indexes: unique index on users.email (lowercase), index on rate_limits.email, index on rate_limits.locked_until

**Checkpoint**: Database schema ready, environment templates created

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core authentication infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Frontend Foundation

- [ ] T009 Install better-auth package in frontend/package.json
- [ ] T010 Create frontend/lib/auth.ts with Better Auth configuration (database provider, emailAndPassword plugin, JWT session config, httpOnly cookies)
- [ ] T011 Configure JWT plugin in frontend/lib/auth.ts with custom claims (user_id, email, name, exp, iat)
- [ ] T012 Create frontend/app/api/auth/[...all]/route.ts with Better Auth API route handlers (GET, POST)
- [ ] T013 Update frontend/lib/api-client.ts to extract JWT from Better Auth session and attach to Authorization header
- [ ] T014 Add 401 error handler to frontend/lib/api-client.ts (store original URL in sessionStorage, redirect to login with query param)
- [ ] T015 [P] Add 429 error handler to frontend/lib/api-client.ts (display rate limit error with retry time)
- [ ] T016 Create frontend/middleware.ts for route protection (check Better Auth session, redirect unauthenticated users to login)
- [ ] T017 Configure middleware matcher in frontend/middleware.ts for /dashboard and /tasks routes

### Backend Foundation

- [ ] T018 Create backend/app/ directory structure (__init__.py, main.py, config.py)
- [ ] T019 Create backend/app/auth/ directory with __init__.py, middleware.py, dependencies.py, utils.py
- [ ] T020 Create backend/app/models/ directory with __init__.py, user.py, rate_limit.py
- [ ] T021 Create backend/app/routes/ directory with __init__.py
- [ ] T022 Implement backend/app/config.py to load environment variables (BETTER_AUTH_SECRET, DATABASE_URL, FRONTEND_URL)
- [ ] T023 Validate BETTER_AUTH_SECRET is set in backend/app/config.py (raise error if missing)
- [ ] T024 Create backend/app/database.py with PostgreSQL connection using DATABASE_URL
- [ ] T025 Implement backend/app/models/user.py with SQLModel User schema (id, name, email, password, created_at, updated_at)
- [ ] T026 [P] Implement backend/app/models/rate_limit.py with SQLModel RateLimit schema (id, email, failed_attempts, last_attempt, locked_until, created_at)
- [ ] T027 Implement JWT verification in backend/app/auth/utils.py (decode token, verify signature with BETTER_AUTH_SECRET, validate exp/iat)
- [ ] T028 Implement backend/app/auth/middleware.py with HTTPBearer security scheme and verify_jwt function
- [ ] T029 Extract user claims (user_id, email, name) in backend/app/auth/middleware.py and return as dict
- [ ] T030 Add error responses in backend/app/auth/middleware.py (401 for invalid/expired/missing tokens with error codes)
- [ ] T031 Create backend/app/auth/dependencies.py with get_current_user FastAPI dependency
- [ ] T032 Implement backend/app/main.py with FastAPI app initialization
- [ ] T033 Configure CORS in backend/app/main.py (allow_origins=[FRONTEND_URL], allow_credentials=True, allow_methods, allow_headers)
- [ ] T034 Add health check endpoint GET / in backend/app/main.py (returns {"status": "ok"})
- [ ] T035 Add example protected endpoint GET /api/protected in backend/app/main.py using get_current_user dependency

**Checkpoint**: Foundation ready - Better Auth configured, JWT verification working, user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration (Priority: P1) 🎯 MVP

**Goal**: Enable new users to create accounts with name, email, and password. System validates input, creates user record, issues JWT token, and automatically logs them in.

**Independent Test**: Navigate to signup page, submit valid registration details, verify JWT token issued and user redirected to dashboard.

### Implementation for User Story 1

- [ ] T036 [P] [US1] Update frontend/app/signup/page.tsx to use Better Auth signup API (auth.signUp.email)
- [ ] T037 [P] [US1] Update frontend/components/auth/SignupForm.tsx to call Better Auth signup with name, email, password
- [ ] T038 [US1] Add client-side validation to frontend/components/auth/SignupForm.tsx (email format RFC 5322, password min 8 chars, required fields)
- [ ] T039 [US1] Display inline validation errors in frontend/components/auth/SignupForm.tsx for invalid inputs
- [ ] T040 [US1] Handle signup errors in frontend/components/auth/SignupForm.tsx (EMAIL_ALREADY_EXISTS, VALIDATION_ERROR)
- [ ] T041 [US1] Display user-friendly error messages in frontend/components/auth/SignupForm.tsx ("Email already registered", "Please enter valid email")
- [ ] T042 [US1] Redirect to /dashboard after successful signup in frontend/app/signup/page.tsx
- [ ] T043 [US1] Verify JWT token stored in httpOnly cookie after signup (check browser DevTools)
- [ ] T044 [US1] Verify JWT token includes required claims (user_id, email, name, exp, iat) using jwt.io decoder

**Checkpoint**: User Story 1 complete - Users can register accounts, JWT tokens issued, validation working

**Acceptance Validation**:
- ✅ Valid signup creates account and issues JWT token
- ✅ Duplicate email shows "Email already registered" error
- ✅ Invalid email format shows validation error
- ✅ Short password shows "Password must be at least 8 characters" error
- ✅ Empty fields show validation errors
- ✅ JWT stored in httpOnly cookie with correct claims

---

## Phase 4: User Story 2 - User Login (Priority: P2)

**Goal**: Enable existing users to log in with email and password. System validates credentials, issues JWT token, and grants access to protected routes.

**Independent Test**: Navigate to login page, submit valid credentials, verify JWT token issued and user gains access to protected routes.

### Implementation for User Story 2

- [ ] T045 [P] [US2] Update frontend/app/login/page.tsx to use Better Auth login API (auth.signIn.email)
- [ ] T046 [P] [US2] Update frontend/components/auth/LoginForm.tsx to call Better Auth login with email, password
- [ ] T047 [US2] Add client-side validation to frontend/components/auth/LoginForm.tsx (required fields)
- [ ] T048 [US2] Handle login errors in frontend/components/auth/LoginForm.tsx (INVALID_CREDENTIALS, RATE_LIMIT_EXCEEDED)
- [ ] T049 [US2] Display user-friendly error messages in frontend/components/auth/LoginForm.tsx ("Invalid email or password", "Too many failed attempts")
- [ ] T050 [US2] Implement rate limiting logic in backend (track failed attempts in rate_limits table)
- [ ] T051 [US2] Check rate limit before password verification in backend (if locked_until > NOW, return 429)
- [ ] T052 [US2] Increment failed_attempts in rate_limits table on incorrect password
- [ ] T053 [US2] Set locked_until = NOW() + 15 minutes after 5 failed attempts
- [ ] T054 [US2] Delete rate_limits record on successful login
- [ ] T055 [US2] Return 429 with retry time when rate limit exceeded
- [ ] T056 [US2] Redirect to /dashboard after successful login in frontend/app/login/page.tsx
- [ ] T057 [US2] Handle redirect query parameter in frontend/app/login/page.tsx (redirect to original URL after login)
- [ ] T058 [US2] Verify JWT token automatically included in Authorization header for API requests

**Checkpoint**: User Story 2 complete - Users can login, rate limiting enforced, JWT attached to requests

**Acceptance Validation**:
- ✅ Valid login issues JWT and redirects to dashboard
- ✅ Incorrect password shows "Invalid email or password" error
- ✅ Non-existent email shows "Invalid email or password" error
- ✅ Empty fields show validation errors
- ✅ JWT stored in httpOnly cookie
- ✅ JWT automatically included in Authorization header
- ✅ 5 failed attempts trigger rate limit with 429 error

---

## Phase 5: User Story 3 - Protected Route Access (Priority: P3)

**Goal**: Ensure authenticated users can access protected routes with JWT automatically attached to API requests. Unauthenticated users are redirected to login.

**Independent Test**: Attempt to access protected routes with and without authentication, verify JWT tokens automatically attached to API requests.

### Implementation for User Story 3

- [ ] T059 [P] [US3] Update frontend/app/dashboard/page.tsx to check authentication state using Better Auth session
- [ ] T060 [P] [US3] Display personalized dashboard content for authenticated users in frontend/app/dashboard/page.tsx
- [ ] T061 [US3] Test unauthenticated access to /dashboard (verify redirect to /login via middleware)
- [ ] T062 [US3] Test authenticated access to /dashboard (verify content displayed)
- [ ] T063 [US3] Verify JWT token automatically included in Authorization header for all API requests (check Network tab)
- [ ] T064 [US3] Test expired token scenario (manually expire token, verify 401 error and redirect to login)
- [ ] T065 [US3] Test invalid token scenario (manually corrupt token, verify 401 error and redirect to login)
- [ ] T066 [US3] Verify backend extracts user_id from JWT in backend/app/auth/dependencies.py
- [ ] T067 [US3] Create example endpoint that uses user_id for database query (e.g., GET /api/user/profile)
- [ ] T068 [US3] Verify user_id used for all database queries (never trust client-provided user_id)

**Checkpoint**: User Story 3 complete - Protected routes enforce authentication, JWT flow working end-to-end

**Acceptance Validation**:
- ✅ Authenticated users see personalized dashboard
- ✅ Unauthenticated users redirected to login
- ✅ JWT automatically included in API requests
- ✅ Expired token triggers 401 and redirect to login
- ✅ Invalid token triggers 401 and redirect to login
- ✅ Backend extracts user_id from JWT for queries

---

## Phase 6: User Story 4 - Session Persistence (Priority: P4)

**Goal**: Maintain authentication state across page refreshes and browser sessions. Users remain logged in without re-entering credentials.

**Independent Test**: Login, close browser, reopen, verify user remains authenticated within token expiration period.

### Implementation for User Story 4

- [ ] T069 [US4] Test page refresh while authenticated (verify user remains logged in)
- [ ] T070 [US4] Test browser close/reopen within 24 hours (verify user remains logged in)
- [ ] T071 [US4] Test browser close/reopen after 24 hours (verify user redirected to login)
- [ ] T072 [US4] Test direct URL navigation to protected route (verify authenticated users see content)
- [ ] T073 [US4] Verify Better Auth session restored on page load (check auth.api.getSession in frontend)
- [ ] T074 [US4] Verify JWT token persists in httpOnly cookie across page refreshes
- [ ] T075 [US4] Test session restoration after token expiration (verify redirect to login, then back to original URL)

**Checkpoint**: User Story 4 complete - Session persistence working, authentication state maintained

**Acceptance Validation**:
- ✅ Page refresh maintains authentication state
- ✅ Browser close/reopen maintains authentication (within 24 hours)
- ✅ Token expiration redirects to login
- ✅ Direct URL navigation works for authenticated users

---

## Phase 7: User Story 5 - User Logout (Priority: P5)

**Goal**: Allow authenticated users to explicitly end their session. System clears JWT token and redirects to landing page.

**Independent Test**: Login, click logout, verify JWT token cleared and user redirected to landing page.

### Implementation for User Story 5

- [ ] T076 [P] [US5] Update frontend/components/layout/ProfileDropdown.tsx to call Better Auth logout (auth.signOut)
- [ ] T077 [US5] Clear JWT token from httpOnly cookie on logout
- [ ] T078 [US5] Redirect to landing page (/) after logout in frontend/components/layout/ProfileDropdown.tsx
- [ ] T079 [US5] Test post-logout access to protected routes (verify redirect to login)
- [ ] T080 [US5] Verify no JWT token present in browser storage after logout
- [ ] T081 [US5] Test browser back button after logout (verify redirect to login, not protected content)
- [ ] T082 [US5] Update frontend/hooks/useAuth.tsx to integrate Better Auth logout function

**Checkpoint**: User Story 5 complete - Logout functionality working, JWT cleared, security enforced

**Acceptance Validation**:
- ✅ Logout clears JWT and redirects to landing page
- ✅ Post-logout access to protected routes redirects to login
- ✅ No JWT present in browser storage after logout
- ✅ Browser back button redirects to login (not protected content)

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T083 [P] Remove all mock authentication logic from frontend (search for "mock", "dummy", "fake" in codebase)
- [ ] T084 [P] Update frontend/hooks/useAuth.tsx to remove mock logic and use Better Auth exclusively
- [ ] T085 [P] Verify no hardcoded user IDs in frontend code
- [ ] T086 [P] Verify no client-provided user_id in API requests (only JWT claims)
- [ ] T087 Add logging for authentication events in backend (login success, login failure, rate limit exceeded)
- [ ] T088 [P] Test concurrent sessions (login on device A, login on device B, verify both work)
- [ ] T089 [P] Test network failure during authentication (verify user-friendly error message)
- [ ] T090 [P] Test malformed JWT tokens (verify 401 error and redirect to login)
- [ ] T091 [P] Test browser blocks cookies scenario (verify error message displayed)
- [ ] T092 Verify HTTPS configuration for production (update CORS, cookie secure flag)
- [ ] T093 Create backend/README.md with setup instructions from quickstart.md
- [ ] T094 [P] Update frontend/.env.example with all required variables
- [ ] T095 [P] Update backend/.env.example with all required variables
- [ ] T096 Run quickstart.md validation (follow all setup steps, verify working)
- [ ] T097 Invoke implementation-validator-playwright skill for automated browser-based validation
- [ ] T098 Invoke integration-testing-engineer skill for end-to-end flow validation
- [ ] T099 Verify all success criteria met (SC-001 to SC-010 from spec.md)
- [ ] T100 Create PHR for implementation work

**Checkpoint**: All user stories complete, system validated, ready for production

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
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Functionally builds on US1 (needs users to exist) but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Functionally requires US2 (needs login) but independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Functionally requires US2/US3 (needs sessions) but independently testable
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Functionally requires US2 (needs login) but independently testable

**Note**: While user stories build on each other functionally, the Foundational phase provides all core infrastructure, allowing each story to be tested independently.

### Within Each User Story

- Frontend components before integration
- Backend logic before frontend integration
- Validation before moving to next story
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002-T003, T004, T007-T008)
- Within Foundational phase: Frontend foundation (T009-T017) and Backend foundation (T018-T035) can run in parallel
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within each user story, tasks marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: Foundational Phase

```bash
# Frontend foundation (can run in parallel with backend):
Task T009: "Install better-auth package"
Task T010: "Create frontend/lib/auth.ts"
Task T011: "Configure JWT plugin"
...

# Backend foundation (can run in parallel with frontend):
Task T018: "Create backend/app/ directory structure"
Task T019: "Create backend/app/auth/ directory"
Task T020: "Create backend/app/models/ directory"
...
```

---

## Parallel Example: User Story 1

```bash
# These tasks can run in parallel (different files):
Task T036: "Update frontend/app/signup/page.tsx"
Task T037: "Update frontend/components/auth/SignupForm.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T035) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T036-T044)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

**MVP Deliverable**: Users can register accounts with JWT authentication

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T035)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!) (T036-T044)
3. Add User Story 2 → Test independently → Deploy/Demo (T045-T058)
4. Add User Story 3 → Test independently → Deploy/Demo (T059-T068)
5. Add User Story 4 → Test independently → Deploy/Demo (T069-T075)
6. Add User Story 5 → Test independently → Deploy/Demo (T076-T082)
7. Polish & Validate → Production ready (T083-T100)

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T035)
2. Once Foundational is done:
   - Developer A: User Story 1 (T036-T044)
   - Developer B: User Story 2 (T045-T058)
   - Developer C: User Story 3 (T059-T068)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests are NOT included - validation via implementation-validator-playwright and integration-testing-engineer skills
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Total tasks: 100 (8 Setup, 27 Foundational, 9 US1, 14 US2, 10 US3, 7 US4, 7 US5, 18 Polish)
