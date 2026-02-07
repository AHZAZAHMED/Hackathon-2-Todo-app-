# Cloud Database Patterns and Best Practices

## AWS RDS (Relational Database Service)

### Database Instance Configuration

**Instance Types and Sizing**
```
# General Purpose (T3/T4g) - Burstable performance
- db.t3.micro: 1 vCPU, 1 GB RAM - Development/testing
- db.t3.small: 2 vCPU, 2 GB RAM - Small applications
- db.t3.medium: 2 vCPU, 4 GB RAM - Medium workloads

# Memory Optimized (R5/R6g) - High memory for caching
- db.r5.large: 2 vCPU, 16 GB RAM - Memory-intensive workloads
- db.r5.xlarge: 4 vCPU, 32 GB RAM - Large databases

# Compute Optimized (C5/C6g) - High CPU performance
- db.c5.large: 2 vCPU, 4 GB RAM - Compute-intensive workloads
```

**Storage Types**
```
# General Purpose SSD (gp3) - Recommended
- Baseline: 3,000 IOPS, 125 MB/s throughput
- Scalable: Up to 16,000 IOPS, 1,000 MB/s
- Cost-effective for most workloads

# Provisioned IOPS SSD (io1/io2) - High performance
- Up to 64,000 IOPS per instance
- Use for I/O intensive workloads
- Higher cost

# Magnetic (standard) - Legacy, not recommended
```

### High Availability

**Multi-AZ Deployment**
```python
# ✅ Good: Enable Multi-AZ for production
import boto3

rds = boto3.client('rds')

response = rds.create_db_instance(
    DBInstanceIdentifier='myapp-prod',
    DBInstanceClass='db.r5.large',
    Engine='postgres',
    EngineVersion='15.3',
    MasterUsername='admin',
    MasterUserPassword='SecurePassword123!',
    AllocatedStorage=100,
    StorageType='gp3',
    MultiAZ=True,  # Enable Multi-AZ
    BackupRetentionPeriod=7,
    PreferredBackupWindow='03:00-04:00',
    PreferredMaintenanceWindow='sun:04:00-sun:05:00',
    PubliclyAccessible=False,
    VpcSecurityGroupIds=['sg-12345678'],
    DBSubnetGroupName='myapp-subnet-group',
    StorageEncrypted=True,
    EnableCloudwatchLogsExports=['postgresql'],
    DeletionProtection=True
)
```

**Read Replicas**
```python
# ✅ Good: Create read replicas for read-heavy workloads
response = rds.create_db_instance_read_replica(
    DBInstanceIdentifier='myapp-prod-replica-1',
    SourceDBInstanceIdentifier='myapp-prod',
    DBInstanceClass='db.r5.large',
    PubliclyAccessible=False,
    AvailabilityZone='us-east-1b'
)

# Application code: Route reads to replica
# Primary endpoint: myapp-prod.abc123.us-east-1.rds.amazonaws.com
# Replica endpoint: myapp-prod-replica-1.abc123.us-east-1.rds.amazonaws.com

# Connection routing
WRITE_DB_HOST = os.getenv('PRIMARY_DB_HOST')
READ_DB_HOST = os.getenv('REPLICA_DB_HOST')

def get_db_connection(read_only=False):
    host = READ_DB_HOST if read_only else WRITE_DB_HOST
    return psycopg2.connect(
        host=host,
        database='myapp',
        user='admin',
        password=os.getenv('DB_PASSWORD')
    )
```

### Backup and Recovery

**Automated Backups**
```python
# ✅ Good: Configure automated backups
response = rds.modify_db_instance(
    DBInstanceIdentifier='myapp-prod',
    BackupRetentionPeriod=30,  # Keep backups for 30 days
    PreferredBackupWindow='03:00-04:00',  # Daily backup window
    ApplyImmediately=False  # Apply during maintenance window
)
```

**Manual Snapshots**
```python
# Create manual snapshot before major changes
response = rds.create_db_snapshot(
    DBSnapshotIdentifier='myapp-prod-before-migration-2024-01-01',
    DBInstanceIdentifier='myapp-prod',
    Tags=[
        {'Key': 'Purpose', 'Value': 'Pre-migration backup'},
        {'Key': 'Date', 'Value': '2024-01-01'}
    ]
)

# Restore from snapshot
response = rds.restore_db_instance_from_db_snapshot(
    DBInstanceIdentifier='myapp-prod-restored',
    DBSnapshotIdentifier='myapp-prod-before-migration-2024-01-01',
    DBInstanceClass='db.r5.large',
    MultiAZ=True
)
```

**Point-in-Time Recovery**
```python
# ✅ Good: Restore to specific point in time
response = rds.restore_db_instance_to_point_in_time(
    SourceDBInstanceIdentifier='myapp-prod',
    TargetDBInstanceIdentifier='myapp-prod-pitr',
    RestoreTime=datetime(2024, 1, 1, 12, 30, 0),  # Restore to this time
    UseLatestRestorableTime=False
)
```

### Performance Insights

**Enable Performance Insights**
```python
# ✅ Good: Enable Performance Insights for monitoring
response = rds.modify_db_instance(
    DBInstanceIdentifier='myapp-prod',
    EnablePerformanceInsights=True,
    PerformanceInsightsRetentionPeriod=7,  # Days to retain data
    ApplyImmediately=False
)
```

**Query Performance Monitoring**
```sql
-- PostgreSQL: View slow queries
SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- MySQL: Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
```

## Amazon Aurora

### Aurora PostgreSQL/MySQL

**Cluster Configuration**
```python
# ✅ Good: Create Aurora cluster with multiple instances
response = rds.create_db_cluster(
    DBClusterIdentifier='myapp-aurora-cluster',
    Engine='aurora-postgresql',
    EngineVersion='15.3',
    MasterUsername='admin',
    MasterUserPassword='SecurePassword123!',
    DatabaseName='myapp',
    BackupRetentionPeriod=7,
    PreferredBackupWindow='03:00-04:00',
    PreferredMaintenanceWindow='sun:04:00-sun:05:00',
    StorageEncrypted=True,
    EnableCloudwatchLogsExports=['postgresql'],
    DeletionProtection=True
)

# Create primary instance
response = rds.create_db_instance(
    DBInstanceIdentifier='myapp-aurora-instance-1',
    DBInstanceClass='db.r5.large',
    Engine='aurora-postgresql',
    DBClusterIdentifier='myapp-aurora-cluster'
)

# Create read replica instance
response = rds.create_db_instance(
    DBInstanceIdentifier='myapp-aurora-instance-2',
    DBInstanceClass='db.r5.large',
    Engine='aurora-postgresql',
    DBClusterIdentifier='myapp-aurora-cluster'
)
```

**Aurora Serverless v2**
```python
# ✅ Good: Aurora Serverless for variable workloads
response = rds.create_db_cluster(
    DBClusterIdentifier='myapp-aurora-serverless',
    Engine='aurora-postgresql',
    EngineMode='provisioned',  # v2 uses provisioned mode
    ServerlessV2ScalingConfiguration={
        'MinCapacity': 0.5,  # Minimum ACUs
        'MaxCapacity': 16    # Maximum ACUs
    },
    MasterUsername='admin',
    MasterUserPassword='SecurePassword123!',
    DatabaseName='myapp'
)

# Create serverless instance
response = rds.create_db_instance(
    DBInstanceIdentifier='myapp-aurora-serverless-instance',
    DBInstanceClass='db.serverless',
    Engine='aurora-postgresql',
    DBClusterIdentifier='myapp-aurora-serverless'
)
```

**Global Database**
```python
# ✅ Good: Aurora Global Database for multi-region
# Create primary cluster in us-east-1
response = rds.create_global_cluster(
    GlobalClusterIdentifier='myapp-global',
    Engine='aurora-postgresql',
    EngineVersion='15.3'
)

# Add primary cluster
response = rds.create_db_cluster(
    DBClusterIdentifier='myapp-primary-cluster',
    Engine='aurora-postgresql',
    GlobalClusterIdentifier='myapp-global',
    MasterUsername='admin',
    MasterUserPassword='SecurePassword123!'
)

# Add secondary cluster in eu-west-1
response = rds.create_db_cluster(
    DBClusterIdentifier='myapp-secondary-cluster',
    Engine='aurora-postgresql',
    GlobalClusterIdentifier='myapp-global',
    Region='eu-west-1'
)
```

## Google Cloud SQL

### Instance Configuration

**Create Cloud SQL Instance**
```python
# ✅ Good: Create Cloud SQL PostgreSQL instance
from google.cloud import sql_v1

client = sql_v1.SqlInstancesServiceClient()

instance = sql_v1.DatabaseInstance(
    name='myapp-prod',
    database_version='POSTGRES_15',
    region='us-central1',
    settings=sql_v1.Settings(
        tier='db-custom-4-16384',  # 4 vCPU, 16 GB RAM
        backup_configuration=sql_v1.BackupConfiguration(
            enabled=True,
            start_time='03:00',
            point_in_time_recovery_enabled=True,
            transaction_log_retention_days=7
        ),
        ip_configuration=sql_v1.IpConfiguration(
            ipv4_enabled=False,  # Disable public IP
            private_network='projects/myproject/global/networks/default',
            require_ssl=True
        ),
        database_flags=[
            sql_v1.DatabaseFlags(name='max_connections', value='200'),
            sql_v1.DatabaseFlags(name='shared_buffers', value='4GB')
        ],
        availability_type='REGIONAL',  # High availability
        disk_type='PD_SSD',
        disk_size=100,
        disk_autoresize=True,
        disk_autoresize_limit=500
    )
)

response = client.insert(project='myproject', instance=instance)
```

**Read Replicas**
```python
# ✅ Good: Create read replica
replica = sql_v1.DatabaseInstance(
    name='myapp-prod-replica',
    database_version='POSTGRES_15',
    region='us-east1',  # Different region
    master_instance_name='projects/myproject/instances/myapp-prod',
    replica_configuration=sql_v1.ReplicaConfiguration(
        failover_target=False
    ),
    settings=sql_v1.Settings(
        tier='db-custom-4-16384'
    )
)

response = client.insert(project='myproject', instance=replica)
```

### Connection Management

**Cloud SQL Proxy**
```bash
# ✅ Good: Use Cloud SQL Proxy for secure connections
# Download and run proxy
./cloud_sql_proxy -instances=myproject:us-central1:myapp-prod=tcp:5432

# Application connects to localhost:5432
# Proxy handles authentication and encryption
```

**Private IP Connection**
```python
# ✅ Good: Connect via private IP (VPC peering)
import psycopg2

conn = psycopg2.connect(
    host='10.1.2.3',  # Private IP
    database='myapp',
    user='postgres',
    password=os.getenv('DB_PASSWORD'),
    sslmode='require'
)
```

## Azure SQL Database

### Service Tiers

**DTU-Based Tiers**
```
# Basic: 5 DTUs, 2 GB storage - Development
# Standard: 10-3000 DTUs, up to 1 TB - General purpose
# Premium: 125-4000 DTUs, up to 4 TB - Mission critical
```

**vCore-Based Tiers**
```python
# ✅ Good: Create vCore-based database
from azure.mgmt.sql import SqlManagementClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = SqlManagementClient(credential, subscription_id)

# Create database
database = client.databases.begin_create_or_update(
    resource_group_name='myapp-rg',
    server_name='myapp-server',
    database_name='myapp-prod',
    parameters={
        'location': 'eastus',
        'sku': {
            'name': 'GP_Gen5',  # General Purpose, Gen5
            'tier': 'GeneralPurpose',
            'capacity': 4  # 4 vCores
        },
        'max_size_bytes': 107374182400,  # 100 GB
        'zone_redundant': True,
        'backup_storage_redundancy': 'Geo'
    }
).result()
```

### Elastic Pools

**Create Elastic Pool**
```python
# ✅ Good: Use elastic pool for multiple databases
elastic_pool = client.elastic_pools.begin_create_or_update(
    resource_group_name='myapp-rg',
    server_name='myapp-server',
    elastic_pool_name='myapp-pool',
    parameters={
        'location': 'eastus',
        'sku': {
            'name': 'GP_Gen5',
            'tier': 'GeneralPurpose',
            'capacity': 8  # 8 vCores shared across databases
        },
        'per_database_settings': {
            'min_capacity': 0,
            'max_capacity': 4
        }
    }
).result()

# Add database to pool
database = client.databases.begin_create_or_update(
    resource_group_name='myapp-rg',
    server_name='myapp-server',
    database_name='myapp-tenant-1',
    parameters={
        'location': 'eastus',
        'elastic_pool_id': elastic_pool.id
    }
).result()
```

### Geo-Replication

**Active Geo-Replication**
```python
# ✅ Good: Set up geo-replication for disaster recovery
# Create secondary database in different region
secondary = client.databases.begin_create_or_update(
    resource_group_name='myapp-rg-west',
    server_name='myapp-server-west',
    database_name='myapp-prod',
    parameters={
        'location': 'westus',
        'create_mode': 'Secondary',
        'source_database_id': primary_database.id
    }
).result()

# Failover to secondary
client.databases.begin_failover(
    resource_group_name='myapp-rg-west',
    server_name='myapp-server-west',
    database_name='myapp-prod'
).result()
```

## Amazon DynamoDB

### Table Design

**Create Table with On-Demand Billing**
```python
# ✅ Good: On-demand billing for unpredictable workloads
import boto3

dynamodb = boto3.client('dynamodb')

response = dynamodb.create_table(
    TableName='Tasks',
    KeySchema=[
        {'AttributeName': 'PK', 'KeyType': 'HASH'},
        {'AttributeName': 'SK', 'KeyType': 'RANGE'}
    ],
    AttributeDefinitions=[
        {'AttributeName': 'PK', 'AttributeType': 'S'},
        {'AttributeName': 'SK', 'AttributeType': 'S'},
        {'AttributeName': 'GSI1PK', 'AttributeType': 'S'},
        {'AttributeName': 'GSI1SK', 'AttributeType': 'S'}
    ],
    GlobalSecondaryIndexes=[
        {
            'IndexName': 'GSI1',
            'KeySchema': [
                {'AttributeName': 'GSI1PK', 'KeyType': 'HASH'},
                {'AttributeName': 'GSI1SK', 'KeyType': 'RANGE'}
            ],
            'Projection': {'ProjectionType': 'ALL'}
        }
    ],
    BillingMode='PAY_PER_REQUEST',  # On-demand
    StreamSpecification={
        'StreamEnabled': True,
        'StreamViewType': 'NEW_AND_OLD_IMAGES'
    },
    SSESpecification={
        'Enabled': True,
        'SSEType': 'KMS',
        'KMSMasterKeyId': 'alias/aws/dynamodb'
    },
    PointInTimeRecoverySpecification={'PointInTimeRecoveryEnabled': True},
    Tags=[
        {'Key': 'Environment', 'Value': 'Production'},
        {'Key': 'Application', 'Value': 'MyApp'}
    ]
)
```

**Provisioned Capacity with Auto Scaling**
```python
# ✅ Good: Provisioned capacity with auto scaling
response = dynamodb.create_table(
    TableName='Tasks',
    KeySchema=[...],
    AttributeDefinitions=[...],
    BillingMode='PROVISIONED',
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# Configure auto scaling
autoscaling = boto3.client('application-autoscaling')

# Register scalable target
autoscaling.register_scalable_target(
    ServiceNamespace='dynamodb',
    ResourceId='table/Tasks',
    ScalableDimension='dynamodb:table:ReadCapacityUnits',
    MinCapacity=5,
    MaxCapacity=100
)

# Create scaling policy
autoscaling.put_scaling_policy(
    PolicyName='TasksReadAutoScaling',
    ServiceNamespace='dynamodb',
    ResourceId='table/Tasks',
    ScalableDimension='dynamodb:table:ReadCapacityUnits',
    PolicyType='TargetTrackingScaling',
    TargetTrackingScalingPolicyConfiguration={
        'TargetValue': 70.0,  # Target 70% utilization
        'PredefinedMetricSpecification': {
            'PredefinedMetricType': 'DynamoDBReadCapacityUtilization'
        }
    }
)
```

### Global Tables

**Multi-Region Replication**
```python
# ✅ Good: Create global table for multi-region
response = dynamodb.create_global_table(
    GlobalTableName='Tasks',
    ReplicationGroup=[
        {'RegionName': 'us-east-1'},
        {'RegionName': 'eu-west-1'},
        {'RegionName': 'ap-southeast-1'}
    ]
)

# Application automatically uses local region
# Writes replicate to all regions
```

### Backup and Recovery

**On-Demand Backups**
```python
# ✅ Good: Create on-demand backup
response = dynamodb.create_backup(
    TableName='Tasks',
    BackupName='Tasks-Backup-2024-01-01'
)

# Restore from backup
response = dynamodb.restore_table_from_backup(
    TargetTableName='Tasks-Restored',
    BackupArn='arn:aws:dynamodb:us-east-1:123456789012:table/Tasks/backup/01234567890123-abcdefgh'
)
```

**Point-in-Time Recovery**
```python
# ✅ Good: Enable PITR
response = dynamodb.update_continuous_backups(
    TableName='Tasks',
    PointInTimeRecoverySpecification={'PointInTimeRecoveryEnabled': True}
)

# Restore to specific time
response = dynamodb.restore_table_to_point_in_time(
    SourceTableName='Tasks',
    TargetTableName='Tasks-PITR',
    RestoreDateTime=datetime(2024, 1, 1, 12, 30, 0)
)
```

## Cost Optimization

### AWS RDS Cost Optimization

**Reserved Instances**
```python
# ✅ Good: Purchase reserved instances for predictable workloads
# 1-year or 3-year commitment for 30-60% savings
response = rds.purchase_reserved_db_instances_offering(
    ReservedDBInstancesOfferingId='offering-id',
    ReservedDBInstanceId='myapp-prod-ri',
    DBInstanceCount=1
)
```

**Storage Optimization**
```
# ✅ Good: Use gp3 instead of gp2
# gp3: $0.08/GB-month + configurable IOPS/throughput
# gp2: $0.10/GB-month + IOPS tied to storage size

# Savings: 20% on storage + better performance control
```

**Right-Sizing**
```python
# Monitor CloudWatch metrics
# - CPUUtilization: Should be 40-70% on average
# - FreeableMemory: Should have 20-30% free
# - DatabaseConnections: Should be < 80% of max

# Downsize if consistently underutilized
# Upsize if hitting resource limits
```

### DynamoDB Cost Optimization

**On-Demand vs Provisioned**
```
# On-Demand: $1.25 per million write requests, $0.25 per million reads
# Provisioned: $0.00065 per WCU-hour, $0.00013 per RCU-hour

# Break-even: ~720 hours/month at consistent load
# Use on-demand for: Unpredictable traffic, new applications
# Use provisioned for: Predictable traffic, cost optimization
```

**Table Class Selection**
```python
# ✅ Good: Use Standard-IA for infrequently accessed data
response = dynamodb.update_table(
    TableName='ArchivedTasks',
    TableClass='STANDARD_INFREQUENT_ACCESS'  # 50% cheaper storage
)
```

### Cloud SQL Cost Optimization

**Committed Use Discounts**
```
# 1-year commitment: 25% discount
# 3-year commitment: 52% discount

# Apply to: Predictable workloads, production databases
```

**Automatic Storage Increase**
```python
# ✅ Good: Enable auto-increase to avoid over-provisioning
settings=sql_v1.Settings(
    disk_autoresize=True,
    disk_autoresize_limit=500  # Set reasonable limit
)
```
