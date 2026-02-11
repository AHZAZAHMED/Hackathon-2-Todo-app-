# Implementation Plan: ChatKit Frontend Integration

**Branch**: `001-chatkit-frontend` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-chatkit-frontend/spec.md`

## Summary

Implement a frontend-only chatbot interface using OpenAI ChatKit that provides authenticated users with a floating chat icon and window to interact with an AI assistant. The chat window opens above the icon (400px × 600px), sends messages to POST /api/chat with JWT authentication, and includes features like message length limits (500 chars), retry mechanism for failed messages, conversation preservation on token expiry, and state persistence across page navigations. This is a pure frontend implementation that integrates with existing Phase-2 authentication and does not include backend, MCP, or AI agent logic.

## Technical Context

**Language/Version**: TypeScript 5.x (Next.js 16+ App Router)
**Primary Dependencies**:
- OpenAI ChatKit (official UI library)
- Next.js 16+ (existing Phase-2)
- React 18+ (existing Phase-2)
- Tailwind CSS (existing Phase-2)
- Better Auth JWT (existing Phase-2)

**Storage**: Session storage for chat state persistence (window open/closed, conversation messages on token expiry)
**Testing**: Playwright (browsing-with-playwright skill for UI validation)
**Target Platform**: Modern web browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
**Project Type**: Web application (frontend-only feature)
**Performance Goals**:
- Chat window open/close < 300ms
- Message rendering < 100ms (for messages under 500 chars)
- Character counter real-time updates without lag
- Instant UI response (< 1 second) for icon click

**Constraints**:
- Frontend-only scope (no backend, MCP, or agent implementation)
- Must not break existing Phase-2 functionality
- Desktop-first (1366x768 minimum resolution)
- Single ephemeral conversation per session
- 500 character message limit
- Must integrate with existing Better Auth JWT system

**Scale/Scope**:
- Single user per browser session
- Ephemeral conversation (no persistence beyond session storage)
- 4 user stories (P1-P4)
- 24 functional requirements
- 10 success criteria

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase-2 Principles (Applicable to Frontend Feature)

✅ **Spec-First Development**: Specification approved, clarifications resolved (5 questions), ready for planning
✅ **JWT-Only Identity**: Will use existing Better Auth JWT from Phase-2, attach automatically to chat requests
✅ **Production-Grade Quality**: TypeScript strict mode, Tailwind CSS official config, environment variables, error handling
✅ **Root-Cause Engineering**: No patch fixes, address root causes only
✅ **Clear Separation of Layers**: Frontend-only scope, no cross-layer bleeding, API contract defined (POST /api/chat)

### Phase-3 Principles (Not Applicable - Frontend Only)

⚠️ **Stateless Backend Architecture**: N/A - This spec is frontend-only
⚠️ **MCP-Only Task Mutations**: N/A - This spec is frontend-only
⚠️ **AI Agent Orchestration**: N/A - This spec is frontend-only

### Frontend-Specific Gates

✅ **No Phase-2 Disruption**: FR-012 requires preserving existing Phase-2 functionality (dashboard, task management, authentication)
✅ **Centralized API Client**: Will use existing `lib/api-client.ts` for JWT attachment
✅ **Environment Variables**: NEXT_PUBLIC_API_BASE_URL, NEXT_PUBLIC_OPENAI_DOMAIN_KEY
✅ **TypeScript Strict Mode**: Existing Phase-2 configuration
✅ **Tailwind CSS**: Existing Phase-2 configuration

### Quality Gates (From Spec)

- [ ] Chat window opens in < 1 second (SC-001)
- [ ] Chat icon visible on 100% of pages (SC-002)
- [ ] Proper dimensions and positioning (SC-003)
- [ ] Messages reach /api/chat with JWT (SC-004)
- [ ] Message send/receive within 5 seconds (SC-005)
- [ ] User-friendly error messages (SC-006)
- [ ] Playwright validation passes (SC-007)
- [ ] Phase-2 regression tests pass (SC-008)
- [ ] No UI degradation on reopen (SC-009)
- [ ] No blank screens (SC-010)

**Gate Status**: ✅ PASS - All applicable constitution principles satisfied for frontend-only scope

## Project Structure

### Documentation (this feature)

```text
specs/001-chatkit-frontend/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (to be generated)
├── contracts/           # Phase 1 output (to be generated)
│   └── chat-api.md      # POST /api/chat contract
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── app/
│   ├── layout.tsx                    # Root layout (existing - will add ChatProvider)
│   ├── dashboard/                    # Existing Phase-2
│   ├── settings/                     # Existing Phase-2
│   └── profile/                      # Existing Phase-2
├── components/
│   ├── chat/                         # NEW: Chat components
│   │   ├── ChatIcon.tsx              # Floating chat icon (bottom-right, 20px offset)
│   │   ├── ChatWindow.tsx            # Chat window container (400px × 600px)
│   │   ├── ChatMessages.tsx          # Message list with user/assistant distinction
│   │   ├── ChatInput.tsx             # Message input with 500-char limit and counter
│   │   ├── ChatMessage.tsx           # Individual message component
│   │   ├── ChatRetryButton.tsx       # Retry button for failed messages
│   │   └── ChatProvider.tsx          # Context provider for chat state
│   ├── dashboard/                    # Existing Phase-2
│   └── ...
├── lib/
│   ├── api-client.ts                 # Existing Phase-2 (JWT attachment)
│   ├── chat-client.ts                # NEW: Chat API client (POST /api/chat)
│   ├── chat-storage.ts               # NEW: Session storage utilities
│   └── ...
├── hooks/
│   ├── useChat.ts                    # NEW: Chat state management hook
│   ├── useChatAuth.ts                # NEW: Chat authentication hook
│   └── ...
├── types/
│   ├── chat.ts                       # NEW: Chat message, session types
│   └── ...
└── styles/
    └── globals.css                   # Existing Phase-2 (Tailwind)

backend/
└── [No changes - backend out of scope]
```

**Structure Decision**: Web application structure (Option 2). This feature adds new components to the existing `frontend/` directory without modifying backend. All new files are isolated in `components/chat/`, `lib/chat-*.ts`, and `hooks/useChat*.ts` to minimize impact on Phase-2 code.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. This frontend-only feature aligns with all applicable constitution principles.

## Phase 0: Research & Technology Decisions

### Research Questions

1. **OpenAI ChatKit Integration**: How to integrate OpenAI ChatKit with Next.js 16+ App Router and configure custom API endpoints?
2. **Session Storage Strategy**: Best practices for persisting chat state (window open/closed, messages on token expiry) across page navigations in Next.js App Router?
3. **JWT Extraction**: How to access Better Auth JWT token from existing Phase-2 authentication system in client components?
4. **Error Handling Patterns**: Best practices for displaying user-friendly error messages and retry mechanisms in chat interfaces?
5. **Z-Index Management**: How to ensure chat window appears above all page content without breaking existing layouts?

### Technology Decisions (From Spec)

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| OpenAI ChatKit | Official UI library from OpenAI, designed for chat interfaces, supports custom API endpoints | Custom chat UI (more work, reinventing wheel), react-chat-elements (less official support) |
| Session Storage | Persists across page navigations within same session, cleared on browser close, appropriate for ephemeral chat | Local Storage (persists too long for ephemeral chat), In-memory state (lost on navigation), Cookies (size limits) |
| Tailwind CSS | Existing Phase-2 configuration, consistent styling | Inline styles (harder to maintain), CSS modules (inconsistent with Phase-2) |
| TypeScript Strict Mode | Existing Phase-2 configuration, type safety | JavaScript (no type safety), TypeScript loose mode (less safe) |
| Playwright | Specified in FR-009, browsing-with-playwright skill available | Jest + React Testing Library (doesn't test real browser), Cypress (not specified) |

## Phase 1: Design Artifacts

### Data Model

See [data-model.md](./data-model.md) for complete entity definitions.

**Key Entities** (Frontend-only, ephemeral):

- **ChatMessage**: Single message in conversation
  - `id`: string (UUID)
  - `role`: "user" | "assistant"
  - `content`: string (max 500 chars)
  - `timestamp`: Date
  - `status`: "sending" | "sent" | "failed"
  - `error`: string | null

- **ChatSession**: Current chat interaction
  - `messages`: ChatMessage[]
  - `isOpen`: boolean
  - `isLoading`: boolean
  - `error`: string | null

### API Contracts

See [contracts/chat-api.md](./contracts/chat-api.md) for complete API specification.

**POST /api/chat**:
- Request: `{ message: string }` + Authorization header
- Response: `{ response: string }` or error
- Headers: `Authorization: Bearer <JWT>`

### Implementation Phases

#### Phase 1.1: Setup & Dependencies

**Tasks**:
1. Install OpenAI ChatKit: `npm install @openai/chatkit` (package name TBD)
2. Add environment variables to `.env.local`:
   - `NEXT_PUBLIC_API_BASE_URL`
   - `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`
3. Create type definitions in `types/chat.ts`

**Acceptance**:
- ChatKit installed without errors
- Environment variables accessible in client components
- TypeScript types compile without errors

#### Phase 1.2: Chat State Management

**Tasks**:
1. Create `lib/chat-storage.ts` for session storage utilities
2. Create `hooks/useChat.ts` for chat state management
3. Create `hooks/useChatAuth.ts` for JWT extraction
4. Create `components/chat/ChatProvider.tsx` for context

**Acceptance**:
- Session storage persists chat state across page navigations
- JWT token extracted from Better Auth
- Chat state accessible via context

#### Phase 1.3: Chat UI Components

**Tasks**:
1. Create `components/chat/ChatIcon.tsx` (floating icon, bottom-right, 20px offset)
2. Create `components/chat/ChatWindow.tsx` (400px × 600px, above icon)
3. Create `components/chat/ChatMessages.tsx` (message list, scrollable)
4. Create `components/chat/ChatMessage.tsx` (individual message, user/assistant distinction)
5. Create `components/chat/ChatInput.tsx` (500-char limit, counter, send button)
6. Create `components/chat/ChatRetryButton.tsx` (retry failed messages)

**Acceptance**:
- Chat icon visible in bottom-right corner (20px from edges)
- Chat window opens above icon with correct dimensions
- Messages display with proper styling
- Character counter updates in real-time
- Retry button appears on failed messages

#### Phase 1.4: Chat API Integration

**Tasks**:
1. Create `lib/chat-client.ts` for POST /api/chat requests
2. Integrate JWT attachment via existing `lib/api-client.ts`
3. Implement message sending logic
4. Implement error handling and retry mechanism
5. Implement loading states

**Acceptance**:
- Messages sent to POST /api/chat with JWT
- Loading indicator displays while waiting for response
- Error messages display user-friendly text
- Retry button resends failed messages

#### Phase 1.5: Authentication Integration

**Tasks**:
1. Add ChatProvider to root layout (`app/layout.tsx`)
2. Implement unauthenticated user redirect to login
3. Implement post-login return to original page with chat auto-open
4. Implement token expiry detection and conversation preservation

**Acceptance**:
- Unauthenticated users redirected to login on icon click
- Users returned to original page after login with chat open
- Conversation preserved in session storage on token expiry
- Conversation restored after re-authentication

#### Phase 1.6: State Persistence

**Tasks**:
1. Implement chat window state persistence (open/closed) across navigations
2. Implement conversation preservation on token expiry
3. Test state persistence across multiple page navigations

**Acceptance**:
- Chat window state persists across page navigations
- Conversation messages preserved on token expiry
- State restored correctly after navigation

#### Phase 1.7: Styling & Polish

**Tasks**:
1. Apply Tailwind CSS styling to all chat components
2. Implement z-index management (chat above page content)
3. Implement mobile responsive sizing (adapt to small screens)
4. Implement scrollable message panel
5. Ensure chat icon never covered by window

**Acceptance**:
- Chat components styled consistently with Phase-2
- Chat window appears above all page content
- Chat adapts to smaller screens
- Message panel scrolls when content overflows
- Chat icon always visible

#### Phase 1.8: Playwright Validation

**Tasks**:
1. Write Playwright test: Icon visibility
2. Write Playwright test: Window open/close
3. Write Playwright test: Message send
4. Write Playwright test: JWT attachment
5. Write Playwright test: Error handling
6. Write Playwright test: Phase-2 regression

**Acceptance**:
- All Playwright tests pass
- Icon visible on all pages
- Window opens/closes correctly
- Messages sent with JWT
- Errors display correctly
- Phase-2 functionality unaffected

### Quickstart Guide

See [quickstart.md](./quickstart.md) for developer setup instructions.

**Quick Setup**:
1. Install dependencies: `npm install`
2. Configure environment variables in `.env.local`
3. Run development server: `npm run dev`
4. Navigate to any page and click chat icon
5. Send test message to verify integration

## Phase 2: Task Breakdown

**Note**: Task breakdown will be generated by `/sp.tasks` command after this plan is approved.

Tasks will be organized by user story:
- **US1 (P1)**: Access Chat Interface (icon, window, open/close)
- **US2 (P2)**: Send Messages (input, send, receive, display)
- **US3 (P3)**: Secure Communication (JWT, auth, redirect)
- **US4 (P4)**: Optimal UI Experience (positioning, sizing, styling)

Each task will include:
- Specific file paths
- Acceptance criteria
- Dependencies
- Parallel execution opportunities

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenAI ChatKit package name unknown | High | Research during Phase 0, check OpenAI docs, fallback to custom UI if needed |
| ChatKit incompatible with Next.js App Router | High | Test integration early, use client components, fallback to custom UI if needed |
| JWT extraction from Better Auth complex | Medium | Review Phase-2 auth implementation, use existing API client patterns |
| Session storage cleared unexpectedly | Medium | Document behavior, add user messaging, consider local storage fallback |
| Chat window breaks existing layouts | Medium | Use fixed positioning, high z-index, test on all Phase-2 pages |
| Backend /api/chat not implemented | Low | Use mock responses during development, coordinate with backend team |

## Success Criteria Mapping

| Success Criterion | Implementation Phase | Validation Method |
|-------------------|---------------------|-------------------|
| SC-001: Open < 1 second | Phase 1.3 (Chat UI) | Playwright performance test |
| SC-002: Icon on 100% pages | Phase 1.3 (Chat UI) | Playwright visibility test on all routes |
| SC-003: Proper dimensions | Phase 1.3 (Chat UI) | Playwright dimension assertions |
| SC-004: JWT attached | Phase 1.4 (API Integration) | Playwright network interception |
| SC-005: Send/receive < 5s | Phase 1.4 (API Integration) | Playwright timing assertions |
| SC-006: User-friendly errors | Phase 1.4 (API Integration) | Playwright error scenario tests |
| SC-007: Playwright passes | Phase 1.8 (Validation) | Run all Playwright tests |
| SC-008: Phase-2 regression | Phase 1.8 (Validation) | Run existing Phase-2 tests |
| SC-009: No degradation | Phase 1.3 (Chat UI) | Playwright repeated open/close test |
| SC-010: No blank screens | Phase 1.3 (Chat UI) | Playwright visual regression test |

## Dependencies & Blockers

### External Dependencies

- **OpenAI ChatKit**: Official package (name TBD during research)
- **Better Auth JWT**: Existing Phase-2 implementation
- **Centralized API Client**: Existing Phase-2 `lib/api-client.ts`

### Internal Dependencies

- **Phase-2 Frontend**: Next.js 16+, TypeScript, Tailwind CSS (existing)
- **Phase-2 Authentication**: Better Auth JWT system (existing)
- **Backend /api/chat**: Will be implemented in separate spec (can use mocks during development)

### Blocking Dependencies

None - This feature can be implemented independently with mock backend responses.

## Next Steps

1. **Approve this plan**: Review and approve implementation approach
2. **Run `/sp.tasks`**: Generate detailed task breakdown organized by user story
3. **Phase 0 Research**: Resolve OpenAI ChatKit package name and integration patterns
4. **Phase 1 Implementation**: Execute tasks in order (1.1 → 1.8)
5. **Playwright Validation**: Run browsing-with-playwright skill to verify all requirements
6. **Phase-2 Regression**: Ensure existing functionality unaffected

**Estimated Complexity**: Medium (frontend-only, well-defined scope, existing infrastructure)

**Ready for `/sp.tasks`**: ✅ Yes - Plan complete, all unknowns identified for research phase
