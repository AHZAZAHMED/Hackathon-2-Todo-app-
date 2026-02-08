import psycopg2
import sys

# Database connection string
DATABASE_URL = "postgresql://neondb_owner:npg_lF0Lv8ZawHrP@ep-dawn-hill-ai6x5641-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Read SQL migration file
with open('backend/migrations/001_create_auth_tables.sql', 'r') as f:
    sql = f.read()

try:
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Execute migration
    cur.execute(sql)
    conn.commit()

    # Verify tables created
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name IN ('users', 'rate_limits')
        ORDER BY table_name;
    """)

    tables = cur.fetchall()
    print("SUCCESS: Migration successful!")
    print(f"SUCCESS: Tables created: {[t[0] for t in tables]}")

    cur.close()
    conn.close()
    sys.exit(0)

except Exception as e:
    print(f"ERROR: Migration failed: {e}")
    sys.exit(1)
