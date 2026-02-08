# Extended Troubleshooting Guide for Better Auth Integration

## Authentication Issues

### Issue: User can register but cannot login

**Symptoms:**
- Registration succeeds and returns token
- Login with same credentials fails with "Invalid credentials"
- User exists in database

**Diagnosis Steps:**

1. Check password hashing consistency:
```python
# In registration endpoint
password_hash = pwd_context.hash(password)
print(f"Hashed password: {password_hash[:20]}...")

# In login endpoint
is_valid = pwd_context.verify(password, user.password_hash)
print(f"Password verification: {is_valid}")
```

2. Verify password context configuration:
```python
# Ensure same configuration in both endpoints
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Must be consistent
)
```

3. Check for whitespace issues:
```python
# Trim whitespace from inputs
email = email.strip()
password = password.strip()
```

**Common Causes:**
- Different password hashing configurations between registration and login
- Whitespace in password input
- Case sensitivity in email comparison
- Password field truncated in database

**Solutions:**

1. Use consistent password context:
```python
# Create shared password context
# src/auth/password.py
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

# Import in both auth routes
from ..auth.password import pwd_context
```

2. Normalize email addresses:
```python
def normalize_email(email: str) -> str:
    """Normalize email to lowercase and trim whitespace."""
    return email.strip().lower()

# Use in both registration and login
email = normalize_email(email)
```

3. Verify database field length:
```sql
-- Ensure password_hash field is long enough
ALTER TABLE users ALTER COLUMN password_hash TYPE VARCHAR(255);
```

### Issue: Token verification fails with "Invalid token"

**Symptoms:**
- Token generated successfully
- Backend returns 401 "Invalid token"
- Token looks valid (3 parts, base64 encoded)

**Diagnosis Steps:**

1. Compare secrets:
```bash
# Frontend
echo $BETTER_AUTH_SECRET | head -c 20

# Backend
python -c "from src.core.config import settings; print(settings.better_auth_secret[:20])"
```

2. Decode token manually:
```python
import jwt
import base64

token = "eyJhbGc..."

# Decode without verification
payload = jwt.decode(token, options={"verify_signature": False})
print(f"Payload: {payload}")

# Try to verify
try:
    verified = jwt.decode(token, "your-secret", algorithms=["HS256"])
    print("Verification successful")
except Exception as e:
    print(f"Verification failed: {e}")
```

3. Check algorithm:
```python
# Ensure HS256 is used consistently
# Generation
token = jwt.encode(payload, secret, algorithm="HS256")

# Verification
payload = jwt.decode(token, secret, algorithms=["HS256"])
```

**Common Causes:**
- BETTER_AUTH_SECRET mismatch between frontend and backend
- Different JWT algorithms used
- Token corrupted during transmission
- Extra whitespace in token string

**Solutions:**

1. Verify secrets match exactly:
```bash
# Generate once, use everywhere
SECRET=$(openssl rand -hex 32)

# Frontend .env.local
echo "BETTER_AUTH_SECRET=$SECRET" >> .env.local

# Backend .env
echo "BETTER_AUTH_SECRET=$SECRET" >> .env
```

2. Trim token before verification:
```python
token = authorization.replace("Bearer ", "").strip()
```

3. Log token details for debugging:
```python
import logging

logger.info(f"Token length: {len(token)}")
logger.info(f"Token parts: {len(token.split('.'))}")
logger.info(f"Token header: {token.split('.')[0]}")
```

### Issue: Authentication state lost on page refresh

**Symptoms:**
- User logs in successfully
- Page refresh redirects to login
- Token exists in localStorage

**Diagnosis Steps:**

1. Check if token is being restored:
```typescript
useEffect(() => {
  console.log('Checking session...')
  const token = localStorage.getItem('auth-token')
  console.log('Token found:', !!token)

  if (token) {
    console.log('Token valid:', isTokenValid(token))
    const payload = decodeToken(token)
    console.log('Payload:', payload)
  }
}, [])
```

2. Verify useEffect dependencies:
```typescript
// ❌ BAD: Missing dependencies
useEffect(() => {
  checkSession()
}, [])

// ✅ GOOD: Proper dependencies
useEffect(() => {
  checkSession()
}, []) // Empty array is correct for one-time initialization
```

3. Check loading state:
```typescript
const [loading, setLoading] = useState(true)

useEffect(() => {
  const checkSession = async () => {
    // ... restore session
    setLoading(false) // Must set loading to false
  }
  checkSession()
}, [])

// Don't render until loading is false
if (loading) return <LoadingSpinner />
```

**Common Causes:**
- useEffect not running on mount
- Loading state never set to false
- Token not being decoded properly
- User state not being updated

**Solutions:**

1. Ensure proper session restoration:
```typescript
useEffect(() => {
  const checkSession = async () => {
    try {
      const token = localStorage.getItem('auth-token')
      if (token && isTokenValid(token)) {
        const payload = JSON.parse(atob(token.split('.')[1]))
        setUser({
          id: payload.sub,
          email: payload.email,
          name: payload.name
        })
      }
    } catch (error) {
      console.error('Session restoration failed:', error)
      localStorage.removeItem('auth-token')
    } finally {
      setLoading(false)
    }
  }

  checkSession()
}, [])
```

2. Add error boundaries:
```typescript
try {
  const payload = JSON.parse(atob(token.split('.')[1]))
  setUser(payload)
} catch (error) {
  console.error('Token decode error:', error)
  localStorage.removeItem('auth-token')
}
```

## Database Issues

### Issue: "relation 'task' does not exist"

**Symptoms:**
- Application starts without errors
- API requests fail with database error
- Tables not created in database

**Diagnosis Steps:**

1. Check if startup event is registered:
```python
@app.on_event("startup")
def on_startup():
    print("Startup event triggered")
    SQLModel.metadata.create_all(bind=engine)
    print("Tables created")
```

2. Verify models are imported:
```python
# main.py
from src.models import task, user  # Must import before create_all

@app.on_event("startup")
def on_startup():
    print(f"Registered tables: {SQLModel.metadata.tables.keys()}")
    SQLModel.metadata.create_all(bind=engine)
```

3. Check database connection:
```python
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Tables in database: {tables}")
```

**Common Causes:**
- Models not imported before create_all()
- Startup event not registered
- Database connection failure
- Wrong database URL

**Solutions:**

1. Import all models explicitly:
```python
# main.py
from src.models import task  # Import model
from src.models import user  # Import all models

@app.on_event("startup")
def on_startup():
    """Create database tables on startup."""
    SQLModel.metadata.create_all(bind=engine)
```

2. Verify database connection:
```python
from sqlalchemy import text

@app.on_event("startup")
def on_startup():
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("Database connection successful")

    # Create tables
    SQLModel.metadata.create_all(bind=engine)
```

3. Use Alembic for migrations (production):
```bash
# Install Alembic
pip install alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Create tables"

# Apply migration
alembic upgrade head
```

### Issue: User can access other users' data

**Symptoms:**
- User can view/modify tasks belonging to other users
- No authorization errors
- User isolation not enforced

**Diagnosis Steps:**

1. Check if user_id is verified:
```python
@router.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    current_user: dict = Depends(verify_jwt_token)
):
    print(f"URL user_id: {user_id}")
    print(f"Token user_id: {current_user['sub']}")
    print(f"Match: {user_id == current_user['sub']}")

    # Should raise 403 if mismatch
```

2. Test with different users:
```python
# Create two users
user1 = create_user("user1@example.com")
user2 = create_user("user2@example.com")

# User 1 creates task
task = create_task(user1.token, "User 1 task")

# User 2 tries to access
response = get_task(user2.token, task.id)
print(f"Response status: {response.status_code}")  # Should be 403
```

3. Check database queries:
```python
# Verify query filters by user_id
tasks = session.exec(
    select(Task).where(Task.user_id == user_id)
).all()

print(f"Query: SELECT * FROM tasks WHERE user_id = '{user_id}'")
```

**Common Causes:**
- Missing user_id verification in routes
- Database queries not filtered by user_id
- Authorization dependency not applied
- user_id parameter not validated

**Solutions:**

1. Add user verification dependency:
```python
async def verify_user_access(
    user_id: str,
    current_user: dict = Depends(verify_jwt_token)
) -> dict:
    """Verify user can access resource."""
    if current_user["sub"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden"
        )
    return current_user

# Apply to all routes
@router.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    current_user: dict = Depends(verify_user_access)
):
    # User is verified
    pass
```

2. Always filter queries by user_id:
```python
# ❌ BAD: Returns all tasks
tasks = session.exec(select(Task)).all()

# ✅ GOOD: Returns only user's tasks
tasks = session.exec(
    select(Task).where(Task.user_id == current_user["sub"])
).all()
```

3. Add integration tests:
```python
def test_user_isolation():
    """Test users cannot access other users' data."""
    # Create two users
    user1_token = register_and_login("user1@example.com")
    user2_token = register_and_login("user2@example.com")

    # User 1 creates task
    task = create_task(user1_token, "Private task")

    # User 2 tries to access User 1's task
    response = requests.get(
        f"{BASE_URL}/api/{user1_id}/tasks/{task.id}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )

    assert response.status_code == 403
```

## CORS Issues

### Issue: CORS errors in browser console

**Symptoms:**
- Browser console shows CORS error
- Network tab shows request blocked
- Backend never receives request

**Diagnosis Steps:**

1. Check CORS middleware configuration:
```python
# Print CORS configuration
print(f"Allowed origins: {settings.cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. Verify request origin:
```javascript
// In browser console
console.log('Request origin:', window.location.origin)
// Should match backend's allow_origins
```

3. Check preflight request:
```bash
# Test OPTIONS request
curl -X OPTIONS http://localhost:8000/api/tasks \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -v
```

**Common Causes:**
- Frontend origin not in allow_origins
- CORS middleware not configured
- Credentials not allowed
- Wrong HTTP method

**Solutions:**

1. Configure CORS properly:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://yourdomain.com"  # Production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)
```

2. Use environment-specific origins:
```python
if settings.environment == "production":
    allowed_origins = ["https://yourdomain.com"]
else:
    allowed_origins = ["http://localhost:3000", "http://localhost:3001"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. Debug CORS headers:
```python
@app.middleware("http")
async def log_cors_headers(request, call_next):
    response = await call_next(request)
    print(f"CORS headers: {response.headers}")
    return response
```

## Performance Issues

### Issue: Slow authentication requests

**Symptoms:**
- Login/registration takes several seconds
- High CPU usage during authentication
- Slow password verification

**Diagnosis Steps:**

1. Profile password hashing:
```python
import time

start = time.time()
password_hash = pwd_context.hash(password)
hash_time = time.time() - start
print(f"Password hashing took: {hash_time:.3f}s")

start = time.time()
is_valid = pwd_context.verify(password, password_hash)
verify_time = time.time() - start
print(f"Password verification took: {verify_time:.3f}s")
```

2. Check bcrypt rounds:
```python
pwd_context = CryptContext(
    schemes=["bcrypt"],
    bcrypt__rounds=12  # Higher = slower but more secure
)
```

3. Monitor database queries:
```python
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

**Common Causes:**
- Too many bcrypt rounds
- N+1 query problems
- Missing database indexes
- No connection pooling

**Solutions:**

1. Optimize bcrypt rounds:
```python
# Balance security and performance
pwd_context = CryptContext(
    schemes=["bcrypt"],
    bcrypt__rounds=12  # 12 is good balance
)
```

2. Add database indexes:
```python
class User(SQLModel, table=True):
    email: str = Field(unique=True, index=True)  # Index for lookups

class Task(SQLModel, table=True):
    user_id: str = Field(index=True)  # Index for filtering
```

3. Use connection pooling:
```python
engine = create_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

4. Cache user lookups (optional):
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_user_by_email(email: str):
    """Cache user lookups."""
    return session.exec(
        select(User).where(User.email == email)
    ).first()
```

## Testing Issues

### Issue: Tests fail with "Database is locked"

**Symptoms:**
- Tests fail intermittently
- Error: "database is locked"
- SQLite specific issue

**Solutions:**

1. Use PostgreSQL for tests:
```python
# conftest.py
@pytest.fixture
def test_db():
    """Use PostgreSQL for tests."""
    engine = create_engine(
        "postgresql://test:test@localhost/test_db"
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
```

2. Use in-memory SQLite with proper configuration:
```python
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False}
)
```

3. Use separate database per test:
```python
@pytest.fixture
def session():
    """Create fresh database for each test."""
    engine = create_engine("sqlite:///test.db")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    os.remove("test.db")
```

### Issue: Frontend tests fail with authentication errors

**Symptoms:**
- E2E tests fail at login step
- Token not being stored
- Authentication state not persisting in tests

**Solutions:**

1. Mock localStorage in tests:
```typescript
// Setup localStorage mock
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
}
global.localStorage = localStorageMock as any
```

2. Use Playwright's storage state:
```typescript
// Save authentication state
await page.context().storageState({ path: 'auth.json' })

// Reuse in other tests
const context = await browser.newContext({
  storageState: 'auth.json'
})
```

3. Create test utilities:
```typescript
async function loginAsTestUser(page: Page) {
  await page.goto('/login')
  await page.fill('[name="email"]', 'test@example.com')
  await page.fill('[name="password"]', 'password123')
  await page.click('button[type="submit"]')
  await page.waitForURL('/dashboard')
}
```

## Deployment Issues

### Issue: Authentication works locally but fails in production

**Symptoms:**
- Local development works fine
- Production returns 401 errors
- Environment variables seem correct

**Diagnosis Steps:**

1. Verify environment variables in production:
```bash
# Check if variables are set
echo $BETTER_AUTH_SECRET | head -c 20

# Verify they match
# Frontend
echo $BETTER_AUTH_SECRET
# Backend
echo $BETTER_AUTH_SECRET
```

2. Check HTTPS configuration:
```python
# Ensure secure cookies in production
if settings.environment == "production":
    response.set_cookie(
        key="auth-token",
        value=token,
        secure=True,  # HTTPS only
        httponly=True,
        samesite="lax"
    )
```

3. Verify CORS origins:
```python
# Use production domain
allow_origins=[
    "https://yourdomain.com",  # Not http://
    "https://www.yourdomain.com"
]
```

**Common Causes:**
- Environment variables not set in production
- HTTP instead of HTTPS
- Wrong CORS origins
- Cookie settings incompatible with production

**Solutions:**

1. Use environment-specific configuration:
```python
class Settings(BaseSettings):
    environment: str = "development"

    @property
    def cors_origins(self) -> list[str]:
        if self.environment == "production":
            return ["https://yourdomain.com"]
        return ["http://localhost:3000"]

    @property
    def cookie_secure(self) -> bool:
        return self.environment == "production"
```

2. Verify deployment checklist:
- [ ] BETTER_AUTH_SECRET set and matches
- [ ] DATABASE_URL points to production database
- [ ] CORS origins include production domain
- [ ] HTTPS enforced
- [ ] Secure cookies enabled
- [ ] Environment set to "production"

3. Add health check endpoint:
```python
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "cors_origins": settings.cors_origins,
        "database_connected": check_db_connection()
    }
```
