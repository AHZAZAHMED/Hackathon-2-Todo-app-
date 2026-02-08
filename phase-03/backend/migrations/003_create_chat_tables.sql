-- Migration: 003_create_chat_tables.sql
-- Description: Creates conversations and messages tables for chat functionality
-- Date: 2026-02-08
-- Phase: Phase-3 Backend Chat API

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Foreign key constraint
    CONSTRAINT fk_conversations_user_id
        FOREIGN KEY (user_id)
        REFERENCES "user"(id)
        ON DELETE CASCADE
);

-- Create index on user_id for efficient lookups
CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- Create messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Foreign key constraint
    CONSTRAINT fk_messages_conversation_id
        FOREIGN KEY (conversation_id)
        REFERENCES conversations(id)
        ON DELETE CASCADE
);

-- Create indexes for efficient queries
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- Add trigger to update conversations.updated_at on new message
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations
    SET updated_at = NOW()
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_conversation_timestamp
    AFTER INSERT ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_timestamp();

-- Add comments for documentation
COMMENT ON TABLE conversations IS 'Stores chat conversations between users and AI agent';
COMMENT ON TABLE messages IS 'Stores individual messages within conversations';
COMMENT ON COLUMN conversations.user_id IS 'References user.id from Better Auth';
COMMENT ON COLUMN messages.role IS 'Message sender: user or assistant';
COMMENT ON COLUMN messages.content IS 'Message text content (max 10,000 characters)';

-- Rollback script (run if migration needs to be reverted):
-- DROP TRIGGER IF EXISTS trigger_update_conversation_timestamp ON messages;
-- DROP FUNCTION IF EXISTS update_conversation_timestamp();
-- DROP TABLE IF EXISTS messages CASCADE;
-- DROP TABLE IF EXISTS conversations CASCADE;
