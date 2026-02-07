# Quickstart Guide: Phase I – Intermediate Level (Organization & Usability)

## Setup Instructions

1. Clone the repository
2. Ensure Python 3.13+ is installed
3. Navigate to the project directory
4. Run `python src/main.py`
5. Use the available commands to manage your todo list with enhanced organization features

## Enhanced Commands

### Basic Level Commands (continued from Basic Level)
- `add <description>` - Add a new todo item
- `view` - View all todo items with their status
- `update <id> <new_description>` - Update an existing item
- `delete <id>` - Delete an item by ID
- `complete <id>` - Mark an item as complete
- `incomplete <id>` - Mark an item as incomplete
- `quit` - Exit the application

### New Enhanced Commands
- `set-priority <id> <level>` - Set priority level (high/medium/low) for an item
- `tag <id> <tag1> [tag2] [tag3]...` - Add tags to an item
- `search <keyword>` - Search for tasks containing keyword
- `filter <criteria> <value>` - Filter tasks (e.g., filter priority high, filter status incomplete, filter tag work)
- `sort <criteria>` - Sort tasks (e.g., sort priority, sort alpha, sort due)

## Example Usage

```
Enter command: add Buy groceries
Added: Buy groceries

Enter command: set-priority 1 high
Set priority of item 1 to high

Enter command: tag 1 shopping weekly
Added tags 'shopping' and 'weekly' to item 1

Enter command: view
1. [ ] [HIGH] shopping,weekly: Buy groceries

Enter command: add Finish report
Added: Finish report

Enter command: set-priority 2 medium
Set priority of item 2 to medium

Enter command: tag 2 work
Added tag 'work' to item 2

Enter command: search groceries
1. [ ] [HIGH] shopping,weekly: Buy groceries

Enter command: filter priority high
1. [ ] [HIGH] shopping,weekly: Buy groceries

Enter command: sort priority
2. [ ] [MEDIUM] work: Finish report
1. [ ] [HIGH] shopping,weekly: Buy groceries

Enter command: quit
Goodbye!
```

## Features

- All Basic Level functionality (Add, View, Update, Delete, Mark Complete/Incomplete)
- Priority levels (high, medium, low) for task importance
- Flexible tagging system for categorizing tasks
- Search functionality to find specific tasks
- Filter functionality to narrow down task lists
- Sort functionality to organize tasks by various criteria
- In-memory storage (data resets when application closes)
- Sequential numeric IDs that reset on restart
- Input validation and error handling
- Clean, user-friendly console interface