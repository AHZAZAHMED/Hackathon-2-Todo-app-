"""
FastAPI dependencies for authentication.
Provides reusable dependencies for protected routes.
"""

from fastapi import Depends
from typing import Dict, Any
from app.auth.middleware import verify_jwt


def get_current_user(user: Dict[str, Any] = Depends(verify_jwt)) -> Dict[str, Any]:
    """
    FastAPI dependency to get the current authenticated user.

    This dependency can be used in route handlers to ensure the user is authenticated
    and to access user information extracted from the JWT token.

    Usage:
        @app.get("/api/protected")
        async def protected_route(user: Dict = Depends(get_current_user)):
            user_id = user["user_id"]
            email = user["email"]
            name = user["name"]
            return {"message": f"Hello, {name}!"}

    Args:
        user: User claims from JWT token (injected by verify_jwt dependency)

    Returns:
        Dict containing user_id, email, and name
    """
    return user
