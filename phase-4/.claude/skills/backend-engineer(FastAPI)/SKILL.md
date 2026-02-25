---
name: backend-engineer-fastapi
description: |
  Backend engineering skills for developing high-performance APIs using FastAPI framework.
  This skill should be used when building server-side applications, RESTful APIs, database integrations, authentication systems, or performing backend development tasks with Python and FastAPI.
---

# Backend Engineer (FastAPI) Skill

Provide expert-level guidance for building production-ready FastAPI applications with proper architecture, security implementation, database integration, and deployment strategies.

## What This Skill Does

- Design and implement RESTful APIs using FastAPI's path operations
- Integrate databases with SQLAlchemy or Tortoise ORM
- Implement OAuth2 authentication and JWT token management
- Configure security best practices (CORS, rate limiting, input validation)
- Write comprehensive tests with pytest
- Deploy applications with Docker and production servers

## What This Skill Does NOT Do

- Frontend development (use frontend skills)
- DevOps infrastructure management (use deployment skills)
- Data science or ML model training
- Non-Python backend frameworks (Django, Flask, etc.)
- Mobile app development

---

## Version Compatibility

This skill covers:
- **FastAPI**: 0.100+
- **Python**: 3.8+
- **Pydantic**: 2.x
- **SQLAlchemy**: 2.x
- **Uvicorn**: 0.20+

For latest patterns and breaking changes, consult official FastAPI documentation.

---

## Required Clarifications

Before implementation, clarify:

1. **Project type**: New API or existing codebase?
2. **Database**: PostgreSQL, MySQL, MongoDB, SQLite, or other?
3. **Authentication**: OAuth2, JWT, API keys, or other method?

## Optional Clarifications

4. **ORM preference**: SQLAlchemy, Tortoise ORM, or raw SQL?
5. **Async requirements**: Fully async or mixed sync/async?
6. **Deployment target**: Docker, serverless, traditional server, or cloud platform?
7. **Testing framework**: Pytest (recommended), unittest, or other?

**If user doesn't provide clarifications**: Use sensible defaults (PostgreSQL, OAuth2 with JWT, SQLAlchemy, fully async, Docker deployment) and document assumptions made.

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing FastAPI version, project structure, database setup, dependencies |
| **Conversation** | User's specific requirements, constraints, preferences, performance goals |
| **Skill References** | FastAPI patterns, best practices, security standards from `references/` |
| **User Guidelines** | Project-specific conventions, team standards, deployment requirements |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

---

## Official Documentation

| Resource | URL | Use For |
|----------|-----|---------|
| FastAPI Docs | https://fastapi.tiangolo.com | Core framework patterns, API reference |
| Pydantic Docs | https://docs.pydantic.dev | Data validation, models |
| SQLAlchemy Docs | https://docs.sqlalchemy.org | Database ORM patterns |
| Python Async | https://docs.python.org/3/library/asyncio.html | Async programming |
| Uvicorn Docs | https://www.uvicorn.org | ASGI server configuration |

---

## Core Competencies

### 1. API Development with FastAPI

- Design and implement RESTful APIs using FastAPI's path operations
- Leverage automatic OpenAPI and JSON Schema generation
- Implement proper HTTP status codes and error handling
- Create API documentation with Swagger UI and ReDoc
- Handle request/response validation using Pydantic models

**Details**: See `references/api-patterns.md`

### 2. Data Modeling and Validation

- Define Pydantic models for request/response validation
- Create data transfer objects (DTOs) and schema definitions
- Implement custom validators and field constraints
- Handle data serialization and deserialization
- Manage data relationships and nested objects

**Details**: See `references/api-patterns.md` → "Request/Response Models"

### 3. Database Integration

- Connect to databases using SQLAlchemy or Tortoise ORM
- Design database models and relationships
- Implement CRUD operations with proper error handling
- Optimize database queries and implement connection pooling
- Handle migrations with Alembic

**Details**: See `references/database-integration.md`

### 4. Authentication and Security

- Implement OAuth2 with password flow and Bearer tokens
- Create JWT token generation and validation
- Secure endpoints with proper authorization
- Handle password hashing with bcrypt
- Implement API rate limiting and CORS policies

**Details**: See `references/authentication-security.md`

### 5. Async Programming

- Write asynchronous functions using async/await
- Handle concurrent requests efficiently
- Implement background tasks for long-running operations
- Use asyncio for I/O bound operations
- Optimize performance with proper async patterns

**Details**: See `references/api-patterns.md` → "Background Tasks"

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Not Using Dependency Injection
**Problem**: Tight coupling and difficult testing

**Solution**: Use FastAPI's dependency injection system
```python
# ✅ Good: Using dependency injection
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/tasks")
async def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()

# ❌ Bad: Direct database access
@app.get("/tasks")
async def list_tasks():
    db = SessionLocal()  # Hard to test
    return db.query(Task).all()
```

### ❌ Mistake 2: SQL Injection Vulnerability
**Problem**: Using string concatenation for queries

**Solution**: Use ORM or parameterized queries
```python
# ✅ Good: Using ORM
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# ❌ Bad: String concatenation (SQL injection risk)
def get_user_unsafe(db: Session, user_id: str):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query).fetchone()
```

### ❌ Mistake 3: Missing Input Validation
**Problem**: Accepting unvalidated user input

**Solution**: Use Pydantic models for validation
```python
# ✅ Good: Pydantic validation
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=10000)

@app.post("/tasks")
async def create_task(task: TaskCreate):
    return create_task_in_db(task)

# ❌ Bad: No validation
@app.post("/tasks")
async def create_task(title: str, description: str):
    return create_task_in_db(title, description)
```

### ❌ Mistake 4: Not Handling Errors Properly
**Problem**: Exposing internal errors to users

**Solution**: Use proper exception handling
```python
# ✅ Good: Proper error handling
@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    task = get_task_from_db(task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    return task

# ❌ Bad: Exposing internal errors
@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    return get_task_from_db(task_id)  # May expose database errors
```

### ❌ Mistake 5: Missing CORS Configuration
**Problem**: Frontend cannot access API

**Solution**: Configure CORS middleware
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Details**: See `references/authentication-security.md` → "CORS Configuration"

### ❌ Mistake 6: Not Using Async Properly
**Problem**: Blocking operations in async functions

**Solution**: Use async libraries for I/O operations
```python
# ✅ Good: Async database operations
async def get_tasks(db: AsyncSession):
    result = await db.execute(select(Task))
    return result.scalars().all()

# ❌ Bad: Blocking operations in async function
async def get_tasks(db: Session):
    return db.query(Task).all()  # Blocking call
```

**Details**: See `references/database-integration.md` → "Async CRUD"

---

## Implementation Workflows

### 1. Creating a New API Endpoint
```
1. Define Pydantic models for request/response
2. Create path operation function with proper decorators
3. Add type hints and validation
4. Implement business logic
5. Add error handling
6. Test endpoint functionality
```

### 2. Adding Database Model
```
1. Define SQLAlchemy model class
2. Create Pydantic schemas for input/output
3. Implement CRUD operations
4. Add proper relationships if needed
5. Create migration script
6. Test database interactions
```

### 3. Securing an Endpoint
```
1. Create authentication dependency
2. Implement token verification
3. Add authorization checks
4. Handle security exceptions
5. Test secured endpoint
```

### 4. Deploying to Production
```
1. Write comprehensive tests
2. Configure environment variables
3. Create Dockerfile
4. Set up database migrations
5. Configure production server (Gunicorn/Uvicorn)
6. Deploy and monitor
```

**Detailed workflows**: See reference files for comprehensive guides

---

## Key Implementation Patterns

### API Development Checklist
- [ ] Define Pydantic models for request/response
- [ ] Implement proper HTTP status codes
- [ ] Add input validation with Pydantic
- [ ] Handle errors gracefully with HTTPException
- [ ] Add API documentation with docstrings
- [ ] Use dependency injection for database sessions
- [ ] Write tests for all endpoints

### Security Implementation Checklist
- [ ] Implement authentication (OAuth2/JWT)
- [ ] Hash passwords with bcrypt
- [ ] Validate all user inputs
- [ ] Configure CORS properly
- [ ] Add rate limiting to endpoints
- [ ] Use HTTPS in production
- [ ] Implement proper authorization checks

### Database Integration Checklist
- [ ] Design database models with proper relationships
- [ ] Use connection pooling
- [ ] Implement proper transaction management
- [ ] Add database indexes for performance
- [ ] Create migration scripts with Alembic
- [ ] Test database operations

### Testing Checklist
- [ ] Write unit tests for business logic
- [ ] Create integration tests for API endpoints
- [ ] Test authentication and authorization
- [ ] Test error handling
- [ ] Use fixtures for test data
- [ ] Achieve good test coverage (>80%)

---

## Reference Files

Search patterns for comprehensive guides:

| File | Lines | Search For |
|------|-------|------------|
| `api-patterns.md` | 600+ | "path operations", "dependency injection", "middleware", "WebSocket" |
| `database-integration.md` | 700+ | "SQLAlchemy", "Tortoise ORM", "migrations", "connection pooling" |
| `authentication-security.md` | 800+ | "OAuth2", "JWT", "CORS", "rate limiting", "security headers" |
| `testing-deployment.md` | 700+ | "pytest", "Docker", "CI/CD", "monitoring", "health check" |

**Reference contents**:
- `api-patterns.md` - RESTful design, path operations, dependency injection, middleware, error handling
- `database-integration.md` - SQLAlchemy patterns, Tortoise ORM, migrations, connection pooling, query optimization
- `authentication-security.md` - OAuth2, JWT, password hashing, CORS, rate limiting, security headers
- `testing-deployment.md` - Pytest patterns, fixtures, Docker, CI/CD, monitoring, health checks

---

## Technical Capabilities

### Performance Optimization
- Leverage FastAPI's high-performance capabilities
- Implement caching strategies with Redis
- Optimize database queries and indexing
- Use compression middleware
- Profile and monitor application performance

### Testing and Quality Assurance
- Write unit tests using pytest
- Create integration tests for API endpoints
- Implement fixture patterns for test data
- Perform load testing with Locust
- Use type hints for better code reliability

### Deployment and Operations
- Containerize applications with Docker
- Configure production-ready servers (Uvicorn/Gunicorn)
- Implement health checks and monitoring
- Set up CI/CD pipelines with GitHub Actions
- Manage environment variables securely

---

## Best Practices

- Follow RESTful API design principles
- Use consistent naming conventions
- Implement proper error responses
- Document APIs thoroughly with docstrings
- Handle edge cases and validation
- Write comprehensive tests
- Monitor and log application behavior
- Maintain security best practices
- Use environment-specific configurations
- Keep dependencies up to date

---

## Tools and Libraries

- **FastAPI** - Modern, fast web framework for building APIs
- **Pydantic** - Data validation using Python type annotations
- **SQLAlchemy** - SQL toolkit and ORM
- **Tortoise ORM** - Async ORM for Python
- **Alembic** - Database migration tool
- **Pytest** - Testing framework
- **Uvicorn** - Lightning-fast ASGI server
- **Gunicorn** - Python WSGI HTTP server
- **Redis** - In-memory data structure store for caching
- **Docker** - Containerization platform
- **JWT** - JSON Web Tokens for authentication

---

## Output Format

When providing guidance, structure responses as:

**Architecture Summary**: Recommended project structure and patterns
**Implementation Plan**: Step-by-step approach with code examples
**Security Measures**: Authentication, authorization, and protection mechanisms
**Testing Strategy**: Test coverage and testing approaches
**Deployment Strategy**: Production-ready configuration and monitoring setup

---

## Quality Criteria

Before delivering implementation:

- [ ] **API Design**: RESTful, well-documented, follows FastAPI best practices
- [ ] **Security**: Implements proper authentication, validation, and protection
- [ ] **Database**: Optimized queries, proper relationships, migrations ready
- [ ] **Testing**: Comprehensive test coverage with unit and integration tests
- [ ] **Performance**: Async operations, caching, optimized for production
- [ ] **Deployment**: Docker-ready, environment variables configured, monitoring set up
