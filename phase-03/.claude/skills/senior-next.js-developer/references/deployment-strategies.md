# Next.js Deployment Strategies

## Vercel Deployment

### Initial Setup

**Install Vercel CLI**
```bash
npm install -g vercel
```

**Deploy from CLI**
```bash
vercel
```

**Deploy to Production**
```bash
vercel --prod
```

### Project Configuration

**vercel.json**
```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["iad1"],
  "env": {
    "DATABASE_URL": "@database-url",
    "JWT_SECRET": "@jwt-secret"
  },
  "build": {
    "env": {
      "NEXT_PUBLIC_API_URL": "https://api.example.com"
    }
  }
}
```

### Environment Variables

**Setting via CLI**
```bash
vercel env add DATABASE_URL production
vercel env add JWT_SECRET production
vercel env add NEXT_PUBLIC_API_URL production
```

**Environment Variable Types:**
- **Production**: Used in production deployments
- **Preview**: Used in preview deployments (PRs)
- **Development**: Used locally with `vercel dev`

### Custom Domains

```bash
# Add domain
vercel domains add example.com

# Add domain to project
vercel domains add example.com --project my-project
```

### Deployment Hooks

**GitHub Integration**
- Automatic deployments on push to main (production)
- Preview deployments for pull requests
- Deployment status checks

**Deploy Hooks**
```bash
# Create deploy hook
curl -X POST https://api.vercel.com/v1/integrations/deploy/[hook-id]
```

### Edge Functions

```typescript
// app/api/edge/route.ts
export const runtime = 'edge'

export async function GET(request: Request) {
  return new Response('Hello from Edge!')
}
```

**Edge Middleware**
```typescript
// middleware.ts
export const config = {
  matcher: '/api/:path*',
}

export function middleware(request: Request) {
  // Runs at the edge
  return new Response('Edge middleware')
}
```

## Self-Hosted Deployment

### Docker Deployment

**Dockerfile**
```dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED 1

RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

**next.config.js for Docker**
```javascript
module.exports = {
  output: 'standalone',
}
```

**docker-compose.yml**
```yaml
version: '3.8'

services:
  nextjs:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - JWT_SECRET=${JWT_SECRET}
    restart: unless-stopped
    depends_on:
      - postgres

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=myuser
      - POSTGRES_PASSWORD=mypassword
      - POSTGRES_DB=mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

**Build and Run**
```bash
docker-compose up -d
```

### Node.js Server Deployment

**Build for Production**
```bash
npm run build
```

**Start Production Server**
```bash
npm start
```

**PM2 Process Manager**
```bash
# Install PM2
npm install -g pm2

# Start application
pm2 start npm --name "nextjs-app" -- start

# Save PM2 configuration
pm2 save

# Setup startup script
pm2 startup
```

**ecosystem.config.js**
```javascript
module.exports = {
  apps: [{
    name: 'nextjs-app',
    script: 'npm',
    args: 'start',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      PORT: 3000,
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
  }]
}
```

### Nginx Reverse Proxy

**nginx.conf**
```nginx
upstream nextjs_upstream {
  server localhost:3000;
}

server {
  listen 80;
  server_name example.com;

  # Redirect HTTP to HTTPS
  return 301 https://$server_name$request_uri;
}

server {
  listen 443 ssl http2;
  server_name example.com;

  ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

  # Security headers
  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
  add_header X-Frame-Options "DENY" always;
  add_header X-Content-Type-Options "nosniff" always;

  # Gzip compression
  gzip on;
  gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

  location / {
    proxy_pass http://nextjs_upstream;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
  }

  # Cache static assets
  location /_next/static {
    proxy_pass http://nextjs_upstream;
    proxy_cache_valid 200 365d;
    add_header Cache-Control "public, immutable";
  }
}
```

## AWS Deployment

### AWS Amplify

**amplify.yml**
```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: .next
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
      - .next/cache/**/*
```

### AWS ECS (Elastic Container Service)

**Task Definition**
```json
{
  "family": "nextjs-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "nextjs",
      "image": "your-ecr-repo/nextjs-app:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "NODE_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:db-url"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/nextjs-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### AWS Lambda (Serverless)

**Using SST (Serverless Stack)**
```typescript
// sst.config.ts
import { SSTConfig } from 'sst'
import { NextjsSite } from 'sst/constructs'

export default {
  config(_input) {
    return {
      name: 'nextjs-app',
      region: 'us-east-1',
    }
  },
  stacks(app) {
    app.stack(function Site({ stack }) {
      const site = new NextjsSite(stack, 'site', {
        environment: {
          DATABASE_URL: process.env.DATABASE_URL!,
        },
      })

      stack.addOutputs({
        SiteUrl: site.url,
      })
    })
  },
} satisfies SSTConfig
```

## CI/CD Pipelines

### GitHub Actions

**.github/workflows/deploy.yml**
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Run linter
        run: npm run lint

      - name: Build application
        run: npm run build
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          JWT_SECRET: ${{ secrets.JWT_SECRET }}

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

**Docker Build and Push**
```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: username/nextjs-app:latest
          cache-from: type=registry,ref=username/nextjs-app:buildcache
          cache-to: type=registry,ref=username/nextjs-app:buildcache,mode=max
```

### GitLab CI/CD

**.gitlab-ci.yml**
```yaml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

test:
  stage: test
  image: node:18-alpine
  script:
    - npm ci
    - npm run lint
    - npm test
  cache:
    paths:
      - node_modules/

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $DOCKER_IMAGE .
    - docker push $DOCKER_IMAGE
  only:
    - main

deploy:
  stage: deploy
  image: alpine:latest
  script:
    - apk add --no-cache curl
    - curl -X POST $DEPLOY_WEBHOOK_URL
  only:
    - main
```

## Monitoring and Logging

### Sentry Integration

**Installation**
```bash
npm install @sentry/nextjs
```

**sentry.client.config.ts**
```typescript
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
})
```

**sentry.server.config.ts**
```typescript
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 1.0,
})
```

### Logging with Winston

```typescript
// lib/logger.ts
import winston from 'winston'

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
})

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple(),
  }))
}

export default logger
```

### Health Check Endpoint

```typescript
// app/api/health/route.ts
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Check database connection
    await checkDatabaseConnection()

    // Check external services
    await checkExternalServices()

    return NextResponse.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
    })
  } catch (error) {
    return NextResponse.json(
      {
        status: 'unhealthy',
        error: error.message,
      },
      { status: 503 }
    )
  }
}
```

## Performance Monitoring

### Vercel Analytics

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

### Custom Metrics

```typescript
// lib/metrics.ts
export function trackMetric(name: string, value: number, tags?: Record<string, string>) {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', name, {
      value,
      ...tags,
    })
  }

  // Send to your metrics service
  fetch('/api/metrics', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, value, tags }),
  })
}

// Usage
trackMetric('api_response_time', 150, { endpoint: '/api/tasks' })
```

## Database Migrations

### Prisma Migrations

```bash
# Create migration
npx prisma migrate dev --name add_user_table

# Apply migrations in production
npx prisma migrate deploy

# Generate Prisma Client
npx prisma generate
```

**Deployment Script**
```bash
#!/bin/bash
set -e

echo "Running database migrations..."
npx prisma migrate deploy

echo "Starting application..."
npm start
```

### Drizzle Migrations

```bash
# Generate migrations
npx drizzle-kit generate:pg

# Apply migrations
npx drizzle-kit push:pg
```

## Zero-Downtime Deployment

### Blue-Green Deployment

```bash
# Deploy new version (green)
docker-compose -f docker-compose.green.yml up -d

# Run health checks
./scripts/health-check.sh green

# Switch traffic to green
./scripts/switch-traffic.sh green

# Stop old version (blue)
docker-compose -f docker-compose.blue.yml down
```

### Rolling Updates (Kubernetes)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nextjs-app
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    spec:
      containers:
      - name: nextjs
        image: nextjs-app:latest
        readinessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Deployment Checklist

### Pre-Deployment
- [ ] Run all tests (unit, integration, E2E)
- [ ] Run linter and type checker
- [ ] Build application successfully
- [ ] Test build locally
- [ ] Review environment variables
- [ ] Check database migration scripts
- [ ] Review security headers configuration
- [ ] Verify CORS settings

### Deployment
- [ ] Deploy to staging first
- [ ] Run smoke tests on staging
- [ ] Check monitoring dashboards
- [ ] Verify health check endpoint
- [ ] Test critical user flows
- [ ] Deploy to production
- [ ] Monitor error rates
- [ ] Check performance metrics

### Post-Deployment
- [ ] Verify application is accessible
- [ ] Check logs for errors
- [ ] Monitor Core Web Vitals
- [ ] Test critical features
- [ ] Verify database connections
- [ ] Check external service integrations
- [ ] Monitor resource usage (CPU, memory)
- [ ] Set up alerts for anomalies

### Rollback Plan
- [ ] Document rollback procedure
- [ ] Keep previous version available
- [ ] Test rollback in staging
- [ ] Monitor for issues requiring rollback
- [ ] Have database rollback scripts ready
