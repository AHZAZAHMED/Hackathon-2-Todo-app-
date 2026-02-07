# Tasks: Phase I – Advanced Level (Overdue & Remind Logic Refinement)

## Phase 1: Setup

- [X] T001 Create pyproject.toml with project metadata for Python 3.13+ and UV compatibility
- [X] T002 Add proper Python version specification to project configuration

## Phase 2: Foundational

- [X] T003 [P] Update TodoItem class with due date and recurrence properties in src/main.py
- [X] T004 [P] Update TodoList class with overdue and due-soon detection methods in src/main.py
- [X] T005 [P] Add date validation utilities using explicit timedelta import in src/main.py

## Phase 3: User Story 1 - Overdue Detection Fix (Priority: P1)

- [X] T006 [US1] Update TodoItem.is_overdue() method to properly compare with current date in src/main.py
- [X] T007 [US1] Implement enhanced get_overdue_items() method in TodoList class in src/main.py
- [X] T008 [US1] Add validation to ensure tasks without due dates are never marked as overdue in src/main.py
- [X] T009 [US1] Update overdue command handler to use correct logic in src/main.py
- [X] T010 [US1] Test overdue detection with past due dates in src/main.py
- [X] T011 [US1] Test that tasks without due dates are not marked as overdue in src/main.py
- [X] T012 [US1] Test overdue detection with future due dates in src/main.py

**Story Goal**: Ensure tasks are marked as overdue only if they have a due date that is in the past compared to the current system date.

**Independent Test**: Can be fully tested by creating tasks with various due date states (past, future, none), running the overdue command, and verifying only tasks with past due dates are shown as overdue.

## Phase 4: User Story 2 - Remind Command Fix (Priority: P1)

- [X] T013 [US2] Implement get_due_soon_items() method in TodoList class for next 24-hour window in src/main.py
- [X] T014 [US2] Add proper date range calculation using timedelta(days=1) in src/main.py
- [X] T015 [US2] Update remind command handler to only show tasks due within 24 hours in src/main.py
- [X] T016 [US2] Add validation to exclude overdue tasks from remind results in src/main.py
- [X] T017 [US2] Add validation to exclude tasks due further than 24 hours in src/main.py
- [X] T018 [US2] Test remind functionality with tasks due within 24 hours in src/main.py
- [X] T019 [US2] Test that tasks due more than 24 hours in future are excluded from remind in src/main.py
- [X] T020 [US2] Test that overdue tasks are excluded from remind results in src/main.py

**Story Goal**: Ensure the remind command only shows tasks that are due within the next 24 hours, not all overdue tasks or tasks due further in the future.

**Independent Test**: Can be fully tested by creating tasks with various due dates (within 24h, beyond 24h, past), running the remind command, and verifying only tasks due within the next 24 hours are shown.

## Phase 5: User Story 3 - DateTime Comparison Validation (Priority: P2)

- [X] T021 [US3] Implement proper date format validation using datetime.strptime in src/main.py
- [X] T022 [US3] Add validation for set-due command to ensure correct date format in src/main.py
- [X] T023 [US3] Ensure all date arithmetic uses explicit timedelta imports (not datetime attributes) in src/main.py
- [X] T024 [US3] Add proper error handling for invalid date comparisons in src/main.py
- [X] T025 [US3] Test date validation with invalid formats in src/main.py
- [X] T026 [US3] Test date comparisons with valid formats in src/main.py
- [X] T027 [US3] Verify deterministic behavior for all date-based operations in src/main.py

**Story Goal**: Ensure datetime comparisons are performed deterministically and consistently with proper validation of date formats and arithmetic operations.

**Independent Test**: Can be fully tested by validating different date formats, boundary conditions, and ensuring consistent behavior across different system times.

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T028 [P] Update main application loop to handle refined commands in src/main.py
- [X] T029 [P] Ensure all Basic and Intermediate Level functionality remains unchanged in src/main.py
- [X] T030 [P] Add comprehensive error handling for all new datetime functionality in src/main.py
- [X] T031 [P] Validate all acceptance scenarios from specification work correctly in src/main.py
- [X] T032 [P] Test all edge cases for date operations (invalid formats, leap years, etc.) in src/main.py
- [X] T033 [P] Update README.md with new datetime functionality documentation
- [X] T034 [P] Verify all success criteria are met (SC-001 to SC-005)

## Dependencies

- Foundational tasks (T003-T005) must be completed before any user story tasks
- User Story 1 (Overdue Detection) and User Story 2 (Remind Command) can be developed in parallel
- User Story 3 (DateTime Validation) can be developed in parallel with other user stories
- Polish phase tasks can be completed after all user stories are functional

## Parallel Execution Examples

- Tasks T003-T005 (Foundational) can be worked on in parallel since they modify different parts of the same file
- Tasks T006-T012 (Overdue Detection) and T013-T020 (Remind Command) can be developed in parallel as they implement different functionality
- Tasks T021-T027 (DateTime Validation) can be developed in parallel with other user story tasks
- Tasks T028-T034 (Polish) can be developed in parallel after core functionality is implemented

## Implementation Strategy

1. **MVP First**: Complete User Story 1 (Overdue Detection) and User Story 2 (Remind Command) to have core datetime functionality
2. **Incremental Delivery**: Add validation and error handling one by one, testing each before moving to the next
3. **Test Early**: Verify acceptance scenarios after each user story is complete
4. **Polish Last**: Add error handling and cross-cutting concerns after core functionality works