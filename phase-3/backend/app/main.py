"""
FastAPI application entry point.
Main application with CORS configuration and routes.
"""

import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from app.config import ALL_ALLOWED_ORIGINS
from app.auth.dependencies import get_current_user
from app.routes import tasks, chat

# Configure logging to output to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Initialize FastAPI application
app = FastAPI(
    title="Hackathon Phase-3 API",
    description="Todo Application with AI Chat Assistant - Better Auth + JWT + OpenAI",
    version="2.0.0",
)

# Configure CORS middleware
# Allow both development (localhost) and production URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALL_ALLOWED_ORIGINS,  # Use configured origins from environment
    allow_credentials=True,  # Required for JWT/cookies
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# Register routers
app.include_router(tasks.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    """
    Health check endpoint.
    Returns API status and version information.
    """
    return {
        "status": "ok",
        "message": "Hackathon Phase-3 API - Todo App with AI Chat",
        "version": "2.0.0"
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
        "service": "todo-api-with-ai-chat",
        "version": "2.0.0"
    }


# Application startup event
@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    Runs when the application starts.
    """
    print("[INFO] Hackathon Phase-3 API starting...")
    print(f"[INFO] CORS enabled for origins: {', '.join(ALL_ALLOWED_ORIGINS)}")
    print("[INFO] Task CRUD endpoints registered at /api/tasks")
    print("[INFO] Chat endpoint registered at /api/chat")
    print("[SUCCESS] Application ready")


# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    Runs when the application shuts down.
    """
    print("[INFO] Hackathon Phase-3 API shutting down...")
