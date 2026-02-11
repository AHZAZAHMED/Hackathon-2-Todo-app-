# Implementation Plan: Frontend Web Application

**Branch**: `001-frontend-web-app` | **Date**: 2026-02-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-frontend-web-app/spec.md`

## Summary

Create a professional-grade Next.js 16+ frontend application for the Hackathon II Phase-2 Todo system. The frontend will provide a complete user interface including a marketing landing page, authentication pages (login/signup), and an authenticated dashboard with task management capabilities. The application will use modern Next.js App Router patterns, TypeScript for type safety, and Tailwind CSS for styling. Session persistence will maintain user authentication across page refreshes and browser sessions until explicit logout. A profile button in the top-right corner will provide intuitive access to logout functionality.

**Key Features**:
- Landing page with hero section, features showcase, and navigation
- Authentication pages with form validation and session persistence
- Dashboard with task statistics cards and task list
- Task CRUD operations with modal overlay for creation
- Profile dropdown with logout functionality
- Responsive design (320px-1920px)
- Full keyboard accessibility
- Centralized API client for backend integration

## Technical Context

**Language/Version**: TypeScript 5.x with Next.js 16+
**Primary Dependencies**:
- Next.js 16+ (App Router)
- React 19+
- TypeScript 5.x
- Tailwind CSS 3.x
- next/link for navigation
- React hooks for state management

**Storage**: N/A (frontend only - backend handles persistence)
**Testing**: Playwright for end-to-end validation (via implementation-validator-playwright skill)
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge) - responsive design for mobile, tablet, desktop
**Project Type**: Web application (frontend only)
**Performance Goals**:
- First Contentful Paint (FCP) < 1.5s
- Time to Interactive (TTI) < 3.5s
- Lighthouse Performance score > 90
- Navigation between pages < 200ms

**Constraints**:
- No mock data or fake API responses
- TypeScript strict mode required
- Tailwind CSS must be officially configured (not CDN)
- Server Components by default, Client Components only for interactivity
- All API calls through centralized client
- Session persistence required across page refreshes

**Scale/Scope**:
- 5 main pages (landing, login, signup, dashboard, task management)
- ~15-20 React components
- Responsive layouts for 3 breakpoints (mobile, tablet, desktop)
- Support for modern browsers (last 2 versions)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅
- **Status**: PASS
- **Evidence**: Implementation plan derived from approved spec.md
- **Action**: Proceed with planning

### Principle II: JWT-Only Identity ✅
- **Status**: PASS (Frontend Scope)
- **Evidence**: Frontend will prepare for JWT integration via centralized API client. JWT handling deferred to authentication feature spec.
- **Action**: Ensure API client structure supports JWT attachment

### Principle III: Database-Backed Persistence ✅
- **Status**: PASS (Frontend Scope)
- **Evidence**: Frontend will not include mock data. All state will be fetched from backend API.
- **Action**: Ensure no hardcoded task data in components

### Principle IV: Production-Grade Architecture ✅
- **Status**: PASS
- **Evidence**:
  - TypeScript strict mode required
  - Tailwind CSS officially configured
  - Centralized API client
  - Environment variables for configuration
- **Action**: Implement all production standards

### Principle V: Root-Cause Engineering ✅
- **Status**: PASS
- **Evidence**: Plan focuses on proper architecture, not quick fixes
- **Action**: Maintain focus on sustainable solutions

### Principle VI: Clear Separation of Layers ✅
- **Status**: PASS
- **Evidence**: Frontend-only scope. API contracts will be defined for backend integration.
- **Action**: Create frontend/CLAUDE.md with frontend-specific rules

### Quality Gates (Frontend)
- [ ] `npm run dev` succeeds without errors
- [ ] Tailwind styles render correctly
- [ ] TypeScript compiles with strict mode
- [ ] No console errors in browser
- [ ] Centralized API client in place

**Constitution Check Result**: ✅ PASS - All principles satisfied for frontend scope

## Project Structure

### Documentation (this feature)

```text
specs/001-frontend-web-app/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── api-client.md    # API client interface specification
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── app/                          # Next.js 16+ App Router
│   ├── layout.tsx               # Root layout with global styles
│   ├── page.tsx                 # Landing page (/)
│   ├── login/
│   │   └── page.tsx             # Login page (/login)
│   ├── signup/
│   │   └── page.tsx             # Signup page (/signup)
│   └── dashboard/
│       └── page.tsx             # Dashboard page (/dashboard)
├── components/                   # React components
│   ├── layout/
│   │   ├── Navbar.tsx           # Navigation bar (public + authenticated)
│   │   ├── Footer.tsx           # Footer component
│   │   └── ProfileDropdown.tsx  # Profile button + dropdown
│   ├── landing/
│   │   ├── Hero.tsx             # Hero section
│   │   └── Features.tsx         # Features showcase
│   ├── auth/
│   │   ├── LoginForm.tsx        # Login form (Client Component)
│   │   └── SignupForm.tsx       # Signup form (Client Component)
│   ├── dashboard/
│   │   ├── StatsCards.tsx       # Task statistics cards
│   │   ├── TaskList.tsx         # Task list display
│   │   └── TaskItem.tsx         # Individual task item
│   ├── tasks/
│   │   ├── AddTaskModal.tsx     # Add task modal (Client Component)
│   │   └── EditTaskModal.tsx    # Edit task modal (Client Component)
│   └── ui/
│       ├── Button.tsx           # Reusable button component
│       ├── Input.tsx            # Reusable input component
│       ├── Modal.tsx            # Reusable modal component
│       └── Card.tsx             # Reusable card component
├── lib/                          # Utility functions and clients
│   ├── api-client.ts            # Centralized API client
│   └── utils.ts                 # Utility functions
├── hooks/                        # Custom React hooks
│   ├── useAuth.ts               # Authentication state hook
│   ├── useTasks.ts              # Task management hook
│   └── useModal.ts              # Modal state management hook
├── types/                        # TypeScript type definitions
│   ├── task.ts                  # Task entity types
│   ├── user.ts                  # User entity types
│   └── api.ts                   # API response types
├── public/                       # Static assets
│   └── images/                  # Image assets
├── styles/                       # Global styles
│   └── globals.css              # Global CSS with Tailwind directives
├── CLAUDE.md                     # Frontend-specific rules
├── .env.example                  # Environment variable template
├── .env.local                    # Local environment variables (gitignored)
├── next.config.js                # Next.js configuration
├── tailwind.config.js            # Tailwind CSS configuration
├── tsconfig.json                 # TypeScript configuration
├── package.json                  # Dependencies and scripts
└── README.md                     # Frontend documentation
```

**Structure Decision**: Web application structure (Option 2 from template) with frontend-only scope. The frontend folder contains a complete Next.js 16+ App Router application with clear separation of concerns: app/ for routes, components/ for UI, lib/ for utilities, hooks/ for custom hooks, and types/ for TypeScript definitions. This structure supports scalability and maintainability while following Next.js best practices.

## Complexity Tracking

> **No violations detected** - All constitution principles satisfied for frontend scope.

## Phase 0: Research & Technology Decisions

### Research Tasks

1. **Next.js 16+ App Router Best Practices**
   - Decision: Use App Router with Server Components by default
   - Rationale: App Router is the recommended approach for Next.js 16+, provides better performance with Server Components
   - Alternatives considered: Pages Router (legacy, not recommended for new projects)

2. **Tailwind CSS Configuration**
   - Decision: Official Tailwind CSS configuration with custom theme
   - Rationale: Provides utility-first styling with design consistency, better than CDN approach
   - Alternatives considered: CSS Modules (more verbose), Styled Components (runtime overhead)

3. **TypeScript Strict Mode**
   - Decision: Enable strict mode in tsconfig.json
   - Rationale: Catches more errors at compile time, enforces better type safety
   - Alternatives considered: Loose mode (not production-grade)

4. **Session Persistence Strategy**
   - Decision: Prepare frontend for httpOnly cookie-based sessions (implementation in auth spec)
   - Rationale: Most secure approach, prevents XSS attacks, automatic with fetch API
   - Alternatives considered: localStorage (vulnerable to XSS), sessionStorage (doesn't persist across tabs)

5. **Navigation Pattern**
   - Decision: Use next/link with Link component for all navigation
   - Rationale: Provides client-side navigation with prefetching, better UX than <a> tags
   - Alternatives considered: <a> tags (causes full page reload), router.push (less declarative)

6. **State Management**
   - Decision: React hooks (useState, useContext) for local state, custom hooks for shared logic
   - Rationale: Sufficient for frontend-only scope, no need for Redux/Zustand complexity
   - Alternatives considered: Redux (overkill), Zustand (unnecessary for this scope)

7. **Form Handling**
   - Decision: Controlled components with React state
   - Rationale: Simple, predictable, works well with validation
   - Alternatives considered: React Hook Form (adds dependency), uncontrolled components (less control)

8. **Modal Implementation**
   - Decision: Custom modal component with portal rendering
   - Rationale: Full control over styling and behavior, no external dependencies
   - Alternatives considered: Headless UI (adds dependency), native dialog (limited browser support)

9. **Responsive Design Breakpoints**
   - Decision: Tailwind default breakpoints (sm: 640px, md: 768px, lg: 1024px, xl: 1280px)
   - Rationale: Industry standard, covers mobile/tablet/desktop
   - Alternatives considered: Custom breakpoints (unnecessary complexity)

10. **API Client Architecture**
    - Decision: Centralized fetch wrapper in lib/api-client.ts
    - Rationale: Single point for JWT attachment, error handling, request/response transformation
    - Alternatives considered: Axios (unnecessary dependency), direct fetch calls (scattered logic)

### Technology Stack Summary

| Category | Technology | Version | Justification |
|----------|-----------|---------|---------------|
| Framework | Next.js | 16+ | Modern App Router, Server Components, optimal performance |
| Language | TypeScript | 5.x | Type safety, better DX, catches errors early |
| Styling | Tailwind CSS | 3.x | Utility-first, consistent design, no runtime overhead |
| Navigation | next/link | Built-in | Client-side navigation, prefetching, better UX |
| State | React Hooks | Built-in | Sufficient for scope, no external dependencies |
| Forms | Controlled Components | Built-in | Simple, predictable, works with validation |
| Testing | Playwright | Latest | E2E validation via implementation-validator-playwright skill |

## Phase 1: Design & Contracts

### Data Model

See [data-model.md](./data-model.md) for complete entity definitions.

**Key Entities**:
- **Task**: Frontend representation of task data (id, title, description, completed, created_at, updated_at, user_id)
- **User**: Frontend representation of user data (id, name, email)
- **AuthState**: Session state (isAuthenticated, user, token)

### API Contracts

See [contracts/api-client.md](./contracts/api-client.md) for complete API specifications.

**API Client Interface**:
- Authentication endpoints (login, signup, logout)
- Task CRUD endpoints (create, read, update, delete, list)
- User profile endpoints (get current user)

### Quickstart Guide

See [quickstart.md](./quickstart.md) for development setup instructions.

## Execution Phases

### Phase 0: Project Initialization ✅ (Completed in Planning)

**Objective**: Set up project foundation and research technology decisions

**Deliverables**:
- ✅ Research document with technology decisions
- ✅ Constitution check passed
- ✅ Project structure defined

### Phase 1: Next.js Application Setup

**Objective**: Initialize Next.js application with TypeScript and Tailwind CSS

**Tasks**:
1. Create `frontend/` directory in repository root
2. Initialize Next.js 16+ application with TypeScript
3. Configure Tailwind CSS with custom theme
4. Set up TypeScript strict mode in tsconfig.json
5. Create folder structure (app/, components/, lib/, hooks/, types/, public/)
6. Create frontend/CLAUDE.md with frontend-specific rules
7. Create .env.example with required environment variables
8. Configure next.config.js for production settings

**Validation**:
- `npm install` succeeds without errors
- `npm run dev` starts development server
- TypeScript compiles without errors
- Tailwind CSS classes work in components

### Phase 2: Global Layout & Navigation

**Objective**: Create root layout, navigation bar, and footer

**Tasks**:
1. Create app/layout.tsx with global styles and metadata
2. Create components/layout/Navbar.tsx with responsive navigation
3. Create components/layout/Footer.tsx
4. Implement navigation links using next/link
5. Add responsive menu for mobile devices
6. Style with Tailwind CSS

**Validation**:
- Navigation bar renders on all pages
- Links navigate without page reload
- Responsive menu works on mobile
- Footer displays correctly

### Phase 3: Landing Page

**Objective**: Create marketing landing page with hero and features sections

**Tasks**:
1. Create app/page.tsx for landing page
2. Create components/landing/Hero.tsx with tagline and CTA
3. Create components/landing/Features.tsx showcasing app features
4. Implement responsive layout
5. Add navigation to login/signup pages
6. Style with Tailwind CSS

**Validation**:
- Landing page renders without errors
- Hero section displays tagline and CTA
- Features section shows all 4 features
- Navigation links work correctly
- Responsive on mobile/tablet/desktop

### Phase 4: Authentication Pages

**Objective**: Create login and signup pages with forms

**Tasks**:
1. Create app/login/page.tsx
2. Create app/signup/page.tsx
3. Create components/auth/LoginForm.tsx (Client Component)
4. Create components/auth/SignupForm.tsx (Client Component)
5. Implement form validation
6. Add links between login and signup pages
7. Style forms with Tailwind CSS

**Validation**:
- Login page renders with email/password fields
- Signup page renders with name/email/password fields
- Form validation shows errors
- Links between pages work
- Forms are keyboard accessible

### Phase 5: Dashboard UI

**Objective**: Create authenticated dashboard with task statistics and list

**Tasks**:
1. Create app/dashboard/page.tsx
2. Create components/dashboard/StatsCards.tsx for task statistics
3. Create components/dashboard/TaskList.tsx
4. Create components/dashboard/TaskItem.tsx
5. Create components/layout/ProfileDropdown.tsx (Client Component)
6. Implement responsive layout
7. Style with Tailwind CSS

**Validation**:
- Dashboard renders statistics cards
- Task list displays correctly
- Profile button appears in top-right corner
- Profile dropdown shows user info and logout
- Responsive on all screen sizes

### Phase 6: Task Management

**Objective**: Create task CRUD functionality with modal overlay

**Tasks**:
1. Create components/tasks/AddTaskModal.tsx (Client Component)
2. Create components/tasks/EditTaskModal.tsx (Client Component)
3. Create components/ui/Modal.tsx reusable component
4. Implement modal open/close logic
5. Add task creation form
6. Add task editing form
7. Implement task deletion confirmation
8. Add completion toggle functionality
9. Style modals with Tailwind CSS

**Validation**:
- Add Task button opens modal
- Modal displays title/description fields
- Save button closes modal
- Cancel button closes modal
- Edit/delete buttons work
- Completion toggle updates visually
- Modal closes on outside click

### Phase 7: API Client & Integration Preparation

**Objective**: Create centralized API client skeleton for backend integration

**Tasks**:
1. Create lib/api-client.ts with fetch wrapper
2. Define API endpoint functions (login, signup, getTasks, createTask, etc.)
3. Create types/api.ts for API request/response types
4. Create types/task.ts for Task entity
5. Create types/user.ts for User entity
6. Create hooks/useAuth.ts for authentication state
7. Create hooks/useTasks.ts for task management
8. Prepare for JWT attachment in API client

**Validation**:
- API client exports all endpoint functions
- TypeScript types defined for all entities
- Custom hooks work with mock data
- No console errors
- Code compiles successfully

### Phase 8: Routing & Navigation

**Objective**: Implement client-side routing and navigation guards

**Tasks**:
1. Ensure all pages use next/link for navigation
2. Implement navigation between pages
3. Add loading states for page transitions
4. Prepare for authentication guards (implementation in auth spec)
5. Test keyboard navigation
6. Verify responsive navigation

**Validation**:
- All navigation uses Link component
- No full page reloads on navigation
- Loading states display correctly
- Keyboard navigation works
- Responsive navigation works on mobile

## Validation Criteria

### Development Environment
- [ ] `npm install` succeeds without errors
- [ ] `npm run dev` starts development server on http://localhost:3000
- [ ] `npm run build` completes successfully
- [ ] `npm run lint` passes without errors
- [ ] TypeScript compilation succeeds with strict mode

### Functional Requirements
- [ ] Landing page displays at / with all sections
- [ ] Login page displays at /login with form
- [ ] Signup page displays at /signup with form
- [ ] Dashboard displays at /dashboard with statistics
- [ ] Task list displays on dashboard
- [ ] Add Task modal opens and closes
- [ ] Profile dropdown opens and closes
- [ ] All navigation uses Link component (no <a> tags)

### Accessibility
- [ ] All forms are keyboard accessible
- [ ] Tab navigation works correctly
- [ ] Focus states visible on all interactive elements
- [ ] ARIA labels present where needed
- [ ] Color contrast meets WCAG 2.1 AA standards

### Responsive Design
- [ ] Layout works on 320px width (mobile)
- [ ] Layout works on 768px width (tablet)
- [ ] Layout works on 1920px width (desktop)
- [ ] Navigation menu adapts to screen size
- [ ] All components responsive

### Code Quality
- [ ] TypeScript strict mode enabled
- [ ] No TypeScript errors
- [ ] No console errors in browser
- [ ] Tailwind CSS configured (not CDN)
- [ ] Centralized API client in place
- [ ] No mock data in components
- [ ] Consistent code style

### Performance
- [ ] First Contentful Paint < 1.5s
- [ ] Time to Interactive < 3.5s
- [ ] No unnecessary re-renders
- [ ] Images optimized
- [ ] Bundle size reasonable

## Next Steps

After completing this implementation plan:

1. **Run `/sp.tasks`** to generate detailed task breakdown from this plan
2. **Implement Phase 1-8** following the task list
3. **Validate with `implementation-validator-playwright` skill** after each phase
4. **Create frontend/CLAUDE.md** with frontend-specific rules
5. **Proceed to authentication feature spec** for JWT integration
6. **Proceed to backend feature spec** for API implementation

## Notes

- This plan covers frontend UI only. Authentication logic (JWT handling) will be implemented in a separate authentication feature.
- Backend API endpoints will be implemented in a separate backend feature.
- Database persistence will be handled by the backend.
- The centralized API client will be structured but not fully functional until backend integration.
- Session persistence implementation details will be defined in the authentication feature spec.
- All modern Next.js patterns will be used (Link component, App Router, Server Components).
