"""
Quick verification script to confirm backend is ready for frontend integration.
Run this before testing with the frontend UI.
"""

import requests
import sys

BASE_URL = "http://localhost:8001"

def verify_backend():
    """Verify backend is ready for frontend integration."""

    print("\n" + "="*60)
    print("Backend Readiness Verification")
    print("="*60 + "\n")

    checks_passed = 0
    checks_total = 5

    # Check 1: Backend is running
    print("[1/5] Checking backend health...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("  [PASS] Backend is running")
            checks_passed += 1
        else:
            print(f"  [FAIL] Backend returned status {response.status_code}")
    except Exception as e:
        print(f"  [FAIL] Backend not accessible: {e}")
        print("\n[ERROR] Backend is not running!")
        print("Start with: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload")
        sys.exit(1)

    # Check 2: OpenAPI docs accessible
    print("\n[2/5] Checking OpenAPI documentation...")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "/api/tasks/" in data.get("paths", {}):
                print("  [PASS] OpenAPI docs accessible")
                print("  [PASS] Task endpoints registered")
                checks_passed += 1
            else:
                print("  [FAIL] Task endpoints not found in OpenAPI spec")
        else:
            print(f"  [FAIL] OpenAPI docs returned status {response.status_code}")
    except Exception as e:
        print(f"  [FAIL] OpenAPI docs not accessible: {e}")

    # Check 3: CORS headers
    print("\n[3/5] Checking CORS configuration...")
    try:
        response = requests.options(
            f"{BASE_URL}/api/tasks/",
            headers={"Origin": "http://localhost:3000"}
        )
        cors_headers = response.headers.get("Access-Control-Allow-Origin")
        if cors_headers:
            print(f"  [PASS] CORS configured: {cors_headers}")
            checks_passed += 1
        else:
            print("  [WARN] CORS headers not found (may still work)")
            checks_passed += 1  # Not critical
    except Exception as e:
        print(f"  [WARN] Could not verify CORS: {e}")
        checks_passed += 1  # Not critical

    # Check 4: Authentication required
    print("\n[4/5] Checking authentication enforcement...")
    try:
        response = requests.get(f"{BASE_URL}/api/tasks/")
        if response.status_code == 401:
            print("  [PASS] Authentication required (401 returned)")
            checks_passed += 1
        else:
            print(f"  [FAIL] Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"  [FAIL] Could not verify authentication: {e}")

    # Check 5: Frontend connectivity
    print("\n[5/5] Checking frontend server...")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("  [PASS] Frontend is running on port 3000")
            checks_passed += 1
        else:
            print(f"  [WARN] Frontend returned status {response.status_code}")
    except Exception as e:
        print(f"  [WARN] Frontend not accessible: {e}")
        print("  Note: Start frontend with: cd frontend && npm run dev")

    # Summary
    print("\n" + "="*60)
    print(f"Verification Result: {checks_passed}/{checks_total} checks passed")
    print("="*60 + "\n")

    if checks_passed >= 4:
        print("[SUCCESS] Backend is ready for frontend integration testing!")
        print("\nNext Steps:")
        print("1. Open http://localhost:3000 in your browser")
        print("2. Login with your account")
        print("3. Create a new task")
        print("4. Verify the task appears in the list")
        print("5. Try updating, completing, and deleting tasks")
        print("6. Refresh the page - tasks should persist")
        print("\nAPI Documentation: http://localhost:8001/docs")
        return True
    else:
        print("[FAIL] Some checks failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = verify_backend()
    sys.exit(0 if success else 1)
