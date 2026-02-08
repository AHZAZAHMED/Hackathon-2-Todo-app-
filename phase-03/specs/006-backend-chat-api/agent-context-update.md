# Agent Context Update: Backend Chat API

**Feature**: 006-backend-chat-api
**Date**: 2026-02-08
**Status**: Complete

## Technologies Added to Agent Context

The following technologies and patterns have been introduced in this feature and should be added to the agent's knowledge base:

### 1. OpenAI Agents SDK
- **Purpose**: AI agent orchestration framework
- **Usage**: Creating agents with tools, executing agent runs
- **Key Concepts**:
  - Agent: AI assistant with instructions and tools
  - Tool: Function that agent can invoke
  - Runner: Executes agent with message history
  - Model: LLM backend (configured for Gemini)

### 2. Gemini 2.0 Flash API
- **Purpose**: Free LLM for agent responses
- **Integration**: Via OpenAI-compatible endpoint
- **Endpoint**: `https://generativelanguage.googleapis.com/v1beta/openai`
- **Model**: `gemini-2.0-flash`
- **Key Feature**: Free tier with generous rate limits

### 3. AsyncOpenAI Client
- **Purpose**: OpenAI-compatible API client
- **Configuration**: Custom base_url for Gemini API
- **Usage**: Provides LLM backend for OpenAI Agents SDK

### 4. MCP (Model Context Protocol)
- **Purpose**: Tool interface for agent-database interaction
- **Pattern**: Function-based tools with structured returns
- **Key Principle**: MCP tools are the ONLY components that mutate task data
- **Tools Implemented**: add_task, list_tasks, complete_task, delete_task, update_task

### 5. Stateless Backend Architecture
- **Pattern**: All conversation state in database
- **Implementation**: Per-request database sessions via dependency injection
- **Key Principle**: Server restarts do not lose conversation data

### 6. Token-Based Conversation History
- **Library**: tiktoken (OpenAI's token counting library)
- **Strategy**: Load last 2000 tokens of conversation history
- **Purpose**: Respect LLM context window limits

### 7. Conversation Management
- **Pattern**: Single conversation per user (auto-created)
- **Storage**: PostgreSQL with conversations and messages tables
- **Relationships**: User → Conversation → Messages

## Implementation Patterns

### Agent Invocation Pattern
```python
from openai import AsyncOpenAI
from openai_agents import OpenAIChatCompletionsModel, Agent, Runner

# Configure client for Gemini
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai"
)

# Create model
model = OpenAIChatCompletionsModel(
    client=client,
    model="gemini-2.0-flash"
)

# Create agent with tools
agent = Agent(
    name="TaskAssistant",
    instructions="You are a helpful task management assistant...",
    model=model,
    tools=[add_task_tool, list_tasks_tool, ...]
)

# Execute agent (synchronous)
result = Runner.run_sync(agent, messages=history)
```

### MCP Tool Pattern
```python
from pydantic import BaseModel

class Task(BaseModel):
    id: int
    title: str
    completed: bool

def add_task(user_id: str, title: str, description: str = "") -> Task:
    """MCP tool that creates task in database."""
    # Use SQLModel for database operation
    # Return structured Pydantic model
    pass
```

### Stateless Endpoint Pattern
```python
@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    session: Session = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id)
):
    # 1. Load conversation history from DB
    # 2. Store user message in DB
    # 3. Invoke agent (stateless)
    # 4. Store assistant response in DB
    # 5. Return response
    pass
```

### Token Counting Pattern
```python
import tiktoken

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
tokens = len(encoding.encode(text))
```

## Architecture Principles

### Phase-3 Specific Principles
1. **MCP-Only Database Mutations**: All task CRUD operations MUST flow through MCP tools
2. **Stateless Backend**: No in-memory conversation state
3. **AI Agent Orchestration**: Agent decides intent, MCP tools execute
4. **JWT-Based User Isolation**: user_id from JWT passed to all MCP tools
5. **Token-Based History**: Load last 2000 tokens (not message count)

### Data Flow
```
User Message → Chat Endpoint → Load History → Store Message →
Invoke Agent → Agent Selects Tools → MCP Tools Execute →
Store Response → Return to User
```

## Dependencies Added

### Python Packages
- `openai` - AsyncOpenAI client
- `openai-agents` - OpenAI Agents SDK
- `tiktoken` - Token counting
- `pydantic` - Structured tool returns (already installed)
- `sqlmodel` - Database ORM (already installed)

### Environment Variables
- `GEMINI_API_KEY` - Gemini API key from Google AI Studio

## Database Schema

### New Tables
- `conversations` - Chat conversations (user_id FK)
- `messages` - Individual messages (conversation_id FK)

### Relationships
- User (1) → Conversation (1) - Single conversation per user
- Conversation (1) → Messages (N) - Many messages per conversation

## Testing Considerations

### Integration Tests
- Complete chat flow (user message → agent → MCP tools → response)
- Conversation persistence across requests
- User isolation (User A cannot see User B's conversations)
- Tool invocations (add task via chat)
- Stateless backend verification (restart server, conversation persists)

### Performance Tests
- 50 concurrent requests without degradation
- <5s response time (95th percentile)
- Token counting accuracy

## Error Handling

### Error Codes
- 401: JWT invalid/missing
- 422: Request validation failed
- 500: MCP tool failure, unexpected errors
- 503: Gemini API unavailable
- 504: Request timeout (>5 seconds)

### Error Handling Pattern
- Middleware for global timeout enforcement
- Structured error responses (no stack traces)
- User-friendly error messages
- Logging for debugging

---

**Agent Context Update Status**: ✅ COMPLETE
**Technologies Documented**: 7 major technologies + patterns
**Ready for**: Task Generation (/sp.tasks)
