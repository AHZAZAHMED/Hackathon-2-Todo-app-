# Acceptance Criteria for Integration Testing

## Spec-Based Testing Principles

### What is Spec-Based Testing?

Spec-based testing derives test cases directly from specifications, ensuring that implementation matches requirements exactly.

**Key Principles**:
- Tests validate WHAT the system should do (from specs), not HOW it does it (implementation details)
- Every requirement in the spec should have at least one test case
- Test cases should be traceable back to specific spec requirements
- Pass/fail criteria should be unambiguous and measurable

### Spec-to-Test Mapping

```
Specification Requirement → Test Case → Acceptance Criteria
```

**Example**:
```
Spec: "Users can only view and modify their own tasks"
  ↓
Test Case: "User A cannot access User B's tasks"
  ↓
Acceptance Criteria:
  - GET /api/{user_b_id}/tasks with User A's token returns 401/403
  - User A's task list does not include User B's tasks
  - Attempting to modify User B's task returns 401/403
```

## Defining Acceptance Criteria

### SMART Criteria Framework

Acceptance criteria should be:
- **Specific**: Clearly defined, no ambiguity
- **Measurable**: Can be verified with pass/fail result
- **Achievable**: Technically feasible to implement and test
- **Relevant**: Directly related to user requirements
- **Testable**: Can be validated through automated or manual testing

### Acceptance Criteria Template

```markdown
## Feature: [Feature Name]

### User Story
As a [user type]
I want to [action]
So that [benefit]

### Acceptance Criteria

#### Scenario 1: [Happy Path]
**Given** [initial context]
**When** [action performed]
**Then** [expected outcome]
**And** [additional expected outcome]

#### Scenario 2: [Error Path]
**Given** [initial context]
**When** [invalid action performed]
**Then** [expected error response]
**And** [system state unchanged]

### Technical Acceptance Criteria
- [ ] API endpoint returns correct status codes
- [ ] Response payload matches schema
- [ ] Database state reflects changes
- [ ] Authorization rules enforced
- [ ] Error messages are clear and actionable
```

### Example: Task Creation Feature

```markdown
## Feature: Task Creation

### User Story
As an authenticated user
I want to create a new task
So that I can track my todos

### Acceptance Criteria

#### Scenario 1: Successful Task Creation
**Given** I am logged in as User A
**When** I POST to /api/{user_a_id}/tasks with valid task data
**Then** I receive a 201 Created response
**And** The response contains the created task with an ID
**And** The task appears in my task list
**And** The task is persisted in the database with my user_id

#### Scenario 2: Unauthorized Task Creation
**Given** I am logged in as User A
**When** I POST to /api/{user_b_id}/tasks (different user)
**Then** I receive a 401 or 403 response
**And** No task is created in the database
**And** User B's task list is unchanged

#### Scenario 3: Invalid Task Data
**Given** I am logged in as User A
**When** I POST to /api/{user_a_id}/tasks with missing required fields
**Then** I receive a 400 Bad Request response
**And** The response contains validation error details
**And** No task is created in the database

### Technical Acceptance Criteria
- [ ] POST /api/{user_id}/tasks returns 201 on success
- [ ] Response includes: id, title, completed, createdAt, userId
- [ ] Database record created with correct user_id
- [ ] JWT token validated before processing
- [ ] user_id in URL matches user_id in JWT
- [ ] Invalid JWT returns 401
- [ ] Mismatched user_id returns 403
- [ ] Missing required fields returns 400 with error details
```

## Pass/Fail Criteria

### Clear Pass/Fail Definitions

Every test must have unambiguous pass/fail criteria.

**Good Pass/Fail Criteria**:
```python
# ✅ Clear and measurable
assert response.status_code == 201
assert "id" in response.json()
assert response.json()["title"] == "Test Task"
assert db.query(Task).filter_by(id=task_id).first() is not None
```

**Bad Pass/Fail Criteria**:
```python
# ❌ Vague and unmeasurable
assert response.status_code in [200, 201]  # Which one is correct?
assert response.json()  # What should be in the response?
assert task_created  # How do we verify this?
```

### Status Code Criteria

Define expected status codes for all scenarios:

| Scenario | Expected Status | Meaning |
|----------|----------------|---------|
| Successful creation | 201 Created | Resource created |
| Successful retrieval | 200 OK | Resource found and returned |
| Successful update | 200 OK | Resource updated |
| Successful deletion | 204 No Content | Resource deleted |
| Invalid request data | 400 Bad Request | Client error in request |
| Missing authentication | 401 Unauthorized | No valid JWT token |
| Insufficient permissions | 403 Forbidden | Valid token, wrong user |
| Resource not found | 404 Not Found | Resource doesn't exist |
| Server error | 500 Internal Server Error | Unexpected server failure |

### Response Payload Criteria

Define expected response structure:

```typescript
// Task Response Schema
interface TaskResponse {
  id: number;           // Required, positive integer
  title: string;        // Required, non-empty string
  completed: boolean;   // Required, boolean
  createdAt: string;    // Required, ISO 8601 datetime
  userId: number;       // Required, matches authenticated user
}

// Test validation
function validateTaskResponse(response: TaskResponse) {
  assert(typeof response.id === 'number' && response.id > 0);
  assert(typeof response.title === 'string' && response.title.length > 0);
  assert(typeof response.completed === 'boolean');
  assert(isValidISO8601(response.createdAt));
  assert(typeof response.userId === 'number' && response.userId > 0);
}
```

### Database State Criteria

Define expected database state after operations:

```python
def test_task_creation_persists_to_database():
    """Verify task creation persists to database."""
    # Arrange
    user = create_test_user()
    token = get_auth_token(user)

    # Act
    response = client.post(
        f"/api/{user.id}/tasks",
        json={"title": "Test Task"},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Assert - Response
    assert response.status_code == 201
    task_id = response.json()["id"]

    # Assert - Database State
    db_task = db.query(Task).filter_by(id=task_id).first()
    assert db_task is not None, "Task not found in database"
    assert db_task.title == "Test Task", "Task title mismatch"
    assert db_task.user_id == user.id, "Task user_id mismatch"
    assert db_task.completed == False, "Task should not be completed"
    assert db_task.created_at is not None, "Task created_at missing"
```

### Authorization Criteria

Define expected authorization behavior:

```python
def test_user_isolation_enforced():
    """Verify users cannot access other users' tasks."""
    # Arrange
    user_a = create_test_user(username="user_a")
    user_b = create_test_user(username="user_b")
    token_a = get_auth_token(user_a)
    token_b = get_auth_token(user_b)

    # Create task for user_b
    task_b = create_task(user_b.id, "User B Task")

    # Act - User A tries to access User B's task
    response = client.get(
        f"/api/{user_b.id}/tasks/{task_b.id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )

    # Assert - Access Denied
    assert response.status_code in [401, 403], "Should deny access"

    # Assert - Database Unchanged
    db_task = db.query(Task).filter_by(id=task_b.id).first()
    assert db_task.user_id == user_b.id, "Task ownership unchanged"
```

## Test Case Design Methodologies

### Equivalence Partitioning

Divide input data into equivalence classes and test one value from each class.

**Example: Task Title Validation**

| Equivalence Class | Example Value | Expected Result |
|-------------------|---------------|-----------------|
| Valid title (1-255 chars) | "Buy groceries" | 201 Created |
| Empty title | "" | 400 Bad Request |
| Title too long (>255 chars) | "A" * 256 | 400 Bad Request |
| Null title | null | 400 Bad Request |

```python
@pytest.mark.parametrize("title,expected_status", [
    ("Buy groceries", 201),           # Valid
    ("", 400),                         # Empty
    ("A" * 256, 400),                  # Too long
    (None, 400),                       # Null
])
def test_task_title_validation(title, expected_status):
    """Test task title validation with equivalence partitioning."""
    user = create_test_user()
    token = get_auth_token(user)

    response = client.post(
        f"/api/{user.id}/tasks",
        json={"title": title},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == expected_status
```

### Boundary Value Analysis

Test values at the boundaries of equivalence classes.

**Example: Task Title Length**

```python
@pytest.mark.parametrize("title_length,expected_status", [
    (0, 400),      # Boundary: empty
    (1, 201),      # Boundary: minimum valid
    (255, 201),    # Boundary: maximum valid
    (256, 400),    # Boundary: too long
])
def test_task_title_length_boundaries(title_length, expected_status):
    """Test task title length boundaries."""
    user = create_test_user()
    token = get_auth_token(user)

    title = "A" * title_length if title_length > 0 else ""

    response = client.post(
        f"/api/{user.id}/tasks",
        json={"title": title},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == expected_status
```

### Decision Table Testing

Test combinations of conditions and their expected outcomes.

**Example: Task Access Authorization**

| User Authenticated | User ID Matches | JWT Valid | Expected Result |
|--------------------|-----------------|-----------|-----------------|
| No | - | - | 401 Unauthorized |
| Yes | No | Yes | 403 Forbidden |
| Yes | Yes | No | 401 Unauthorized |
| Yes | Yes | Yes | 200 OK |

```python
@pytest.mark.parametrize("authenticated,user_id_matches,jwt_valid,expected_status", [
    (False, False, False, 401),  # No auth
    (True, False, True, 403),    # Wrong user
    (True, True, False, 401),    # Invalid JWT
    (True, True, True, 200),     # Valid access
])
def test_task_access_authorization(authenticated, user_id_matches, jwt_valid, expected_status):
    """Test task access authorization decision table."""
    user_a = create_test_user(username="user_a")
    user_b = create_test_user(username="user_b")
    task = create_task(user_a.id, "Test Task")

    # Determine which user to use
    request_user = user_a if user_id_matches else user_b

    # Determine token
    if not authenticated:
        token = None
    elif jwt_valid:
        token = get_auth_token(request_user)
    else:
        token = "invalid.jwt.token"

    # Make request
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = client.get(
        f"/api/{user_a.id}/tasks/{task.id}",
        headers=headers
    )

    assert response.status_code == expected_status
```

### State Transition Testing

Test state changes and transitions.

**Example: Task Completion State**

```
[Created] --complete--> [Completed] --uncomplete--> [Created]
```

```python
def test_task_completion_state_transitions():
    """Test task completion state transitions."""
    user = create_test_user()
    token = get_auth_token(user)

    # Create task (initial state: not completed)
    response = client.post(
        f"/api/{user.id}/tasks",
        json={"title": "Test Task"},
        headers={"Authorization": f"Bearer {token}"}
    )
    task_id = response.json()["id"]
    assert response.json()["completed"] == False

    # Transition: Created -> Completed
    response = client.patch(
        f"/api/{user.id}/tasks/{task_id}/complete",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["completed"] == True

    # Verify database state
    db_task = db.query(Task).filter_by(id=task_id).first()
    assert db_task.completed == True

    # Transition: Completed -> Created (toggle)
    response = client.patch(
        f"/api/{user.id}/tasks/{task_id}/complete",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["completed"] == False

    # Verify database state
    db_task = db.query(Task).filter_by(id=task_id).first()
    assert db_task.completed == False
```

### Error Guessing

Test scenarios based on experience with common errors.

**Common Error Scenarios**:
```python
def test_common_error_scenarios():
    """Test common error scenarios based on experience."""
    user = create_test_user()
    token = get_auth_token(user)

    # Error 1: SQL injection attempt
    response = client.post(
        f"/api/{user.id}/tasks",
        json={"title": "'; DROP TABLE tasks; --"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201  # Should be sanitized
    assert db.query(Task).count() > 0  # Table still exists

    # Error 2: XSS attempt
    response = client.post(
        f"/api/{user.id}/tasks",
        json={"title": "<script>alert('XSS')</script>"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    task = response.json()
    assert "<script>" not in task["title"]  # Should be escaped

    # Error 3: Very large payload
    response = client.post(
        f"/api/{user.id}/tasks",
        json={"title": "A" * 10000},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400  # Should reject

    # Error 4: Concurrent updates
    task = create_task(user.id, "Test Task")

    # Simulate concurrent updates
    response1 = client.put(
        f"/api/{user.id}/tasks/{task.id}",
        json={"title": "Update 1"},
        headers={"Authorization": f"Bearer {token}"}
    )
    response2 = client.put(
        f"/api/{user.id}/tasks/{task.id}",
        json={"title": "Update 2"},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Both should succeed (last write wins)
    assert response1.status_code == 200
    assert response2.status_code == 200

    # Verify final state
    db_task = db.query(Task).filter_by(id=task.id).first()
    assert db_task.title == "Update 2"
```

## Integration Test Checklist

### Pre-Test Checklist
- [ ] Spec requirements identified and documented
- [ ] Acceptance criteria defined for each requirement
- [ ] Test cases designed using appropriate methodology
- [ ] Test data prepared (users, tasks, etc.)
- [ ] Test environment configured (database, API, frontend)
- [ ] Authentication mechanism tested and working

### Test Execution Checklist
- [ ] All happy path scenarios pass
- [ ] All error path scenarios pass
- [ ] Authorization rules enforced correctly
- [ ] Database state verified after each operation
- [ ] Response payloads match expected schema
- [ ] Status codes match expected values
- [ ] Cross-layer integration verified (UI → API → DB)

### Post-Test Checklist
- [ ] Test data cleaned up
- [ ] Database reset to clean state
- [ ] Test results documented
- [ ] Failed tests investigated and logged
- [ ] Coverage metrics calculated
- [ ] Regression tests added for bugs found

## Traceability Matrix

Link requirements to test cases for complete coverage.

| Requirement ID | Requirement | Test Case | Status |
|----------------|-------------|-----------|--------|
| REQ-001 | User can create task | test_create_task_success | ✅ Pass |
| REQ-001 | User can create task | test_create_task_invalid_data | ✅ Pass |
| REQ-002 | User can view own tasks | test_list_tasks_success | ✅ Pass |
| REQ-003 | User cannot view other's tasks | test_user_isolation | ✅ Pass |
| REQ-004 | User can update own task | test_update_task_success | ✅ Pass |
| REQ-004 | User cannot update other's task | test_update_task_unauthorized | ✅ Pass |
| REQ-005 | User can delete own task | test_delete_task_success | ✅ Pass |
| REQ-005 | User cannot delete other's task | test_delete_task_unauthorized | ✅ Pass |
| REQ-006 | User can complete task | test_complete_task_success | ✅ Pass |
| REQ-007 | Unauthorized requests rejected | test_unauthorized_access | ✅ Pass |

## Best Practices

### Writing Effective Acceptance Criteria

1. **Use Given-When-Then format** for clarity
2. **Be specific** about expected outcomes
3. **Include both positive and negative scenarios**
4. **Define measurable success criteria**
5. **Avoid implementation details** (focus on behavior)
6. **Make criteria testable** (can be automated)
7. **Keep criteria independent** (no dependencies between criteria)

### Common Mistakes to Avoid

❌ **Vague criteria**: "System should work correctly"
✅ **Specific criteria**: "POST /api/{user_id}/tasks returns 201 with task ID"

❌ **Implementation-focused**: "Use bcrypt to hash password"
✅ **Behavior-focused**: "User password is stored securely and cannot be retrieved in plain text"

❌ **Untestable**: "System should be fast"
✅ **Testable**: "API response time < 200ms for 95th percentile"

❌ **Ambiguous**: "Error handling should be good"
✅ **Clear**: "Invalid requests return 400 with descriptive error message"

### Acceptance Criteria Review Checklist

Before finalizing acceptance criteria, verify:
- [ ] Criteria are specific and unambiguous
- [ ] Criteria are measurable (pass/fail is clear)
- [ ] Criteria cover both happy and error paths
- [ ] Criteria are testable (can be automated)
- [ ] Criteria are independent (no hidden dependencies)
- [ ] Criteria trace back to spec requirements
- [ ] Criteria define expected status codes
- [ ] Criteria define expected response payloads
- [ ] Criteria define expected database state
- [ ] Criteria define expected authorization behavior
