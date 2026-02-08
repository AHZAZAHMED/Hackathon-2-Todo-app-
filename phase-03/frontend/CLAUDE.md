# Frontend Rules - Todo Application

**Context**: Next.js 16+ frontend for Hackathon II Phase-2 Todo Application with Phase-3 ChatKit Integration

## Architecture

- **Framework**: Next.js 16+ with App Router
- **Language**: TypeScript 5.x with strict mode
- **Styling**: Tailwind CSS 3.x (official configuration, not CDN)
- **State Management**: React hooks (useState, useContext) and custom hooks
- **Navigation**: next/link Link component (NEVER use <a> tags)
- **Components**: Server Components by default, Client Components only for interactivity
- **Chat Integration**: OpenAI ChatKit (@openai/chatkit-react) for conversational interface

## Core Rules

### 1. No Mock Data
- NEVER use hardcoded arrays, fake data, or mock API responses
- All data MUST come from real API calls to backend
- Use loading states while fetching real data
- Display empty states when no data exists

### 2. Modern Next.js Patterns
- **Navigation**: ALWAYS use `<Link href="/path">` from next/link, NEVER `<a href="/path">`
- **Server Components**: Default for all components unless they need:
  - Event handlers (onClick, onChange, etc.)
  - React hooks (useState, useEffect, etc.)
  - Browser APIs (localStorage, window, etc.)
- **Client Components**: Add `'use client'` directive only when needed
- **App Router**: Use app/ directory structure, not pages/

### 3. TypeScript Strict Mode
- All functions must have explicit parameter and return types
- No `any` type - use `unknown` if type is truly unknown
- Use interfaces for object shapes
- Leverage union types for multiple possibilities
- Use type guards for narrowing types

### 4. ChatKit Integration (Phase-3)
- **Package**: Use `@openai/chatkit-react` for React integration
- **Configuration**: ChatKit requires CustomApiConfig with:
  - `url`: Backend API endpoint (e.g., `${apiBaseUrl}/api/chat`)
  - `domainKey`: OpenAI domain key from environment variable
  - `fetch`: Custom fetch function to inject JWT token in headers
- **Authentication**: JWT token must be added to fetch headers, not passed as authToken
- **State Management**:
  - ChatKit manages conversation state internally (messages, loading, errors)
  - Custom wrapper manages UI state (isOpen, isMinimized) via ChatUIContext
- **Components**:
  - Use `useChatKit()` hook to configure ChatKit
  - Use `<ChatKit control={chatKitHook.control} />` component to render
  - Wrap in custom components for floating launcher functionality
- **Styling**: Customize via CSS variables (--chatkit-primary-color, --chatkit-user-message-bg, etc.)

### 5. Component Structure
```typescript
// Server Component (default)
import { ComponentName } from '@/components/path';

export default function PageName() {
  return <ComponentName />;
}

// Client Component (only when needed)
'use client';

import { useState } from 'react';

export function ComponentName() {
  const [state, setState] = useState<Type>(initialValue);
  return <div>...</div>;
}
```

### 5. API Integration
- Use centralized API client from `lib/api-client.ts`
- All API calls go through the API client singleton
- Handle errors with try-catch and display user-friendly messages
- Use custom hooks for shared API logic (useAuth, useTasks)

### 6. Form Handling
- Use controlled components with React state
- Validate on submit and display inline error messages
- Disable submit button while processing
- Clear form after successful submission

### 7. Styling with Tailwind CSS
- Use utility classes directly in JSX
- Follow mobile-first responsive design (sm, md, lg, xl breakpoints)
- Use custom theme colors defined in globals.css
- No inline styles or CSS modules

### 8. Session Persistence
- Prepare for httpOnly cookie-based sessions (backend handles)
- Use `credentials: 'include'` in fetch requests
- Frontend doesn't manually store tokens
- Session persists until logout or browser close

### 9. User Isolation
- Backend enforces user isolation via JWT user_id
- Frontend doesn't need to filter by user_id
- All API responses are already scoped to authenticated user

### 10. Accessibility
- Use semantic HTML elements
- Ensure keyboard navigation works (Tab, Enter, Escape)
- Provide visible focus states on interactive elements
- Use proper ARIA labels where needed

## File Organization

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Landing page (/)
│   ├── login/page.tsx     # Login page
│   ├── signup/page.tsx    # Signup page
│   └── dashboard/page.tsx # Dashboard page
├── components/
│   ├── layout/            # Navbar, Footer, ProfileDropdown
│   ├── landing/           # Hero, Features
│   ├── auth/              # LoginForm, SignupForm
│   ├── dashboard/         # StatsCards, TaskList, TaskItem
│   ├── tasks/             # AddTaskModal, EditTaskModal
│   └── ui/                # Button, Input, Card, Modal
├── lib/
│   ├── api-client.ts      # Centralized API client
│   └── utils.ts           # Helper functions
├── hooks/
│   ├── useAuth.ts         # Auth state management
│   ├── useTasks.ts        # Task management
│   └── useModal.ts        # Modal state management
├── types/
│   ├── task.ts            # Task types
│   ├── user.ts            # User types
│   ├── auth.ts            # Auth types
│   └── api.ts             # API response types
├── public/                # Static assets
├── styles/                # Additional styles if needed
└── .env.local             # Environment variables (gitignored)
```

## Environment Variables

Required in `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_APP_NAME=Todo App
```

## Development Workflow

1. **Start dev server**: `npm run dev`
2. **Build for production**: `npm run build`
3. **Run linter**: `npm run lint`
4. **Type check**: `npx tsc --noEmit`

## Quality Standards

- No console errors in browser
- TypeScript compiles without errors (strict mode)
- ESLint passes with no warnings
- All pages responsive (320px - 1920px)
- Keyboard navigation works throughout
- Color contrast meets WCAG 2.1 AA standards

## Common Patterns

### Navigation
```typescript
import Link from 'next/link';

// Correct
<Link href="/dashboard">Dashboard</Link>

// Incorrect - NEVER do this
<a href="/dashboard">Dashboard</a>
```

### API Calls
```typescript
'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';
import { Task } from '@/types/task';

export function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadTasks = async () => {
      try {
        const data = await apiClient.getTasks();
        setTasks(data);
      } catch (error) {
        console.error('Failed to load tasks:', error);
      } finally {
        setLoading(false);
      }
    };
    loadTasks();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (tasks.length === 0) return <div>No tasks yet</div>;

  return (
    <div>
      {tasks.map(task => (
        <div key={task.id}>{task.title}</div>
      ))}
    </div>
  );
}
```

### Forms
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
      setErrors({ form: 'Login failed' });
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

## References

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## Notes

- This is frontend-only. Backend API implemented separately.
- Authentication logic (JWT handling) in authentication feature.
- Database persistence handled by backend.
- All modern Next.js patterns enforced.
