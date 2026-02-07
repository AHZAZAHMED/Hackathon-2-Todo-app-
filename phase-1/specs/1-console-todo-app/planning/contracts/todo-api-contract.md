# Todo API Contract: Console Commands

## Command Specifications

### Add Command
- **Syntax**: `add <description>`
- **Action**: Creates a new todo item with the given description
- **Success Response**: Item is added to the list with next sequential ID
- **Error Response**: Shows error message if description is empty

### View Command
- **Syntax**: `view`
- **Action**: Displays all todo items with their completion status
- **Success Response**: Lists all items with [ ] or [x] for incomplete/complete
- **Error Response**: Shows "No items in your todo list" if empty

### Update Command
- **Syntax**: `update <id> <new_description>`
- **Action**: Updates the description of the item with the given ID
- **Success Response**: Updates the item's description
- **Error Response**: Shows error if ID is invalid or description is empty

### Delete Command
- **Syntax**: `delete <id>`
- **Action**: Removes the item with the given ID from the list
- **Success Response**: Removes the item from the list
- **Error Response**: Shows error if ID is invalid

### Complete Command
- **Syntax**: `complete <id>`
- **Action**: Marks the item with the given ID as completed
- **Success Response**: Sets the item's completion status to True
- **Error Response**: Shows error if ID is invalid

### Incomplete Command
- **Syntax**: `incomplete <id>`
- **Action**: Marks the item with the given ID as incomplete
- **Success Response**: Sets the item's completion status to False
- **Error Response**: Shows error if ID is invalid

### Quit Command
- **Syntax**: `quit`
- **Action**: Exits the application gracefully
- **Success Response**: Application terminates