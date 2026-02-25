#!/usr/bin/env python
"""
MCP Task Server Startup Script

Starts the MCP server with stdio transport for agent communication.
The server exposes 5 task management tools that the OpenAI Agent can invoke.

Usage:
    python backend/scripts/run_mcp_server.py

Environment Variables:
    DATABASE_URL: PostgreSQL connection string (required)
"""

import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.mcp.server import run_server

if __name__ == "__main__":
    print("Starting MCP Task Server...", file=sys.stderr)
    print("Transport: stdio", file=sys.stderr)
    print("Tools: add_task, list_tasks, update_task, complete_task, delete_task", file=sys.stderr)
    run_server()
