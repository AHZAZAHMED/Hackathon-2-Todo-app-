# Tasks: Phase I – Intermediate Level (Organization & Usability)

## Phase 1: Setup

- [X] T001 Update main.py to extend existing Basic Level implementation with organization features

## Phase 2: Foundational

- [X] T002 [P] Extend TodoItem class with priority and tags properties in src/main.py
- [X] T003 [P] Update TodoList class with search, filter, and sort methods in src/main.py
- [X] T004 [P] Add validation for new properties (priority, tags) in src/main.py

## Phase 3: User Story 1 - Set Task Priority (Priority: P1)

- [X] T005 [US1] Implement set_priority method in TodoList class in src/main.py
- [X] T006 [US1] Add priority validation for set-priority command in src/main.py
- [X] T007 [US1] Update display format to show priority levels in src/main.py
- [X] T008 [US1] Implement 'set-priority' command handler in src/main.py
- [X] T009 [US1] Add error handling for invalid priority levels in src/main.py
- [X] T010 [US1] Test setting priority levels on todo items in src/main.py

## Phase 4: User Story 2 - Add Task Tags/Categories (Priority: P1)

- [X] T011 [US2] Implement add_tag method in TodoList class in src/main.py
- [X] T012 [US2] Implement remove_tag method in TodoList class in src/main.py
- [X] T013 [US2] Add tag validation for tag command in src/main.py
- [X] T014 [US2] Update display format to show tags in src/main.py
- [X] T015 [US2] Implement 'tag' command handler in src/main.py
- [X] T016 [US2] Test adding tags to todo items in src/main.py
- [X] T017 [US2] Test multiple tags on a single task in src/main.py

## Phase 5: User Story 3 - Search Tasks by Keyword (Priority: P2)

- [X] T018 [US3] Implement search method in TodoList class in src/main.py
- [X] T019 [US3] Implement case-insensitive substring matching for search in src/main.py
- [X] T020 [US3] Update display to handle search results in src/main.py
- [X] T021 [US3] Implement 'search' command handler in src/main.py
- [X] T022 [US3] Add error handling for empty search terms in src/main.py
- [X] T023 [US3] Test searching for tasks by keyword in src/main.py
- [X] T024 [US3] Test case-insensitive search functionality in src/main.py

## Phase 6: User Story 4 - Filter Tasks (Priority: P2)

- [X] T025 [US4] Implement filter method in TodoList class in src/main.py
- [X] T026 [US4] Add support for filtering by status in src/main.py
- [X] T027 [US4] Add support for filtering by priority in src/main.py
- [X] T028 [US4] Add support for filtering by tags in src/main.py
- [X] T029 [US4] Update display to handle filtered results in src/main.py
- [X] T030 [US4] Implement 'filter' command handler in src/main.py
- [X] T031 [US4] Test filtering tasks by status in src/main.py
- [X] T032 [US4] Test filtering tasks by priority in src/main.py
- [X] T033 [US4] Test filtering tasks by tags in src/main.py

## Phase 7: User Story 5 - Sort Tasks (Priority: P2)

- [X] T034 [US5] Implement sort method in TodoList class in src/main.py
- [X] T035 [US5] Add support for sorting by priority in src/main.py
- [X] T036 [US5] Add support for sorting alphabetically in src/main.py
- [X] T037 [US5] Add support for sorting by due date in src/main.py
- [X] T038 [US5] Update display to handle sorted results in src/main.py
- [X] T039 [US5] Implement 'sort' command handler in src/main.py
- [X] T040 [US5] Test sorting tasks by priority in src/main.py
- [X] T041 [US5] Test sorting tasks alphabetically in src/main.py
- [X] T042 [US5] Test sorting tasks by due date in src/main.py

## Phase 8: Polish & Cross-Cutting Concerns

- [X] T043 [P] Update main application loop to handle new commands in src/main.py
- [X] T044 [P] Ensure Basic Level functionality remains unchanged in src/main.py
- [X] T045 [P] Add proper error handling for new functionality in src/main.py
- [X] T046 [P] Validate all acceptance scenarios from specification in src/main.py
- [X] T047 [P] Test combining search and filter operations in src/main.py
- [X] T048 [P] Verify console output remains clear and readable with enhanced information in src/main.py
- [X] T049 [P] Update README.md with new functionality documentation
- [X] T050 [P] Verify all success criteria are met (SC-001 to SC-005)

## Dependencies

- Foundational tasks (T002-T004) must be completed before any user story tasks
- User Story 1 (Priority) and User Story 2 (Tags) can be developed in parallel
- User Story 3 (Search) and User Story 4 (Filter) can be developed in parallel after foundational tasks
- User Story 5 (Sort) can be developed in parallel after foundational tasks
- Polish phase tasks can be completed after all user stories are functional

## Parallel Execution Examples

- Tasks T002-T004 (Foundational) can be worked on in parallel since they modify different parts of the same file
- Tasks T005-T010 (Priority) and T011-T017 (Tags) can be developed in parallel as they implement different functionality
- Tasks T018-T024 (Search) and T025-T033 (Filter) can be developed in parallel as they implement different functionality
- Tasks T034-T042 (Sort) can be developed in parallel with other user story tasks

## Implementation Strategy

1. **MVP First**: Complete User Story 1 (Set Priority) and User Story 2 (Tags) to have core organization features
2. **Incremental Delivery**: Add search, filter, and sort functionality one by one, testing each before moving to the next
3. **Test Early**: Verify acceptance scenarios after each user story is complete
4. **Polish Last**: Add error handling and cross-cutting concerns after core functionality works