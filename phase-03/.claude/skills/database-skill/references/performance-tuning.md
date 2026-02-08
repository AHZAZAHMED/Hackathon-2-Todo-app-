# Database Performance Tuning and Optimization

## Query Optimization

### Understanding Query Execution Plans

**PostgreSQL EXPLAIN**
```sql
-- Basic explain
EXPLAIN SELECT * FROM tasks WHERE user_id = 123;

-- Explain with actual execution statistics
EXPLAIN ANALYZE SELECT * FROM tasks WHERE user_id = 123;

-- Verbose output with additional details
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT * FROM tasks WHERE user_id = 123;

-- Key metrics to look for:
-- - Execution Time: Total time taken
-- - Planning Time: Time to plan the query
-- - Rows: Estimated vs actual rows
-- - Buffers: Shared hits (cache) vs reads (disk)
```

**Reading Execution Plans**
```sql
-- ❌ Bad: Sequential Scan (full table scan)
Seq Scan on tasks  (cost=0.00..1234.56 rows=10000 width=100)
  Filter: (user_id = 123)

-- ✅ Good: Index Scan (using index)
Index Scan using idx_tasks_user_id on tasks  (cost=0.42..8.44 rows=1 width=100)
  Index Cond: (user_id = 123)

-- ✅ Good: Index Only Scan (covered by index)
Index Only Scan using idx_tasks_covering on tasks  (cost=0.42..4.44 rows=1 width=20)
  Index Cond: (user_id = 123)
```

**MySQL EXPLAIN**
```sql
-- Basic explain
EXPLAIN SELECT * FROM tasks WHERE user_id = 123;

-- Extended explain with warnings
EXPLAIN EXTENDED SELECT * FROM tasks WHERE user_id = 123;
SHOW WARNINGS;

-- JSON format for detailed analysis
EXPLAIN FORMAT=JSON SELECT * FROM tasks WHERE user_id = 123;

-- Key columns to check:
-- - type: ALL (bad), index (good), ref (good), const (best)
-- - possible_keys: Available indexes
-- - key: Actually used index
-- - rows: Estimated rows examined
-- - Extra: Additional information (Using filesort, Using temporary)
```

### Index Optimization

**Index Selection Strategy**
```sql
-- ✅ Good: Index on foreign keys
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- ✅ Good: Index on frequently filtered columns
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);

-- ✅ Good: Composite index for common query patterns
CREATE INDEX idx_tasks_user_status_created
ON tasks(user_id, status, created_at DESC);

-- This index supports:
-- WHERE user_id = ?
-- WHERE user_id = ? AND status = ?
-- WHERE user_id = ? AND status = ? ORDER BY created_at DESC

-- ❌ Bad: Too many indexes (slows down writes)
CREATE INDEX idx_tasks_title ON tasks(title);
CREATE INDEX idx_tasks_description ON tasks(description);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
-- Each index adds overhead to INSERT/UPDATE/DELETE
```

**Index Maintenance**
```sql
-- PostgreSQL: Rebuild bloated indexes
REINDEX INDEX idx_tasks_user_id;
REINDEX TABLE tasks;

-- PostgreSQL: Analyze table statistics
ANALYZE tasks;

-- MySQL: Optimize table (rebuilds indexes)
OPTIMIZE TABLE tasks;

-- MySQL: Analyze table statistics
ANALYZE TABLE tasks;
```

**Unused Index Detection**
```sql
-- PostgreSQL: Find unused indexes
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
    AND indexrelname NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexrelid) DESC;

-- MySQL: Find unused indexes
SELECT
    object_schema,
    object_name,
    index_name
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE index_name IS NOT NULL
    AND count_star = 0
    AND object_schema != 'mysql'
ORDER BY object_schema, object_name;
```

### Query Rewriting

**Avoid SELECT ***
```sql
-- ❌ Bad: Select all columns
SELECT * FROM tasks WHERE user_id = 123;

-- ✅ Good: Select only needed columns
SELECT id, title, completed, created_at
FROM tasks
WHERE user_id = 123;

-- Benefits:
-- - Less data transferred
-- - Can use covering indexes
-- - Reduces memory usage
```

**Use EXISTS Instead of IN**
```sql
-- ❌ Bad: IN with subquery (can be slow)
SELECT * FROM users
WHERE id IN (SELECT DISTINCT user_id FROM tasks WHERE completed = false);

-- ✅ Good: EXISTS (stops at first match)
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM tasks t
    WHERE t.user_id = u.id AND t.completed = false
);
```

**Avoid Functions on Indexed Columns**
```sql
-- ❌ Bad: Function on indexed column (can't use index)
SELECT * FROM tasks
WHERE LOWER(title) = 'important task';

-- ✅ Good: Use functional index
CREATE INDEX idx_tasks_title_lower ON tasks(LOWER(title));
SELECT * FROM tasks
WHERE LOWER(title) = 'important task';

-- Or better: Store normalized data
ALTER TABLE tasks ADD COLUMN title_normalized TEXT;
UPDATE tasks SET title_normalized = LOWER(title);
CREATE INDEX idx_tasks_title_normalized ON tasks(title_normalized);
```

**Optimize OR Conditions**
```sql
-- ❌ Bad: OR condition (may not use indexes efficiently)
SELECT * FROM tasks
WHERE user_id = 123 OR assigned_to = 123;

-- ✅ Good: Use UNION (can use indexes on both)
SELECT * FROM tasks WHERE user_id = 123
UNION
SELECT * FROM tasks WHERE assigned_to = 123;
```

## Database Configuration Tuning

### PostgreSQL Configuration

**Memory Settings**
```ini
# postgresql.conf

# Shared Buffers: 25% of total RAM (up to 8-16GB)
shared_buffers = 4GB

# Effective Cache Size: 50-75% of total RAM
effective_cache_size = 12GB

# Work Memory: RAM / max_connections / 2-4
work_mem = 64MB

# Maintenance Work Memory: For VACUUM, CREATE INDEX
maintenance_work_mem = 1GB

# WAL Buffers: 16MB is usually sufficient
wal_buffers = 16MB

# Checkpoint Settings
checkpoint_completion_target = 0.9
max_wal_size = 2GB
min_wal_size = 1GB
```

**Connection Settings**
```ini
# Max Connections: Based on application needs
max_connections = 200

# Connection Pooling (use pgBouncer)
# Application → pgBouncer (1000 connections) → PostgreSQL (100 connections)
```

**Query Planner Settings**
```ini
# Random Page Cost: Lower for SSD
random_page_cost = 1.1  # Default: 4.0 (for HDD)

# Effective IO Concurrency: Number of concurrent disk I/O operations
effective_io_concurrency = 200  # For SSD

# Default Statistics Target: Higher = better estimates, slower ANALYZE
default_statistics_target = 100  # Default: 100
```

### MySQL Configuration

**InnoDB Settings**
```ini
# my.cnf

# Buffer Pool: 70-80% of total RAM
innodb_buffer_pool_size = 12G

# Buffer Pool Instances: 1 per GB (up to 64)
innodb_buffer_pool_instances = 12

# Log File Size: 25% of buffer pool size
innodb_log_file_size = 3G

# Flush Method: O_DIRECT for dedicated server
innodb_flush_method = O_DIRECT

# Flush Log at Transaction Commit
innodb_flush_log_at_trx_commit = 1  # ACID compliance
# = 2 for better performance, slight risk of data loss

# File Per Table
innodb_file_per_table = 1
```

**Query Cache (MySQL 5.7 and earlier)**
```ini
# Query Cache: Deprecated in MySQL 8.0
query_cache_type = 1
query_cache_size = 256M
query_cache_limit = 2M
```

**Connection Settings**
```ini
# Max Connections
max_connections = 200

# Connection Timeout
wait_timeout = 600
interactive_timeout = 600
```

## Monitoring and Profiling

### Key Performance Metrics

**Database Server Metrics**
```
# CPU Utilization
- Target: 40-70% average
- Alert: > 80% sustained

# Memory Usage
- Shared buffers hit ratio: > 99%
- Free memory: 20-30% available

# Disk I/O
- IOPS: Monitor against provisioned limits
- Latency: < 10ms for reads, < 20ms for writes
- Queue depth: < 10

# Network
- Throughput: Monitor against bandwidth limits
- Connections: < 80% of max_connections
```

**Query Performance Metrics**
```
# Query Execution Time
- p50: < 100ms
- p95: < 500ms
- p99: < 1000ms

# Slow Queries
- Count: < 1% of total queries
- Threshold: > 1 second

# Lock Waits
- Duration: < 100ms average
- Deadlocks: < 1 per hour
```

### PostgreSQL Monitoring

**pg_stat_statements**
```sql
-- Enable extension
CREATE EXTENSION pg_stat_statements;

-- Top 10 slowest queries by average time
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time,
    stddev_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Top 10 queries by total time
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- Queries with high variance
SELECT
    query,
    calls,
    mean_exec_time,
    stddev_exec_time,
    (stddev_exec_time / mean_exec_time) as coefficient_of_variation
FROM pg_stat_statements
WHERE calls > 100
ORDER BY coefficient_of_variation DESC
LIMIT 10;
```

**Connection and Lock Monitoring**
```sql
-- Active connections
SELECT
    datname,
    usename,
    application_name,
    client_addr,
    state,
    query,
    query_start,
    state_change
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;

-- Blocking queries
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

### MySQL Monitoring

**Performance Schema**
```sql
-- Enable Performance Schema
UPDATE performance_schema.setup_instruments
SET ENABLED = 'YES', TIMED = 'YES';

UPDATE performance_schema.setup_consumers
SET ENABLED = 'YES';

-- Top 10 slowest statements
SELECT
    DIGEST_TEXT,
    COUNT_STAR,
    AVG_TIMER_WAIT / 1000000000 as avg_ms,
    MAX_TIMER_WAIT / 1000000000 as max_ms,
    SUM_TIMER_WAIT / 1000000000 as total_ms
FROM performance_schema.events_statements_summary_by_digest
ORDER BY AVG_TIMER_WAIT DESC
LIMIT 10;

-- Table I/O statistics
SELECT
    object_schema,
    object_name,
    count_read,
    count_write,
    count_fetch,
    count_insert,
    count_update,
    count_delete
FROM performance_schema.table_io_waits_summary_by_table
WHERE object_schema NOT IN ('mysql', 'performance_schema', 'information_schema')
ORDER BY count_read + count_write DESC
LIMIT 10;
```

**InnoDB Monitoring**
```sql
-- InnoDB status
SHOW ENGINE INNODB STATUS;

-- Buffer pool statistics
SELECT
    pool_id,
    pool_size,
    free_buffers,
    database_pages,
    old_database_pages,
    modified_database_pages,
    pending_reads,
    pending_writes
FROM information_schema.innodb_buffer_pool_stats;

-- Transaction locks
SELECT
    trx_id,
    trx_state,
    trx_started,
    trx_requested_lock_id,
    trx_wait_started,
    trx_weight,
    trx_mysql_thread_id,
    trx_query
FROM information_schema.innodb_trx;
```

## Caching Strategies

### Application-Level Caching

**Redis Caching Pattern**
```python
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(ttl=300):
    """Decorator to cache function results in Redis."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{args}:{kwargs}"

            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            redis_client.setex(cache_key, ttl, json.dumps(result))

            return result
        return wrapper
    return decorator

@cache_result(ttl=600)
def get_user_tasks(user_id):
    """Get tasks for user (cached for 10 minutes)."""
    return db.query("SELECT * FROM tasks WHERE user_id = %s", user_id)
```

**Cache Invalidation**
```python
def update_task(task_id, data):
    """Update task and invalidate related caches."""
    # Get task to find user_id
    task = db.query("SELECT user_id FROM tasks WHERE id = %s", task_id)

    # Update database
    db.execute("UPDATE tasks SET ... WHERE id = %s", task_id)

    # Invalidate caches
    redis_client.delete(f"task:{task_id}")
    redis_client.delete(f"get_user_tasks:({task['user_id']},):{{}}")
    redis_client.delete(f"user:{task['user_id']}:task_count")
```

### Database Query Caching

**Materialized Views (PostgreSQL)**
```sql
-- Create materialized view for expensive aggregations
CREATE MATERIALIZED VIEW user_task_stats AS
SELECT
    user_id,
    COUNT(*) as total_tasks,
    COUNT(*) FILTER (WHERE completed = true) as completed_tasks,
    COUNT(*) FILTER (WHERE completed = false) as pending_tasks,
    MAX(created_at) as last_task_created
FROM tasks
GROUP BY user_id;

-- Create index on materialized view
CREATE INDEX idx_user_task_stats_user_id ON user_task_stats(user_id);

-- Refresh materialized view
REFRESH MATERIALIZED VIEW user_task_stats;

-- Refresh concurrently (non-blocking)
REFRESH MATERIALIZED VIEW CONCURRENTLY user_task_stats;

-- Query materialized view (fast)
SELECT * FROM user_task_stats WHERE user_id = 123;
```

**Summary Tables**
```sql
-- Create summary table
CREATE TABLE daily_task_summary (
    date DATE PRIMARY KEY,
    total_tasks INTEGER,
    completed_tasks INTEGER,
    created_tasks INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Populate summary table (run daily)
INSERT INTO daily_task_summary (date, total_tasks, completed_tasks, created_tasks)
SELECT
    CURRENT_DATE,
    COUNT(*),
    COUNT(*) FILTER (WHERE completed = true),
    COUNT(*) FILTER (WHERE DATE(created_at) = CURRENT_DATE)
FROM tasks
ON CONFLICT (date) DO UPDATE SET
    total_tasks = EXCLUDED.total_tasks,
    completed_tasks = EXCLUDED.completed_tasks,
    created_tasks = EXCLUDED.created_tasks,
    updated_at = CURRENT_TIMESTAMP;
```

## Scaling Strategies

### Vertical Scaling (Scale Up)

**When to Scale Up**
```
# Indicators:
- CPU utilization > 80% sustained
- Memory pressure (high swap usage)
- Disk I/O saturation
- Connection pool exhaustion

# Approach:
1. Monitor metrics to identify bottleneck
2. Increase appropriate resource (CPU, RAM, IOPS)
3. Test performance improvement
4. Adjust database configuration for new resources
```

### Horizontal Scaling (Scale Out)

**Read Replicas**
```python
# ✅ Good: Route reads to replicas
class DatabaseRouter:
    def __init__(self):
        self.primary = connect_to_primary()
        self.replicas = [connect_to_replica(i) for i in range(3)]
        self.replica_index = 0

    def get_connection(self, read_only=False):
        if read_only:
            # Round-robin across replicas
            replica = self.replicas[self.replica_index]
            self.replica_index = (self.replica_index + 1) % len(self.replicas)
            return replica
        else:
            return self.primary

# Usage
db_router = DatabaseRouter()

# Write to primary
conn = db_router.get_connection(read_only=False)
conn.execute("INSERT INTO tasks ...")

# Read from replica
conn = db_router.get_connection(read_only=True)
results = conn.query("SELECT * FROM tasks ...")
```

**Sharding**
```python
# ✅ Good: Shard by user_id
def get_shard(user_id, num_shards=4):
    """Determine shard for user_id."""
    return user_id % num_shards

def get_connection(user_id):
    """Get database connection for user's shard."""
    shard_id = get_shard(user_id)
    return shard_connections[shard_id]

# Usage
user_id = 12345
conn = get_connection(user_id)
tasks = conn.query("SELECT * FROM tasks WHERE user_id = %s", user_id)
```

### Connection Pooling

**pgBouncer Configuration**
```ini
# pgbouncer.ini

[databases]
myapp = host=localhost port=5432 dbname=myapp

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

# Pool mode
pool_mode = transaction  # or session, statement

# Connection limits
max_client_conn = 1000
default_pool_size = 25
reserve_pool_size = 5
reserve_pool_timeout = 3

# Timeouts
server_idle_timeout = 600
server_lifetime = 3600
```

**Application Connection Pool**
```python
# ✅ Good: Use connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://user:pass@localhost/myapp',
    poolclass=QueuePool,
    pool_size=20,          # Persistent connections
    max_overflow=10,       # Additional connections when needed
    pool_timeout=30,       # Wait time for connection
    pool_recycle=3600,     # Recycle connections after 1 hour
    pool_pre_ping=True     # Verify connection before using
)
```
