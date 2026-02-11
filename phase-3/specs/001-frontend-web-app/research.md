# Research Document: Frontend Web Application

**Feature**: Frontend Web Application
**Branch**: 001-frontend-web-app
**Created**: 2026-02-05
**Phase**: 0 - Research & Technology Decisions

## Overview

This document consolidates all research findings and technology decisions made during the planning phase for the Frontend Web Application feature. Each decision includes the rationale, alternatives considered, and implementation guidance.

---

## 1. Next.js 16+ App Router Best Practices

### Decision
Use Next.js 16+ App Router with Server Components by default, Client Components only for interactivity.

### Rationale
- **App Router** is the recommended approach for Next.js 16+
- **Server Components** provide better performance by reducing JavaScript sent to client
- **Automatic code splitting** improves initial load time
- **Built-in data fetching** with async/await in Server Components
- **Streaming and Suspense** support for better UX

### Alternatives Considered
- **Pages Router**: Legacy approach, not recommended for new projects, lacks Server Components
- **Client-only React**: Would require more JavaScript on client, worse performance

### Implementation Guidance
- Use Server Components by default (no 'use client' directive)
- Add 'use client' only for components with:
  - Event handlers (onClick, onChange, etc.)
  - React hooks (useState, useEffect, etc.)
  - Browser APIs (localStorage, window, etc.)
- Use next/link for navigation (not <a> tags)
- Leverage automatic route-based code splitting

### References
- [Next.js App Router Documentation](https://nextjs.org/docs/app)
- [Server Components Guide](https://nextjs.org/docs/app/building-your-application/rendering/server-components)

---

## 2. Tailwind CSS Configuration

### Decision
Official Tailwind CSS configuration with custom theme, not CDN approach.

### Rationale
- **Utility-first approach** provides consistent design system
- **No runtime overhead** - styles compiled at build time
- **Purging unused styles** keeps bundle size small
- **Custom theme** allows brand consistency
- **Responsive design** built-in with breakpoint utilities
- **Better than CDN** - allows customization and tree-shaking

### Alternatives Considered
- **CSS Modules**: More verbose, requires separate CSS files, harder to maintain consistency
- **Styled Components**: Runtime overhead, larger bundle size, CSS-in-JS complexity
- **CDN Tailwind**: Cannot customize, includes all styles (large bundle), no tree-shaking

### Implementation Guidance
- Configure in `tailwind.config.js` with custom colors
- Use utility classes directly in JSX
- Follow mobile-first responsive design (sm, md, lg, xl breakpoints)
- Create reusable component classes in `globals.css` if needed
- Use Tailwind CSS IntelliSense VS Code extension

### Custom Theme
```javascript
theme: {
  extend: {
    colors: {
      primary: {
        50: '#eff6ff',
        100: '#dbeafe',
        500: '#3b82f6',
        600: '#2563eb',
        700: '#1d4ed8',
      },
    },
  },
}
```

### References
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Customizing Theme](https://tailwindcss.com/docs/theme)

---

## 3. TypeScript Strict Mode

### Decision
Enable TypeScript strict mode in tsconfig.json.

### Rationale
- **Catches more errors** at compile time before runtime
- **Better type safety** prevents common bugs
- **Improved IDE support** with better autocomplete
- **Production-grade requirement** per constitution
- **Forces explicit typing** improves code quality

### Alternatives Considered
- **Loose mode**: Easier to write but allows more bugs, not production-grade
- **No TypeScript**: JavaScript only, loses all type safety benefits

### Implementation Guidance
```json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitReturns": true,
    "noUncheckedIndexedAccess": true
  }
}
```

### Common Strict Mode Patterns
- Always type function parameters and return types
- Use interfaces for object shapes
- Avoid `any` type - use `unknown` if type truly unknown
- Use type guards for narrowing types
- Leverage union types for multiple possibilities

### References
- [TypeScript Strict Mode](https://www.typescriptlang.org/tsconfig#strict)
- [TypeScript Best Practices](https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html)

---

## 4. Session Persistence Strategy

### Decision
Prepare frontend for httpOnly cookie-based sessions (implementation details in authentication feature spec).

### Rationale
- **Most secure approach** - httpOnly cookies cannot be accessed by JavaScript
- **Prevents XSS attacks** - token not exposed to client-side code
- **Automatic with fetch** - browser includes cookies automatically
- **Persists across tabs** - same cookie shared across browser tabs
- **Survives page refresh** - cookie persists until expiration or logout

### Alternatives Considered
- **localStorage**: Vulnerable to XSS attacks, accessible by any JavaScript
- **sessionStorage**: Doesn't persist across tabs, lost on tab close
- **Memory only**: Lost on page refresh, poor UX

### Implementation Guidance
- Use `credentials: 'include'` in fetch requests
- Backend sets httpOnly cookie on login
- Frontend doesn't need to manually handle token storage
- Cookie automatically included in all requests to same domain
- Logout clears cookie on backend

### Security Considerations
- httpOnly flag prevents JavaScript access
- Secure flag ensures HTTPS-only transmission
- SameSite attribute prevents CSRF attacks
- Short expiration time limits exposure window

### References
- [HTTP Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)
- [httpOnly Cookies](https://owasp.org/www-community/HttpOnly)

---

## 5. Navigation Pattern

### Decision
Use next/link with Link component for all navigation, not <a> tags.

### Rationale
- **Client-side navigation** - no full page reload
- **Prefetching** - Link prefetches pages on hover for instant navigation
- **Better UX** - faster navigation, maintains scroll position
- **Automatic code splitting** - only loads needed JavaScript
- **Modern Next.js pattern** - recommended approach

### Alternatives Considered
- **<a> tags**: Causes full page reload, loses application state, slower
- **router.push()**: Less declarative, harder to maintain, no prefetching

### Implementation Guidance
```typescript
import Link from 'next/link';

// Correct
<Link href="/dashboard">Dashboard</Link>

// Incorrect
<a href="/dashboard">Dashboard</a>
```

### Link Component Features
- Prefetches linked pages in viewport
- Maintains scroll position on back/forward
- Supports dynamic routes
- Works with query parameters
- Accessible by default

### References
- [next/link Documentation](https://nextjs.org/docs/app/api-reference/components/link)
- [Client-side Navigation](https://nextjs.org/docs/app/building-your-application/routing/linking-and-navigating)

---

## 6. State Management

### Decision
React hooks (useState, useContext) for local state, custom hooks for shared logic.

### Rationale
- **Sufficient for scope** - frontend-only, no complex global state
- **No external dependencies** - uses built-in React features
- **Simple and maintainable** - easy to understand and debug
- **Custom hooks** provide reusability without complexity
- **Context API** sufficient for auth state sharing

### Alternatives Considered
- **Redux**: Overkill for this scope, adds boilerplate and complexity
- **Zustand**: Unnecessary external dependency, React hooks sufficient
- **Recoil**: Too complex for simple state needs

### Implementation Guidance

**Local State**:
```typescript
const [tasks, setTasks] = useState<Task[]>([]);
```

**Shared State (Context)**:
```typescript
const AuthContext = createContext<AuthState | null>(null);

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
```

**Custom Hooks**:
```typescript
export function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);

  const loadTasks = async () => {
    setLoading(true);
    const data = await apiClient.getTasks();
    setTasks(data);
    setLoading(false);
  };

  return { tasks, loading, loadTasks };
}
```

### References
- [React Hooks](https://react.dev/reference/react)
- [Context API](https://react.dev/reference/react/useContext)

---

## 7. Form Handling

### Decision
Controlled components with React state for form handling.

### Rationale
- **Simple and predictable** - React state as single source of truth
- **Works well with validation** - easy to validate on change
- **No external dependencies** - uses built-in React features
- **Sufficient for scope** - forms are simple (login, signup, task creation)

### Alternatives Considered
- **React Hook Form**: Adds dependency, overkill for simple forms
- **Uncontrolled components**: Less control, harder to validate, refs needed

### Implementation Guidance
```typescript
'use client';

import { useState, FormEvent } from 'react';

export function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Validation
    const newErrors: Record<string, string> = {};
    if (!email) newErrors.email = 'Email is required';
    if (!password) newErrors.password = 'Password is required';

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    // Submit
    try {
      await apiClient.login({ email, password });
    } catch (error) {
      // Handle error
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      {errors.email && <span>{errors.email}</span>}
      {/* ... */}
    </form>
  );
}
```

### References
- [Controlled Components](https://react.dev/reference/react-dom/components/input#controlling-an-input-with-a-state-variable)
- [Form Handling](https://react.dev/learn/reacting-to-input-with-state)

---

## 8. Modal Implementation

### Decision
Custom modal component with portal rendering using React createPortal.

### Rationale
- **Full control** over styling and behavior
- **No external dependencies** - uses React built-in features
- **Portal rendering** - renders outside parent DOM hierarchy
- **Accessible** - can implement proper focus management
- **Customizable** - easy to adapt to design requirements

### Alternatives Considered
- **Headless UI**: Adds dependency, more complex than needed
- **Native dialog**: Limited browser support, less control over styling

### Implementation Guidance
```typescript
'use client';

import { ReactNode, useEffect } from 'react';
import { createPortal } from 'react-dom';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: ReactNode;
}

export function Modal({ isOpen, onClose, children }: ModalProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-lg p-6 max-w-md w-full">
        {children}
      </div>
    </div>,
    document.body
  );
}
```

### References
- [createPortal](https://react.dev/reference/react-dom/createPortal)
- [Modal Accessibility](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)

---

## 9. Responsive Design Breakpoints

### Decision
Use Tailwind CSS default breakpoints (sm: 640px, md: 768px, lg: 1024px, xl: 1280px).

### Rationale
- **Industry standard** - widely used and tested
- **Covers all devices** - mobile, tablet, desktop
- **Mobile-first approach** - base styles for mobile, override for larger screens
- **Well-documented** - extensive examples and community support

### Alternatives Considered
- **Custom breakpoints**: Unnecessary complexity, standard breakpoints sufficient

### Implementation Guidance

**Mobile-first approach**:
```typescript
<div className="w-full md:w-1/2 lg:w-1/3">
  {/* Full width on mobile, half on tablet, third on desktop */}
</div>
```

**Breakpoint Reference**:
- **Default (< 640px)**: Mobile phones
- **sm (≥ 640px)**: Large phones, small tablets
- **md (≥ 768px)**: Tablets
- **lg (≥ 1024px)**: Laptops, small desktops
- **xl (≥ 1280px)**: Large desktops
- **2xl (≥ 1536px)**: Extra large screens

### Testing Strategy
- Test at 375px (iPhone SE)
- Test at 768px (iPad)
- Test at 1280px (laptop)
- Test at 1920px (desktop)

### References
- [Tailwind Responsive Design](https://tailwindcss.com/docs/responsive-design)
- [Breakpoints](https://tailwindcss.com/docs/breakpoints)

---

## 10. API Client Architecture

### Decision
Centralized fetch wrapper in lib/api-client.ts with singleton pattern.

### Rationale
- **Single point of control** for all API communication
- **JWT attachment** - automatically adds token to all requests
- **Error handling** - centralized error transformation
- **Request/response transformation** - consistent data format
- **No external dependencies** - uses native fetch API
- **Type safety** - TypeScript types for all endpoints

### Alternatives Considered
- **Axios**: Unnecessary dependency, fetch API sufficient
- **Direct fetch calls**: Scattered logic, hard to maintain, no centralization

### Implementation Guidance
```typescript
class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
  }

  private async request<T>(endpoint: string, config: RequestConfig): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...config.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: config.method,
      headers,
      body: config.body ? JSON.stringify(config.body) : undefined,
      credentials: 'include',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new ApiError(error.message, response.status, error);
    }

    return response.json();
  }

  async getTasks(): Promise<Task[]> {
    return this.request<ApiResponse<Task[]>>('/tasks', {
      method: 'GET',
    }).then(res => res.data);
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
```

### Benefits
- All API calls go through single client
- Easy to add interceptors for logging, retry logic
- Consistent error handling across application
- Type-safe API calls with TypeScript
- Easy to mock for testing

### References
- [Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [TypeScript Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html)

---

## Summary

All technology decisions have been finalized and documented. The chosen stack provides:

- **Modern architecture**: Next.js 16+ App Router with Server Components
- **Type safety**: TypeScript strict mode
- **Consistent styling**: Tailwind CSS with custom theme
- **Secure authentication**: httpOnly cookie-based sessions
- **Optimal UX**: Client-side navigation with prefetching
- **Simple state management**: React hooks and Context API
- **Maintainable forms**: Controlled components
- **Accessible modals**: Custom implementation with portals
- **Responsive design**: Mobile-first with Tailwind breakpoints
- **Centralized API**: Single API client with type safety

All decisions align with constitution principles and production-grade requirements.

---

## Next Steps

1. Proceed to Phase 1: Design & Contracts (✅ Completed)
2. Generate tasks with `/sp.tasks` command
3. Begin implementation following task list
4. Validate each phase with `implementation-validator-playwright` skill
