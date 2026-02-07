# Data Model: Phase I – Intermediate Level (Organization & Usability)

## Enhanced Todo Item Entity

### Fields
- `id`: Integer (sequential, starts from 1)
- `description`: String (the task text)
- `completed`: Boolean (whether the task is completed)
- `priority`: String (priority level: "high", "medium", "low")
- `tags`: List of Strings (list of tag strings)
- `due_date`: Optional String/Date (due date if specified)

### Validation
- Description must not be empty or whitespace-only
- ID must be positive integer
- Priority must be one of "high", "medium", "low"
- Tags must be non-empty strings

### State Transitions
- `incomplete` → `completed` (via complete command)
- `completed` → `incomplete` (via incomplete command)
- Priority levels can be updated
- Tags can be added/removed

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