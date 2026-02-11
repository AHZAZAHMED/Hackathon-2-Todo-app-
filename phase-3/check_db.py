"""
Quick MCP Tools Verification
Run this after testing each tool in the chatbot
"""
import sys
sys.path.insert(0, r'E:\Hackathon-2\phase-3\backend')

from sqlmodel import Session, select, create_engine
from app.models.task import Task
from app.config import DATABASE_URL

USER_ID = "SUeetRmW8cp7kOulX8VHwkFnK5U3FGHp"
engine = create_engine(DATABASE_URL)

def check_database():
    with Session(engine) as session:
        tasks = session.exec(
            select(Task)
            .where(Task.user_id == USER_ID)
            .order_by(Task.created_at.desc())
        ).all()

        print("\n" + "="*80)
        print("CURRENT DATABASE STATE")
        print("="*80)

        if not tasks:
            print("No tasks found")
        else:
            print(f"Total tasks: {len(tasks)}\n")
            for task in tasks:
                status = "[X]" if task.completed else "[ ]"
                print(f"{status} ID:{task.id:3d} | {task.title}")

        print("="*80)
        return tasks

if __name__ == "__main__":
    check_database()
