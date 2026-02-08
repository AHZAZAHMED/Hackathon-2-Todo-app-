"""MCP server setup and tool registration."""
from typing import List, Dict, Any
from app.mcp.tools import add_task, list_tasks, complete_task, delete_task, update_task


def get_tool_definitions() -> List[Dict[str, Any]]:
    """
    Get OpenAI function calling tool definitions for MCP tools.

    Returns tool schemas in OpenAI function calling format.
    These are passed to the chat completions API.

    Returns:
        List[Dict]: Tool definitions for OpenAI API
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Creates a new task for the user. Use this when the user wants to add, create, or remember something to do.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The task title or description of what needs to be done"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional additional details about the task"
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
                "description": "Lists all tasks for the user. Use this when the user wants to see their tasks, check what they need to do, or review their todo list.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "completed": {
                            "type": "boolean",
                            "description": "Optional filter: true for completed tasks only, false for incomplete tasks only, omit for all tasks"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Toggles a task's completion status. Use this when the user wants to mark a task as done or undone.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to toggle completion status"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Deletes a task permanently. Use this when the user wants to remove or delete a task.",
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
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Updates a task's title and/or description. Use this when the user wants to change or edit a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New title for the task (optional)"
                        },
                        "description": {
                            "type": "string",
                            "description": "New description for the task (optional)"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        }
    ]


def execute_tool(tool_name: str, arguments: Dict[str, Any], user_id: str) -> Any:
    """
    Execute an MCP tool with the given arguments.

    Routes tool calls to the appropriate MCP tool function.
    Injects user_id from JWT into tool arguments.

    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments from agent
        user_id: User ID from JWT

    Returns:
        Tool execution result

    Raises:
        ValueError: If tool name is unknown
        Exception: If tool execution fails
    """
    # Map tool names to functions
    tool_map = {
        "add_task": add_task,
        "list_tasks": list_tasks,
        "complete_task": complete_task,
        "delete_task": delete_task,
        "update_task": update_task
    }

    if tool_name not in tool_map:
        raise ValueError(f"Unknown tool: {tool_name}")

    # Get tool function
    tool_func = tool_map[tool_name]

    # Inject user_id into arguments
    arguments["user_id"] = user_id

    # Execute tool
    try:
        result = tool_func(**arguments)
        return result
    except Exception as e:
        # Log error and re-raise
        print(f"[ERROR] Tool {tool_name} execution failed: {e}")
        raise
