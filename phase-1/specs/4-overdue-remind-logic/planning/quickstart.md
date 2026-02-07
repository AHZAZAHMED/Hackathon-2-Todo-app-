# Quickstart Guide: Phase I – Advanced Level (Overdue & Remind Logic Refinement)

## Setup Instructions

1. Clone the repository
2. Ensure Python 3.13+ is installed
3. Navigate to the project directory
4. Run `python src/main.py`
5. Use the available commands to manage your todo list with enhanced datetime functionality

## Enhanced Commands Available

### Basic Level Commands (continued from previous phases)
- `add <description>` - Add a new todo item
- `view` - View all todo items with their status
- `update <id> <new_description>` - Update an existing item
- `delete <id>` - Delete an item by ID
- `complete <id>` - Mark an item as complete
- `incomplete <id>` - Mark an item as incomplete
- `quit` - Exit the application

### Intermediate Level Commands (from previous phases)
- `set-priority <id> <level>` - Set priority (high/medium/low) for an item
- `tag <id> <tag1> [tag2]...` - Add tags to an item
- `search <keyword>` - Search tasks by keyword
- `filter <criteria> <value>` - Filter tasks by criteria
- `sort <criteria>` - Sort tasks by criteria

### Advanced Level Commands (Phase I - Overdue & Remind Logic Refinement)
- `set-due <id> <YYYY-MM-DD>` - Set due date for a task
- `overdue` - Show only tasks that are past their due date (tasks with due dates AND current date > due date)
- `remind` - Show only tasks due within the next 24 hours (current date ≤ due date ≤ current date + 1 day)

## Example Usage

```
Enter command: add Submit quarterly report
Added: Submit quarterly report

Enter command: set-due 1 2026-01-25
Set due date for item 1 to 2026-01-25

Enter command: set-priority 1 high
Set priority of item 1 to high

Enter command: tag 1 work urgent
Added tags work, urgent to item 1

Enter command: add Walk the dog
Added: Walk the dog

Enter command: set-due 2 2026-01-22  # Tomorrow
Set due date for item 2 to 2026-01-22

Enter command: view
1. [ ] [H] Submit quarterly report (DUE:2026-01-25) [work, urgent]
2. [ ] [M] Walk the dog (DUE:2026-01-22)

Enter command: overdue
No overdue tasks  # Because these dates are in the future

Enter command: remind
2. [ ] [M] Walk the dog (DUE:2026-01-22)  # Due tomorrow (within 24 hours)

Enter command: quit
Goodbye!
```

## Key Features

- All Basic, Intermediate, and Advanced Level functionality working together
- Proper overdue detection (only tasks with due dates in the past)
- Smart reminder system (only tasks due within next 24 hours)
- Date validation using ISO 8601 format (YYYY-MM-DD)
- Explicit timedelta imports for date arithmetic
- Console-based interface with clear, readable output
- In-memory storage with sequential IDs that reset on restart
- Input validation and error handling for all commands
- Natural language command processing