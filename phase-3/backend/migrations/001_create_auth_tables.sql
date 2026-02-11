-- Migration: Create users and rate_limits tables for authentication system
-- Date: 2026-02-05
-- Feature: 002-auth

-- Create users table (managed by Better Auth)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create unique index on lowercase email for case-insensitive lookups
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(LOWER(email));

-- Create rate_limits table for tracking failed login attempts
CREATE TABLE IF NOT EXISTS rate_limits (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    last_attempt TIMESTAMP NOT NULL,
    locked_until TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for rate_limits table
CREATE INDEX IF NOT EXISTS idx_rate_limits_email ON rate_limits(email);
CREATE INDEX IF NOT EXISTS idx_rate_limits_locked_until ON rate_limits(locked_until);

-- Verify tables created
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
AND table_name IN ('users', 'rate_limits')
ORDER BY table_name;
