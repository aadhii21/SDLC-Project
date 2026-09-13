# Integration Testing Standards

## 1. Purpose

Define standards for testing interactions between multiple application components and external dependencies.

Integration tests must verify that independently developed components work correctly together.

---

# 2. Integration Testing Standards Summary

Integration tests must validate:

* Component interactions
* Database integration
* API integration
* External service integration
* Authentication integration
* Repository behavior
* Service-to-repository communication
* FastAPI dependency integration
* RAG component integration
* Agent-to-tool integration
* Configuration integration

Integration tests should use realistic environments while remaining isolated from production.

---

# 3. Definition of Integration Test

An integration test verifies that two or more components work correctly together.

Example:

```text
API
 ↓
Service
 ↓
Repository
 ↓
PostgreSQL
```

Unlike unit tests, integration tests may use real infrastructure such as:

```text
PostgreSQL
Redis
Qdrant
Docker services
Test APIs
```

---

# 4. Integration Testing Goals

Integration testing must identify problems involving:

```text
Component A
     ↓
Component B
     ↓
Component C
```

Examples:

* Incorrect database queries
* Incorrect ORM mappings
* API contract mismatches
* Serialization problems
* Authentication integration problems
* Incorrect dependency configuration
* External service failures

---

# 5. Integration vs Unit Testing

| Area         | Unit Test         | Integration Test                   |
| ------------ | ----------------- | ---------------------------------- |
| Scope        | Single component  | Multiple components                |
| Database     | Mocked            | Usually real/test DB               |
| External API | Mocked            | Test/staging API where appropriate |
| Speed        | Very fast         | Slower                             |
| Isolation    | High              | Moderate                           |
| Purpose      | Logic correctness | Component interaction              |
| Environment  | Minimal           | Realistic                          |

---

# 6. Integration Test Project Structure

Recommended:

```text
tests/
├── integration/
│   ├── test_database.py
│   ├── test_repositories.py
│   ├── test_services.py
│   ├── test_external_apis.py
│   ├── test_authentication.py
│   ├── test_rag.py
│   ├── test_agents.py
│   └── test_workflows.py
│
├── fixtures/
└── conftest.py
```

Tests should be organized according to integration boundaries.

---

# 7. Integration Environment

Integration tests must use a dedicated environment.

Recommended:

```text
Development
     ↓
Integration/Test Environment
     ↓
Staging
     ↓
Production
```

Never run integration tests against production infrastructure unless explicitly approved for a controlled test.

---

# 8. Database Integration Testing

Database integration tests must verify:

* Connection
* Schema
* Tables
* Constraints
* Relationships
* Queries
* Transactions
* ORM mappings
* Indexes where relevant
* Migrations

Example:

```python
def test_create_project(db):
    project = Project(name="Demo")

    db.add(project)
    db.commit()

    result = db.query(Project).filter_by(name="Demo").first()

    assert result is not None
```

---

# 9. PostgreSQL Integration

For PostgreSQL-backed applications, integration tests should preferably use a dedicated test database.

Example:

```text
Application
    ↓
SQLAlchemy
    ↓
PostgreSQL Test DB
```

Do not use production database credentials.

---

# 10. Database Isolation

Each test must avoid affecting other tests.

Preferred strategies:

```text
Transaction rollback
Test database recreation
Test schema
Unique test data
Database cleanup
```

Example:

```text
Test A
 ↓
Insert data
 ↓
Rollback
 ↓
Test B
```

---

# 11. Database Fixtures

Database setup should be centralized through fixtures.

Example:

```python
import pytest

@pytest.fixture
def db_session():
    session = create_test_session()

    yield session

    session.rollback()
    session.close()
```

Fixtures must clean up resources after the test.

---

# 12. Database Migration Testing

Integration tests must verify that migrations can be applied successfully.

Example:

```bash
alembic upgrade head
```

Validate:

```text
Migration
   ↓
Database Schema
   ↓
Application
```

Migration failures must block deployment.

---

# 13. Repository Integration Testing

Repository tests should verify actual database interaction.

Example:

```python
def test_project_repository_create(db_session):
    repository = ProjectRepository(db_session)

    project = repository.create("Demo")

    assert project.id is not None
    assert project.name == "Demo"
```

Unlike unit tests, the database should normally be real test infrastructure.

---

# 14. Service + Repository Integration

Verify that services correctly communicate with repositories.

Flow:

```text
Service
   ↓
Repository
   ↓
Database
```

Example:

```python
def test_create_project_service(db_session):
    repository = ProjectRepository(db_session)
    service = ProjectService(repository)

    result = service.create_project("Demo")

    assert result.name == "Demo"
```

---

# 15. FastAPI Integration Testing

FastAPI integration tests should verify application components together.

Example:

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_project():
    response = client.post(
        "/api/v1/projects",
        json={"name": "Demo"}
    )

    assert response.status_code == 201
```

The test should validate the complete application path where appropriate.

---

# 16. API + Database Integration

Verify that API requests correctly affect the database.

Flow:

```text
HTTP Request
     ↓
FastAPI
     ↓
Service
     ↓
Repository
     ↓
PostgreSQL
```

Example:

```python
def test_create_project_persists_data(client, db_session):
    response = client.post(
        "/api/v1/projects",
        json={"name": "Demo"}
    )

    assert response.status_code == 201

    project = db_session.query(Project).filter_by(
        name="Demo"
    ).first()

    assert project is not None
```

---

# 17. Request Validation Integration

Verify that FastAPI validation works correctly with application logic.

Test:

```text
Valid Request
     ↓
Application
     ↓
Success
```

and:

```text
Invalid Request
     ↓
Validation
     ↓
400/422
```

depending on the API contract.

---

# 18. Response Integration Testing

Verify that application output is correctly converted into API responses.

Validate:

* Response structure
* Required fields
* Data types
* Nested objects
* Serialization
* Null handling

Example:

```python
def test_project_response(client):
    response = client.get("/api/v1/projects/1")

    body = response.json()

    assert "id" in body
    assert "name" in body
```

---

# 19. Authentication Integration Testing

Authentication must be tested across the application stack.

Example:

```text
Request
 ↓
Authentication
 ↓
Token Validation
 ↓
User Context
 ↓
Endpoint
```

Test:

```text
Valid token
Invalid token
Expired token
Missing token
Malformed token
```

---

# 20. Authorization Integration Testing

Authentication and authorization must be tested separately.

Example:

```text
Authenticated User
        ↓
Role / Permission
        ↓
Resource Access
```

Test:

```text
Admin → Allowed
Developer → Allowed where permitted
Normal User → Restricted
Unauthenticated → Rejected
```

---

# 21. External API Integration

External APIs should be tested using:

```text
Test API
Sandbox API
Controlled mock server
```

when available.

Do not depend on unstable third-party production APIs for routine CI integration tests.

---

# 22. External API Failure Testing

Integration tests must verify:

```text
Timeout
Connection Error
5xx
4xx
Malformed Response
Rate Limit
Authentication Failure
```

Example:

```python
def test_external_api_timeout(client):
    response = client.get("/api/v1/external-resource")

    assert response.status_code == 504
```

Expected status codes must follow the API contract.

---

# 23. Redis Integration Testing

If Redis is used, integration tests should verify:

```text
Application
   ↓
Redis
```

Test:

* Set
* Get
* Expiration
* Delete
* Cache invalidation
* Serialization

Example:

```python
def test_cache_set_and_get(redis_client):
    redis_client.set("project:1", "Demo")

    result = redis_client.get("project:1")

    assert result == "Demo"
```

---

# 24. Cache Integration Testing

Verify complete cache behavior:

```text
Request
 ↓
Cache Lookup
 ↓
Cache Hit → Return
 ↓
Cache Miss
 ↓
Database
 ↓
Cache Store
 ↓
Return
```

Tests must verify both cache-hit and cache-miss paths.

---

# 25. RAG Integration Testing

RAG integration tests should verify:

```text
User Query
     ↓
Embedding
     ↓
Vector Database
     ↓
Retriever
     ↓
Context
     ↓
LLM
     ↓
Response
```

Validate that components communicate correctly.

---

# 26. Vector Database Integration

For Qdrant or another vector database, integration tests should verify:

* Collection creation
* Document insertion
* Embedding storage
* Metadata storage
* Similarity search
* Metadata filtering
* Retrieval results

Example:

```python
def test_vector_search(qdrant_client):
    qdrant_client.upsert(
        collection_name="test",
        points=[...]
    )

    results = qdrant_client.search(...)

    assert len(results) > 0
```

Use a dedicated test collection.

---

# 27. RAG Retrieval Integration

Verify:

```text
Query
 ↓
Embedding
 ↓
Vector Search
 ↓
Top-K Documents
 ↓
Metadata Filtering
```

Test that retrieved documents satisfy the requested filters.

---

# 28. LLM Integration Testing

LLM integration tests should verify communication between the application and the configured LLM provider.

Validate:

* API authentication
* Request format
* Model configuration
* Response parsing
* Structured output
* Error handling
* Timeout handling
* Retry handling

Routine CI should prefer controlled test calls or mocked providers to avoid unpredictable cost and latency.

---

# 29. Agent + Tool Integration

Agent integration tests must verify:

```text
Agent
 ↓
Tool Selection
 ↓
Tool Invocation
 ↓
Tool Result
 ↓
Agent
 ↓
Final Result
```

Example:

```python
def test_agent_calls_github_tool(agent, github_tool):
    result = agent.run("Create a repository")

    github_tool.assert_called_once()
    assert result.status == "success"
```

---

# 30. Agent Workflow Integration

For multi-agent systems, test communication between agents.

Example:

```text
Requirements Agent
        ↓
Design Agent
        ↓
Frontend Agent
        ↓
Backend Agent
        ↓
Testing Agent
```

Validate:

* State transfer
* Input/output contracts
* Agent sequencing
* Error propagation
* Workflow recovery

---

# 31. LangGraph Integration Testing

For LangGraph workflows, verify complete graph execution.

Example:

```text
START
 ↓
Requirements
 ↓
Design
 ↓
Backend
 ↓
Testing
 ↓
END
```

Validate:

```text
State updates
Node execution
Conditional edges
Retries
Failures
Final state
```

---

# 32. MCP Integration Testing

MCP integrations must verify:

```text
Agent
 ↓
MCP Client
 ↓
MCP Server
 ↓
Tool
 ↓
Result
```

Test:

* Tool discovery
* Tool input
* Tool invocation
* Tool output
* Invalid parameters
* Tool errors
* Timeout handling

Use a test MCP server where practical.

---

# 33. GitHub Integration Testing

For GitHub-related workflows, verify:

```text
Agent
 ↓
GitHub MCP / API
 ↓
Repository
 ↓
Branch
 ↓
Commit / PR
```

Tests must use test repositories or controlled environments.

Never allow CI integration tests to modify production repositories.

---

# 34. Jenkins Integration Testing

Jenkins integration tests should verify:

```text
Application
 ↓
Jenkins API / MCP
 ↓
Pipeline
 ↓
Build
 ↓
Build Result
```

Test:

* Job lookup
* Build trigger
* Build status
* Failure handling
* Authentication
* Timeout handling

Use a dedicated Jenkins test job.

---

# 35. AWS Integration Testing

AWS integrations must use a dedicated test account or isolated resources where possible.

Examples:

```text
ECR
S3
ECS
CloudWatch
IAM
```

Avoid destructive tests against production resources.

---

# 36. Docker Integration Testing

Verify that the application works inside its container.

Example:

```text
Source Code
 ↓
Docker Build
 ↓
Container
 ↓
Application
 ↓
Health Check
```

Example:

```bash
docker build -t test-app .
docker run -d -p 8000:8000 test-app
```

Then verify:

```bash
curl http://localhost:8000/health
```

---

# 37. Environment Configuration Testing

Integration tests must verify environment configuration.

Test:

```text
Development
Staging/Test
Production-like
```

Configuration must be supplied through environment variables or secure configuration.

Never commit real secrets.

---

# 38. Transaction Integration Testing

Verify transaction behavior.

Example:

```text
Operation A
 ↓
Operation B
 ↓
Operation C
```

If Operation C fails:

```text
Rollback
 ↓
Database returns to previous state
```

Test both successful and failed transactions.

---

# 39. Concurrency Integration Testing

Integration tests should validate important concurrent operations.

Examples:

```text
Two requests updating same resource
Two workers processing same job
Multiple users creating records
Concurrent cache updates
```

Validate that:

* Data remains consistent
* Duplicate operations are controlled
* Locks work correctly where required
* Race conditions are handled

---

# 40. Background Job Integration Testing

Test complete background-job flows.

Example:

```text
API
 ↓
Create Job
 ↓
Job ID
 ↓
Queue / Worker
 ↓
Processing
 ↓
Status Update
```

Validate:

```text
queued
running
completed
failed
```

---

# 41. Idempotency Integration Testing

Verify idempotency across the complete application stack.

Example:

```text
Request
 ↓
API
 ↓
Service
 ↓
Database
```

Repeated requests with the same idempotency key must not create duplicate side effects.

---

# 42. Integration Test Data

Integration test data must be:

* Controlled
* Reproducible
* Isolated
* Non-production
* Easy to clean up

Example:

```text
test_project_001
test_user_001
test_job_001
```

Never use real customer data.

---

# 43. Integration Test Cleanup

Every integration test must clean up created resources.

Examples:

```text
Database records
Redis keys
Vector collections
Temporary files
Docker containers
Cloud resources
Test repositories
Jenkins jobs
```

Prefer automatic cleanup through fixtures.

---

# 44. Integration Test Markers

Use pytest markers.

Example:

```python
import pytest

@pytest.mark.integration
def test_database_connection():
    ...
```

Run:

```bash
pytest -m integration
```

This allows CI to selectively execute integration tests.

---

# 45. Integration Test Commands

Run all integration tests:

```bash
pytest tests/integration/
```

Verbose:

```bash
pytest tests/integration/ -v
```

Run a specific test:

```bash
pytest tests/integration/test_database.py
```

Run using the marker:

```bash
pytest -m integration
```

With coverage:

```bash
pytest tests/integration/ --cov=app --cov-report=term-missing
```

---

# 46. Docker-Based Integration Environment

When practical, dependencies should run through Docker.

Example:

```text
Docker Compose
      ↓
PostgreSQL
Redis
Qdrant
Application
```

This provides a reproducible integration environment.

Example:

```bash
docker compose up -d
pytest tests/integration/
docker compose down
```

---

# 47. Integration Test CI Standards

Recommended CI sequence:

```text
Formatting
   ↓
Linting
   ↓
Type Checking
   ↓
Unit Tests
   ↓
Integration Environment
   ↓
Integration Tests
   ↓
API Tests
   ↓
Security Tests
   ↓
E2E Tests
```

Integration failures must block deployment promotion.

---

# 48. Integration Test Failure Handling

When an integration test fails, report:

```text
Test Name
Component
Dependency
Failure
Root Cause
Severity
Recommended Fix
```

Example:

```json
{
  "test": "test_create_project",
  "component": "PostgreSQL",
  "status": "failed",
  "severity": "high",
  "reason": "Database migration missing"
}
```

---

# 49. Integration Testing Agent Input

The Integration Testing Agent should receive structured input.

Example:

```json
{
  "project_id": "project-001",
  "language": "python",
  "framework": "fastapi",
  "database": "postgresql",
  "cache": "redis",
  "vector_database": "qdrant",
  "external_services": [
    "github",
    "jenkins",
    "aws"
  ],
  "authentication": "jwt",
  "requirements": [
    "database integration required",
    "API integration required",
    "external services must be validated"
  ]
}
```

---

# 50. Integration Testing Agent Output

The agent should return structured results.

Example:

```json
{
  "tests_generated": 35,
  "tests_passed": 34,
  "tests_failed": 1,
  "database_tests_passed": true,
  "api_tests_passed": true,
  "external_service_tests_passed": true,
  "critical_failures": 0,
  "high_failures": 0,
  "status": "passed"
}
```

---

# 51. Integration Testing Agent Workflow

The Integration Testing Agent should follow:

```text
Receive Backend
       ↓
Analyze Architecture
       ↓
Identify Integration Boundaries
       ↓
Identify External Dependencies
       ↓
Prepare Test Environment
       ↓
Prepare Test Database
       ↓
Prepare Fixtures
       ↓
Generate Integration Tests
       ↓
Run Migrations
       ↓
Start Dependencies
       ↓
Run Integration Tests
       ↓
Analyze Failures
       ↓
Classify Severity
       ↓
Validate Cleanup
       ↓
Generate Report
       ↓
Return Result
```

---

# 52. Integration Testing Validation Checklist

Before marking integration testing complete:

* [ ] Test environment is isolated
* [ ] Test database is configured
* [ ] Database connection is tested
* [ ] Database schema is validated
* [ ] Migrations are tested
* [ ] Repository integration is tested
* [ ] Service + repository integration is tested
* [ ] FastAPI integration is tested
* [ ] API + database integration is tested
* [ ] Authentication integration is tested
* [ ] Authorization integration is tested
* [ ] External API integration is tested
* [ ] Redis integration is tested where applicable
* [ ] Cache behavior is tested
* [ ] RAG integration is tested where applicable
* [ ] Vector database integration is tested where applicable
* [ ] LLM integration is controlled
* [ ] Agent + tool integration is tested
* [ ] MCP integration is tested where applicable
* [ ] GitHub integration is controlled
* [ ] Jenkins integration is controlled
* [ ] AWS integration is isolated
* [ ] Docker integration is tested
* [ ] Background jobs are tested
* [ ] Idempotency is tested
* [ ] Concurrency is tested where required
* [ ] Test data is isolated
* [ ] Resources are cleaned up
* [ ] No production secrets are used
* [ ] No destructive production operations are performed
* [ ] All critical/high failures are resolved

---

# 53. Integration Testing Quality Gates

Integration testing passes only when:

```text
Integration Environment Ready
          +
Required Dependencies Available
          +
Database Integration Passed
          +
API Integration Passed
          +
Required External Integrations Passed
          +
Critical Failures = 0
          +
High Failures = 0
          +
Cleanup Successful
          ↓
INTEGRATION TESTING PASSED
```

Otherwise:

```text
INTEGRATION TESTING FAILED
```

The agent must provide the failure reason.

---

# 54. Final Integration Testing Rule

Integration testing must prove that application components work correctly together in an isolated, reproducible, and production-representative environment.

Integration tests must validate important boundaries such as API → Service → Repository → Database, external services, RAG pipelines, Agent → Tool workflows, MCP integrations, background jobs, authentication, authorization, and infrastructure integrations where applicable.

No application should proceed to final deployment validation when required integration tests contain unresolved Critical or High-severity failures.
