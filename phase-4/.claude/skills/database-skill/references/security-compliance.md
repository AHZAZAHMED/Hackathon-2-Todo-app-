# Database Security and Compliance

## Data Encryption

### Encryption at Rest

**PostgreSQL - Transparent Data Encryption (TDE)**
```bash
# Using pgcrypto extension for column-level encryption
CREATE EXTENSION pgcrypto;

-- Encrypt sensitive data
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    ssn BYTEA,  -- Encrypted column
    credit_card BYTEA  -- Encrypted column
);

-- Insert encrypted data
INSERT INTO users (username, email, ssn, credit_card)
VALUES (
    'john_doe',
    'john@example.com',
    pgp_sym_encrypt('123-45-6789', 'encryption_key'),
    pgp_sym_encrypt('4111-1111-1111-1111', 'encryption_key')
);

-- Query encrypted data
SELECT
    username,
    email,
    pgp_sym_decrypt(ssn, 'encryption_key') as ssn,
    pgp_sym_decrypt(credit_card, 'encryption_key') as credit_card
FROM users
WHERE username = 'john_doe';
```

**MySQL - Encryption at Rest**
```sql
-- Enable encryption for tablespace
CREATE TABLESPACE encrypted_space
ADD DATAFILE 'encrypted.ibd'
ENCRYPTION = 'Y';

-- Create table in encrypted tablespace
CREATE TABLE sensitive_data (
    id INT PRIMARY KEY,
    ssn VARCHAR(11),
    credit_card VARCHAR(19)
) TABLESPACE = encrypted_space;

-- Column-level encryption with AES
INSERT INTO sensitive_data (id, ssn, credit_card)
VALUES (
    1,
    AES_ENCRYPT('123-45-6789', 'encryption_key'),
    AES_ENCRYPT('4111-1111-1111-1111', 'encryption_key')
);

-- Decrypt data
SELECT
    id,
    AES_DECRYPT(ssn, 'encryption_key') as ssn,
    AES_DECRYPT(credit_card, 'encryption_key') as credit_card
FROM sensitive_data;
```

**AWS RDS - Encryption at Rest**
```python
# ✅ Good: Enable encryption when creating RDS instance
import boto3

rds = boto3.client('rds')

response = rds.create_db_instance(
    DBInstanceIdentifier='myapp-prod',
    DBInstanceClass='db.r5.large',
    Engine='postgres',
    MasterUsername='admin',
    MasterUserPassword='SecurePassword123!',
    AllocatedStorage=100,
    StorageEncrypted=True,  # Enable encryption
    KmsKeyId='arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012'
)
```

### Encryption in Transit

**PostgreSQL - SSL/TLS Configuration**
```ini
# postgresql.conf

# Enable SSL
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'
ssl_ca_file = '/path/to/root.crt'

# Require SSL for all connections
ssl_min_protocol_version = 'TLSv1.2'
ssl_prefer_server_ciphers = on
ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'
```

```sql
-- Require SSL for specific users
ALTER USER myapp_user WITH CONNECTION LIMIT 10;
ALTER USER myapp_user SET ssl TO on;

-- pg_hba.conf: Require SSL for all connections
hostssl all all 0.0.0.0/0 md5
```

**MySQL - SSL/TLS Configuration**
```ini
# my.cnf

[mysqld]
# Enable SSL
ssl-ca=/path/to/ca.pem
ssl-cert=/path/to/server-cert.pem
ssl-key=/path/to/server-key.pem

# Require SSL for all connections
require_secure_transport=ON
```

```sql
-- Require SSL for specific users
CREATE USER 'myapp_user'@'%'
IDENTIFIED BY 'password'
REQUIRE SSL;

-- Grant privileges
GRANT ALL PRIVILEGES ON myapp.* TO 'myapp_user'@'%';
```

**Application Connection with SSL**
```python
# PostgreSQL with SSL
import psycopg2

conn = psycopg2.connect(
    host='db.example.com',
    database='myapp',
    user='myapp_user',
    password='password',
    sslmode='require',  # or 'verify-ca', 'verify-full'
    sslrootcert='/path/to/ca.crt',
    sslcert='/path/to/client.crt',
    sslkey='/path/to/client.key'
)

# MySQL with SSL
import mysql.connector

conn = mysql.connector.connect(
    host='db.example.com',
    database='myapp',
    user='myapp_user',
    password='password',
    ssl_ca='/path/to/ca.pem',
    ssl_cert='/path/to/client-cert.pem',
    ssl_key='/path/to/client-key.pem',
    ssl_verify_cert=True
)
```

## Access Control

### Role-Based Access Control (RBAC)

**PostgreSQL - Roles and Privileges**
```sql
-- Create roles
CREATE ROLE readonly;
CREATE ROLE readwrite;
CREATE ROLE admin;

-- Grant privileges to roles
-- Read-only role
GRANT CONNECT ON DATABASE myapp TO readonly;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly;

-- Read-write role
GRANT CONNECT ON DATABASE myapp TO readwrite;
GRANT USAGE ON SCHEMA public TO readwrite;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO readwrite;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO readwrite;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO readwrite;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO readwrite;

-- Admin role
GRANT ALL PRIVILEGES ON DATABASE myapp TO admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;

-- Create users and assign roles
CREATE USER app_reader WITH PASSWORD 'reader_password';
GRANT readonly TO app_reader;

CREATE USER app_writer WITH PASSWORD 'writer_password';
GRANT readwrite TO app_writer;

CREATE USER app_admin WITH PASSWORD 'admin_password';
GRANT admin TO app_admin;
```

**MySQL - Roles and Privileges**
```sql
-- Create roles
CREATE ROLE 'readonly';
CREATE ROLE 'readwrite';
CREATE ROLE 'admin';

-- Grant privileges to roles
-- Read-only role
GRANT SELECT ON myapp.* TO 'readonly';

-- Read-write role
GRANT SELECT, INSERT, UPDATE, DELETE ON myapp.* TO 'readwrite';

-- Admin role
GRANT ALL PRIVILEGES ON myapp.* TO 'admin';

-- Create users and assign roles
CREATE USER 'app_reader'@'%' IDENTIFIED BY 'reader_password';
GRANT 'readonly' TO 'app_reader'@'%';

CREATE USER 'app_writer'@'%' IDENTIFIED BY 'writer_password';
GRANT 'readwrite' TO 'app_writer'@'%';

CREATE USER 'app_admin'@'%' IDENTIFIED BY 'admin_password';
GRANT 'admin' TO 'app_admin'@'%';

-- Activate roles
SET DEFAULT ROLE ALL TO 'app_reader'@'%';
SET DEFAULT ROLE ALL TO 'app_writer'@'%';
SET DEFAULT ROLE ALL TO 'app_admin'@'%';
```

### Row-Level Security (RLS)

**PostgreSQL - Row-Level Security**
```sql
-- Enable RLS on table
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Create policy: Users can only see their own tasks
CREATE POLICY user_tasks_policy ON tasks
FOR ALL
TO PUBLIC
USING (user_id = current_setting('app.current_user_id')::INTEGER);

-- Set user context in application
-- Before each query, set the current user
SET app.current_user_id = '123';

-- Now queries automatically filter by user_id
SELECT * FROM tasks;  -- Only returns tasks where user_id = 123

-- Policy for admins (bypass RLS)
CREATE POLICY admin_all_tasks_policy ON tasks
FOR ALL
TO admin_role
USING (true);
```

**Application Implementation**
```python
# ✅ Good: Set user context for RLS
def execute_query_with_rls(user_id, query, params):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Set user context
        cursor.execute(f"SET app.current_user_id = {user_id}")

        # Execute query (RLS automatically applies)
        cursor.execute(query, params)
        results = cursor.fetchall()

        return results
    finally:
        cursor.close()
        conn.close()

# Usage
user_id = 123
tasks = execute_query_with_rls(
    user_id,
    "SELECT * FROM tasks WHERE completed = %s",
    (False,)
)
```

## Audit Logging

### PostgreSQL - Audit Logging

**pgAudit Extension**
```sql
-- Install pgAudit extension
CREATE EXTENSION pgaudit;

-- Configure audit logging
ALTER SYSTEM SET pgaudit.log = 'write, ddl';
ALTER SYSTEM SET pgaudit.log_catalog = off;
ALTER SYSTEM SET pgaudit.log_parameter = on;
ALTER SYSTEM SET pgaudit.log_relation = on;

-- Reload configuration
SELECT pg_reload_conf();

-- Audit specific tables
ALTER TABLE sensitive_data SET (pgaudit.log = 'read, write');

-- View audit logs in PostgreSQL log files
-- Example log entry:
-- AUDIT: SESSION,1,1,WRITE,INSERT,TABLE,public.users,"INSERT INTO users (username, email) VALUES ('john', 'john@example.com')",<not logged>
```

**Custom Audit Table**
```sql
-- Create audit log table
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    operation VARCHAR(10) NOT NULL,
    user_name VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    old_data JSONB,
    new_data JSONB
);

-- Create audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, operation, user_name, new_data)
        VALUES (TG_TABLE_NAME, TG_OP, current_user, row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, operation, user_name, old_data, new_data)
        VALUES (TG_TABLE_NAME, TG_OP, current_user, row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, operation, user_name, old_data)
        VALUES (TG_TABLE_NAME, TG_OP, current_user, row_to_json(OLD));
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to tables
CREATE TRIGGER tasks_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON tasks
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

CREATE TRIGGER users_audit_trigger
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
```

### MySQL - Audit Logging

**MySQL Enterprise Audit**
```sql
-- Install audit plugin
INSTALL PLUGIN audit_log SONAME 'audit_log.so';

-- Configure audit logging
SET GLOBAL audit_log_policy = 'ALL';
SET GLOBAL audit_log_format = 'JSON';
SET GLOBAL audit_log_file = 'audit.log';

-- Filter specific events
SET GLOBAL audit_log_include_accounts = 'app_user@%,admin@%';
SET GLOBAL audit_log_exclude_accounts = 'monitoring@%';
```

**Custom Audit Table (MySQL)**
```sql
-- Create audit log table
CREATE TABLE audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    operation VARCHAR(10) NOT NULL,
    user_name VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    old_data JSON,
    new_data JSON
);

-- Create audit trigger
DELIMITER $$

CREATE TRIGGER tasks_audit_insert
AFTER INSERT ON tasks
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, operation, user_name, new_data)
    VALUES ('tasks', 'INSERT', USER(), JSON_OBJECT(
        'id', NEW.id,
        'user_id', NEW.user_id,
        'title', NEW.title,
        'completed', NEW.completed
    ));
END$$

CREATE TRIGGER tasks_audit_update
AFTER UPDATE ON tasks
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, operation, user_name, old_data, new_data)
    VALUES ('tasks', 'UPDATE', USER(),
        JSON_OBJECT('id', OLD.id, 'user_id', OLD.user_id, 'title', OLD.title, 'completed', OLD.completed),
        JSON_OBJECT('id', NEW.id, 'user_id', NEW.user_id, 'title', NEW.title, 'completed', NEW.completed)
    );
END$$

CREATE TRIGGER tasks_audit_delete
AFTER DELETE ON tasks
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, operation, user_name, old_data)
    VALUES ('tasks', 'DELETE', USER(), JSON_OBJECT(
        'id', OLD.id,
        'user_id', OLD.user_id,
        'title', OLD.title,
        'completed', OLD.completed
    ));
END$$

DELIMITER ;
```

## Compliance

### GDPR Compliance

**Right to Access (Data Export)**
```sql
-- Export all user data
SELECT
    u.id,
    u.username,
    u.email,
    u.created_at,
    json_agg(
        json_build_object(
            'id', t.id,
            'title', t.title,
            'completed', t.completed,
            'created_at', t.created_at
        )
    ) as tasks
FROM users u
LEFT JOIN tasks t ON u.id = t.user_id
WHERE u.id = 123
GROUP BY u.id, u.username, u.email, u.created_at;
```

**Right to Erasure (Data Deletion)**
```sql
-- Delete user and all related data
BEGIN;

-- Delete related data
DELETE FROM tasks WHERE user_id = 123;
DELETE FROM user_preferences WHERE user_id = 123;
DELETE FROM audit_log WHERE user_name = (SELECT username FROM users WHERE id = 123);

-- Delete user
DELETE FROM users WHERE id = 123;

COMMIT;

-- Or use CASCADE
ALTER TABLE tasks
ADD CONSTRAINT fk_tasks_user
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Now simple delete cascades
DELETE FROM users WHERE id = 123;
```

**Data Anonymization**
```sql
-- Anonymize user data instead of deleting
UPDATE users
SET
    username = 'deleted_user_' || id,
    email = 'deleted_' || id || '@example.com',
    first_name = 'Deleted',
    last_name = 'User',
    phone = NULL,
    address = NULL,
    deleted_at = CURRENT_TIMESTAMP
WHERE id = 123;

-- Keep tasks but anonymize
UPDATE tasks
SET
    title = 'Deleted task',
    description = NULL
WHERE user_id = 123;
```

**Data Retention Policies**
```sql
-- Create function to delete old data
CREATE OR REPLACE FUNCTION delete_old_audit_logs()
RETURNS void AS $$
BEGIN
    DELETE FROM audit_log
    WHERE timestamp < CURRENT_DATE - INTERVAL '7 years';
END;
$$ LANGUAGE plpgsql;

-- Schedule with pg_cron
CREATE EXTENSION pg_cron;

SELECT cron.schedule(
    'delete-old-audit-logs',
    '0 2 * * 0',  -- Every Sunday at 2 AM
    'SELECT delete_old_audit_logs()'
);
```

### HIPAA Compliance

**Access Controls**
```sql
-- Strict access controls for PHI (Protected Health Information)
CREATE ROLE hipaa_user;

-- Grant minimal necessary privileges
GRANT CONNECT ON DATABASE healthcare TO hipaa_user;
GRANT USAGE ON SCHEMA public TO hipaa_user;
GRANT SELECT, INSERT, UPDATE ON patient_records TO hipaa_user;

-- Deny access to audit logs
REVOKE ALL ON audit_log FROM hipaa_user;

-- Enable RLS for patient records
ALTER TABLE patient_records ENABLE ROW LEVEL SECURITY;

CREATE POLICY patient_access_policy ON patient_records
FOR ALL
TO hipaa_user
USING (
    patient_id IN (
        SELECT patient_id FROM user_patient_access
        WHERE user_id = current_setting('app.current_user_id')::INTEGER
    )
);
```

**Audit Requirements**
```sql
-- Comprehensive audit logging for HIPAA
CREATE TABLE hipaa_audit_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,
    user_name VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER,
    ip_address INET,
    session_id VARCHAR(100),
    old_data JSONB,
    new_data JSONB
);

-- Trigger for patient records access
CREATE OR REPLACE FUNCTION hipaa_audit_trigger_func()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO hipaa_audit_log (
        user_id,
        user_name,
        action,
        table_name,
        record_id,
        ip_address,
        session_id,
        old_data,
        new_data
    )
    VALUES (
        current_setting('app.current_user_id')::INTEGER,
        current_user,
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        inet_client_addr(),
        current_setting('app.session_id'),
        CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN row_to_json(OLD) END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) END
    );

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER patient_records_hipaa_audit
AFTER INSERT OR UPDATE OR DELETE ON patient_records
FOR EACH ROW EXECUTE FUNCTION hipaa_audit_trigger_func();
```

### PCI DSS Compliance

**Cardholder Data Protection**
```sql
-- ❌ Bad: Storing full credit card numbers
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    credit_card VARCHAR(19),  -- Never store full card numbers
    cvv VARCHAR(4),  -- Never store CVV
    amount DECIMAL(10, 2)
);

-- ✅ Good: Store only last 4 digits and use tokenization
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    card_last_four VARCHAR(4),  -- Only last 4 digits
    card_token VARCHAR(100),  -- Token from payment processor
    card_brand VARCHAR(20),  -- Visa, Mastercard, etc.
    amount DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Use payment processor API for actual transactions
-- Never store full card numbers, CVV, or PIN
```

**Access Logging for Cardholder Data**
```sql
-- Log all access to payment data
CREATE TABLE pci_access_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    payment_id INTEGER,
    ip_address INET,
    success BOOLEAN
);

-- Trigger for payment access
CREATE OR REPLACE FUNCTION pci_access_trigger_func()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO pci_access_log (user_id, action, payment_id, ip_address, success)
    VALUES (
        current_setting('app.current_user_id')::INTEGER,
        TG_OP,
        COALESCE(NEW.id, OLD.id),
        inet_client_addr(),
        true
    );

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER payments_pci_access
AFTER SELECT OR INSERT OR UPDATE OR DELETE ON payments
FOR EACH ROW EXECUTE FUNCTION pci_access_trigger_func();
```

## Security Best Practices

### Password Security

**Secure Password Storage**
```sql
-- ✅ Good: Use bcrypt or similar for password hashing
CREATE EXTENSION pgcrypto;

-- Store hashed passwords
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Hash password on insert
INSERT INTO users (username, password_hash)
VALUES ('john_doe', crypt('user_password', gen_salt('bf', 10)));

-- Verify password
SELECT id, username
FROM users
WHERE username = 'john_doe'
    AND password_hash = crypt('user_password', password_hash);
```

### SQL Injection Prevention

**Parameterized Queries**
```python
# ✅ Good: Use parameterized queries
def get_user_tasks(user_id):
    query = "SELECT * FROM tasks WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    return cursor.fetchall()

# ❌ Bad: String concatenation (SQL injection risk)
def get_user_tasks_unsafe(user_id):
    query = f"SELECT * FROM tasks WHERE user_id = {user_id}"
    cursor.execute(query)
    return cursor.fetchall()
```

### Database Firewall Rules

**AWS RDS Security Groups**
```python
# ✅ Good: Restrict database access to application servers only
import boto3

ec2 = boto3.client('ec2')

# Create security group for RDS
response = ec2.create_security_group(
    GroupName='rds-security-group',
    Description='Security group for RDS database',
    VpcId='vpc-12345678'
)

security_group_id = response['GroupId']

# Allow access only from application security group
ec2.authorize_security_group_ingress(
    GroupId=security_group_id,
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 5432,
            'ToPort': 5432,
            'UserIdGroupPairs': [
                {'GroupId': 'sg-app-servers'}  # Application server security group
            ]
        }
    ]
)
```

### Regular Security Audits

**Security Checklist**
```
# Database Security Audit Checklist

## Access Control
- [ ] Principle of least privilege applied
- [ ] No default or weak passwords
- [ ] Unused accounts disabled
- [ ] Regular access review conducted

## Encryption
- [ ] Encryption at rest enabled
- [ ] Encryption in transit (SSL/TLS) enforced
- [ ] Encryption keys rotated regularly
- [ ] Key management system in place

## Audit Logging
- [ ] Audit logging enabled
- [ ] Logs retained per compliance requirements
- [ ] Log monitoring and alerting configured
- [ ] Regular log review conducted

## Network Security
- [ ] Database not publicly accessible
- [ ] Firewall rules restrict access
- [ ] VPN or private network used
- [ ] IP whitelisting configured

## Compliance
- [ ] GDPR requirements met (if applicable)
- [ ] HIPAA requirements met (if applicable)
- [ ] PCI DSS requirements met (if applicable)
- [ ] Regular compliance audits conducted

## Backup and Recovery
- [ ] Regular backups configured
- [ ] Backup encryption enabled
- [ ] Backup restoration tested
- [ ] Disaster recovery plan documented

## Patching and Updates
- [ ] Database software up to date
- [ ] Security patches applied promptly
- [ ] Maintenance windows scheduled
- [ ] Change management process followed
```
