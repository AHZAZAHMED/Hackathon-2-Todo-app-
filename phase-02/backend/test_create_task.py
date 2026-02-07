"""
Test script to create a task via API and see detailed error logs.
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

# Test user (from database test)
test_user = {
    "user_id": "SUeetRmW8cp7kOulX8VHwkFnK5U3FGHp",
    "email": "ahzazahmed159@gmail.com",
    "name": "Test User"
}

# Generate JWT token
print("=" * 60)
print("TESTING TASK CREATION API")
print("=" * 60)

print("\n[STEP 1] Generating JWT token...")
payload = {
    "user_id": test_user["user_id"],
    "email": test_user["email"],
    "name": test_user["name"],
    "iat": datetime.utcnow(),
    "exp": datetime.utcnow() + timedelta(hours=24)
}

token = jwt.encode(payload, BETTER_AUTH_SECRET, algorithm="HS256")
print(f"Token generated: {token[:50]}...")

# Make API request
print("\n[STEP 2] Making POST request to /api/tasks/...")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

task_data = {
    "title": "Test Task from Script",
    "description": "Testing task creation via API"
}

try:
    response = requests.post(
        f"{BACKEND_URL}/api/tasks/",
        json=task_data,
        headers=headers,
        timeout=10
    )

    print(f"\n[STEP 3] Response received:")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

    if response.status_code == 201:
        print("\n[SUCCESS] Task created successfully!")
        print(f"Task data: {response.json()}")
    else:
        print(f"\n[ERROR] Request failed with status {response.status_code}")
        print("Check backend logs for detailed error information")

except requests.exceptions.RequestException as e:
    print(f"\n[ERROR] Request failed: {e}")

print("\n" + "=" * 60)
print("Check the backend server logs for detailed error traces")
print("=" * 60)
