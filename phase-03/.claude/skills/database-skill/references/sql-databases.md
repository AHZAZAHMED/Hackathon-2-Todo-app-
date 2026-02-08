# SQL Database Patterns and Best Practices

## PostgreSQL

### Database Design

**Schema Design Patterns**
```sql
-- ✅ Good: Normalized schema with proper relationships
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for foreign keys and frequently queried columns
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

**Composite Indexes**
```sql
-- ✅ Good: Composite index for common query patterns
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);

-- Query that benefits from composite index
SELECT * FROM tasks
WHERE user_id = 123 AND completed = false
ORDER BY created_at DESC;

-- ❌ Bad: Separate indexes when composite would be better
CREATE INDEX idx_tasks_user_id_only ON tasks(user_id);
CREATE INDEX idx_tasks_completed_only ON tasks(completed);
-- This creates two separate indexes instead of one efficient composite
```

**Partial Indexes**
```sql
-- ✅ Good: Partial index for frequently filtered subset
CREATE INDEX idx_active_tasks ON tasks(user_id, created_at)
WHERE completed = false;

-- This index is smaller and faster for queries on incomplete tasks
SELECT * FROM tasks
WHERE user_id = 123 AND completed = false
ORDER BY created_at DESC;
```

### Query Optimization

**Using EXPLAIN ANALYZE**
```sql
-- Analyze query performance
EXPLAIN ANALYZE
SELECT u.username, COUNT(t.id) as task_count
FROM users u
LEFT JOIN tasks t ON u.id = t.user_id
WHERE t.completed = false
GROUP BY u.id, u.username
ORDER BY task_count DESC
LIMIT 10;

-- Look for:
-- - Seq Scan (bad for large tables, need index)
-- - Index Scan (good)
-- - Nested Loop (can be slow for large datasets)
-- - Hash Join (good for large datasets)
```

**Avoiding N+1 Queries**
```sql
-- ❌ Bad: N+1 query pattern (one query + N queries in loop)
-- Application code:
-- users = SELECT * FROM users;
-- for each user:
--     tasks = SELECT * FROM tasks WHERE user_id = user.id;

-- ✅ Good: Single query with JOIN
SELECT
    u.id,
    u.username,
    json_agg(
        json_build_object(
            'id', t.id,
            'title', t.title,
            'completed', t.completed
        )
    ) as tasks
FROM users u
LEFT JOIN tasks t ON u.id = t.user_id
GROUP BY u.id, u.username;
```

**Efficient Pagination**
```sql
-- ❌ Bad: OFFSET pagination (slow for large offsets)
SELECT * FROM tasks
ORDER BY created_at DESC
LIMIT 20 OFFSET 10000;  -- Scans and discards 10000 rows

-- ✅ Good: Cursor-based pagination (keyset pagination)
SELECT * FROM tasks
WHERE created_at < '2024-01-01 12:00:00'  -- Last seen timestamp
ORDER BY created_at DESC
LIMIT 20;

-- Even better with composite key
SELECT * FROM tasks
WHERE (created_at, id) < ('2024-01-01 12:00:00', 12345)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

**Batch Operations**
```sql
-- ❌ Bad: Multiple individual inserts
INSERT INTO tasks (user_id, title) VALUES (1, 'Task 1');
INSERT INTO tasks (user_id, title) VALUES (1, 'Task 2');
INSERT INTO tasks (user_id, title) VALUES (1, 'Task 3');

-- ✅ Good: Batch insert
INSERT INTO tasks (user_id, title) VALUES
    (1, 'Task 1'),
    (1, 'Task 2'),
    (1, 'Task 3');

-- ✅ Good: Batch update with CASE
UPDATE tasks
SET priority = CASE
    WHEN id = 1 THEN 'high'
    WHEN id = 2 THEN 'medium'
    WHEN id = 3 THEN 'low'
END
WHERE id IN (1, 2, 3);
```

### Advanced Features

**Common Table Expressions (CTEs)**
```sql
-- ✅ Good: Using CTE for complex queries
WITH user_stats AS (
    SELECT
        user_id,
        COUNT(*) as total_tasks,
        COUNT(*) FILTER (WHERE completed = true) as completed_tasks
    FROM tasks
    GROUP BY user_id
)
SELECT
    u.username,
    us.total_tasks,
    us.completed_tasks,
    ROUND(100.0 * us.completed_tasks / us.total_tasks, 2) as completion_rate
FROM users u
JOIN user_stats us ON u.id = us.user_id
WHERE us.total_tasks > 0
ORDER BY completion_rate DESC;
```

**Window Functions**
```sql
-- ✅ Good: Using window functions for rankings
SELECT
    user_id,
    title,
    created_at,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) as task_rank
FROM tasks
WHERE completed = false;

-- Get top 3 most recent tasks per user
SELECT * FROM (
    SELECT
        user_id,
        title,
        created_at,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) as rn
    FROM tasks
) ranked
WHERE rn <= 3;
```

**JSON Operations**
```sql
-- Store and query JSON data
CREATE TABLE user_preferences (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    settings JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Create GIN index for JSON queries
CREATE INDEX idx_user_preferences_settings ON user_preferences USING GIN (settings);

-- Query JSON data
SELECT user_id, settings->>'theme' as theme
FROM user_preferences
WHERE settings->>'notifications' = 'enabled';

-- Update JSON field
UPDATE user_preferences
SET settings = jsonb_set(settings, '{theme}', '"dark"')
WHERE user_id = 123;
```

**Full-Text Search**
```sql
-- Add tsvector column for full-text search
ALTER TABLE tasks ADD COLUMN search_vector tsvector;

-- Create GIN index
CREATE INDEX idx_tasks_search ON tasks USING GIN (search_vector);

-- Update search vector
UPDATE tasks
SET search_vector =
    setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(description, '')), 'B');

-- Create trigger to auto-update search vector
CREATE FUNCTION tasks_search_trigger() RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.description, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tasks_search_update
BEFORE INSERT OR UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION tasks_search_trigger();

-- Search query
SELECT title, ts_rank(search_vector, query) as rank
FROM tasks, to_tsquery('english', 'important & task') query
WHERE search_vector @@ query
ORDER BY rank DESC;
```

### Transactions and Concurrency

**Transaction Isolation Levels**
```sql
-- Read Committed (default)
BEGIN;
SELECT * FROM tasks WHERE id = 1;
-- Another transaction can modify this row
COMMIT;

-- Repeatable Read (prevents non-repeatable reads)
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT * FROM tasks WHERE id = 1;
-- Row values won't change even if another transaction commits
COMMIT;

-- Serializable (strictest isolation)
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- Prevents all concurrency anomalies
COMMIT;
```

**Row-Level Locking**
```sql
-- ✅ Good: Explicit locking for updates
BEGIN;
SELECT * FROM tasks WHERE id = 1 FOR UPDATE;
-- Row is locked, other transactions must wait
UPDATE tasks SET completed = true WHERE id = 1;
COMMIT;

-- FOR UPDATE SKIP LOCKED (useful for job queues)
BEGIN;
SELECT * FROM tasks
WHERE completed = false
ORDER BY created_at
LIMIT 1
FOR UPDATE SKIP LOCKED;
-- Skips locked rows, useful for concurrent workers
COMMIT;
```

**Optimistic Locking**
```sql
-- Add version column
ALTER TABLE tasks ADD COLUMN version INTEGER DEFAULT 1;

-- Update with version check
UPDATE tasks
SET
    completed = true,
    version = version + 1
WHERE id = 1 AND version = 5;

-- Check affected rows to detect conflicts
-- If 0 rows affected, another transaction modified the row
```

## MySQL

### Storage Engines

**InnoDB (Recommended)**
```sql
-- ✅ Good: Use InnoDB for ACID compliance and foreign keys
CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_completed (completed)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Character Sets and Collations**
```sql
-- ✅ Good: Use utf8mb4 for full Unicode support (including emojis)
CREATE DATABASE myapp
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- ❌ Bad: Using utf8 (only supports 3-byte UTF-8)
CREATE DATABASE myapp
CHARACTER SET utf8
COLLATE utf8_general_ci;
```

### Query Optimization

**Index Hints**
```sql
-- Force index usage when optimizer chooses wrong index
SELECT * FROM tasks
USE INDEX (idx_user_completed)
WHERE user_id = 123 AND completed = false;

-- Ignore specific index
SELECT * FROM tasks
IGNORE INDEX (idx_created_at)
WHERE user_id = 123;
```

**Covering Indexes**
```sql
-- ✅ Good: Covering index includes all queried columns
CREATE INDEX idx_tasks_covering ON tasks(user_id, completed, title, created_at);

-- Query uses only index, no table access needed
SELECT title, created_at
FROM tasks
WHERE user_id = 123 AND completed = false;
```

### Partitioning

**Range Partitioning**
```sql
-- Partition by date range
CREATE TABLE tasks (
    id INT AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (YEAR(created_at)) (
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);

-- Query specific partition
SELECT * FROM tasks PARTITION (p2024)
WHERE user_id = 123;
```

**List Partitioning**
```sql
-- Partition by discrete values
CREATE TABLE tasks (
    id INT AUTO_INCREMENT,
    user_id INT NOT NULL,
    status ENUM('pending', 'active', 'completed', 'archived'),
    PRIMARY KEY (id, status)
) PARTITION BY LIST COLUMNS(status) (
    PARTITION p_active VALUES IN ('pending', 'active'),
    PARTITION p_completed VALUES IN ('completed'),
    PARTITION p_archived VALUES IN ('archived')
);
```

## SQL Server

### Query Optimization

**Execution Plans**
```sql
-- View estimated execution plan
SET SHOWPLAN_ALL ON;
GO
SELECT * FROM tasks WHERE user_id = 123;
GO
SET SHOWPLAN_ALL OFF;
GO

-- View actual execution plan with statistics
SET STATISTICS IO ON;
SET STATISTICS TIME ON;
GO
SELECT * FROM tasks WHERE user_id = 123;
GO
SET STATISTICS IO OFF;
SET STATISTICS TIME OFF;
GO
```

**Index Recommendations**
```sql
-- Find missing indexes
SELECT
    migs.avg_user_impact,
    migs.avg_total_user_cost,
    migs.user_seeks,
    mid.statement,
    mid.equality_columns,
    mid.inequality_columns,
    mid.included_columns
FROM sys.dm_db_missing_index_groups mig
INNER JOIN sys.dm_db_missing_index_group_stats migs ON mig.index_group_handle = migs.group_handle
INNER JOIN sys.dm_db_missing_index_details mid ON mig.index_handle = mid.index_handle
ORDER BY migs.avg_user_impact DESC;
```

### Temporal Tables

**System-Versioned Tables**
```sql
-- Create temporal table with history
CREATE TABLE tasks (
    id INT PRIMARY KEY,
    user_id INT NOT NULL,
    title NVARCHAR(255) NOT NULL,
    completed BIT DEFAULT 0,
    valid_from DATETIME2 GENERATED ALWAYS AS ROW START,
    valid_to DATETIME2 GENERATED ALWAYS AS ROW END,
    PERIOD FOR SYSTEM_TIME (valid_from, valid_to)
) WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = dbo.tasks_history));

-- Query historical data
SELECT * FROM tasks
FOR SYSTEM_TIME AS OF '2024-01-01 12:00:00'
WHERE user_id = 123;

-- Query all changes
SELECT * FROM tasks
FOR SYSTEM_TIME ALL
WHERE id = 1
ORDER BY valid_from;
```

## Common SQL Patterns

### Upsert (Insert or Update)

**PostgreSQL**
```sql
-- ON CONFLICT clause
INSERT INTO tasks (id, user_id, title, completed)
VALUES (1, 123, 'Task 1', false)
ON CONFLICT (id)
DO UPDATE SET
    title = EXCLUDED.title,
    completed = EXCLUDED.completed,
    updated_at = CURRENT_TIMESTAMP;
```

**MySQL**
```sql
-- ON DUPLICATE KEY UPDATE
INSERT INTO tasks (id, user_id, title, completed)
VALUES (1, 123, 'Task 1', false)
ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    completed = VALUES(completed),
    updated_at = CURRENT_TIMESTAMP;

-- Or use REPLACE (deletes and inserts)
REPLACE INTO tasks (id, user_id, title, completed)
VALUES (1, 123, 'Task 1', false);
```

**SQL Server**
```sql
-- MERGE statement
MERGE tasks AS target
USING (SELECT 1 AS id, 123 AS user_id, 'Task 1' AS title, 0 AS completed) AS source
ON target.id = source.id
WHEN MATCHED THEN
    UPDATE SET
        title = source.title,
        completed = source.completed,
        updated_at = GETDATE()
WHEN NOT MATCHED THEN
    INSERT (id, user_id, title, completed)
    VALUES (source.id, source.user_id, source.title, source.completed);
```

### Recursive Queries

**Hierarchical Data**
```sql
-- Category tree structure
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER REFERENCES categories(id)
);

-- Get all descendants of a category
WITH RECURSIVE category_tree AS (
    -- Base case: start with parent category
    SELECT id, name, parent_id, 1 as level
    FROM categories
    WHERE id = 1

    UNION ALL

    -- Recursive case: get children
    SELECT c.id, c.name, c.parent_id, ct.level + 1
    FROM categories c
    INNER JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree
ORDER BY level, name;

-- Get path from leaf to root
WITH RECURSIVE category_path AS (
    -- Base case: start with leaf category
    SELECT id, name, parent_id, name as path
    FROM categories
    WHERE id = 10

    UNION ALL

    -- Recursive case: traverse up to parent
    SELECT c.id, c.name, c.parent_id, c.name || ' > ' || cp.path
    FROM categories c
    INNER JOIN category_path cp ON c.id = cp.parent_id
)
SELECT path FROM category_path
WHERE parent_id IS NULL;
```

## Performance Best Practices

### Connection Pooling

**Configuration Guidelines**
```
Pool Size = (Number of CPU cores × 2) + Number of disks

Example for 4-core server with 1 disk:
Pool Size = (4 × 2) + 1 = 9 connections

Adjust based on:
- Application workload (read-heavy vs write-heavy)
- Query complexity (simple vs complex)
- Connection hold time (short vs long)
```

### Query Caching

**Application-Level Caching**
```python
# ✅ Good: Cache frequently accessed data
import redis

cache = redis.Redis(host='localhost', port=6379)

def get_user_tasks(user_id):
    cache_key = f"user:{user_id}:tasks"

    # Try cache first
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)

    # Query database
    tasks = db.query("SELECT * FROM tasks WHERE user_id = %s", user_id)

    # Cache for 5 minutes
    cache.setex(cache_key, 300, json.dumps(tasks))

    return tasks
```

### Monitoring Queries

**Slow Query Log (MySQL)**
```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;  -- Log queries taking > 2 seconds
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow-query.log';
```

**pg_stat_statements (PostgreSQL)**
```sql
-- Enable extension
CREATE EXTENSION pg_stat_statements;

-- View slowest queries
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```
