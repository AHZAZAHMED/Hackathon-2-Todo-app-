# Feature Specification: Phase-3 Chatbot Frontend

**Feature Branch**: `004-chatbot-frontend`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Phase-3 Chatbot Frontend (OpenAI ChatKit UI) - Production-ready ChatKit-based frontend providing conversational interface for managing todos via Phase-3 chat API"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Send and Receive Chat Messages (Priority: P1)

As a logged-in user, I want to send messages to the AI chatbot and receive responses so that I can manage my todos through natural conversation.

**Why this priority**: This is the core functionality of the chatbot frontend. Without the ability to send and receive messages, no other features matter. This delivers immediate value by enabling conversational todo management.

**Independent Test**: Can be fully tested by logging in, typing a message like "Show me my tasks", sending it, and verifying that an AI response appears in the chat interface. Delivers the core value of conversational interaction.

**Acceptance Scenarios**:

1. **Given** I am logged in and on the chat page, **When** I type "Add a task to buy groceries" and press send, **Then** the message appears in the chat as my message and I receive an assistant response confirming the task was added
2. **Given** I am logged in and on the chat page, **When** I type "What are my tasks?" and send it, **Then** I see my message followed by an assistant response listing my current tasks
3. **Given** I am on the chat page, **When** I send a message, **Then** the input field clears and a loading indicator appears until the response arrives
4. **Given** I am on the chat page, **When** I receive an assistant response, **Then** the message is clearly visually distinguished from my messages (different styling, alignment, or avatar)

---

### User Story 2 - View Conversation History (Priority: P2)

As a user, I want to see the history of my conversation with the chatbot so that I can maintain context and review previous interactions.

**Why this priority**: Conversation history provides context and continuity. Users need to see what they've asked and what the assistant responded to understand the flow of their todo management session. This is essential for a good chat experience but can be implemented after basic send/receive works.

**Independent Test**: Can be tested by sending multiple messages in sequence, refreshing the page, and verifying that all previous messages are still visible in the correct order. Delivers value by maintaining conversation context.

**Acceptance Scenarios**:

1. **Given** I have sent 5 messages and received 5 responses, **When** I scroll up in the chat interface, **Then** I can see all 10 messages in chronological order (oldest at top, newest at bottom)
2. **Given** I have an active conversation, **When** I refresh the page, **Then** my conversation history loads and displays all previous messages
3. **Given** I am viewing a long conversation, **When** new messages arrive, **Then** the chat automatically scrolls to show the latest message
4. **Given** I have multiple conversations over time, **When** I return to the chat page, **Then** I see my most recent conversation history

---

### User Story 3 - Access Chatbot from Any Page (Priority: P2)

As a logged-in user, I want to access the chatbot from any authenticated page via a floating launcher icon so that I can quickly manage my todos without navigating away from my current page.

**Why this priority**: The floating launcher provides convenient access to the chatbot from anywhere in the application. This is essential for a good user experience as it eliminates the need to navigate to a dedicated chat page. Users can stay in their workflow while interacting with the chatbot. This should be implemented after basic chat functionality works but before error handling polish.

**Independent Test**: Can be tested by logging in, navigating to different pages (dashboard, tasks list, settings), and verifying that the floating icon appears consistently. Clicking the icon should open the chat interface. Delivers value by making the chatbot accessible throughout the application.

**Acceptance Scenarios**:

1. **Given** I am logged in and on any authenticated page, **When** I look at the bottom-right corner of the screen, **Then** I see a floating chatbot launcher icon
2. **Given** I see the floating launcher icon, **When** I click on it, **Then** the chat interface opens in a modal or slide-in panel
3. **Given** the chat interface is open, **When** I click the close button, **Then** the chat interface closes and I return to the underlying page
4. **Given** the chat interface is open, **When** I click the minimize button, **Then** the chat interface minimizes back to the floating icon
5. **Given** I am on one page with the chat interface open, **When** I navigate to another page, **Then** the chat interface remains open with my conversation intact
6. **Given** I am on a mobile device, **When** I view any authenticated page, **Then** the floating icon is positioned appropriately for mobile screens and does not obstruct important content

---

### User Story 4 - Handle Errors Gracefully (Priority: P3)

As a user, I want to see clear error messages when something goes wrong so that I understand what happened and can take appropriate action.

**Why this priority**: Error handling is important for user experience but not critical for MVP. Users can still accomplish their goals even with basic error handling. This priority ensures the core functionality works first, then adds polish.

**Independent Test**: Can be tested by simulating network failures, invalid tokens, or backend errors, and verifying that appropriate error messages appear. Delivers value by preventing user confusion when issues occur.

**Acceptance Scenarios**:

1. **Given** I am not logged in, **When** I try to access the chat page, **Then** I am redirected to the login page
2. **Given** I am on the chat page and my JWT expires, **When** I try to send a message, **Then** I see an error message indicating I need to log in again
3. **Given** I am on the chat page and the backend is unavailable, **When** I send a message, **Then** I see an error message like "Unable to connect to chat service. Please try again."
4. **Given** I send a message and the backend returns an error, **When** the error response arrives, **Then** I see a user-friendly error message (not technical details)
5. **Given** I am on the chat page and my network connection is lost, **When** I try to send a message, **Then** I see an error message indicating network connectivity issues

---

### Edge Cases

- What happens when the user sends an empty message? (System should prevent sending or show validation error)
- What happens when the user sends a very long message (>10,000 characters)? (System should either truncate or show character limit)
- What happens when the backend response takes longer than 30 seconds? (System should show timeout error)
- What happens when the user rapidly sends multiple messages? (System should queue them or disable send button until response received)
- What happens when the JWT token is missing or malformed? (System should redirect to login)
- What happens when the user navigates away while waiting for a response? (System should cancel the request or handle gracefully on return)
- What happens when the floating launcher icon overlaps with page content? (System should ensure proper z-index and positioning to avoid obstruction)
- What happens when the user clicks the floating icon while the chat is already open? (System should either do nothing or toggle close)
- What happens when the user opens the chat on one page and navigates to another? (Chat should remain open with conversation intact)
- What happens when the user minimizes the chat and then navigates to a different page? (Icon should remain minimized until clicked again)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST integrate OpenAI ChatKit UI library for the chat interface
- **FR-002**: System MUST display a text input field where users can type messages
- **FR-003**: System MUST display a send button to submit messages
- **FR-004**: System MUST send all messages to POST /api/chat endpoint (user_id extracted from JWT by backend)
- **FR-005**: System MUST automatically attach JWT token to all chat API requests via Authorization header
- **FR-006**: System MUST display user messages and assistant messages in the chat interface with clear visual distinction
- **FR-007**: System MUST show a loading indicator while waiting for assistant responses
- **FR-008**: System MUST display error messages when chat requests fail
- **FR-009**: System MUST redirect unauthenticated users to the login page
- **FR-010**: System MUST load and display conversation history when the chat page loads
- **FR-011**: System MUST automatically scroll to the latest message when new messages arrive
- **FR-012**: System MUST clear the input field after a message is sent
- **FR-013**: System MUST support OpenAI domain allowlist configuration via NEXT_PUBLIC_OPENAI_DOMAIN_KEY environment variable
- **FR-014**: System MUST use NEXT_PUBLIC_API_BASE_URL environment variable for the chat API endpoint
- **FR-015**: System MUST work in both local development and production environments
- **FR-016**: System MUST display messages in chronological order (oldest first, newest last)
- **FR-017**: System MUST prevent sending empty messages
- **FR-018**: System MUST handle streaming or progressive responses if supported by ChatKit
- **FR-019**: System MUST display a floating chatbot launcher icon fixed at the bottom-right corner of all authenticated pages
- **FR-020**: System MUST position the floating icon with appropriate spacing from screen edges (e.g., 20-30px from bottom and right)
- **FR-021**: System MUST ensure the floating icon has a high z-index to appear above other page content
- **FR-022**: System MUST open the chat interface (modal or slide-in panel) when the floating icon is clicked
- **FR-023**: System MUST provide a close button in the chat interface to dismiss it and return to the floating icon
- **FR-024**: System MUST provide a minimize button in the chat interface to collapse it back to the floating icon
- **FR-025**: System MUST persist the chat interface state (open/closed) across page navigations within the same session
- **FR-026**: System MUST ensure the floating icon is responsive and appropriately positioned on mobile devices
- **FR-027**: System MUST ensure the floating icon does not obstruct important page content or interactive elements
- **FR-028**: System MUST maintain conversation context when the chat interface is reopened after being closed or minimized

### Key Entities *(include if feature involves data)*

- **Chat Message**: Represents a single message in the conversation
  - Role: Either "user" (sent by the user) or "assistant" (sent by the AI)
  - Content: The text content of the message
  - Timestamp: When the message was sent/received
  - Status: Pending, sent, delivered, or error

- **Conversation**: Represents the chat session
  - Messages: Collection of chat messages in chronological order
  - User: The authenticated user (identified by JWT)
  - Status: Active, loading, or error state

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can send a message and receive a response in under 5 seconds (95th percentile)
- **SC-002**: Users can successfully complete a todo management task (add, list, complete, delete) via chat on their first attempt with 90% success rate
- **SC-003**: Chat interface loads and displays conversation history in under 2 seconds
- **SC-004**: Error messages appear within 1 second of a failure occurring
- **SC-005**: Users can send at least 50 messages in a single conversation without performance degradation
- **SC-006**: Chat interface works correctly on desktop browsers (Chrome, Firefox, Safari, Edge) and mobile browsers (iOS Safari, Android Chrome)
- **SC-007**: JWT authentication prevents unauthorized access 100% of the time (all unauthenticated requests redirect to login)
- **SC-008**: Chat interface maintains conversation context across page refreshes (100% of messages preserved)
- **SC-009**: Users can distinguish between their messages and assistant messages at a glance (verified through user testing)
- **SC-010**: System handles network errors gracefully with clear error messages (no technical jargon or stack traces visible to users)
- **SC-011**: Floating chatbot launcher icon is visible on 100% of authenticated pages within 500ms of page load
- **SC-012**: Chat interface opens within 300ms of clicking the floating launcher icon (95th percentile)
- **SC-013**: Chat interface state (open/closed/minimized) persists correctly across page navigations 100% of the time
- **SC-014**: Floating icon does not obstruct critical page content or interactive elements (verified through user testing on multiple page types)
- **SC-015**: Floating icon is appropriately positioned and functional on mobile devices (iOS Safari, Android Chrome) with screen sizes down to 375px width

## Non-Functional Requirements *(optional)*

### Performance

- Chat interface must render initial view in under 1 second
- Message send/receive latency must be under 5 seconds (95th percentile)
- Conversation history with 100+ messages must load in under 3 seconds
- UI must remain responsive during message sending (no blocking operations)

### Security

- JWT tokens must be transmitted securely (HTTPS only in production)
- JWT tokens must not be exposed in URLs or logs
- Chat API requests must include proper CORS headers
- User messages must not be stored in browser localStorage (only in backend database)

### Usability

- Chat interface must be intuitive for non-technical users
- Error messages must be clear and actionable (no technical jargon)
- Visual distinction between user and assistant messages must be immediately obvious
- Loading states must provide clear feedback that the system is working
- Floating chatbot launcher icon must be easily discoverable and recognizable as a chat trigger
- Floating icon must not interfere with user's ability to interact with page content
- Chat interface open/close/minimize actions must provide immediate visual feedback
- Floating icon must have appropriate hover states to indicate interactivity

### Compatibility

- Must work on modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- Must work on mobile browsers (iOS Safari 14+, Android Chrome 90+)
- Must support responsive design (desktop, tablet, mobile)
- Must work with OpenAI ChatKit library (official version)

## Assumptions *(optional)*

1. **Backend API exists**: We assume the POST /api/chat endpoint is already implemented or will be implemented in parallel
2. **JWT authentication works**: We assume Better Auth JWT authentication from Phase-2 is fully functional
3. **OpenAI ChatKit compatibility**: We assume OpenAI ChatKit library is compatible with Next.js 16+ and React 19+
4. **Conversation persistence**: We assume the backend handles conversation persistence (frontend only displays what backend provides)
5. **Single conversation per user**: We assume each user has one active conversation (no conversation switching in this phase)
6. **Text-only messages**: We assume messages are text-only (no images, files, or rich media in this phase)
7. **No real-time updates**: We assume no WebSocket or real-time updates (polling or manual refresh only)
8. **Standard HTTP/REST**: We assume standard HTTP POST requests (no GraphQL or other protocols)

## Dependencies *(optional)*

### External Dependencies

- **OpenAI ChatKit**: Official UI library for chat interfaces (must be installed via npm)
- **Better Auth**: Existing Phase-2 authentication system (provides JWT tokens)
- **Next.js 16+**: Existing Phase-2 frontend framework
- **React 19+**: Existing Phase-2 UI library

### Internal Dependencies

- **Phase-2 Authentication**: Must be complete and functional (JWT issuance, storage, verification)
- **Phase-2 Frontend**: Must have working Next.js setup, routing, and API client infrastructure
- **Phase-3 Backend Chat API**: POST /api/chat endpoint must be implemented (can be developed in parallel)

### Environment Variables

- **NEXT_PUBLIC_API_BASE_URL**: Base URL for the backend API (e.g., http://localhost:8000 or https://api.production.com)
- **NEXT_PUBLIC_OPENAI_DOMAIN_KEY**: OpenAI domain allowlist key for ChatKit (required for production deployment)

## Out of Scope *(optional)*

The following are explicitly NOT part of this specification:

- **Backend implementation**: Chat endpoint, agent logic, MCP server, database models
- **AI logic**: OpenAI Agents SDK integration, intent analysis, tool selection
- **MCP tools**: Task CRUD operations (add_task, list_tasks, etc.)
- **Conversation persistence**: Database storage of messages (handled by backend)
- **Multi-conversation support**: Switching between different conversations
- **Rich media**: Images, files, voice messages, or other non-text content
- **Real-time updates**: WebSocket connections, server-sent events, or live updates
- **Conversation branching**: Editing previous messages or creating alternate conversation paths
- **Export/import**: Downloading or uploading conversation history
- **Search**: Searching within conversation history
- **Conversation management**: Deleting, archiving, or organizing conversations
- **User preferences**: Customizing chat appearance, notification settings, etc.
- **Analytics**: Tracking user behavior, message metrics, or usage statistics

## Technical Constraints *(optional)*

1. **Frontend-only scope**: This specification covers ONLY the frontend chat UI. All backend logic is out of scope.
2. **OpenAI ChatKit required**: Must use the official OpenAI ChatKit library (no custom chat UI implementations)
3. **JWT-only authentication**: Must use existing Better Auth JWT tokens (no new authentication mechanisms)
4. **Single endpoint**: Must communicate exclusively with POST /api/chat (no direct access to task APIs)
5. **Stateless frontend**: Frontend must not maintain conversation state (all state comes from backend)
6. **No WebSockets**: Must use standard HTTP requests (no real-time protocols)
7. **Next.js App Router**: Must integrate with existing Next.js 16+ App Router architecture
8. **TypeScript strict mode**: Must follow existing Phase-2 TypeScript strict mode requirements
9. **Tailwind CSS**: Must use existing Tailwind CSS for any custom styling
10. **Production-ready**: Must meet Phase-2 production standards (no placeholder logic, no mock data)

## Risks & Mitigations *(optional)*

### Risk 1: OpenAI ChatKit Compatibility
**Risk**: OpenAI ChatKit may not be compatible with Next.js 16+ or React 19+
**Impact**: High - Would require finding alternative chat UI library or downgrading Next.js/React
**Mitigation**: Test ChatKit integration early in development. Have fallback plan to build custom chat UI if needed.

### Risk 2: JWT Token Expiration
**Risk**: JWT tokens may expire during long chat sessions, causing authentication failures
**Impact**: Medium - Users would see errors and need to re-login
**Mitigation**: Implement token refresh logic or graceful error handling with clear "please log in again" message.

### Risk 3: Backend API Not Ready
**Risk**: Backend chat API may not be implemented when frontend is ready
**Impact**: Medium - Frontend cannot be fully tested or deployed
**Mitigation**: Define clear API contract early. Use mock responses for frontend development. Coordinate with backend team on timeline.

### Risk 4: Performance with Long Conversations
**Risk**: Rendering 100+ messages may cause performance issues
**Impact**: Low - Most conversations will be shorter, but edge case exists
**Mitigation**: Implement virtual scrolling or pagination if performance issues arise. Test with large conversation datasets.

### Risk 5: OpenAI Domain Allowlist Configuration
**Risk**: Domain allowlist configuration may be complex or poorly documented
**Impact**: Low - May delay production deployment
**Mitigation**: Research OpenAI domain allowlist requirements early. Test in staging environment before production.

### Risk 6: Floating Icon Z-Index Conflicts
**Risk**: Floating chatbot launcher icon may conflict with existing page elements (modals, dropdowns, tooltips) due to z-index stacking issues
**Impact**: Medium - Icon may be hidden behind other elements or may obstruct critical UI components
**Mitigation**: Establish clear z-index hierarchy in design system. Test floating icon on all authenticated pages. Use high but reasonable z-index value (e.g., 1000-9999) that doesn't conflict with modals (typically 10000+).

## Open Questions *(optional)*

None - All requirements are clear based on the provided context and Phase-2 foundation.
