# Backend API - Hackathon Phase-2 Authentication System

FastAPI backend with JWT verification for the Todo Application authentication system.

## Tech Stack

- **Framework**: FastAPI 0.109.0
- **Authentication**: JWT verification (Better Auth tokens)
- **Database**: PostgreSQL (Neon Serverless)
- **ORM**: SQLModel 0.0.14
- **Python**: 3.11+

## Features

- ✅ JWT token verification with Better Auth integration
- ✅ User authentication middleware
- ✅ Rate limiting (5 failed attempts per email per 15 minutes)
- ✅ CORS configuration for frontend
- ✅ Protected API endpoints
- ✅ Database-backed persistence

## Prerequisites

- Python 3.11 or higher
- PostgreSQL database (Neon Serverless or local)
- BETTER_AUTH_SECRET (must match frontend)

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
# JWT Verification (MUST match frontend BETTER_AUTH_SECRET)
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long

# Database (Neon Serverless or local PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/database

# CORS (Frontend URL)
FRONTEND_URL=http://localhost:3000

# Server
HOST=0.0.0.0
PORT=8000
```

**Important**: Use the SAME `BETTER_AUTH_SECRET` as the frontend.

### 4. Run Database Migrations

```bash
# Connect to your PostgreSQL database and run:
psql "your-database-url" -f migrations/001_create_auth_tables.sql
```

Or use your preferred migration tool.

### 5. Start Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check

```
GET /
GET /api/health
```

Returns API status and version.

### Protected Endpoint (Example)

```
GET /api/protected
Authorization: Bearer <jwt_token>
```

Returns authenticated user information.

**Response**:
```json
{
  "message": "This is a protected route",
  "user": {
    "user_id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

## Authentication Flow

1. **User signs up/logs in** on frontend (Better Auth)
2. **Better Auth issues JWT token** stored in httpOnly cookie
3. **Frontend attaches JWT** to API requests in Authorization header
4. **Backend verifies JWT signature** using BETTER_AUTH_SECRET
5. **Backend extracts user_id** from JWT claims
6. **Backend uses user_id** for all database queries

## JWT Token Structure

**Claims**:
- `user_id`: Primary user identifier
- `email`: User email address
- `name`: User display name
- `exp`: Expiration timestamp (24 hours)
- `iat`: Issued-at timestamp

**Algorithm**: HS256 (HMAC with SHA-256)

## Rate Limiting

- **Limit**: 5 failed login attempts per email per 15 minutes
- **Storage**: PostgreSQL `rate_limits` table
- **Response**: 429 Too Many Requests with retry time

## Error Responses

### 401 Unauthorized

```json
{
  "detail": {
    "error": {
      "code": "TOKEN_EXPIRED",
      "message": "Token has expired. Please log in again."
    }
  }
}
```

**Error Codes**:
- `TOKEN_EXPIRED`: JWT token has expired
- `INVALID_TOKEN`: JWT signature invalid or malformed
- `MISSING_TOKEN`: No Authorization header provided

### 429 Too Many Requests

```json
{
  "detail": {
    "error": {
      "code": "RATE_LIMIT_EXCEEDED",
      "message": "Too many failed login attempts. Please try again in 10 minutes.",
      "retryAfter": 600
    }
  }
}
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Environment configuration
│   ├── database.py          # Database connection
│   ├── auth/                # Authentication module
│   │   ├── __init__.py
│   │   ├── middleware.py    # JWT verification middleware
│   │   ├── dependencies.py  # FastAPI dependencies
│   │   └── utils.py         # JWT utilities
│   ├── models/              # SQLModel schemas
│   │   ├── __init__.py
│   │   ├── user.py          # User model
│   │   └── rate_limit.py    # Rate limit model
│   └── routes/              # API routes
│       ├── __init__.py
│       └── rate_limit.py    # Rate limiting logic
├── migrations/              # Database migrations
│   └── 001_create_auth_tables.sql
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

## Development

### Run with Auto-Reload

```bash
uvicorn app.main:app --reload
```

### View API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Testing Protected Endpoints

1. Get JWT token from frontend (login/signup)
2. Copy token from browser DevTools → Application → Cookies
3. Use token in Authorization header:

```bash
curl -X GET http://localhost:8000/api/protected \
  -H "Authorization: Bearer <your-jwt-token>"
```

## Security

- ✅ JWT tokens verified on every request
- ✅ Passwords hashed with bcrypt (managed by Better Auth)
- ✅ Rate limiting prevents brute-force attacks
- ✅ CORS configured for specific frontend origin
- ✅ httpOnly cookies prevent XSS attacks
- ✅ Stateless backend (horizontally scalable)

## Troubleshooting

### "BETTER_AUTH_SECRET is not set"

**Solution**: Create `.env` file with `BETTER_AUTH_SECRET` matching frontend.

### "Database connection failed"

**Solution**: Verify `DATABASE_URL` is correct and database is accessible.

### "401 Unauthorized" on all requests

**Solution**: Verify `BETTER_AUTH_SECRET` is identical in frontend and backend.

### CORS errors

**Solution**: Verify `FRONTEND_URL` in `.env` matches frontend URL exactly.

## Production Deployment

1. Set `BETTER_AUTH_SECRET` to a cryptographically secure value (32+ characters)
2. Use production PostgreSQL database URL
3. Set `FRONTEND_URL` to production frontend domain
4. Use HTTPS for all requests
5. Consider using a process manager (e.g., gunicorn, supervisor)

```bash
# Production server with gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## License

Hackathon II Phase-2 Project
