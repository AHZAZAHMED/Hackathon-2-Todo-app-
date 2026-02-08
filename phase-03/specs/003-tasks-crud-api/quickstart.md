# Quickstart Guide: Backend API + Database Persistence

**Feature**: Backend API + Database Persistence (003-tasks-crud-api)
**Date**: 2026-02-06
**Estimated Setup Time**: 15-20 minutes

## Overview

This guide walks you through setting up and running the Task CRUD API backend. The backend extends existing infrastructure (JWT verification, database connection) with new Task model and endpoints.

## Prerequisites

Before starting, ensure you have:

- ✅ Python 3.11+ installed
- ✅ PostgreSQL database (Neon Serverless) accessible
- ✅ DATABASE_URL environment variable configured
- ✅ BETTER_AUTH_SECRET environment variable configured (matches frontend)
- ✅ Frontend already running with Better Auth authentication
- ✅ Git repository cloned

## Quick Start (5 Steps)

### Step 1: Verify Environment Variables

Check that `backend/.env` exists with required variables:

```bash
cd backend
cat .env
```

**Required Variables**:
```bash
DATABASE_URL=postgresql://user:password@host:5432/database
BETTER_AUTH_SECRET=your-64-character-secret-here
FRONTEND_URL=http://localhost:3000
HOST=0.0.0.0
PORT=8000
```

**If `.env` doesn't exist**, copy from template:
```bash
cp .env.example .env
# Edit .env with your actual values
```

**Verify BETTER_AUTH_SECRET matches frontend**:
```bash
# Backend
grep BETTER_AUTH_SECRET backend/.env

# Frontend
grep BETTER_AUTH_SECRET frontend/.env.local
```

⚠️ **CRITICAL**: BETTER_AUTH_SECRET must be identical in both frontend and backend!

---

### Step 2: Install Python Dependencies

```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Expected Dependencies**:
- fastapi>=0.104.0
- sqlmodel>=0.0.14
- pyjwt>=2.8.0
- uvicorn>=0.24.0
- psycopg2-binary>=2.9.0
- python-dotenv>=1.0.0

**Verify Installation**:
```bash
python -c "import fastapi, sqlmodel, jwt; print('Dependencies OK')"
```

---

### Step 3: Run Database Migration

Create the tasks table with indexes and foreign key constraints:

```bash
# From backend/ directory
psql $DATABASE_URL -f migrations/002_create_tasks_table.sql
```

**Expected Output**:
```
CREATE TABLE
CREATE INDEX
CREATE INDEX
```

**Verify Migration**:
```bash
# Check table exists
psql $DATABASE_URL -c "\d tasks"

# Check indexes
psql $DATABASE_URL -c "\di tasks*"

# Check foreign key
psql $DATABASE_URL -c "\d+ tasks" | grep FOREIGN
```

**Expected Table Structure**:
```
Column      | Type                     | Nullable | Default
------------+--------------------------+----------+---------
id          | integer                  | not null | nextval(...)
user_id     | text                     | not null |
title       | character varying(500)   | not null |
description | text                     |          |
completed   | boolean                  | not null | false
created_at  | timestamp                | not null | now()
updated_at  | timestamp                | not null | now()

Indexes:
  "tasks_pkey" PRIMARY KEY, btree (id)
  "idx_tasks_completed" btree (completed)
  "idx_tasks_user_id" btree (user_id)

Foreign-key constraints:
  "tasks_user_id_fkey" FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
```

---

### Step 4: Start Backend Server

```bash
# From backend/ directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify Backend Running**:
```bash
# Health check
curl http://localhost:8000/

# Expected: {"message": "FastAPI backend is running"}

# Check OpenAPI docs
open http://localhost:8000/docs
```

**Verify Task Endpoints Registered**:
- Navigate to http://localhost:8000/docs
- Look for `/api/tasks` endpoints (should see 6 endpoints)

---

### Step 5: Test with Frontend

```bash
# In separate terminal, start frontend
cd frontend
npm run dev
```

**Test Flow**:
1. Open http://localhost:3000
2. Login with existing user (or signup)
3. Click "Add Task" button
4. Enter task title and description
5. Click "Save"
6. Verify task appears in list
7. Refresh page - task should persist

**Verify Database Persistence**:
```bash
# Check tasks in database
psql $DATABASE_URL -c "SELECT id, user_id, title, completed FROM tasks;"
```

---

## Detailed Setup

### Environment Configuration

#### Backend `.env` File

Create `backend/.env` with these variables:

```bash
# Database Connection
DATABASE_URL=postgresql://username:password@host:5432/database

# JWT Authentication (MUST match frontend)
BETTER_AUTH_SECRET=your-64-character-hex-secret-here

# CORS Configuration
FRONTEND_URL=http://localhost:3000

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

#### Frontend `.env.local` File

Verify `frontend/.env.local` has matching secret:

```bash
# Better Auth Configuration
BETTER_AUTH_SECRET=your-64-character-hex-secret-here  # MUST match backend
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://username:password@host:5432/database

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

---

### Database Setup

#### Option 1: Neon Serverless (Recommended)

1. Create Neon project at https://neon.tech
2. Copy connection string
3. Set DATABASE_URL in both frontend and backend `.env` files

#### Option 2: Local PostgreSQL

```bash
# Install PostgreSQL
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql

# Start PostgreSQL
# macOS: brew services start postgresql
# Ubuntu: sudo systemctl start postgresql

# Create database
createdb todo_app

# Set DATABASE_URL
export DATABASE_URL=postgresql://localhost:5432/todo_app
```

---

### Troubleshooting

#### Problem: Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

---

#### Problem: Database connection fails

**Error**: `could not connect to server: Connection refused`

**Solution**:
1. Verify DATABASE_URL is correct
2. Check database is running
3. Test connection: `psql $DATABASE_URL -c "SELECT 1;"`

---

#### Problem: JWT verification fails

**Error**: `401 Unauthorized` on all requests

**Solution**:
1. Verify BETTER_AUTH_SECRET matches in frontend and backend
2. Check JWT token is being sent in Authorization header
3. Verify user is logged in on frontend

**Debug**:
```bash
# Check frontend sends JWT
# Open browser DevTools → Network → Select API request → Headers
# Look for: Authorization: Bearer <token>

# Verify backend receives token
# Check backend logs for JWT verification messages
```

---

#### Problem: Migration fails

**Error**: `relation "user" does not exist`

**Solution**:
1. Run frontend Prisma migrations first: `cd frontend && npx prisma migrate dev`
2. Verify `user` table exists: `psql $DATABASE_URL -c "\d user"`
3. Then run backend migration

---

#### Problem: CORS errors

**Error**: `Access to fetch at 'http://localhost:8000/api/tasks' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Solution**:
1. Verify FRONTEND_URL in backend/.env matches frontend URL
2. Check CORS middleware in backend/app/main.py
3. Restart backend server

---

#### Problem: Tasks not persisting

**Error**: Tasks disappear after page refresh

**Solution**:
1. Verify migration ran successfully
2. Check database connection: `psql $DATABASE_URL -c "SELECT * FROM tasks;"`
3. Check backend logs for database errors
4. Verify frontend API client is calling backend (not using mock data)

---

## Validation Checklist

After setup, verify these items:

### Backend Validation
- [ ] `uvicorn app.main:app --reload` starts without errors
- [ ] Health check returns 200: `curl http://localhost:8000/`
- [ ] OpenAPI docs accessible: http://localhost:8000/docs
- [ ] All 6 task endpoints visible in docs

### Database Validation
- [ ] Tasks table exists: `psql $DATABASE_URL -c "\d tasks"`
- [ ] Indexes created: `psql $DATABASE_URL -c "\di tasks*"`
- [ ] Foreign key constraint exists: `psql $DATABASE_URL -c "\d+ tasks"`
- [ ] Can insert test task: `psql $DATABASE_URL -c "INSERT INTO tasks (user_id, title) VALUES ('test', 'Test Task');"`

### Authentication Validation
- [ ] Requests without JWT return 401
- [ ] Requests with valid JWT succeed
- [ ] BETTER_AUTH_SECRET matches in frontend and backend

### Integration Validation
- [ ] Frontend can create tasks
- [ ] Tasks appear in database
- [ ] Tasks persist after page refresh
- [ ] User can update tasks
- [ ] User can delete tasks
- [ ] User can toggle completion

---

## Development Workflow

### Starting Development

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate  # If using venv
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Database monitoring (optional)
watch -n 2 'psql $DATABASE_URL -c "SELECT id, title, completed FROM tasks ORDER BY created_at DESC LIMIT 10;"'
```

### Making Changes

**Backend Changes**:
1. Edit files in `backend/app/`
2. Uvicorn auto-reloads on file changes
3. Check logs for errors

**Database Changes**:
1. Create new migration file: `backend/migrations/003_*.sql`
2. Run migration: `psql $DATABASE_URL -f migrations/003_*.sql`
3. Update SQLModel models if needed

**Testing Changes**:
1. Use frontend UI to test
2. Check backend logs for errors
3. Verify database state: `psql $DATABASE_URL -c "SELECT * FROM tasks;"`

---

## API Testing

### Using cURL

```bash
# Get JWT token from browser
# 1. Login on frontend
# 2. Open DevTools → Application → Cookies → better-auth.session_token
# 3. Copy token value

export JWT_TOKEN="your-jwt-token-here"

# List tasks
curl -H "Authorization: Bearer $JWT_TOKEN" \
  http://localhost:8000/api/tasks

# Create task
curl -X POST \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "description": "Testing API"}' \
  http://localhost:8000/api/tasks

# Get single task
curl -H "Authorization: Bearer $JWT_TOKEN" \
  http://localhost:8000/api/tasks/1

# Update task
curl -X PUT \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Task", "description": "Updated"}' \
  http://localhost:8000/api/tasks/1

# Toggle completion
curl -X PATCH \
  -H "Authorization: Bearer $JWT_TOKEN" \
  http://localhost:8000/api/tasks/1/complete

# Delete task
curl -X DELETE \
  -H "Authorization: Bearer $JWT_TOKEN" \
  http://localhost:8000/api/tasks/1
```

### Using Swagger UI

1. Navigate to http://localhost:8000/docs
2. Click "Authorize" button
3. Enter JWT token: `Bearer <your-token>`
4. Click "Authorize"
5. Test endpoints directly in browser

---

## Production Deployment

### Environment Variables

**Production `.env`**:
```bash
DATABASE_URL=postgresql://prod-user:prod-pass@prod-host:5432/prod-db
BETTER_AUTH_SECRET=production-secret-64-chars
FRONTEND_URL=https://yourdomain.com
HOST=0.0.0.0
PORT=8000
```

### Deployment Checklist

- [ ] Set production DATABASE_URL
- [ ] Generate new BETTER_AUTH_SECRET for production
- [ ] Update FRONTEND_URL to production domain
- [ ] Run migrations on production database
- [ ] Configure HTTPS/SSL
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

---

## Next Steps

After successful setup:

1. **Run `/sp.tasks`**: Generate detailed task breakdown
2. **Implement**: Execute tasks in sequence
3. **Validate**: Run integration tests
4. **Document**: Create PHR for implementation work

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Neon Serverless](https://neon.tech/docs)
- Feature Specification: specs/003-tasks-crud-api/spec.md
- Implementation Plan: specs/003-tasks-crud-api/plan.md
- API Contracts: specs/003-tasks-crud-api/contracts/tasks-api.md

---

## Support

If you encounter issues not covered in this guide:

1. Check backend logs for error messages
2. Verify all environment variables are set correctly
3. Test database connection independently
4. Review API contracts for correct request format
5. Check CORS configuration if frontend can't reach backend
