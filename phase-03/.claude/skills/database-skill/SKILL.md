---
name: database-skill
description: |
  Database engineering skills for designing, implementing, and optimizing database systems.
  This skill should be used when working with database architecture, performance tuning, cloud databases, data pipelines, security implementation, or performing database engineering tasks across SQL, NoSQL, and cloud-native solutions.
---

# Database Engineer Skill

Provide expert-level guidance for designing, implementing, maintaining, and optimizing database systems across SQL, NoSQL, and cloud-native platforms with proper architecture, security, performance tuning, and compliance.

## What This Skill Does

- Design scalable database schemas and select appropriate technologies
- Optimize query performance and implement efficient indexing strategies
- Configure and manage cloud databases (AWS RDS, Azure SQL, Google Cloud SQL)
- Implement security controls and ensure compliance (GDPR, HIPAA, PCI DSS)
- Set up backup, recovery, and high availability solutions
- Monitor database performance and troubleshoot issues

## What This Skill Does NOT Do

- Application development (use backend skills)
- Data science or ML model training
- Frontend data visualization
- Network infrastructure setup
- Business intelligence reporting tools

---

## Version Compatibility

This skill covers:
- **PostgreSQL**: 12+
- **MySQL**: 8.0+
- **MongoDB**: 4.4+
- **Redis**: 6.0+
- **SQL Server**: 2019+
- **AWS RDS/Aurora**: Current versions
- **Azure SQL Database**: Current versions
- **Google Cloud SQL**: Current versions

For latest features and breaking changes, consult official documentation.

---

## Required Clarifications

Before implementation, clarify:

1. **Database type**: SQL (PostgreSQL, MySQL) or NoSQL (MongoDB, Redis, Cassandra)?
2. **Use case**: OLTP (transactional), OLAP (analytics), or hybrid?
3. **Scale requirements**: Expected data volume, query load, concurrent users?

## Optional Clarifications

4. **Cloud provider**: AWS, Azure, Google Cloud, or on-premises?
5. **Existing infrastructure**: Current database setup, migration needs?
6. **Compliance requirements**: GDPR, HIPAA, PCI DSS, or other regulations?
7. **ORM preference**: SQLAlchemy, Prisma, TypeORM, or raw SQL?

**If user doesn't provide clarifications**: Use sensible defaults (PostgreSQL for SQL, MongoDB for NoSQL, cloud-managed services) and document assumptions made.

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing database setup, ORM/query patterns, connection management |
| **Conversation** | User's specific requirements, scale, performance goals, compliance needs |
| **Skill References** | Database patterns, best practices, security standards from `references/` |
| **User Guidelines** | Project-specific conventions, team standards, deployment requirements |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

---

## Official Documentation

| Resource | URL | Use For |
|----------|-----|---------|
| PostgreSQL Docs | https://www.postgresql.org/docs/ | SQL patterns, advanced features, performance tuning |
| MySQL Docs | https://dev.mysql.com/doc/ | InnoDB engine, replication, optimization |
| MongoDB Docs | https://docs.mongodb.com/ | Document design, aggregation, sharding |
| Redis Docs | https://redis.io/documentation | Data structures, caching patterns, pub/sub |
| AWS RDS Docs | https://docs.aws.amazon.com/rds/ | Cloud database setup, Multi-AZ, read replicas |

---

## Core Competencies

### 1. Database Architecture & Design

- Design scalable database schemas for various use cases
- Select appropriate database technologies (SQL, NoSQL, graph, time-series)
- Create normalized and denormalized data models
- Implement proper indexing strategies
- Design for high availability and disaster recovery

**Details**: See `references/sql-databases.md` and `references/nosql-databases.md`

### 2. Performance Optimization

- Analyze and optimize slow queries
- Implement efficient indexing strategies
- Configure database parameters for optimal performance
- Monitor database performance metrics
- Plan capacity and scaling strategies

**Details**: See `references/performance-tuning.md`

### 3. Multi-Database Expertise

- Work with relational databases (PostgreSQL, MySQL, SQL Server)
- Implement NoSQL solutions (MongoDB, Cassandra, Redis)
- Use cloud-native databases (DynamoDB, Firestore)
- Apply polyglot persistence strategies
- Handle database migrations and versioning

**Details**: See `references/sql-databases.md` and `references/nosql-databases.md`

### 4. Cloud Database Management

- Deploy databases on AWS, Azure, and Google Cloud
- Implement managed database services (RDS, Cloud SQL)
- Configure serverless database options
- Manage cost optimization in cloud environments
- Implement hybrid and multi-cloud strategies

**Details**: See `references/cloud-databases.md`

### 5. Security & Compliance

- Implement data encryption (at rest and in transit)
- Configure access controls and authentication
- Ensure compliance with regulations (GDPR, HIPAA, PCI DSS)
- Conduct security audits and vulnerability assessments
- Implement audit logging and monitoring

**Details**: See `references/security-compliance.md`

---

## Common Mistakes to Avoid

### ❌ Mistake 1: N+1 Query Problem
**Problem**: Executing separate queries in a loop instead of joining

**Solution**: Use JOINs or batch queries
```sql
-- ❌ Bad: N+1 queries (1 + N queries)
-- SELECT * FROM users;
-- for each user: SELECT * FROM tasks WHERE user_id = ?;

-- ✅ Good: Single query with JOIN
SELECT u.*, t.*
FROM users u
LEFT JOIN tasks t ON u.id = t.user_id;
```

### ❌ Mistake 2: Missing Indexes
**Problem**: Full table scans on large tables

**Solution**: Create indexes on frequently queried columns
```sql
-- ❌ Bad: No index on foreign key
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(255)
);

-- ✅ Good: Index on foreign key
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(255)
);
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
```

### ❌ Mistake 3: No Connection Pooling
**Problem**: Creating new connection for each request

**Solution**: Use connection pooling
```python
# ❌ Bad: New connection each time
def get_data():
    conn = psycopg2.connect(...)
    cursor = conn.cursor()
    cursor.execute("SELECT ...")
    conn.close()

# ✅ Good: Connection pooling
from sqlalchemy import create_engine
engine = create_engine('postgresql://...', pool_size=20)
```

### ❌ Mistake 4: Storing Sensitive Data Unencrypted
**Problem**: Plain text passwords or credit cards

**Solution**: Encrypt sensitive data
```sql
-- ❌ Bad: Plain text password
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    password VARCHAR(255)  -- Plain text!
);

-- ✅ Good: Hashed password
CREATE EXTENSION pgcrypto;
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    password_hash TEXT  -- Bcrypt hash
);
INSERT INTO users (password_hash)
VALUES (crypt('password', gen_salt('bf')));
```

### ❌ Mistake 5: No Backup Strategy
**Problem**: Data loss with no recovery option

**Solution**: Implement automated backups
```bash
# ✅ Good: Automated daily backups
# PostgreSQL backup
pg_dump -U postgres myapp > backup_$(date +%Y%m%d).sql

# Enable point-in-time recovery
# AWS RDS: BackupRetentionPeriod=7
```

### ❌ Mistake 6: Ignoring Query Performance
**Problem**: Not monitoring or optimizing slow queries

**Solution**: Use EXPLAIN and monitor query performance
```sql
-- ✅ Good: Analyze query performance
EXPLAIN ANALYZE
SELECT * FROM tasks WHERE user_id = 123;

-- Look for: Seq Scan (bad) vs Index Scan (good)
```

**Details**: See `references/performance-tuning.md` for comprehensive optimization guide

---

## Implementation Workflows

### 1. Database Design and Implementation
```
1. Analyze requirements and data models
2. Select appropriate database technology
3. Design schema with proper normalization
4. Implement indexing and partitioning strategies
5. Create backup and recovery procedures
6. Test performance and scalability
```

### 2. Performance Tuning
```
1. Monitor database performance metrics
2. Identify slow queries and bottlenecks
3. Analyze execution plans
4. Optimize queries and indexes
5. Adjust configuration parameters
6. Validate performance improvements
```

### 3. Cloud Migration
```
1. Assess current database infrastructure
2. Choose appropriate cloud database service
3. Plan migration strategy and downtime windows
4. Execute migration with minimal disruption
5. Validate data integrity and performance
6. Optimize for cloud environment
```

### 4. Security Implementation
```
1. Enable encryption at rest and in transit
2. Configure access controls and authentication
3. Implement audit logging
4. Set up compliance monitoring
5. Conduct security assessment
6. Document security procedures
```

**Detailed workflows**: See reference files for comprehensive guides

---

## Key Implementation Patterns

### Database Design Checklist
- [ ] Select appropriate database type (SQL vs NoSQL)
- [ ] Design normalized schema with proper relationships
- [ ] Create indexes on foreign keys and frequently queried columns
- [ ] Implement constraints (NOT NULL, UNIQUE, CHECK)
- [ ] Plan for data growth and partitioning
- [ ] Document schema and relationships

### Performance Optimization Checklist
- [ ] Analyze slow queries with EXPLAIN
- [ ] Create appropriate indexes (avoid over-indexing)
- [ ] Optimize query patterns (avoid N+1 queries)
- [ ] Configure connection pooling
- [ ] Set up query caching where appropriate
- [ ] Monitor key performance metrics

### Security Implementation Checklist
- [ ] Enable encryption at rest and in transit
- [ ] Implement strong authentication (no default passwords)
- [ ] Configure role-based access control (RBAC)
- [ ] Enable audit logging for sensitive operations
- [ ] Regularly update and patch database software
- [ ] Conduct security audits and vulnerability assessments

### Migration Checklist
- [ ] Backup current database
- [ ] Test migration in staging environment
- [ ] Plan for minimal downtime
- [ ] Validate data integrity after migration
- [ ] Update connection strings and configurations
- [ ] Monitor performance post-migration

---

## Reference Files

Search patterns for comprehensive guides:

| File | Lines | Search For |
|------|-------|------------|
| `sql-databases.md` | 800+ | "PostgreSQL", "MySQL", "indexing", "query optimization", "transactions" |
| `nosql-databases.md` | 700+ | "MongoDB", "Redis", "Cassandra", "document design", "caching patterns" |
| `cloud-databases.md` | 700+ | "AWS RDS", "Aurora", "Azure SQL", "Cloud SQL", "DynamoDB" |
| `performance-tuning.md` | 800+ | "EXPLAIN", "slow queries", "connection pooling", "monitoring" |
| `security-compliance.md` | 800+ | "encryption", "GDPR", "HIPAA", "audit logging", "access control" |

**Reference contents**:
- `sql-databases.md` - PostgreSQL/MySQL patterns, query optimization, indexing, transactions
- `nosql-databases.md` - MongoDB/Redis/Cassandra patterns, document design, caching
- `cloud-databases.md` - AWS RDS/Aurora, Azure SQL, Google Cloud SQL, DynamoDB
- `performance-tuning.md` - Query optimization, monitoring, configuration tuning, scaling
- `security-compliance.md` - Encryption, access control, GDPR/HIPAA/PCI compliance, audit logging

---

## Best Practices

- Follow ACID properties and transaction management
- Implement proper backup and disaster recovery
- Use connection pooling and query optimization
- Apply security best practices consistently
- Monitor and alert on key metrics
- Document database schemas and processes
- Maintain version control for database changes
- Plan for scalability and growth
- Implement data governance policies
- Regular security assessments and updates

---

## Tools and Technologies

### Relational Databases
- PostgreSQL, MySQL, Microsoft SQL Server, Oracle
- SQLite for embedded systems

### NoSQL Databases
- MongoDB, Cassandra, Redis, Couchbase
- Amazon DynamoDB, Google Firestore

### Cloud Platforms
- Amazon RDS/Aurora, Google Cloud SQL, Azure SQL Database
- Amazon Redshift, Google BigQuery, Snowflake
- AWS Lambda, Azure Functions for serverless operations

### Monitoring & Management
- pgAdmin, phpMyAdmin, SQL Server Management Studio
- Prometheus, Grafana, Datadog
- Database monitoring tools specific to each platform

### Development Tools
- DBeaver, DataGrip, Navicat
- Liquibase, Flyway for database migrations
- Apache Kafka, Apache Airflow for data pipelines

---

## Output Format

When providing guidance, structure responses as:

**Database Selection**: Recommended database type and rationale
**Schema Design**: Table structures, relationships, and constraints
**Performance Strategy**: Indexing, query optimization, and caching approaches
**Security Measures**: Encryption, access control, and compliance requirements
**Deployment Strategy**: Cloud setup, backup procedures, and monitoring configuration
