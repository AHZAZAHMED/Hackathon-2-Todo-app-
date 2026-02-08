"""Chat API endpoint for conversational task management."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Dict, Any
from app.auth.dependencies import get_current_user
from app.database import get_session
from app.schemas.chat import ChatRequest, ChatResponse, ToolCall
from app.services.conversation_service import get_or_create_conversation
from app.services.message_service import store_message, load_conversation_history
from app.models.message import MessageRole
from app.ai.agent import invoke_agent
from app.mcp.server import get_tool_definitions
from app.exceptions import GeminiAPIError, MCPToolError, ValidationError

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Send chat message to AI agent and receive response.

    **Flow**:
    1. Verify JWT and extract user_id
    2. Get or create conversation
    3. Load conversation history (last 2000 tokens)
    4. Store user message
    5. Invoke AI agent with Gemini 2.0 Flash and MCP tools
    6. Store assistant response
    7. Return response with tool invocation details

    **Stateless**: All conversation state persists in database.

    Args:
        request: ChatRequest with message and optional conversation_id
        user: Authenticated user from JWT
        session: Database session

    Returns:
        ChatResponse with conversation_id, response, and tool_calls

    Raises:
        HTTPException 401: Invalid JWT
        HTTPException 403: Unauthorized conversation access
        HTTPException 422: Invalid request (message too long, etc.)
        HTTPException 500: Internal server error or MCP tool failure
        HTTPException 503: AI service unavailable
        HTTPException 504: Request timeout (handled by middleware)
    """
    user_id = user["user_id"]

    try:
        # Validate message length (Pydantic already validates, but double-check)
        if len(request.message) > 10000:
            print(f"[ERROR] Validation error: Message too long ({len(request.message)} characters)")
            raise ValidationError("Message must be less than 10,000 characters")

        # Get or create conversation
        # Single conversation per user pattern - auto-creates on first message
        # If conversation_id provided, validates ownership for security
        try:
            conversation = get_or_create_conversation(
                session=session,
                user_id=user_id,
                conversation_id=request.conversation_id
            )
        except ValueError as e:
            # Conversation doesn't belong to user - return 403 Forbidden
            # This enforces user isolation at the conversation level
            print(f"[AUTH] User {user_id} attempted to access unauthorized conversation {request.conversation_id}")
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Access denied. You do not have permission to access this conversation."
                }
            )

        # Load conversation history (up to 2000 tokens)
        # Token counting ensures we stay within Gemini context limits
        # History provides context for agent to understand conversation flow
        history = load_conversation_history(
            session=session,
            conversation_id=conversation.id,
            max_tokens=2000
        )

        # Store user message BEFORE agent invocation
        # This ensures message is persisted even if agent fails
        # Maintains stateless backend - all state in database
        store_message(
            session=session,
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )

        # Get MCP tool definitions
        # These are the task management tools the agent can invoke
        tools = get_tool_definitions()

        # Invoke AI agent with conversation history and MCP tools
        # Agent analyzes intent and decides which tools to call
        # Agent NEVER accesses database directly - only through MCP tools
        try:
            agent_response = await invoke_agent(
                user_id=user_id,
                conversation_history=history,
                user_message=request.message,
                tools=tools
            )
        except GeminiAPIError as e:
            # Gemini API failure - return 503
            print(f"[ERROR] Gemini API error: {e}")
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "AI service temporarily unavailable. Please try again later."
                }
            )
        except Exception as e:
            # Check if it's a tool-related error
            error_msg = str(e)
            if "tool" in error_msg.lower() or "mcp" in error_msg.lower():
                print(f"[ERROR] MCP tool error during agent invocation: {e}")
                raise MCPToolError(f"Task operation failed: {error_msg}")
            else:
                # Re-raise as generic error
                print(f"[ERROR] Unexpected error during agent invocation: {e}")
                raise

        # Store assistant response AFTER agent completion
        # This ensures response is persisted for conversation history
        store_message(
            session=session,
            conversation_id=conversation.id,
            role="assistant",
            content=agent_response["content"]
        )

        # Build response with tool calls
        # tool_calls array shows which MCP tools were invoked
        # Frontend can use this to display tool invocation details
        tool_calls = [
            ToolCall(**tool_call)
            for tool_call in agent_response.get("tool_calls", [])
        ]

        return ChatResponse(
            conversation_id=conversation.id,
            response=agent_response["content"],
            tool_calls=tool_calls
        )

    except HTTPException:
        # Re-raise HTTP exceptions (401, 403, etc.)
        raise

    except ValidationError as e:
        # Validation error - return 422
        print(f"[ERROR] Validation error: {e}")
        raise HTTPException(
            status_code=422,
            detail={
                "error": f"Invalid request: {str(e)}"
            }
        )

    except MCPToolError as e:
        # MCP tool failure - return 500
        print(f"[ERROR] MCP tool error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unable to complete task operation. Please try again."
            }
        )

    except GeminiAPIError as e:
        # Gemini API failure - return 503
        print(f"[ERROR] Gemini API error: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "AI service temporarily unavailable. Please try again later."
            }
        )

    except Exception as e:
        # Log error and return 500 for unexpected errors
        print(f"[ERROR] Unexpected error in chat endpoint: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "An unexpected error occurred. Please try again."
            }
        )
