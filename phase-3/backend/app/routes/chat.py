"""
Chat API routes for conversational AI functionality.
Implements POST /api/chat endpoint for sending messages and receiving AI responses.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import logging
import json
import hashlib

from app.auth.dependencies import get_current_user
from app.database import engine
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_agent import ai_agent


router = APIRouter(prefix="/api/chat", tags=["chat"])

# Configure structured logging
logger = logging.getLogger(__name__)


def log_structured(level: str, request_id: str, user_id: str, event: str, **kwargs):
    """
    Log structured JSON messages per spec FR-015.

    Args:
        level: Log level (info, warning, error)
        request_id: Unique request identifier
        user_id: User ID (will be hashed for privacy)
        event: Event description
        **kwargs: Additional context fields
    """
    # Hash user_id for privacy (per spec FR-015)
    hashed_user_id = hashlib.sha256(user_id.encode()).hexdigest()[:16]

    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id,
        "user_id_hash": hashed_user_id,
        "endpoint": "/api/chat",
        "event": event,
        **kwargs
    }

    log_message = json.dumps(log_data)

    if level == "info":
        logger.info(log_message)
    elif level == "warning":
        logger.warning(log_message)
    elif level == "error":
        logger.error(log_message)
    else:
        logger.debug(log_message)


@router.post("/", response_model=ChatResponse, status_code=200)
async def send_chat_message(
    chat_data: ChatRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Send a message to the AI assistant and receive a response.

    This endpoint:
    1. Verifies JWT authentication
    2. Creates or loads conversation
    3. Stores user message
    4. Generates AI response
    5. Stores assistant message
    6. Returns response with conversation_id

    Args:
        chat_data: ChatRequest with message and optional conversation_id
        user: Authenticated user from JWT (injected by dependency)

    Returns:
        ChatResponse with conversation_id, response, and timestamp

    Raises:
        401: Missing or invalid JWT token
        422: Invalid request data (empty message, too long, etc.)
        500: Database error
        503: AI service unavailable
    """
    # Generate unique request ID for tracing
    request_id = str(uuid4())

    try:
        # Extract user_id from JWT claims (NEVER from request body)
        user_id = user["user_id"]

        # Log request start
        log_structured(
            "info",
            request_id,
            user_id,
            "chat_request_received",
            conversation_id=str(chat_data.conversation_id) if chat_data.conversation_id else None,
            message_length=len(chat_data.message)
        )

        # Validate message (strip whitespace)
        message_content = chat_data.message.strip()
        if not message_content:
            log_structured(
                "warning",
                request_id,
                user_id,
                "validation_error",
                error_type="empty_message"
            )
            raise HTTPException(
                status_code=422,
                detail={"code": "VALIDATION_ERROR", "message": "Message cannot be empty"}
            )

        # Get or create conversation
        conversation_id = chat_data.conversation_id
        conversation = None

        with Session(engine) as session:
            # Begin explicit transaction with Read Committed isolation
            session.begin()

            try:
                if conversation_id:
                    # Try to load existing conversation with row lock (SELECT FOR UPDATE)
                    statement = (
                        select(Conversation)
                        .where(
                            Conversation.id == conversation_id,
                            Conversation.user_id == user_id
                        )
                        .with_for_update()  # Row-level lock for concurrent safety
                    )
                    conversation = session.exec(statement).first()

                    # If conversation doesn't exist or doesn't belong to user,
                    # create new conversation (forgiving approach per spec)
                    if not conversation:
                        log_structured(
                            "info",
                            request_id,
                            user_id,
                            "conversation_created",
                            reason="conversation_not_found_or_unauthorized"
                        )
                        conversation = Conversation(user_id=user_id)
                        session.add(conversation)
                        session.flush()  # Get ID without committing
                    else:
                        log_structured(
                            "info",
                            request_id,
                            user_id,
                            "conversation_loaded",
                            conversation_id=str(conversation.id)
                        )
                else:
                    # Create new conversation
                    log_structured(
                        "info",
                        request_id,
                        user_id,
                        "conversation_created",
                        reason="new_conversation"
                    )
                    conversation = Conversation(user_id=user_id)
                    session.add(conversation)
                    session.flush()  # Get ID without committing

                # Store user message
                user_message = Message(
                    conversation_id=conversation.id,
                    role=MessageRole.USER,
                    content=message_content
                )
                session.add(user_message)
                session.flush()  # Persist user message before AI call

                # Load conversation history (last 50 messages, oldest first)
                statement = (
                    select(Message)
                    .where(Message.conversation_id == conversation.id)
                    .order_by(Message.created_at.asc())
                    .limit(50)
                )
                messages = session.exec(statement).all()

                # Build message array for AI (exclude the just-added user message from history)
                conversation_history = []
                for msg in messages:
                    if msg.id != user_message.id:  # Exclude the current message
                        conversation_history.append({
                            "role": msg.role.value,
                            "content": msg.content
                        })

                # Add current user message
                conversation_history.append({
                    "role": "user",
                    "content": message_content
                })

                # Generate AI response
                try:
                    log_structured(
                        "info",
                        request_id,
                        user_id,
                        "ai_request_started",
                        conversation_id=str(conversation.id),
                        history_length=len(conversation_history)
                    )
                    ai_response = await ai_agent.generate_response(conversation_history, user_id, request_id)
                except Exception as e:
                    # Rollback transaction on AI service failure
                    session.rollback()
                    log_structured(
                        "error",
                        request_id,
                        user_id,
                        "ai_service_error",
                        error_type="SERVICE_UNAVAILABLE",
                        error_message=str(e)
                    )
                    raise HTTPException(
                        status_code=503,
                        detail={"code": "SERVICE_UNAVAILABLE", "message": "AI service is temporarily unavailable"}
                    )

                # Store assistant message
                assistant_message = Message(
                    conversation_id=conversation.id,
                    role=MessageRole.ASSISTANT,
                    content=ai_response
                )
                session.add(assistant_message)

                # Commit entire transaction (conversation + user message + assistant message)
                session.commit()

                # Log successful response
                log_structured(
                    "info",
                    request_id,
                    user_id,
                    "chat_response_success",
                    conversation_id=str(conversation.id),
                    response_length=len(ai_response)
                )

                # Return response
                return ChatResponse(
                    conversation_id=conversation.id,
                    response=ai_response,
                    timestamp=datetime.utcnow()
                )

            except HTTPException:
                # Rollback on HTTP exceptions and re-raise
                session.rollback()
                raise
            except Exception as e:
                # Rollback on unexpected errors
                session.rollback()
                log_structured(
                    "error",
                    request_id,
                    user_id,
                    "database_error",
                    error_type="DATABASE_ERROR",
                    error_message=str(e)
                )
                raise

    except HTTPException:
        # Re-raise HTTP exceptions (401, 422, 503)
        raise
    except Exception as e:
        # Log unexpected errors and return 500
        log_structured(
            "error",
            request_id if 'request_id' in locals() else "unknown",
            user.get("user_id", "unknown") if 'user' in locals() else "unknown",
            "internal_error",
            error_type="INTERNAL_ERROR",
            error_message=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail={"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}
        )
