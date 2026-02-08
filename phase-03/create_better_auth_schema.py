"""
Create Better Auth database schema
Initializes the required tables for Better Auth with PostgreSQL
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('frontend/.env.local')

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in frontend/.env.local")
    exit(1)

# Better Auth required schema
BETTER_AUTH_SCHEMA = """
-- Drop existing tables if they exist
DROP TABLE IF EXISTS verification CASCADE;
DROP TABLE IF EXISTS session CASCADE;
DROP TABLE IF EXISTS account CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;

-- Create user table (singular, as required by Better Auth)
CREATE TABLE "user" (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    "emailVerified" BOOLEAN NOT NULL DEFAULT FALSE,
    name TEXT NOT NULL,
    "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    image TEXT,
    banned BOOLEAN DEFAULT FALSE,
    "banReason" TEXT,
    "banExpires" BIGINT
);

-- Create session table
CREATE TABLE session (
    id TEXT PRIMARY KEY,
    "expiresAt" TIMESTAMP NOT NULL,
    token TEXT NOT NULL UNIQUE,
    "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "ipAddress" TEXT,
    "userAgent" TEXT,
    "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    "impersonatedBy" TEXT,
    "activeOrganizationId" TEXT
);

-- Create account table
CREATE TABLE account (
    id TEXT PRIMARY KEY,
    "accountId" TEXT NOT NULL,
    "providerId" TEXT NOT NULL,
    "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    "accessToken" TEXT,
    "refreshToken" TEXT,
    "idToken" TEXT,
    "accessTokenExpiresAt" TIMESTAMP,
    "refreshTokenExpiresAt" TIMESTAMP,
    scope TEXT,
    password TEXT,
    "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create verification table
CREATE TABLE verification (
    id TEXT PRIMARY KEY,
    identifier TEXT NOT NULL,
    value TEXT NOT NULL,
    "expiresAt" TIMESTAMP NOT NULL,
    "createdAt" TIMESTAMP DEFAULT NOW(),
    "updatedAt" TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_session_user_id ON session("userId");
CREATE INDEX idx_account_user_id ON account("userId");
CREATE INDEX idx_verification_identifier ON verification(identifier);

-- Grant permissions (if needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO neondb_owner;
"""

try:
    print("Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    print("Creating Better Auth schema...")
    cur.execute(BETTER_AUTH_SCHEMA)

    conn.commit()
    print("SUCCESS: Better Auth schema created successfully!")

    # Verify tables were created
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name IN ('user', 'session', 'account', 'verification')
        ORDER BY table_name;
    """)

    tables = cur.fetchall()
    print(f"\nSUCCESS: Created tables: {', '.join([t[0] for t in tables])}")

    cur.close()
    conn.close()

except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
