import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

print("Adding 'title' column to conversations table...")

with engine.connect() as conn:
    # Add the missing title column
    conn.execute(text("""
        ALTER TABLE conversations 
        ADD COLUMN IF NOT EXISTS title VARCHAR(200);
    """))
    conn.commit()
    print("✓ Column added successfully")
    
    # Verify the fix
    result = conn.execute(text("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'conversations'
        ORDER BY ordinal_position;
    """))
    
    print("\nUpdated conversations table schema:")
    for row in result:
        print(f"  - {row[0]}: {row[1]} (nullable: {row[2]})")

print("\n✓ Database schema fixed!")
