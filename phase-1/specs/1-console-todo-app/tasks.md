# Tasks: Phase I – In-Memory Python Console Todo App

## Phase 1: Setup

- [x] T001 Create project structure with src directory
- [x] T002 Initialize Python project with proper configuration
- [x] T003 Create src/main.py file as main application entry point

## Phase 2: Foundational

- [x] T004 Define TodoItem class with id, description, and completed fields in src/main.py
- [x] T005 Define TodoList class with items list in src/main.py
- [x] T006 Implement basic command-line argument parsing in src/main.py

## Phase 3: User Story 1 - Add Todo Items (Priority: P1)

- [x] T007 [US1] Implement TodoItem constructor with validation in src/main.py
- [x] T008 [US1] Implement TodoList.add_item method in src/main.py
- [x] T009 [US1] Implement 'add' command handler in src/main.py
- [x] T010 [US1] Add validation for empty descriptions in add command in src/main.py
- [x] T011 [US1] Test adding todo items with valid input in src/main.py
- [x] T012 [US1] Test error handling for invalid add command format in src/main.py

**Story Goal**: Enable users to add new todo items to their list by typing a command in the console

**Independent Test**: Can be fully tested by running the console app, entering an "add" command with a todo description, and verifying the item appears in the list.

## Phase 4: User Story 2 - View Todo List (Priority: P1)

- [x] T013 [US2] Implement TodoList.view_items method in src/main.py
- [x] T014 [US2] Implement 'view' command handler in src/main.py
- [x] T015 [US2] Format output to show completion status ([ ] or [x]) in src/main.py
- [x] T016 [US2] Handle empty list case with appropriate message in src/main.py
- [x] T017 [US2] Test viewing todo items with multiple items in src/main.py
- [x] T018 [US2] Test viewing empty todo list in src/main.py

**Story Goal**: Allow users to see all their current todo items displayed in a clear, organized format in the console

**Independent Test**: Can be fully tested by running the console app, adding some items, and using the "view" command to see the list.

## Phase 5: User Story 3 - Update Todo Items (Priority: P2)

- [x] T019 [US3] Implement TodoList.update_item method in src/main.py
- [x] T020 [US3] Implement 'update' command handler in src/main.py
- [x] T021 [US3] Add validation for item index in update command in src/main.py
- [x] T022 [US3] Add validation for new description in update command in src/main.py
- [x] T023 [US3] Test updating existing todo item in src/main.py
- [x] T024 [US3] Test error handling for invalid indices in update command in src/main.py
- [x] T025 [US3] Test error handling for invalid command format in update command in src/main.py

**Story Goal**: Allow users to modify the text of an existing todo item by specifying its position in the list and the new text

**Independent Test**: Can be fully tested by adding an item, updating its text, and verifying the change is reflected when viewing the list.

## Phase 6: User Story 4 - Delete Todo Items (Priority: P2)

- [x] T026 [US4] Implement TodoList.delete_item method in src/main.py
- [x] T027 [US4] Implement 'delete' command handler in src/main.py
- [x] T028 [US4] Add validation for item index in delete command in src/main.py
- [x] T029 [US4] Handle empty list case for delete command in src/main.py
- [x] T030 [US4] Test deleting todo items by valid index in src/main.py
- [x] T031 [US4] Test error handling for invalid indices in delete command in src/main.py
- [x] T032 [US4] Test error handling for invalid command format in delete command in src/main.py
- [x] T033 [US4] Test error handling for deleting from empty list in src/main.py

**Story Goal**: Allow users to remove completed or unwanted todo items from their list by specifying the item's position

**Independent Test**: Can be fully tested by adding items, deleting one, and verifying it no longer appears in the list.

## Phase 7: User Story 5 - Mark Todo Items Complete/Incomplete (Priority: P2)

- [x] T034 [US5] Implement TodoList.mark_complete method in src/main.py
- [x] T035 [US5] Implement TodoList.mark_incomplete method in src/main.py
- [x] T036 [US5] Implement 'complete' command handler in src/main.py
- [x] T037 [US5] Implement 'incomplete' command handler in src/main.py
- [x] T038 [US5] Add validation for item index in completion commands in src/main.py
- [x] T039 [US5] Test marking todo items as complete in src/main.py
- [x] T040 [US5] Test marking todo items as incomplete in src/main.py
- [x] T041 [US5] Test error handling for invalid indices in completion commands in src/main.py
- [x] T042 [US5] Test error handling for invalid command format in completion commands in src/main.py
- [x] T043 [US5] Test error handling for completion commands on empty list in src/main.py

**Story Goal**: Allow users to mark todo items as completed or mark completed items as incomplete to track their progress

**Independent Test**: Can be fully tested by adding items, marking them as complete/incomplete, and seeing the status update in the view.

## Phase 8: Polish & Cross-Cutting Concerns

- [x] T044 Implement main application loop to continuously accept commands
- [x] T045 Implement 'quit' command to exit the application gracefully
- [x] T046 Add proper error handling with user-friendly messages throughout
- [x] T047 Implement index validation helper function for all commands
- [x] T048 Add validation for empty or whitespace-only descriptions
- [x] T049 Test complete application workflow with all commands
- [x] T050 Verify all acceptance scenarios from specification work correctly
- [x] T051 Update README.md with setup and usage instructions
- [x] T052 Verify application meets all success criteria (SC-001 to SC-004)

## Dependencies

- User Story 1 (Add) must be completed before User Stories 3, 4, and 5 can be properly tested
- User Story 2 (View) is needed to verify other operations work correctly
- Foundational tasks must be completed before any user story tasks

## Parallel Execution Examples

- Tasks T019-T025 (Update) can be developed in parallel with T026-T033 (Delete) as they operate on different methods
- Tasks T034-T043 (Completion) can be developed in parallel with T019-T025 (Update) as they operate on different methods
- Error handling tasks (T010, T016, T021, T022, etc.) can be implemented in parallel once the base functionality exists

## Implementation Strategy

1. **MVP First**: Complete User Story 1 (Add) and User Story 2 (View) to have a basic working application
2. **Incremental Delivery**: Add one user story at a time, testing each before moving to the next
3. **Test Early**: Verify acceptance scenarios after each user story is complete
4. **Polish Last**: Add error handling and cross-cutting concerns after core functionality works