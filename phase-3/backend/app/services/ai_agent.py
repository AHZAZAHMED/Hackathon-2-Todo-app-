"""
AI Agent Service for chat functionality.
Integrates OpenAI Agents SDK with OpenRouter API for AI responses.
Supports function calling to invoke MCP tools for task management.
"""

from openai import AsyncOpenAI
from app.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, AI_MODEL
from typing import List, Dict, Any
import logging
import json
from datetime import datetime

# Import MCP tool functions directly
from app.mcp.tools.add_task import add_task
from app.mcp.tools.list_tasks import list_tasks
from app.mcp.tools.complete_task import complete_task
from app.mcp.tools.update_task import update_task
from app.mcp.tools.delete_task import delete_task


# Configure structured logging
logger = logging.getLogger(__name__)


def log_ai_structured(level: str, request_id: str, event: str, **kwargs):
    """
    Log structured JSON messages for AI service per spec FR-015.

    Args:
        level: Log level (info, warning, error)
        request_id: Unique request identifier
        event: Event description
        **kwargs: Additional context fields (excludes sensitive data)
    """
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id,
        "service": "ai_agent",
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


class AIAgentService:
    """
    Service for generating AI responses using OpenAI SDK with OpenRouter.

    This service provides a stateless interface for generating AI responses
    based on conversation history. It uses OpenRouter API as a third-party
    LLM provider and supports function calling to invoke MCP tools.
    """

    def __init__(self):
        """
        Initialize the AI agent service.

        Creates an AsyncOpenAI client configured to use OpenRouter API
        as the backend provider.
        """
        self.client = AsyncOpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
            default_headers={
                "HTTP-Referer": "https://hackathon-phase3.com",
                "X-Title": "Todo AI Chatbot"
            }
        )

        self.system_prompt = (
            "You are a helpful task management assistant. You have access to functions that can manage tasks. "
            "Use these functions to help users with their tasks."
            "\n\nWhen a user refers to a task by its title or description (not by ID number):"
            "\n1. First, call list_tasks() to see all available tasks"
            "\n2. Find the task that matches what the user described"
            "\n3. Use the task's ID to call the appropriate function"
            "\n\nExamples:"
            "\n- User: 'Mark the milk task as complete' → Call list_tasks(), find 'Buy milk' task, then call complete_task with its ID"
            "\n- User: 'Delete my grocery task' → Call list_tasks(), find the grocery task, then call delete_task with its ID"
            "\n- User: 'Update the prayer task title to Morning prayer' → Call list_tasks(), find the prayer task, then call update_task with its ID"
            "\n\nAlways use the functions to perform actions. After calling a function, tell the user what was done based on the result."
        )

        self.model = AI_MODEL

        # Define available tools for function calling
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new task for the user with a title and optional description",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The task title (max 500 characters)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional task description"
                            }
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "Retrieve the user's tasks, optionally filtered by completion status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["all", "pending", "completed"],
                                "description": "Filter by status: 'all', 'pending', or 'completed' (default: 'all')"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of tasks to return (default: 100, max: 1000)"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Toggle the completion status of a task (mark as done or undone)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to toggle"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update a task's title and/or description",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New task title (max 500 characters)"
                            },
                            "description": {
                                "type": "string",
                                "description": "New task description"
                            }
                        },
                        "required": ["task_id", "title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task permanently",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to delete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            }
        ]

    async def generate_response(self, conversation_history: List[Dict[str, str]], user_id: str, request_id: str = "unknown") -> str:
        """
        Generate AI response based on conversation history with tool support.

        This method takes the conversation history and generates a contextually
        relevant response using the configured AI model via OpenRouter. It supports
        function calling to invoke MCP tools for task management.

        Args:
            conversation_history: List of message dicts with 'role' and 'content'.
                                 Example: [{"role": "user", "content": "Hello"}]
            user_id: The authenticated user's ID (passed to MCP tools)
            request_id: Unique request identifier for tracing

        Returns:
            str: AI-generated response message

        Raises:
            Exception: If AI service fails (caller should handle and return 503)
        """
        # Build messages array with system prompt
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(conversation_history)

        try:
            log_ai_structured(
                "info",
                request_id,
                "openrouter_request_started",
                model=self.model,
                message_count=len(messages)
            )

            # Agentic loop: Allow multiple rounds of tool calling
            max_iterations = 5  # Prevent infinite loops
            iteration = 0

            print(f"\n[AGENTIC LOOP] Starting agentic loop for request {request_id}")

            while iteration < max_iterations:
                iteration += 1

                print(f"\n[AGENTIC LOOP] === Iteration {iteration}/{max_iterations} ===")
                print(f"[AGENTIC LOOP] Messages in conversation: {len(messages)}")
                print(f"[AGENTIC LOOP] Last message role: {messages[-1]['role'] if messages else 'None'}")

                # Log the messages being sent to the model
                log_ai_structured(
                    "info",
                    request_id,
                    "agentic_loop_iteration_start",
                    iteration=iteration,
                    message_count=len(messages),
                    last_message_role=messages[-1]["role"] if messages else None
                )

                # Call OpenRouter API via OpenAI SDK with tools
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",
                    temperature=0.7,
                    max_tokens=500
                )

                # Get the assistant's response
                assistant_message = response.choices[0].message

                print(f"[AGENTIC LOOP] Model response received")
                print(f"[AGENTIC LOOP] Has tool_calls: {bool(assistant_message.tool_calls)}")
                print(f"[AGENTIC LOOP] Tool calls count: {len(assistant_message.tool_calls) if assistant_message.tool_calls else 0}")
                print(f"[AGENTIC LOOP] Content: {assistant_message.content[:100] if assistant_message.content else 'None'}...")

                # Log what the model returned with full details
                log_ai_structured(
                    "info",
                    request_id,
                    "model_response_received",
                    iteration=iteration,
                    has_tool_calls=bool(assistant_message.tool_calls),
                    tool_calls_count=len(assistant_message.tool_calls) if assistant_message.tool_calls else 0,
                    content=assistant_message.content[:200] if assistant_message.content else None,
                    content_length=len(assistant_message.content) if assistant_message.content else 0
                )

                # Check if the AI wants to call tools
                if assistant_message.tool_calls:
                    log_ai_structured(
                        "info",
                        request_id,
                        "tool_calls_requested",
                        iteration=iteration,
                        tool_count=len(assistant_message.tool_calls),
                        tool_names=[tc.function.name for tc in assistant_message.tool_calls]
                    )

                    # Add assistant's message with tool calls to conversation
                    messages.append({
                        "role": "assistant",
                        "content": assistant_message.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in assistant_message.tool_calls
                        ]
                    })

                    # Execute each tool call
                    for tool_call in assistant_message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)

                        log_ai_structured(
                            "info",
                            request_id,
                            "tool_execution_started",
                            iteration=iteration,
                            tool_name=function_name,
                            tool_args=function_args
                        )

                        # Invoke the appropriate MCP tool
                        tool_result = await self._invoke_tool(function_name, user_id, function_args)

                        log_ai_structured(
                            "info",
                            request_id,
                            "tool_execution_completed",
                            iteration=iteration,
                            tool_name=function_name,
                            tool_result=tool_result
                        )

                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(tool_result)
                        })

                    # Log that we're continuing the loop
                    log_ai_structured(
                        "info",
                        request_id,
                        "agentic_loop_continuing",
                        iteration=iteration,
                        reason="tools_executed",
                        total_messages=len(messages)
                    )

                    # Continue loop to allow model to call more tools or generate final response
                    continue
                else:
                    # No more tool calls, return the final response
                    log_ai_structured(
                        "info",
                        request_id,
                        "agentic_loop_exiting",
                        iteration=iteration,
                        reason="no_tool_calls",
                        final_content=assistant_message.content[:200] if assistant_message.content else None
                    )
                    response_content = assistant_message.content
                    break

            # If we hit max iterations, return whatever we have
            if iteration >= max_iterations:
                response_content = assistant_message.content if assistant_message.content else "I've completed the requested actions."

            log_ai_structured(
                "info",
                request_id,
                "openrouter_response_success",
                model=self.model,
                response_length=len(response_content) if response_content else 0
            )

            return response_content

        except Exception as e:
            # Log error and re-raise for caller to handle
            log_ai_structured(
                "error",
                request_id,
                "openrouter_request_failed",
                model=self.model,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            raise

    async def _invoke_tool(self, tool_name: str, user_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke an MCP tool with the given arguments.

        Args:
            tool_name: Name of the tool to invoke
            user_id: User ID to pass to the tool
            args: Tool arguments

        Returns:
            Tool execution result
        """
        # Add user_id to args
        args["user_id"] = user_id

        # Invoke the appropriate tool
        if tool_name == "add_task":
            return await add_task(**args)
        elif tool_name == "list_tasks":
            return await list_tasks(**args)
        elif tool_name == "complete_task":
            return await complete_task(**args)
        elif tool_name == "update_task":
            return await update_task(**args)
        elif tool_name == "delete_task":
            return await delete_task(**args)
        else:
            return {"error": f"Unknown tool: {tool_name}"}


# Singleton instance
ai_agent = AIAgentService()
