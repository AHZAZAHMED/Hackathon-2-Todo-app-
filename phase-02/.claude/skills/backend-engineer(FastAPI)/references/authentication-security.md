# FastAPI Authentication and Security

## OAuth2 with Password Flow

### Basic OAuth2 Setup

**OAuth2 Password Bearer**
```python
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI()

# Security configuration
SECRET_KEY = "your-secret-key-keep-it-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Password hashing
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)

# Token creation
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Authentication
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(username=username)
    if user is None:
        raise credentials_exception
    return user

# Login endpoint
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint to get access token."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protected endpoint
@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user
```

### JWT Token with Refresh Tokens

```python
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Token configuration
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_refresh_token(data: dict):
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login to get access and refresh tokens."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/token/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")

        if username is None or token_type != "refresh":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(username=username)
    if user is None:
        raise credentials_exception

    # Create new tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
```

## Role-Based Access Control (RBAC)

### User Roles and Permissions

```python
from enum import Enum
from typing import List

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

class User(BaseModel):
    username: str
    email: str
    roles: List[Role] = [Role.USER]
    is_active: bool = True

def has_role(user: User, required_roles: List[Role]) -> bool:
    """Check if user has required role."""
    return any(role in user.roles for role in required_roles)

# Role-based dependency
def require_role(required_roles: List[Role]):
    """Dependency to require specific roles."""
    async def role_checker(current_user: User = Depends(get_current_user)):
        if not has_role(current_user, required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# Admin-only endpoint
@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_role([Role.ADMIN]))
):
    """Delete user (admin only)."""
    delete_user_from_db(user_id)
    return {"message": "User deleted"}

# Moderator or admin endpoint
@app.post("/posts/{post_id}/moderate")
async def moderate_post(
    post_id: int,
    current_user: User = Depends(require_role([Role.ADMIN, Role.MODERATOR]))
):
    """Moderate post (admin or moderator)."""
    moderate_post_in_db(post_id)
    return {"message": "Post moderated"}
```

### Permission-Based Access Control

```python
from typing import Set

class Permission(str, Enum):
    READ_USERS = "read:users"
    WRITE_USERS = "write:users"
    DELETE_USERS = "delete:users"
    READ_POSTS = "read:posts"
    WRITE_POSTS = "write:posts"

class User(BaseModel):
    username: str
    permissions: Set[Permission] = set()

def has_permission(user: User, required_permissions: Set[Permission]) -> bool:
    """Check if user has required permissions."""
    return required_permissions.issubset(user.permissions)

def require_permissions(required_permissions: Set[Permission]):
    """Dependency to require specific permissions."""
    async def permission_checker(current_user: User = Depends(get_current_user)):
        if not has_permission(current_user, required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {required_permissions}"
            )
        return current_user
    return permission_checker

@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_permissions({Permission.DELETE_USERS}))
):
    """Delete user (requires delete:users permission)."""
    delete_user_from_db(user_id)
    return {"message": "User deleted"}
```

## API Key Authentication

### Simple API Key

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    """Validate API key."""
    if api_key != "your-secret-api-key":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    return api_key

@app.get("/protected")
async def protected_route(api_key: str = Depends(get_api_key)):
    """Protected endpoint requiring API key."""
    return {"message": "Access granted"}
```

### Database-Backed API Keys

```python
from sqlalchemy.orm import Session

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

async def get_api_key(
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
):
    """Validate API key from database."""
    db_key = db.query(APIKey).filter(
        APIKey.key == api_key,
        APIKey.is_active == True
    ).first()

    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or inactive API Key"
        )

    # Check expiration
    if db_key.expires_at and db_key.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key has expired"
        )

    return db_key
```

## CORS Configuration

### Basic CORS Setup

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment-Specific CORS

```python
import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    allowed_origins = [
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ]
else:
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:8080"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=3600,
)
```

## Rate Limiting

### Simple Rate Limiter

```python
from fastapi import Request
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, requests: int, window: int):
        """
        Initialize rate limiter.

        Args:
            requests: Number of requests allowed
            window: Time window in seconds
        """
        self.requests = requests
        self.window = window
        self.clients = defaultdict(list)

    async def __call__(self, request: Request):
        """Check rate limit for client."""
        client_ip = request.client.host
        now = datetime.now()

        # Clean old requests
        self.clients[client_ip] = [
            req_time for req_time in self.clients[client_ip]
            if now - req_time < timedelta(seconds=self.window)
        ]

        # Check limit
        if len(self.clients[client_ip]) >= self.requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )

        # Add current request
        self.clients[client_ip].append(now)

# Apply rate limiter
rate_limiter = RateLimiter(requests=10, window=60)

@app.get("/limited")
async def limited_endpoint(request: Request, _: None = Depends(rate_limiter)):
    """Rate-limited endpoint (10 requests per minute)."""
    return {"message": "Success"}
```

### Redis-Based Rate Limiter

```python
import redis
from fastapi import Request

redis_client = redis.Redis(host='localhost', port=6379, db=0)

async def rate_limit_redis(request: Request, limit: int = 10, window: int = 60):
    """Rate limit using Redis."""
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"

    # Get current count
    current = redis_client.get(key)

    if current is None:
        # First request
        redis_client.setex(key, window, 1)
    elif int(current) >= limit:
        # Limit exceeded
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    else:
        # Increment counter
        redis_client.incr(key)

@app.get("/limited")
async def limited_endpoint(request: Request, _: None = Depends(rate_limit_redis)):
    """Rate-limited endpoint using Redis."""
    return {"message": "Success"}
```

## Security Headers

### Security Headers Middleware

```python
from fastapi import Request

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)

    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Enable XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Enforce HTTPS
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # Content Security Policy
    response.headers["Content-Security-Policy"] = "default-src 'self'"

    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Permissions Policy
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

    return response
```

## Input Validation and Sanitization

### SQL Injection Prevention

```python
# ✅ Good: Using ORM (SQLAlchemy)
def get_user_safe(db: Session, user_id: int):
    """Safe query using ORM."""
    return db.query(User).filter(User.id == user_id).first()

# ✅ Good: Parameterized query
def get_user_parameterized(db: Session, user_id: int):
    """Safe query using parameters."""
    result = db.execute(
        "SELECT * FROM users WHERE id = :user_id",
        {"user_id": user_id}
    )
    return result.fetchone()

# ❌ Bad: String concatenation (SQL injection risk)
def get_user_unsafe(db: Session, user_id: str):
    """UNSAFE: SQL injection vulnerability."""
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query).fetchone()
```

### XSS Prevention

```python
import bleach
from pydantic import validator

class PostCreate(BaseModel):
    title: str
    content: str

    @validator('content')
    def sanitize_content(cls, v):
        """Sanitize HTML content to prevent XSS."""
        allowed_tags = ['p', 'br', 'strong', 'em', 'a']
        allowed_attributes = {'a': ['href', 'title']}
        return bleach.clean(v, tags=allowed_tags, attributes=allowed_attributes)
```

### Path Traversal Prevention

```python
import os
from pathlib import Path

UPLOAD_DIR = Path("/var/uploads")

@app.get("/files/{filename}")
async def get_file(filename: str):
    """Get file with path traversal protection."""
    # Resolve path and check if it's within upload directory
    file_path = (UPLOAD_DIR / filename).resolve()

    if not str(file_path).startswith(str(UPLOAD_DIR)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file path"
        )

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    return FileResponse(file_path)
```

## Secrets Management

### Environment Variables

```python
from pydantic import BaseSettings, SecretStr

class Settings(BaseSettings):
    """Application settings from environment variables."""
    database_url: SecretStr
    secret_key: SecretStr
    api_key: SecretStr

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Access secret values
db_url = settings.database_url.get_secret_value()
```

### Secrets Validation

```python
from pydantic import validator

class Settings(BaseSettings):
    secret_key: SecretStr
    database_url: SecretStr

    @validator('secret_key')
    def validate_secret_key(cls, v):
        """Validate secret key strength."""
        secret = v.get_secret_value()
        if len(secret) < 32:
            raise ValueError("Secret key must be at least 32 characters")
        return v

    @validator('database_url')
    def validate_database_url(cls, v):
        """Validate database URL format."""
        url = v.get_secret_value()
        if not url.startswith(('postgresql://', 'mysql://', 'sqlite://')):
            raise ValueError("Invalid database URL format")
        return v
```

## HTTPS and SSL/TLS

### Force HTTPS Redirect

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Only in production
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

### SSL Configuration for Uvicorn

```bash
# Run with SSL
uvicorn main:app --host 0.0.0.0 --port 443 \
    --ssl-keyfile=/path/to/key.pem \
    --ssl-certfile=/path/to/cert.pem
```

## Security Best Practices Checklist

### Authentication & Authorization
- [ ] Use strong password hashing (bcrypt, argon2)
- [ ] Implement JWT with proper expiration
- [ ] Use refresh tokens for long-lived sessions
- [ ] Implement role-based or permission-based access control
- [ ] Validate tokens on every protected request
- [ ] Implement rate limiting on authentication endpoints

### Input Validation
- [ ] Use Pydantic models for all input validation
- [ ] Sanitize HTML content to prevent XSS
- [ ] Use parameterized queries to prevent SQL injection
- [ ] Validate file uploads (type, size, content)
- [ ] Implement path traversal protection

### API Security
- [ ] Configure CORS properly (specific origins, not *)
- [ ] Add security headers (CSP, X-Frame-Options, etc.)
- [ ] Implement rate limiting
- [ ] Use HTTPS in production
- [ ] Validate API keys from database

### Secrets Management
- [ ] Store secrets in environment variables
- [ ] Never commit secrets to version control
- [ ] Use strong, randomly generated secrets
- [ ] Rotate secrets regularly
- [ ] Validate secret strength at startup

### Error Handling
- [ ] Don't expose sensitive information in error messages
- [ ] Log security events
- [ ] Implement proper exception handling
- [ ] Return generic error messages to clients
