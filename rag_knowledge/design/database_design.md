# Database Design Standards

## 1. Purpose

This document defines the database design standards that all AI agents must follow when designing, generating, or modifying databases for applications created by the Agentic SDLC platform.

The database design must be:

* Reliable
* Secure
* Scalable
* Maintainable
* Performant
* Consistent
* Migration-safe
* Suitable for production workloads

The Database Design must be derived from the approved requirements and system architecture.

---

# 2. Database Selection

## Primary Relational Database

The default relational database is:

**PostgreSQL**

PostgreSQL should be used when the application requires:

* Relational data
* Transactions
* Strong consistency
* Complex queries
* Foreign-key relationships
* Aggregations
* Reporting
* Structured business data

## Supporting Data Stores

The platform may use additional data stores when appropriate.

| Technology              | Primary Purpose                                 |
| ----------------------- | ----------------------------------------------- |
| PostgreSQL              | Primary transactional database                  |
| Redis                   | Cache, sessions, temporary state, rate limiting |
| Qdrant                  | Vector embeddings and semantic search           |
| LangGraph Checkpointing | Agent/workflow state                            |
| S3                      | Files, documents, generated artifacts           |

Redis, Qdrant, and S3 must not be used as replacements for PostgreSQL transactional data unless explicitly justified by the architecture.

---

# 3. Database Design Principles

All database designs should follow:

1. Design from requirements.
2. Identify entities before creating tables.
3. Define relationships explicitly.
4. Use appropriate constraints.
5. Avoid unnecessary duplication.
6. Design indexes based on query patterns.
7. Protect sensitive data.
8. Plan for scalability.
9. Plan migrations before implementation.
10. Design for backup and recovery.
11. Avoid storing derived data unless required for performance.
12. Keep transactional and analytical workloads separated when necessary.

---

# 4. Entity Identification

The Database Agent must identify:

* Core business entities
* Supporting entities
* User entities
* Authentication entities
* Authorization entities
* Audit entities
* Configuration entities
* Transaction entities
* Relationship entities
* Background-job entities

Example:

```text
User
  ↓
Project
  ↓
Task
  ↓
TaskResult
```

Each entity should have a clear business purpose.

---

# 5. Entity Relationships

Relationships must be explicitly defined.

Common relationships:

### One-to-One

```text
User 1 ───── 1 UserProfile
```

### One-to-Many

```text
User 1 ───── N Projects
```

### Many-to-Many

```text
User N ───── N Projects
```

Many-to-many relationships should normally use an intermediate/junction table.

Example:

```text
users
projects
user_projects
```

---

# 6. Normalization

Database designs should normally follow relational normalization principles.

Prefer:

```text
users
projects
tasks
```

Instead of storing repeated information:

```text
project_1_user_name
project_2_user_name
project_3_user_name
```

Avoid unnecessary duplication.

Normalization should generally be applied up to an appropriate level such as 3NF.

Denormalization may be introduced when:

* Query performance requires it
* Reporting requires it
* Read-heavy workloads justify it
* The architecture explicitly approves it

Any intentional denormalization should be documented.

---

# 7. Primary Keys

Every table must have a primary key unless there is a documented reason otherwise.

Preferred approach:

```text
id
```

The key may use:

* UUID
* BIGINT
* Other appropriate identifiers

For distributed systems, UUIDs are generally preferred when globally unique identifiers are beneficial.

Example:

```text
id UUID PRIMARY KEY
```

Primary keys must be:

* Unique
* Stable
* Non-null
* Immutable whenever possible

---

# 8. Foreign Keys

Relationships between tables should use foreign keys.

Example:

```text
projects.user_id
        ↓
users.id
```

Foreign keys should define appropriate:

* Referential integrity
* Delete behavior
* Update behavior

Example:

```text
FOREIGN KEY (user_id)
REFERENCES users(id)
```

Avoid creating relationships only through application code when database-level referential integrity is appropriate.

---

# 9. Constraints

Use database constraints to protect data integrity.

Common constraints:

* PRIMARY KEY
* FOREIGN KEY
* UNIQUE
* NOT NULL
* CHECK
* DEFAULT

Example:

```text
email VARCHAR(255) NOT NULL UNIQUE
```

Business-critical invariants should be enforced at the database level where practical.

---

# 10. Naming Conventions

Use consistent naming.

### Tables

Use lowercase `snake_case`.

```text
users
projects
project_tasks
```

### Columns

```text
created_at
updated_at
user_id
project_id
```

### Foreign Keys

Use:

```text
<entity>_id
```

Examples:

```text
user_id
project_id
task_id
```

Avoid inconsistent naming such as:

```text
UserID
userId
USER_ID
```

---

# 11. Data Types

Use appropriate PostgreSQL data types.

Examples:

| Data            | Recommended Type         |
| --------------- | ------------------------ |
| Identifier      | UUID / BIGINT            |
| Name            | VARCHAR                  |
| Long text       | TEXT                     |
| Boolean         | BOOLEAN                  |
| Integer         | INTEGER / BIGINT         |
| Decimal         | NUMERIC                  |
| Date            | DATE                     |
| Timestamp       | TIMESTAMP WITH TIME ZONE |
| Structured JSON | JSONB                    |
| Array           | ARRAY where appropriate  |

Avoid storing everything as `TEXT`.

Choose data types based on:

* Data meaning
* Validation requirements
* Query requirements
* Storage efficiency

---

# 12. Timestamps

Important tables should normally contain:

```text
created_at
updated_at
```

Example:

```text
created_at TIMESTAMP WITH TIME ZONE NOT NULL
updated_at TIMESTAMP WITH TIME ZONE NOT NULL
```

Use UTC for persisted timestamps.

Applications should convert timestamps to the user's required timezone when displaying them.

---

# 13. Soft Delete

Soft deletion may be used when records must be retained for:

* Auditing
* Compliance
* Recovery
* Historical reporting

Example:

```text
deleted_at TIMESTAMP WITH TIME ZONE
```

Avoid soft deletion when it creates unnecessary complexity.

The application must ensure deleted records are excluded from normal queries.

---

# 14. Indexing

Indexes must be designed based on actual query patterns.

Common indexed columns:

```text
user_id
project_id
email
created_at
status
```

Example:

```text
CREATE INDEX idx_projects_user_id
ON projects(user_id);
```

Unique fields should use unique indexes or constraints.

Avoid creating indexes on every column.

Too many indexes can:

* Increase storage
* Slow INSERT operations
* Slow UPDATE operations
* Increase maintenance cost

---

# 15. Composite Indexes

Use composite indexes when queries commonly filter or sort using multiple columns.

Example:

```text
CREATE INDEX idx_tasks_project_status
ON tasks(project_id, status);
```

The order of columns should reflect common query patterns.

---

# 16. Query Design

Queries should:

* Retrieve only required columns
* Use appropriate indexes
* Avoid unnecessary joins
* Avoid N+1 query patterns
* Use pagination for large datasets
* Use parameterized queries
* Avoid loading huge datasets into memory

Avoid:

```sql
SELECT *
FROM users;
```

when only specific columns are required.

Prefer:

```sql
SELECT id, name, email
FROM users;
```

---

# 17. Pagination

Large datasets must use pagination.

Preferred approaches include:

* Offset pagination for simple use cases
* Cursor/keyset pagination for large datasets

Example:

```text
GET /projects?limit=20&offset=40
```

For very large datasets:

```text
GET /projects?limit=20&cursor=<cursor>
```

---

# 18. Transactions

Operations that must succeed or fail together should use database transactions.

Example:

```text
Create Order
      ↓
Create Payment Record
      ↓
Update Inventory
```

If one critical operation fails, the transaction should roll back where appropriate.

Transactions should be kept reasonably short.

Avoid holding transactions open during:

* External API calls
* Long-running AI calls
* File uploads
* Human approval
* Long-running background tasks

---

# 19. ACID Requirements

Transactional operations should respect ACID principles:

```text
Atomicity
Consistency
Isolation
Durability
```

The database isolation level should be selected according to application requirements.

Do not use stronger isolation levels unnecessarily because they can reduce concurrency.

---

# 20. Connection Management

Applications must use database connection pooling.

For FastAPI applications:

```text
FastAPI
   ↓
SQLAlchemy
   ↓
Connection Pool
   ↓
PostgreSQL
```

The connection pool should be configured according to:

* Application concurrency
* Database capacity
* Deployment size
* Expected workload

Connections must be properly released.

---

# 21. SQLAlchemy Standards

Backend applications using Python should use SQLAlchemy for database interaction.

Recommended structure:

```text
backend/
├── models/
├── schemas/
├── repositories/
├── services/
└── database/
```

Responsibilities should be separated.

### Models

Define database tables.

### Repositories

Handle database queries.

### Services

Handle business logic.

### Schemas

Handle API input/output validation.

Avoid placing large amounts of business logic directly inside ORM models.

---

# 22. Alembic Migrations

Database schema changes must be managed through Alembic migrations.

Example:

```text
Model Change
     ↓
Alembic Migration
     ↓
Review
     ↓
Migration Execution
     ↓
Database Updated
```

Never depend on manually modifying production tables.

Migration files must be:

* Version controlled
* Reviewable
* Reproducible
* Tested

---

# 23. Migration Safety

Production migrations must consider:

* Existing data
* Downtime
* Backward compatibility
* Rollback strategy
* Large-table operations
* Index creation
* Data transformation

Avoid destructive migrations without an explicit migration strategy.

For example, instead of immediately removing a production column:

```text
Deploy code without using column
        ↓
Verify
        ↓
Migrate data if required
        ↓
Remove column later
```

---

# 24. Redis Usage

Redis may be used for:

* Caching
* Session data
* Rate limiting
* Temporary state
* Distributed locks
* Job queues

Redis should not normally be the source of truth for permanent business data.

Example:

```text
Request
   ↓
Redis Cache
   ↓
Cache Miss
   ↓
PostgreSQL
   ↓
Redis
```

---

# 25. Qdrant and Vector Data

Qdrant is used for vector search and semantic retrieval.

Typical flow:

```text
Document
   ↓
Chunking
   ↓
Embedding
   ↓
Qdrant
```

Qdrant should store:

* Embeddings
* Chunk content or references
* Metadata
* Document identifiers
* Filtering metadata

Transactional business records should remain in PostgreSQL.

Example:

```text
PostgreSQL
    ↓
Document Metadata

Qdrant
    ↓
Document Embeddings
```

---

# 26. RAG Metadata

RAG systems should maintain metadata such as:

```text
document_id
source
category
version
created_at
updated_at
chunk_id
permissions
```

Metadata should support:

* Filtering
* Versioning
* Access control
* Document tracking
* Re-indexing

Sensitive documents must have appropriate access-control metadata.

---

# 27. Agent and Workflow Data

The Agentic SDLC platform may persist:

```text
projects
requirements
agent_runs
workflow_runs
tasks
approvals
generated_artifacts
deployment_records
audit_logs
```

Example:

```text
Project
   ↓
Workflow Run
   ↓
Agent Run
   ↓
Task
   ↓
Artifact
```

Long-running agent workflows should store enough state to support recovery and observability.

---

# 28. LangGraph State

LangGraph workflow state/checkpoints should be handled through the configured persistence mechanism.

Database storage may be used for:

* Workflow checkpoints
* Execution status
* Agent state
* Recovery information

Do not store large transient objects unnecessarily.

Large artifacts should be stored in appropriate object storage such as S3.

---

# 29. Security

Database security must include:

* Least-privilege database users
* Strong authentication
* Encrypted connections
* Encryption at rest where supported
* Network restrictions
* Private database access
* Secret management
* Access auditing

Applications must not use PostgreSQL superuser credentials.

---

# 30. Secrets

Database credentials must never be hardcoded.

Never store:

```text
DATABASE_PASSWORD="password123"
```

inside source code.

Use:

* AWS Secrets Manager
* Environment variables
* Secure CI/CD secrets
* Other approved secret-management systems

Do not commit `.env` files containing real credentials.

---

# 31. Sensitive Data

Sensitive information should be:

* Minimized
* Properly protected
* Encrypted when required
* Access controlled
* Excluded from unnecessary logs

Do not store sensitive information unless there is a legitimate business requirement.

---

# 32. Audit Logging

Important operations should be auditable.

Examples:

```text
User created
Project created
Permission changed
Deployment triggered
Database configuration changed
Agent approved deployment
```

Audit records may contain:

```text
actor_id
action
resource
resource_id
timestamp
result
metadata
```

Avoid storing secrets or sensitive payloads inside audit logs.

---

# 33. Backup and Recovery

Production databases must have:

* Automated backups
* Retention policies
* Recovery procedures
* Disaster recovery planning
* Backup monitoring

The system should define:

```text
RPO = Recovery Point Objective
RTO = Recovery Time Objective
```

Backups must be tested periodically.

A backup that has never been restored should not be considered fully validated.

---

# 34. Environment Separation

Use separate databases or isolated database environments for:

```text
Development
Testing
Staging
Production
```

Production data must not be copied into development environments without appropriate security controls and data sanitization.

---

# 35. Performance

Database performance must consider:

* Query complexity
* Indexes
* Connection pool size
* Table size
* Data growth
* Lock contention
* Query frequency
* Caching
* Read/write patterns

Slow queries should be investigated using PostgreSQL query-analysis tools.

---

# 36. Scalability

The database architecture should support future growth.

Possible strategies:

```text
Vertical Scaling
      ↓
Read Replicas
      ↓
Caching
      ↓
Partitioning
      ↓
Database Sharding
```

Do not introduce distributed database complexity unless the application's scale requires it.

---

# 37. Database Partitioning

Partitioning may be considered for very large tables.

Good candidates may include:

```text
audit_logs
events
metrics
large historical datasets
```

Partitioning should be introduced only when there is a clear performance or operational benefit.

---

# 38. Data Retention

Each major data category should have an appropriate retention policy.

Examples:

```text
Temporary agent state → Short retention
Application data      → Business-defined retention
Audit logs            → Compliance-defined retention
Generated artifacts   → Project-defined retention
```

Expired data should be cleaned up safely.

---

# 39. Database Testing

Database-related tests should include:

* Model tests
* Constraint tests
* Repository tests
* Transaction tests
* Migration tests
* Integration tests
* Query performance tests where required

Test databases should be isolated from production databases.

---

# 40. Agent-Generated Database Design

When an AI agent designs a database, it must:

1. Read requirements.
2. Read architecture standards.
3. Identify entities.
4. Identify relationships.
5. Define schemas.
6. Define constraints.
7. Identify indexes.
8. Identify security requirements.
9. Identify scalability requirements.
10. Define migration strategy.
11. Validate the design.
12. Generate database artifacts.

The agent must not blindly generate tables from natural-language requirements.

---

# 41. Expected Database Design Artifacts

The Database Design Agent should produce:

```text
Entity definitions
        ↓
ER/Data model
        ↓
Table definitions
        ↓
Relationships
        ↓
Constraints
        ↓
Indexes
        ↓
Migration strategy
        ↓
Security considerations
        ↓
Backup/recovery considerations
        ↓
SQLAlchemy models
        ↓
Alembic migrations
```

---

# 42. Database Design Checklist

Before implementation, verify:

* [ ] All major entities identified
* [ ] Relationships defined
* [ ] Primary keys defined
* [ ] Foreign keys defined
* [ ] Constraints defined
* [ ] Appropriate data types selected
* [ ] Naming conventions followed
* [ ] Timestamps included where required
* [ ] Indexes designed according to queries
* [ ] Pagination considered
* [ ] Transactions identified
* [ ] Connection pooling considered
* [ ] SQLAlchemy structure defined
* [ ] Alembic migration strategy defined
* [ ] Redis usage justified
* [ ] Qdrant usage separated from transactional data
* [ ] RAG metadata defined
* [ ] Agent/workflow persistence considered
* [ ] Security requirements defined
* [ ] Backup/recovery considered
* [ ] Environment separation defined
* [ ] Scalability considered
* [ ] Testing strategy defined

---

# 43. Agentic SDLC Database Rule

> **Database design must be derived from requirements and architecture, enforce data integrity through appropriate constraints, use PostgreSQL as the primary transactional database by default, use Redis and Qdrant only for their intended purposes, manage schema changes through Alembic migrations, protect sensitive data, and produce a production-ready, scalable, secure database design before implementation begins.**


# 4A. Explicit Schema Design Template

Every database designed by an AI agent must follow the schema template below before generating SQLAlchemy models or Alembic migrations.

## Schema Design Template

### Entity

```text
Entity Name:
Purpose:
Description:
```

### Table

```text
Table Name:
Purpose:
```

### Columns

| Column     | Data Type   | Nullable | Default | Key | Description           |
| ---------- | ----------- | -------- | ------- | --- | --------------------- |
| id         | UUID        | NO       | uuid    | PK  | Unique identifier     |
| created_at | TIMESTAMPTZ | NO       | now()   |     | Creation timestamp    |
| updated_at | TIMESTAMPTZ | NO       | now()   |     | Last update timestamp |

### Constraints

```text
Primary Key:
Foreign Keys:
Unique Constraints:
Check Constraints:
Not Null Constraints:
Default Values:
```

### Relationships

```text
Relationship:
Related Entity:
Cardinality:
Delete Behavior:
Update Behavior:
```

Example:

```text
User 1 ───── N Projects

projects.user_id
        ↓
users.id

ON DELETE CASCADE
```

### Indexes

| Index Name              | Columns    | Type   | Purpose                |
| ----------------------- | ---------- | ------ | ---------------------- |
| idx_projects_user_id    | user_id    | B-tree | User project lookup    |
| idx_projects_created_at | created_at | B-tree | Recent project queries |

### Data Lifecycle

```text
Creation:
Updates:
Soft Delete:
Hard Delete:
Retention:
Archival:
```

### Security

```text
Sensitive Fields:
Encryption Required:
Access Restrictions:
Audit Required:
PII Handling:
```

### Performance

```text
Expected Read Pattern:
Expected Write Pattern:
High-Frequency Queries:
Caching Required:
Pagination Required:
Partitioning Required:
```

### Migration

```text
Migration Required:
Migration Type:
Backward Compatibility:
Data Migration Required:
Rollback Strategy:
Production Risk:
```

---

## Complete Example

### Entity

```text
Entity Name: Project

Purpose:
Represents an application/project created and managed by the Agentic SDLC platform.
```

### Table

```text
Table Name: projects

Purpose:
Stores project-level information and ownership.
```

### Columns

| Column      | Data Type    | Nullable | Default   | Key | Description            |
| ----------- | ------------ | -------- | --------- | --- | ---------------------- |
| id          | UUID         | NO       | uuid      | PK  | Project identifier     |
| user_id     | UUID         | NO       | —         | FK  | Project owner          |
| name        | VARCHAR(255) | NO       | —         |     | Project name           |
| description | TEXT         | YES      | NULL      |     | Project description    |
| status      | VARCHAR(50)  | NO       | `created` |     | Current project status |
| created_at  | TIMESTAMPTZ  | NO       | now()     |     | Creation timestamp     |
| updated_at  | TIMESTAMPTZ  | NO       | now()     |     | Last update timestamp  |

### Constraints

```text
Primary Key:
    projects.id

Foreign Key:
    projects.user_id → users.id

Unique:
    name per user

Not Null:
    user_id
    name
    status
    created_at
    updated_at
```

### Relationships

```text
User 1 ───── N Projects

users.id
    ↓
projects.user_id
```

### Indexes

```text
idx_projects_user_id
    → projects(user_id)

idx_projects_status
    → projects(status)

idx_projects_created_at
    → projects(created_at)
```

### Security

```text
Project data must only be accessible to authorized users.

user_id must be validated against the authenticated user.

Sensitive project information must not be written to application logs.
```

### Migration

```text
Create projects table
        ↓
Create constraints
        ↓
Create indexes
        ↓
Validate migration
        ↓
Deploy
```

---

## Agent Rule

The Database Design Agent must complete this schema template for **every major entity** before generating:

```text
Schema Design
     ↓
SQLAlchemy Models
     ↓
Alembic Migration
     ↓
Database Tests
```

No database table should be generated without an explicit schema definition.
