# Next.js Performance Optimization

## Core Web Vitals

### Understanding the Metrics

**Largest Contentful Paint (LCP)**
- Measures loading performance
- Target: < 2.5 seconds
- Affected by: Server response time, render-blocking resources, slow resource load times

**First Input Delay (FID) / Interaction to Next Paint (INP)**
- Measures interactivity
- FID Target: < 100ms
- INP Target: < 200ms
- Affected by: JavaScript execution time, long tasks

**Cumulative Layout Shift (CLS)**
- Measures visual stability
- Target: < 0.1
- Affected by: Images without dimensions, dynamic content injection, web fonts

### Measuring Core Web Vitals

```typescript
// app/layout.tsx
import { Analytics } from '@vercel/analytics/react'
import { SpeedInsights } from '@vercel/speed-insights/next'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  )
}
```

**Using web-vitals Library**
```typescript
// lib/vitals.ts
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'

export function reportWebVitals() {
  getCLS(console.log)
  getFID(console.log)
  getFCP(console.log)
  getLCP(console.log)
  getTTFB(console.log)
}
```

## Bundle Optimization

### Bundle Analysis

**Setup @next/bundle-analyzer**
```bash
npm install @next/bundle-analyzer
```

```javascript
// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

module.exports = withBundleAnalyzer({
  // Your Next.js config
})
```

**Run Analysis**
```bash
ANALYZE=true npm run build
```

### Code Splitting Strategies

**Dynamic Imports**
```typescript
// Lazy load heavy components
import dynamic from 'next/dynamic'

const HeavyChart = dynamic(() => import('@/components/HeavyChart'), {
  loading: () => <Spinner />,
  ssr: false // Disable SSR for client-only components
})

export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <HeavyChart />
    </div>
  )
}
```

**Route-Based Code Splitting**
```typescript
// Automatically split by route in App Router
// Each page.tsx creates a separate bundle
```

**Component-Level Splitting**
```typescript
// Split large component libraries
const Button = dynamic(() => import('@/components/ui/Button'))
const Modal = dynamic(() => import('@/components/ui/Modal'))
const Dropdown = dynamic(() => import('@/components/ui/Dropdown'))
```

### Tree Shaking

**Import Only What You Need**
```typescript
// ❌ Bad: Imports entire library
import _ from 'lodash'

// ✅ Good: Import specific functions
import debounce from 'lodash/debounce'
import throttle from 'lodash/throttle'

// ✅ Better: Use ES modules
import { debounce, throttle } from 'lodash-es'
```

**Configure next.config.js**
```javascript
module.exports = {
  webpack: (config) => {
    config.optimization.usedExports = true
    return config
  }
}
```

### Dependency Optimization

**Analyze Package Sizes**
```bash
npm install -g bundle-phobia-cli
bundle-phobia [package-name]
```

**Replace Heavy Dependencies**
```typescript
// ❌ Heavy: moment.js (67.9kB)
import moment from 'moment'

// ✅ Lightweight: date-fns (13.4kB)
import { format, parseISO } from 'date-fns'

// ✅ Native: Intl API (0kB)
new Intl.DateTimeFormat('en-US').format(new Date())
```

## Image Optimization

### Next.js Image Component

**Basic Usage**
```typescript
import Image from 'next/image'

export function ProductImage() {
  return (
    <Image
      src="/product.jpg"
      alt="Product"
      width={500}
      height={300}
      priority // Load immediately for above-fold images
    />
  )
}
```

**Responsive Images**
```typescript
<Image
  src="/hero.jpg"
  alt="Hero"
  fill
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  style={{ objectFit: 'cover' }}
/>
```

**External Images**
```javascript
// next.config.js
module.exports = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.example.com',
        port: '',
        pathname: '/uploads/**',
      },
    ],
  },
}
```

### Image Optimization Strategies

**Lazy Loading**
```typescript
// Images below the fold are lazy loaded by default
<Image
  src="/below-fold.jpg"
  alt="Below fold"
  width={500}
  height={300}
  loading="lazy" // Default behavior
/>
```

**Blur Placeholder**
```typescript
<Image
  src="/product.jpg"
  alt="Product"
  width={500}
  height={300}
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRg..." // Generate with plaiceholder
/>
```

**Modern Formats**
```javascript
// next.config.js
module.exports = {
  images: {
    formats: ['image/avif', 'image/webp'], // Serve modern formats
  },
}
```

### Image CDN Integration

```javascript
// next.config.js
module.exports = {
  images: {
    loader: 'cloudinary',
    path: 'https://res.cloudinary.com/demo/image/upload/',
  },
}
```

## Font Optimization

### Next.js Font Optimization

**Using next/font**
```typescript
// app/layout.tsx
import { Inter, Roboto_Mono } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

const robotoMono = Roboto_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-roboto-mono',
})

export default function RootLayout({ children }) {
  return (
    <html className={`${inter.variable} ${robotoMono.variable}`}>
      <body>{children}</body>
    </html>
  )
}
```

**Local Fonts**
```typescript
import localFont from 'next/font/local'

const customFont = localFont({
  src: './fonts/CustomFont.woff2',
  display: 'swap',
  variable: '--font-custom',
})
```

**Font Display Strategies**
- `swap`: Show fallback immediately, swap when font loads (best for performance)
- `optional`: Use font if available within 100ms, otherwise use fallback
- `block`: Hide text until font loads (avoid FOIT)
- `fallback`: Brief block period, then swap

## Caching Strategies

### App Router Caching

**Fetch Caching**
```typescript
// Cache for 1 hour
const data = await fetch('https://api.example.com/data', {
  next: { revalidate: 3600 }
})

// No caching (always fresh)
const data = await fetch('https://api.example.com/data', {
  cache: 'no-store'
})

// Cache indefinitely (until revalidated)
const data = await fetch('https://api.example.com/data', {
  cache: 'force-cache'
})
```

**Route Segment Config**
```typescript
// app/dashboard/page.tsx
export const revalidate = 3600 // Revalidate every hour
export const dynamic = 'force-dynamic' // Always dynamic
export const fetchCache = 'force-cache' // Force cache all fetches

export default async function DashboardPage() {
  // ...
}
```

**On-Demand Revalidation**
```typescript
// app/api/revalidate/route.ts
import { revalidatePath, revalidateTag } from 'next/cache'

export async function POST(request: Request) {
  const { path, tag } = await request.json()

  if (path) {
    revalidatePath(path)
  }

  if (tag) {
    revalidateTag(tag)
  }

  return Response.json({ revalidated: true })
}
```

**Tagged Caching**
```typescript
// Fetch with tags
const data = await fetch('https://api.example.com/posts', {
  next: { tags: ['posts'] }
})

// Revalidate by tag
revalidateTag('posts')
```

### Client-Side Caching

**SWR Configuration**
```typescript
import useSWR from 'swr'

function TaskList() {
  const { data, error } = useSWR('/api/tasks', fetcher, {
    revalidateOnFocus: false,
    revalidateOnReconnect: true,
    dedupingInterval: 2000,
    refreshInterval: 0,
  })
}
```

**React Query Configuration**
```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
    },
  },
})
```

### HTTP Caching Headers

```typescript
// app/api/data/route.ts
export async function GET() {
  const data = await fetchData()

  return new Response(JSON.stringify(data), {
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'public, s-maxage=3600, stale-while-revalidate=86400',
    },
  })
}
```

## JavaScript Optimization

### Reduce JavaScript Execution

**Server Components First**
```typescript
// ✅ Good: Server component (no JS sent to client)
async function TaskList() {
  const tasks = await fetchTasks()
  return <ul>{tasks.map(/* ... */)}</ul>
}

// ❌ Bad: Client component when not needed
'use client'
function TaskList() {
  const [tasks, setTasks] = useState([])
  useEffect(() => { fetchTasks().then(setTasks) }, [])
  return <ul>{tasks.map(/* ... */)}</ul>
}
```

**Minimize Client-Side JavaScript**
```typescript
// Only mark interactive parts as client components
export default function Page() {
  return (
    <div>
      <StaticHeader /> {/* Server component */}
      <InteractiveForm /> {/* Client component */}
      <StaticFooter /> {/* Server component */}
    </div>
  )
}
```

### Debouncing and Throttling

```typescript
import { useDebouncedCallback } from 'use-debounce'

function SearchInput() {
  const debouncedSearch = useDebouncedCallback(
    (value) => {
      // API call
      searchAPI(value)
    },
    500 // Wait 500ms after user stops typing
  )

  return (
    <input
      type="text"
      onChange={(e) => debouncedSearch(e.target.value)}
    />
  )
}
```

### Web Workers

```typescript
// workers/heavy-computation.ts
self.addEventListener('message', (e) => {
  const result = performHeavyComputation(e.data)
  self.postMessage(result)
})

// components/DataProcessor.tsx
'use client'

export function DataProcessor() {
  useEffect(() => {
    const worker = new Worker(new URL('../workers/heavy-computation.ts', import.meta.url))

    worker.postMessage(data)
    worker.onmessage = (e) => {
      console.log('Result:', e.data)
    }

    return () => worker.terminate()
  }, [])
}
```

## Rendering Strategies

### Static Generation (SSG)

**Best for:**
- Marketing pages
- Blog posts
- Documentation
- Product pages

```typescript
// app/blog/[slug]/page.tsx
export async function generateStaticParams() {
  const posts = await fetchPosts()
  return posts.map((post) => ({ slug: post.slug }))
}

export default async function BlogPost({ params }) {
  const post = await fetchPost(params.slug)
  return <Article post={post} />
}
```

### Incremental Static Regeneration (ISR)

**Best for:**
- E-commerce product pages
- News articles
- Content that updates periodically

```typescript
// Revalidate every hour
export const revalidate = 3600

export default async function ProductPage({ params }) {
  const product = await fetchProduct(params.id)
  return <ProductDetails product={product} />
}
```

### Server-Side Rendering (SSR)

**Best for:**
- Personalized content
- Real-time data
- Authentication-dependent pages

```typescript
// Force dynamic rendering
export const dynamic = 'force-dynamic'

export default async function DashboardPage() {
  const user = await getCurrentUser()
  const data = await fetchUserData(user.id)
  return <Dashboard data={data} />
}
```

### Client-Side Rendering (CSR)

**Best for:**
- Highly interactive UIs
- Real-time updates
- User-specific data after initial load

```typescript
'use client'

export function LiveDashboard() {
  const { data } = useSWR('/api/live-data', fetcher, {
    refreshInterval: 1000 // Update every second
  })

  return <RealtimeChart data={data} />
}
```

## Database Query Optimization

### Connection Pooling

```typescript
// lib/db.ts
import { Pool } from 'pg'

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20, // Maximum connections
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
})

export async function query(text: string, params?: any[]) {
  const start = Date.now()
  const res = await pool.query(text, params)
  const duration = Date.now() - start
  console.log('Executed query', { text, duration, rows: res.rowCount })
  return res
}
```

### Query Optimization

```typescript
// ❌ Bad: N+1 query problem
async function getTasks() {
  const tasks = await db.query('SELECT * FROM tasks')
  for (const task of tasks) {
    task.user = await db.query('SELECT * FROM users WHERE id = $1', [task.user_id])
  }
  return tasks
}

// ✅ Good: Single query with JOIN
async function getTasks() {
  return db.query(`
    SELECT tasks.*, users.name as user_name
    FROM tasks
    LEFT JOIN users ON tasks.user_id = users.id
  `)
}
```

### Pagination

```typescript
// Offset-based pagination (simple but slower for large offsets)
async function getTasks(page: number, limit: number) {
  const offset = (page - 1) * limit
  return db.query('SELECT * FROM tasks LIMIT $1 OFFSET $2', [limit, offset])
}

// Cursor-based pagination (faster, better for infinite scroll)
async function getTasks(cursor?: string, limit: number = 20) {
  if (cursor) {
    return db.query(
      'SELECT * FROM tasks WHERE id > $1 ORDER BY id LIMIT $2',
      [cursor, limit]
    )
  }
  return db.query('SELECT * FROM tasks ORDER BY id LIMIT $1', [limit])
}
```

## Monitoring and Profiling

### Performance Monitoring

**Vercel Analytics**
```typescript
// app/layout.tsx
import { Analytics } from '@vercel/analytics/react'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
```

**Custom Performance Tracking**
```typescript
// lib/performance.ts
export function measurePerformance(name: string, fn: () => void) {
  const start = performance.now()
  fn()
  const end = performance.now()
  console.log(`${name} took ${end - start}ms`)
}

// Usage
measurePerformance('Data Processing', () => {
  processLargeDataset(data)
})
```

### React Profiler

```typescript
import { Profiler } from 'react'

function onRenderCallback(
  id: string,
  phase: 'mount' | 'update',
  actualDuration: number,
) {
  console.log(`${id} (${phase}) took ${actualDuration}ms`)
}

export default function App() {
  return (
    <Profiler id="App" onRender={onRenderCallback}>
      <Dashboard />
    </Profiler>
  )
}
```

## Performance Checklist

### Initial Load Performance
- [ ] Enable compression (gzip/brotli)
- [ ] Minimize bundle size (<200KB initial JS)
- [ ] Use code splitting for routes and components
- [ ] Optimize images with next/image
- [ ] Preload critical resources
- [ ] Use font-display: swap
- [ ] Implement proper caching headers

### Runtime Performance
- [ ] Use Server Components by default
- [ ] Minimize client-side JavaScript
- [ ] Debounce/throttle expensive operations
- [ ] Use React.memo for expensive components
- [ ] Implement virtual scrolling for long lists
- [ ] Avoid unnecessary re-renders

### Data Fetching Performance
- [ ] Use appropriate rendering strategy (SSG/ISR/SSR)
- [ ] Implement proper caching (fetch cache, SWR, React Query)
- [ ] Optimize database queries (avoid N+1)
- [ ] Use connection pooling
- [ ] Implement pagination for large datasets

### Core Web Vitals
- [ ] LCP < 2.5s (optimize largest content)
- [ ] FID < 100ms (reduce JavaScript execution)
- [ ] CLS < 0.1 (set image dimensions, avoid layout shifts)
- [ ] Monitor with Vercel Analytics or web-vitals

### Monitoring
- [ ] Set up performance monitoring (Vercel Analytics, Sentry)
- [ ] Track Core Web Vitals
- [ ] Monitor bundle size over time
- [ ] Set up alerts for performance regressions
