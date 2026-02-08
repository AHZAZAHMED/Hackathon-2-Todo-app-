"""AI agent setup and invocation using OpenAI SDK with Gemini."""
from typing import List, Dict, Any, Optional
import json
from openai import AsyncOpenAI
from app.ai.gemini_client import get_client
from app.ai.prompts import get_system_prompt
from app.mcp.server import get_tool_definitions, execute_tool
from app.exceptions import GeminiAPIError


async def invoke_agent(
    user_id: str,
    conversation_history: List[Dict[str, str]],
    user_message: str,
    tools: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Invoke AI agent with conversation history and user message.

    Uses Gemini 2.0 Flash via OpenAI-compatible API.
    Agent analyzes user intent and may invoke MCP tools.

    Args:
        user_id: Authenticated user ID from JWT
        conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
        user_message: Current user message
        tools: Optional list of MCP tools for agent to invoke

    Returns:
        Dict with:
            - content: Agent's response message
            - tool_calls: List of tool invocations (if any)

    Raises:
        Exception: If Gemini API call fails
    """
    client = get_client()

    # Get tool definitions if not provided
    if tools is None:
        tools = get_tool_definitions()

    # Build messages array with system prompt, history, and current message
    messages = [
        {"role": "system", "content": get_system_prompt()}
    ]

    # Add conversation history
    messages.extend(conversation_history)

    # Add current user message
    messages.append({"role": "user", "content": user_message})

    try:
        # Call AI model via OpenRouter with function calling support
        response = await client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=messages,
            tools=tools,
            temperature=0.7,
            max_tokens=1000
        )

        message = response.choices[0].message
        tool_calls_list = []

        # Check if agent wants to call tools
        if message.tool_calls:
            # Execute each tool call requested by the agent
            # This implements the function calling pattern where:
            # 1. Agent decides which tools to invoke
            # 2. We execute the tools with user_id injection
            # 3. We send results back to agent
            # 4. Agent formulates final response based on tool results
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                try:
                    # Execute tool with user_id injection for security
                    # user_id from JWT ensures users can only access their own data
                    tool_result = execute_tool(tool_name, tool_args, user_id)

                    # Convert Pydantic models to dict for JSON serialization
                    # MCP tools return Pydantic models, but we need plain dicts for API
                    if hasattr(tool_result, 'dict'):
                        tool_result = tool_result.dict()
                    elif isinstance(tool_result, list) and len(tool_result) > 0 and hasattr(tool_result[0], 'dict'):
                        tool_result = [item.dict() for item in tool_result]

                    # Store tool call details for response to client
                    # This allows frontend to show which tools were invoked
                    tool_calls_list.append({
                        "tool": tool_name,
                        "arguments": tool_args,
                        "result": tool_result
                    })

                    # Add tool result to messages for agent to see
                    # This follows OpenAI function calling protocol:
                    # - First message: assistant with tool_calls
                    # - Second message: tool with result
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call.dict()]
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result)
                    })

                except Exception as e:
                    # Tool execution failed - add error to messages
                    error_msg = f"Tool execution failed: {str(e)}"
                    print(f"[ERROR] {error_msg}")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"error": error_msg})
                    })

            # Get final response from agent after tool execution
            final_response = await client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )

            assistant_message = final_response.choices[0].message.content

            return {
                "content": assistant_message,
                "tool_calls": tool_calls_list
            }

        else:
            # No tool calls - return direct response
            assistant_message = message.content

            return {
                "content": assistant_message,
                "tool_calls": []
            }

    except Exception as e:
        # Log error and re-raise as GeminiAPIError for endpoint to handle
        print(f"[ERROR] Gemini API call failed: {e}")
        raise GeminiAPIError(f"AI service error: {str(e)}")


def create_agent_context(user_id: str) -> Dict[str, Any]:
    """
    Create agent context with user information.

    This context is used to pass user_id to MCP tools.

    Args:
        user_id: Authenticated user ID from JWT

    Returns:
        Dict with user context for agent
    """
    return {
        "user_id": user_id
    }
