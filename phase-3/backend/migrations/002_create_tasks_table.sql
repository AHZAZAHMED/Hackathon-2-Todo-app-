-- Migration: Create tasks table
-- Feature: Backend API + Database Persistence (003-tasks-crud-api)
-- Date: 2026-02-06
-- Purpose: Create tasks table with user isolation and foreign key constraints

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT tasks_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES "user"(id) ON DELETE CASCADE
);

-- Create index on user_id for fast filtering by user
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);

-- Create index on completed for fast filtering by completion status
CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);

-- Verify table creation
-- Expected output: tasks table with 7 columns and 2 indexes

/*
Rollback script (run if migration needs to be reverted):

DROP INDEX IF EXISTS idx_tasks_completed;
DROP INDEX IF EXISTS idx_tasks_user_id;
DROP TABLE IF EXISTS tasks;
*/
