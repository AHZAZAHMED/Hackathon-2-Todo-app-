"""
FastAPI application entry point.
Main application with CORS configuration and routes.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from app.config import FRONTEND_URL
from app.auth.dependencies import get_current_user
from app.routes import tasks

# Initialize FastAPI application
app = FastAPI(
    title="Hackathon Phase-2 API",
    description="Authentication system with Better Auth + JWT for Todo Application",
    version="1.0.0",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # Explicit frontend origin whitelist
    allow_credentials=True,  # Required for cookies
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Register routers
app.include_router(tasks.router)


@app.get("/")
async def root():
    """
    Health check endpoint.
    Returns API status and version information.
    """
    return {
        "status": "ok",
        "message": "Hackathon Phase-2 API",
        "version": "1.0.0"
    }


@app.get("/api/protected")
async def protected_route(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Example protected endpoint that requires authentication.

    This endpoint demonstrates how to use the get_current_user dependency
    to protect routes and access authenticated user information.

    Args:
        user: Authenticated user claims from JWT token

    Returns:
        Dict with welcome message and user information
    """
    return {
        "message": "This is a protected route",
        "user": {
            "user_id": user["user_id"],
            "email": user["email"],
            "name": user["name"]
        }
    }


@app.get("/api/health")
async def health_check():
    """
    Detailed health check endpoint.
    Can be extended to check database connectivity, etc.
    """
    return {
        "status": "healthy",
        "service": "authentication-api",
        "version": "1.0.0"
    }


# Application startup event
@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    Runs when the application starts.
    """
    print("[INFO] Hackathon Phase-2 API starting...")
    print(f"[INFO] CORS enabled for: {FRONTEND_URL}")
    print("[INFO] Task CRUD endpoints registered at /api/tasks")
    print("[SUCCESS] Application ready")


# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    Runs when the application shuts down.
    """
    print("[INFO] Hackathon Phase-2 API shutting down...")
