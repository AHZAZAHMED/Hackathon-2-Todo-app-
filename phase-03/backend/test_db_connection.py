"""
Database connection test script.
Tests database connectivity, table existence, and user data.
"""

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

print("=" * 60)
print("DATABASE CONNECTION TEST")
print("=" * 60)

try:
    # Test 1: Check connection
    print("\n[TEST 1] Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print("[PASS] Database connected")
    print(f"   PostgreSQL version: {version[:50]}...")

    # Test 2: Check tasks table exists
    print("\n[TEST 2] Checking if 'tasks' table exists...")
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'tasks'
        );
    """)
    if cursor.fetchone()[0]:
        print("[PASS] Tasks table exists")

        # Get table schema
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'tasks'
            ORDER BY ordinal_position;
        """)
        print("   Table schema:")
        for col in cursor.fetchall():
            print(f"     - {col[0]}: {col[1]} (nullable: {col[2]})")
    else:
        print("[FAIL] Tasks table does NOT exist")
        print("   Run migration: psql $DATABASE_URL -f backend/migrations/002_create_tasks_table.sql")

    # Test 3: Check user table exists
    print("\n[TEST 3] Checking if 'user' table exists...")
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'user'
        );
    """)
    if cursor.fetchone()[0]:
        print("[PASS] User table exists")

        # Count users
        cursor.execute('SELECT COUNT(*) FROM "user"')
        user_count = cursor.fetchone()[0]
        print(f"   Total users in database: {user_count}")

        # Show first few user IDs
        if user_count > 0:
            cursor.execute('SELECT id, email FROM "user" LIMIT 5')
            print("   Sample users:")
            for user in cursor.fetchall():
                print(f"     - ID: {user[0]}, Email: {user[1]}")
    else:
        print("[FAIL] User table does NOT exist")
        print("   Run Better Auth migration first")

    # Test 4: Check if specific user exists (from JWT)
    print("\n[TEST 4] Checking if authenticated user exists...")
    # This is the user_id from the JWT token you're testing with
    test_user_id = "SUeetRmW8cp7kOulX8VHwkFnK5U3FGHp"
    cursor.execute('SELECT id, email FROM "user" WHERE id = %s', (test_user_id,))
    user = cursor.fetchone()
    if user:
        print(f"[PASS] User {test_user_id} exists in database")
        print(f"   Email: {user[1]}")
    else:
        print(f"[FAIL] User {test_user_id} does NOT exist in database")
        print("   This user_id is from the JWT token but not in the database")
        print("   Possible causes:")
        print("     1. User was deleted from database")
        print("     2. JWT was generated with wrong user_id")
        print("     3. Database was reset but JWT still valid")

    # Test 5: Try to insert a test task
    print("\n[TEST 5] Testing task insertion...")
    try:
        cursor.execute("""
            INSERT INTO tasks (user_id, title, description, completed, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            RETURNING id, title;
        """, (test_user_id, "Test Task", "Test Description", False))

        task = cursor.fetchone()
        print("[PASS] Task insertion successful")
        print(f"   Created task ID: {task[0]}, Title: {task[1]}")

        # Clean up test task
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task[0],))
        conn.commit()
        print("   Test task cleaned up")
    except Exception as e:
        print(f"[FAIL] Task insertion failed: {type(e).__name__}: {e}")
        conn.rollback()

    cursor.close()
    conn.close()

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")
    import traceback
    print("\nFull traceback:")
    print(traceback.format_exc())
