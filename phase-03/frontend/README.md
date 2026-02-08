# Frontend - Todo Application

A modern task management application built with Next.js 16+, TypeScript, and Tailwind CSS.

## Tech Stack

- **Framework**: Next.js 16+ with App Router
- **Language**: TypeScript 5.x (strict mode)
- **Styling**: Tailwind CSS 3.x
- **State Management**: React hooks and custom hooks
- **API Client**: Centralized fetch wrapper

## Prerequisites

- Node.js 18.x or higher
- npm 9.x or higher

## Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Setup

Copy the example environment file:

```bash
cp .env.example .env.local
```

Update `.env.local` with your configuration:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_APP_NAME=Todo App
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### 3. Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4. Production Build

```bash
npm run build
npm run start
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout with Navbar/Footer
│   ├── page.tsx           # Landing page
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
│   ├── useAuth.tsx        # Auth state management
│   ├── useTasks.ts        # Task management
│   └── useModal.ts        # Modal state management
├── types/
│   ├── task.ts            # Task types
│   ├── user.ts            # User types
│   ├── auth.ts            # Auth types
│   └── api.ts             # API response types
└── public/                # Static assets
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npx tsc --noEmit` - Type check without emitting files

## Features

### Implemented

- ✅ Landing page with hero section and features showcase
- ✅ Login and signup pages with form validation
- ✅ Dashboard with task statistics
- ✅ Task list with empty state
- ✅ Add/Edit/Delete task modals
- ✅ Task completion toggle
- ✅ Profile dropdown with logout option
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Keyboard navigation support
- ✅ TypeScript strict mode
- ✅ Centralized API client

### Pending Backend Integration

The following features are implemented in the UI but require backend API integration:

- Authentication (login, signup, logout)
- Session persistence
- Task CRUD operations
- User profile data

## Architecture Decisions

### Modern Next.js Patterns

- **Navigation**: Uses `Link` component from next/link (not `<a>` tags)
- **Server Components**: Default for all components
- **Client Components**: Only for interactivity (`'use client'` directive)
- **App Router**: Uses app/ directory structure

### State Management

- React hooks (useState, useEffect) for local state
- Custom hooks (useAuth, useTasks, useModal) for shared logic
- No external state management library needed

### API Integration

- Centralized API client in `lib/api-client.ts`
- All API calls go through singleton instance
- JWT token management built-in
- Error handling with custom ApiError class
- Credentials included for session persistence

### Form Handling

- Controlled components with React state
- Client-side validation before submission
- Inline error messages
- Disabled state during submission

## Code Style

### Component Structure

```typescript
// Server Component (default)
export default function PageName() {
  return <div>...</div>;
}

// Client Component (only when needed)
'use client';

import { useState } from 'react';

export function ComponentName() {
  const [state, setState] = useState<Type>(initialValue);
  return <div>...</div>;
}
```

### Navigation

```typescript
import Link from 'next/link';

// ✅ Correct
<Link href="/dashboard">Dashboard</Link>

// ❌ Incorrect
<a href="/dashboard">Dashboard</a>
```

### API Calls

```typescript
import { apiClient } from '@/lib/api-client';

try {
  const tasks = await apiClient.getTasks();
  setTasks(tasks);
} catch (error) {
  console.error('Failed to load tasks:', error);
}
```

## Responsive Design

The application is fully responsive across all screen sizes:

- **Mobile**: 320px - 767px
- **Tablet**: 768px - 1023px
- **Desktop**: 1024px+

Tailwind CSS breakpoints:
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px

## Accessibility

- Semantic HTML elements
- Keyboard navigation (Tab, Enter, Escape)
- Visible focus states
- ARIA labels where needed
- Color contrast meets WCAG 2.1 AA standards

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use different port
npm run dev -- -p 3001
```

### TypeScript Errors

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Tailwind Styles Not Working

1. Check `globals.css` imports Tailwind directives
2. Restart development server
3. Clear browser cache

## Next Steps

1. **Backend Integration**: Connect to FastAPI backend when ready
2. **Authentication**: Implement Better Auth JWT integration
3. **Testing**: Add Playwright tests for user flows
4. **Deployment**: Deploy to Vercel or similar platform

## Documentation

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## Notes

- This is a frontend-only implementation
- Backend API integration pending
- No mock data used - all components ready for real API
- Session persistence via httpOnly cookies (backend responsibility)
- All modern Next.js patterns enforced

## License

MIT
