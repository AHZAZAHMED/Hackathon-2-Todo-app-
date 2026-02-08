"""Timeout middleware for chat endpoint."""
import asyncio
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable


class TimeoutMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce 5 second timeout for /api/chat endpoint.

    Prevents long-running requests from blocking the server.
    Returns 504 Gateway Timeout if request exceeds timeout.
    """

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process request with timeout enforcement.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler

        Returns:
            Response from handler or 504 timeout error
        """
        # Only apply timeout to chat endpoint
        if request.url.path == "/api/chat":
            try:
                # 5 second timeout for chat requests
                response = await asyncio.wait_for(
                    call_next(request),
                    timeout=5.0
                )
                return response
            except asyncio.TimeoutError:
                raise HTTPException(
                    status_code=504,
                    detail={
                        "error": "Request took too long to process. Please try again with a simpler message."
                    }
                )
        else:
            # No timeout for other endpoints
            return await call_next(request)
