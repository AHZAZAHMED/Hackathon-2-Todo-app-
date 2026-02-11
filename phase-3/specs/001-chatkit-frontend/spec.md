# Feature Specification: ChatKit Frontend Integration

**Feature Branch**: `001-chatkit-frontend`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "Phase-3 Spec-1 — ChatKit Frontend Integration - Frontend chatbot interface using OpenAI ChatKit with floating chat icon and properly sized chat window for authenticated users to send messages to POST /api/chat endpoint"

## Clarifications

### Session 2026-02-09

- Q: Should unauthenticated users see a login modal overlay or be redirected to the login page? → A: Redirect to existing login page, then return to original page with chat opened
- Q: Should there be a maximum message length, and if so, what should it be? → A: 500 characters maximum with visible character counter
- Q: Should the conversation messages be preserved when JWT expires and user re-authenticates? → A: Preserve conversation in session storage and restore after re-login
- Q: How should users retry failed messages? → A: Display failed message in conversation with error indicator and "Retry" button next to it
- Q: Should the chat icon be positioned in a specific location, or is there flexibility? → A: Bottom-right corner (fixed) - 20px from bottom, 20px from right

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Access Chat Interface (Priority: P1)

As an authenticated user, I want to see a floating chat icon on every page and click it to open a chat window, so I can interact with the AI assistant without navigating away from my current task.

**Why this priority**: This is the entry point for all chatbot functionality. Without the ability to open the chat interface, no other features are accessible. This represents the minimum viable product.

**Independent Test**: Can be fully tested by logging in, navigating to any page, clicking the chat icon, and verifying the chat window opens with proper positioning and sizing. Delivers immediate value by providing access to AI assistance.

**Acceptance Scenarios**:

1. **Given** I am logged in and on the dashboard page, **When** I look at the page, **Then** I see a floating chat icon in the bottom-right corner (20px from bottom, 20px from right edge)
2. **Given** I see the chat icon, **When** I click on it, **Then** a chat window opens above the icon with dimensions approximately 400px wide by 600px tall
3. **Given** the chat window is open, **When** I look at the interface, **Then** I see a close button, message input field, and empty conversation area
4. **Given** the chat window is open, **When** I click the close button, **Then** the chat window closes and the chat icon remains visible
5. **Given** I am on any page (dashboard, settings, profile), **When** I look for the chat icon, **Then** it is consistently visible in the bottom-right corner (20px from bottom, 20px from right edge)

---

### User Story 2 - Send Messages to AI Assistant (Priority: P2)

As an authenticated user, I want to type messages in the chat window and receive AI responses, so I can get help with my tasks through natural conversation.

**Why this priority**: This is the core functionality that delivers value. Once users can open the chat (P1), they need to be able to communicate with the AI assistant. This builds on P1 to create a functional chatbot experience.

**Independent Test**: Can be tested by opening the chat window, typing a message, sending it, and verifying the message appears in the conversation and a response is received from the backend. Delivers value by enabling AI-assisted task management.

**Acceptance Scenarios**:

1. **Given** the chat window is open, **When** I type "Hello" in the message input field and press Enter (or click Send), **Then** my message appears in the conversation area with a "user" indicator
2. **Given** I have sent a message, **When** the backend processes the request, **Then** I see a loading indicator while waiting for the response
3. **Given** the backend returns a response, **When** the response is received, **Then** the AI assistant's message appears in the conversation area with an "assistant" indicator
4. **Given** I have an ongoing conversation, **When** I send multiple messages, **Then** all messages appear in chronological order with proper visual distinction between user and assistant messages
5. **Given** I send a message, **When** the request is made, **Then** the message is sent to POST /api/chat endpoint (not any other endpoint)

---

### User Story 3 - Secure Communication (Priority: P3)

As an authenticated user, I want my chat requests to be automatically secured with my authentication token, so my conversations are private and associated with my account.

**Why this priority**: Security is critical but builds on the communication functionality (P2). Users need to be able to send messages before security becomes relevant. This ensures user isolation and data privacy.

**Independent Test**: Can be tested by inspecting network requests when sending messages and verifying the JWT token is present in the Authorization header. Delivers value by ensuring secure, user-specific conversations.

**Acceptance Scenarios**:

1. **Given** I am logged in with a valid JWT token, **When** I send a chat message, **Then** the request includes the JWT token in the Authorization header
2. **Given** my JWT token is invalid or expired, **When** I try to send a message, **Then** I see an error message indicating I need to log in again
3. **Given** I am not logged in, **When** I see the page, **Then** the chat icon is visible
4. **Given** I am not logged in and see the chat icon, **When** I click on it, **Then** I am redirected to the login page
5. **Given** I am redirected to login after clicking the chat icon, **When** I successfully log in, **Then** I am returned to the page where I clicked the chat icon and the chat window opens automatically

---

### User Story 4 - Optimal UI Experience (Priority: P4)

As a user, I want the chat interface to be well-positioned, properly sized, and non-intrusive, so I can use it comfortably without it interfering with my main tasks.

**Why this priority**: This enhances the user experience but is not critical for basic functionality. Users can interact with a poorly positioned chat window, but a well-designed UI improves satisfaction and adoption.

**Independent Test**: Can be tested by opening the chat on different pages and screen sizes, verifying positioning, sizing, and that it doesn't break existing layouts. Delivers value through improved usability and user satisfaction.

**Acceptance Scenarios**:

1. **Given** the chat window is open, **When** I look at its position, **Then** it appears above the chat icon and does not cover the icon itself
2. **Given** the chat window is open, **When** I look at its size, **Then** it has a reasonable width (approximately 400px) and height (approximately 600px) that fits on standard screens
3. **Given** the chat window is open, **When** I interact with the rest of the page, **Then** the existing page layout is not broken or obscured
4. **Given** the chat window is open, **When** I scroll the page, **Then** the chat window remains in a fixed position (does not scroll with content)
5. **Given** the chat window is open, **When** I view it, **Then** I never see a blank black or white screen - the UI always renders properly
6. **Given** the chat window is open, **When** I look at the interface, **Then** it never opens in fullscreen mode - it remains a floating window

---

### Edge Cases

- **What happens when the backend /api/chat endpoint is unreachable?** The chat UI should display a user-friendly error message (e.g., "Unable to connect to chat service. Please try again later.") instead of crashing or showing technical errors.
- **What happens when a message send fails due to network issues?** The failed message should be displayed in the conversation area with a clear error indicator (e.g., red border or error icon) and a "Retry" button next to it. When the user clicks the retry button, the system should attempt to resend the same message.
- **What happens when the JWT token expires during an active chat session?** The UI should detect the 401 response and redirect the user to log in again. The conversation messages should be preserved in session storage and automatically restored after successful re-authentication, allowing the user to continue their conversation seamlessly.
- **What happens when the user opens multiple browser tabs?** Each tab should have its own independent chat instance (no shared state between tabs).
- **What happens on mobile or small screens?** The chat window should adapt to smaller screens, potentially taking up more screen space but still remaining usable and closable.
- **What happens when the user navigates to a different page while the chat is open?** The system should remember the last state of the chat window. If the chat was open when the user navigated away, it should remain open on the new page. If it was closed, it should remain closed. This state should be preserved using session storage or similar mechanism.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST integrate OpenAI ChatKit UI library into the Next.js frontend
- **FR-002**: System MUST display a floating chat icon on all pages in the bottom-right corner, positioned 20px from the bottom edge and 20px from the right edge
- **FR-003**: System MUST open a chat window above the chat icon when the icon is clicked, with dimensions approximately 400px wide by 600px tall
- **FR-004**: Chat window MUST include a close button that is always accessible and closes the window when clicked
- **FR-005**: System MUST send all chat messages exclusively to the POST /api/chat endpoint (no other endpoints)
- **FR-006**: System MUST automatically attach the Better Auth JWT token to all chat requests via the Authorization header
- **FR-007**: System MUST support the following environment variables:
  - `NEXT_PUBLIC_API_BASE_URL`: Base URL for backend API (e.g., "http://localhost:8000")
  - `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`: OpenAI domain key for ChatKit configuration
- **FR-008**: System MUST display graceful, user-friendly error messages when the backend is unreachable or returns errors (no technical stack traces or blank screens)
- **FR-009**: System MUST be validated using the browsing-with-playwright skill to verify UI rendering, interaction, and message sending
- **FR-010**: Chat icon MUST remain visible when the chat window is open (window does not cover the icon)
- **FR-011**: Chat window MUST never open in fullscreen mode - it must remain a floating window
- **FR-012**: System MUST preserve existing Phase-2 functionality (dashboard, task management, authentication) without breaking layouts or features
- **FR-013**: System MUST display the chat icon to both authenticated and unauthenticated users on all pages
- **FR-014**: System MUST redirect unauthenticated users to the login page when they click the chat icon, preserving the current page URL for return navigation
- **FR-015**: System MUST automatically open the chat window after a user logs in via the chat icon prompt, returning them to the page where they clicked the icon
- **FR-016**: System MUST remember the chat window state (open or closed) across page navigations using session storage or similar mechanism
- **FR-017**: System MUST restore the chat window to its previous state (open or closed) when the user navigates to a different page
- **FR-018**: System MUST enforce a maximum message length of 500 characters for user input
- **FR-019**: System MUST display a visible character counter showing remaining characters as the user types
- **FR-020**: System MUST prevent message submission when the character limit is exceeded
- **FR-021**: System MUST preserve conversation messages in session storage when JWT token expires (401 response)
- **FR-022**: System MUST restore the preserved conversation after successful re-authentication following token expiry
- **FR-023**: System MUST display failed messages in the conversation area with a clear error indicator when message send fails
- **FR-024**: System MUST provide a "Retry" button next to each failed message that allows users to resend the message

### Key Entities *(include if feature involves data)*

- **Chat Message**: Represents a single message in the conversation
  - Content: The text of the message
  - Role: Either "user" (sent by the user) or "assistant" (sent by the AI)
  - Timestamp: When the message was sent (for display purposes)
  - Note: This is a frontend-only representation; backend persistence is out of scope for this spec

- **Chat Session**: Represents the current chat interaction
  - Messages: Array of chat messages in chronological order
  - Loading State: Boolean indicating if waiting for AI response
  - Error State: String containing error message if request fails
  - Note: This is ephemeral frontend state; no persistence required for this spec

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Authenticated users can open the chat window by clicking the chat icon in under 1 second (instant UI response)
- **SC-002**: Chat icon remains visible and accessible on 100% of authenticated pages (dashboard, settings, profile, etc.)
- **SC-003**: Chat window renders with proper dimensions (400px ± 50px wide, 600px ± 100px tall) and positioning (above icon, not covering icon) on standard desktop screens (1920x1080 and 1366x768)
- **SC-004**: Messages successfully reach the POST /api/chat endpoint with JWT token attached in 100% of send attempts (when backend is available)
- **SC-005**: Users can send a message and receive a response within 5 seconds (assuming backend responds within 3 seconds)
- **SC-006**: Error messages are displayed in user-friendly language (no technical jargon or stack traces) when backend is unreachable
- **SC-007**: Playwright validation confirms all UI interactions work correctly (icon click, window open, message send, window close)
- **SC-008**: Existing Phase-2 functionality (task CRUD operations, authentication flows) continues to work without regression (verified through existing tests)
- **SC-009**: Chat window can be closed and reopened multiple times without UI degradation or memory leaks
- **SC-010**: Chat interface renders correctly without blank black/white screens in 100% of test cases

## Non-Functional Requirements *(optional)*

### Performance

- Chat window open/close animations should complete within 300ms for smooth user experience
- Message rendering should be instantaneous (< 100ms) for messages under 500 characters
- Character counter should update in real-time without perceptible lag

### Usability

- Chat icon should be visually distinct and recognizable as a chat/help feature
- Chat window should have clear visual hierarchy (message history, input field, send button)
- User and assistant messages should be visually distinguishable (different colors, alignment, or avatars)

### Compatibility

- Must work in modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- Must be responsive and usable on desktop screens (1366x768 minimum resolution)

## Assumptions *(optional)*

1. **Backend Endpoint Exists**: We assume the POST /api/chat endpoint will be implemented in a separate spec/phase. For this spec, we only need to send requests to it; the endpoint can return mock responses or errors during frontend development.

2. **Better Auth JWT Available**: We assume the Better Auth JWT token is already available in the frontend (from Phase-2 implementation) and can be accessed via the existing centralized API client.

3. **OpenAI ChatKit Compatibility**: We assume OpenAI ChatKit is compatible with Next.js 16+ App Router and can be configured to use custom API endpoints (not OpenAI's default endpoints).

4. **Single Conversation**: For this spec, we assume a single, ephemeral conversation per session. Conversation history persistence and multiple conversation threads are out of scope.

5. **Desktop-First**: We assume the primary use case is desktop browsers. Mobile responsiveness is considered but not the primary focus for this spec.

6. **Authenticated Users Only**: We assume the chat feature is only available to authenticated users. Unauthenticated users will not see the chat icon (or it will be disabled).

## Dependencies *(optional)*

### External Dependencies

- **OpenAI ChatKit**: Official UI library from OpenAI for building chat interfaces
  - Version: Latest stable version compatible with Next.js 16+
  - Installation: `npm install @openai/chatkit` (or similar - exact package name to be confirmed during implementation)

- **Better Auth JWT**: Existing authentication system from Phase-2
  - Dependency: JWT token must be accessible from frontend for attaching to requests

### Internal Dependencies

- **Phase-2 Frontend**: Existing Next.js application with App Router, TypeScript, Tailwind CSS
- **Phase-2 Authentication**: Existing Better Auth integration with JWT token management
- **Centralized API Client**: Existing `lib/api-client.ts` (or similar) that handles JWT attachment

### Blocking Dependencies

- None - This spec can be implemented independently as a frontend-only feature. The backend endpoint can return mock responses during development.

## Out of Scope *(mandatory)*

The following are explicitly **NOT** included in this specification:

1. **Backend Implementation**: POST /api/chat endpoint, FastAPI routes, request handling
2. **AI Agent Logic**: OpenAI Agents SDK integration, intent analysis, tool selection
3. **MCP Tools**: Task management tools (add_task, list_tasks, etc.)
4. **Database Operations**: Conversation persistence, message storage, database schema
5. **Conversation History**: Loading previous conversations, conversation threads, message persistence
6. **Advanced Chat Features**: File attachments, voice input, markdown rendering, code syntax highlighting
7. **Multi-User Chat**: Group conversations, user mentions, presence indicators
8. **Real-Time Updates**: WebSocket connections, streaming responses, live typing indicators
9. **Mobile App**: Native mobile applications (iOS/Android)
10. **Internationalization**: Multi-language support, translations
11. **Accessibility Enhancements**: Screen reader optimization, keyboard navigation (beyond basic functionality)
12. **Analytics**: Usage tracking, conversation analytics, user behavior monitoring

## Security Considerations *(optional)*

- **JWT Token Protection**: JWT tokens must be transmitted securely (HTTPS in production) and never exposed in client-side logs or error messages
- **XSS Prevention**: All user input and AI responses must be properly sanitized before rendering to prevent cross-site scripting attacks
- **CSRF Protection**: Requests to /api/chat should include CSRF tokens if required by the backend (coordinate with backend implementation)
- **Rate Limiting**: Consider implementing client-side rate limiting to prevent abuse (e.g., max 10 messages per minute)

## Open Questions *(optional)*

1. **OpenAI ChatKit Package Name**: What is the exact npm package name for OpenAI ChatKit? (To be confirmed during implementation)

**Resolved Questions**:

1. ~~**Unauthenticated User Behavior**~~: **RESOLVED** - Show chat icon but prompt login when clicked (Option B)
2. ~~**Cross-Page Chat Persistence**~~: **RESOLVED** - Remember last state using session storage (Option C)

## Validation Plan *(optional)*

### Manual Testing

1. **Visual Inspection**: Verify chat icon and window render correctly on all pages
2. **Interaction Testing**: Click icon, send messages, close window, reopen - verify all interactions work
3. **Error Testing**: Disconnect backend, verify error messages display correctly
4. **Cross-Browser Testing**: Test in Chrome, Firefox, Safari, Edge

### Automated Testing (Playwright)

1. **Icon Visibility Test**: Navigate to dashboard, verify chat icon is present
2. **Window Open/Close Test**: Click icon, verify window opens, click close, verify window closes
3. **Message Send Test**: Open chat, type message, send, verify message appears in conversation
4. **JWT Attachment Test**: Intercept network request, verify Authorization header contains JWT
5. **Error Handling Test**: Mock backend failure, verify error message displays

### Integration Testing

1. **Phase-2 Regression Test**: Run existing Phase-2 tests to ensure no functionality is broken
2. **End-to-End Flow**: Login → Open chat → Send message → Receive response → Close chat → Logout

## Success Metrics *(optional)*

- **Implementation Success**: All 10 success criteria (SC-001 through SC-010) pass validation
- **Quality Gate**: Playwright validation passes with 100% test success rate
- **Regression Gate**: All existing Phase-2 tests continue to pass
- **User Acceptance**: Chat interface is usable and meets the 4 user stories (P1-P4)
