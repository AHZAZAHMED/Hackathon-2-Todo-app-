# Data Model: Phase I – In-Memory Python Console Todo App

## Todo Item Entity

### Fields
- `id`: Integer (sequential, starts from 1)
- `description`: String (the task text)
- `completed`: Boolean (whether the task is completed)

### Validation
- Description must not be empty or whitespace-only
- ID must be positive integer

### State Transitions
- `incomplete` → `completed` (via complete command)
- `completed` → `incomplete` (via incomplete command)

## Todo List Entity

### Fields
- `items`: List of TodoItem objects

### Operations
- Add new item (appends to list)
- View all items (returns all items)
- Update item by ID (modifies specific item)
- Delete item by ID (removes specific item)
- Mark complete/incomplete by ID (changes completion status)