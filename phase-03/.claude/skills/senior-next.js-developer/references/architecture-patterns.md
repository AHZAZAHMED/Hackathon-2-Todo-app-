# Next.js Architecture Patterns

## Project Structure Patterns

### App Router Structure (Next.js 13+)

```
app/
├── (auth)/                    # Route group for auth pages
│   ├── login/
│   │   └── page.tsx
│   ├── register/
│   │   └── page.tsx
│   └── layout.tsx            # Auth-specific layout
├── (dashboard)/              # Route group for dashboard
│   ├── settings/
│   │   └── page.tsx
│   ├── profile/
│   │   └── page.tsx
│   └── layout.tsx            # Dashboard layout with sidebar
├── api/                      # API routes
│   ├── auth/
│   │   └── [...nextauth]/
│   │       └── route.ts
│   └── tasks/
│       └── route.ts
├── layout.tsx                # Root layout
├── page.tsx                  # Home page
└── error.tsx                 # Error boundary
```

**Benefits:**
- Route groups `(name)` organize without affecting URL structure
- Colocation of related routes
- Shared layouts per section
- Clear separation of concerns

### Pages Router Structure (Next.js 12.x)

```
pages/
├── api/                      # API routes
│   ├── auth/
│   │   └── [...nextauth].ts
│   └── tasks.ts
├── _app.tsx                  # Custom App component
├── _document.tsx             # Custom Document
├── index.tsx                 # Home page
├── login.tsx
└── dashboard/
    ├── index.tsx
    └── settings.tsx

components/
├── common/                   # Shared components
│   ├── Button.tsx
│   ├── Input.tsx
│   └── Modal.tsx
├── layout/                   # Layout components
│   ├── Header.tsx
│   ├── Footer.tsx
│   └── Sidebar.tsx
└── features/                 # Feature-specific components
    ├── auth/
    │   ├── LoginForm.tsx
    │   └── RegisterForm.tsx
    └── tasks/
        ├── TaskList.tsx
        └── TaskItem.tsx
```

### Recommended Folder Structure

```
src/
├── app/                      # Next.js app directory
├── components/               # React components
│   ├── ui/                  # Reusable UI components
│   ├── forms/               # Form components
│   └── layouts/             # Layout components
├── lib/                      # Utility functions
│   ├── api.ts               # API client
│   ├── auth.ts              # Auth utilities
│   └── utils.ts             # General utilities
├── hooks/                    # Custom React hooks
│   ├── useAuth.ts
│   ├── useTasks.ts
│   └── useDebounce.ts
├── types/                    # TypeScript types
│   ├── api.ts
│   ├── models.ts
│   └── index.ts
├── config/                   # Configuration files
│   ├── site.ts              # Site metadata
│   └── constants.ts         # App constants
└── styles/                   # Global styles
    ├── globals.css
    └── themes/
```

## Component Organization Patterns

### Server vs Client Components (App Router)

**Server Components (Default)**
```typescript
// app/tasks/page.tsx
import { getTasks } from '@/lib/api'

export default async function TasksPage() {
  const tasks = await getTasks() // Fetch on server

  return (
    <div>
      <h1>Tasks</h1>
      <TaskList tasks={tasks} />
    </div>
  )
}
```

**Client Components (Interactive)**
```typescript
// components/TaskList.tsx
'use client'

import { useState } from 'react'

export function TaskList({ tasks }) {
  const [filter, setFilter] = useState('all')

  return (
    <div>
      <FilterButtons onFilterChange={setFilter} />
      {tasks.filter(/* ... */).map(task => (
        <TaskItem key={task.id} task={task} />
      ))}
    </div>
  )
}
```

**When to Use Each:**
- **Server Components**: Data fetching, static content, SEO-critical content
- **Client Components**: Interactivity, event handlers, browser APIs, state management

### Component Composition Patterns

**Container/Presenter Pattern**
```typescript
// Container (handles logic)
async function TasksContainer() {
  const tasks = await fetchTasks()

  return <TasksPresenter tasks={tasks} />
}

// Presenter (handles UI)
function TasksPresenter({ tasks }) {
  return (
    <ul>
      {tasks.map(task => (
        <li key={task.id}>{task.title}</li>
      ))}
    </ul>
  )
}
```

**Compound Components Pattern**
```typescript
// Flexible, composable components
<Card>
  <Card.Header>
    <Card.Title>Task Details</Card.Title>
  </Card.Header>
  <Card.Body>
    <Card.Description>Task description here</Card.Description>
  </Card.Body>
  <Card.Footer>
    <Button>Save</Button>
  </Card.Footer>
</Card>
```

**Render Props Pattern**
```typescript
<DataFetcher url="/api/tasks">
  {({ data, loading, error }) => {
    if (loading) return <Spinner />
    if (error) return <Error message={error.message} />
    return <TaskList tasks={data} />
  }}
</DataFetcher>
```

## Routing Patterns

### Dynamic Routes

**App Router**
```typescript
// app/tasks/[id]/page.tsx
export default function TaskPage({ params }: { params: { id: string } }) {
  return <div>Task {params.id}</div>
}

// Generate static params for SSG
export async function generateStaticParams() {
  const tasks = await fetchTasks()
  return tasks.map(task => ({ id: task.id.toString() }))
}
```

**Pages Router**
```typescript
// pages/tasks/[id].tsx
import { useRouter } from 'next/router'

export default function TaskPage() {
  const router = useRouter()
  const { id } = router.query

  return <div>Task {id}</div>
}
```

### Catch-All Routes

```typescript
// app/docs/[...slug]/page.tsx
export default function DocsPage({ params }: { params: { slug: string[] } }) {
  // /docs/a/b/c → params.slug = ['a', 'b', 'c']
  return <div>Docs: {params.slug.join('/')}</div>
}
```

### Parallel Routes (App Router)

```typescript
// app/dashboard/@analytics/page.tsx
// app/dashboard/@team/page.tsx
// app/dashboard/layout.tsx

export default function DashboardLayout({
  children,
  analytics,
  team
}: {
  children: React.ReactNode
  analytics: React.ReactNode
  team: React.ReactNode
}) {
  return (
    <div>
      {children}
      <div className="grid grid-cols-2">
        {analytics}
        {team}
      </div>
    </div>
  )
}
```

### Intercepting Routes (App Router)

```typescript
// app/photos/[id]/page.tsx - Full page
// app/@modal/(.)photos/[id]/page.tsx - Modal overlay

// Useful for modal views that can also be direct links
```

## Data Fetching Patterns

### Server-Side Rendering (SSR)

**App Router**
```typescript
// app/tasks/page.tsx
async function getTasks() {
  const res = await fetch('https://api.example.com/tasks', {
    cache: 'no-store' // Disable caching for dynamic data
  })
  return res.json()
}

export default async function TasksPage() {
  const tasks = await getTasks()
  return <TaskList tasks={tasks} />
}
```

**Pages Router**
```typescript
// pages/tasks.tsx
export async function getServerSideProps() {
  const res = await fetch('https://api.example.com/tasks')
  const tasks = await res.json()

  return {
    props: { tasks }
  }
}

export default function TasksPage({ tasks }) {
  return <TaskList tasks={tasks} />
}
```

### Static Site Generation (SSG)

**App Router**
```typescript
// app/blog/[slug]/page.tsx
async function getPost(slug: string) {
  const res = await fetch(`https://api.example.com/posts/${slug}`, {
    next: { revalidate: 3600 } // Revalidate every hour
  })
  return res.json()
}

export default async function BlogPost({ params }) {
  const post = await getPost(params.slug)
  return <Article post={post} />
}

export async function generateStaticParams() {
  const posts = await fetch('https://api.example.com/posts').then(r => r.json())
  return posts.map(post => ({ slug: post.slug }))
}
```

**Pages Router**
```typescript
// pages/blog/[slug].tsx
export async function getStaticProps({ params }) {
  const post = await fetchPost(params.slug)

  return {
    props: { post },
    revalidate: 3600 // ISR: Revalidate every hour
  }
}

export async function getStaticPaths() {
  const posts = await fetchPosts()

  return {
    paths: posts.map(post => ({ params: { slug: post.slug } })),
    fallback: 'blocking' // or true, false
  }
}
```

### Incremental Static Regeneration (ISR)

```typescript
// App Router
export const revalidate = 3600 // Revalidate every hour

// Pages Router
export async function getStaticProps() {
  return {
    props: { /* ... */ },
    revalidate: 3600
  }
}
```

### Client-Side Fetching

**Using SWR**
```typescript
import useSWR from 'swr'

function TaskList() {
  const { data, error, isLoading } = useSWR('/api/tasks', fetcher)

  if (isLoading) return <Spinner />
  if (error) return <Error />

  return <div>{data.map(/* ... */)}</div>
}
```

**Using React Query**
```typescript
import { useQuery } from '@tanstack/react-query'

function TaskList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['tasks'],
    queryFn: fetchTasks
  })

  if (isLoading) return <Spinner />
  if (error) return <Error />

  return <div>{data.map(/* ... */)}</div>
}
```

## State Management Patterns

### Server State vs Client State

**Server State (Data from APIs)**
- Use SWR, React Query, or native fetch with caching
- Handles loading, error, and success states
- Automatic revalidation and background updates

**Client State (UI state)**
- Use React Context, Zustand, or Redux
- Form state, modal visibility, theme preferences
- Local to the application

### Context Pattern

```typescript
// contexts/AuthContext.tsx
'use client'

import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)

  return (
    <AuthContext.Provider value={{ user, setUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
```

### Zustand Pattern (Lightweight State)

```typescript
// stores/taskStore.ts
import { create } from 'zustand'

interface TaskStore {
  tasks: Task[]
  addTask: (task: Task) => void
  removeTask: (id: string) => void
}

export const useTaskStore = create<TaskStore>((set) => ({
  tasks: [],
  addTask: (task) => set((state) => ({ tasks: [...state.tasks, task] })),
  removeTask: (id) => set((state) => ({
    tasks: state.tasks.filter(t => t.id !== id)
  }))
}))
```

### Redux Pattern (Complex State)

```typescript
// store/slices/taskSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit'

const taskSlice = createSlice({
  name: 'tasks',
  initialState: { items: [], loading: false },
  reducers: {
    addTask: (state, action: PayloadAction<Task>) => {
      state.items.push(action.payload)
    },
    removeTask: (state, action: PayloadAction<string>) => {
      state.items = state.items.filter(t => t.id !== action.payload)
    }
  }
})

export const { addTask, removeTask } = taskSlice.actions
export default taskSlice.reducer
```

## API Route Patterns

### RESTful API Routes

```typescript
// app/api/tasks/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const tasks = await fetchTasks()
  return NextResponse.json(tasks)
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  const task = await createTask(body)
  return NextResponse.json(task, { status: 201 })
}
```

### Dynamic API Routes

```typescript
// app/api/tasks/[id]/route.ts
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const task = await fetchTask(params.id)
  if (!task) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 })
  }
  return NextResponse.json(task)
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const body = await request.json()
  const task = await updateTask(params.id, body)
  return NextResponse.json(task)
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  await deleteTask(params.id)
  return NextResponse.json({ success: true }, { status: 204 })
}
```

### Middleware Pattern

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Authentication check
  const token = request.cookies.get('token')

  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/:path*']
}
```

## Error Handling Patterns

### Error Boundaries (App Router)

```typescript
// app/error.tsx
'use client'

export default function Error({
  error,
  reset
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
  )
}
```

### Not Found Pages

```typescript
// app/not-found.tsx
export default function NotFound() {
  return (
    <div>
      <h2>404 - Page Not Found</h2>
      <Link href="/">Go home</Link>
    </div>
  )
}
```

### Loading States

```typescript
// app/tasks/loading.tsx
export default function Loading() {
  return <Spinner />
}
```

## TypeScript Patterns

### Type-Safe API Routes

```typescript
// types/api.ts
export interface Task {
  id: string
  title: string
  completed: boolean
}

export interface ApiResponse<T> {
  data: T
  error?: string
}

// app/api/tasks/route.ts
export async function GET(): Promise<NextResponse<ApiResponse<Task[]>>> {
  const tasks = await fetchTasks()
  return NextResponse.json({ data: tasks })
}
```

### Type-Safe Route Params

```typescript
// types/params.ts
export interface TaskPageParams {
  params: { id: string }
  searchParams: { filter?: string }
}

// app/tasks/[id]/page.tsx
export default function TaskPage({ params, searchParams }: TaskPageParams) {
  // Fully typed params and searchParams
}
```

## Testing Patterns

### Component Testing

```typescript
// __tests__/TaskList.test.tsx
import { render, screen } from '@testing-library/react'
import TaskList from '@/components/TaskList'

describe('TaskList', () => {
  it('renders tasks', () => {
    const tasks = [{ id: '1', title: 'Test Task', completed: false }]
    render(<TaskList tasks={tasks} />)
    expect(screen.getByText('Test Task')).toBeInTheDocument()
  })
})
```

### API Route Testing

```typescript
// __tests__/api/tasks.test.ts
import { GET, POST } from '@/app/api/tasks/route'
import { NextRequest } from 'next/server'

describe('/api/tasks', () => {
  it('returns tasks', async () => {
    const request = new NextRequest('http://localhost:3000/api/tasks')
    const response = await GET(request)
    const data = await response.json()
    expect(Array.isArray(data)).toBe(true)
  })
})
```

### E2E Testing with Playwright

```typescript
// e2e/tasks.spec.ts
import { test, expect } from '@playwright/test'

test('create task flow', async ({ page }) => {
  await page.goto('/tasks')
  await page.click('text=Add Task')
  await page.fill('input[name="title"]', 'New Task')
  await page.click('button[type="submit"]')
  await expect(page.locator('text=New Task')).toBeVisible()
})
```
