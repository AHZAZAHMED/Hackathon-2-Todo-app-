import psycopg2
import sys

# Database connection string
DATABASE_URL = "postgresql://neondb_owner:npg_lF0Lv8ZawHrP@ep-dawn-hill-ai6x5641-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

try:
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Drop manually created tables
    print("Dropping manually created tables...")
    cur.execute("DROP TABLE IF EXISTS rate_limits CASCADE;")
    cur.execute("DROP TABLE IF EXISTS users CASCADE;")
    conn.commit()

    print("SUCCESS: Manually created tables dropped")
    print("Better Auth will now create its own tables automatically")

    cur.close()
    conn.close()
    sys.exit(0)

except Exception as e:
    print(f"ERROR: Failed to drop tables: {e}")
    sys.exit(1)
