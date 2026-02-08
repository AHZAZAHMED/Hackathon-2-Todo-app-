# Implementation Plan: Chatbot Frontend UI Fixes + Playwright Validation

**Branch**: `005-chatbot-ui-fixes` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-chatbot-ui-fixes/spec.md`

**Note**: This plan addresses critical UI defects in the Phase-3 Chatbot Frontend (004-chatbot-frontend) implementation.

## Summary

Fix critical UI defects in the existing ChatKit-based chat interface to ensure proper sizing, positioning, visibility, and interaction. The current implementation has a non-functional floating chat window with sizing issues, hidden icons, and broken close functionality. This plan focuses exclusively on frontend CSS/layout fixes, z-index management, event handlers, and Playwright validation. No backend, agent, MCP, or database changes are permitted.

**Primary Requirements**:
- Fix chat window sizing (max 420px width, max 70vh height)
- Fix positioning (24px bottom margin, bottom-right corner)
- Fix z-index hierarchy (icon above window)
- Fix close/minimize functionality
- Add keyboard shortcuts (Escape key)
- Add click-outside-to-close behavior
- Ensure ChatKit content renders (no blank panels)
- Add Playwright automated validation (10 checks)
- Responsive mobile behavior (full-screen on <640px)

**Technical Approach**:
- Refactor ChatInterface component with proper CSS constraints
- Fix z-index values (icon: z-60, window: z-50)
- Add event listeners for Escape key and click-outside
- Ensure ChatKit mounts correctly with proper container sizing
- Add transition animations for smooth open/close
- Create Playwright test suite using browsing-with-playwright skill
- Validate all fixes with automated browser tests

## Technical Context

**Language/Version**: TypeScript 5.x with strict mode (existing Phase-3 configuration)
**Primary Dependencies**:
- Next.js 16+ (existing)
- React 19+ (existing)
- OpenAI ChatKit React (@openai/chatkit-react v1.4.3) (existing)
- Tailwind CSS (existing)
- Lucide React (existing - for icons)
- Playwright (for validation)

**Storage**: N/A (frontend-only fixes)
**Testing**: Playwright for browser-based validation using browsing-with-playwright skill
**Target Platform**: Web browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+, iOS Safari 14+, Android Chrome 90+)
**Project Type**: Web application (frontend extension of existing Phase-3)
**Performance Goals**:
- Chat window opens within 300ms (95th percentile)
- Chat content renders within 500ms of opening
- Smooth animations (60fps)
- No layout shift or jank

**Constraints**:
- Frontend-only scope (no backend, AI, MCP, or database changes)
- Must reuse existing ChatKit integration
- Must maintain existing JWT authentication flow
- Must preserve existing ChatUIContext state management
- Must not break existing Phase-2 or Phase-3 functionality
- Must work on all supported browsers and mobile devices

**Scale/Scope**:
- 3 components to modify (ChatInterface, FloatingChatLauncher, ChatHeader)
- 1 CSS file to update (globals.css)
- 1 Playwright test suite to create
- Estimated 8-10 files affected total

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase-2 Principles (Inherited)

✅ **Principle I: Spec-Driven Development**
- Status: COMPLIANT
- Evidence: Implementation follows approved specification from 005-chatbot-ui-fixes/spec.md
- No deviations permitted

✅ **Principle II: JWT-Only Identity**
- Status: N/A (frontend UI fixes only, no authentication changes)
- Evidence: No changes to JWT flow or authentication logic

✅ **Principle III: Database-Backed Persistence**
- Status: N/A (frontend UI fixes only, no database changes)
- Evidence: No changes to data persistence layer

✅ **Principle IV: Production-Grade Architecture**
- Status: COMPLIANT
- Evidence: TypeScript strict mode, Tailwind CSS official config, proper error handling, no shortcuts

✅ **Principle V: Root-Cause Engineering**
- Status: COMPLIANT
- Evidence: Fixes address root causes (CSS constraints, z-index hierarchy, event handlers) not symptoms

✅ **Principle VI: Clear Separation of Layers**
- Status: COMPLIANT
- Evidence: Frontend-only scope, no backend/AI/MCP logic, clear boundaries

### Phase-3 Principles (Applicable)

✅ **Principle VII: MCP-Only Database Mutations**
- Status: N/A (frontend UI fixes only, no database operations)
- Evidence: No changes to MCP layer or database

✅ **Principle VIII: Stateless Backend Architecture**
- Status: N/A (frontend UI fixes only, no backend changes)
- Evidence: No changes to backend architecture

✅ **Principle IX: AI Agent Orchestration**
- Status: N/A (frontend UI fixes only, no agent changes)
- Evidence: No changes to AI agent layer

### Quality Gates

**Frontend Gates**:
- [ ] Chat window opens at correct size (≤420px width, ≤70vh height)
- [ ] Chat window has proper positioning (24px bottom margin)
- [ ] Chat icon remains visible above chat window (z-index hierarchy correct)
- [ ] Close button works correctly
- [ ] Minimize button works correctly
- [ ] Escape key closes chat
- [ ] Click-outside closes chat
- [ ] ChatKit content renders (no blank panels)
- [ ] Smooth animations (300ms transitions)
- [ ] Responsive mobile behavior (full-screen on <640px)
- [ ] TypeScript compiles with strict mode
- [ ] No console errors in browser

**Playwright Validation Gates**:
- [ ] Icon visible on page load
- [ ] Clicking icon opens chat
- [ ] Chat renders messages (not blank)
- [ ] Icon remains clickable when chat open
- [ ] Close button works
- [ ] Window closes correctly
- [ ] Window respects size constraints
- [ ] Mobile viewport behavior verified
- [ ] No visual overlap
- [ ] No console errors

### Constitution Compliance Summary

**Status**: ✅ FULLY COMPLIANT

All applicable constitution principles are satisfied. No violations require justification. This is a frontend-only fix that maintains existing architecture and adds no complexity.

## Project Structure

### Documentation (this feature)

```text
specs/005-chatbot-ui-fixes/
├── spec.md              # Feature specification (approved)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (to be generated)
├── contracts/           # Phase 1 output (to be generated)
│   └── playwright-validation.md  # Playwright test requirements
├── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
└── checklists/
    └── requirements.md  # Specification quality checklist (existing)
```

### Source Code (repository root)

```text
frontend/
├── CLAUDE.md                          # Frontend-specific rules (existing Phase-2)
├── app/
│   ├── layout.tsx                     # Root layout (existing - no changes needed)
│   └── globals.css                    # Global styles (MODIFY - z-index, animations)
├── components/
│   └── chat/                          # Chat-specific components (existing)
│       ├── ChatInterface.tsx          # MODIFY - fix sizing, positioning, rendering
│       ├── ChatHeader.tsx             # MODIFY - ensure close/minimize work
│       └── FloatingChatLauncher.tsx   # MODIFY - fix z-index, toggle logic
├── lib/
│   └── contexts/
│       └── ChatUIContext.tsx          # Existing - no changes needed
└── types/
    └── chat.ts                        # Existing - no changes needed

tests/
└── playwright/                        # NEW - Playwright test suite
    ├── chatbot-ui.spec.ts             # NEW - UI validation tests
    └── playwright.config.ts           # NEW - Playwright configuration

backend/                               # Existing Phase-2 (no changes)
```

**Structure Decision**:

This feature modifies the existing Phase-3 frontend chat components to fix UI defects. The structure follows Next.js 16+ App Router conventions established in Phase-2 and Phase-3. Key changes:

1. **Modify existing components**: ChatInterface, ChatHeader, FloatingChatLauncher
2. **Update global styles**: Add proper z-index hierarchy and animations
3. **Add Playwright tests**: New test suite for automated validation
4. **No new components**: All fixes are to existing code

The frontend-only scope means no changes to backend, database, or AI layers.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. This section is not applicable.

## Phase 0: Research & Technology Validation

**Objective**: Resolve all technical unknowns and validate fix approaches before implementation.

### Research Tasks

1. **ChatKit Container Sizing Best Practices**
   - Research: How to properly constrain ChatKit component within fixed-size container
   - Investigate: CSS properties for max-width, max-height, overflow handling
   - Validate: ChatKit respects parent container constraints
   - Document: Recommended CSS patterns for ChatKit wrapper

2. **Z-Index Hierarchy Management**
   - Research: Best practices for z-index management in Next.js/Tailwind
   - Investigate: Proper z-index values to ensure icon stays above window
   - Validate: No conflicts with existing page elements (navbar, modals, etc.)
   - Document: Z-index hierarchy (icon: z-60, window: z-50, page content: default)

3. **React Event Handlers for Close Behavior**
   - Research: Best practices for Escape key and click-outside handlers in React
   - Investigate: useEffect patterns for adding/removing event listeners
   - Validate: Event handlers don't interfere with ChatKit internal events
   - Document: Recommended patterns for keyboard and click-outside detection

4. **ChatKit Rendering Issues**
   - Research: Common causes of blank/empty ChatKit panels
   - Investigate: ChatKit initialization timing and mount lifecycle
   - Validate: ChatKit content renders immediately after container mounts
   - Document: Proper ChatKit mounting sequence and error handling

5. **Playwright Browser Automation**
   - Research: Playwright setup for Next.js applications
   - Investigate: browsing-with-playwright skill capabilities and API
   - Validate: Playwright can interact with floating chat UI elements
   - Document: Test patterns for floating UI, z-index validation, size constraints

6. **Responsive Mobile Behavior**
   - Research: Best practices for full-screen modals on mobile
   - Investigate: Tailwind breakpoint patterns for responsive chat UI
   - Validate: Chat transitions smoothly between desktop panel and mobile modal
   - Document: Responsive CSS patterns and breakpoint strategy

### Research Output

**Deliverable**: `research.md` containing:
- Decision: Technology/pattern chosen for each research area
- Rationale: Why this approach is suitable for fixing the UI issues
- Implementation guidance: Specific CSS properties, event handler patterns, Playwright setup
- Key steps and gotchas for each fix area

**Success Criteria**:
- All technical unknowns resolved
- ChatKit container sizing approach validated
- Z-index hierarchy defined
- Event handler patterns selected
- Playwright validation approach confirmed
- No blocking technical unknowns remain

## Phase 1: Design & Contracts

**Prerequisites**: `research.md` complete with all technical unknowns resolved

### 1.1 Data Model

**Objective**: Define frontend data structures (if any new structures needed).

**Deliverable**: `data-model.md`

**Analysis**: This feature modifies existing UI components and does not introduce new data structures. The existing ChatUIState (isOpen, isMinimized) is sufficient. No new entities required.

**Content**:
- Confirm existing ChatUIState structure is adequate
- Document CSS class structure for chat components
- Document z-index hierarchy as "data" for styling

### 1.2 Contracts

**Objective**: Define Playwright validation contract.

**Deliverable**: `contracts/playwright-validation.md`

**Validation Contract**:

```markdown
# Playwright Validation Contract

## Test Suite: Chatbot UI Validation

### Test 1: Icon Visibility on Page Load
- Navigate to authenticated page
- Assert: Floating chat icon is visible
- Assert: Icon has correct position (bottom-right)
- Assert: Icon has correct z-index (above page content)

### Test 2: Click Icon Opens Chat
- Click floating chat icon
- Assert: Chat window appears
- Assert: Chat window has correct size (≤420px width, ≤70vh height)
- Assert: Chat window has correct position (24px from bottom)

### Test 3: Chat Renders Messages (Not Blank)
- Open chat window
- Wait for ChatKit to load (max 500ms)
- Assert: ChatKit content is visible (not blank/black/white)
- Assert: Chat interface elements are present

### Test 4: Icon Remains Clickable
- Open chat window
- Assert: Floating icon is still visible
- Assert: Icon is above chat window (z-index check)
- Click icon
- Assert: Chat window closes

### Test 5: Close Button Works
- Open chat window
- Click close (X) button in header
- Assert: Chat window closes
- Assert: Only floating icon remains visible

### Test 6: Escape Key Closes Chat
- Open chat window
- Press Escape key
- Assert: Chat window closes

### Test 7: Click Outside Closes Chat
- Open chat window
- Click outside chat window (on page background)
- Assert: Chat window closes

### Test 8: Size Constraints Respected
- Open chat window
- Measure window dimensions
- Assert: Width ≤ 420px
- Assert: Height ≤ 70vh
- Assert: Bottom margin ≥ 24px

### Test 9: Mobile Viewport Behavior
- Set viewport to mobile size (<640px)
- Open chat window
- Assert: Chat appears as full-screen modal
- Assert: Close button still works

### Test 10: No Console Errors
- Open chat window
- Interact with chat (send message, close, reopen)
- Assert: No console errors logged
```

### 1.3 Component Architecture

**Objective**: Define component modifications and CSS structure.

**Deliverable**: Component architecture documented in `quickstart.md`

**Modified Component Tree**:
```
App Layout (existing)
└── ChatUIProvider (existing)
    ├── Navbar (existing)
    ├── Main Content (existing)
    ├── Footer (existing)
    └── FloatingChatLauncher (MODIFY)
        ├── Floating Icon Button (MODIFY - z-index fix)
        └── ChatInterface (MODIFY - when open)
            ├── ChatHeader (MODIFY - close/minimize fix)
            └── ChatKit Component (existing - ensure renders)
```

**Component Modifications**:

1. **FloatingChatLauncher** (frontend/components/chat/FloatingChatLauncher.tsx)
   - Fix z-index to z-60 (above chat window)
   - Add proper toggle logic (open/close on click)
   - Ensure icon always visible

2. **ChatInterface** (frontend/components/chat/ChatInterface.tsx)
   - Fix container sizing (max-width: 420px, max-height: 70vh)
   - Fix positioning (bottom: 24px, right: 24px)
   - Fix z-index to z-50 (below icon)
   - Add Escape key handler
   - Add click-outside handler
   - Ensure ChatKit mounts properly
   - Add transition animations

3. **ChatHeader** (frontend/components/chat/ChatHeader.tsx)
   - Ensure close button calls closeChat()
   - Ensure minimize button calls minimizeChat()
   - Add proper event handlers

4. **globals.css** (frontend/app/globals.css)
   - Update z-index hierarchy
   - Add transition animations
   - Add responsive breakpoints

### 1.4 CSS Architecture

**Objective**: Define CSS fixes and z-index hierarchy.

**Z-Index Hierarchy**:
```css
/* Z-index hierarchy for chat components */
--z-50: 50;  /* Chat window */
--z-60: 60;  /* Floating chat icon (above window) */
```

**CSS Fixes**:
```css
/* Chat window constraints */
.chat-window {
  position: fixed;
  bottom: 24px;
  right: 24px;
  max-width: 420px;
  max-height: 70vh;
  z-index: 50;
  border-radius: 12px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  transition: all 300ms ease-in-out;
}

/* Floating icon */
.chat-icon {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 60; /* Above chat window */
  transition: transform 200ms ease-in-out;
}

/* Mobile responsive */
@media (max-width: 640px) {
  .chat-window {
    bottom: 0;
    right: 0;
    left: 0;
    top: 0;
    max-width: 100%;
    max-height: 100%;
    border-radius: 0;
  }
}
```

### 1.5 Quickstart Guide

**Objective**: Provide implementation quickstart for developers.

**Deliverable**: `quickstart.md`

**Contents**:
1. Overview of UI fixes needed
2. Component modification guide
3. CSS changes required
4. Event handler implementation
5. Playwright test setup
6. Testing approach
7. Common issues and solutions

### 1.6 Agent Context Update

**Objective**: Update agent-specific context file with UI fix patterns.

**Action**: Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`

**Expected Updates**:
- Add z-index management patterns
- Add event handler patterns for Escape key and click-outside
- Add Playwright validation patterns
- Preserve existing Phase-2 and Phase-3 context

## Phase 2: Task Breakdown

**Note**: Phase 2 (task generation) is handled by the `/sp.tasks` command, NOT by `/sp.plan`.

This plan stops after Phase 1 design artifacts are generated. The user must run `/sp.tasks` to generate the task breakdown.

## Implementation Steps (For Task Generation)

The following steps will be broken down into tasks by `/sp.tasks`:

### Step 1: UI Root Container Refactor
- Locate ChatInterface component
- Apply CSS constraints (max-width: 420px, max-height: 70vh)
- Fix positioning (bottom: 24px, right: 24px)
- Add overflow: hidden
- Add border-radius and shadow
- Ensure z-index: 50

### Step 2: Floating Icon + Toggle Logic
- Fix FloatingChatLauncher z-index to 60
- Ensure icon always visible
- Add toggle logic (click icon to open/close)
- Connect close button to closeChat()
- Connect minimize button to minimizeChat()
- Prevent multiple chat windows

### Step 3: Chat Rendering Fix
- Ensure ChatKit loads immediately after toggle
- Remove any blank/empty placeholder panels
- Verify ChatKit provider is correctly mounted
- Add loading state if needed
- Enforce 500ms render timeout

### Step 4: Event Handlers
- Add Escape key handler (useEffect with event listener)
- Add click-outside handler (useEffect with event listener)
- Ensure handlers clean up on unmount
- Test handlers don't interfere with ChatKit

### Step 5: Visual UX Improvements
- Add transition animations (300ms ease-in-out)
- Ensure smooth slide-up effect
- Add hover states for icon
- Prevent page scroll lock when chat open

### Step 6: Responsive Constraints
- Add mobile breakpoint (<640px)
- Full-screen modal on mobile
- Maintain 24px margin on desktop
- Test on various screen sizes

### Step 7: Playwright Validation (MANDATORY)
- Set up Playwright test suite
- Implement 10 validation tests (see contracts)
- Use browsing-with-playwright skill
- Capture screenshots
- Verify all tests pass

### Step 8: Final Regression Check
- Test open/close multiple times
- Verify no layout regression
- Verify no multiple windows
- Verify no console errors

## Validation Criteria

### Phase 0 Validation (Research Complete)
- [ ] `research.md` exists and contains all required sections
- [ ] ChatKit container sizing approach validated
- [ ] Z-index hierarchy defined
- [ ] Event handler patterns selected
- [ ] Playwright validation approach confirmed
- [ ] No unresolved technical unknowns

### Phase 1 Validation (Design Complete)
- [ ] `data-model.md` exists (confirms no new data structures needed)
- [ ] `contracts/playwright-validation.md` exists with complete test contract
- [ ] `quickstart.md` exists with implementation guide
- [ ] Component architecture documented
- [ ] CSS architecture defined
- [ ] Agent context updated successfully
- [ ] Constitution Check re-evaluated (still compliant)

### Implementation Readiness
- [ ] All design artifacts generated
- [ ] No blocking dependencies
- [ ] Clear implementation path defined
- [ ] Ready for `/sp.tasks` command

## Agent Assignment

**Primary Agent**: `senior-next.js-developer`
- Responsible for: Next.js 16+ App Router, React component modifications, TypeScript implementation, CSS fixes

**Supporting Agents**:
- `browsing-with-playwright`: Playwright validation and automated testing
- `implementation-validator-playwright`: Browser-based validation after implementation

**Agent Invocation Strategy**:
1. Use `senior-next.js-developer` for all frontend implementation tasks
2. Use `browsing-with-playwright` for Playwright test creation and validation
3. Use `implementation-validator-playwright` for final end-to-end validation

## Phase Compliance Statement

This implementation plan complies with all Phase-3 constitution principles:

✅ **Spec-Driven Development**: Plan follows approved specification (005-chatbot-ui-fixes/spec.md)
✅ **Production-Grade Architecture**: TypeScript strict mode, proper CSS architecture, automated testing
✅ **Root-Cause Engineering**: Fixes address root causes (CSS constraints, z-index, event handlers) not symptoms
✅ **Clear Separation of Layers**: Frontend-only scope, no backend/AI/MCP changes

**Phase-2 Foundation**: This feature fixes existing Phase-3 frontend without breaking Phase-2 functionality.

**Phase-3 Integration**: Frontend fixes maintain existing ChatKit integration and JWT authentication flow.

---

**Plan Status**: ✅ READY FOR PHASE 0 RESEARCH

**Next Command**: Continue with Phase 0 research task execution (automated by this command)
