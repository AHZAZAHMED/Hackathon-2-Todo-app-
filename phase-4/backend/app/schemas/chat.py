"""
Pydantic schemas for chat API request/response.
"""

from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """
    Request schema for POST /api/chat endpoint.

    Fields:
    - message: User's message (required, 1-2000 characters)
    - conversation_id: Optional UUID of existing conversation
    """
    message: str = Field(min_length=1, max_length=2000, description="User's message to the AI assistant")
    conversation_id: Optional[UUID] = Field(default=None, description="Existing conversation ID (omit for new conversation)")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello! Can you help me with my tasks?",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class ChatResponse(BaseModel):
    """
    Response schema for POST /api/chat endpoint.

    Fields:
    - conversation_id: UUID of the conversation (new or existing)
    - response: AI assistant's response message
    - timestamp: When the response was generated
    """
    conversation_id: UUID = Field(description="Conversation ID")
    response: str = Field(description="AI assistant's response")
    timestamp: datetime = Field(description="Response timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "response": "Hello! I'd be happy to help you with your tasks. What would you like to do?",
                "timestamp": "2026-02-09T10:00:00Z"
            }
        }
