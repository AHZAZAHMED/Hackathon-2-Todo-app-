# Feature Specification: Chatbot Frontend UI Fixes + Playwright Validation

**Feature Branch**: `005-chatbot-ui-fixes`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Feature Update: Phase-3 Spec-1 Chatbot Frontend UI Fixes + Playwright Validation - Fix ChatKit UI rendering, layout constraints, and add automated browser validation"

## Context

This specification addresses critical UI defects in the Phase-3 Chatbot Frontend (004-chatbot-frontend) that prevent proper user interaction with the ChatKit-based chat interface. The existing implementation exhibits multiple layout and rendering issues that make the chatbot unusable.

**Current Issues:**
- Chat window opens at excessive size, covering most of the viewport
- Black/white empty panel appears instead of chat content
- Chat icon becomes hidden behind the chat window when opened
- Chat window cannot be closed once opened (close button non-functional)
- Chat window overlaps the bottom edge instead of floating above it
- User cannot dismiss the chatbot panel
- ChatKit UI fails to render correctly on initial load

**Scope:** Frontend-only fixes to the existing ChatKit integration. No backend, agent, MCP, or database changes.

## User Scenarios & Testing

### User Story 1 - Fix Chat Window Sizing and Positioning (Priority: P1)

Users need the chat window to open at a reasonable size that doesn't overwhelm the page and maintains proper spacing from viewport edges.

**Why this priority**: Without proper sizing, the chat window is unusable and blocks the entire page, making it impossible to interact with the application while chatting.

**Independent Test**: Open the chat by clicking the floating icon. The chat window should appear at a constrained size (max 420px width, max 70vh height) with visible margins from the bottom edge (minimum 24px). The window should not cover the entire viewport.

**Acceptance Scenarios**:

1. **Given** user is on any authenticated page, **When** user clicks the chat icon, **Then** chat window opens with width ≤ 420px and height ≤ 70vh
2. **Given** chat window is open, **When** user views the layout, **Then** window has minimum 24px margin from bottom edge
3. **Given** chat window is open on desktop, **When** user views the page, **Then** window appears as a fixed panel at bottom-right, not full-screen
4. **Given** chat window is open on mobile (<640px), **When** user views the page, **Then** window appears as full-screen modal with proper constraints

---

### User Story 2 - Fix Chat Icon Visibility and Z-Index (Priority: P1)

Users need the chat icon to remain visible and clickable at all times, even when the chat window is open, so they can toggle the chat on and off.

**Why this priority**: If the icon is hidden behind the chat window, users cannot close the chat, effectively trapping them in the chat interface.

**Independent Test**: Open the chat window and verify the floating icon remains visible above the chat window. Click the icon to close the chat. The icon should always be accessible.

**Acceptance Scenarios**:

1. **Given** chat window is closed, **When** user views the page, **Then** floating icon is visible at bottom-right corner
2. **Given** chat window is open, **When** user views the page, **Then** floating icon remains visible above the chat window (higher z-index)
3. **Given** chat window is open, **When** user clicks the floating icon, **Then** chat window closes
4. **Given** chat window is open, **When** user hovers over the icon, **Then** icon shows hover state indicating it's clickable

---

### User Story 3 - Fix Close and Minimize Functionality (Priority: P1)

Users need working close (X) and minimize (-) buttons in the chat header to dismiss or minimize the chat window.

**Why this priority**: Without functional close/minimize buttons, users cannot control the chat interface, making it intrusive and unusable.

**Independent Test**: Open the chat window. Click the close (X) button in the header. The chat window should close completely. Reopen and click the minimize (-) button. The chat should minimize to just the icon.

**Acceptance Scenarios**:

1. **Given** chat window is open, **When** user clicks the close (X) button, **Then** chat window closes completely and only the floating icon remains visible
2. **Given** chat window is open, **When** user clicks the minimize (-) button, **Then** chat window minimizes and only the floating icon remains visible
3. **Given** chat window is closed, **When** user clicks the floating icon, **Then** chat window opens again
4. **Given** chat window is minimized, **When** user clicks the floating icon, **Then** chat window opens to full size

---

### User Story 4 - Add Keyboard and Click-Outside Interactions (Priority: P2)

Users need intuitive ways to close the chat using keyboard shortcuts (Escape key) and by clicking outside the chat window.

**Why this priority**: These are standard UI patterns that improve usability and meet user expectations for modal-like interfaces.

**Independent Test**: Open the chat window. Press the Escape key. The chat should close. Reopen the chat and click anywhere outside the chat window. The chat should close.

**Acceptance Scenarios**:

1. **Given** chat window is open, **When** user presses the Escape key, **Then** chat window closes
2. **Given** chat window is open, **When** user clicks outside the chat window (on the page background), **Then** chat window closes
3. **Given** chat window is open, **When** user clicks inside the chat window, **Then** chat window remains open
4. **Given** chat window is open, **When** user scrolls the page, **Then** page scrolling works normally (chat doesn't block scrolling)

---

### User Story 5 - Playwright Automated Validation (Priority: P2)

Development team needs automated browser tests to verify all chat UI behaviors work correctly and prevent regression.

**Why this priority**: Automated tests ensure the fixes remain stable and catch any future regressions in the chat UI.

**Independent Test**: Run the Playwright test suite. All 10 validation checks should pass, confirming proper chat behavior across different scenarios.

**Acceptance Scenarios**:

1. **Given** Playwright test suite is executed, **When** tests run, **Then** all 10 validation checks pass
2. **Given** tests are running, **When** icon visibility test executes, **Then** test confirms icon is visible on page load
3. **Given** tests are running, **When** chat open test executes, **Then** test confirms clicking icon opens chat with proper size
4. **Given** tests are running, **When** content rendering test executes, **Then** test confirms ChatKit content renders (not blank)
5. **Given** tests are running, **When** close functionality test executes, **Then** test confirms close button works
6. **Given** tests are running, **When** mobile viewport test executes, **Then** test confirms responsive behavior on mobile

---

### Edge Cases

- What happens when the viewport is very small (< 375px width)? Chat should adapt to full-screen modal.
- What happens when the user rapidly clicks the chat icon multiple times? Only one chat window should open, no duplicates.
- What happens when ChatKit fails to load? Show error message in chat window, don't show blank panel.
- What happens when the user has a very long conversation (100+ messages)? Chat should scroll properly without performance issues.
- What happens when the user opens the chat on a page with high z-index elements? Chat icon and window should have higher z-index (icon: z-60, window: z-50).
- What happens when the user resizes the browser window while chat is open? Chat should maintain proper positioning and constraints.
- What happens when the user navigates to a different page while chat is open? Chat state should persist (remain open or closed based on previous state).
- What happens when the JWT token expires while chat is open? Show authentication error in chat, prompt user to log in again.

## Requirements

### Functional Requirements

- **FR-019**: Chatbot icon MUST be fixed at bottom-right corner and always visible above chat window
- **FR-020**: Chat window MUST open slightly above bottom edge with minimum 24px margin
- **FR-021**: Chat window width MUST NOT exceed 420px
- **FR-022**: Chat window height MUST NOT exceed 70vh (70% of viewport height)
- **FR-023**: Chat window MUST support close and minimize toggle functionality
- **FR-024**: Chat window MUST NOT obscure the chatbot icon
- **FR-025**: No blank, black, or white empty container allowed - ChatKit content must render
- **FR-026**: Chat content MUST render within 500ms after opening
- **FR-027**: Only one chat window allowed at a time (no duplicates)
- **FR-028**: Clicking the floating icon MUST toggle chat open/close
- **FR-029**: Pressing Escape key MUST close the chat window
- **FR-030**: Clicking outside the chat window MUST close it
- **FR-031**: Chat window MUST NOT block page scrolling
- **FR-032**: Z-index hierarchy MUST keep icon (z-60) above window (z-50)
- **FR-033**: Responsive behavior on mobile required (full-screen modal on <640px)

### UI Requirements

- **UI-001**: Floating circular chatbot icon at bottom-right corner
- **UI-002**: Chat panel slides upward with smooth transition animation (300ms)
- **UI-003**: Chat window has rounded corners (border-radius: 12px on desktop)
- **UI-004**: Chat window has shadow elevation (shadow-2xl)
- **UI-005**: Chat window uses fixed positioning
- **UI-006**: Close (X) button visible and functional in chat header
- **UI-007**: Minimize (-) button visible and functional in chat header
- **UI-008**: ChatKit container MUST NOT overflow viewport
- **UI-009**: Chat window background is white with proper contrast
- **UI-010**: Icon has hover state (scale: 1.05, background: darker blue)

### Validation Requirements

Playwright automated tests using `browsing-with-playwright` skill MUST verify:

- **VAL-001**: Icon visible on page load
- **VAL-002**: Clicking icon opens chat window
- **VAL-003**: Chat renders messages (not blank/empty)
- **VAL-004**: Icon remains clickable when chat is open
- **VAL-005**: Close button works correctly
- **VAL-006**: Window closes when close button clicked
- **VAL-007**: Window respects size constraints (width ≤ 420px, height ≤ 70vh)
- **VAL-008**: Mobile viewport behavior verified (full-screen on <640px)
- **VAL-009**: No visual overlap between icon and window
- **VAL-010**: No console errors during chat interactions

### Key Entities

- **ChatUIState**: Represents the UI state of the floating launcher (isOpen: boolean, isMinimized: boolean)
- **ChatInterface**: The main chat window component that wraps ChatKit
- **FloatingChatLauncher**: The floating icon button that toggles chat visibility
- **ChatHeader**: The header component with close and minimize buttons

## Success Criteria

### Measurable Outcomes

- **SC-001**: Chat window opens at correct size (width ≤ 420px, height ≤ 70vh) in 100% of test cases
- **SC-002**: Chat content renders within 500ms of opening in 95% of cases
- **SC-003**: Chat icon remains visible and clickable in 100% of scenarios
- **SC-004**: Close button successfully closes chat in 100% of attempts
- **SC-005**: Minimize button successfully minimizes chat in 100% of attempts
- **SC-006**: Escape key closes chat in 100% of attempts
- **SC-007**: Click-outside closes chat in 100% of attempts
- **SC-008**: Chat window maintains proper 24px bottom margin in 100% of cases
- **SC-009**: No blank/empty chat panels appear in any scenario
- **SC-010**: All 10 Playwright validation tests pass
- **SC-011**: Chat UI works correctly on mobile viewports (<640px) in 100% of test cases
- **SC-012**: Page scrolling works normally when chat is open
- **SC-013**: No console errors occur during chat interactions
- **SC-014**: Chat state persists correctly across page navigations
- **SC-015**: Users can successfully interact with chat without UI blocking issues

## Out of Scope

- Backend API changes
- AI agent modifications
- MCP server changes
- Database schema updates
- New chat features beyond fixing existing UI
- Real-time streaming responses
- Voice input/output
- File attachments
- Multi-modal capabilities
- Conversation branching or editing
- Custom chat themes beyond fixing current styling

## Assumptions

- Existing ChatKit integration is functional at the API level (messages can be sent/received)
- JWT authentication is working correctly
- Backend POST /api/chat endpoint is operational
- Better Auth session management is functional
- Database conversation storage is working
- The issues are purely frontend UI/layout problems
- ChatKit library itself is not the source of the rendering issues
- Playwright is available for automated testing
- `browsing-with-playwright` skill can be used for validation

## Dependencies

- Existing Phase-3 Chatbot Frontend implementation (004-chatbot-frontend)
- OpenAI ChatKit React library (@openai/chatkit-react)
- Lucide React icons library (for close/minimize icons)
- Tailwind CSS for styling
- Next.js 16+ App Router
- React 19+
- Playwright for automated testing
- `browsing-with-playwright` skill for validation

## Constraints

- MUST reuse existing ChatKit integration (no custom chat framework)
- NO backend changes allowed
- NO changes to agent, MCP, or database layers
- MUST follow existing Phase-2 and Phase-3 architecture patterns
- MUST maintain backward compatibility with existing chat functionality
- MUST use existing JWT authentication flow
- MUST follow Spec-Driven Development workflow (specify → plan → tasks → implement)
- MUST use TypeScript strict mode
- MUST follow Next.js 16+ App Router conventions

## Technical Constraints

- Frontend-only changes
- Must work with existing ChatKit API configuration
- Must maintain existing ChatUIContext state management
- Must preserve existing JWT token injection logic
- Must work on all supported browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- Must work on mobile devices (iOS Safari 14+, Android Chrome 90+)

## Success Outcome

The floating ChatKit UI behaves like a production-quality chatbot widget with:
- Proper sizing and positioning
- Always-visible and clickable icon
- Functional close and minimize controls
- Smooth animations and transitions
- No blank or empty panels
- Responsive mobile behavior
- Validated browser behavior via Playwright automated tests
- No console errors or visual glitches
- Intuitive keyboard and click-outside interactions
- Stable layout that doesn't interfere with page content
