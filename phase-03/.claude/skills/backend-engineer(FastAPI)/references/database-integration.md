# FastAPI Database Integration Patterns

## SQLAlchemy Integration

### Database Setup

**Database Configuration**
```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/dbname"

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

**Async Database Configuration**
```python
# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20,
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()
```

### Database Models

**Basic Model**
```python
# models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tasks = relationship("Task", back_populates="owner")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="tasks")
```

**Model with Indexes and Constraints**
```python
from sqlalchemy import Index, CheckConstraint, UniqueConstraint

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String)
    completed = Column(Boolean, default=False)
    priority = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Composite indexes
    __table_args__ = (
        Index('idx_user_completed', 'user_id', 'completed'),
        Index('idx_user_priority', 'user_id', 'priority'),
        CheckConstraint('priority >= 0 AND priority <= 5', name='check_priority_range'),
        UniqueConstraint('user_id', 'title', name='unique_user_task_title'),
    )

    owner = relationship("User", back_populates="tasks")
```

### Database Session Management

**Dependency for Database Session**
```python
# dependencies.py
from database import SessionLocal

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Async Database Session**
```python
from database import async_session

async def get_async_db():
    """Get async database session."""
    async with async_session() as session:
        yield session
```

### CRUD Operations

**Synchronous CRUD**
```python
# crud.py
from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email."""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Get list of users with pagination."""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create new user."""
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserUpdate) -> Optional[models.User]:
    """Update user."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    update_data = user.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """Delete user."""
    db_user = get_user(db, user_id)
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True
```

**Async CRUD**
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def get_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    """Get user by ID (async)."""
    result = await db.execute(
        select(models.User).filter(models.User.id == user_id)
    )
    return result.scalar_one_or_none()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Get list of users with pagination (async)."""
    result = await db.execute(
        select(models.User).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def create_user(db: AsyncSession, user: schemas.UserCreate) -> models.User:
    """Create new user (async)."""
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
```

### Query Optimization

**Eager Loading with Relationships**
```python
from sqlalchemy.orm import joinedload, selectinload

def get_user_with_tasks(db: Session, user_id: int) -> Optional[models.User]:
    """Get user with all tasks (eager loading)."""
    return db.query(models.User)\
        .options(joinedload(models.User.tasks))\
        .filter(models.User.id == user_id)\
        .first()

def get_users_with_tasks(db: Session) -> List[models.User]:
    """Get all users with tasks (select in loading for collections)."""
    return db.query(models.User)\
        .options(selectinload(models.User.tasks))\
        .all()
```

**Filtering and Sorting**
```python
from sqlalchemy import and_, or_, desc

def get_tasks_filtered(
    db: Session,
    user_id: int,
    completed: Optional[bool] = None,
    priority_min: Optional[int] = None,
    sort_by: str = "created_at"
) -> List[models.Task]:
    """Get tasks with filtering and sorting."""
    query = db.query(models.Task).filter(models.Task.user_id == user_id)

    # Apply filters
    if completed is not None:
        query = query.filter(models.Task.completed == completed)

    if priority_min is not None:
        query = query.filter(models.Task.priority >= priority_min)

    # Apply sorting
    if sort_by == "priority":
        query = query.order_by(desc(models.Task.priority))
    elif sort_by == "title":
        query = query.order_by(models.Task.title)
    else:
        query = query.order_by(desc(models.Task.created_at))

    return query.all()
```

**Aggregation Queries**
```python
from sqlalchemy import func

def get_task_statistics(db: Session, user_id: int) -> dict:
    """Get task statistics for user."""
    stats = db.query(
        func.count(models.Task.id).label('total'),
        func.sum(func.cast(models.Task.completed, Integer)).label('completed'),
        func.avg(models.Task.priority).label('avg_priority')
    ).filter(models.Task.user_id == user_id).first()

    return {
        'total': stats.total or 0,
        'completed': stats.completed or 0,
        'pending': (stats.total or 0) - (stats.completed or 0),
        'avg_priority': float(stats.avg_priority or 0)
    }
```

### Connection Pooling

**Pool Configuration**
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,              # Number of connections to maintain
    max_overflow=20,           # Max connections beyond pool_size
    pool_timeout=30,           # Seconds to wait for connection
    pool_recycle=3600,         # Recycle connections after 1 hour
    pool_pre_ping=True,        # Verify connections before using
)
```

**Pool Event Listeners**
```python
from sqlalchemy import event

@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Event listener for new connections."""
    print("New database connection established")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Event listener for connection checkout."""
    print("Connection checked out from pool")
```

## Database Migrations with Alembic

### Alembic Setup

**Initialize Alembic**
```bash
alembic init alembic
```

**Configure Alembic**
```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import models
from database import Base

config = context.config

# Set SQLAlchemy URL
config.set_main_option('sqlalchemy.url', DATABASE_URL)

target_metadata = Base.metadata

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()
```

### Creating Migrations

**Auto-generate Migration**
```bash
alembic revision --autogenerate -m "Add users and tasks tables"
```

**Manual Migration**
```python
# alembic/versions/xxx_add_priority_column.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    """Add priority column to tasks table."""
    op.add_column('tasks', sa.Column('priority', sa.Integer(), nullable=True))
    op.create_index('idx_task_priority', 'tasks', ['priority'])

def downgrade():
    """Remove priority column from tasks table."""
    op.drop_index('idx_task_priority', table_name='tasks')
    op.drop_column('tasks', 'priority')
```

**Apply Migrations**
```bash
# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

## Tortoise ORM Integration

### Tortoise ORM Setup

**Configuration**
```python
# database.py
from tortoise import Tortoise

TORTOISE_ORM = {
    "connections": {
        "default": "postgres://user:password@localhost:5432/dbname"
    },
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        }
    },
}

async def init_db():
    """Initialize database."""
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

async def close_db():
    """Close database connections."""
    await Tortoise.close_connections()
```

**FastAPI Integration**
```python
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

app = FastAPI()

register_tortoise(
    app,
    db_url="postgres://user:password@localhost:5432/dbname",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
```

### Tortoise Models

```python
# models.py
from tortoise import fields
from tortoise.models import Model

class User(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True, index=True)
    username = fields.CharField(max_length=50, unique=True)
    hashed_password = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # Relationships
    tasks: fields.ReverseRelation["Task"]

    class Meta:
        table = "users"

class Task(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    completed = fields.BooleanField(default=False)
    user = fields.ForeignKeyField("models.User", related_name="tasks")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "tasks"
```

### Tortoise CRUD Operations

```python
# crud.py
from typing import List, Optional
from models import User, Task
from tortoise.exceptions import DoesNotExist

async def get_user(user_id: int) -> Optional[User]:
    """Get user by ID."""
    try:
        return await User.get(id=user_id)
    except DoesNotExist:
        return None

async def get_users(skip: int = 0, limit: int = 100) -> List[User]:
    """Get list of users."""
    return await User.all().offset(skip).limit(limit)

async def create_user(email: str, username: str, password: str) -> User:
    """Create new user."""
    user = await User.create(
        email=email,
        username=username,
        hashed_password=hash_password(password)
    )
    return user

async def update_user(user_id: int, **kwargs) -> Optional[User]:
    """Update user."""
    user = await get_user(user_id)
    if not user:
        return None

    await user.update_from_dict(kwargs).save()
    return user

async def delete_user(user_id: int) -> bool:
    """Delete user."""
    user = await get_user(user_id)
    if not user:
        return False

    await user.delete()
    return True

async def get_user_with_tasks(user_id: int) -> Optional[User]:
    """Get user with tasks (prefetch)."""
    try:
        return await User.get(id=user_id).prefetch_related("tasks")
    except DoesNotExist:
        return None
```

## Transaction Management

### SQLAlchemy Transactions

**Basic Transaction**
```python
from sqlalchemy.orm import Session

def transfer_task(db: Session, task_id: int, from_user_id: int, to_user_id: int):
    """Transfer task between users with transaction."""
    try:
        task = db.query(models.Task).filter(
            models.Task.id == task_id,
            models.Task.user_id == from_user_id
        ).first()

        if not task:
            raise ValueError("Task not found")

        # Update task owner
        task.user_id = to_user_id

        # Log transfer
        log = models.TransferLog(
            task_id=task_id,
            from_user_id=from_user_id,
            to_user_id=to_user_id
        )
        db.add(log)

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
```

**Nested Transactions (Savepoints)**
```python
def complex_operation(db: Session):
    """Complex operation with savepoints."""
    try:
        # Main transaction
        user = create_user(db, user_data)

        # Savepoint
        savepoint = db.begin_nested()
        try:
            task = create_task(db, task_data)
            savepoint.commit()
        except Exception:
            savepoint.rollback()
            # Continue with user creation

        db.commit()
    except Exception:
        db.rollback()
        raise
```

### Tortoise Transactions

```python
from tortoise.transactions import in_transaction

async def transfer_task_tortoise(task_id: int, from_user_id: int, to_user_id: int):
    """Transfer task with transaction (Tortoise)."""
    async with in_transaction() as connection:
        task = await Task.get(id=task_id, user_id=from_user_id)
        task.user_id = to_user_id
        await task.save(using_db=connection)

        log = await TransferLog.create(
            task_id=task_id,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            using_db=connection
        )
```

## Database Performance Optimization

### Indexing Strategies

```python
# Add indexes for frequently queried columns
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)  # Foreign key index
    completed = Column(Boolean, default=False, index=True)  # Filter index
    created_at = Column(DateTime, index=True)  # Sort index

    # Composite index for common query patterns
    __table_args__ = (
        Index('idx_user_completed_created', 'user_id', 'completed', 'created_at'),
    )
```

### Query Result Caching

```python
from functools import lru_cache
from datetime import datetime, timedelta

# Simple in-memory cache
_cache = {}
_cache_timeout = {}

def cached_query(key: str, timeout_seconds: int = 300):
    """Decorator for caching query results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            now = datetime.now()

            # Check cache
            if key in _cache and key in _cache_timeout:
                if now < _cache_timeout[key]:
                    return _cache[key]

            # Execute query
            result = func(*args, **kwargs)

            # Update cache
            _cache[key] = result
            _cache_timeout[key] = now + timedelta(seconds=timeout_seconds)

            return result
        return wrapper
    return decorator

@cached_query("user_stats", timeout_seconds=60)
def get_user_statistics(db: Session, user_id: int):
    """Get user statistics with caching."""
    return db.query(
        func.count(models.Task.id),
        func.sum(func.cast(models.Task.completed, Integer))
    ).filter(models.Task.user_id == user_id).first()
```

### Batch Operations

```python
def bulk_create_tasks(db: Session, tasks: List[schemas.TaskCreate], user_id: int):
    """Bulk create tasks efficiently."""
    db_tasks = [
        models.Task(
            title=task.title,
            description=task.description,
            user_id=user_id
        )
        for task in tasks
    ]
    db.bulk_save_objects(db_tasks)
    db.commit()

def bulk_update_tasks(db: Session, task_updates: List[dict]):
    """Bulk update tasks efficiently."""
    db.bulk_update_mappings(models.Task, task_updates)
    db.commit()
```
