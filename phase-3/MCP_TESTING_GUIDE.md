# MCP Tools Testing Guide
# Test all 5 MCP tools and verify database changes

## Current Database State
Tasks in database:
- ID:22 | Title: butter jam | Completed: False
- ID:21 | Title: Buy milk | Completed: False
- ID:20 | Title: Namaz | Completed: False
Total: 3 tasks

## Testing Instructions

### Setup
1. Open http://localhost:3000 in your browser
2. Click the chatbot icon in the bottom right corner
3. The chat window should open

---

## TEST 1: LIST_TASKS (View all tasks)

### Message to send:
```
Show me all my tasks
```

### Expected AI Response:
Should list all 3 tasks (butter jam, Buy milk, Namaz)

### Database Verification:
Run this command in a terminal:
```bash
cd "E:\Hackathon-2\phase-3\backend" && python -c "from sqlmodel import Session, select, create_engine; from app.models.task import Task; from app.config import DATABASE_URL; engine = create_engine(DATABASE_URL); session = Session(engine); tasks = session.exec(select(Task).where(Task.user_id == 'SUeetRmW8cp7kOulX8VHwkFnK5U3FGHp').order_by(Task.created_at.desc())).all(); print('Tasks:'); [print(f'  ID:{t.id} | {t.title} | Completed:{t.completed}') for t in tasks]"
```

### Expected Result:
✅ PASS: list_tasks doesn't modify database, just returns data
(Database should still have same 3 tasks)

---

## TEST 2: COMPLETE_TASK (Mark task as done)

### Message to send:
```
Mark task 21 as completed
```

### Expected AI Response:
Should confirm that task 21 (Buy milk) has been marked as completed

### Database Verification:
Run this command:
```bash
cd "E:\Hackathon-2\phase-3\backend" && python -c "from sqlmodel import Session, select, create_engine; from app.models.task import Task; from app.config import DATABASE_URL; engine = create_engine(DATABASE_URL); session = Session(engine); task = session.exec(select(Task).where(Task.id == 21)).first(); print(f'Task 21: {task.title} | Completed: {task.completed}' if task else 'Task not found')"
```

### Expected Result:
✅ PASS: Task 21 completed status should change from False to True
❌ FAIL: If completed is still False, the tool is hallucinating

---

## TEST 3: UPDATE_TASK (Change task title)

### Message to send:
```
Change task 21 title to Buy organic milk and eggs
```

### Expected AI Response:
Should confirm that task 21 title has been updated

### Database Verification:
Run this command:
```bash
cd "E:\Hackathon-2\phase-3\backend" && python -c "from sqlmodel import Session, select, create_engine; from app.models.task import Task; from app.config import DATABASE_URL; engine = create_engine(DATABASE_URL); session = Session(engine); task = session.exec(select(Task).where(Task.id == 21)).first(); print(f'Task 21 title: {task.title}' if task else 'Task not found')"
```

### Expected Result:
✅ PASS: Title should change from "Buy milk" to "Buy organic milk and eggs"
❌ FAIL: If title is still "Buy milk", the tool is hallucinating

---

## TEST 4: ADD_TASK (Create new task)

### Message to send:
```
Add a task: Test deletion task
```

### Expected AI Response:
Should confirm that a new task has been created

### Database Verification:
Run this command:
```bash
cd "E:\Hackathon-2\phase-3\backend" && python -c "from sqlmodel import Session, select, create_engine; from app.models.task import Task; from app.config import DATABASE_URL; engine = create_engine(DATABASE_URL); session = Session(engine); tasks = session.exec(select(Task).where(Task.user_id == 'SUeetRmW8cp7kOulX8VHwkFnK5U3FGHp').order_by(Task.created_at.desc())).all(); print(f'Total tasks: {len(tasks)}'); [print(f'  ID:{t.id} | {t.title}') for t in tasks]"
```

### Expected Result:
✅ PASS: Total tasks should increase from 3 to 4, new task should appear
❌ FAIL: If still 3 tasks, the tool is hallucinating

---

## TEST 5: DELETE_TASK (Remove task)

### Message to send:
```
Delete the test deletion task
```

### Expected AI Response:
Should confirm that the task has been deleted

### Database Verification:
Run this command:
```bash
cd "E:\Hackathon-2\phase-3\backend" && python -c "from sqlmodel import Session, select, create_engine; from app.models.task import Task; from app.config import DATABASE_URL; engine = create_engine(DATABASE_URL); session = Session(engine); tasks = session.exec(select(Task).where(Task.user_id == 'SUeetRmW8cp7kOulX8VHwkFnK5U3FGHp').order_by(Task.created_at.desc())).all(); print(f'Total tasks: {len(tasks)}'); [print(f'  ID:{t.id} | {t.title}') for t in tasks]"
```

### Expected Result:
✅ PASS: Total tasks should decrease from 4 to 3, deletion task should be gone
❌ FAIL: If still 4 tasks, the tool is hallucinating

---

## Summary

After completing all tests, you should see:
- ✅ list_tasks: Working (returns data)
- ✅/❌ complete_task: Check if task 21 completed status changed
- ✅/❌ update_task: Check if task 21 title changed
- ✅/❌ add_task: Check if new task was created
- ✅/❌ delete_task: Check if task was removed

If any tool shows ❌ FAIL, it means the AI is hallucinating responses without actually executing the MCP tool to modify the database.
