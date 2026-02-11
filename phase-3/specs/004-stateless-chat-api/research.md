# Research: Stateless Chat API + OpenAI Agent Orchestration

**Feature**: 004-stateless-chat-api
**Date**: 2026-02-09
**Status**: Complete

## Overview

This document captures all technical research and decisions made during the planning phase. Each research area addresses a specific unknown from the Technical Context section of the implementation plan.

---

## Research Area 1: OpenRouter API Integration

### Question
How to configure OpenAI Agents SDK to use OpenRouter as a third-party LLM provider with Gemini model?

### Research Findings

**OpenRouter API Basics**:
- OpenRouter provides an OpenAI-compatible API endpoint
- Base URL: `https://openrouter.ai/api/v1`
- Authentication: API key in `Authorization: Bearer <key>` header
- Model identifier: `google/gemini-pro` (or `openai/gpt-3.5-turbo` for compatibility mode)

**OpenAI Agents SDK Configuration**:
```python
from agents import AsyncOpenAI

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    default_headers={
        "HTTP-Referer": "https://your-app-url.com",  # Optional
        "X-Title": "Todo AI Chatbot"  # Optional
    }
)
```

**Model Selection**:
- Use `google/gemini-pro` for Gemini model via OpenRouter
- Fallback: `openai/gpt-3.5-turbo` if Gemini unavailable
- Model specified in chat completion request, not client initialization

### Decision

**Chosen Approach**: Configure AsyncOpenAI client with OpenRouter base URL and API key

**Implementation**:
```python
# app/config.py
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
AI_MODEL = os.getenv("AI_MODEL", "google/gemini-pro")

# app/services/ai_agent.py
client = AsyncOpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENROUTER_API_KEY
)
```

**Rationale**: OpenRouter provides OpenAI-compatible API, allowing use of OpenAI SDK without modifications. This approach is simpler than custom HTTP clients and maintains compatibility with OpenAI Agents SDK patterns.

**Alternatives Considered**:
- Direct Gemini API: Rejected due to different API format requiring custom integration
- Custom HTTP client: Rejected due to complexity and lack of SDK features
- OpenAI official API: Rejected due to cost considerations (OpenRouter provides cheaper access)

---

## Research Area 2: OpenAI Agents SDK Usage Patterns

### Question
How to use OpenAI Agents SDK for basic conversational AI without tools or MCP integration?

### Research Findings

**Complete Integration Pattern with Third-Party LLM (OpenRouter)**:

```python
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, function_tool
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API key from environment
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

if not openrouter_api_key:
    raise ValueError("OPENROUTER_API_KEY is not set in environment variables")

# Create AsyncOpenAI provider with OpenRouter base URL
provider = AsyncOpenAI(
    api_key=openrouter_api_key,
    base_url="https://openrouter.ai/api/v1"
)

# Create OpenAI Chat Completions Model
model = OpenAIChatCompletionsModel(
    model="google/gemini-pro",  # or "openai/gpt-3.5-turbo"
    openai_client=provider
)

# Create Agent with the model
chat_agent = Agent(
    name="TodoChatAgent",
    instructions=(
        "You are a helpful AI assistant for a todo application. "
        "You can chat with users and provide assistance with task management."
    ),
    model=model
)
```

**Key Components**:
1. **AsyncOpenAI Provider**: Custom base_url points to OpenRouter API
2. **OpenAIChatCompletionsModel**: Wraps the provider for Agents SDK
3. **Agent**: Uses the model for conversational AI
4. **Runner**: Executes the agent with conversation history

**Message Array Format**:
```python
messages = [
    {"role": "system", "content": "You are a helpful AI assistant for a todo application."},
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi! How can I help you today?"},
    {"role": "user", "content": "What can you do?"}
]
```

**Error Handling**:
```python
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI
from openai import APIError, APIConnectionError, RateLimitError

try:
    # Create runner for the agent
    runner = Runner(agent=self.agent)

    # Run agent with conversation history
    result = await runner.run(messages=conversation_history)

    # Extract response from result
    return result.messages[-1].content

except RateLimitError:
    # Handle rate limiting (429)
    raise HTTPException(status_code=503, detail="AI service rate limited")
except APIConnectionError:
    # Handle connection errors
    raise HTTPException(status_code=503, detail="AI service unavailable")
except APIError as e:
    # Handle other API errors
    raise HTTPException(status_code=500, detail="AI service error")
```

### Decision

**Chosen Approach**: Use OpenAI Agents SDK with OpenAIChatCompletionsModel and custom AsyncOpenAI provider pointing to OpenRouter

**Complete Implementation Pattern**:

```python
# app/services/ai_agent.py
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, function_tool
from dotenv import load_dotenv
import os

load_dotenv()

class AIAgentService:
    def __init__(self):
        # Get API key from environment
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is not set in environment variables")

        # Create AsyncOpenAI provider with OpenRouter base URL
        self.provider = AsyncOpenAI(
            api_key=openrouter_api_key,
            base_url="https://openrouter.ai/api/v1"
        )

        # Create OpenAI Chat Completions Model
        self.model = OpenAIChatCompletionsModel(
            model=os.getenv("AI_MODEL", "google/gemini-pro"),
            openai_client=self.provider
        )

        # Create Agent with the model
        self.agent = Agent(
            name="TodoChatAgent",
            instructions=(
                "You are a helpful AI assistant for a todo application. "
                "You can chat with users and provide assistance with task management."
            ),
            model=self.model
        )

    async def generate_response(self, conversation_history: list[dict]) -> str:
        """
        Generate AI response using OpenAI Agents SDK.

        Args:
            conversation_history: List of message dicts with 'role' and 'content'

        Returns:
            AI-generated response string
        """
        try:
            # Create runner for the agent
            runner = Runner(agent=self.agent)

            # Run agent with conversation history
            result = await runner.run(messages=conversation_history)

            # Extract response from result
            return result.messages[-1].content

        except Exception as e:
            print(f"AI Agent Error: {str(e)}")
            raise

# Singleton instance
ai_agent = AIAgentService()
```

**Key Integration Points**:
1. **AsyncOpenAI Provider**: Custom `base_url` points to OpenRouter API endpoint
2. **OpenAIChatCompletionsModel**: Wraps the provider for Agents SDK compatibility
3. **Agent**: Configured with instructions and the custom model
4. **Runner**: Executes the agent with conversation history

**Rationale**: This pattern uses the full OpenAI Agents SDK framework, which provides:
- Structured agent configuration
- Built-in message handling
- Easy extension for future tool integration (Spec-3)
- Consistent with OpenAI Agents SDK best practices

**Alternatives Considered**:
- Direct chat.completions.create(): Rejected as it bypasses Agents SDK benefits
- Custom HTTP client: Rejected due to complexity and lack of SDK features
- Direct Gemini API: Rejected due to different API format requiring custom integration

---

## Research Area 3: SQLModel Async Patterns

### Question
How to implement async database operations with SQLModel for conversation and message persistence?

### Research Findings

**Async Session Management**:
```python
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

# Engine creation
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # SQL logging for development
    pool_size=10,
    max_overflow=20
)

# Session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency for FastAPI
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
```

**Query Patterns**:
```python
from sqlmodel import select

# Load last 50 messages
async def get_conversation_messages(
    session: AsyncSession,
    conversation_id: UUID,
    limit: int = 50
) -> list[Message]:
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(statement)
    messages = result.scalars().all()
    return list(reversed(messages))  # Oldest first
```

**Transaction Handling**:
```python
async def create_message(
    session: AsyncSession,
    conversation_id: UUID,
    role: str,
    content: str
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message
```

### Decision

**Chosen Approach**: Use SQLModel with async engine and AsyncSession for all database operations

**Implementation**:
```python
# app/database.py
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
# Convert postgresql:// to postgresql+asyncpg://
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Disable in production
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Verify connections before use
)

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
```

**Rationale**: Async operations prevent blocking the FastAPI event loop, enabling high concurrency. SQLModel provides type-safe ORM with async support via SQLAlchemy 2.0. Connection pooling ensures efficient database resource usage.

**Alternatives Considered**:
- Synchronous SQLModel: Rejected due to blocking I/O
- Raw asyncpg: Rejected due to lack of ORM features and type safety
- Tortoise ORM: Rejected due to unfamiliarity and smaller ecosystem

---

## Research Area 4: JWT Verification with Better Auth

### Question
How to verify Better Auth JWT tokens and extract user_id in FastAPI?

### Research Findings

**Better Auth JWT Structure**:
- Algorithm: HS256 (HMAC with SHA-256)
- Secret: Stored in `BETTER_AUTH_SECRET` environment variable
- Claims: Standard JWT claims plus custom `user_id` or `sub` claim

**PyJWT Verification**:
```python
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def verify_jwt(credentials: HTTPAuthorizationCredentials) -> dict:
    try:
        payload = jwt.decode(
            credentials.credentials,
            key=os.getenv("BETTER_AUTH_SECRET"),
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**User ID Extraction**:
```python
def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    payload = verify_jwt(credentials)
    user_id = payload.get("sub") or payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: missing user_id")
    return user_id
```

### Decision

**Chosen Approach**: Use PyJWT with HS256 algorithm to verify Better Auth tokens and extract user_id from claims

**Implementation**:
```python
# app/auth/dependencies.py
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import BETTER_AUTH_SECRET

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Verify JWT token and extract user_id.

    Raises:
        HTTPException: 401 if token invalid, expired, or missing user_id
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            key=BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )

        # Extract user_id from standard 'sub' claim or custom 'user_id' claim
        user_id = payload.get("sub") or payload.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing user identifier"
            )

        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Rationale**: PyJWT is the standard Python library for JWT verification. Better Auth uses HS256 algorithm with a shared secret, making verification straightforward. Extracting user_id from claims ensures server-side identity control.

**Alternatives Considered**:
- python-jose: Rejected due to additional dependencies and similar functionality
- Custom JWT parsing: Rejected due to security risks and complexity
- Better Auth SDK: Rejected as Better Auth is frontend-focused, backend only needs verification

---

## Research Area 5: Database Migration Strategy

### Question
What approach should be used for creating and managing database migrations for conversations and messages tables?

### Research Findings

**Option 1: Alembic (SQLAlchemy migration tool)**:
- Pros: Auto-generates migrations from model changes, version control, rollback support
- Cons: Additional dependency, learning curve, overkill for simple schema

**Option 2: Raw SQL Migration Scripts**:
- Pros: Simple, explicit, no additional dependencies, easy to review
- Cons: Manual creation, no auto-generation, requires careful ordering

**Option 3: SQLModel.metadata.create_all()**:
- Pros: Simplest approach, no migration files needed
- Cons: No version control, no rollback, not suitable for production

**Existing Project Pattern**:
- Project already uses raw SQL migrations (001_create_auth_tables.sql, 002_create_tasks_table.sql)
- Migrations stored in `backend/migrations/` directory
- Applied manually or via custom script

### Decision

**Chosen Approach**: Raw SQL migration script following existing project pattern

**Implementation**:
```sql
-- backend/migrations/003_create_chat_tables.sql

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    title VARCHAR(200),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Foreign key to Better Auth user table
    CONSTRAINT fk_conversations_user
        FOREIGN KEY (user_id)
        REFERENCES "user"(id)
        ON DELETE CASCADE
);

-- Create index on user_id for query performance
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Foreign key to conversations table
    CONSTRAINT fk_messages_conversation
        FOREIGN KEY (conversation_id)
        REFERENCES conversations(id)
        ON DELETE CASCADE
);

-- Create indexes for query performance
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created ON messages(conversation_id, created_at DESC);

-- Add updated_at trigger for conversations table
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

**Rationale**: Consistency with existing project patterns. Raw SQL migrations are explicit, reviewable, and sufficient for this project's scale. No need for complex migration tooling.

**Alternatives Considered**:
- Alembic: Rejected as overkill for simple schema and inconsistent with existing pattern
- SQLModel.metadata.create_all(): Rejected as unsuitable for production (no version control)

---

## Summary of Decisions

| Research Area | Decision | Key Technology |
|---------------|----------|----------------|
| OpenRouter API Integration | Use AsyncOpenAI with OpenRouter base URL | AsyncOpenAI, OpenRouter API |
| OpenAI Agents SDK Usage | Use OpenAI Agents SDK with Agent, OpenAIChatCompletionsModel, and Runner | OpenAI Agents SDK, AsyncOpenAI |
| SQLModel Async Patterns | Async engine with AsyncSession and connection pooling | SQLModel + asyncpg |
| JWT Verification | PyJWT with HS256 algorithm, extract user_id from claims | PyJWT |
| Database Migrations | Raw SQL script following existing project pattern | PostgreSQL SQL |

---

## Environment Variables Required

```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Authentication
BETTER_AUTH_SECRET=your-secret-key-here

# AI Service
OPENROUTER_API_KEY=your-openrouter-api-key-here
AI_MODEL=google/gemini-pro  # or openai/gpt-3.5-turbo
```

---

## Dependencies to Add

```txt
# requirements.txt additions
openai>=1.0.0           # OpenAI SDK for API calls
agents>=0.1.0          # OpenAI Agents SDK for agent orchestration
pyjwt>=2.8.0           # JWT verification
asyncpg>=0.29.0        # PostgreSQL async driver
httpx>=0.25.0          # Async HTTP client (OpenAI SDK dependency)
```

---

**Status**: ✅ All research complete. Ready for Phase 1 (Design & Contracts).
