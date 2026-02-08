"""
Database migration runner script.
Executes SQL migration files using psycopg2.
"""

import os
import sys
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("[ERROR] DATABASE_URL not found in .env file")
    sys.exit(1)

def run_migration(migration_file: str):
    """
    Execute a SQL migration file.

    Args:
        migration_file: Path to the SQL migration file
    """
    migration_path = Path(migration_file)

    if not migration_path.exists():
        print(f"[ERROR] Migration file not found: {migration_file}")
        sys.exit(1)

    print(f"[INFO] Reading migration: {migration_path.name}")

    # Read SQL file
    with open(migration_path, 'r', encoding='utf-8') as f:
        sql = f.read()

    print(f"[INFO] Connecting to database...")

    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()

        print(f"[INFO] Executing migration...")

        # Execute SQL
        cursor.execute(sql)

        print(f"[SUCCESS] Migration completed successfully!")

        # Verify table exists
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name = 'tasks'
        """)

        if cursor.fetchone():
            print(f"[SUCCESS] Table 'tasks' created successfully")

        # Verify indexes
        cursor.execute("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'tasks'
        """)

        indexes = cursor.fetchall()
        print(f"[SUCCESS] Indexes created: {len(indexes)} indexes")
        for idx in indexes:
            print(f"   - {idx[0]}")

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"[ERROR] Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_migration.py <migration_file>")
        print("Example: python run_migration.py migrations/002_create_tasks_table.sql")
        sys.exit(1)

    migration_file = sys.argv[1]
    run_migration(migration_file)
