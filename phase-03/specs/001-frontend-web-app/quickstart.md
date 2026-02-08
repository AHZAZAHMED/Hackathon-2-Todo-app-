# Quickstart Guide: Frontend Web Application

**Feature**: Frontend Web Application
**Branch**: 001-frontend-web-app
**Created**: 2026-02-05

## Prerequisites

Before starting development, ensure you have the following installed:

- **Node.js**: Version 18.x or higher
- **npm**: Version 9.x or higher (comes with Node.js)
- **Git**: For version control
- **Code Editor**: VS Code recommended with extensions:
  - ESLint
  - Prettier
  - Tailwind CSS IntelliSense
  - TypeScript and JavaScript Language Features

## Initial Setup

### 1. Clone Repository

```bash
cd E:\Hackathon-2\phase-02
git checkout 001-frontend-web-app
```

### 2. Create Frontend Directory

```bash
mkdir frontend
cd frontend
```

### 3. Initialize Next.js Application

```bash
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*"
```

**Configuration prompts**:
- ✅ TypeScript: Yes
- ✅ ESLint: Yes
- ✅ Tailwind CSS: Yes
- ✅ App Router: Yes
- ❌ src/ directory: No
- ✅ Import alias: Yes (@/*)

### 4. Install Additional Dependencies

```bash
npm install
```

### 5. Configure TypeScript Strict Mode

Edit `tsconfig.json`:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    // ... other options
  }
}
```

### 6. Configure Tailwind CSS

Edit `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
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
  },
  plugins: [],
}
```

### 7. Create Folder Structure

```bash
mkdir -p components/layout components/landing components/auth components/dashboard components/tasks components/ui
mkdir -p lib hooks types public/images styles
```

### 8. Create Environment Files

Create `.env.example`:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Application Configuration
NEXT_PUBLIC_APP_NAME=Todo App
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

Create `.env.local` (gitignored):

```bash
cp .env.example .env.local
```

### 9. Update .gitignore

Ensure `.env.local` is in `.gitignore`:

```
# local env files
.env*.local
```

### 10. Create Frontend CLAUDE.md

Create `frontend/CLAUDE.md` with frontend-specific rules (see template in plan.md).

---

## Development Workflow

### Start Development Server

```bash
npm run dev
```

Application will be available at: http://localhost:3000

### Build for Production

```bash
npm run build
```

### Run Linter

```bash
npm run lint
```

### Type Check

```bash
npx tsc --noEmit
```

---

## Project Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Landing page (/)
│   ├── login/page.tsx           # Login page
│   ├── signup/page.tsx          # Signup page
│   └── dashboard/page.tsx       # Dashboard page
├── components/                   # React components
│   ├── layout/                  # Layout components
│   ├── landing/                 # Landing page components
│   ├── auth/                    # Auth form components
│   ├── dashboard/               # Dashboard components
│   ├── tasks/                   # Task management components
│   └── ui/                      # Reusable UI components
├── lib/                          # Utilities
│   ├── api-client.ts            # API client
│   └── utils.ts                 # Helper functions
├── hooks/                        # Custom React hooks
│   ├── useAuth.ts               # Auth state hook
│   ├── useTasks.ts              # Task management hook
│   └── useModal.ts              # Modal state hook
├── types/                        # TypeScript types
│   ├── task.ts                  # Task types
│   ├── user.ts                  # User types
│   ├── auth.ts                  # Auth types
│   └── api.ts                   # API types
├── public/                       # Static assets
├── styles/                       # Global styles
│   └── globals.css              # Global CSS
├── CLAUDE.md                     # Frontend rules
├── .env.example                  # Environment template
├── .env.local                    # Local environment (gitignored)
├── next.config.js                # Next.js config
├── tailwind.config.js            # Tailwind config
├── tsconfig.json                 # TypeScript config
├── package.json                  # Dependencies
└── README.md                     # Documentation
```

---

## Common Commands

### Development

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint errors
```

### Type Checking

```bash
npx tsc --noEmit     # Type check without emitting files
```

### Component Generation

```bash
# Create new component (manual)
touch components/ui/NewComponent.tsx
```

---

## Code Style Guidelines

### Component Structure

```typescript
// components/ui/Button.tsx
'use client'; // Only if Client Component

import { ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
}

export function Button({ variant = 'primary', children, ...props }: ButtonProps) {
  return (
    <button
      className={`px-4 py-2 rounded ${variant === 'primary' ? 'bg-blue-500' : 'bg-gray-500'}`}
      {...props}
    >
      {children}
    </button>
  );
}
```

### Page Structure

```typescript
// app/page.tsx (Server Component by default)
import { Hero } from '@/components/landing/Hero';
import { Features } from '@/components/landing/Features';

export default function HomePage() {
  return (
    <main>
      <Hero />
      <Features />
    </main>
  );
}
```

### API Client Usage

```typescript
// In a Client Component
'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api-client';
import { Task } from '@/types/task';

export function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);

  const loadTasks = async () => {
    try {
      const data = await apiClient.getTasks();
      setTasks(data);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    }
  };

  // ... rest of component
}
```

---

## Troubleshooting

### Port Already in Use

If port 3000 is already in use:

```bash
# Kill process on port 3000 (Windows)
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

1. Check `tailwind.config.js` content paths
2. Ensure `globals.css` imports Tailwind directives:
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```
3. Restart development server

### Module Not Found

```bash
# Clear cache and rebuild
rm -rf .next
npm run dev
```

---

## Testing

### Manual Testing Checklist

- [ ] Landing page loads at http://localhost:3000
- [ ] Navigation links work (no full page reload)
- [ ] Login page accessible at /login
- [ ] Signup page accessible at /signup
- [ ] Dashboard page accessible at /dashboard
- [ ] All pages responsive on mobile/tablet/desktop
- [ ] No console errors in browser
- [ ] TypeScript compiles without errors

### Browser Testing

Test in multiple browsers:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

### Responsive Testing

Test at different screen sizes:
- Mobile: 375px, 414px
- Tablet: 768px, 1024px
- Desktop: 1280px, 1920px

---

## Next Steps

After completing setup:

1. **Implement Phase 1**: Next.js Application Setup
2. **Implement Phase 2**: Global Layout & Navigation
3. **Implement Phase 3**: Landing Page
4. **Implement Phase 4**: Authentication Pages
5. **Implement Phase 5**: Dashboard UI
6. **Implement Phase 6**: Task Management
7. **Implement Phase 7**: API Client & Integration
8. **Implement Phase 8**: Routing & Navigation

Follow the detailed task list generated by `/sp.tasks` command.

---

## Resources

### Documentation

- [Next.js 16 Documentation](https://nextjs.org/docs)
- [React 19 Documentation](https://react.dev)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

### Best Practices

- Use Server Components by default
- Use Client Components only for interactivity
- Use next/link for navigation (not <a> tags)
- Use TypeScript strict mode
- Follow Tailwind utility-first approach
- Keep components small and focused
- Use custom hooks for shared logic

---

## Support

For issues or questions:
1. Check this quickstart guide
2. Review plan.md for architecture details
3. Check data-model.md for type definitions
4. Check contracts/api-client.md for API specifications
5. Consult Next.js documentation
6. Ask team for help

---

## Notes

- This is a frontend-only setup. Backend API will be implemented separately.
- Authentication logic (JWT handling) will be implemented in authentication feature.
- Database persistence will be handled by backend.
- Session persistence implementation details in authentication feature spec.
- All modern Next.js patterns used (Link component, App Router, Server Components).
