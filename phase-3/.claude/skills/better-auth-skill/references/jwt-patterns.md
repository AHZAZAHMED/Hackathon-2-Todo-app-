# JWT Patterns for Better Auth Integration

## JWT Token Structure

### Standard JWT Format

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Three parts separated by dots:
1. **Header** - Algorithm and token type
2. **Payload** - Claims (user data)
3. **Signature** - Verification signature

### Recommended Payload Structure

```json
{
  "sub": "user-uuid-here",           // Subject (user ID) - REQUIRED
  "email": "user@example.com",       // User email
  "name": "John Doe",                // User name (optional)
  "iat": 1516239022,                 // Issued at (timestamp)
  "exp": 1516242622,                 // Expiration (timestamp) - REQUIRED
  "jti": "token-unique-id"           // JWT ID (for revocation)
}
```

**Critical Claims:**
- `sub` - User identifier, used for authorization
- `exp` - Expiration time, prevents token reuse
- `iat` - Issued at time, for audit logging

## Token Generation (Backend)

### Python (FastAPI) Implementation

```python
import jwt
from datetime import datetime, timedelta
from typing import Dict

def generate_jwt_token(
    user_id: str,
    email: str,
    secret: str,
    expires_in_minutes: int = 60
) -> str:
    """Generate JWT token with user claims."""

    now = datetime.utcnow()
    expiration = now + timedelta(minutes=expires_in_minutes)

    payload = {
        "sub": user_id,              # User ID
        "email": email,              # User email
        "iat": int(now.timestamp()), # Issued at
        "exp": int(expiration.timestamp()),  # Expiration
        "jti": str(uuid.uuid4())     # Unique token ID
    }

    token = jwt.encode(
        payload,
        secret,
        algorithm="HS256"
    )

    return token
```

### Token Expiration Strategy

| Token Type | Expiration | Use Case |
|------------|------------|----------|
| Access Token | 15-60 minutes | API requests |
| Refresh Token | 7-30 days | Token renewal |
| Remember Me | 30-90 days | Long sessions |

## Token Verification (Backend)

### Python (FastAPI) Implementation

```python
from fastapi import HTTPException, Header
import jwt

async def verify_jwt_token(
    authorization: str = Header(None)
) -> Dict:
    """Verify JWT token and return payload."""

    # Check Authorization header exists
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    # Extract token from "Bearer <token>"
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme"
        )

    token = authorization.replace("Bearer ", "")

    try:
        # Verify and decode token
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"]
        )

        # Validate required claims
        if "sub" not in payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload"
            )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
```

## Token Storage (Frontend)

### localStorage Implementation

```typescript
// Store token
function storeToken(token: string): void {
  localStorage.setItem('auth-token', token)
}

// Retrieve token
function getToken(): string | null {
  return localStorage.getItem('auth-token')
}

// Remove token
function removeToken(): void {
  localStorage.removeItem('auth-token')
}

// Check if token is valid
function isTokenValid(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    const currentTime = Math.floor(Date.now() / 1000)
    return !payload.exp || payload.exp > currentTime
  } catch {
    return false
  }
}
```

### httpOnly Cookie Implementation (More Secure)

```typescript
// Backend sets cookie
response.set_cookie(
    key="auth-token",
    value=token,
    httponly=True,      # Prevents JavaScript access
    secure=True,        # HTTPS only
    samesite="lax",     # CSRF protection
    max_age=3600        # 1 hour
)

// Frontend automatically sends cookie with requests
// No manual token management needed
```

## Token Validation Patterns

### Frontend Token Validation

```typescript
interface TokenPayload {
  sub: string
  email: string
  exp: number
  iat: number
}

function decodeToken(token: string): TokenPayload | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload as TokenPayload
  } catch {
    return null
  }
}

function validateToken(token: string): boolean {
  const payload = decodeToken(token)
  if (!payload) return false

  // Check expiration
  const currentTime = Math.floor(Date.now() / 1000)
  if (payload.exp && payload.exp < currentTime) {
    return false
  }

  // Check required fields
  if (!payload.sub || !payload.email) {
    return false
  }

  return true
}
```

### Backend User Isolation Pattern

```python
from fastapi import Depends, HTTPException

async def verify_user_access(
    user_id: str,
    current_user: dict = Depends(verify_jwt_token)
) -> dict:
    """Verify user can access resource."""

    # Extract user ID from token
    token_user_id = current_user.get("sub")

    # Compare with requested user_id
    if token_user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden"
        )

    return current_user

# Usage in route
@router.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    current_user: dict = Depends(verify_user_access)
):
    # User is authorized to access this resource
    return get_user_tasks(user_id)
```

## Token Refresh Pattern

### Backend Refresh Endpoint

```python
@router.post("/api/auth/refresh")
async def refresh_token(
    refresh_token: str = Body(..., embed=True)
):
    """Generate new access token from refresh token."""

    try:
        # Verify refresh token
        payload = jwt.decode(
            refresh_token,
            settings.better_auth_secret,
            algorithms=["HS256"]
        )

        # Check token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type"
            )

        # Generate new access token
        new_token = generate_jwt_token(
            user_id=payload["sub"],
            email=payload["email"]
        )

        return {"token": new_token}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Refresh token expired"
        )
```

### Frontend Automatic Refresh

```typescript
async function makeAuthenticatedRequest(url: string, options: RequestInit = {}) {
  let token = getToken()

  // Check if token is about to expire (within 5 minutes)
  if (token && isTokenExpiringSoon(token, 300)) {
    // Refresh token
    const refreshToken = getRefreshToken()
    const response = await fetch('/api/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken })
    })

    if (response.ok) {
      const data = await response.json()
      storeToken(data.token)
      token = data.token
    }
  }

  // Make request with token
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  })
}

function isTokenExpiringSoon(token: string, seconds: number): boolean {
  const payload = decodeToken(token)
  if (!payload || !payload.exp) return false

  const currentTime = Math.floor(Date.now() / 1000)
  return payload.exp - currentTime < seconds
}
```

## Security Best Practices

### Token Signing Algorithm

```python
# ✅ GOOD: Use HS256 (HMAC with SHA-256)
jwt.encode(payload, secret, algorithm="HS256")

# ❌ BAD: Don't use "none" algorithm
jwt.encode(payload, secret, algorithm="none")  # Insecure!

# ❌ BAD: Don't use asymmetric algorithms without proper key management
jwt.encode(payload, secret, algorithm="RS256")  # Requires public/private keys
```

### Secret Key Requirements

```python
# ✅ GOOD: Strong random secret (32+ bytes)
import secrets
secret = secrets.token_hex(32)  # 64 character hex string

# ❌ BAD: Weak or predictable secret
secret = "my-secret-key"  # Too short, predictable

# ❌ BAD: Hardcoded secret
SECRET_KEY = "abc123"  # Never hardcode!
```

### Token Validation Checklist

- [ ] Verify signature with correct secret
- [ ] Check token expiration (exp claim)
- [ ] Validate required claims (sub, email)
- [ ] Verify token format (3 parts, base64)
- [ ] Check algorithm matches expected (HS256)
- [ ] Validate issuer if using multi-tenant (iss claim)
- [ ] Check audience if using multiple services (aud claim)

## Common JWT Errors

### Error: "Invalid token"

**Causes:**
- Token signature doesn't match
- BETTER_AUTH_SECRET mismatch between frontend/backend
- Token format is incorrect
- Token has been tampered with

**Solution:**
```python
# Verify secrets match
print(f"Backend secret: {settings.better_auth_secret[:10]}...")

# Check token format
parts = token.split('.')
print(f"Token parts: {len(parts)}")  # Should be 3
```

### Error: "Token expired"

**Causes:**
- Token expiration time has passed
- System clock skew between servers
- Token not refreshed before expiration

**Solution:**
```typescript
// Check token expiration
const payload = decodeToken(token)
const currentTime = Math.floor(Date.now() / 1000)
console.log(`Token expires at: ${new Date(payload.exp * 1000)}`)
console.log(`Current time: ${new Date(currentTime * 1000)}`)

// Implement token refresh before expiration
```

### Error: "Missing sub claim"

**Causes:**
- Token generated without user ID
- Token payload structure incorrect
- Old token format being used

**Solution:**
```python
# Always include sub claim
payload = {
    "sub": user_id,  # REQUIRED
    "email": email,
    "exp": expiration
}
```

## Testing JWT Implementation

### Unit Test Example

```python
import pytest
from datetime import datetime, timedelta

def test_generate_valid_token():
    """Test token generation with valid claims."""
    token = generate_jwt_token(
        user_id="test-user-123",
        email="test@example.com",
        secret="test-secret",
        expires_in_minutes=60
    )

    # Decode token
    payload = jwt.decode(token, "test-secret", algorithms=["HS256"])

    # Verify claims
    assert payload["sub"] == "test-user-123"
    assert payload["email"] == "test@example.com"
    assert "exp" in payload
    assert "iat" in payload

def test_verify_expired_token():
    """Test that expired tokens are rejected."""
    # Generate token that expires immediately
    token = generate_jwt_token(
        user_id="test-user",
        email="test@example.com",
        secret="test-secret",
        expires_in_minutes=-1  # Already expired
    )

    # Verify token fails
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(token, "test-secret", algorithms=["HS256"])
```

### Integration Test Example

```typescript
test('complete authentication flow with JWT', async () => {
  // 1. Register user
  const registerResponse = await fetch('/api/auth/sign-up/email', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      email: 'test@example.com',
      password: 'password123',
      name: 'Test User'
    })
  })

  const registerData = await registerResponse.json()
  expect(registerData.token).toBeDefined()

  // 2. Verify token structure
  const tokenParts = registerData.token.split('.')
  expect(tokenParts).toHaveLength(3)

  // 3. Decode and verify payload
  const payload = JSON.parse(atob(tokenParts[1]))
  expect(payload.sub).toBeDefined()
  expect(payload.email).toBe('test@example.com')
  expect(payload.exp).toBeGreaterThan(Date.now() / 1000)

  // 4. Use token for authenticated request
  const tasksResponse = await fetch(`/api/${payload.sub}/tasks`, {
    headers: {
      'Authorization': `Bearer ${registerData.token}`
    }
  })

  expect(tasksResponse.status).toBe(200)
})
```
