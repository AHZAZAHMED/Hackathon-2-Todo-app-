import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'conversations'
        ORDER BY ordinal_position;
    """))
    
    print("Conversations table schema:")
    columns = []
    for row in result:
        columns.append(row[0])
        print(f"  - {row[0]}: {row[1]} (nullable: {row[2]})")
    
    if 'title' in columns:
        print("\n[OK] Title column exists!")
    else:
        print("\n[ERROR] Title column is missing!")
