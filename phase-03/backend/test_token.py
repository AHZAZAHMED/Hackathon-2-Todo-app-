"""
JWT Token Diagnostic Tool
Tests and validates JWT tokens to diagnose authentication issues.
"""

import sys
import jwt
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

def test_token(token: str):
    """
    Test and diagnose a JWT token.

    Args:
        token: JWT token string to test
    """
    print("\n" + "="*60)
    print("JWT Token Diagnostic Tool")
    print("="*60 + "\n")

    # Step 1: Check token format
    print("[1/5] Checking token format...")

    if not token:
        print("  [ERROR] Token is empty!")
        print("  Please provide a token as argument.")
        sys.exit(1)

    # Remove "Bearer " prefix if present
    if token.startswith("Bearer "):
        print("  [INFO] Removing 'Bearer ' prefix...")
        token = token[7:]

    # Check basic format
    parts = token.split(".")
    if len(parts) != 3:
        print(f"  [ERROR] Invalid JWT format! Token has {len(parts)} parts, expected 3")
        print(f"  Token should have format: header.payload.signature")
        print(f"  Your token: {token[:50]}...")
        sys.exit(1)

    if not token.startswith("eyJ"):
        print(f"  [ERROR] Token doesn't start with 'eyJ'")
        print(f"  Your token starts with: {token[:10]}")
        sys.exit(1)

    print("  [PASS] Token format looks valid (3 parts, starts with 'eyJ')")
    print(f"  Token length: {len(token)} characters")

    # Step 2: Decode header (without verification)
    print("\n[2/5] Decoding token header...")
    try:
        header = jwt.get_unverified_header(token)
        print(f"  [PASS] Header decoded successfully")
        print(f"  Algorithm: {header.get('alg')}")
        print(f"  Type: {header.get('typ')}")

        if header.get('alg') != 'HS256':
            print(f"  [WARN] Expected algorithm 'HS256', got '{header.get('alg')}'")
    except Exception as e:
        print(f"  [ERROR] Failed to decode header: {e}")
        sys.exit(1)

    # Step 3: Decode payload (without verification)
    print("\n[3/5] Decoding token payload (without verification)...")
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        print(f"  [PASS] Payload decoded successfully")
        print(f"  Claims found:")
        for key, value in payload.items():
            if key in ['exp', 'iat']:
                # Convert timestamp to readable date
                dt = datetime.fromtimestamp(value)
                print(f"    - {key}: {value} ({dt})")
            else:
                print(f"    - {key}: {value}")

        # Check required claims
        required_claims = ['user_id', 'email', 'exp', 'iat']
        missing_claims = [claim for claim in required_claims if claim not in payload]

        if missing_claims:
            print(f"  [WARN] Missing required claims: {missing_claims}")
        else:
            print(f"  [PASS] All required claims present")

        # Check expiration
        exp = payload.get('exp')
        if exp:
            exp_dt = datetime.fromtimestamp(exp)
            now = datetime.now()
            if exp_dt < now:
                print(f"  [ERROR] Token has EXPIRED!")
                print(f"    Expired at: {exp_dt}")
                print(f"    Current time: {now}")
                print(f"    Expired {(now - exp_dt).total_seconds() / 60:.1f} minutes ago")
                print("\n  [SOLUTION] Login again to get a fresh token")
                sys.exit(1)
            else:
                remaining = (exp_dt - now).total_seconds() / 60
                print(f"  [PASS] Token is still valid ({remaining:.1f} minutes remaining)")

    except Exception as e:
        print(f"  [ERROR] Failed to decode payload: {e}")
        sys.exit(1)

    # Step 4: Verify signature
    print("\n[4/5] Verifying token signature...")

    if not BETTER_AUTH_SECRET:
        print("  [ERROR] BETTER_AUTH_SECRET not found in .env file!")
        sys.exit(1)

    print(f"  Using secret: {BETTER_AUTH_SECRET[:10]}... (length: {len(BETTER_AUTH_SECRET)})")

    try:
        verified_payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=['HS256']
        )
        print("  [PASS] Signature verified successfully!")
        print("  [PASS] Token is valid and can be used for authentication")

    except jwt.ExpiredSignatureError:
        print("  [ERROR] Token has expired!")
        print("  [SOLUTION] Login again to get a fresh token")
        sys.exit(1)
    except jwt.InvalidSignatureError:
        print("  [ERROR] Invalid signature!")
        print("  [ISSUE] The token was signed with a different secret")
        print("  [CHECK] Make sure BETTER_AUTH_SECRET matches between frontend and backend")
        sys.exit(1)
    except jwt.DecodeError as e:
        print(f"  [ERROR] Token decode error: {e}")
        print("  [ISSUE] Token format is invalid or corrupted")
        sys.exit(1)
    except Exception as e:
        print(f"  [ERROR] Verification failed: {e}")
        sys.exit(1)

    # Step 5: Test with backend
    print("\n[5/5] Testing with backend API...")
    try:
        import requests

        response = requests.post(
            "http://localhost:8001/api/tasks/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "title": "Test Task from Diagnostic Tool",
                "description": "Testing token"
            }
        )

        if response.status_code == 201:
            print("  [PASS] Successfully created task!")
            data = response.json()
            print(f"  Task ID: {data['data']['id']}")
            print(f"  Task Title: {data['data']['title']}")
            print(f"  User ID: {data['data']['user_id']}")
        elif response.status_code == 401:
            print("  [ERROR] Backend returned 401 Unauthorized")
            print(f"  Response: {response.json()}")
        else:
            print(f"  [ERROR] Backend returned status {response.status_code}")
            print(f"  Response: {response.text}")

    except Exception as e:
        print(f"  [WARN] Could not test with backend: {e}")
        print("  [INFO] Make sure backend is running on http://localhost:8001")

    # Summary
    print("\n" + "="*60)
    print("[SUCCESS] Token is valid and ready to use!")
    print("="*60)
    print("\nYou can use this token in Swagger UI:")
    print(f"Bearer {token[:50]}...")
    print("\nOr use this curl command:")
    print(f'curl -X POST "http://localhost:8001/api/tasks/" \\')
    print(f'  -H "Authorization: Bearer {token}" \\')
    print(f'  -H "Content-Type: application/json" \\')
    print(f'  -d \'{{"title":"Test Task","description":"Testing"}}\'')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUsage: python test_token.py <your-jwt-token>")
        print("\nExample:")
        print('  python test_token.py "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."')
        print("\nHow to get your token:")
        print("  1. Login to http://localhost:3000")
        print("  2. Press F12 to open DevTools")
        print("  3. Go to Application -> Cookies -> http://localhost:3000")
        print("  4. Copy the value of 'better-auth.session_token'")
        print("  5. Run: python test_token.py \"<paste-token-here>\"")
        sys.exit(1)

    token = sys.argv[1]
    test_token(token)
