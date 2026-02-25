import jwt
import requests
import json
from datetime import datetime, timedelta

# JWT secret from .env
SECRET = "zv4LMH5HdFzF7sOF3bdwxLzauA5TQiFf"
USER_ID = "SUeetRmW8cp7kOulX8VHwkFnK5U3FGHp"

# Create JWT token
payload = {
    "sub": USER_ID,
    "user_id": USER_ID,
    "email": "ahzazahmed159@gmail.com",
    "name": "Ahzaz Ahmed",
    "iat": datetime.utcnow(),
    "exp": datetime.utcnow() + timedelta(days=7)
}

token = jwt.encode(payload, SECRET, algorithm="HS256")

# Create test tasks
url = "http://localhost:8001/api/chat/"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

tasks = [
    "Add a task: Buy groceries",
    "Add a task: Complete homework",
    "Add a task: Call dentist"
]

print("Creating test tasks...")
print("=" * 60)

for task_msg in tasks:
    data = {"message": task_msg}
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            print(f"[OK] {task_msg}")
        else:
            print(f"[FAIL] {task_msg} - Status: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] {task_msg} - Error: {e}")

print("\nTest tasks created successfully!")
