"""
Verify database migration script.
Checks that tasks table, indexes, and foreign key constraints exist.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("[ERROR] DATABASE_URL not found in .env file")
    sys.exit(1)

def verify_migration():
    """Verify that tasks table migration was successful."""

    print("[INFO] Connecting to database...")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Check 1: Verify table exists
        print("\n[CHECK 1] Verifying tasks table exists...")
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name = 'tasks'
        """)

        if cursor.fetchone():
            print("[PASS] Table 'tasks' exists")
        else:
            print("[FAIL] Table 'tasks' does not exist")
            sys.exit(1)

        # Check 2: Verify table structure
        print("\n[CHECK 2] Verifying table structure...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'tasks'
            ORDER BY ordinal_position
        """)

        columns = cursor.fetchall()
        expected_columns = {
            'id': 'integer',
            'user_id': 'text',
            'title': 'character varying',
            'description': 'text',
            'completed': 'boolean',
            'created_at': 'timestamp without time zone',
            'updated_at': 'timestamp without time zone'
        }

        found_columns = {col[0]: col[1] for col in columns}

        for col_name, col_type in expected_columns.items():
            if col_name in found_columns:
                print(f"[PASS] Column '{col_name}' exists ({found_columns[col_name]})")
            else:
                print(f"[FAIL] Column '{col_name}' missing")
                sys.exit(1)

        # Check 3: Verify indexes
        print("\n[CHECK 3] Verifying indexes...")
        cursor.execute("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'tasks'
        """)

        indexes = cursor.fetchall()
        expected_indexes = ['tasks_pkey', 'idx_tasks_user_id', 'idx_tasks_completed']
        found_indexes = [idx[0] for idx in indexes]

        for idx_name in expected_indexes:
            if idx_name in found_indexes:
                print(f"[PASS] Index '{idx_name}' exists")
            else:
                print(f"[FAIL] Index '{idx_name}' missing")
                sys.exit(1)

        # Check 4: Verify foreign key constraint
        print("\n[CHECK 4] Verifying foreign key constraint...")
        cursor.execute("""
            SELECT
                tc.constraint_name,
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                rc.delete_rule
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            JOIN information_schema.referential_constraints AS rc
                ON tc.constraint_name = rc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_name = 'tasks'
        """)

        fk = cursor.fetchone()

        if fk:
            constraint_name, table_name, column_name, foreign_table, foreign_column, delete_rule = fk
            print(f"[PASS] Foreign key constraint exists: {constraint_name}")
            print(f"       {table_name}.{column_name} -> {foreign_table}.{foreign_column}")
            print(f"       ON DELETE {delete_rule}")

            if delete_rule == 'CASCADE':
                print("[PASS] CASCADE delete rule configured correctly")
            else:
                print(f"[WARN] Expected CASCADE, found {delete_rule}")
        else:
            print("[FAIL] Foreign key constraint missing")
            sys.exit(1)

        cursor.close()
        conn.close()

        print("\n" + "="*60)
        print("[SUCCESS] All migration checks passed!")
        print("="*60)

    except psycopg2.Error as e:
        print(f"[ERROR] Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_migration()
