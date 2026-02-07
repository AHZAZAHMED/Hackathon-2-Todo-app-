# Implementation Plan: Phase I – In-Memory Python Console Todo App

**Branch**: 1-console-todo-app
**Created**: 2026-01-21
**Status**: Draft

## Technical Context

**Application Type**: Console application with in-memory storage
**Primary Language**: Python 3.13+
**Architecture**: Single-process application with in-memory data structures
**Data Model**: Todo items with text description and completion status
**Storage**: In-memory only, no persistence (reset on restart)
**Task IDs**: Sequential numeric IDs (1, 2, 3...) that reset on restart
**Interaction Style**: Command-line interface with text-based commands
**Dependencies**: None beyond Python standard library (initially)

**Unknowns**:
- Specific Python modules to use for command parsing (NEEDS CLARIFICATION)
- Exact file structure under /src (NEEDS CLARIFICATION)
- Error handling strategy details (NEEDS CLARIFICATION)

## Constitution Check

This implementation plan adheres to the project constitution by:
- Following the spec-driven development principle: implementation based strictly on approved specification
- Maintaining incremental correctness: Phase I focuses on core functionality before advancing
- Supporting reproducibility: clear structure and predictable behavior
- Following quality standards: clean, modular Python project structure
- Staying within Phase I constraints: in-memory only, console-based interface

## Gates

**GATE 1: Specification Clarity** - PASSED ✓
All core requirements from the feature specification are understood and testable.

**GATE 2: Technical Feasibility** - PASSED ✓
Python is suitable for console applications with in-memory storage.

**GATE 3: Resource Availability** - PASSED ✓
All required technologies (Python 3.13+) are available.

**GATE 4: Constraint Compliance** - PASSED ✓
Solution respects in-memory-only and console-interface constraints.

## Phase 0: Outline & Research

### Research Tasks

1. **Command-line parsing approach**
   - Decision: Use Python's built-in `sys.argv` for simple command parsing
   - Rationale: Keeps implementation simple for Phase I, avoids external dependencies
   - Alternative considered: argparse module (more complex than needed)

2. **File structure under /src**
   - Decision: Single main.py file for initial implementation
   - Rationale: Simplest approach for Phase I, can be refactored later if needed
   - Alternative considered: Modular structure (not needed for Phase I scope)

3. **Error handling strategy**
   - Decision: Try/catch blocks with user-friendly error messages
   - Rationale: Provides clear feedback for invalid inputs as required by spec
   - Alternative considered: Custom exception classes (overkill for Phase I)

### Consolidated Findings

- **Decision**: Use a single-file approach with `main.py` containing all functionality
- **Rationale**: Aligns with Phase I's simplicity goal and in-memory constraints
- **Alternatives considered**: Multi-module structure was evaluated but deemed unnecessarily complex for this phase

## Phase 1: Design & Contracts

### Data Model

#### Todo Item Entity
- **Fields**:
  - `id`: Integer (sequential, starts from 1)
  - `description`: String (the task text)
  - `completed`: Boolean (whether the task is completed)
- **Validation**:
  - Description must not be empty or whitespace-only
  - ID must be positive integer
- **State Transitions**:
  - `incomplete` → `completed` (via complete command)
  - `completed` → `incomplete` (via incomplete command)

#### Todo List Entity
- **Fields**:
  - `items`: List of TodoItem objects
- **Operations**:
  - Add new item (appends to list)
  - View all items (returns all items)
  - Update item by ID (modifies specific item)
  - Delete item by ID (removes specific item)
  - Mark complete/incomplete by ID (changes completion status)

### File Structure
```
src/
└── main.py              # Main application logic
```

### API Contracts (Console Commands)

1. **Add Command**: `add <description>`
   - Action: Creates a new todo item with the given description
   - Success: Item is added to the list with next sequential ID
   - Error: Shows error message if description is empty

2. **View Command**: `view`
   - Action: Displays all todo items with their completion status
   - Success: Lists all items with [ ] or [x] for incomplete/complete
   - Error: Shows "No items in your todo list" if empty

3. **Update Command**: `update <id> <new_description>`
   - Action: Updates the description of the item with the given ID
   - Success: Updates the item's description
   - Error: Shows error if ID is invalid or description is empty

4. **Delete Command**: `delete <id>`
   - Action: Removes the item with the given ID from the list
   - Success: Removes the item from the list
   - Error: Shows error if ID is invalid

5. **Complete Command**: `complete <id>`
   - Action: Marks the item with the given ID as completed
   - Success: Sets the item's completion status to True
   - Error: Shows error if ID is invalid

6. **Incomplete Command**: `incomplete <id>`
   - Action: Marks the item with the given ID as incomplete
   - Success: Sets the item's completion status to False
   - Error: Shows error if ID is invalid

7. **Quit Command**: `quit`
   - Action: Exits the application gracefully
   - Success: Application terminates

### Quickstart Guide

1. Clone the repository
2. Ensure Python 3.13+ is installed
3. Navigate to the project directory
4. Run `python src/main.py`
5. Use the available commands to manage your todo list

## Phase 2: Implementation Steps

### Step 1: Set up project structure
- Create `src/main.py` file
- Define TodoItem class with id, description, and completed fields
- Define TodoList class with methods for all required operations

### Step 2: Implement core data structures
- Implement TodoItem class with initialization and string representation
- Implement TodoList class with add, view, update, delete, complete, incomplete methods
- Add validation and error handling for each method

### Step 3: Implement command parsing
- Create main loop that accepts user input
- Parse commands and route to appropriate TodoList methods
- Handle command syntax validation

### Step 4: Implement error handling
- Add try/catch blocks for invalid inputs
- Provide user-friendly error messages
- Validate all user inputs according to specification

### Step 5: Testing and validation
- Manually test each command
- Verify all acceptance scenarios from the specification
- Ensure graceful handling of edge cases

## Success Criteria Validation

Each of the original success criteria will be validated:
- **SC-001**: Users can add, view, update, delete, and mark complete/incomplete all todo items
- **SC-002**: Console application responds to user commands within 1 second
- **SC-003**: All 5 basic todo features function correctly without data loss during a session
- **SC-004**: Application handles invalid inputs gracefully with appropriate error messages