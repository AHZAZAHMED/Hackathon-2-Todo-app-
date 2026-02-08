# NoSQL Database Patterns and Best Practices

## MongoDB

### Document Design

**Embedding vs Referencing**
```javascript
// ✅ Good: Embed when data is accessed together (one-to-few)
{
  _id: ObjectId("..."),
  username: "john_doe",
  email: "john@example.com",
  profile: {
    firstName: "John",
    lastName: "Doe",
    avatar: "https://..."
  },
  settings: {
    theme: "dark",
    notifications: true
  }
}

// ✅ Good: Reference when data is large or accessed independently (one-to-many)
// Users collection
{
  _id: ObjectId("user123"),
  username: "john_doe",
  email: "john@example.com"
}

// Tasks collection
{
  _id: ObjectId("task456"),
  userId: ObjectId("user123"),
  title: "Complete project",
  completed: false,
  createdAt: ISODate("2024-01-01")
}

// ❌ Bad: Embedding large arrays (unbounded growth)
{
  _id: ObjectId("user123"),
  username: "john_doe",
  tasks: [
    { title: "Task 1", completed: false },
    { title: "Task 2", completed: true },
    // ... potentially thousands of tasks
  ]
}
```

**Schema Validation**
```javascript
// ✅ Good: Define schema validation rules
db.createCollection("tasks", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["userId", "title", "completed", "createdAt"],
      properties: {
        userId: {
          bsonType: "objectId",
          description: "must be an objectId and is required"
        },
        title: {
          bsonType: "string",
          minLength: 1,
          maxLength: 255,
          description: "must be a string between 1-255 characters"
        },
        completed: {
          bsonType: "bool",
          description: "must be a boolean"
        },
        priority: {
          enum: ["low", "medium", "high"],
          description: "must be one of the enum values"
        },
        createdAt: {
          bsonType: "date",
          description: "must be a date"
        }
      }
    }
  }
});
```

### Indexing Strategies

**Single Field Indexes**
```javascript
// Create index on userId for fast lookups
db.tasks.createIndex({ userId: 1 });

// Create unique index
db.users.createIndex({ email: 1 }, { unique: true });

// Create sparse index (only indexes documents with the field)
db.tasks.createIndex({ dueDate: 1 }, { sparse: true });
```

**Compound Indexes**
```javascript
// ✅ Good: Compound index for common query patterns
db.tasks.createIndex({ userId: 1, completed: 1, createdAt: -1 });

// This index supports queries like:
// - { userId: 123 }
// - { userId: 123, completed: false }
// - { userId: 123, completed: false, createdAt: ... }

// Query using the index
db.tasks.find({ userId: ObjectId("..."), completed: false })
  .sort({ createdAt: -1 })
  .limit(20);
```

**Text Indexes**
```javascript
// Create text index for full-text search
db.tasks.createIndex({ title: "text", description: "text" });

// Search with text index
db.tasks.find({
  $text: { $search: "important meeting" }
});

// Search with relevance score
db.tasks.find(
  { $text: { $search: "important meeting" } },
  { score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } });
```

**Geospatial Indexes**
```javascript
// Create 2dsphere index for location queries
db.locations.createIndex({ coordinates: "2dsphere" });

// Store location data
db.locations.insertOne({
  name: "Office",
  coordinates: {
    type: "Point",
    coordinates: [-73.97, 40.77]  // [longitude, latitude]
  }
});

// Find nearby locations
db.locations.find({
  coordinates: {
    $near: {
      $geometry: {
        type: "Point",
        coordinates: [-73.98, 40.78]
      },
      $maxDistance: 1000  // meters
    }
  }
});
```

### Query Optimization

**Aggregation Pipeline**
```javascript
// ✅ Good: Efficient aggregation with early filtering
db.tasks.aggregate([
  // Stage 1: Filter early to reduce documents
  { $match: { userId: ObjectId("..."), completed: false } },

  // Stage 2: Sort
  { $sort: { createdAt: -1 } },

  // Stage 3: Limit
  { $limit: 20 },

  // Stage 4: Lookup (join) with users
  {
    $lookup: {
      from: "users",
      localField: "userId",
      foreignField: "_id",
      as: "user"
    }
  },

  // Stage 5: Unwind user array
  { $unwind: "$user" },

  // Stage 6: Project final shape
  {
    $project: {
      title: 1,
      completed: 1,
      createdAt: 1,
      "user.username": 1,
      "user.email": 1
    }
  }
]);

// ❌ Bad: Filtering after expensive operations
db.tasks.aggregate([
  { $lookup: { ... } },  // Expensive join on all documents
  { $unwind: "$user" },
  { $match: { userId: ObjectId("...") } }  // Filter too late
]);
```

**Covered Queries**
```javascript
// Create index with all queried fields
db.tasks.createIndex({ userId: 1, completed: 1, title: 1, createdAt: 1 });

// ✅ Good: Covered query (uses only index, no document fetch)
db.tasks.find(
  { userId: ObjectId("..."), completed: false },
  { _id: 0, title: 1, createdAt: 1 }  // Exclude _id, project only indexed fields
);

// Verify it's covered
db.tasks.find(
  { userId: ObjectId("..."), completed: false },
  { _id: 0, title: 1, createdAt: 1 }
).explain("executionStats");
// Look for: totalDocsExamined: 0 (no documents fetched)
```

**Bulk Operations**
```javascript
// ✅ Good: Bulk write for multiple operations
const bulkOps = [
  {
    insertOne: {
      document: { userId: ObjectId("..."), title: "Task 1" }
    }
  },
  {
    updateOne: {
      filter: { _id: ObjectId("...") },
      update: { $set: { completed: true } }
    }
  },
  {
    deleteOne: {
      filter: { _id: ObjectId("...") }
    }
  }
];

db.tasks.bulkWrite(bulkOps, { ordered: false });

// ❌ Bad: Individual operations in loop
for (const task of tasks) {
  db.tasks.insertOne(task);  // Separate network round-trip for each
}
```

### Transactions

**Multi-Document Transactions**
```javascript
// ✅ Good: Use transactions for multi-document operations
const session = client.startSession();

try {
  session.startTransaction();

  // Transfer task ownership
  await db.tasks.updateOne(
    { _id: taskId },
    { $set: { userId: newUserId } },
    { session }
  );

  // Log the transfer
  await db.auditLog.insertOne(
    {
      action: "transfer_task",
      taskId: taskId,
      fromUser: oldUserId,
      toUser: newUserId,
      timestamp: new Date()
    },
    { session }
  );

  await session.commitTransaction();
} catch (error) {
  await session.abortTransaction();
  throw error;
} finally {
  session.endSession();
}
```

### Change Streams

**Real-Time Data Monitoring**
```javascript
// Watch for changes in tasks collection
const changeStream = db.tasks.watch([
  { $match: { "fullDocument.userId": ObjectId("...") } }
]);

changeStream.on("change", (change) => {
  console.log("Change detected:", change);

  switch (change.operationType) {
    case "insert":
      console.log("New task:", change.fullDocument);
      break;
    case "update":
      console.log("Updated task:", change.documentKey);
      break;
    case "delete":
      console.log("Deleted task:", change.documentKey);
      break;
  }
});
```

## Redis

### Data Structures

**Strings**
```redis
# ✅ Good: Cache user session
SET session:user123 "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." EX 3600

# Get session
GET session:user123

# Increment counter
INCR page:views:homepage

# Set if not exists (distributed lock)
SET lock:resource:123 "worker1" NX EX 30
```

**Hashes**
```redis
# ✅ Good: Store user object
HMSET user:123 username "john_doe" email "john@example.com" status "active"

# Get specific fields
HMGET user:123 username email

# Get all fields
HGETALL user:123

# Increment numeric field
HINCRBY user:123 login_count 1
```

**Lists**
```redis
# ✅ Good: Task queue (FIFO)
LPUSH queue:tasks "task1"
LPUSH queue:tasks "task2"
RPOP queue:tasks  # Returns "task1"

# Recent items (keep last 100)
LPUSH recent:views:user123 "page1"
LTRIM recent:views:user123 0 99

# Blocking pop (wait for items)
BRPOP queue:tasks 30  # Wait up to 30 seconds
```

**Sets**
```redis
# ✅ Good: Unique tags
SADD task:123:tags "urgent" "work" "meeting"

# Check membership
SISMEMBER task:123:tags "urgent"  # Returns 1

# Get all members
SMEMBERS task:123:tags

# Set operations
SINTER task:123:tags task:456:tags  # Intersection
SUNION task:123:tags task:456:tags  # Union
SDIFF task:123:tags task:456:tags   # Difference
```

**Sorted Sets**
```redis
# ✅ Good: Leaderboard
ZADD leaderboard 100 "user1" 200 "user2" 150 "user3"

# Get top 10
ZREVRANGE leaderboard 0 9 WITHSCORES

# Get rank
ZREVRANK leaderboard "user2"  # Returns 0 (highest score)

# Increment score
ZINCRBY leaderboard 50 "user1"

# Get by score range
ZRANGEBYSCORE leaderboard 100 200
```

### Caching Patterns

**Cache-Aside (Lazy Loading)**
```python
# ✅ Good: Cache-aside pattern
def get_user(user_id):
    cache_key = f"user:{user_id}"

    # Try cache first
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # Cache miss - query database
    user = db.query("SELECT * FROM users WHERE id = %s", user_id)

    # Store in cache
    redis.setex(cache_key, 3600, json.dumps(user))

    return user
```

**Write-Through Cache**
```python
# ✅ Good: Write-through pattern
def update_user(user_id, data):
    # Update database
    db.execute("UPDATE users SET ... WHERE id = %s", user_id)

    # Update cache immediately
    cache_key = f"user:{user_id}"
    user = db.query("SELECT * FROM users WHERE id = %s", user_id)
    redis.setex(cache_key, 3600, json.dumps(user))

    return user
```

**Cache Invalidation**
```python
# ✅ Good: Invalidate related caches
def delete_task(task_id):
    task = db.query("SELECT user_id FROM tasks WHERE id = %s", task_id)

    # Delete from database
    db.execute("DELETE FROM tasks WHERE id = %s", task_id)

    # Invalidate caches
    redis.delete(f"task:{task_id}")
    redis.delete(f"user:{task['user_id']}:tasks")
    redis.delete(f"user:{task['user_id']}:task_count")
```

### Pub/Sub

**Real-Time Notifications**
```python
# Publisher
redis.publish("notifications:user123", json.dumps({
    "type": "task_completed",
    "taskId": 456,
    "timestamp": datetime.now().isoformat()
}))

# Subscriber
pubsub = redis.pubsub()
pubsub.subscribe("notifications:user123")

for message in pubsub.listen():
    if message["type"] == "message":
        data = json.loads(message["data"])
        print(f"Notification: {data}")
```

## Cassandra

### Data Modeling

**Partition Key Design**
```cql
-- ✅ Good: Partition by user_id for even distribution
CREATE TABLE tasks (
    user_id UUID,
    task_id UUID,
    title TEXT,
    completed BOOLEAN,
    created_at TIMESTAMP,
    PRIMARY KEY (user_id, task_id)
) WITH CLUSTERING ORDER BY (task_id DESC);

-- Query pattern: Get all tasks for a user
SELECT * FROM tasks WHERE user_id = ?;

-- ❌ Bad: Single partition key for all data
CREATE TABLE tasks (
    partition_key TEXT,  -- Always 'tasks'
    task_id UUID,
    user_id UUID,
    title TEXT,
    PRIMARY KEY (partition_key, task_id)
);
-- This creates a hot partition with all data
```

**Composite Partition Key**
```cql
-- ✅ Good: Composite partition key for time-series data
CREATE TABLE task_events (
    user_id UUID,
    year_month TEXT,  -- '2024-01'
    event_time TIMESTAMP,
    event_type TEXT,
    task_id UUID,
    PRIMARY KEY ((user_id, year_month), event_time)
) WITH CLUSTERING ORDER BY (event_time DESC);

-- Query pattern: Get events for user in specific month
SELECT * FROM task_events
WHERE user_id = ? AND year_month = '2024-01';
```

**Denormalization**
```cql
-- ✅ Good: Denormalize for query patterns
-- Table 1: Tasks by user
CREATE TABLE tasks_by_user (
    user_id UUID,
    task_id UUID,
    title TEXT,
    completed BOOLEAN,
    created_at TIMESTAMP,
    PRIMARY KEY (user_id, created_at, task_id)
) WITH CLUSTERING ORDER BY (created_at DESC);

-- Table 2: Tasks by status
CREATE TABLE tasks_by_status (
    status TEXT,
    created_at TIMESTAMP,
    task_id UUID,
    user_id UUID,
    title TEXT,
    PRIMARY KEY (status, created_at, task_id)
) WITH CLUSTERING ORDER BY (created_at DESC);

-- Write to both tables
BEGIN BATCH
    INSERT INTO tasks_by_user (user_id, task_id, title, completed, created_at)
    VALUES (?, ?, ?, ?, ?);

    INSERT INTO tasks_by_status (status, created_at, task_id, user_id, title)
    VALUES ('pending', ?, ?, ?, ?);
APPLY BATCH;
```

### Query Patterns

**Efficient Queries**
```cql
-- ✅ Good: Query with partition key
SELECT * FROM tasks WHERE user_id = ?;

-- ✅ Good: Query with partition key and clustering columns
SELECT * FROM tasks
WHERE user_id = ? AND created_at > '2024-01-01';

-- ❌ Bad: Query without partition key (requires ALLOW FILTERING)
SELECT * FROM tasks WHERE completed = true ALLOW FILTERING;
-- This scans all partitions - very slow
```

**Pagination**
```cql
-- ✅ Good: Use paging state for pagination
SELECT * FROM tasks
WHERE user_id = ?
LIMIT 20;

-- Get next page using paging state from previous query
-- (handled by driver, not manual)
```

### Consistency Levels

**Tunable Consistency**
```cql
-- Strong consistency: QUORUM reads and writes
-- Write with QUORUM
INSERT INTO tasks (user_id, task_id, title)
VALUES (?, ?, ?)
USING CONSISTENCY QUORUM;

-- Read with QUORUM
SELECT * FROM tasks WHERE user_id = ?
USING CONSISTENCY QUORUM;

-- Eventual consistency: ONE
-- Faster but may read stale data
SELECT * FROM tasks WHERE user_id = ?
USING CONSISTENCY ONE;
```

## DynamoDB

### Table Design

**Single Table Design**
```javascript
// ✅ Good: Single table design with composite keys
// Table: AppData
// PK: Partition Key, SK: Sort Key

// User item
{
  PK: "USER#123",
  SK: "METADATA",
  username: "john_doe",
  email: "john@example.com"
}

// Task items
{
  PK: "USER#123",
  SK: "TASK#2024-01-01#456",
  title: "Complete project",
  completed: false
}

// Query all tasks for user
const params = {
  TableName: "AppData",
  KeyConditionExpression: "PK = :pk AND begins_with(SK, :sk)",
  ExpressionAttributeValues: {
    ":pk": "USER#123",
    ":sk": "TASK#"
  }
};
```

**Global Secondary Index (GSI)**
```javascript
// ✅ Good: GSI for alternate access patterns
// GSI: GSI1
// GSI1PK: Status, GSI1SK: CreatedAt

// Item with GSI attributes
{
  PK: "USER#123",
  SK: "TASK#456",
  GSI1PK: "STATUS#pending",
  GSI1SK: "2024-01-01T12:00:00Z",
  title: "Task 1"
}

// Query all pending tasks
const params = {
  TableName: "AppData",
  IndexName: "GSI1",
  KeyConditionExpression: "GSI1PK = :status",
  ExpressionAttributeValues: {
    ":status": "STATUS#pending"
  }
};
```

### Conditional Writes

**Optimistic Locking**
```javascript
// ✅ Good: Conditional update with version check
const params = {
  TableName: "AppData",
  Key: { PK: "USER#123", SK: "TASK#456" },
  UpdateExpression: "SET completed = :completed, version = :newVersion",
  ConditionExpression: "version = :currentVersion",
  ExpressionAttributeValues: {
    ":completed": true,
    ":newVersion": 2,
    ":currentVersion": 1
  }
};

try {
  await dynamodb.update(params).promise();
} catch (error) {
  if (error.code === "ConditionalCheckFailedException") {
    // Version conflict - item was modified by another process
    console.log("Conflict detected, retry with latest version");
  }
}
```

### Batch Operations

**BatchGetItem**
```javascript
// ✅ Good: Batch get multiple items
const params = {
  RequestItems: {
    "AppData": {
      Keys: [
        { PK: "USER#123", SK: "TASK#456" },
        { PK: "USER#123", SK: "TASK#789" },
        { PK: "USER#456", SK: "TASK#123" }
      ]
    }
  }
};

const result = await dynamodb.batchGet(params).promise();
```

**BatchWriteItem**
```javascript
// ✅ Good: Batch write up to 25 items
const params = {
  RequestItems: {
    "AppData": [
      {
        PutRequest: {
          Item: { PK: "USER#123", SK: "TASK#456", title: "Task 1" }
        }
      },
      {
        DeleteRequest: {
          Key: { PK: "USER#123", SK: "TASK#789" }
        }
      }
    ]
  }
};

await dynamodb.batchWrite(params).promise();
```

## Common NoSQL Anti-Patterns

### ❌ Anti-Pattern 1: Using NoSQL Like SQL
```javascript
// ❌ Bad: Normalizing data in NoSQL
// Users collection
{ _id: 1, username: "john" }

// Tasks collection with reference
{ _id: 1, userId: 1, title: "Task 1" }

// Requires application-level join
const user = db.users.findOne({ _id: 1 });
const tasks = db.tasks.find({ userId: user._id });

// ✅ Good: Embed related data
{
  _id: 1,
  username: "john",
  recentTasks: [
    { title: "Task 1", completed: false },
    { title: "Task 2", completed: true }
  ]
}
```

### ❌ Anti-Pattern 2: Not Considering Query Patterns
```javascript
// ❌ Bad: Schema doesn't match query patterns
// Need to query tasks by status, but no index
db.tasks.find({ status: "pending" });  // Full collection scan

// ✅ Good: Design schema for query patterns
db.tasks.createIndex({ status: 1, createdAt: -1 });
```

### ❌ Anti-Pattern 3: Unbounded Array Growth
```javascript
// ❌ Bad: Array can grow indefinitely
{
  userId: 123,
  tasks: [/* potentially thousands of tasks */]
}

// ✅ Good: Use separate collection with reference
// Or limit array size with $slice
db.users.updateOne(
  { _id: 123 },
  {
    $push: {
      recentTasks: {
        $each: [newTask],
        $slice: -10  // Keep only last 10
      }
    }
  }
);
```
