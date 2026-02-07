# Feature Specification: Phase I – Advanced Level (Overdue & Remind Logic Refinement)

**Feature Branch**: `4-overdue-remind-logic`
**Created**: 2026-01-21
**Status**: Draft
**Input**: User description: "Project: Phase I – Advanced Level (Overdue & Remind Logic Refinement)
Continuation of: Phase I – Basic and Intermediate Console Todo Apps

Target audience:
- Claude Code implementing Advanced-level datetime logic for Phase-1 console todo app.

Focus:
- Fix overdue detection.
- Fix remind command for upcoming tasks only.

Success criteria:
- A task is marked overdue if:
  - It has a due date
  - Current system time is greater than due date
- Tasks without due dates are never overdue.
- Remind command lists only tasks due within the next 24 hours.
- Remind command never crashes.
- Datetime arithmetic is valid and deterministic.

Constraints:
- Phase-1 in-memory Python console only.
- No persistence.
- No UI or browser notifications.
- No manual code edits.
- `timedelta` must be imported explicitly and never accessed as an attribute of `datetime`.

Not building:
- Recurring logic
- Overdue reminders
- Background schedulers
- New features

Required outputs:
- Explicit datetime comparison rules.
- Explicit upcoming window logic (now → now + 24 hours).
- Acceptance tests:
  - Overdue t"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Overdue Detection Fix (Priority: P1)

A user wants to see tasks that have passed their due date properly identified as overdue, with only tasks that have due dates and are past their due date showing as overdue.

**Why this priority**: This is the foundational functionality for the overdue detection system that ensures users can identify missed deadlines accurately.

**Independent Test**: Can be fully tested by creating tasks with past due dates, running the overdue command, and verifying only tasks with due dates that are in the past are shown as overdue.

**Acceptance Scenarios**:

1. **Given** user has a task with a due date in the past, **When** user enters "overdue", **Then** the task is displayed as overdue with the appropriate overdue indicator
2. **Given** user has a task without a due date, **When** user enters "overdue", **Then** the task is not included in the overdue list
3. **Given** user has a task with a future due date, **When** user enters "overdue", **Then** the task is not included in the overdue list
4. **Given** user has multiple tasks with various due date states, **When** user enters "overdue", **Then** only tasks with past due dates are displayed

---

### User Story 2 - Remind Command Fix (Priority: P1)

A user wants to see only tasks that are due within the next 24 hours when using the remind command, not all overdue tasks or tasks due further in the future.

**Why this priority**: This ensures users get relevant, timely reminders for tasks that need immediate attention without being overwhelmed by distant due dates or all overdue items.

**Independent Test**: Can be fully tested by creating tasks with various due dates, running the remind command, and verifying only tasks due within the next 24 hours are shown.

**Acceptance Scenarios**:

1. **Given** user has tasks due within the next 24 hours, **When** user enters "remind", **Then** those tasks are displayed as requiring attention
2. **Given** user has tasks due more than 24 hours in the future, **When** user enters "remind", **Then** those tasks are not included in the results
3. **Given** user has tasks due more than 24 hours ago (highly overdue), **When** user enters "remind", **Then** those tasks are not included in the results (only upcoming tasks within 24 hours)
4. **Given** user has no tasks due within the next 24 hours, **When** user enters "remind", **Then** the system shows "No upcoming tasks due in the next 24 hours"

---

### User Story 3 - DateTime Comparison Validation (Priority: P2)

A user expects that datetime comparisons are performed deterministically and consistently, with proper validation of date formats and arithmetic operations.

**Why this priority**: This ensures reliability and predictability of the date-based functionality across different environments and inputs.

**Independent Test**: Can be fully tested by validating different date formats, boundary conditions, and ensuring consistent behavior across different system times.

**Acceptance Scenarios**:

1. **Given** user enters an invalid date format, **When** user attempts to set a due date, **Then** the system shows a clear error message with the correct format
2. **Given** user enters a valid date format, **When** user sets a due date, **Then** the date is properly stored and compared against the current system time
3. **Given** system needs to calculate date differences, **When** datetime arithmetic is performed, **Then** timedelta is imported explicitly and not accessed as an attribute of datetime
4. **Given** system compares dates, **When** date comparison is performed, **Then** the comparison is deterministic and reliable

---

### Edge Cases

- What happens when a task has an invalid date format in its due date field?
- How does the system handle timezone considerations when comparing dates?
- What occurs when the system clock is adjusted (daylight saving, manual adjustment)?
- How does the system handle date comparisons during leap years?
- What happens when datetime calculations result in invalid dates (e.g., February 30)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST mark a task as overdue only if it has a due date AND the current system time is greater than the due date
- **FR-002**: System MUST never mark tasks without due dates as overdue
- **FR-003**: Remind command MUST only list tasks due within the next 24 hours (not overdue tasks or tasks due further in the future)
- **FR-004**: System MUST validate all date inputs to ensure they follow the required format (YYYY-MM-DD)
- **FR-005**: System MUST handle datetime arithmetic using explicit timedelta imports (not as attributes of datetime)
- **FR-006**: System MUST provide clear error messages when date comparisons fail or invalid dates are encountered
- **FR-007**: System MUST maintain deterministic behavior for all date-based operations regardless of execution time
- **FR-008**: System MUST ensure the remind command never crashes when encountering date issues
- **FR-009**: System MUST properly handle edge cases in date calculations (month boundaries, leap years, etc.)
- **FR-010**: System MUST continue to support all existing Basic and Intermediate Level functionality unchanged

### Key Entities *(include if feature involves data)*

- **Datetime Validator**: Component responsible for validating date formats and performing date arithmetic operations using explicit timedelta imports
- **Overdue Detector**: Component that determines which tasks are overdue based on due dates and current system time
- **Reminder Checker**: Component that identifies tasks due within the next 24 hours for the remind command

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All tasks with past due dates are correctly identified as overdue with 100% accuracy (tasks without due dates are never marked as overdue)
- **SC-002**: The remind command only returns tasks due within the next 24 hours with 100% accuracy (no overdue tasks or tasks due further in the future)
- **SC-003**: All date comparisons are performed deterministically and reliably without crashing
- **SC-004**: DateTime arithmetic operations use explicit timedelta imports with no usage of datetime attributes
- **SC-005**: System handles all edge cases for date operations (invalid formats, leap years, month boundaries) gracefully without errors