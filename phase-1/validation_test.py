#!/usr/bin/env python3
"""
Validation test for the enhanced console todo application.
This script tests all the functionality implemented in the enhanced version.
"""

import sys
import os
import subprocess
from io import StringIO
from unittest.mock import patch

# Add src directory to path to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import TodoItem, TodoList


def test_priority_functionality():
    """Test priority setting functionality."""
    print("Testing Priority Functionality...")

    # Create a todo list
    todo_list = TodoList()

    # Add an item
    item = todo_list.add_item("Test task", "medium")
    assert item.priority == "medium", "Default priority should be medium"

    # Test setting priority
    success = todo_list.set_priority(1, "high")
    assert success, "Setting priority should succeed"
    assert todo_list.view_items()[0].priority == "high", "Priority should be updated to high"

    # Test invalid priority
    try:
        todo_list.set_priority(1, "invalid")
        assert False, "Should not accept invalid priority"
    except ValueError:
        pass  # Expected

    print("  PASS: Priority functionality works")


def test_tag_functionality():
    """Test tagging functionality."""
    print("Testing Tag Functionality...")

    todo_list = TodoList()

    # Add an item
    item = todo_list.add_item("Test task")

    # Add tags
    success = todo_list.add_tags(1, ["work", "urgent"])
    assert success, "Adding tags should succeed"
    assert "work" in todo_list.view_items()[0].tags, "Work tag should be added"
    assert "urgent" in todo_list.view_items()[0].tags, "Urgent tag should be added"

    # Add duplicate tag (should not duplicate)
    initial_count = len(todo_list.view_items()[0].tags)
    success = todo_list.add_tags(1, ["work"])  # work already exists
    assert success, "Adding existing tag should succeed"
    final_count = len(todo_list.view_items()[0].tags)
    assert initial_count == final_count, "Duplicate tags should not be added"

    # Remove tag
    success = todo_list.remove_tags(1, ["urgent"])
    assert success, "Removing tags should succeed"
    assert "urgent" not in todo_list.view_items()[0].tags, "Urgent tag should be removed"

    print("  PASS: Tag functionality works")


def test_search_functionality():
    """Test search functionality."""
    print("Testing Search Functionality...")

    todo_list = TodoList()

    # Add items with different content
    todo_list.add_item("Buy groceries", tags=["shopping"])
    todo_list.add_item("Walk the dog", tags=["pets"])
    todo_list.add_item("Finish report", tags=["work"])

    # Search by description
    results = todo_list.search_items("groceries")
    assert len(results) == 1, "Should find one item with groceries"
    assert "groceries" in results[0].description.lower(), "Result should contain groceries"

    # Search by tag
    results = todo_list.search_items("pets")
    assert len(results) >= 1, "Should find item with pets tag"

    # Case insensitive search
    results = todo_list.search_items("GROCERIES")
    assert len(results) == 1, "Should find items regardless of case"

    # Empty search should raise error
    try:
        todo_list.search_items("")
        assert False, "Should not allow empty search"
    except ValueError:
        pass  # Expected

    print("  PASS: Search functionality works")


def test_filter_functionality():
    """Test filter functionality."""
    print("Testing Filter Functionality...")

    todo_list = TodoList()

    # Add items with different priorities
    todo_list.add_item("High priority task", priority="high")
    todo_list.add_item("Medium priority task", priority="medium")
    todo_list.add_item("Low priority task", priority="low")

    # Mark one as complete
    todo_list.mark_complete(2)

    # Filter by priority
    high_priority = todo_list.filter_items("priority", "high")
    assert len(high_priority) == 1, "Should have one high priority item"
    assert high_priority[0].priority == "high", "Item should have high priority"

    # Filter by status
    completed = todo_list.filter_items("status", "complete")
    assert len(completed) == 1, "Should have one completed item"
    assert completed[0].completed, "Item should be completed"

    incomplete = todo_list.filter_items("status", "incomplete")
    assert len(incomplete) == 2, "Should have two incomplete items"

    # Filter by tag (add a tag first)
    todo_list.add_tags(1, ["important"])
    tagged_items = todo_list.filter_items("tag", "important")
    assert len(tagged_items) == 1, "Should have one item with 'important' tag"

    print("  PASS: Filter functionality works")


def test_sort_functionality():
    """Test sort functionality."""
    print("Testing Sort Functionality...")

    todo_list = TodoList()

    # Add items with different priorities
    todo_list.add_item("Medium priority", priority="medium")
    todo_list.add_item("High priority", priority="high")
    todo_list.add_item("Low priority", priority="low")

    # Sort by priority (high first)
    sorted_items = todo_list.sort_items("priority")
    assert sorted_items[0].priority == "high", "High priority should come first"
    assert sorted_items[-1].priority == "low", "Low priority should come last"

    # Sort alphabetically
    sorted_items = todo_list.sort_items("alphabetical")
    descriptions = [item.description for item in sorted_items]
    assert descriptions == sorted(descriptions, key=str.lower), "Should be sorted alphabetically"

    print("  PASS: Sort functionality works")


def test_error_handling():
    """Test error handling for edge cases."""
    print("Testing Error Handling...")

    todo_list = TodoList()

    # Add one item
    todo_list.add_item("Test task")

    # Test invalid operations
    assert not todo_list.set_priority(999, "high"), "Should not set priority on non-existent item"
    assert not todo_list.add_tags(999, ["tag"]), "Should not add tags to non-existent item"
    assert not todo_list.remove_tags(999, ["tag"]), "Should not remove tags from non-existent item"
    assert not todo_list.mark_complete(999), "Should not mark non-existent item complete"

    # Test empty operations
    try:
        todo_list.add_item("", "medium")
        assert False, "Should not add empty description"
    except ValueError:
        pass  # Expected

    print("  PASS: Error handling works")


def test_combined_operations():
    """Test combining different operations."""
    print("Testing Combined Operations...")

    todo_list = TodoList()

    # Add multiple items with different properties
    todo_list.add_item("Urgent report", priority="high", tags=["work", "urgent"])
    todo_list.add_item("Daily walk", priority="medium", tags=["health"])
    todo_list.add_item("Buy milk", priority="low", tags=["shopping"])

    # Filter by priority then sort
    high_priority = todo_list.filter_items("priority", "high")
    assert len(high_priority) == 1, "Should have one high priority item"

    # Search then filter
    search_results = todo_list.search_items("report")
    assert len(search_results) == 1, "Should find the report item"

    # Add tags to existing item
    success = todo_list.add_tags(1, ["important"])
    assert success, "Should be able to add more tags"
    assert "important" in todo_list.view_items()[0].tags, "Important tag should be added"

    print("  PASS: Combined operations work")


def main():
    """Run all validation tests."""
    print("Starting validation tests for Enhanced Console Todo App...\n")

    try:
        test_priority_functionality()
        test_tag_functionality()
        test_search_functionality()
        test_filter_functionality()
        test_sort_functionality()
        test_error_handling()
        test_combined_operations()

        print("\nPASSED: All validation tests passed!")
        print("\nImplementation Summary:")
        print("- Priority levels (high/medium/low) working correctly")
        print("- Tagging system with add/remove functionality working")
        print("- Search by keyword (case-insensitive) working")
        print("- Filter by status, priority, and tags working")
        print("- Sort by priority and alphabetically working")
        print("- Proper error handling for invalid inputs")
        print("- All features work in combination")
        print("\nThe implementation successfully meets all requirements!")

        return True

    except Exception as e:
        print(f"\nFAILED: Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)