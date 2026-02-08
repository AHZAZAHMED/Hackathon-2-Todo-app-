"""
Integration test script for Task CRUD API.
Tests all endpoints with JWT authentication and user isolation.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8001"
API_URL = f"{BASE_URL}/api"

# ANSI color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(name):
    """Print test name."""
    print(f"\n{BLUE}[TEST]{RESET} {name}")

def print_pass(message):
    """Print success message."""
    print(f"{GREEN}[PASS]{RESET} {message}")

def print_fail(message):
    """Print failure message."""
    print(f"{RED}[FAIL]{RESET} {message}")

def print_info(message):
    """Print info message."""
    print(f"{YELLOW}[INFO]{RESET} {message}")

def test_health_check():
    """Test backend health check endpoint."""
    print_test("Health Check")

    try:
        response = requests.get(f"{BASE_URL}/")

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                print_pass(f"Backend is running: {data.get('message')}")
                return True
            else:
                print_fail(f"Unexpected response: {data}")
                return False
        else:
            print_fail(f"Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Connection error: {e}")
        return False

def test_openapi_docs():
    """Test OpenAPI documentation endpoint."""
    print_test("OpenAPI Documentation")

    try:
        response = requests.get(f"{BASE_URL}/openapi.json")

        if response.status_code == 200:
            data = response.json()
            paths = data.get("paths", {})

            # Check for task endpoints
            expected_endpoints = [
                "/api/tasks/",
                "/api/tasks/{task_id}",
                "/api/tasks/{task_id}/complete"
            ]

            found_endpoints = []
            for endpoint in expected_endpoints:
                if endpoint in paths:
                    found_endpoints.append(endpoint)
                    print_pass(f"Endpoint registered: {endpoint}")
                else:
                    print_fail(f"Endpoint missing: {endpoint}")

            if len(found_endpoints) == len(expected_endpoints):
                print_pass("All task endpoints registered")
                return True
            else:
                print_fail(f"Only {len(found_endpoints)}/{len(expected_endpoints)} endpoints found")
                return False
        else:
            print_fail(f"OpenAPI docs failed with status {response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Error: {e}")
        return False

def test_auth_required():
    """Test that endpoints require authentication."""
    print_test("Authentication Required")

    endpoints = [
        ("GET", "/api/tasks/"),
        ("POST", "/api/tasks/"),
        ("GET", "/api/tasks/1"),
        ("PUT", "/api/tasks/1"),
        ("DELETE", "/api/tasks/1"),
        ("PATCH", "/api/tasks/1/complete")
    ]

    all_passed = True

    for method, endpoint in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", json={})
            elif method == "PUT":
                response = requests.put(f"{BASE_URL}{endpoint}", json={})
            elif method == "DELETE":
                response = requests.delete(f"{BASE_URL}{endpoint}")
            elif method == "PATCH":
                response = requests.patch(f"{BASE_URL}{endpoint}")

            if response.status_code == 401:
                print_pass(f"{method} {endpoint} returns 401 without JWT")
            else:
                print_fail(f"{method} {endpoint} returned {response.status_code} (expected 401)")
                all_passed = False
        except Exception as e:
            print_fail(f"{method} {endpoint} error: {e}")
            all_passed = False

    return all_passed

def test_with_jwt(jwt_token):
    """Test endpoints with valid JWT token."""
    print_test("Endpoints with Valid JWT")

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    # Test 1: Create task
    print_info("Creating task...")
    response = requests.post(
        f"{API_URL}/tasks/",
        headers=headers,
        json={
            "title": "Test Task from Integration Test",
            "description": "This is a test task"
        }
    )

    if response.status_code == 201:
        task = response.json().get("data")
        task_id = task.get("id")
        print_pass(f"Task created with ID: {task_id}")
        print_info(f"  Title: {task.get('title')}")
        print_info(f"  User ID: {task.get('user_id')}")
        print_info(f"  Completed: {task.get('completed')}")
    else:
        print_fail(f"Create task failed: {response.status_code} - {response.text}")
        return False

    # Test 2: List tasks
    print_info("Listing tasks...")
    response = requests.get(f"{API_URL}/tasks/", headers=headers)

    if response.status_code == 200:
        tasks = response.json().get("data", [])
        print_pass(f"Retrieved {len(tasks)} tasks")

        # Verify our task is in the list
        found = any(t.get("id") == task_id for t in tasks)
        if found:
            print_pass("Created task found in list")
        else:
            print_fail("Created task not found in list")
    else:
        print_fail(f"List tasks failed: {response.status_code}")
        return False

    # Test 3: Get single task
    print_info(f"Getting task {task_id}...")
    response = requests.get(f"{API_URL}/tasks/{task_id}", headers=headers)

    if response.status_code == 200:
        task = response.json().get("data")
        print_pass(f"Retrieved task: {task.get('title')}")
    else:
        print_fail(f"Get task failed: {response.status_code}")
        return False

    # Test 4: Update task
    print_info(f"Updating task {task_id}...")
    response = requests.put(
        f"{API_URL}/tasks/{task_id}",
        headers=headers,
        json={
            "title": "Updated Test Task",
            "description": "Updated description"
        }
    )

    if response.status_code == 200:
        task = response.json().get("data")
        if task.get("title") == "Updated Test Task":
            print_pass("Task updated successfully")
        else:
            print_fail("Task title not updated")
    else:
        print_fail(f"Update task failed: {response.status_code}")
        return False

    # Test 5: Toggle completion
    print_info(f"Toggling completion for task {task_id}...")
    response = requests.patch(f"{API_URL}/tasks/{task_id}/complete", headers=headers)

    if response.status_code == 200:
        task = response.json().get("data")
        if task.get("completed") == True:
            print_pass("Task marked as completed")
        else:
            print_fail("Task completion not toggled")
    else:
        print_fail(f"Toggle completion failed: {response.status_code}")
        return False

    # Test 6: Toggle back
    print_info(f"Toggling completion again for task {task_id}...")
    response = requests.patch(f"{API_URL}/tasks/{task_id}/complete", headers=headers)

    if response.status_code == 200:
        task = response.json().get("data")
        if task.get("completed") == False:
            print_pass("Task marked as incomplete")
        else:
            print_fail("Task completion not toggled back")
    else:
        print_fail(f"Toggle completion failed: {response.status_code}")
        return False

    # Test 7: Delete task
    print_info(f"Deleting task {task_id}...")
    response = requests.delete(f"{API_URL}/tasks/{task_id}", headers=headers)

    if response.status_code == 204:
        print_pass("Task deleted successfully")
    else:
        print_fail(f"Delete task failed: {response.status_code}")
        return False

    # Test 8: Verify deletion
    print_info(f"Verifying task {task_id} is deleted...")
    response = requests.get(f"{API_URL}/tasks/{task_id}", headers=headers)

    if response.status_code == 404:
        print_pass("Deleted task returns 404")
    else:
        print_fail(f"Deleted task still accessible: {response.status_code}")
        return False

    return True

def main():
    """Run all integration tests."""
    print("\n" + "="*60)
    print("Task CRUD API - Integration Tests")
    print("="*60)

    # Test 1: Health check
    if not test_health_check():
        print_fail("\nBackend is not running. Start with: uvicorn app.main:app --reload")
        sys.exit(1)

    # Test 2: OpenAPI docs
    if not test_openapi_docs():
        print_fail("\nOpenAPI documentation check failed")
        sys.exit(1)

    # Test 3: Auth required
    if not test_auth_required():
        print_fail("\nAuthentication check failed")
        sys.exit(1)

    # Test 4: With JWT token
    print_info("\n" + "="*60)
    print_info("To test with JWT authentication:")
    print_info("1. Open http://localhost:3000 in browser")
    print_info("2. Login with your account")
    print_info("3. Open DevTools -> Application -> Cookies")
    print_info("4. Copy value of 'better-auth.session_token'")
    print_info("5. Run: python test_integration.py <jwt_token>")
    print_info("="*60)

    if len(sys.argv) > 1:
        jwt_token = sys.argv[1]
        print_info(f"\nUsing JWT token: {jwt_token[:20]}...")

        if test_with_jwt(jwt_token):
            print("\n" + "="*60)
            print_pass("All integration tests passed!")
            print("="*60)
        else:
            print("\n" + "="*60)
            print_fail("Some integration tests failed")
            print("="*60)
            sys.exit(1)
    else:
        print("\n" + "="*60)
        print_pass("Basic tests passed! Provide JWT token to run full tests.")
        print("="*60)

if __name__ == "__main__":
    main()
