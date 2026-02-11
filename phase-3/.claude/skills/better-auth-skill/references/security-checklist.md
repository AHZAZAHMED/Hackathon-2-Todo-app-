# Security Checklist for Better Auth Integration

## Environment Security

### Secret Management

- [ ] **Generate strong secrets**
  ```bash
  # Use cryptographically secure random generation
  openssl rand -hex 32
  # Or
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

- [ ] **Same secret in frontend and backend**
  ```bash
  # Verify secrets match
  # Frontend .env.local
  BETTER_AUTH_SECRET=abc123...

  # Backend .env
  BETTER_AUTH_SECRET=abc123...  # Must be identical
  ```

- [ ] **Never commit secrets to version control**
  ```gitignore
  # .gitignore
  .env
  .env.local
  .env.*.local
  *.pem
  *.key
  ```

- [ ] **Use environment variables, never hardcode**
  ```python
  # ❌ BAD
  SECRET_KEY = "my-secret-key"

  # ✅ GOOD
  from pydantic_settings import BaseSettings

  class Settings(BaseSettings):
      better_auth_secret: str

      class Config:
          env_file = ".env"
  ```

- [ ] **Rotate secrets periodically**
  - Production: Every 90 days
  - After security incident: Immediately
  - When team member leaves: Within 24 hours

### HTTPS/TLS

- [ ] **Enforce HTTPS in production**
  ```python
  # FastAPI
  if settings.environment == "production":
      app.add_middleware(
          HTTPSRedirectMiddleware
      )
  ```

- [ ] **Use secure cookies**
  ```python
  response.set_cookie(
      key="auth-token",
      value=token,
      secure=True,      # HTTPS only
      httponly=True,    # No JavaScript access
      samesite="lax"    # CSRF protection
  )
  ```

- [ ] **Configure security headers**
  ```python
  @app.middleware("http")
  async def add_security_headers(request, call_next):
      response = await call_next(request)
      response.headers["Strict-Transport-Security"] = "max-age=31536000"
      response.headers["X-Content-Type-Options"] = "nosniff"
      response.headers["X-Frame-Options"] = "DENY"
      response.headers["X-XSS-Protection"] = "1; mode=block"
      return response
  ```

## Authentication Security

### Password Security

- [ ] **Use strong password hashing**
  ```python
  from passlib.context import CryptContext

  pwd_context = CryptContext(
      schemes=["bcrypt"],
      deprecated="auto",
      bcrypt__rounds=12  # Cost factor
  )

  # Hash password
  hashed = pwd_context.hash(plain_password)

  # Verify password
  is_valid = pwd_context.verify(plain_password, hashed)
  ```

- [ ] **Enforce password requirements**
  ```python
  def validate_password(password: str) -> bool:
      """Validate password meets security requirements."""
      if len(password) < 8:
          return False
      if not any(c.isupper() for c in password):
          return False
      if not any(c.islower() for c in password):
          return False
      if not any(c.isdigit() for c in password):
          return False
      return True
  ```

- [ ] **Never log or display passwords**
  ```python
  # ❌ BAD
  logger.info(f"User login: {email}, password: {password}")

  # ✅ GOOD
  logger.info(f"User login attempt: {email}")
  ```

- [ ] **Implement rate limiting on auth endpoints**
  ```python
  from slowapi import Limiter
  from slowapi.util import get_remote_address

  limiter = Limiter(key_func=get_remote_address)

  @app.post("/api/auth/sign-in/email")
  @limiter.limit("5/minute")  # 5 attempts per minute
  async def login(request: Request, ...):
      pass
  ```

### Token Security

- [ ] **Use appropriate token expiration**
  ```python
  # Access tokens: Short-lived
  ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour

  # Refresh tokens: Long-lived
  REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 days
  ```

- [ ] **Validate token signature**
  ```python
  try:
      payload = jwt.decode(
          token,
          settings.better_auth_secret,
          algorithms=["HS256"]  # Specify algorithm
      )
  except jwt.InvalidTokenError:
      raise HTTPException(status_code=401)
  ```

- [ ] **Check token expiration**
  ```python
  current_time = datetime.utcnow().timestamp()
  if payload.get("exp", 0) < current_time:
      raise HTTPException(
          status_code=401,
          detail="Token expired"
      )
  ```

- [ ] **Implement token revocation (optional)**
  ```python
  # Store revoked tokens in Redis/database
  revoked_tokens = set()

  def revoke_token(jti: str):
      """Revoke token by JWT ID."""
      revoked_tokens.add(jti)

  def is_token_revoked(jti: str) -> bool:
      """Check if token is revoked."""
      return jti in revoked_tokens
  ```

## Authorization Security

### User Isolation

- [ ] **Always verify user_id matches token**
  ```python
  @router.get("/api/{user_id}/tasks")
  async def get_tasks(
      user_id: str,
      current_user: dict = Depends(verify_jwt_token)
  ):
      # Verify user_id matches authenticated user
      if current_user["sub"] != user_id:
          raise HTTPException(status_code=403, detail="Forbidden")

      return get_user_tasks(user_id)
  ```

- [ ] **Filter database queries by user_id**
  ```python
  # ❌ BAD: Returns all tasks
  tasks = session.exec(select(Task)).all()

  # ✅ GOOD: Returns only user's tasks
  tasks = session.exec(
      select(Task).where(Task.user_id == current_user["sub"])
  ).all()
  ```

- [ ] **Test user isolation**
  ```python
  def test_user_isolation():
      """Test users cannot access other users' data."""
      # Create two users
      user1_token = create_user_and_login("user1@example.com")
      user2_token = create_user_and_login("user2@example.com")

      # User 1 creates task
      task = create_task(user1_token, "User 1 task")

      # User 2 tries to access User 1's task
      response = get_task(user2_token, task.id)

      # Should return 403 Forbidden
      assert response.status_code == 403
  ```

### Input Validation

- [ ] **Validate all user inputs**
  ```python
  from pydantic import BaseModel, EmailStr, validator

  class UserCreate(BaseModel):
      email: EmailStr  # Validates email format
      password: str
      name: str

      @validator('password')
      def validate_password(cls, v):
          if len(v) < 8:
              raise ValueError('Password must be at least 8 characters')
          return v

      @validator('name')
      def validate_name(cls, v):
          if len(v) > 100:
              raise ValueError('Name too long')
          return v.strip()
  ```

- [ ] **Sanitize inputs to prevent injection**
  ```python
  import bleach

  def sanitize_input(text: str) -> str:
      """Remove potentially dangerous HTML/JavaScript."""
      return bleach.clean(text, strip=True)
  ```

- [ ] **Use parameterized queries**
  ```python
  # ✅ GOOD: SQLModel/SQLAlchemy uses parameterized queries
  tasks = session.exec(
      select(Task).where(Task.user_id == user_id)
  ).all()

  # ❌ BAD: String concatenation (SQL injection risk)
  query = f"SELECT * FROM tasks WHERE user_id = '{user_id}'"
  ```

## API Security

### CORS Configuration

- [ ] **Restrict allowed origins**
  ```python
  # ❌ BAD: Allow all origins
  allow_origins=["*"]

  # ✅ GOOD: Specific origins
  allow_origins=[
      "http://localhost:3000",  # Development
      "https://yourdomain.com"  # Production
  ]
  ```

- [ ] **Enable credentials for auth**
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:3000"],
      allow_credentials=True,  # Required for cookies/auth
      allow_methods=["GET", "POST", "PUT", "DELETE"],
      allow_headers=["*"],
  )
  ```

- [ ] **Use environment-specific CORS**
  ```python
  if settings.environment == "production":
      allowed_origins = ["https://yourdomain.com"]
  else:
      allowed_origins = ["http://localhost:3000"]
  ```

### Rate Limiting

- [ ] **Implement rate limiting**
  ```python
  from slowapi import Limiter

  limiter = Limiter(key_func=get_remote_address)

  # Authentication endpoints: Strict limits
  @app.post("/api/auth/sign-in/email")
  @limiter.limit("5/minute")
  async def login(...):
      pass

  # API endpoints: Generous limits
  @app.get("/api/{user_id}/tasks")
  @limiter.limit("100/minute")
  async def get_tasks(...):
      pass
  ```

- [ ] **Return appropriate rate limit headers**
  ```python
  response.headers["X-RateLimit-Limit"] = "100"
  response.headers["X-RateLimit-Remaining"] = "95"
  response.headers["X-RateLimit-Reset"] = "1640000000"
  ```

### Error Handling

- [ ] **Return generic error messages**
  ```python
  # ❌ BAD: Reveals too much information
  raise HTTPException(
      status_code=401,
      detail="User 'john@example.com' not found in database"
  )

  # ✅ GOOD: Generic message
  raise HTTPException(
      status_code=401,
      detail="Invalid credentials"
  )
  ```

- [ ] **Log detailed errors server-side**
  ```python
  try:
      user = authenticate_user(email, password)
  except Exception as e:
      # Log detailed error
      logger.error(f"Authentication failed for {email}: {str(e)}")

      # Return generic error to user
      raise HTTPException(
          status_code=401,
          detail="Invalid credentials"
      )
  ```

- [ ] **Don't expose stack traces**
  ```python
  # Production: Disable debug mode
  app = FastAPI(debug=False)

  # Custom exception handler
  @app.exception_handler(Exception)
  async def generic_exception_handler(request, exc):
      logger.error(f"Unhandled exception: {exc}")
      return JSONResponse(
          status_code=500,
          content={"detail": "Internal server error"}
      )
  ```

## Database Security

### Connection Security

- [ ] **Use SSL for database connections**
  ```python
  DATABASE_URL = "postgresql://user:pass@host:5432/db?sslmode=require"
  ```

- [ ] **Store database credentials securely**
  ```python
  # ✅ GOOD: Environment variables
  DATABASE_URL = os.getenv("DATABASE_URL")

  # ❌ BAD: Hardcoded credentials
  DATABASE_URL = "postgresql://admin:password123@localhost/db"
  ```

- [ ] **Use connection pooling**
  ```python
  engine = create_engine(
      settings.database_url,
      pool_size=10,
      max_overflow=20,
      pool_pre_ping=True  # Verify connections
  )
  ```

### Data Protection

- [ ] **Encrypt sensitive data at rest**
  ```python
  from cryptography.fernet import Fernet

  def encrypt_sensitive_data(data: str, key: bytes) -> str:
      """Encrypt sensitive data before storing."""
      f = Fernet(key)
      return f.encrypt(data.encode()).decode()
  ```

- [ ] **Use database-level encryption**
  ```sql
  -- PostgreSQL: Enable encryption
  ALTER TABLE users ALTER COLUMN ssn TYPE bytea
  USING pgp_sym_encrypt(ssn, 'encryption-key');
  ```

- [ ] **Implement audit logging**
  ```python
  class AuditLog(SQLModel, table=True):
      id: int = Field(primary_key=True)
      user_id: str
      action: str
      resource: str
      timestamp: datetime = Field(default_factory=datetime.utcnow)
      ip_address: str

  def log_action(user_id: str, action: str, resource: str, ip: str):
      """Log user actions for audit trail."""
      log = AuditLog(
          user_id=user_id,
          action=action,
          resource=resource,
          ip_address=ip
      )
      session.add(log)
      session.commit()
  ```

## Frontend Security

### XSS Prevention

- [ ] **Sanitize user-generated content**
  ```typescript
  import DOMPurify from 'dompurify'

  function sanitizeHTML(dirty: string): string {
    return DOMPurify.sanitize(dirty)
  }

  // Use in React
  <div dangerouslySetInnerHTML={{ __html: sanitizeHTML(userContent) }} />
  ```

- [ ] **Use React's built-in XSS protection**
  ```typescript
  // ✅ GOOD: React escapes by default
  <div>{userInput}</div>

  // ❌ BAD: Bypasses protection
  <div dangerouslySetInnerHTML={{ __html: userInput }} />
  ```

### CSRF Prevention

- [ ] **Use SameSite cookies**
  ```python
  response.set_cookie(
      key="auth-token",
      value=token,
      samesite="lax"  # or "strict"
  )
  ```

- [ ] **Implement CSRF tokens (if using cookies)**
  ```python
  from fastapi_csrf_protect import CsrfProtect

  @app.post("/api/tasks")
  async def create_task(
      csrf_protect: CsrfProtect = Depends()
  ):
      await csrf_protect.validate_csrf(request)
      # Process request
  ```

### Token Storage

- [ ] **Choose appropriate storage method**
  ```typescript
  // Option 1: localStorage (vulnerable to XSS)
  localStorage.setItem('auth-token', token)

  // Option 2: httpOnly cookies (more secure)
  // Set by backend, automatically sent with requests

  // Option 3: sessionStorage (cleared on tab close)
  sessionStorage.setItem('auth-token', token)
  ```

- [ ] **Clear tokens on logout**
  ```typescript
  function logout() {
    // Clear all auth data
    localStorage.removeItem('auth-token')
    localStorage.removeItem('refresh-token')
    localStorage.removeItem('user')

    // Redirect to login
    router.push('/login')
  }
  ```

## Monitoring and Logging

### Security Logging

- [ ] **Log authentication events**
  ```python
  logger.info(f"Login attempt: {email} from {ip_address}")
  logger.info(f"Login success: {user_id}")
  logger.warning(f"Login failed: {email} - invalid password")
  logger.warning(f"Login failed: {email} - account locked")
  ```

- [ ] **Log authorization failures**
  ```python
  logger.warning(
      f"Unauthorized access attempt: "
      f"user={current_user['sub']} "
      f"resource={resource_id} "
      f"action={action}"
  )
  ```

- [ ] **Monitor for suspicious activity**
  ```python
  # Track failed login attempts
  failed_attempts = {}

  def check_failed_attempts(email: str) -> bool:
      """Check if account should be locked."""
      attempts = failed_attempts.get(email, 0)
      if attempts >= 5:
          logger.warning(f"Account locked: {email}")
          return True
      return False
  ```

### Security Alerts

- [ ] **Set up alerts for security events**
  - Multiple failed login attempts
  - Unusual access patterns
  - Token validation failures
  - Database connection errors
  - Rate limit violations

- [ ] **Implement security dashboards**
  - Failed authentication rate
  - Active sessions count
  - API error rates
  - Suspicious IP addresses

## Compliance

### GDPR Compliance

- [ ] **Implement data deletion**
  ```python
  @router.delete("/api/users/{user_id}")
  async def delete_user_data(
      user_id: str,
      current_user: dict = Depends(verify_jwt_token)
  ):
      """Delete all user data (GDPR right to erasure)."""
      # Verify user is deleting their own data
      if current_user["sub"] != user_id:
          raise HTTPException(status_code=403)

      # Delete user data
      delete_user_tasks(user_id)
      delete_user_account(user_id)

      return {"message": "User data deleted"}
  ```

- [ ] **Implement data export**
  ```python
  @router.get("/api/users/{user_id}/export")
  async def export_user_data(
      user_id: str,
      current_user: dict = Depends(verify_jwt_token)
  ):
      """Export all user data (GDPR right to data portability)."""
      if current_user["sub"] != user_id:
          raise HTTPException(status_code=403)

      user_data = get_all_user_data(user_id)
      return JSONResponse(content=user_data)
  ```

### Security Audit Trail

- [ ] **Maintain audit logs**
  - User authentication events
  - Data access and modifications
  - Permission changes
  - Security configuration changes

- [ ] **Retain logs appropriately**
  - Security logs: 1 year minimum
  - Audit logs: Per compliance requirements
  - Error logs: 90 days minimum

## Security Testing

### Penetration Testing

- [ ] **Test for common vulnerabilities**
  - SQL injection
  - XSS attacks
  - CSRF attacks
  - Authentication bypass
  - Authorization bypass
  - Token manipulation

- [ ] **Use security scanning tools**
  ```bash
  # OWASP ZAP
  zap-cli quick-scan http://localhost:8000

  # Bandit (Python security linter)
  bandit -r src/

  # npm audit (Node.js dependencies)
  npm audit
  ```

### Security Review Checklist

- [ ] All secrets in environment variables
- [ ] HTTPS enforced in production
- [ ] Strong password hashing (bcrypt/argon2)
- [ ] JWT tokens properly signed and verified
- [ ] Token expiration implemented
- [ ] User isolation enforced
- [ ] CORS properly configured
- [ ] Rate limiting on auth endpoints
- [ ] Input validation on all endpoints
- [ ] Error messages don't leak information
- [ ] Security headers configured
- [ ] Database connections encrypted
- [ ] Audit logging implemented
- [ ] Security monitoring in place
- [ ] Regular security updates applied
