# Phase I – In-Memory Python Console Todo App

A simple console-based todo application that stores tasks in memory during runtime.

## Setup

1. Ensure Python 3.13+ is installed on your system
2. Clone this repository
3. Navigate to the project directory

## Usage

Run the application using:
```bash
python src/main.py
```

## Available Commands

### Basic Commands
- `add <description>` - Add a new todo item
- `view` - View all todo items with their status
- `update <id> <new_description>` - Update an existing item
- `delete <id>` - Delete an item by ID
- `complete <id>` - Mark an item as complete
- `incomplete <id>` - Mark an item as incomplete

### Enhanced Commands (Phase I - Intermediate Level)
- `set-priority <id> <level>` - Set priority level (high/medium/low) for an item
- `tag <id> <tag1> [tag2] [tag3]...` - Add tags to an item
- `search <keyword>` - Search for tasks containing keyword
- `filter <criteria> <value>` - Filter tasks (criteria: status/priority/tag, value: varies by criteria)
- `sort <criteria>` - Sort tasks (criteria: priority/alpha/alphabetical/due)

- `quit` - Exit the application

## Example Usage

```
Welcome to the Enhanced Todo App!
Available commands: add, view, update, delete, complete, incomplete, set-priority, tag, search, filter, sort, quit

Enter command: add Buy groceries
Added: Buy groceries

Enter command: set-priority 1 high
Set priority of item 1 to high

Enter command: tag 1 shopping weekly
Added tags shopping, weekly to item 1

Enter command: view
1. [ ] [H] Buy groceries [shopping, weekly]

Enter command: add Walk the dog
Added: Walk the dog

Enter command: set-priority 2 medium
Set priority of item 2 to medium

Enter command: view
1. [ ] [H] Buy groceries [shopping, weekly]
2. [ ] [M] Walk the dog

Enter command: search groceries
1. [ ] [H] Buy groceries [shopping, weekly]

Enter command: filter priority high
1. [ ] [H] Buy groceries [shopping, weekly]

Enter command: sort priority
2. [ ] [M] Walk the dog
1. [ ] [H] Buy groceries [shopping, weekly]

Enter command: quit
Goodbye!
```

## Features

- Add, view, update, delete, and mark todo items as complete/incomplete
- Priority levels (high, medium, low) for organizing tasks by importance
- Tagging system for categorizing tasks (e.g., work, personal, urgent)
- Search functionality to find tasks by keyword in description or tags
- Filtering by status (complete/incomplete), priority (high/medium/low), or tags
- Sorting by priority, alphabetical order, or due date
- In-memory storage (data resets when application closes)
- Sequential numeric IDs that reset on restart
- Input validation and error handling
- Clean, user-friendly console interface