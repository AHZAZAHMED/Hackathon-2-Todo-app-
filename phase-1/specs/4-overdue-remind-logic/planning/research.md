# Research Findings: Phase I – Advanced Level (Overdue & Remind Logic Refinement)

## Decision: Current time retrieval approach
**Rationale**: Use `datetime.date.today()` to get current date for comparison as it provides the current date without time components that could complicate overdue calculations
**Alternative considered**: `datetime.datetime.now().date()` (similar functionality, but date.today() is more direct for date-only comparisons)

## Decision: Due date storage and parsing
**Rationale**: Store due dates as string in 'YYYY-MM-DD' format with validation using `datetime.strptime()` as it maintains consistency with existing ISO 8601 format requirement while enabling proper date comparisons
**Alternative considered**: Store as datetime objects (unnecessary complexity for in-memory storage, harder to serialize/deserialize)

## Decision: Overdue comparison implementation
**Rationale**: Compare due date with current date using proper date comparison: `due_date_obj < current_date_obj` to accurately detect overdue tasks only when due date is in the past
**Alternative considered**: Using string comparison (unreliable for date comparisons)

## Decision: Upcoming window calculation (now → now + 24 hours)
**Rationale**: Use `timedelta(days=1)` to calculate the 24-hour window for remind functionality to enable accurate detection of tasks due within the next 24 hours
**Alternative considered**: Using hardcoded time windows (less flexible than timedelta approach)

## Decision: Timedelta import approach
**Rationale**: Import timedelta explicitly as `from datetime import timedelta` and use as `timedelta(days=1)` to follow specification requirement to import timedelta explicitly and not access as attribute of datetime
**Alternative considered**: Accessing as `datetime.timedelta` (violates specification requirement)