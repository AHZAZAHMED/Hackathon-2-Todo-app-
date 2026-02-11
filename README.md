# Hackathon-2: Multi-Phase Todo Application

A comprehensive todo application built across multiple phases, progressing from a simple console app to a full-stack AI-powered chatbot application.

## Project Structure

```
Hackathon-2/
├── phase-1/          # Console-based Python Todo App (In-Memory)
├── phase-02/         # Full-Stack Todo App (Next.js + FastAPI + PostgreSQL)
├── phase-03/         # AI-Powered Chatbot Todo App (OpenAI Agents + MCP)
├── phase-3/          # Alternative implementation
└── specs/            # Feature specifications and documentation
```

---

## Phase 1: Console Todo App

**Stack:** Python 3.13+

A simple in-memory console-based todo application with enhanced features.

### Features
- Basic CRUD operations (add, view, update, delete, complete)
- Priority levels (high, medium, low)
- Tagging system for categorization
- Search and filter functionality
- Sorting by priority, alphabetical, or due date
- Clean console UI with visual indicators

### Setup
```bash
cd phase-1
python src/main.py
```

### Commands
- `add <description>` - Add new task
- `view` - View all tasks
- `complete <id>` - Mark task complete
- `set-priority <id> <level>` - Set priority (high/medium/low)
- `tag <id> <tag1> <tag2>...` - Add tags
- `search <keyword>` - Search tasks
- `filter <criteria> <value>` - Filter tasks
- `sort <criteria>` - Sort tasks
- `quit` - Exit

---

## Phase 2: Full-Stack Todo App

**Stack:** Next.js 16 + FastAPI + PostgreSQL + Better Auth

A production-ready full-stack todo application with authentication and database persistence.

### Architecture
- **Frontend:** Next.js 16 (App Router) + TypeScript + Tailwind CSS
- **Backend:** FastAPI + SQLModel ORM
- **Database:** PostgreSQL (Neon Serverless)
- **Authentication:** Better Auth + JWT
- **ORM:** Prisma (auth tables) + SQLModel (application data)

### Features
- User authentication (signup/login) with JWT
- Secure task management with user isolation
- Real-time CRUD operations
- Responsive modern UI
- Database persistence
- RESTful API endpoints

### Setup

#### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL database (Neon recommended)

#### Frontend Setup
```bash
cd phase-02/frontend
npm install
cp .env.example .env.local
# Edit .env.local with your configuration
npm run dev
```

#### Backend Setup
```bash
cd phase-02/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database URL and secrets
uvicorn app.main:app --reload
```

#### Environment Variables

**Frontend (.env.local):**
```env
BETTER_AUTH_SECRET=your-64-character-hex-secret
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://user:password@host:port/database
```

**Backend (.env):**
```env
BETTER_AUTH_SECRET=your-64-character-hex-secret
DATABASE_URL=postgresql://user:password@host:port/database
FRONTEND_URL=http://localhost:3000
```

#### Database Migrations
```bash
cd phase-02/backend
psql $DATABASE_URL -f migrations/001_create_auth_tables.sql
psql $DATABASE_URL -f migrations/002_create_tasks_table.sql
```

### API Endpoints
- `POST /api/tasks` - Create task
- `GET /api/tasks` - List all tasks
- `GET /api/tasks/{id}` - Get single task
- `PUT /api/tasks/{id}` - Update task
- `PATCH /api/tasks/{id}/complete` - Toggle completion
- `DELETE /api/tasks/{id}` - Delete task

---

## Phase 3: AI-Powered Chatbot Todo App

**Stack:** Next.js 16 + FastAPI + OpenAI Agents SDK + MCP + PostgreSQL

An AI-powered conversational interface for task management using natural language.

### Architecture
- **Frontend:** Next.js 16 + OpenAI ChatKit UI
- **Backend:** FastAPI (stateless)
- **AI Layer:** OpenAI Agents SDK
- **MCP Layer:** Official MCP SDK with task tools
- **Database:** PostgreSQL (conversations + messages tables)
- **Authentication:** Better Auth + JWT

### Features
- Natural language task management
- AI-powered intent recognition
- Conversational interface with ChatKit UI
- MCP tools for database operations
- Stateless backend architecture
- Conversation history persistence
- User isolation and security

### Setup

#### Prerequisites
- All Phase 2 prerequisites
- OpenAI API key

#### Frontend Setup
```bash
cd phase-03/frontend
npm install
cp .env.example .env.local
# Edit .env.local with your configuration
npm run dev
```

#### Backend Setup
```bash
cd phase-03/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
uvicorn app.main:app --reload
```

#### Environment Variables

**Frontend (.env.local):**
```env
BETTER_AUTH_SECRET=your-64-character-hex-secret
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://user:password@host:port/database
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend (.env):**
```env
BETTER_AUTH_SECRET=your-64-character-hex-secret
DATABASE_URL=postgresql://user:password@host:port/database
FRONTEND_URL=http://localhost:3000
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key
```

#### Database Migrations
```bash
cd phase-03/backend
psql $DATABASE_URL -f migrations/001_create_auth_tables.sql
psql $DATABASE_URL -f migrations/002_create_tasks_table.sql
psql $DATABASE_URL -f migrations/003_create_chat_tables.sql
```

### MCP Tools
- `add_task(title, description)` - Create new task
- `list_tasks()` - Retrieve all user tasks
- `complete_task(task_id)` - Toggle task completion
- `update_task(task_id, title, description)` - Update task
- `delete_task(task_id)` - Delete task

### Chat Endpoint
- `POST /api/chat` - Send message to AI chatbot

---

## Specifications

The `specs/` directory contains detailed feature specifications:

- **001-mcp-task-server/** - MCP server implementation specs
- **004-stateless-chat-api/** - Stateless chat API specs

Each spec includes:
- `spec.md` - Feature requirements
- `plan.md` - Implementation plan
- `tasks.md` - Task breakdown
- `contracts/` - API contracts
- `data-model.md` - Database schema

---

## Development Workflow

This project follows **Spec-Driven Development (SDD)** using the Agentic Dev Stack:

1. **Specify** - Create feature specification (`/sp.specify`)
2. **Plan** - Generate implementation plan (`/sp.plan`)
3. **Tasks** - Break down into testable tasks (`/sp.tasks`)
4. **Implement** - Execute via Claude Code
5. **Validate** - Test and verify implementation

---

## Security Notes

- Never commit `.env` files
- Use `.env.example` templates with placeholder values
- JWT secrets must be 64-character hex strings
- Database credentials should be stored securely
- Enable CORS only for trusted origins
- All API endpoints require JWT authentication
- User isolation enforced at database query level

---

## Testing

Test files are excluded from the repository but can be found locally:
- Backend: `test_*.py` files in backend directories
- Frontend: `*.test.ts`, `*.spec.ts` files in test directories
- Integration: Playwright tests in `tests/` directories

---

## Contributing

1. Follow the spec-driven development workflow
2. Create feature specifications before coding
3. Maintain user isolation and security principles
4. Write tests for all new features
5. Update documentation as needed

---

## License

This project is part of Hackathon-2 and is for educational purposes.

---

## Support

For issues or questions:
- Check the `specs/` directory for detailed documentation
- Review `CLAUDE.md` files for development rules
- Consult implementation summaries in each phase directory

---

## Project Status

- ✅ Phase 1: Complete (Console Todo App)
- ✅ Phase 2: Complete (Full-Stack Todo App)
- 🚧 Phase 3: In Progress (AI Chatbot Integration)
