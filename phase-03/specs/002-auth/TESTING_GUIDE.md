# Testing Guide: Authentication System

**Feature**: Authentication System (Better Auth + JWT)
**Date**: 2026-02-05
**Status**: Ready for Testing

## Prerequisites

Before testing, ensure you have:
- ✅ PostgreSQL database (Neon Serverless or local)
- ✅ Node.js 18+ installed
- ✅ Python 3.11+ installed
- ✅ Both frontend and backend code implemented

---

## Setup Instructions

### Step 1: Database Setup

**Option A: Using Neon Serverless (Recommended)**

1. Go to [neon.tech](https://neon.tech) and create a free account
2. Create a new project: "hackathon-phase2"
3. Copy your connection string (format: `postgresql://user:password@host/database`)
4. Run the migration script:

```bash
# Connect to Neon and run migrations
psql "your-neon-connection-string" -f backend/migrations/001_create_auth_tables.sql
```

**Option B: Using Local PostgreSQL**

```bash
# Create database
psql postgres
CREATE DATABASE hackathon_phase2;
\q

# Run migrations
psql hackathon_phase2 -f backend/migrations/001_create_auth_tables.sql
```

**Verify Tables Created:**

```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('users', 'rate_limits');

-- Should return:
-- users
-- rate_limits
```

---

### Step 2: Frontend Setup

```bash
cd frontend

# Install dependencies (if not already done)
npm install

# Create .env.local from template
cp .env.example .env.local

# Edit .env.local with your values
# Use the same BETTER_AUTH_SECRET for both frontend and backend!
```

**frontend/.env.local** (example):

```bash
BETTER_AUTH_SECRET=497080c78b03d34b16328f63b4f5c5e6b8d7cd372648fca6066ba2d507d66540
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://your-connection-string
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Todo App
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**Start Frontend:**

```bash
npm run dev
```

Expected output:
```
▲ Next.js 16.x.x
- Local:        http://localhost:3000
- Ready in X.Xs
```

---

### Step 3: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env from template
cp .env.example .env

# Edit .env with your values
# IMPORTANT: Use the SAME BETTER_AUTH_SECRET as frontend!
```

**backend/.env** (example):

```bash
BETTER_AUTH_SECRET=497080c78b03d34b16328f63b4f5c5e6b8d7cd372648fca6066ba2d507d66540
DATABASE_URL=postgresql://your-connection-string
FRONTEND_URL=http://localhost:3000
HOST=0.0.0.0
PORT=8000
```

**Start Backend:**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
🚀 Hackathon Phase-2 API starting...
📍 CORS enabled for: http://localhost:3000
✅ Application ready
```

---

## Testing Checklist

### ✅ Phase 1: User Registration (User Story 1)

**Test Case 1.1: Successful Signup**

1. Navigate to `http://localhost:3000/signup`
2. Fill in the form:
   - Name: "Test User"
   - Email: "test@example.com"
   - Password: "password123"
3. Click "Create account"

**Expected Results:**
- ✅ Redirected to `/dashboard`
- ✅ See "Welcome back, Test User!" message
- ✅ JWT token stored in httpOnly cookie (check DevTools → Application → Cookies)
- ✅ Cookie name: `better-auth.session_token` or similar
- ✅ No errors in browser console

**Test Case 1.2: Duplicate Email**

1. Try to signup again with "test@example.com"

**Expected Results:**
- ✅ Error message: "Email already registered"
- ✅ Stay on signup page

**Test Case 1.3: Invalid Email**

1. Try to signup with email: "invalid-email"

**Expected Results:**
- ✅ Error message: "Please enter a valid email address"

**Test Case 1.4: Short Password**

1. Try to signup with password: "short"

**Expected Results:**
- ✅ Error message: "Password must be at least 8 characters"

**Test Case 1.5: Empty Fields**

1. Submit form with empty fields

**Expected Results:**
- ✅ Validation errors for each empty field

---

### ✅ Phase 2: User Login (User Story 2)

**Test Case 2.1: Successful Login**

1. Logout (if logged in)
2. Navigate to `http://localhost:3000/login`
3. Enter credentials:
   - Email: "test@example.com"
   - Password: "password123"
4. Click "Sign in"

**Expected Results:**
- ✅ Redirected to `/dashboard`
- ✅ See "Welcome back, Test User!" message
- ✅ JWT token stored in httpOnly cookie

**Test Case 2.2: Incorrect Password**

1. Try to login with wrong password

**Expected Results:**
- ✅ Error message: "Invalid email or password"

**Test Case 2.3: Non-existent Email**

1. Try to login with "nonexistent@example.com"

**Expected Results:**
- ✅ Error message: "Invalid email or password"

**Test Case 2.4: Rate Limiting**

1. Attempt login with wrong password 5 times

**Expected Results:**
- ✅ After 5th attempt: Error message "Too many failed attempts. Please try again in X minutes."
- ✅ Cannot login for 15 minutes
- ✅ Check database: `SELECT * FROM rate_limits WHERE email = 'test@example.com';`
- ✅ Should see record with `failed_attempts = 5` and `locked_until` timestamp

**Test Case 2.5: Rate Limit Reset**

1. Wait 15 minutes (or delete rate_limits record manually)
2. Login with correct password

**Expected Results:**
- ✅ Login successful
- ✅ Rate limit record deleted from database

---

### ✅ Phase 3: Protected Route Access (User Story 3)

**Test Case 3.1: Authenticated Access**

1. While logged in, navigate to `http://localhost:3000/dashboard`

**Expected Results:**
- ✅ Dashboard loads successfully
- ✅ See personalized greeting with user name

**Test Case 3.2: Unauthenticated Access**

1. Logout
2. Try to navigate directly to `http://localhost:3000/dashboard`

**Expected Results:**
- ✅ Redirected to `/login?redirect=/dashboard`
- ✅ After login, redirected back to `/dashboard`

**Test Case 3.3: JWT in API Requests**

1. Login
2. Open DevTools → Network tab
3. Make any API request (or refresh dashboard)
4. Check request headers

**Expected Results:**
- ✅ `Authorization: Bearer <jwt_token>` header present
- ✅ Token is a valid JWT (copy and paste into jwt.io to decode)
- ✅ Token contains claims: `user_id`, `email`, `name`, `exp`, `iat`

**Test Case 3.4: Backend JWT Verification**

1. Login and get JWT token from cookie
2. Test backend protected endpoint:

```bash
# Get token from browser DevTools → Application → Cookies
# Copy the value of better-auth.session_token

curl -X GET http://localhost:8000/api/protected \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**Expected Results:**
- ✅ Response:
```json
{
  "message": "This is a protected route",
  "user": {
    "user_id": 1,
    "email": "test@example.com",
    "name": "Test User"
  }
}
```

**Test Case 3.5: Invalid Token**

```bash
curl -X GET http://localhost:8000/api/protected \
  -H "Authorization: Bearer invalid-token"
```

**Expected Results:**
- ✅ Status: 401 Unauthorized
- ✅ Response:
```json
{
  "detail": {
    "error": {
      "code": "INVALID_TOKEN",
      "message": "..."
    }
  }
}
```

---

### ✅ Phase 4: Session Persistence (User Story 4)

**Test Case 4.1: Page Refresh**

1. Login
2. Refresh the page (F5)

**Expected Results:**
- ✅ Still logged in
- ✅ Dashboard content still visible

**Test Case 4.2: Browser Close/Reopen (Within 24 Hours)**

1. Login
2. Close browser completely
3. Reopen browser
4. Navigate to `http://localhost:3000/dashboard`

**Expected Results:**
- ✅ Still logged in (JWT token persists in cookie)
- ✅ Dashboard content visible

**Test Case 4.3: Token Expiration (After 24 Hours)**

1. Login
2. Wait 24 hours (or manually expire token by changing `exp` claim)
3. Try to access dashboard

**Expected Results:**
- ✅ Redirected to `/login?redirect=/dashboard`
- ✅ After login, redirected back to `/dashboard`

**Test Case 4.4: Direct URL Navigation**

1. Login
2. Navigate directly to `http://localhost:3000/dashboard` by typing in address bar

**Expected Results:**
- ✅ Dashboard loads without redirect to login

---

### ✅ Phase 5: User Logout (User Story 5)

**Test Case 5.1: Logout**

1. Login
2. Click profile dropdown (top right)
3. Click "Logout"

**Expected Results:**
- ✅ Redirected to landing page (`/`)
- ✅ JWT token cleared from cookie (check DevTools → Application → Cookies)
- ✅ No `better-auth.session_token` cookie present

**Test Case 5.2: Post-Logout Access**

1. After logout, try to navigate to `/dashboard`

**Expected Results:**
- ✅ Redirected to `/login`

**Test Case 5.3: Browser Back Button**

1. Logout
2. Click browser back button

**Expected Results:**
- ✅ Redirected to `/login` (not back to protected content)

---

## Edge Cases Testing

### Edge Case 1: Concurrent Sessions

1. Login on Browser A (Chrome)
2. Login on Browser B (Firefox) with same account
3. Verify both sessions work simultaneously

**Expected Results:**
- ✅ Both browsers remain logged in
- ✅ Both can access dashboard
- ✅ Each has its own JWT token in cookie

### Edge Case 2: Network Failure

1. Disconnect internet
2. Try to login

**Expected Results:**
- ✅ User-friendly error message (not raw network error)
- ✅ Can retry after reconnecting

### Edge Case 3: Malformed Token

1. Login
2. Manually corrupt JWT token in cookie (edit in DevTools)
3. Try to access dashboard

**Expected Results:**
- ✅ Redirected to `/login`
- ✅ Backend returns 401 Unauthorized

---

## Database Verification

### Check Users Table

```sql
SELECT id, name, email, created_at FROM users;
```

**Expected:**
- ✅ Test user record exists
- ✅ Password is hashed (not plaintext)

### Check Rate Limits Table

```sql
SELECT * FROM rate_limits;
```

**Expected:**
- ✅ Empty after successful login
- ✅ Contains record after 5 failed attempts
- ✅ `locked_until` timestamp is 15 minutes in future

---

## Troubleshooting

### Issue: "BETTER_AUTH_SECRET is not set"

**Solution:**
- Verify `.env.local` (frontend) and `.env` (backend) exist
- Verify `BETTER_AUTH_SECRET` is set in both files
- Restart both servers

### Issue: "Database connection failed"

**Solution:**
- Verify `DATABASE_URL` is correct
- Test connection: `psql "your-database-url"`
- Check database is accessible

### Issue: "401 Unauthorized" on all requests

**Solution:**
- Verify `BETTER_AUTH_SECRET` is IDENTICAL in frontend and backend
- Check JWT token exists in cookie
- Verify backend is running

### Issue: CORS errors in browser console

**Solution:**
- Verify `FRONTEND_URL` in backend `.env` is `http://localhost:3000`
- Verify backend CORS middleware is configured
- Restart backend server

### Issue: Rate limiting not working

**Solution:**
- Verify `rate_limits` table exists
- Check database connection
- Verify backend rate limiting logic is running

---

## Success Criteria

All tests should pass:
- ✅ User can register account
- ✅ User can login
- ✅ User can access protected routes
- ✅ Session persists across page refreshes
- ✅ User can logout
- ✅ Rate limiting prevents brute-force attacks
- ✅ JWT tokens stored in httpOnly cookies
- ✅ Backend verifies JWT and extracts user_id
- ✅ Concurrent sessions work
- ✅ Session restoration works after token expiration

---

## Next Steps After Testing

1. **If all tests pass:**
   - ✅ System is ready for production
   - Consider running automated validation:
     - `implementation-validator-playwright` skill
     - `integration-testing-engineer` skill

2. **If tests fail:**
   - Check troubleshooting section
   - Review error messages in browser console and backend logs
   - Verify environment variables are correct
   - Ensure database migrations ran successfully

3. **Production Deployment:**
   - Generate new `BETTER_AUTH_SECRET` for production
   - Update `DATABASE_URL` to production database
   - Update `FRONTEND_URL` and `NEXT_PUBLIC_API_URL` to production domains
   - Enable HTTPS
   - Set `secure: true` for cookies in production

---

## Testing Completion Checklist

- [ ] Database migrations run successfully
- [ ] Frontend starts without errors
- [ ] Backend starts without errors
- [ ] User registration works
- [ ] User login works
- [ ] Protected routes enforce authentication
- [ ] Session persistence works
- [ ] User logout works
- [ ] Rate limiting works (5 attempts per 15 minutes)
- [ ] JWT tokens stored in httpOnly cookies
- [ ] Backend JWT verification works
- [ ] Concurrent sessions work
- [ ] Session restoration works
- [ ] All edge cases handled
- [ ] No errors in browser console
- [ ] No errors in backend logs

---

**Status**: Ready for Testing ✅

Follow this guide step-by-step to validate the authentication system implementation.
