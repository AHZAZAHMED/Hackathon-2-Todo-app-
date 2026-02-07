# Data Model: Phase I – Advanced Level (Overdue & Remind Logic Refinement)

## Enhanced Todo Item Entity

### Fields
- `id`: Integer (sequential, starts from 1)
- `description`: String (the task text)
- `completed`: Boolean (whether the task is completed)
- `priority`: String (priority level: "high", "medium", "low")
- `tags`: List of Strings (list of tag strings)
- `due_date`: Optional String (due date in 'YYYY-MM-DD' format if specified)
- `recurrence_pattern`: Optional String (recurrence: "daily", "weekly", "monthly", or None)
- `next_occurrence`: Optional String (when the next occurrence is due, for recurring tasks)

### Validation
- Description must not be empty or whitespace-only
- ID must be positive integer
- Priority must be one of "high", "medium", "low"
- Tags must be non-empty strings
- Due date must be in 'YYYY-MM-DD' format if specified
- Recurrence pattern must be valid if specified

### State Transitions
- `incomplete` → `completed` (via complete command)
- `completed` → `incomplete` (via incomplete command)
- Priority levels can be updated
- Tags can be added/removed
- Due dates can be set/cleared
- Recurring tasks generate next occurrence on completion

## Enhanced Todo List Entity

### Fields
- `items`: List of EnhancedTodoItem objects

### Operations
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
- Handle recurring tasks (reschedules on completion)
- Identify overdue items (due date < current date)
- Identify upcoming items (due date within next 24 hours)
- Validate date formats (checks for proper 'YYYY-MM-DD' format)