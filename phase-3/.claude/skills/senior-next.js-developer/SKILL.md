---
name: "senior-nextjs-developer"
description: |
  Expert Next.js development skills covering advanced architecture, performance optimization, security, deployment, and enterprise-level implementations.
  This skill should be used when working on complex Next.js projects requiring senior-level expertise in full-stack development, optimization, and scalable application design, or when users ask for advanced Next.js guidance, performance tuning, security implementation, or production deployment strategies.
---

# Senior Next.js Developer Skill

Provide expert-level guidance for building production-ready Next.js applications with advanced architecture, performance optimization, security implementation, and deployment strategies.

## What This Skill Does

- Design scalable Next.js application architectures (App Router and Pages Router)
- Implement performance optimizations (Core Web Vitals, bundle size, caching)
- Configure security best practices (authentication, authorization, input validation)
- Guide deployment strategies (Vercel, self-hosted, Docker, AWS)
- Troubleshoot complex Next.js issues with senior-level expertise

## What This Skill Does NOT Do

- Basic Next.js tutorials (use official docs for beginners)
- Framework comparisons (React vs Vue vs Angular)
- Non-Next.js React applications
- Backend-only API development without frontend
- Mobile app development (React Native)

---

## Version Compatibility

This skill covers:
- **Next.js**: 13.x and 14.x (App Router and Pages Router)
- **React**: 18.x
- **Node.js**: 18+ LTS
- **TypeScript**: 5.x

For latest patterns and breaking changes, consult official Next.js documentation.

---

## Required Clarifications

Before implementation, clarify:

1. **Project type**: New project or existing codebase?
2. **Next.js version**: App Router (13+) or Pages Router (12.x)?
3. **Deployment target**: Vercel, self-hosted, Docker, AWS, or other platform?

## Optional Clarifications

4. **State management**: Preference for Redux, Zustand, Context, or other?
5. **Authentication**: NextAuth.js, custom JWT, Better Auth, or other solution?
6. **Database**: PostgreSQL, MongoDB, MySQL, or other?
7. **Styling**: Tailwind CSS, CSS Modules, styled-components, or other?

**If user doesn't provide clarifications**: Use sensible defaults (App Router, Vercel deployment, Context for state, NextAuth.js for auth) and document assumptions made.

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing Next.js version, current architecture, dependencies, folder structure |
| **Conversation** | User's specific requirements, constraints, preferences, performance goals |
| **Skill References** | Next.js patterns, best practices, optimization techniques from `references/` |
| **User Guidelines** | Project-specific conventions, team standards, deployment requirements |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

---

## Official Documentation

| Resource | URL | Use For |
|----------|-----|---------|
| Next.js Docs | https://nextjs.org/docs | Core framework patterns, API reference |
| React Docs | https://react.dev | Component patterns, hooks, best practices |
| Vercel Guides | https://vercel.com/guides | Deployment strategies, platform features |
| Next.js Examples | https://github.com/vercel/next.js/tree/canary/examples | Reference implementations |
| Next.js Blog | https://nextjs.org/blog | Latest features, migration guides |

---

## Core Competencies

### 1. Advanced Architecture & Performance
- Application architecture with proper folder structures and component organization
- Performance optimization with bundle analysis, code splitting, and Core Web Vitals improvements
- Caching strategies using ISR, SSR, SSG, and advanced patterns
- Database integration with optimized queries and connection pooling

**Details**: See `references/architecture-patterns.md` and `references/performance-optimization.md`

### 2. Security Implementation
- Authentication and authorization with secure best practices
- Input validation and sanitization for all user inputs
- Environment configuration with secure variable management
- Security headers (CSP, CORS, CSRF protection)

**Details**: See `references/security-best-practices.md`

### 3. Full-Stack Development
- Robust API routes with error handling, validation, and rate limiting
- Complex state management with Redux, Zustand, or React Context
- Authentication systems with JWT, OAuth, or custom flows
- Third-party integrations with external APIs and services

**Details**: See `references/architecture-patterns.md` → "API Route Patterns"

### 4. Deployment & DevOps
- Optimized deployments on Vercel, Netlify, or custom platforms
- CI/CD pipelines with automated testing and deployment
- Monitoring with error tracking and performance metrics
- Environment management for staging and production

**Details**: See `references/deployment-strategies.md`

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Using Client Components Everywhere
**Problem**: Sending unnecessary JavaScript to the client, impacting performance

**Solution**: Use Server Components by default, only mark interactive parts as client components
```typescript
// ✅ Good: Server component for static content
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

### ❌ Mistake 2: Not Optimizing Images
**Problem**: Large image files slow down page load, poor Core Web Vitals

**Solution**: Use next/image component with proper sizing
```typescript
import Image from 'next/image'

<Image
  src="/product.jpg"
  alt="Product"
  width={500}
  height={300}
  priority // For above-fold images
/>
```

### ❌ Mistake 3: Ignoring Bundle Size
**Problem**: Large JavaScript bundles increase load time

**Solution**: Use dynamic imports and bundle analyzer
```typescript
import dynamic from 'next/dynamic'

const HeavyChart = dynamic(() => import('@/components/HeavyChart'), {
  loading: () => <Spinner />,
  ssr: false
})
```

### ❌ Mistake 4: Missing Security Headers
**Problem**: Application vulnerable to XSS, clickjacking, and other attacks

**Solution**: Configure security headers in next.config.js

**Details**: See `references/security-best-practices.md` → "Security Headers"

### ❌ Mistake 5: Not Implementing Proper Caching
**Problem**: Unnecessary API calls and slow page loads

**Solution**: Use appropriate caching strategy (ISR, SSG, fetch cache)

**Details**: See `references/performance-optimization.md` → "Caching Strategies"

### ❌ Mistake 6: Hardcoding Environment Variables
**Problem**: Security risk, difficult to manage across environments

**Solution**: Use .env files and validate at startup

**Details**: See `references/security-best-practices.md` → "Environment Variables Security"

---

## Implementation Workflows

### 1. New Project Setup
```
1. Initialize Next.js project (npx create-next-app@latest)
2. Configure TypeScript and ESLint
3. Set up folder structure (see architecture-patterns.md)
4. Install core dependencies (state management, UI library)
5. Configure environment variables
6. Set up authentication (NextAuth.js or custom)
7. Implement base layout and navigation
```

### 2. Performance Optimization
```
1. Run bundle analyzer (@next/bundle-analyzer)
2. Identify large dependencies and replace if possible
3. Implement code splitting with dynamic imports
4. Optimize images with next/image
5. Configure caching strategy (ISR, SSG, or SSR)
6. Measure Core Web Vitals (Vercel Analytics)
7. Optimize fonts with next/font
```

### 3. Security Hardening
```
1. Implement authentication (NextAuth.js or JWT)
2. Add input validation (Zod schemas)
3. Configure security headers (CSP, CORS)
4. Implement CSRF protection
5. Add rate limiting to API routes
6. Validate environment variables
7. Run security audit (npm audit)
```

### 4. Production Deployment
```
1. Run tests and linter
2. Build application (npm run build)
3. Test build locally
4. Configure environment variables for production
5. Set up monitoring (Sentry, Vercel Analytics)
6. Deploy to platform (Vercel, Docker, AWS)
7. Verify deployment and run smoke tests
```

**Detailed workflows**: See reference files for comprehensive guides

---

## Key Implementation Patterns

### Performance Optimization Checklist
- [ ] Bundle Analysis: Use `@next/bundle-analyzer` to identify large dependencies
- [ ] Image Optimization: Use `<Image>` component with proper sizing and lazy loading
- [ ] Font Optimization: Use `next/font` with font-display: swap
- [ ] Core Web Vitals: Optimize LCP (<2.5s), FID (<100ms), CLS (<0.1)
- [ ] Code Splitting: Use dynamic imports for heavy components
- [ ] Caching: Implement appropriate strategy (ISR, SSG, SSR)

### Security Implementation Checklist
- [ ] Authentication: Implement NextAuth.js or custom JWT authentication
- [ ] Authorization: Protect routes and API endpoints with proper access controls
- [ ] Input Validation: Use Zod or Joi for server-side validation
- [ ] Security Headers: Configure CSP, X-Frame-Options, HSTS
- [ ] CSRF Protection: Implement token-based CSRF protection
- [ ] Rate Limiting: Add rate limiting to authentication and API endpoints
- [ ] Environment Variables: Validate and secure all environment variables

### Deployment Checklist
- [ ] Tests: Run all tests (unit, integration, E2E)
- [ ] Linter: Run ESLint and TypeScript type checker
- [ ] Build: Build application successfully
- [ ] Environment: Configure production environment variables
- [ ] Monitoring: Set up error tracking (Sentry) and analytics
- [ ] Health Check: Implement /api/health endpoint
- [ ] CI/CD: Configure automated deployment pipeline

---

## Reference Files

Search patterns for comprehensive guides:

| File | Lines | Search For |
|------|-------|------------|
| `architecture-patterns.md` | 600+ | "folder structure", "component patterns", "routing", "state management" |
| `performance-optimization.md` | 500+ | "Core Web Vitals", "bundle size", "caching", "image optimization" |
| `security-best-practices.md` | 700+ | "authentication", "authorization", "input validation", "security headers" |
| `deployment-strategies.md` | 600+ | "Vercel", "Docker", "AWS", "CI/CD", "monitoring" |

**Reference contents**:
- `architecture-patterns.md` - Project structures, component patterns, routing, API routes, state management
- `performance-optimization.md` - Core Web Vitals, bundle optimization, caching, database optimization
- `security-best-practices.md` - Authentication, authorization, input validation, security headers, CSRF
- `deployment-strategies.md` - Vercel, Docker, AWS, CI/CD pipelines, monitoring, zero-downtime deployment

---

## Output Format

When providing guidance, structure responses as:

**Architecture Summary**: Recommended project structure and patterns
**Performance Strategy**: Optimization techniques and tools to implement
**Security Measures**: Authentication, authorization, and protection mechanisms
**Implementation Plan**: Step-by-step approach with code examples
**Deployment Strategy**: Production-ready configuration and monitoring setup

---

## Quality Criteria

Before delivering implementation:

- [ ] **Architecture**: Scalable, maintainable, follows Next.js best practices
- [ ] **Performance**: Optimized for Core Web Vitals and fast loading times
- [ ] **Security**: Implements proper authentication, validation, and protection
- [ ] **Code Quality**: Clean, well-documented, follows TypeScript best practices
- [ ] **Testing**: Comprehensive test coverage with unit, integration, and E2E tests
- [ ] **Deployment**: Production-ready with monitoring and error tracking

---

## Example Usage

**Input**: "Help me optimize a Next.js e-commerce site for performance and security"

**Output**:

**Architecture Summary**:
- App Router structure with route groups for organization
- Server Components for product listings, Client Components for cart
- API routes for checkout with proper validation

**Performance Strategy**:
- Implement ISR for product pages (revalidate: 3600)
- Use next/image for all product images with blur placeholders
- Apply code splitting with dynamic imports for heavy components (reviews, recommendations)
- Add bundle analysis to identify and replace large dependencies

**Security Measures**:
- Implement NextAuth.js with credentials provider for user authentication
- Add Zod validation for all form inputs and API requests
- Configure security headers (CSP, X-Frame-Options, HSTS)
- Implement CSRF protection for checkout forms
- Add rate limiting to authentication and checkout endpoints

**Implementation Plan**:
1. Set up NextAuth.js with secure session configuration
2. Create protected routes for checkout and user dashboard
3. Implement product pages with ISR and proper caching
4. Add image optimization with next/image and blur placeholders
5. Configure security headers in next.config.js
6. Add input validation with Zod schemas
7. Implement rate limiting middleware

**Deployment Strategy**:
- Deploy on Vercel with environment-specific configurations
- Set up Sentry for error tracking and monitoring
- Implement performance monitoring with Vercel Analytics
- Configure CI/CD pipeline with GitHub Actions
- Add health check endpoint for monitoring

**Next Steps**: Review `references/performance-optimization.md` for detailed caching strategies and `references/security-best-practices.md` for complete security implementation guide.
