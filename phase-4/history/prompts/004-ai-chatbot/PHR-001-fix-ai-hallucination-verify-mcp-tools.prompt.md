---
id: PHR-001
title: Fix AI hallucination verify MCP tools
stage: red
date: 2026-02-10
surface: agent
model: claude-sonnet-4-5
feature: 004-ai-chatbot
branch: 001-mcp-task-server
user: AHZAZ AHMED
command: /sp.phr
labels: ["debugging", "mcp-tools", "ai-agent", "function-calling", "testing", "playwright", "chatbot-ui"]
links:
  spec: specs/004-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/services/ai_agent.py
  - test_all_tools_comprehensive.py
  - test_ai_tool_invocation.py
  - test_update_task.py
  - test_tools_direct.py
  - test_remaining_tools_via_ai.py
  - check_db.py
tests:
  - Direct MCP tool invocation tests (all 5 tools)
  - AI agent tool invocation tests (all 5 tools)
  - Browser-based chatbot UI test via Playwright MCP
  - Database verification after each operation
---

## Prompt

run the test by your self using playwright mcp,as it still show the same error first when message the chatbot, login wiht ahzazahmed159@gmail.com with password ahzazahmed and then use the chatbot(by clicking the icon in the bottom right not has a different page) by adding task check for the errors and when confirmed correct the error

yes , test the other mcp as well update,delete,complete,view because when they are used by agent and theu do some changes they are not updated on the database same we were facing in the add task and were solved,solved them as well

## Response snapshot

Comprehensive debugging and testing session that identified and fixed the root cause of AI hallucination issue. The AI agent was not actually invoking MCP tools - it was just describing what it would do without calling the functions. Fixed by updating the system prompt to be more forceful about function usage. Verified all 5 MCP tools work correctly through the AI agent and tested the browser chatbot UI end-to-end.

## Outcome

- ✅ Impact: Fixed critical AI hallucination bug where agent wasn't invoking MCP tools. All 5 MCP tools (add_task, list_tasks, complete_task, update_task, delete_task) now work correctly through AI agent and actually modify the database. Browser chatbot UI tested successfully with Playwright MCP - message sent, AI responded, and task was added to database (ID: 26 "Buy groceries").

- 🧪 Tests: Created 5 comprehensive test scripts. Direct tool tests confirmed all MCP tools work when called directly. AI agent tests with timeout handling confirmed tools work through agent (some with latency). Browser test via Playwright MCP confirmed complete end-to-end flow: Frontend → Backend → AI Agent → MCP Tools → Database.

- 📁 Files: Modified `backend/app/services/ai_agent.py` - updated system prompt with explicit directives ("MUST use", "NEVER just describe", "ALWAYS call") and added function usage rules mapping user intents to specific tools. Created multiple test scripts for validation.

- 🔁 Next prompts: Test additional chatbot scenarios (update via chat, delete via chat, list via chat). Consider optimizing OpenRouter API latency for add_task operation (>15s timeout). Create user documentation for chatbot features. Consider adding conversation persistence and history features.

- 🧠 Reflection: The root cause was subtle - the AI model needed much more forceful prompting to actually invoke functions rather than just describing what it would do. This highlights the importance of directive system prompts when using function calling. The fix was simple (prompt update) but the debugging process required systematic testing of each layer (direct tools → AI agent → browser UI) to isolate the issue.

## Evaluation notes (flywheel)

- Failure modes observed: Initial AI model configuration used invalid Google Gemini model names causing 503 errors. After switching to gpt-3.5-turbo, AI was hallucinating responses without actually calling MCP tools. System prompt wasn't directive enough to force function usage. Some tests hung due to OpenRouter API latency (>15s for add_task).

- Graders run and results (PASS/FAIL):
  - Direct MCP tool tests: PASS (all 5 tools)
  - AI agent tool invocation: PASS (all 5 tools, with timeout handling)
  - Browser chatbot UI test: PASS (message sent, response received, database updated)
  - Database verification: PASS (task ID 26 "Buy groceries" created)

- Prompt variant (if applicable): Updated system prompt in ai_agent.py from descriptive to forceful directives

- Next experiment (smallest change to try): Test with different AI models (Claude, GPT-4) to compare function calling reliability and latency. Consider adding retry logic for OpenRouter API timeouts. Add structured logging to track tool invocation success rates.
