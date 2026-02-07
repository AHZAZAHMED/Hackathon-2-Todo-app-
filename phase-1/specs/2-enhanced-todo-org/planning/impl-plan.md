# Implementation Plan: Phase I – Intermediate Level (Organization & Usability)

**Branch**: 2-enhanced-todo-org
**Created**: 2026-01-21
**Status**: Draft

## Technical Context

**Application Type**: Extension of existing console application with enhanced organization features
**Primary Language**: Python 3.13+
**Architecture**: Single-process application extending existing in-memory data structures
**Data Model**: Enhanced Todo items with priority levels, tags, and search/filter capabilities
**Storage**: In-memory only, no persistence (reset on restart) - continuing Basic Level constraint
**Task IDs**: Sequential numeric IDs (1, 2, 3...) that reset on restart
**Interaction Style**: Command-line interface with text-based commands extending Basic Level
**Dependencies**: Python standard library (continuing Basic Level approach)

**Unknowns**:
- Priority storage implementation approach (NEEDS CLARIFICATION)
- Tag management approach (free-text vs predefined) (NEEDS CLARIFICATION)
- Search algorithm implementation (linear vs indexed) (NEEDS CLARIFICATION)
- Sorting implementation (custom vs built-in Python sort) (NEEDS CLARIFICATION)
- Console output formatting for enhanced information (NEEDS CLARIFICATION)

## Constitution Check

This implementation plan adheres to the project constitution by:
- Following the spec-driven development principle: implementation based strictly on approved specification
- Maintaining incremental correctness: building on completed Basic Level functionality
- Supporting reproducibility: clear structure and predictable behavior
- Following quality standards: clean, modular Python project structure
- Staying within Phase I Intermediate Level constraints: console-based interface, in-memory only
- Following the required sequence: Basic → Intermediate → Advanced as per governance rules
- Building upon existing Basic Level implementation without breaking changes

## Gates

**GATE 1: Specification Clarity** - PASSED ✓
All core requirements from the feature specification are understood and testable.

**GATE 2: Technical Feasibility** - PASSED ✓
Python is suitable for enhancing console applications with organization features.

**GATE 3: Resource Availability** - PASSED ✓
All required technologies (Python 3.13+) are available.

**GATE 4: Constraint Compliance** - PASSED ✓
Solution respects in-memory-only and console-interface constraints.

**GATE 5: Phase Compliance** - PASSED ✓
Implementation stays within Intermediate Level scope as defined in constitution.

## Phase 0: Outline & Research

### Research Tasks

1. **Priority storage approach**
   - Decision: Use string constants for priority levels (high, medium, low)
   - Rationale: Simple implementation that matches specification requirements and is easily extensible
   - Alternative considered: Enum class (more complex than needed)

2. **Tag management approach**
   - Decision: Free-text tags with flexible string values
   - Rationale: Provides maximum flexibility for users to create custom tags as needed
   - Alternative considered: Predefined tag categories (too restrictive)

3. **Search algorithm implementation**
   - Decision: Linear search through items with case-insensitive substring matching
   - Rationale: For in-memory console application, linear search is sufficient and simple to implement
   - Alternative considered: Indexed search (unnecessary complexity for small datasets)

4. **Sorting implementation**
   - Decision: Use Python's built-in sorted() function with custom key functions
   - Rationale: Leverages Python's efficient sorting algorithm while providing flexibility
   - Alternative considered: Custom sorting algorithms (unnecessary complexity)

5. **Console output formatting**
   - Decision: Extend existing format to include priority and tags in a clean, readable layout
   - Rationale: Maintains consistency with Basic Level while adding required information
   - Alternative considered: Separate display formats (would complicate the interface)

### Consolidated Findings

- **Decision**: Extend the existing TodoItem class with priority and tags properties
- **Rationale**: Maintains backward compatibility with Basic Level while adding required features
- **Alternatives considered**: Separate data models for enhanced items (would complicate integration)

## Phase 1: Design & Contracts

### Data Model

#### Enhanced Todo Item Entity
- **Fields**:
  - `id`: Integer (sequential, starts from 1)
  - `description`: String (the task text)
  - `completed`: Boolean (whether the task is completed)
  - `priority`: String (priority level: "high", "medium", "low")
  - `tags`: List of Strings (list of tag strings)
  - `due_date`: Optional String/Date (due date if specified)
- **Validation**:
  - Description must not be empty or whitespace-only
  - ID must be positive integer
  - Priority must be one of "high", "medium", "low"
  - Tags must be non-empty strings
- **State Transitions**:
  - `incomplete` → `completed` (via complete command)
  - `completed` → `incomplete` (via incomplete command)
  - Priority levels can be updated
  - Tags can be added/removed

#### Enhanced Todo List Entity
- **Fields**:
  - `items`: List of EnhancedTodoItem objects
- **Operations**:
  - Add new item (appends to list)
  - View all items (returns all items)
  - Update item by ID (modifies specific item)
  - Delete item by ID (removes specific item)
  - Mark complete/incomplete by ID (changes completion status)
  - Set priority by ID (sets priority level)
  - Add/remove tags by ID (manages tags)
  - Search by keyword (returns matching items)
  - Filter by criteria (returns matching items)
  - Sort by criteria (returns sorted list)

### File Structure
```
src/
└── main.py              # Enhanced application logic (extends Basic Level)
```

### API Contracts (Console Commands)

1. **Set Priority Command**: `set-priority <id> <level>`
   - Action: Sets the priority level of the item with the given ID
   - Success: Item's priority is updated to specified level (high/medium/low)
   - Error: Shows error if ID is invalid or priority level is not recognized

2. **Tag Command**: `tag <id> <tag1> [tag2] [tag3]...`
   - Action: Adds tags to the item with the given ID
   - Success: Tags are added to the item
   - Error: Shows error if ID is invalid or no tags provided

3. **Search Command**: `search <keyword>`
   - Action: Finds all items containing the keyword in their description
   - Success: Displays all matching items
   - Error: Shows "No tasks found matching '[keyword]'" if no matches

4. **Filter Command**: `filter <criteria> <value>`
   - Action: Filters items by the specified criteria (status, priority, tag)
   - Success: Displays all items matching the criteria
   - Error: Shows error if criteria or value is invalid

5. **Sort Command**: `sort <criteria>`
   - Action: Sorts items by the specified criteria (priority, alpha, due)
   - Success: Displays items in sorted order
   - Error: Shows error if criteria is invalid

6. **Original Basic Level Commands** (continue to work):
   - `add <description>`
   - `view`
   - `update <id> <new_description>`
   - `delete <id>`
   - `complete <id>`
   - `incomplete <id>`
   - `quit`

### Quickstart Guide

1. Clone the repository
2. Ensure Python 3.13+ is installed
3. Navigate to the project directory
4. Run `python src/main.py`
5. Use the available commands to manage your todo list with enhanced organization features

## Phase 2: Implementation Steps

### Step 1: Extend data model in existing main.py
- Update TodoItem class to include priority and tags properties
- Update TodoList class to include search, filter, and sort methods
- Add validation for new properties and operations

### Step 2: Implement priority functionality
- Add set_priority method to TodoList class
- Add priority validation
- Update display format to show priority levels

### Step 3: Implement tag functionality
- Add add_tag and remove_tag methods to TodoList class
- Add tag validation
- Update display format to show tags

### Step 4: Implement search functionality
- Add search method to TodoList class
- Implement case-insensitive substring matching
- Update display to handle search results

### Step 5: Implement filter functionality
- Add filter method to TodoList class
- Support filtering by status, priority, and tags
- Update display to handle filtered results

### Step 6: Implement sort functionality
- Add sort method to TodoList class
- Support sorting by priority, alphabetical, and due date
- Update display to handle sorted results

### Step 7: Update command handlers
- Add handlers for new commands (set-priority, tag, search, filter, sort)
- Update existing command handlers to maintain compatibility
- Add proper error handling for new functionality

### Step 8: Testing and validation
- Manually test all new commands
- Verify all acceptance scenarios from the specification
- Ensure Basic Level functionality remains unchanged
- Verify all success criteria are met

## Success Criteria Validation

Each of the original success criteria will be validated:
- **SC-001**: Users can assign priority levels and tags to all todo items
- **SC-002**: Users can search, filter, and sort todo lists with all specified criteria working correctly
- **SC-003**: All Basic Level functionality continues to work without degradation
- **SC-004**: Console output remains clear, readable, and predictable with enhanced information
- **SC-005**: System responds to search/filter/sort commands within 1 second