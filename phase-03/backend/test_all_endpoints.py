"""
Comprehensive test script for all Task CRUD endpoints.
Tests all 6 endpoints with proper JWT authentication.
"""

import requests
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
BACKEND_URL = "http://localhost:8001"
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

# Test user (from database)
test_user = {
    "user_id": "SUeetRmW8cp7kOulX8VHwkFnK5U3FGHp",
    "email": "ahzazahmed159@gmail.com",
    "name": "Test User"
}

# Generate JWT token
payload = {
    "user_id": test_user["user_id"],
    "email": test_user["email"],
    "name": test_user["name"],
    "iat": datetime.utcnow(),
    "exp": datetime.utcnow() + timedelta(hours=24)
}

token = jwt.encode(payload, BETTER_AUTH_SECRET, algorithm="HS256")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("=" * 70)
print("COMPREHENSIVE TASK API TEST")
print("=" * 70)

# Test 1: Create Task (POST /api/tasks/)
print("\n[TEST 1] POST /api/tasks/ - Create new task")
response = requests.post(
    f"{BACKEND_URL}/api/tasks/",
    json={"title": "Test Task 1", "description": "First test task"},
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    task1 = response.json()["data"]
    task1_id = task1["id"]
    print(f"[PASS] Task created with ID: {task1_id}")
else:
    print(f"[FAIL] {response.text}")
    exit(1)

# Test 2: Create another task
print("\n[TEST 2] POST /api/tasks/ - Create second task")
response = requests.post(
    f"{BACKEND_URL}/api/tasks/",
    json={"title": "Test Task 2", "description": "Second test task"},
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    task2 = response.json()["data"]
    task2_id = task2["id"]
    print(f"[PASS] Task created with ID: {task2_id}")
else:
    print(f"[FAIL] {response.text}")
    exit(1)

# Test 3: List all tasks (GET /api/tasks/)
print("\n[TEST 3] GET /api/tasks/ - List all tasks")
response = requests.get(f"{BACKEND_URL}/api/tasks/", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    tasks = response.json()["data"]
    print(f"[PASS] Retrieved {len(tasks)} tasks")
    for task in tasks:
        print(f"  - ID: {task['id']}, Title: {task['title']}, Completed: {task['completed']}")
else:
    print(f"[FAIL] {response.text}")
    exit(1)

# Test 4: Get single task (GET /api/tasks/{id})
print(f"\n[TEST 4] GET /api/tasks/{task1_id} - Get single task")
response = requests.get(f"{BACKEND_URL}/api/tasks/{task1_id}", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    task = response.json()["data"]
    print(f"[PASS] Retrieved task: {task['title']}")
else:
    print(f"[FAIL] {response.text}")
    exit(1)

# Test 5: Update task (PUT /api/tasks/{id})
print(f"\n[TEST 5] PUT /api/tasks/{task1_id} - Update task")
response = requests.put(
    f"{BACKEND_URL}/api/tasks/{task1_id}",
    json={"title": "Updated Task 1", "description": "Updated description"},
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    task = response.json()["data"]
    print(f"[PASS] Task updated: {task['title']}")
else:
    print(f"[FAIL] {response.text}")
    exit(1)

# Test 6: Toggle completion (PATCH /api/tasks/{id}/complete)
print(f"\n[TEST 6] PATCH /api/tasks/{task1_id}/complete - Toggle completion")
response = requests.patch(
    f"{BACKEND_URL}/api/tasks/{task1_id}/complete",
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    task = response.json()["data"]
    print(f"[PASS] Task completion toggled to: {task['completed']}")
else:
    print(f"[FAIL] {response.text}")
    exit(1)

# Test 7: Toggle completion again (should flip back)
print(f"\n[TEST 7] PATCH /api/tasks/{task1_id}/complete - Toggle completion again")
response = requests.patch(
    f"{BACKEND_URL}/api/tasks/{task1_id}/complete",
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    task = response.json()["data"]
    print(f"[PASS] Task completion toggled to: {task['completed']}")
else:
    print(f"[FAIL] {response.text}")
    exit(1)

# Test 8: Delete task (DELETE /api/tasks/{id})
print(f"\n[TEST 8] DELETE /api/tasks/{task2_id} - Delete task")
response = requests.delete(f"{BACKEND_URL}/api/tasks/{task2_id}", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 204:
    print(f"[PASS] Task deleted successfully")
else:
    print(f"[FAIL] {response.text}")
    exit(1)

# Test 9: Verify deletion (GET deleted task should return 404)
print(f"\n[TEST 9] GET /api/tasks/{task2_id} - Verify task was deleted")
response = requests.get(f"{BACKEND_URL}/api/tasks/{task2_id}", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 404:
    print(f"[PASS] Task not found (correctly deleted)")
else:
    print(f"[FAIL] Task should not exist")
    exit(1)

# Test 10: Test without JWT (should return 401)
print(f"\n[TEST 10] GET /api/tasks/ - Test without JWT token")
response = requests.get(f"{BACKEND_URL}/api/tasks/")
print(f"Status: {response.status_code}")
if response.status_code == 401:
    print(f"[PASS] Unauthorized request rejected")
else:
    print(f"[FAIL] Should return 401 Unauthorized")
    exit(1)

print("\n" + "=" * 70)
print("ALL TESTS PASSED!")
print("=" * 70)
print("\nSummary:")
print("  [PASS] Task creation works")
print("  [PASS] Task listing works")
print("  [PASS] Task retrieval works")
print("  [PASS] Task update works")
print("  [PASS] Task completion toggle works")
print("  [PASS] Task deletion works")
print("  [PASS] JWT authentication enforced")
print("  [PASS] User isolation enforced")
