# Better Auth Database Adapter Fix

## Problem
Better Auth shows "Failed to initialize database adapter" error because the PostgreSQL adapter package is not installed.

## Solution

### Option 1: Install Kysely Adapter (Recommended)

```bash
cd frontend
npm install @better-auth/kysely kysely kysely-postgres
```

Then update `lib/auth.ts`:

```typescript
import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";
import { Pool } from "pg";
import { Kysely, PostgresDialect } from "kysely";

const dialect = new PostgresDialect({
  pool: new Pool({
    connectionString: process.env.DATABASE_URL!,
  }),
});

const db = new Kysely({ dialect });

export const auth = betterAuth({
  database: db,
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
  session: {
    expiresIn: 60 * 60 * 24, // 24 hours
    updateAge: 60 * 60 * 24, // 24 hours
    cookieCache: {
      enabled: true,
      maxAge: 60 * 60 * 24, // 24 hours
    },
  },
  plugins: [nextCookies()],
  secret: process.env.BETTER_AUTH_SECRET!,
  baseURL: process.env.BETTER_AUTH_URL!,
});
```

### Option 2: Use Better Auth CLI to Generate Schema

```bash
cd frontend
npx better-auth migrate
```

This will create the necessary database tables automatically.

### Option 3: Manual Database Setup

If Better Auth requires specific tables, create them:

```sql
-- Better Auth typically needs these tables:
CREATE TABLE IF NOT EXISTS user (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    emailVerified BOOLEAN DEFAULT FALSE,
    name TEXT,
    image TEXT,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS session (
    id TEXT PRIMARY KEY,
    userId TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    expiresAt TIMESTAMP NOT NULL,
    token TEXT UNIQUE NOT NULL,
    ipAddress TEXT,
    userAgent TEXT,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS account (
    id TEXT PRIMARY KEY,
    userId TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    accountId TEXT NOT NULL,
    providerId TEXT NOT NULL,
    accessToken TEXT,
    refreshToken TEXT,
    idToken TEXT,
    expiresAt TIMESTAMP,
    password TEXT,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS verification (
    id TEXT PRIMARY KEY,
    identifier TEXT NOT NULL,
    value TEXT NOT NULL,
    expiresAt TIMESTAMP NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## After Fix

1. Restart frontend: `npm run dev`
2. Check console - should see no database adapter errors
3. Test signup flow
4. Test login flow
5. Verify JWT tokens in cookies

## Verification

Navigate to http://localhost:3000 and check browser console:
- ✅ No "Failed to initialize database adapter" error
- ✅ No unhandled rejections
- ✅ Application loads without errors

## Next Steps After Fix

1. Test user registration
2. Test user login
3. Verify JWT tokens stored in httpOnly cookies
4. Test protected route access
5. Test logout functionality
6. Run comprehensive validation with Playwright
