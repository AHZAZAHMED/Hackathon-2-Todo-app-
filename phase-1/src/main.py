#!/usr/bin/env python3
"""
Console Todo Application
Phase I – In-Memory Python Console Todo App
"""

import sys
from typing import List, Optional


from datetime import datetime, date, timedelta
import re


class TodoItem:
    """
    Represents a single todo item with id, description, completion status, priority, tags, due date, and recurrence pattern.
    """

    def __init__(self, id: int, description: str, completed: bool = False, priority: str = "medium", tags: List[str] = None, due_date: Optional[str] = None, recurrence_pattern: Optional[str] = None, next_occurrence: Optional[str] = None):
        if not description or description.strip() == "":
            raise ValueError("Description cannot be empty or whitespace-only")
        if id <= 0:
            raise ValueError("ID must be a positive integer")

        # Validate priority
        if priority not in ["high", "medium", "low"]:
            raise ValueError("Priority must be one of 'high', 'medium', or 'low'")

        # Validate tags
        if tags is None:
            tags = []
        else:
            for tag in tags:
                if not tag or tag.strip() == "":
                    raise ValueError("Tags cannot be empty or whitespace-only")

        # Validate recurrence pattern if provided
        if recurrence_pattern is not None:
            if recurrence_pattern not in ["daily", "weekly", "monthly"]:
                raise ValueError("Recurrence pattern must be one of 'daily', 'weekly', or 'monthly'")

        # Validate due date format if provided
        if due_date is not None:
            if not self._is_valid_date_format(due_date):
                raise ValueError("Due date must be in YYYY-MM-DD format")

        self.id = id
        self.description = description.strip()
        self.completed = completed
        self.priority = priority
        self.tags = tags
        self.due_date = due_date
        self.recurrence_pattern = recurrence_pattern
        self.next_occurrence = next_occurrence

    @staticmethod
    def _is_valid_date_format(date_str: str) -> bool:
        """Validate that date string is in YYYY-MM-DD format."""
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(pattern, date_str):
            return False

        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def is_overdue(self) -> bool:
        """Check if the task is overdue based on due date."""
        if self.due_date is None or self.completed:
            return False

        try:
            due = datetime.strptime(self.due_date, '%Y-%m-%d').date()
            today = date.today()
            return due < today
        except ValueError:
            return False  # If date parsing fails, consider not overdue

    def __str__(self):
        """Return a string representation of the todo item for display."""
        status = "[x]" if self.completed else "[ ]"
        priority_str = self.priority.upper()[0]  # First letter: H, M, L
        tags_str = ""
        if self.tags:
            tags_str = f" [{', '.join(self.tags)}]"

        # Add due date info if present
        due_str = ""
        if self.due_date:
            if self.is_overdue():
                due_str = f" (DUE:{self.due_date}*OVERDUE*)"
            else:
                due_str = f" (DUE:{self.due_date})"

        # Add recurrence info if present
        recurrence_str = ""
        if self.recurrence_pattern:
            recurrence_str = f" [RECURRING:{self.recurrence_pattern.upper()}]"

        return f"{self.id}. {status} [{priority_str}] {self.description}{due_str}{recurrence_str}{tags_str}"


def validate_date_format(date_str: str) -> bool:
    """Validate date format externally for use in command handlers."""
    return TodoItem._is_valid_date_format(date_str)


def get_current_date() -> date:
    """Get the current date for comparison operations."""
    return date.today()


def is_overdue_check(due_date_str: str) -> bool:
    """Check if a given date string represents an overdue date."""
    if not due_date_str:
        return False

    try:
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        current_date = get_current_date()
        return due_date < current_date
    except ValueError:
        return False  # If date parsing fails, consider not overdue


def get_tasks_due_soon(todo_list, days_ahead: int = 1) -> List[TodoItem]:
    """Get tasks due within the specified number of days (default 1 day for 24-hour window)."""
    due_soon_items = []
    today = get_current_date()
    future_date = today + timedelta(days=days_ahead)

    for item in todo_list.items:
        if item.due_date and not item.completed:
            try:
                due_date = datetime.strptime(item.due_date, '%Y-%m-%d').date()
                # Check if due date is between today and future_date (inclusive)
                if today <= due_date <= future_date:
                    due_soon_items.append(item)
            except ValueError:
                continue  # Skip items with invalid due dates

    return due_soon_items


class TodoList:
    """
    Collection of todo items maintained in-memory during application runtime.
    """

    def __init__(self):
        self.items: List[TodoItem] = []
        self.next_id = 1

    def add_item(self, description: str, priority: str = "medium", tags: List[str] = None) -> TodoItem:
        """Add a new todo item to the list."""
        if not description or description.strip() == "":
            raise ValueError("Description cannot be empty or whitespace-only")

        # Validate priority
        if priority not in ["high", "medium", "low"]:
            raise ValueError("Priority must be one of 'high', 'medium', or 'low'")

        # Validate tags
        if tags is None:
            tags = []
        else:
            for tag in tags:
                if not tag or tag.strip() == "":
                    raise ValueError("Tags cannot be empty or whitespace-only")

        item = TodoItem(self.next_id, description, priority=priority, tags=tags)
        self.items.append(item)
        self.next_id += 1
        return item

    def view_items(self) -> List[TodoItem]:
        """Return all todo items in the list."""
        return self.items

    def update_item(self, item_id: int, new_description: str = None, new_priority: str = None, new_tags: List[str] = None) -> bool:
        """Update the description, priority, or tags of an existing todo item."""
        item = self._get_item_by_id(item_id)
        if not item:
            return False

        # Update description if provided
        if new_description is not None:
            if not new_description or new_description.strip() == "":
                raise ValueError("Description cannot be empty or whitespace-only")
            item.description = new_description.strip()

        # Update priority if provided
        if new_priority is not None:
            if new_priority not in ["high", "medium", "low"]:
                raise ValueError("Priority must be one of 'high', 'medium', or 'low'")
            item.priority = new_priority

        # Update tags if provided
        if new_tags is not None:
            for tag in new_tags:
                if not tag or tag.strip() == "":
                    raise ValueError("Tags cannot be empty or whitespace-only")
            item.tags = new_tags

        return True

    def delete_item(self, item_id: int) -> bool:
        """Remove a todo item from the list."""
        item = self._get_item_by_id(item_id)
        if item:
            self.items.remove(item)
            # Renumber remaining items to maintain sequential IDs
            for i, item in enumerate(self.items[item_id-1:], start=item_id):
                item.id = i
            self._renumber_items()
            return True
        return False

    def mark_complete(self, item_id: int) -> bool:
        """Mark a todo item as completed."""
        item = self._get_item_by_id(item_id)
        if item:
            item.completed = True

            # If this is a recurring task, schedule the next occurrence
            if item.recurrence_pattern:
                self._schedule_next_occurrence(item)

            return True
        return False

    def mark_incomplete(self, item_id: int) -> bool:
        """Mark a todo item as incomplete."""
        item = self._get_item_by_id(item_id)
        if item:
            item.completed = False
            return True
        return False

    def set_priority(self, item_id: int, priority: str) -> bool:
        """Set the priority of a todo item."""
        if priority not in ["high", "medium", "low"]:
            raise ValueError("Priority must be one of 'high', 'medium', or 'low'")

        item = self._get_item_by_id(item_id)
        if item:
            item.priority = priority
            return True
        return False

    def add_tags(self, item_id: int, tags: List[str]) -> bool:
        """Add tags to a todo item."""
        for tag in tags:
            if not tag or tag.strip() == "":
                raise ValueError("Tags cannot be empty or whitespace-only")

        item = self._get_item_by_id(item_id)
        if item:
            # Add tags without duplication
            for tag in tags:
                if tag not in item.tags:
                    item.tags.append(tag)
            return True
        return False

    def remove_tags(self, item_id: int, tags_to_remove: List[str]) -> bool:
        """Remove tags from a todo item."""
        item = self._get_item_by_id(item_id)
        if item:
            for tag in tags_to_remove:
                if tag in item.tags:
                    item.tags.remove(tag)
            return True
        return False

    def search_items(self, keyword: str) -> List[TodoItem]:
        """Search for todo items containing the keyword in description, tags, or other fields."""
        if not keyword:
            raise ValueError("Keyword cannot be empty")

        keyword_lower = keyword.lower()
        matching_items = []

        for item in self.items:
            # Search in description
            if keyword_lower in item.description.lower():
                if item not in matching_items:  # Avoid duplicates
                    matching_items.append(item)
                continue

            # Search in tags
            for tag in item.tags:
                if keyword_lower in tag.lower():
                    if item not in matching_items:  # Avoid duplicates
                        matching_items.append(item)
                    break

        return matching_items

    def filter_items(self, criteria: str, value: str) -> List[TodoItem]:
        """Filter todo items by criteria and value."""
        filtered_items = []

        for item in self.items:
            if criteria == "status":
                if value == "complete" and item.completed:
                    filtered_items.append(item)
                elif value == "incomplete" and not item.completed:
                    filtered_items.append(item)
            elif criteria == "priority":
                if value in ["high", "medium", "low"] and item.priority == value:
                    filtered_items.append(item)
            elif criteria == "tag":
                if value in item.tags:
                    filtered_items.append(item)

        return filtered_items

    def sort_items(self, criteria: str) -> List[TodoItem]:
        """Sort todo items by criteria."""
        if criteria == "priority":
            # Define priority order: high > medium > low
            priority_order = {"high": 0, "medium": 1, "low": 2}
            return sorted(self.items, key=lambda x: priority_order[x.priority])
        elif criteria == "alpha" or criteria == "alphabetical":
            return sorted(self.items, key=lambda x: x.description.lower())
        elif criteria == "due":
            # For due date sorting, sort by due date if available, with items without due dates at the end
            return sorted(self.items, key=lambda x: (x.due_date is None, x.due_date))
        else:
            # Default to returning items as-is if criteria not recognized
            return self.items[:]

    def add_recurring_task(self, description: str, recurrence_pattern: str, priority: str = "medium", tags: List[str] = None) -> TodoItem:
        """Add a new recurring task that will reschedule after completion."""
        if recurrence_pattern not in ["daily", "weekly", "monthly"]:
            raise ValueError("Recurrence pattern must be one of 'daily', 'weekly', or 'monthly'")

        item = TodoItem(
            id=self.next_id,
            description=description,
            priority=priority,
            tags=tags,
            recurrence_pattern=recurrence_pattern
        )
        self.items.append(item)
        self.next_id += 1
        return item

    def set_due_date(self, item_id: int, due_date: str) -> bool:
        """Set the due date of a todo item."""
        if not validate_date_format(due_date):
            raise ValueError("Due date must be in YYYY-MM-DD format")

        item = self._get_item_by_id(item_id)
        if item:
            item.due_date = due_date
            return True
        return False

    def get_overdue_items(self) -> List[TodoItem]:
        """Get all items that are past their due date and not completed."""
        overdue_items = []
        for item in self.items:
            if item.due_date and not item.completed:
                try:
                    due_date = datetime.strptime(item.due_date, '%Y-%m-%d').date()
                    current_date = date.today()
                    if due_date < current_date:
                        overdue_items.append(item)
                except ValueError:
                    continue  # Skip items with invalid due dates
        return overdue_items

    def get_due_soon_items(self, days_ahead: int = 1) -> List[TodoItem]:
        """Get tasks due within the specified number of days (default 1 day for 24-hour window)."""
        due_soon_items = []
        today = date.today()
        future_date = today + timedelta(days=days_ahead)

        for item in self.items:
            if item.due_date and not item.completed:
                try:
                    due_date = datetime.strptime(item.due_date, '%Y-%m-%d').date()
                    # Check if due date is between today and future_date (inclusive)
                    if today <= due_date <= future_date:
                        due_soon_items.append(item)
                except ValueError:
                    continue  # Skip items with invalid due dates

        return due_soon_items

    def _get_item_by_id(self, item_id: int) -> Optional[TodoItem]:
        """Get a todo item by its ID."""
        if item_id <= 0 or item_id > len(self.items):
            return None

        # Since IDs should match their position in the list (1-indexed),
        # we look for the item with the given ID
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def _renumber_items(self):
        """Renumber all items to maintain sequential IDs after deletions."""
        for i, item in enumerate(self.items, start=1):
            item.id = i
        self.next_id = len(self.items) + 1

    def _schedule_next_occurrence(self, item: TodoItem):
        """Schedule the next occurrence of a recurring task based on its pattern."""
        if not item.recurrence_pattern:
            return

        current_date = date.today()

        if item.recurrence_pattern == "daily":
            next_date = current_date + timedelta(days=1)
        elif item.recurrence_pattern == "weekly":
            next_date = current_date + timedelta(weeks=1)
        elif item.recurrence_pattern == "monthly":
            # Handle month overflow (e.g., Jan 31 + 1 month = Feb 28/29)
            next_month = current_date.month + 1
            next_year = current_date.year
            if next_month > 12:
                next_month = 1
                next_year += 1

            # Handle month-end edge cases (e.g., Jan 31 -> Feb 28)
            try:
                next_date = current_date.replace(year=next_year, month=next_month)
            except ValueError:  # Day doesn't exist in target month
                # Move to last day of target month
                if next_month == 2:  # February
                    if next_year % 4 == 0 and (next_year % 100 != 0 or next_year % 400 == 0):
                        day = 29  # Leap year
                    else:
                        day = 28
                elif next_month in [4, 6, 9, 11]:  # April, June, Sept, Nov
                    day = 30
                else:  # Rest have 31 days
                    day = 31

                # Find the last day of the target month
                import calendar
                max_day = calendar.monthrange(next_year, next_month)[1]
                day = min(day, max_day)

                next_date = current_date.replace(year=next_year, month=next_month, day=day)

        # Create a new instance of the same task with next occurrence date
        new_item = TodoItem(
            id=self.next_id,
            description=item.description,
            priority=item.priority,
            tags=item.tags.copy(),
            recurrence_pattern=item.recurrence_pattern,
            due_date=next_date.strftime('%Y-%m-%d')  # Set the due date to the next occurrence
        )
        self.items.append(new_item)
        self.next_id += 1


def validate_index(todo_list: TodoList, item_id: int) -> bool:
    """Validate if the given item ID is valid for the current todo list."""
    if item_id <= 0:
        return False
    if item_id > len(todo_list.view_items()):
        return False
    return True


def handle_add_command(todo_list: TodoList, args: List[str]) -> str:
    """Handle the 'add' command to add a new todo item."""
    if len(args) < 2:
        raise ValueError("Add command requires a description. Usage: add <description>")

    description = " ".join(args[1:])
    try:
        todo_list.add_item(description)
        return f"Added: {description}"
    except ValueError as e:
        return f"Error: {str(e)}"


def handle_view_command(todo_list: TodoList) -> str:
    """Handle the 'view' command to display all todo items."""
    items = todo_list.view_items()
    if not items:
        return "No items in your todo list"

    output_lines = []
    for item in items:
        output_lines.append(str(item))
    return "\n".join(output_lines)


def handle_update_command(todo_list: TodoList, args: List[str]) -> str:
    """Handle the 'update' command to modify an existing todo item."""
    if len(args) < 3:
        raise ValueError("Update command requires an ID and new description. Usage: update <id> <new_description>")

    try:
        item_id = int(args[1])
        if not validate_index(todo_list, item_id):
            return f"Error: Invalid item ID '{item_id}'. Please provide a valid item number."

        new_description = " ".join(args[2:])
        if not new_description or new_description.strip() == "":
            raise ValueError("Description cannot be empty or whitespace-only")

        success = todo_list.update_item(item_id, new_description)
        if success:
            return f"Updated item {item_id} to: {new_description}"
        else:
            return f"Error: Could not update item {item_id}. Item not found."
    except ValueError as e:
        if "invalid literal for int()" in str(e):
            return f"Error: Invalid item ID '{args[1]}'. Please provide a valid number."
        else:
            return f"Error: {str(e)}"


def handle_delete_command(todo_list: TodoList, args: List[str]) -> str:
    """Handle the 'delete' command to remove a todo item."""
    if len(args) < 2:
        raise ValueError("Delete command requires an ID. Usage: delete <id>")

    try:
        item_id = int(args[1])
        if not validate_index(todo_list, item_id):
            return f"Error: Invalid item ID '{item_id}'. Please provide a valid item number."

        items_before = len(todo_list.view_items())
        success = todo_list.delete_item(item_id)
        if success:
            return f"Deleted item {item_id}"
        else:
            return f"Error: Could not delete item {item_id}. Item not found."
    except ValueError as e:
        if "invalid literal for int()" in str(e):
            return f"Error: Invalid item ID '{args[1]}'. Please provide a valid number."
        else:
            return f"Error: {str(e)}"


def handle_complete_command(todo_list: TodoList, args: List[str]) -> str:
    """Handle the 'complete' command to mark an item as completed."""
    if len(args) < 2:
        raise ValueError("Complete command requires an ID. Usage: complete <id>")

    try:
        item_id = int(args[1])
        if not validate_index(todo_list, item_id):
            return f"Error: Invalid item ID '{item_id}'. Please provide a valid item number."

        success = todo_list.mark_complete(item_id)
        if success:
            return f"Marked item {item_id} as complete"
        else:
            return f"Error: Could not mark item {item_id} as complete. Item not found."
    except ValueError as e:
        if "invalid literal for int()" in str(e):
            return f"Error: Invalid item ID '{args[1]}'. Please provide a valid number."
        else:
            return f"Error: {str(e)}"


def handle_incomplete_command(todo_list: TodoList, args: List[str]) -> str:
    """Handle the 'incomplete' command to mark an item as incomplete."""
    if len(args) < 2:
        raise ValueError("Incomplete command requires an ID. Usage: incomplete <id>")

    try:
        item_id = int(args[1])
        if not validate_index(todo_list, item_id):
            return f"Error: Invalid item ID '{item_id}'. Please provide a valid item number."

        success = todo_list.mark_incomplete(item_id)
        if success:
            return f"Marked item {item_id} as incomplete"
        else:
            return f"Error: Could not mark item {item_id} as incomplete. Item not found."
    except ValueError as e:
        if "invalid literal for int()" in str(e):
            return f"Error: Invalid item ID '{args[1]}'. Please provide a valid number."
        else:
            return f"Error: {str(e)}"


def handle_set_priority_command(todo_list: TodoList, args: List[str]) -> str:
    """Handle the 'set-priority' command to set priority level of an item."""
    if len(args) < 3:
        raise ValueError("Set-priority command requires an ID and priority level. Usage: set-priority <id> <level>")

    try:
        item_id = int(args[1])
        if not validate_index(todo_list, item_id):
            return f"Error: Invalid item ID '{item_id}'. Please provide a valid item number."

        priority_level = args[2].lower()
        if priority_level not in ["high", "medium", "low"]:
            return f"Error: Invalid priority level '{priority_level}'. Valid options are: high, medium, low"

        success = todo_list.set_priority(item_id, priority_level)
        if success:
            return f"Set priority of item {item_id} to {priority_level}"
        else:
            return f"Error: Could not set priority of item {item_id}. Item not found."
    except ValueError as e:
        if "invalid literal for int()" in str(e):
            return f"Error: Invalid item ID '{args[1]}'. Please provide a valid number."
        else:
            return f"Error: {str(e)}"


def handle_tag_command(todo_list: TodoList, args: List[str]) -> str:
    """Handle the 'tag' command to add tags to an item."""
    if len(args) < 3:
        raise ValueError("Tag command requires an ID and at least one tag. Usage: tag <id> <tag1> [tag2] [tag3]...")

    try:
        item_id = int(args[1])
        if not validate_index(todo_list, item_id):
            return f"Error: Invalid item ID '{item_id}'. Please provide a valid item number."

        tags = args[2:]  # All remaining arguments are tags
        for tag in tags:
            if not tag or tag.strip() == "":
                raise ValueError("Tags cannot be empty or whitespace-only")

        success = todo_list.add_tags(item_id, tags)
        if success:
            return f"Added tags {', '.join([f'{t}' for t in tags])} to item {item_id}"
        else:
            return f"Error: Could not add tags to item {item_id}. Item not found."
    except ValueError as e:
        if "invalid literal for int()" in str(e):
            return f"Error: Invalid item ID '{args[1]}'. Please provide a valid number."
        else:
            return f"Error: {str(e)}"


def handle_search_command(todo_list: TodoList, args: List[str]) -> str:
    """Handle the 'search' command to search for items by keyword."""
    if len(args) < 2:
        raise ValueError("Search command requires a keyword. Usage: search <keyword>")

    try:
        keyword = " ".join(args[1:])  # Join all remaining arguments as the keyword
        if not keyword or keyword.strip() == "":
            return "Error: Search keyword cannot be empty. Please provide a search term."

        results = todo_list.search_items(keyword.strip())
        if results:
            output_lines = []
            for item in results:
                output_lines.append(str(item))
            return "\n".join(output_lines)
        else:
            return f"No tasks found matching '{keyword}'"
    except ValueError as e:
        return f"Error: {str(e)}"


def handle_filter_command(todo_list: TodoList, args: List[str]) -> str:
    """Handle the 'filter' command to filter items by criteria."""
    if len(args) < 3:
        raise ValueError("Filter command requires criteria and value. Usage: filter <criteria> <value>")

    try:
        criteria = args[1].lower()
        value = args[2].lower()

        # Validate criteria and value
        valid_criteria = ["status", "priority", "tag"]
        if criteria not in valid_criteria:
            return f"Error: Invalid criteria '{criteria}'. Valid options are: {', '.join(valid_criteria)}"

        if criteria == "status" and value not in ["complete", "incomplete"]:
            return f"Error: Invalid status value '{value}'. Valid options are: complete, incomplete"
        elif criteria == "priority" and value not in ["high", "medium", "low"]:
            return f"Error: Invalid priority value '{value}'. Valid options are: high, medium, low"

        results = todo_list.filter_items(criteria, value)
        if results:
            output_lines = []
            for item in results:
                output_lines.append(str(item))
            return "\n".join(output_lines)
        else:
            return f"No tasks found matching filter: {criteria}={value}"
    except ValueError as e:
        return f"Error: {str(e)}"


def handle_sort_command(todo_list: TodoList, args: List[str]) -> str:
    """Handle the 'sort' command to sort items by criteria."""
    if len(args) < 2:
        raise ValueError("Sort command requires criteria. Usage: sort <criteria>")

    try:
        criteria = args[1].lower()
        valid_criteria = ["priority", "alpha", "alphabetical", "due"]

        if criteria not in valid_criteria:
            return f"Error: Invalid sort criteria '{criteria}'. Valid options are: {' '.join(valid_criteria)}"

        # Normalize 'alpha' to 'alphabetical' for consistency
        normalized_criteria = "alphabetical" if criteria == "alpha" else criteria

        results = todo_list.sort_items(normalized_criteria)
        if results:
            output_lines = []
            for item in results:
                output_lines.append(str(item))
            return "\n".join(output_lines)
        else:
            # Even if list is empty, we return an empty list
            items = todo_list.view_items()
            if not items:
                return "No items in your todo list"
            else:
                output_lines = []
                for item in items:  # Show all items if sorting doesn't filter them
                    output_lines.append(str(item))
                return "\n".join(output_lines)
    except ValueError as e:
        return f"Error: {str(e)}"


def handle_add_recurring_command(todo_list: TodoList, args: List[str]) -> str:
    """Handle the 'add-recurring' command to add a recurring todo item."""
    if len(args) < 3:
        raise ValueError("Add-recurring command requires a pattern and description. Usage: add-recurring <pattern> <description>")

    try:
        pattern = args[1].lower()
        if pattern not in ["daily", "weekly", "monthly"]:
            return f"Error: Invalid recurrence pattern '{pattern}'. Valid options are: daily, weekly, monthly"

        description = " ".join(args[2:])
        if not description or description.strip() == "":
            raise ValueError("Description cannot be empty or whitespace-only")

        item = todo_list.add_recurring_task(description, pattern)
        return f"Added recurring task: {description} ({pattern} recurrence)"
    except ValueError as e:
        return f"Error: {str(e)}"


def handle_set_due_command(todo_list: TodoList, args: List[str]) -> str:
    """Handle the 'set-due' command to set due date for a task."""
    if len(args) < 3:
        raise ValueError("Set-due command requires an ID and date. Usage: set-due <id> <YYYY-MM-DD>")

    try:
        item_id = int(args[1])
        if not validate_index(todo_list, item_id):
            return f"Error: Invalid item ID '{item_id}'. Please provide a valid item number."

        due_date = args[2]
        if not validate_date_format(due_date):
            return f"Error: Invalid date format '{due_date}'. Please use YYYY-MM-DD format."

        success = todo_list.set_due_date(item_id, due_date)
        if success:
            return f"Set due date for item {item_id} to {due_date}"
        else:
            return f"Error: Could not set due date for item {item_id}. Item not found."
    except ValueError as e:
        if "invalid literal for int()" in str(e):
            return f"Error: Invalid item ID '{args[1]}'. Please provide a valid number."
        else:
            return f"Error: {str(e)}"


def handle_overdue_command(todo_list: TodoList) -> str:
    """Handle the 'overdue' command to show all overdue tasks."""
    overdue_items = todo_list.get_overdue_items()

    if overdue_items:
        output_lines = []
        for item in overdue_items:
            output_lines.append(str(item))
        return "\n".join(output_lines)
    else:
        return "No overdue tasks"


def handle_remind_command(todo_list: TodoList) -> str:
    """Handle the 'remind' command to check for upcoming deadlines and overdue items."""
    # For the remind command, we only want tasks due within the next 24 hours (1 day)
    due_soon_items = todo_list.get_due_soon_items(1)  # Only next 1 day

    if due_soon_items:
        output_lines = []
        for item in due_soon_items:
            output_lines.append(str(item))
        return "\n".join(output_lines)
    else:
        return "No upcoming tasks due in the next 24 hours"


def main():
    """Main application loop to handle user commands."""
    todo_list = TodoList()

    print("Welcome to the Enhanced Todo App!")
    print("Available commands: add, view, update, delete, complete, incomplete, set-priority, tag, search, filter, sort, add-recurring, set-due, overdue, remind, quit")

    while True:
        try:
            # Get user input
            user_input = input("\nEnter command: ").strip()

            if not user_input:
                print("Please enter a command.")
                continue

            # Parse the command
            args = user_input.split()
            command = args[0].lower()

            # Handle different commands
            if command == "add":
                result = handle_add_command(todo_list, args)
                print(result)

            elif command == "view":
                result = handle_view_command(todo_list)
                print(result)

            elif command == "update":
                result = handle_update_command(todo_list, args)
                print(result)

            elif command == "delete":
                result = handle_delete_command(todo_list, args)
                print(result)

            elif command == "complete":
                result = handle_complete_command(todo_list, args)
                print(result)

            elif command == "incomplete":
                result = handle_incomplete_command(todo_list, args)
                print(result)

            elif command == "set-priority":
                result = handle_set_priority_command(todo_list, args)
                print(result)

            elif command == "tag":
                result = handle_tag_command(todo_list, args)
                print(result)

            elif command == "search":
                result = handle_search_command(todo_list, args)
                print(result)

            elif command == "filter":
                result = handle_filter_command(todo_list, args)
                print(result)

            elif command == "sort":
                result = handle_sort_command(todo_list, args)
                print(result)

            elif command == "add-recurring":
                result = handle_add_recurring_command(todo_list, args)
                print(result)

            elif command == "set-due":
                result = handle_set_due_command(todo_list, args)
                print(result)

            elif command == "overdue":
                result = handle_overdue_command(todo_list)
                print(result)

            elif command == "remind":
                result = handle_remind_command(todo_list)
                print(result)

            elif command == "quit":
                print("Goodbye!")
                break

            else:
                print(f"Unknown command: {command}. Available commands: add, view, update, delete, complete, incomplete, set-priority, tag, search, filter, sort, add-recurring, set-due, overdue, remind, quit")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()