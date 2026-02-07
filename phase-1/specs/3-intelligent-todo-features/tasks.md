# Tasks: Phase I – Advanced Level (Intelligent Features)

## Phase 1: Setup

- [X] T001 Create directory structure for advanced features implementation
- [X] T002 Set up Python project configuration with UV for package management
- [X] T003 Prepare development environment with Python 3.13+ support

## Phase 2: Foundational

- [X] T004 [P] Extend TodoItem class with due date and recurrence properties in src/main.py
- [X] T005 [P] Update TodoList class with recurring task handling methods in src/main.py
- [X] T006 [P] Add date/time parsing and validation utilities in src/main.py

## Phase 3: User Story 1 - Define Recurring Tasks (Priority: P1)

- [X] T007 [US1] Implement create_recurring_task method in TodoList class in src/main.py
- [X] T008 [US1] Add recurrence pattern validation (daily, weekly, monthly) in src/main.py
- [X] T009 [US1] Implement next occurrence calculation logic in src/main.py
- [X] T010 [US1] Update display format to show recurrence patterns in src/main.py
- [X] T011 [US1] Implement 'add-recurring' command handler in src/main.py
- [X] T012 [US1] Add error handling for invalid recurrence patterns in src/main.py
- [X] T013 [US1] Test recurring task creation and scheduling in src/main.py

**Story Goal**: Enable users to create recurring tasks that automatically reschedule after completion, such as daily habits or weekly chores, using natural language commands.

**Independent Test**: Can be fully tested by creating a recurring task with a specific rule (e.g., daily), completing it, and verifying the next occurrence is automatically scheduled.

## Phase 4: User Story 2 - Set Task Due Dates (Priority: P1)

- [X] T014 [US2] Implement set_due_date method in TodoList class in src/main.py
- [X] T015 [US2] Add due date validation and parsing in src/main.py
- [X] T016 [US2] Update display format to show due dates in src/main.py
- [X] T017 [US2] Implement 'set-due' command handler in src/main.py
- [X] T018 [US2] Add error handling for invalid date formats in src/main.py
- [X] T019 [US2] Test due date assignment and display in src/main.py
- [X] T020 [US2] Test date format validation in src/main.py

**Story Goal**: Allow users to assign due dates to tasks using natural language expressions to track deadlines and time-sensitive items with date and optional time components.

**Independent Test**: Can be fully tested by adding a task with a due date, checking for overdue status, and verifying the date is properly stored and displayed.

## Phase 5: User Story 3 - Identify Overdue Tasks (Priority: P2)

- [X] T021 [US3] Implement overdue detection logic in TodoList class in src/main.py
- [X] T022 [US3] Add current date comparison for overdue status in src/main.py
- [X] T023 [US3] Update display format to highlight overdue items in src/main.py
- [X] T024 [US3] Implement 'overdue' command handler in src/main.py
- [X] T025 [US3] Add error handling for empty overdue lists in src/main.py
- [X] T026 [US3] Test overdue identification with past due dates in src/main.py
- [X] T027 [US3] Test overdue identification with future due dates in src/main.py

**Story Goal**: Allow users to use natural language commands to see all tasks that have passed their due date to prioritize time-sensitive items that need attention.

**Independent Test**: Can be fully tested by creating tasks with past due dates and using a command to identify overdue items.

## Phase 6: User Story 4 - Trigger Reminder Checks (Priority: P2)

- [X] T028 [US4] Implement reminder check logic in TodoList class in src/main.py
- [X] T029 [US4] Add upcoming deadline detection in src/main.py
- [X] T030 [US4] Implement 'remind' command handler in src/main.py
- [X] T031 [US4] Add configurable timeframe for reminder checks in src/main.py
- [X] T032 [US4] Test reminder functionality with various due date scenarios in src/main.py
- [X] T033 [US4] Test reminder functionality with no time-sensitive tasks in src/main.py
- [X] T034 [US4] Validate reminder accuracy and determinism in src/main.py

**Story Goal**: Allow users to use natural language commands to check for upcoming due tasks or overdue items to stay organized without relying on notifications.

**Independent Test**: Can be fully tested by setting up tasks with various due dates and running the reminder check command to see which tasks require attention.

## Phase 7: User Story 5 - Search and Filter by Date/Priority (Priority: P2)

- [X] T035 [US5] Implement search method in TodoList class in src/main.py
- [X] T036 [US5] Implement keyword matching algorithm in src/main.py
- [X] T037 [US5] Implement filter method in TodoList class in src/main.py
- [X] T038 [US5] Add filtering by status, priority, and date in src/main.py
- [X] T039 [US5] Implement 'search' command handler in src/main.py
- [X] T040 [US5] Implement 'filter' command handler in src/main.py
- [X] T041 [US5] Test search functionality with various keywords in src/main.py
- [X] T042 [US5] Test filter functionality with various criteria in src/main.py
- [X] T043 [US5] Test combined search and filter operations in src/main.py

**Story Goal**: Allow users to use natural language commands to search and filter tasks by due date ranges, priority levels, and recurrence patterns to better organize their workload.

**Independent Test**: Can be fully tested by creating tasks with various due dates and priorities, then applying search and filter operations to verify only matching tasks are returned.

## Phase 8: Polish & Cross-Cutting Concerns

- [X] T044 [P] Update main application loop to handle new commands in src/main.py
- [X] T045 [P] Ensure Basic and Intermediate Level functionality remains unchanged in src/main.py
- [X] T046 [P] Add proper error handling for new functionality in src/main.py
- [X] T047 [P] Validate all acceptance scenarios from specification in src/main.py
- [X] T048 [P] Test combining search and filter operations in src/main.py
- [X] T049 [P] Verify console output remains clear and readable with enhanced information in src/main.py
- [X] T050 [P] Update README.md with new functionality documentation
- [X] T051 [P] Verify all success criteria are met (SC-001 to SC-005)

## Dependencies

- Foundational tasks (T004-T006) must be completed before any user story tasks
- User Story 1 (Recurring Tasks) and User Story 2 (Due Dates) can be developed in parallel
- User Story 3 (Overdue Detection) and User Story 4 (Reminders) can be developed in parallel after foundational tasks
- User Story 5 (Search/Filter) can be developed in parallel after foundational tasks
- Polish phase tasks can be completed after all user stories are functional

## Parallel Execution Examples

- Tasks T004-T006 (Foundational) can be worked on in parallel since they modify different parts of the same file
- Tasks T007-T013 (Recurring Tasks) and T014-T020 (Due Dates) can be developed in parallel as they implement different functionality
- Tasks T021-T027 (Overdue Detection) and T028-T034 (Reminders) can be developed in parallel as they implement different functionality
- Tasks T035-T043 (Search/Filter) can be developed in parallel with other user story tasks

## Implementation Strategy

1. **MVP First**: Complete User Story 1 (Recurring Tasks) and User Story 2 (Due Dates) to have core intelligent features
2. **Incremental Delivery**: Add overdue detection, reminders, and search/filter functionality one by one, testing each before moving to the next
3. **Test Early**: Verify acceptance scenarios after each user story is complete
4. **Polish Last**: Add error handling and cross-cutting concerns after core functionality works