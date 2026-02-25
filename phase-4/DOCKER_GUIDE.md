# Docker Deployment Guide

## Built Images

Successfully built Docker images for the Hackathon Phase-4 application:

- **Backend**: `hackathon-backend:latest` (701MB, compressed: 169MB)
- **Frontend**: `hackathon-frontend:latest` (523MB, compressed: 132MB)

## Image Details

### Backend Image (FastAPI + AI Chatbot)
- **Base**: Python 3.11 slim
- **Port**: 8000
- **Features**:
  - FastAPI REST API
  - OpenAI Agents SDK integration
  - MCP server for task tools
  - PostgreSQL connection via SQLModel
  - JWT authentication
  - Health check endpoint

### Frontend Image (Next.js 16)
- **Base**: Node 20 Alpine
- **Port**: 3000
- **Features**:
  - Next.js 16 with App Router
  - Better Auth authentication
  - OpenAI ChatKit UI
  - Prisma Client (generated)
  - Standalone output for optimized deployment

## Running the Images

### 1. Backend Container

```bash
docker run -d \
  --name hackathon-backend \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:password@host:5432/database" \
  -e BETTER_AUTH_SECRET="your-secret-key-here" \
  -e FRONTEND_URL="http://localhost:3000" \
  -e OPENROUTER_API_KEY="your-openrouter-api-key" \
  -e AI_MODEL="google/gemini-pro" \
  -e HOST="0.0.0.0" \
  -e PORT="8000" \
  hackathon-backend:latest
```

**Required Environment Variables:**
- `DATABASE_URL`: PostgreSQL connection string
- `BETTER_AUTH_SECRET`: Secret key for JWT verification (must match frontend)
- `FRONTEND_URL`: Frontend URL for CORS
- `OPENROUTER_API_KEY`: API key for AI chatbot functionality
- `AI_MODEL`: AI model to use (default: google/gemini-pro)

### 2. Frontend Container

```bash
docker run -d \
  --name hackathon-frontend \
  -p 3000:3000 \
  -e BETTER_AUTH_SECRET="your-secret-key-here" \
  -e BETTER_AUTH_URL="http://localhost:3000" \
  -e DATABASE_URL="postgresql://user:password@host:5432/database" \
  -e NEXT_PUBLIC_API_URL="http://localhost:8000" \
  -e NEXT_PUBLIC_APP_NAME="Todo App" \
  -e NEXT_PUBLIC_APP_URL="http://localhost:3000" \
  hackathon-frontend:latest
```

**Required Environment Variables:**
- `BETTER_AUTH_SECRET`: Secret key for JWT (must match backend)
- `BETTER_AUTH_URL`: Frontend URL for Better Auth
- `DATABASE_URL`: PostgreSQL connection string (for Better Auth)
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_APP_NAME`: Application name
- `NEXT_PUBLIC_APP_URL`: Frontend URL

## Using with PostgreSQL

### Option 1: External PostgreSQL (Recommended for Production)

Use a managed PostgreSQL service like:
- Neon (https://neon.tech)
- Supabase (https://supabase.com)
- AWS RDS
- Google Cloud SQL

### Option 2: PostgreSQL Container (Development)

```bash
# Run PostgreSQL container
docker run -d \
  --name hackathon-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=hackathon_phase4 \
  -p 5432:5432 \
  postgres:15-alpine

# Use this connection string in your containers:
# DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/hackathon_phase4
```

## Complete Setup Example

```bash
# 1. Start PostgreSQL
docker run -d \
  --name hackathon-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=hackathon_phase4 \
  -p 5432:5432 \
  postgres:15-alpine

# 2. Generate a secret key
SECRET=$(node -e "console.log(require('crypto').randomBytes(32).toString('hex'))")

# 3. Start Backend
docker run -d \
  --name hackathon-backend \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://postgres:postgres@host.docker.internal:5432/hackathon_phase4" \
  -e BETTER_AUTH_SECRET="$SECRET" \
  -e FRONTEND_URL="http://localhost:3000" \
  -e OPENROUTER_API_KEY="your-openrouter-api-key" \
  -e AI_MODEL="google/gemini-pro" \
  hackathon-backend:latest

# 4. Start Frontend
docker run -d \
  --name hackathon-frontend \
  -p 3000:3000 \
  -e BETTER_AUTH_SECRET="$SECRET" \
  -e BETTER_AUTH_URL="http://localhost:3000" \
  -e DATABASE_URL="postgresql://postgres:postgres@host.docker.internal:5432/hackathon_phase4" \
  -e NEXT_PUBLIC_API_URL="http://localhost:8000" \
  -e NEXT_PUBLIC_APP_NAME="Todo App" \
  -e NEXT_PUBLIC_APP_URL="http://localhost:3000" \
  hackathon-frontend:latest
```

## Health Checks

### Backend Health Check
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "todo-api-with-ai-chat",
  "version": "2.0.0"
}
```

### Frontend Health Check
The frontend includes a built-in health check that runs every 30 seconds.

## Stopping and Removing Containers

```bash
# Stop containers
docker stop hackathon-frontend hackathon-backend hackathon-postgres

# Remove containers
docker rm hackathon-frontend hackathon-backend hackathon-postgres

# Remove images (if needed)
docker rmi hackathon-frontend:latest hackathon-backend:latest
```

## Viewing Logs

```bash
# Backend logs
docker logs -f hackathon-backend

# Frontend logs
docker logs -f hackathon-frontend

# PostgreSQL logs
docker logs -f hackathon-postgres
```

## Pushing to Registry (Optional)

### Docker Hub
```bash
# Tag images
docker tag hackathon-backend:latest yourusername/hackathon-backend:latest
docker tag hackathon-frontend:latest yourusername/hackathon-frontend:latest

# Push images
docker push yourusername/hackathon-backend:latest
docker push yourusername/hackathon-frontend:latest
```

### Private Registry
```bash
# Tag images
docker tag hackathon-backend:latest registry.example.com/hackathon-backend:latest
docker tag hackathon-frontend:latest registry.example.com/hackathon-frontend:latest

# Push images
docker push registry.example.com/hackathon-backend:latest
docker push registry.example.com/hackathon-frontend:latest
```

## Production Deployment

For production deployment, consider:

1. **Use environment-specific tags**: `v1.0.0`, `production`, etc.
2. **Use secrets management**: AWS Secrets Manager, HashiCorp Vault, etc.
3. **Set up reverse proxy**: Nginx, Traefik, or cloud load balancer
4. **Enable HTTPS**: Use Let's Encrypt or cloud SSL certificates
5. **Configure monitoring**: Prometheus, Grafana, or cloud monitoring
6. **Set up logging**: ELK stack, CloudWatch, or similar
7. **Use orchestration**: Kubernetes, Docker Swarm, or ECS

## Troubleshooting

### Backend won't start
- Check DATABASE_URL is correct
- Verify BETTER_AUTH_SECRET is set
- Check OPENROUTER_API_KEY is valid
- View logs: `docker logs hackathon-backend`

### Frontend won't start
- Check BETTER_AUTH_SECRET matches backend
- Verify DATABASE_URL is correct
- Check NEXT_PUBLIC_API_URL points to backend
- View logs: `docker logs hackathon-frontend`

### Database connection issues
- Ensure PostgreSQL is running
- Check connection string format
- Verify network connectivity
- Use `host.docker.internal` for localhost on Mac/Windows

### CORS errors
- Verify FRONTEND_URL in backend matches actual frontend URL
- Check NEXT_PUBLIC_API_URL in frontend is correct
- Ensure no trailing slashes in URLs

## Files Created

- `backend/Dockerfile` - Backend Docker configuration
- `backend/.dockerignore` - Backend Docker ignore rules
- `frontend/Dockerfile` - Frontend Docker configuration (multi-stage)
- `frontend/.dockerignore` - Frontend Docker ignore rules

## Next Steps

1. Test the containers locally
2. Set up CI/CD pipeline for automated builds
3. Deploy to cloud platform (AWS, GCP, Azure, etc.)
4. Configure domain and SSL certificates
5. Set up monitoring and alerting
6. Configure backup strategy for database
