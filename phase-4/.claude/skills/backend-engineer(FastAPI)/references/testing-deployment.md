# FastAPI Testing and Deployment

## Testing with Pytest

### Test Setup

**conftest.py**
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    """Create test database."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    """Create test client."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### Unit Tests

**Testing Endpoints**
```python
def test_create_task(client):
    """Test creating a task."""
    response = client.post(
        "/tasks",
        json={"title": "Test Task", "description": "Test Description"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert "id" in data

def test_get_task(client):
    """Test getting a task."""
    # Create task
    create_response = client.post(
        "/tasks",
        json={"title": "Test Task"}
    )
    task_id = create_response.json()["id"]

    # Get task
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task"

def test_get_nonexistent_task(client):
    """Test getting a nonexistent task."""
    response = client.get("/tasks/999")
    assert response.status_code == 404

def test_update_task(client):
    """Test updating a task."""
    # Create task
    create_response = client.post(
        "/tasks",
        json={"title": "Original Title"}
    )
    task_id = create_response.json()["id"]

    # Update task
    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated Title", "completed": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["completed"] is True

def test_delete_task(client):
    """Test deleting a task."""
    # Create task
    create_response = client.post(
        "/tasks",
        json={"title": "Test Task"}
    )
    task_id = create_response.json()["id"]

    # Delete task
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    # Verify deletion
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404
```

**Testing Authentication**
```python
def test_login_success(client):
    """Test successful login."""
    # Create user first
    client.post(
        "/register",
        json={"username": "testuser", "password": "testpass123"}
    )

    # Login
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/token",
        data={"username": "invalid", "password": "wrong"}
    )
    assert response.status_code == 401

def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token."""
    response = client.get("/users/me")
    assert response.status_code == 401

def test_protected_endpoint_with_token(client):
    """Test accessing protected endpoint with valid token."""
    # Register and login
    client.post(
        "/register",
        json={"username": "testuser", "password": "testpass123"}
    )
    login_response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]

    # Access protected endpoint
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
```

### Fixtures and Factories

**User Factory**
```python
import pytest
from models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture
def user_factory(db):
    """Factory for creating test users."""
    def create_user(username="testuser", email="test@example.com", password="testpass"):
        user = User(
            username=username,
            email=email,
            hashed_password=pwd_context.hash(password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    return create_user

def test_with_user_factory(client, user_factory):
    """Test using user factory."""
    user = user_factory(username="john", email="john@example.com")
    assert user.id is not None
    assert user.username == "john"
```

**Authenticated Client Fixture**
```python
@pytest.fixture
def authenticated_client(client, user_factory):
    """Create authenticated test client."""
    user = user_factory()

    # Get token
    response = client.post(
        "/token",
        data={"username": user.username, "password": "testpass"}
    )
    token = response.json()["access_token"]

    # Add token to client headers
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

def test_with_authenticated_client(authenticated_client):
    """Test using authenticated client."""
    response = authenticated_client.get("/users/me")
    assert response.status_code == 200
```

### Async Testing

**Async Test Setup**
```python
import pytest
from httpx import AsyncClient
from main import app

@pytest.fixture
async def async_client():
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_async_endpoint(async_client):
    """Test async endpoint."""
    response = await async_client.get("/tasks")
    assert response.status_code == 200
```

### Parametrized Tests

```python
@pytest.mark.parametrize("title,description,expected_status", [
    ("Valid Task", "Valid Description", 201),
    ("", "No title", 422),  # Validation error
    ("A" * 300, "Too long title", 422),  # Exceeds max length
])
def test_create_task_validation(client, title, description, expected_status):
    """Test task creation with various inputs."""
    response = client.post(
        "/tasks",
        json={"title": title, "description": description}
    )
    assert response.status_code == expected_status
```

### Mocking Dependencies

```python
from unittest.mock import Mock, patch

def test_with_mocked_database(client):
    """Test with mocked database."""
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    response = client.get("/tasks/1")
    assert response.status_code == 404

    app.dependency_overrides.clear()

@patch('services.email.send_email')
def test_with_mocked_email(mock_send_email, client):
    """Test with mocked email service."""
    mock_send_email.return_value = True

    response = client.post(
        "/send-notification",
        json={"email": "test@example.com", "message": "Test"}
    )
    assert response.status_code == 200
    mock_send_email.assert_called_once()
```

## Docker Deployment

### Dockerfile

**Production Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Multi-Stage Dockerfile**
```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

**docker-compose.yml**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/appdb
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=appdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

**Production docker-compose.yml**
```yaml
version: '3.8'

services:
  api:
    image: myapp:latest
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    depends_on:
      - db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api

volumes:
  postgres_data:
```

## Production Server Configuration

### Uvicorn with Gunicorn

**gunicorn_conf.py**
```python
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "fastapi-app"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None
```

**Run with Gunicorn**
```bash
gunicorn main:app -c gunicorn_conf.py
```

### Systemd Service

**fastapi.service**
```ini
[Unit]
Description=FastAPI Application
After=network.target

[Service]
Type=notify
User=appuser
Group=appuser
WorkingDirectory=/opt/app
Environment="PATH=/opt/app/venv/bin"
ExecStart=/opt/app/venv/bin/gunicorn main:app -c gunicorn_conf.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Enable and start service**
```bash
sudo systemctl enable fastapi
sudo systemctl start fastapi
sudo systemctl status fastapi
```

## CI/CD Pipeline

### GitHub Actions

**.github/workflows/test.yml**
```yaml
name: Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
        run: |
          pytest --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

**.github/workflows/deploy.yml**
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: |
          docker build -t myapp:${{ github.sha }} .
          docker tag myapp:${{ github.sha }} myapp:latest

      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push myapp:${{ github.sha }}
          docker push myapp:latest

      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/app
            docker-compose pull
            docker-compose up -d
```

## Monitoring and Logging

### Health Check Endpoint

```python
from fastapi import status
from sqlalchemy import text

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Check database connection
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
```

### Structured Logging

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON log formatter."""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

# Configure logging
logging.basicConfig(level=logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger(__name__)
logger.addHandler(handler)

# Usage
logger.info("User logged in", extra={"user_id": 123})
logger.error("Database error", exc_info=True)
```

### Request Logging Middleware

```python
import time
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests."""
    start_time = time.time()

    # Log request
    logger.info(
        "Request started",
        extra={
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host
        }
    )

    # Process request
    response = await call_next(request)

    # Log response
    process_time = time.time() - start_time
    logger.info(
        "Request completed",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": f"{process_time:.3f}s"
        }
    )

    return response
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Response

# Metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    """Collect Prometheus metrics."""
    start_time = time.time()

    response = await call_next(request)

    # Record metrics
    duration = time.time() - start_time
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response

@app.get("/metrics")
async def metrics():
    """Expose Prometheus metrics."""
    return Response(content=generate_latest(), media_type="text/plain")
```

## Performance Testing

### Load Testing with Locust

**locustfile.py**
```python
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login before starting tasks."""
        response = self.client.post(
            "/token",
            data={"username": "testuser", "password": "testpass"}
        )
        self.token = response.json()["access_token"]
        self.client.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def list_tasks(self):
        """List tasks (weight: 3)."""
        self.client.get("/tasks")

    @task(2)
    def create_task(self):
        """Create task (weight: 2)."""
        self.client.post(
            "/tasks",
            json={"title": "Load Test Task", "description": "Testing"}
        )

    @task(1)
    def get_task(self):
        """Get specific task (weight: 1)."""
        self.client.get("/tasks/1")
```

**Run load test**
```bash
locust -f locustfile.py --host=http://localhost:8000
```

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] SSL certificates configured
- [ ] Monitoring and logging set up
- [ ] Health check endpoint implemented
- [ ] Rate limiting configured

### Deployment
- [ ] Build Docker image
- [ ] Push to container registry
- [ ] Run database migrations
- [ ] Deploy new version
- [ ] Verify health check
- [ ] Run smoke tests
- [ ] Monitor error rates

### Post-Deployment
- [ ] Verify application is accessible
- [ ] Check logs for errors
- [ ] Monitor performance metrics
- [ ] Test critical user flows
- [ ] Verify database connections
- [ ] Check external service integrations
