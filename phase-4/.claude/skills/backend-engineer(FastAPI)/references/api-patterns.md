# FastAPI API Patterns and Best Practices

## RESTful API Design

### Path Operations

**Basic CRUD Operations**
```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Task(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    completed: bool = False

# In-memory storage (use database in production)
tasks_db = {}
task_id_counter = 1

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task: Task):
    """Create a new task."""
    global task_id_counter
    task.id = task_id_counter
    tasks_db[task_id_counter] = task
    task_id_counter += 1
    return task

@app.get("/tasks", response_model=List[Task])
async def list_tasks():
    """List all tasks."""
    return list(tasks_db.values())

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: int):
    """Get a specific task."""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    return tasks_db[task_id]

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task: Task):
    """Update a task."""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    task.id = task_id
    tasks_db[task_id] = task
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int):
    """Delete a task."""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    del tasks_db[task_id]
```

### Query Parameters and Filtering

```python
from typing import Optional

@app.get("/tasks", response_model=List[Task])
async def list_tasks(
    completed: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
):
    """List tasks with optional filtering and pagination."""
    tasks = list(tasks_db.values())

    # Filter by completion status
    if completed is not None:
        tasks = [t for t in tasks if t.completed == completed]

    # Pagination
    return tasks[skip : skip + limit]
```

### Path Parameters with Validation

```python
from pydantic import Field

@app.get("/users/{user_id}/tasks/{task_id}")
async def get_user_task(
    user_id: int = Path(..., gt=0, description="User ID must be positive"),
    task_id: int = Path(..., gt=0, description="Task ID must be positive")
):
    """Get a specific task for a user."""
    # Implementation
    pass
```

## Dependency Injection

### Basic Dependencies

```python
from fastapi import Depends, Header, HTTPException

async def verify_token(x_token: str = Header(...)):
    """Verify authentication token."""
    if x_token != "secret-token":
        raise HTTPException(status_code=400, detail="Invalid X-Token header")
    return x_token

async def verify_key(x_key: str = Header(...)):
    """Verify API key."""
    if x_key != "secret-key":
        raise HTTPException(status_code=400, detail="Invalid X-Key header")
    return x_key

@app.get("/protected")
async def protected_route(
    token: str = Depends(verify_token),
    key: str = Depends(verify_key)
):
    """Protected endpoint requiring both token and key."""
    return {"message": "Access granted"}
```

### Database Session Dependency

```python
from sqlalchemy.orm import Session
from database import SessionLocal

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/tasks")
async def list_tasks(db: Session = Depends(get_db)):
    """List tasks from database."""
    return db.query(Task).all()
```

### Current User Dependency

```python
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(user_id)
    if user is None:
        raise credentials_exception
    return user

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user
```

### Class-Based Dependencies

```python
from typing import Optional

class CommonQueryParams:
    def __init__(
        self,
        skip: int = 0,
        limit: int = 100,
        q: Optional[str] = None
    ):
        self.skip = skip
        self.limit = limit
        self.q = q

@app.get("/items")
async def read_items(commons: CommonQueryParams = Depends()):
    """List items with common query parameters."""
    return {
        "skip": commons.skip,
        "limit": commons.limit,
        "q": commons.q
    }
```

## Request/Response Models

### Pydantic Models

```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=10000)
    completed: bool = False

class TaskCreate(TaskBase):
    """Schema for creating a task."""
    pass

class TaskUpdate(BaseModel):
    """Schema for updating a task (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=10000)
    completed: Optional[bool] = None

class TaskInDB(TaskBase):
    """Schema for task in database."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TaskResponse(TaskBase):
    """Schema for task response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
```

### Custom Validators

```python
from pydantic import validator
import re

class UserCreate(BaseModel):
    email: str
    password: str
    username: str

    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', v):
            raise ValueError('Invalid email format')
        return v.lower()

    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

    @validator('username')
    def validate_username(cls, v):
        """Validate username format."""
        if not re.match(r'^[a-zA-Z0-9_-]{3,20}$', v):
            raise ValueError('Username must be 3-20 alphanumeric characters')
        return v
```

## Error Handling

### Custom Exception Handlers

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class TaskNotFoundException(Exception):
    def __init__(self, task_id: int):
        self.task_id = task_id

@app.exception_handler(TaskNotFoundException)
async def task_not_found_handler(request: Request, exc: TaskNotFoundException):
    """Handle task not found exceptions."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Task not found",
            "task_id": exc.task_id,
            "detail": f"Task with ID {exc.task_id} does not exist"
        }
    )

class ValidationException(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message

@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    """Handle validation exceptions."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "field": exc.field,
            "message": exc.message
        }
    )
```

### Structured Error Responses

```python
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error: str
    detail: str
    code: Optional[str] = None

@app.get("/tasks/{task_id}", responses={
    404: {"model": ErrorResponse, "description": "Task not found"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def get_task(task_id: int):
    """Get task with documented error responses."""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error="Not Found",
                detail=f"Task {task_id} not found",
                code="TASK_NOT_FOUND"
            ).dict()
        )
    return tasks_db[task_id]
```

## Middleware

### Custom Middleware

```python
from fastapi import Request
import time
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing."""
    start_time = time.time()

    # Log request
    logger.info(f"Request: {request.method} {request.url}")

    # Process request
    response = await call_next(request)

    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} ({process_time:.3f}s)")

    # Add custom header
    response.headers["X-Process-Time"] = str(process_time)

    return response
```

### CORS Middleware

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Trusted Host Middleware

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)
```

## Background Tasks

### Simple Background Tasks

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    """Send email (simulated)."""
    print(f"Sending email to {email}: {message}")
    # Actual email sending logic here

@app.post("/send-notification")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    """Send notification in background."""
    background_tasks.add_task(send_email, email, "Task completed!")
    return {"message": "Notification will be sent"}
```

### Multiple Background Tasks

```python
def write_log(message: str):
    """Write to log file."""
    with open("log.txt", "a") as f:
        f.write(f"{message}\n")

def update_analytics(user_id: int, action: str):
    """Update analytics."""
    print(f"Analytics: User {user_id} performed {action}")

@app.post("/tasks")
async def create_task(
    task: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Create task with background logging and analytics."""
    # Create task
    new_task = create_task_in_db(task, current_user.id)

    # Add background tasks
    background_tasks.add_task(write_log, f"Task created: {new_task.id}")
    background_tasks.add_task(update_analytics, current_user.id, "create_task")

    return new_task
```

## Response Models and Status Codes

### Multiple Response Models

```python
from typing import Union

@app.get(
    "/items/{item_id}",
    response_model=Union[ItemResponse, ErrorResponse],
    responses={
        200: {"model": ItemResponse, "description": "Successful response"},
        404: {"model": ErrorResponse, "description": "Item not found"}
    }
)
async def get_item(item_id: int):
    """Get item with multiple possible response types."""
    if item_id not in items_db:
        return ErrorResponse(
            error="Not Found",
            detail=f"Item {item_id} not found"
        )
    return items_db[item_id]
```

### Custom Status Codes

```python
from fastapi import Response

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    """Create task with 201 status code."""
    new_task = save_task(task)
    return new_task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int):
    """Delete task with 204 status code."""
    delete_task_from_db(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

## API Versioning

### URL Path Versioning

```python
from fastapi import APIRouter

# Version 1
v1_router = APIRouter(prefix="/api/v1")

@v1_router.get("/tasks")
async def list_tasks_v1():
    """List tasks (v1)."""
    return {"version": "1.0", "tasks": []}

# Version 2
v2_router = APIRouter(prefix="/api/v2")

@v2_router.get("/tasks")
async def list_tasks_v2():
    """List tasks (v2) with enhanced features."""
    return {"version": "2.0", "tasks": [], "total": 0}

app.include_router(v1_router)
app.include_router(v2_router)
```

### Header-Based Versioning

```python
@app.get("/tasks")
async def list_tasks(api_version: str = Header(default="1.0")):
    """List tasks with version from header."""
    if api_version == "2.0":
        return {"version": "2.0", "tasks": [], "total": 0}
    return {"version": "1.0", "tasks": []}
```

## WebSocket Support

### Basic WebSocket

```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
```

### WebSocket with Connection Manager

```python
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    """WebSocket with connection management."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client {client_id} left")
```

## File Uploads

### Single File Upload

```python
from fastapi import File, UploadFile

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a single file."""
    contents = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents)
    }
```

### Multiple File Uploads

```python
from typing import List

@app.post("/upload-multiple")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """Upload multiple files."""
    results = []
    for file in files:
        contents = await file.read()
        results.append({
            "filename": file.filename,
            "size": len(contents)
        })
    return results
```

### File Upload with Validation

```python
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload image with validation."""
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG and PNG images are allowed"
        )

    # Validate file size (max 5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size must be less than 5MB"
        )

    # Save file
    with open(f"uploads/{file.filename}", "wb") as f:
        f.write(contents)

    return {"filename": file.filename, "size": len(contents)}
```
