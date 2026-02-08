"""Pydantic schemas for chat API."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID


class ChatRequest(BaseModel):
    """Request schema for POST /api/chat endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's chat message (1-10,000 characters)"
    )

    conversation_id: Optional[UUID] = Field(
        None,
        description="Optional UUID of existing conversation. If omitted, backend auto-creates new conversation."
    )

    class Config:
        schema_extra = {
            "example": {
                "message": "Add a task to buy milk",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class ToolCall(BaseModel):
    """Schema for MCP tool invocation details."""

    tool: str = Field(
        ...,
        description="Name of MCP tool invoked (add_task, list_tasks, etc.)"
    )

    arguments: Dict[str, Any] = Field(
        ...,
        description="Arguments passed to the tool"
    )

    result: Any = Field(
        ...,
        description="Result returned by the tool"
    )

    class Config:
        schema_extra = {
            "example": {
                "tool": "add_task",
                "arguments": {
                    "title": "Buy milk",
                    "description": ""
                },
                "result": {
                    "id": 123,
                    "title": "Buy milk",
                    "completed": False
                }
            }
        }


class ChatResponse(BaseModel):
    """Response schema for POST /api/chat endpoint."""

    conversation_id: UUID = Field(
        ...,
        description="UUID of conversation (newly created or existing)"
    )

    response: str = Field(
        ...,
        description="AI agent's response message"
    )

    tool_calls: List[ToolCall] = Field(
        default_factory=list,
        description="List of MCP tools invoked during request (empty if no tools used)"
    )

    class Config:
        schema_extra = {
            "example": {
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "response": "I've added a task to buy milk to your todo list.",
                "tool_calls": [
                    {
                        "tool": "add_task",
                        "arguments": {
                            "title": "Buy milk",
                            "description": ""
                        },
                        "result": {
                            "id": 123,
                            "title": "Buy milk",
                            "completed": False
                        }
                    }
                ]
            }
        }
