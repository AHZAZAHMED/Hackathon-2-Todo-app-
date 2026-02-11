"""
MCP Tools Utilities

This module provides shared utilities for MCP tool implementations:
- Response format helpers
- Input validation helpers
- Error handling utilities

All tools use these utilities to ensure consistent behavior and responses.
"""

from typing import Dict, Any, Optional


def success_response(
    task_id: int,
    status: str,
    title: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a standardized success response for MCP tools.

    Args:
        task_id: The task identifier
        status: Operation status (e.g., "created", "updated", "completed", "deleted")
        title: The task title
        **kwargs: Additional fields to include in response

    Returns:
        Dictionary with task_id, status, title, and any additional fields

    Example:
        >>> success_response(123, "created", "Buy groceries")
        {"task_id": 123, "status": "created", "title": "Buy groceries"}
    """
    response = {
        "task_id": task_id,
        "status": status,
        "title": title
    }
    response.update(kwargs)
    return response


def error_response(message: str) -> Dict[str, str]:
    """
    Create a standardized error response for MCP tools.

    Args:
        message: Human-readable error message

    Returns:
        Dictionary with error key

    Example:
        >>> error_response("user_id is required")
        {"error": "user_id is required"}
    """
    return {"error": message}


def validate_user_id(user_id: Optional[str]) -> Optional[Dict[str, str]]:
    """
    Validate that user_id is provided and not empty.

    Args:
        user_id: The user identifier to validate

    Returns:
        None if valid, error response dict if invalid

    Example:
        >>> validate_user_id(None)
        {"error": "user_id is required"}
        >>> validate_user_id("")
        {"error": "user_id is required"}
        >>> validate_user_id("user123")
        None
    """
    if not user_id:
        return error_response("user_id is required")

    if not user_id.strip():
        return error_response("user_id is required")

    return None


def validate_title(title: Optional[str], max_length: int = 500) -> Optional[Dict[str, str]]:
    """
    Validate task title.

    Args:
        title: The title to validate
        max_length: Maximum allowed length (default 500)

    Returns:
        None if valid, error response dict if invalid

    Example:
        >>> validate_title(None)
        {"error": "title is required"}
        >>> validate_title("   ")
        {"error": "title cannot be empty"}
        >>> validate_title("a" * 501)
        {"error": "title exceeds maximum length of 500 characters"}
        >>> validate_title("Valid title")
        None
    """
    if title is None:
        return error_response("title is required")

    title_stripped = title.strip()

    if not title_stripped:
        return error_response("title cannot be empty")

    if len(title) > max_length:
        return error_response(f"title exceeds maximum length of {max_length} characters")

    return None


def validate_task_id(task_id: Optional[int]) -> Optional[Dict[str, str]]:
    """
    Validate that task_id is provided.

    Args:
        task_id: The task identifier to validate

    Returns:
        None if valid, error response dict if invalid

    Example:
        >>> validate_task_id(None)
        {"error": "task_id is required"}
        >>> validate_task_id(123)
        None
    """
    if task_id is None:
        return error_response("task_id is required")

    return None


def validate_status(status: Optional[str]) -> Optional[Dict[str, str]]:
    """
    Validate status filter parameter for list_tasks.

    Args:
        status: The status filter value

    Returns:
        None if valid, error response dict if invalid

    Example:
        >>> validate_status("all")
        None
        >>> validate_status("pending")
        None
        >>> validate_status("completed")
        None
        >>> validate_status("invalid")
        {"error": "status must be 'all', 'pending', or 'completed'"}
    """
    if status is None:
        return None

    valid_statuses = ["all", "pending", "completed"]
    if status not in valid_statuses:
        return error_response("status must be 'all', 'pending', or 'completed'")

    return None


__all__ = [
    "success_response",
    "error_response",
    "validate_user_id",
    "validate_title",
    "validate_task_id",
    "validate_status",
]
