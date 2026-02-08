# Phase 0 Research: Phase-3 Chatbot Frontend

**Date**: 2026-02-08
**Feature**: 004-chatbot-frontend
**Status**: Complete

## Executive Summary

Phase 0 research confirms that OpenAI ChatKit is available and suitable for the Phase-3 chatbot frontend implementation. This document provides implementation guidance and best practices for integrating ChatKit with the existing Phase-2 Next.js architecture.

## Research Findings

### 1. OpenAI ChatKit Investigation

**Research Question**: How to integrate OpenAI ChatKit with Next.js 16+ and React 19+?

**Finding**: ✅ **OpenAI ChatKit is available**

**Documentation**: https://platform.openai.com/docs/guides/chatkit

**Key Information**:
- Official OpenAI UI library for building chat interfaces
- Designed for React applications
- Provides pre-built components for chat functionality
- Supports customization and theming
- Requires domain allowlist configuration for production (NEXT_PUBLIC_OPENAI_DOMAIN_KEY)

**Implementation Approach**:
- Install ChatKit via npm
- Configure ChatKit components in Next.js App Router
- Integrate with existing Phase-2 authentication (JWT)
- Connect to POST /api/chat endpoint
- Configure domain allowlist for production deployment

### 2. ChatKit Integration with Next.js

**Research Question**: Best practices for integrating ChatKit with Next.js 16+ App Router?

**Finding**: ✅ ChatKit is compatible with Next.js and React 19+

**Implementation Pattern**:

1. **Installation**
   - Install ChatKit package from npm
   - Follow official ChatKit documentation for setup

2. **Component Integration**
   - Use ChatKit components within Next.js pages/components
   - Wrap with ChatKit provider at appropriate level
   - Configure ChatKit with API endpoint and authentication

3. **Authentication Integration**
   - Attach JWT token to ChatKit requests
   - Use existing Phase-2 API client patterns
   - Ensure user_id extracted from JWT by backend

4. **Styling**
   - ChatKit supports theming and customization
   - Can be styled to match existing Tailwind CSS design system
   - Responsive design built into ChatKit components

### 3. Floating Launcher Implementation

**Research Question**: Best practices for implementing floating UI elements with ChatKit?

**Finding**: ✅ Well-established patterns exist

**Implementation Pattern**:

1. **Global Provider Component**
   - Create `FloatingChatProvider` component
   - Render in root layout (`app/layout.tsx`)
   - Wrap all authenticated pages
   - Manage global chat state (open/closed/minimized)

2. **Z-Index Management**
   - Establish z-index hierarchy in Tailwind config
   - Recommended values:
     - Page content: z-0 to z-10
     - Dropdowns/tooltips: z-20 to z-30
     - Floating launcher icon: z-40
     - Chat interface (modal/panel): z-50
     - Modals (critical): z-[100]
   - Avoid conflicts with existing Phase-2 UI elements

3. **Positioning Strategy**
   - Use `fixed` positioning for floating icon
   - Position: `bottom-6 right-6` (24px from edges)
   - Responsive adjustments for mobile: `bottom-4 right-4` (16px from edges)
   - Ensure icon doesn't obstruct FAB buttons or other fixed elements

4. **Component Structure**:
```
FloatingChatProvider (Context Provider)
├── FloatingChatLauncher (Fixed position icon)
└── ChatKitInterface (ChatKit components, conditional render when open)
    ├── ChatHeader (Close/Minimize buttons)
    └── ChatKit Components (Message display, input, etc.)
```

**Alternatives Considered**:
- Portal-based rendering: More complex, not needed for this use case
- Separate route for chat: Doesn't meet "accessible from any page" requirement

### 4. Chat State Management

**Research Question**: Best approach for managing chat UI state with ChatKit?

**Finding**: ✅ React Context API for UI state, ChatKit handles message state

**Decision**: Use React Context API for UI state (open/closed/minimized), ChatKit manages conversation state

**Rationale**:
- ChatKit handles message state internally
- React Context needed for floating launcher UI state (open/closed/minimized)
- Integrates well with Next.js App Router
- TypeScript support
- Easy to test

**Implementation Approach**:

1. **ChatUIContext** (React Context)
   - Manages: isOpen, isMinimized (UI state only)
   - Provides: openChat(), closeChat(), minimizeChat()

2. **ChatKit State**
   - ChatKit manages: messages, loading, errors
   - ChatKit provides: sendMessage(), loadHistory() via its API

3. **State Persistence**:
   - UI state (open/closed) can persist to sessionStorage
   - Conversation history managed by ChatKit and backend

**Alternatives Considered**:
- Zustand: Overkill for simple UI state
- Redux: Too heavy, not needed
- Local state only: Doesn't persist across navigations

### 5. JWT Integration with Chat API

**Research Question**: How to integrate JWT authentication with ChatKit?

**Finding**: ✅ ChatKit supports custom authentication

**Implementation Approach**:

1. **Configure ChatKit with JWT**
   - Pass JWT token to ChatKit configuration
   - ChatKit will include token in API requests
   - Backend extracts user_id from JWT

2. **API Client Integration**
   - Use existing Phase-2 API client patterns
   - ChatKit configured to use POST /api/chat endpoint
   - JWT automatically attached via ChatKit configuration

3. **Token Refresh**
   - Handle JWT expiration gracefully
   - Redirect to login if token invalid
   - ChatKit error handling for auth failures

**Validation**: Confirmed with existing Phase-2 architecture (CLAUDE.md, API client patterns)

### 6. Responsive Design with ChatKit

**Research Question**: How does ChatKit handle responsive design?

**Finding**: ✅ ChatKit includes responsive design features

**Implementation Strategy**:

1. **Breakpoints** (Tailwind CSS defaults):
   - Mobile: < 640px (sm)
   - Tablet: 640px - 1024px (sm to lg)
   - Desktop: > 1024px (lg+)

2. **Floating Launcher Icon**:
   - Desktop: 60px × 60px, bottom-6 right-6
   - Mobile: 56px × 56px, bottom-4 right-4
   - Ensure touch target size ≥ 44px × 44px (iOS guidelines)

3. **Chat Interface**:
   - Desktop: Slide-in panel from right (400px width)
   - Tablet: Slide-in panel from right (360px width)
   - Mobile: Full-screen modal (100vw × 100vh)
   - ChatKit components adapt to container size

4. **ChatKit Customization**:
   - Use ChatKit theming to match Tailwind CSS design
   - Configure responsive behavior via ChatKit props
   - Ensure mobile-friendly touch targets

**Validation**: Aligns with Phase-2 responsive design patterns

### 7. Domain Allowlist Configuration

**Research Question**: How to configure OpenAI domain allowlist for production?

**Finding**: ✅ Requires NEXT_PUBLIC_OPENAI_DOMAIN_KEY environment variable

**Implementation**:
- Obtain domain allowlist key from OpenAI platform
- Set NEXT_PUBLIC_OPENAI_DOMAIN_KEY in environment variables
- Configure ChatKit with domain key for production deployment
- Test in staging environment before production

## Research Summary

### Resolved Technical Unknowns

| Unknown | Resolution |
|---------|-----------|
| OpenAI ChatKit existence | ✅ Exists and is suitable for this project |
| ChatKit compatibility | ✅ Compatible with Next.js 16+ and React 19+ |
| Floating launcher pattern | ✅ Global provider with fixed positioning |
| State management approach | ✅ React Context for UI state, ChatKit for message state |
| JWT integration | ✅ ChatKit supports custom authentication with JWT |
| Responsive design strategy | ✅ ChatKit includes responsive features, customize with Tailwind |
| Domain allowlist | ✅ Configure via NEXT_PUBLIC_OPENAI_DOMAIN_KEY |

### Key Decisions

1. **Chat UI Implementation**: OpenAI ChatKit (as specified)
2. **Floating Launcher**: Custom wrapper component with ChatKit inside
3. **UI State Management**: React Context API for open/closed/minimized state
4. **Message State**: Managed by ChatKit
5. **API Integration**: Configure ChatKit to use POST /api/chat with JWT
6. **Responsive Design**: ChatKit responsive features + custom container sizing
7. **Domain Allowlist**: Configure NEXT_PUBLIC_OPENAI_DOMAIN_KEY for production

### Implementation Guidance

**Installation Steps**:
1. Install OpenAI ChatKit via npm (follow official documentation)
2. Configure ChatKit provider in Next.js application
3. Set up environment variables (NEXT_PUBLIC_API_BASE_URL, NEXT_PUBLIC_OPENAI_DOMAIN_KEY)
4. Integrate with existing Phase-2 authentication

**Key Implementation Steps**:
1. Install ChatKit package
2. Create FloatingChatProvider wrapper component
3. Configure ChatKit with API endpoint and JWT
4. Implement floating launcher icon
5. Integrate ChatKit components within launcher
6. Add open/close/minimize functionality
7. Style to match Phase-2 design system
8. Test responsive behavior
9. Configure domain allowlist for production

### Common Issues and Solutions

**Issue**: Z-index conflicts with existing UI elements
**Solution**: Establish clear z-index hierarchy in Tailwind config, test on all pages

**Issue**: Chat state lost on page navigation
**Solution**: Use React Context at root layout level for UI state persistence

**Issue**: JWT token expiration during chat session
**Solution**: Implement token refresh logic or graceful error handling with re-login prompt

**Issue**: ChatKit styling conflicts with Tailwind
**Solution**: Use ChatKit theming API to match existing design system

## Next Steps

1. ✅ Phase 0 Research: COMPLETE
2. ⏭️ Phase 1 Design: Generate data-model.md, contracts/, quickstart.md
3. ⏭️ Update agent context with research findings
4. ⏭️ Re-evaluate Constitution Check (compliant with ChatKit approach)

## Appendix: Environment Variables

**Required**:
- `NEXT_PUBLIC_API_BASE_URL`: Backend API base URL (existing Phase-2)
- `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`: OpenAI domain allowlist key for ChatKit (production)

---

**Research Status**: ✅ COMPLETE
**Blocking Issues**: None
**Ready for Phase 1**: ✅ YES (with OpenAI ChatKit as specified)
