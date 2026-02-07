# Implementation Plan: Phase I – Advanced Level (Overdue & Remind Logic Refinement)

## Feature Overview
- **Feature**: 4-overdue-remind-logic
- **Branch**: 4-overdue-remind-logic
- **Type**: Logic refinement for existing console-based todo application
- **Focus**: Correcting overdue detection and remind command functionality

## Technical Context
- **Application Type**: Enhancement to existing console application with improved datetime logic
- **Primary Language**: Python 3.13+
- **Architecture**: Single-process application extending existing in-memory data structures
- **Data Model**: Enhanced Todo items with improved due date handling and comparison logic
- **Storage**: In-memory only, no persistence (reset on restart) - continuing Basic/Intermediate/Advanced Level constraints
- **Task IDs**: Sequential numeric IDs (1, 2, 3...) that reset on restart
- **Interaction Style**: Natural language command-line interface with text-based commands
- **Dependencies**: Python standard library only (datetime, timedelta modules specifically)

**Unknowns**:
- Current time retrieval approach (NEEDS CLARIFICATION)
- Due date storage format (NEEDS CLARIFICATION)
- Overdue comparison implementation (NEEDS CLARIFICATION)
- Upcoming window calculation (NEEDS CLARIFICATION)
- Timedelta import approach (NEEDS CLARIFICATION)

## Constitution Check
This implementation plan adheres to the project constitution by:
- Following the spec-driven development principle: implementation based strictly on approved specification
- Maintaining incremental correctness: building on completed Basic, Intermediate, and Advanced Level functionality
- Supporting reproducibility: clear structure and predictable behavior
- Following quality standards: clean, modular Python project structure
- Staying within Phase I constraints: console-based interface, in-memory only, deterministic behavior
- Following the required sequence: Basic → Intermediate → Advanced → Current refinement as per governance rules
- Building upon existing functionality without breaking changes

## Gates
- **GATE 1: Specification Clarity** - PASSED ✓
  All core requirements from the feature specification are understood and testable.

- **GATE 2: Technical Feasibility** - PASSED ✓
  Python is suitable for datetime operations with in-memory storage.

- **GATE 3: Resource Availability** - PASSED ✓
  All required technologies (Python 3.13+, datetime module) are available.

- **GATE 4: Constraint Compliance** - PASSED ✓
  Solution respects in-memory-only and console-interface constraints.

- **GATE 5: Phase Compliance** - PASSED ✓
  Implementation stays within Advanced Level scope as defined in constitution.

## Phase 0: Research & Analysis

### Research Tasks

1. **Current time retrieval approach**
   - Decision: Use `datetime.now().date()` to get current date for comparison
   - Rationale: Provides the current date for overdue comparisons without time component complications
   - Alternative considered: `date.today()` (similar functionality, chose datetime.now().date() for consistency)

2. **Due date storage and parsing**
   - Decision: Store due dates as string in 'YYYY-MM-DD' format with validation using datetime.strptime
   - Rationale: Maintains consistency with existing ISO 8601 format requirement while enabling proper comparison
   - Alternative considered: Store as datetime objects (unnecessary complexity for in-memory storage)

3. **Overdue comparison implementation**
   - Decision: Compare due date with current date using proper date comparison: due_date < current_date
   - Rationale: Provides accurate overdue detection only for tasks with due dates in the past
   - Alternative considered: Different comparison operators (less than is correct for overdue detection)

4. **Upcoming window calculation (now → now + 24 hours)**
   - Decision: Use timedelta(days=1) to calculate the 24-hour window for remind functionality
   - Rationale: Enables accurate detection of tasks due within the next 24 hours
   - Alternative considered: Hardcoded time windows (less flexible than timedelta approach)

5. **Timedelta import approach**
   - Decision: Import timedelta explicitly as `from datetime import timedelta` and use as `timedelta(days=1)`
   - Rationale: Follows specification requirement to import timedelta explicitly and not access as attribute of datetime
   - Alternative considered: Accessing as datetime.timedelta (violates specification requirement)

### Consolidated Findings
- **Decision**: Implement all datetime operations using proper imports and date comparisons
- **Rationale**: Aligns with specification requirements for deterministic, reliable behavior while maintaining simplicity
- **Alternatives considered**: Various datetime libraries and approaches were evaluated but Python's standard datetime/timedelta is most appropriate

## Phase 1: Architecture & Design

### Data Model Extensions

#### Enhanced Todo Item Entity (Refined)
- **Fields**:
  - `id`: Integer (sequential, starts from 1)
  - `description`: String (the task text)
  - `completed`: Boolean (whether the task is completed)
  - `priority`: String (priority level: "high", "medium", "low")
  - `tags`: List of Strings (list of tag strings)
  - `due_date`: Optional String (due date in 'YYYY-MM-DD' format if specified)
  - `recurrence_pattern`: Optional String (recurrence: "daily", "weekly", "monthly", or None)
  - `next_occurrence`: Optional String (when the next occurrence is due, for recurring tasks)
- **Validation**:
  - Description must not be empty or whitespace-only
  - ID must be positive integer
  - Priority must be one of "high", "medium", "low"
  - Tags must be non-empty strings
  - Due date must be in 'YYYY-MM-DD' format if specified
  - Recurrence pattern must be valid if specified
- **State Transitions**:
  - `incomplete` → `completed` (via complete command)
  - `completed` → `incomplete` (via incomplete command)
  - Priority levels can be updated
  - Tags can be added/removed
  - Due dates can be set/cleared
  - Recurring tasks generate next occurrence on completion

#### Enhanced Todo List Entity (Refined)
- **Fields**:
  - `items`: List of EnhancedTodoItem objects
- **Operations**:
  - All existing operations from Basic/Intermediate/Advanced levels
  - **Enhanced Overdue Detection**: Check if item has due date AND due date < current date
  - **Enhanced Remind Logic**: Check for tasks due between now and now + 24 hours
  - **Date Validation**: Verify proper 'YYYY-MM-DD' format for all date operations

### Architecture Components

#### DateTime Handler
- **Responsibility**: Centralized date/time operations and comparisons
- **Functions**:
  - Get current date for comparisons
  - Validate date format ('YYYY-MM-DD')
  - Compare dates for overdue detection
  - Calculate upcoming windows for reminders
  - Handle date arithmetic using timedelta

#### Overdue Detector
- **Responsibility**: Identify tasks that are past their due date
- **Logic**: Only tasks with due dates that are earlier than current date are overdue
- **Input**: List of todo items
- **Output**: List of overdue items only

#### Reminder Calculator
- **Responsibility**: Identify tasks due within the next 24 hours
- **Logic**: Tasks with due dates between current date and current date + 1 day
- **Input**: List of todo items
- **Output**: List of tasks due soon (within 24 hours)

### File Structure
```
.src/
└── main.py              # Enhanced application logic with refined datetime operations
```

### API Contracts (Console Commands - Enhanced)

1. **Overdue Command (Enhanced)**: `overdue`
   - Action: Finds tasks with due dates that are in the past (due_date < current_date)
   - Success: Displays only tasks that have due dates AND are past their due date
   - Error: Shows "No overdue tasks" if none found

2. **Remind Command (Enhanced)**: `remind`
   - Action: Finds tasks due within the next 24 hours (current_date ≤ due_date ≤ current_date + 1 day)
   - Success: Displays only tasks due within the next 24 hours
   - Error: Shows "No upcoming tasks due in the next 24 hours" if none found

3. **Set-Due Command (Enhanced)**: `set-due <id> <YYYY-MM-DD>`
   - Action: Sets due date for task with proper validation
   - Success: Task's due date is updated
   - Error: Shows error if date format is invalid or ID doesn't exist

4. **All Existing Commands**: Continue to work as before (add, view, update, delete, complete, incomplete, set-priority, tag, search, filter, sort, quit)

### Quickstart Guide (Enhanced)

1. Clone the repository
2. Ensure Python 3.13+ is installed
3. Navigate to the project directory
4. Run `python src/main.py`
5. Use the available commands to manage your todo list with enhanced datetime functionality

## Phase 2: Implementation Steps

### Step 1: Update DateTime Imports and Utilities
- Import timedelta explicitly from datetime module
- Add proper date validation utilities
- Implement current date retrieval function

### Step 2: Enhance TodoItem Class
- Update is_overdue() method to properly compare with current date
- Ensure tasks without due dates are never considered overdue
- Add proper error handling for invalid date formats

### Step 3: Enhance TodoList Class
- Update get_overdue_items() to use proper comparison logic
- Implement get_due_soon_items() method for remind functionality
- Add proper date range calculations using timedelta

### Step 4: Update Command Handlers
- Enhance overdue command handler with correct logic
- Implement enhanced remind command handler with 24-hour window
- Update set-due command handler with proper validation

### Step 5: Testing and Validation
- Test overdue detection with various date scenarios
- Test remind functionality with different due date ranges
- Validate all edge cases for date operations
- Verify all acceptance scenarios from specification

## Success Criteria Validation

Each of the original success criteria will be validated:
- **SC-001**: All tasks with past due dates correctly identified as overdue, tasks without due dates never marked as overdue
- **SC-002**: Remind command only returns tasks due within the next 24 hours
- **SC-003**: All date comparisons performed deterministically and reliably without crashes
- **SC-004**: DateTime arithmetic uses explicit timedelta imports with no usage as datetime attributes
- **SC-005**: System handles edge cases for date operations gracefully without errors