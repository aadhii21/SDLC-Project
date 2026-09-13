# Staging Rules

## 1. Purpose

This document defines standards for the staging environment of the Agentic SDLC platform.

The staging environment is the final validation environment before production.

It must closely represent production while remaining isolated from real production users, credentials, and data.

---

## 2. Staging Environment Principle

The staging environment must answer:

> "Is this application safe and ready to deploy to production?"

Staging must validate:

* Application functionality
* API behavior
* Database integration
* Authentication
* Authorization
* Security
* Docker image
* ECS deployment
* Infrastructure
* Performance
* Agent workflows
* RAG
* MCP
* External integrations
* Observability
* Rollback

---

## 3. Staging Position in CI/CD

Recommended flow:

```text
Developer
    ↓
Git
    ↓
Build
    ↓
Unit Tests
    ↓
Security Tests
    ↓
Docker Build
    ↓
ECR
    ↓
STAGING
    ↓
Integration Tests
    ↓
E2E Tests
    ↓
Security Validation
    ↓
Smoke Tests
    ↓
Approval
    ↓
PRODUCTION
```

AWS's CI/CD guidance similarly places staging before production and uses staging for integration/load/other tests.

---

## 4. Staging Must Be Production-Like

Staging should resemble production in:

* Application architecture
* Container runtime
* ECS configuration
* Networking
* IAM model
* Database technology
* Cache technology
* Load balancer
* Monitoring
* Secrets management
* Deployment strategy

Avoid creating a completely different staging architecture.

---

## 5. Staging vs Production

Staging and production should be similar but isolated.

| Area       | Staging          | Production          |
| ---------- | ---------------- | ------------------- |
| ECS        | Yes              | Yes                 |
| ECR        | Yes              | Yes                 |
| ALB        | Yes              | Yes                 |
| Database   | Staging DB       | Production DB       |
| Secrets    | Staging secrets  | Production secrets  |
| Users      | Test users       | Real users          |
| Data       | Synthetic/masked | Production data     |
| Traffic    | Test traffic     | Real traffic        |
| Scaling    | Reduced          | Production capacity |
| Deployment | Automated        | Controlled          |
| Approval   | Validation       | Production approval |

---

## 6. Staging Isolation

Staging must not accidentally access production resources.

Do not allow:

```text
Staging ECS
    ↓
Production Database
```

unless explicitly approved for a controlled migration or compatibility test.

Preferred:

```text
Staging ECS
    ↓
Staging Database
```

---

## 7. Staging AWS Resources

Where appropriate, staging should have separate:

```text
VPC
Subnets
Security Groups
ECS Service
ECR Repository/Images
Database
Redis
Secrets
CloudWatch Logs
ALB
Target Groups
```

Resource sharing should be intentional rather than accidental.

---

## 8. Staging Naming

Use consistent environment naming.

Examples:

```text
agentic-sdlc-staging
myapp-staging
myapp-staging-db
/ecs/myapp/staging
```

Avoid ambiguous names such as:

```text
test
new
temp
demo
```

---

## 9. Staging Branch

The organization should define a clear promotion strategy.

Example:

```text
feature/*
    ↓
develop
    ↓
staging
    ↓
main
```

or:

```text
feature/*
    ↓
main
    ↓
automatic staging deployment
    ↓
production approval
```

The chosen strategy must be documented and consistent.

---

## 10. Staging Deployment Trigger

Staging deployment may be triggered by:

* Merge to staging branch
* Pull request merge
* Successful CI pipeline
* Release candidate creation
* Manual deployment

Recommended:

```text
Code Merge
    ↓
CI Quality Gates
    ↓
Automatic Staging Deployment
```

---

## 11. Staging Image

Staging should use the same validated image intended for production whenever possible.

Preferred:

```text
Build Once
    ↓
Scan
    ↓
ECR
    ↓
Staging
    ↓
Production
```

Avoid rebuilding the image between staging and production.

---

## 12. Image Traceability

Every staging deployment must be traceable to:

```text
Repository
    ↓
Commit SHA
    ↓
Jenkins Build
    ↓
Docker Image
    ↓
ECR Digest
    ↓
ECS Task Definition
```

---

## 13. No `latest`

Staging should not depend exclusively on:

```text
myapp:latest
```

Use:

```text
myapp:build-152
```

or preferably an immutable digest:

```text
myapp@sha256:abc123...
```

---

## 14. Staging ECS

The staging application should run using the same ECS architecture as production where practical.

Example:

```text
ALB
 ↓
ECS Service
 ↓
Tasks
 ↓
ECR
```

The task configuration should be production-like while using staging-sized resources.

---

## 15. Staging Capacity

Staging does not necessarily require production capacity.

Example:

```text
Production:
Min = 2
Desired = 3
Max = 10

Staging:
Min = 1
Desired = 1
Max = 3
```

Capacity must still be sufficient for meaningful testing.

---

## 16. Staging Auto Scaling

Auto Scaling should be tested in staging when it is part of the production architecture.

Example:

```text
Load
 ↓
CloudWatch
 ↓
ECS Auto Scaling
 ↓
Task Count
```

Staging should verify that scaling policies actually behave as expected.

---

## 17. Staging Load Balancer

If production uses an ALB, staging should preferably use an ALB too.

Example:

```text
staging-api.example.com
        ↓
Staging ALB
        ↓
Staging ECS
```

---

## 18. Staging HTTPS

External staging endpoints should use HTTPS where practical.

Example:

```text
https://staging-api.example.com
```

Staging TLS configuration should be equivalent to production where possible.

---

## 19. Staging Authentication

Staging must use realistic authentication flows.

Test:

```text
Valid Login
Invalid Login
Expired Token
Missing Token
Invalid Token
Logout
Refresh Token
```

Do not disable authentication merely to simplify testing.

---

## 20. Staging Authorization

Authorization must also be tested.

Example:

```text
Admin
User
Read-only User
Unauthorized User
```

Verify that users cannot access resources outside their permissions.

---

## 21. Staging Test Users

Use dedicated staging test accounts.

Do not use real customer accounts.

Example:

```text
test-admin
test-user
test-readonly
test-agent
```

Credentials must be securely managed.

---

## 22. Staging Data

Staging should use:

* Synthetic data
* Generated test data
* Sanitized data
* Masked datasets

Production customer data must not be copied into staging without explicit authorization and appropriate protection.

---

## 23. Database

Staging should use a dedicated database where possible.

Example:

```text
Production → prod-db
Staging    → staging-db
```

---

## 24. Database Schema Validation

Every database migration must be tested in staging before production.

Flow:

```text
Migration
    ↓
Staging DB
    ↓
Integration Tests
    ↓
Application Validation
    ↓
Production
```

---

## 25. Migration Safety

Production database migrations should be backward compatible where practical.

Preferred:

```text
Add New Column
    ↓
Deploy Compatible Code
    ↓
Migrate Data
    ↓
Remove Old Column Later
```

Avoid destructive schema changes in the same release unless explicitly validated.

---

## 26. Staging Database Backup

Staging backups should follow organizational requirements.

Important migrations should have a tested recovery strategy before production execution.

---

## 27. Redis / Cache

If production uses Redis or another cache, staging should use a separate staging instance or logically isolated environment.

Do not allow:

```text
Staging Application
      ↓
Production Redis
```

---

## 28. External APIs

Staging should use:

* Sandbox APIs
* Test endpoints
* Dedicated staging credentials
* Mock services where appropriate

Avoid sending unintended real customer transactions.

---

## 29. Payment Integrations

If payment integrations exist, staging must use the provider's test/sandbox environment.

Never execute real financial transactions from staging.

---

## 30. Email and Notifications

Staging emails should not accidentally reach real customers.

Use:

* Test recipients
* Mail sandbox
* Notification sink
* Dedicated staging channels

---

## 31. Third-Party Integrations

Every important external integration should be validated in staging.

Examples:

```text
GitHub
Jenkins
AWS
Slack
LLM APIs
Vector DB
MCP Servers
Payment APIs
Email
```

---

## 32. LLM Testing

The staging environment must validate:

* Model connectivity
* Prompt behavior
* Tool calling
* Structured output
* Token limits
* Timeouts
* Retry behavior
* Failure handling

Production LLM credentials should not be used in staging unless explicitly required and protected.

---

## 33. RAG Testing

Staging must validate:

```text
Document Ingestion
      ↓
Chunking
      ↓
Embedding
      ↓
Vector Storage
      ↓
Retrieval
      ↓
Context
      ↓
LLM
      ↓
Answer
```

Validate:

* Retrieval relevance
* Metadata filtering
* Access control
* Prompt injection resistance
* Missing-context behavior
* Hallucination controls

---

## 34. Agent Testing

Every important Agentic SDLC workflow should be tested in staging.

Examples:

```text
Requirements Agent
Design Agent
Frontend Agent
Backend Agent
Testing Agent
Security Agent
DevOps Agent
Deployment Agent
Monitoring Agent
```

---

## 35. Agent Workflow Validation

Validate:

```text
Agent A
  ↓
Agent B
  ↓
Agent C
  ↓
Quality Gate
  ↓
Next Agent
```

A failed mandatory agent must block downstream production promotion.

---

## 36. MCP Testing

MCP integrations should be tested in staging.

Validate:

* Tool discovery
* Authentication
* Tool invocation
* Input validation
* Output validation
* Timeout
* Error handling
* Permission boundaries

---

## 37. GitHub Integration

If GitHub is used:

```text
Agent
 ↓
GitHub MCP
 ↓
Repository
```

Staging should verify that:

* Repository access works
* Branch rules work
* Pull requests can be created where authorized
* Commits are traceable
* Unauthorized repository access is blocked

---

## 38. Jenkins Integration

Staging should validate Jenkins automation.

Example:

```text
Git
 ↓
Jenkins
 ↓
Build
 ↓
Test
 ↓
Docker
 ↓
ECR
 ↓
ECS Staging
```

---

## 39. Terraform Validation

Infrastructure changes should be validated before staging deployment.

Recommended:

```bash
terraform fmt -check
terraform validate
terraform plan
```

Security scanning should also be performed.

---

## 40. Application Testing

Staging must run appropriate:

```text
Unit Tests
Integration Tests
API Tests
E2E Tests
Security Tests
Regression Tests
Smoke Tests
```

---

## 41. Integration Tests

Integration testing should validate real service boundaries where practical.

Examples:

```text
FastAPI
 ↓
PostgreSQL

FastAPI
 ↓
Redis

Agent
 ↓
Vector DB

Agent
 ↓
MCP

Application
 ↓
AWS
```

---

## 42. End-to-End Testing

Critical user journeys should be tested from beginning to end.

Example:

```text
Create Project
    ↓
Requirements
    ↓
Design
    ↓
Frontend
    ↓
Backend
    ↓
Testing
    ↓
Security
    ↓
Docker
    ↓
ECR
    ↓
ECS
    ↓
Health
```

---

## 43. Smoke Tests

After deployment:

```bash
curl --fail https://staging-api.example.com/health
```

Then test critical APIs.

Example:

```bash
curl --fail https://staging-api.example.com/api/v1/projects
```

Authentication should be included where required.

---

## 44. Regression Testing

Existing functionality must be tested after new changes.

Regression testing should cover:

* Existing APIs
* Authentication
* Authorization
* Database operations
* Critical workflows
* Agent workflows
* Integrations

---

## 45. Security Testing

Staging must run security checks before production.

Examples:

```text
Dependency Scan
Container Scan
Secret Scan
SAST
DAST
API Security Tests
IAM Validation
Infrastructure Scan
```

---

## 46. Dependency Security

Run:

```bash
pip-audit
```

before production promotion.

Vulnerabilities must follow the organization's severity policy.

---

## 47. Container Security

The staging image must be scanned before promotion.

Example:

```text
Docker Image
     ↓
ECR
     ↓
Vulnerability Scan
     ↓
Pass
     ↓
Staging
```

---

## 48. Secret Scanning

Staging must verify that generated application artifacts do not contain:

* AWS credentials
* API keys
* Database passwords
* Private keys
* LLM keys
* GitHub tokens

---

## 49. Performance Testing

Staging should be used for performance validation when required.

Test:

```text
Response Time
Throughput
Concurrency
CPU
Memory
Database Load
External API Latency
```

---

## 50. Load Testing

Load tests should simulate expected production traffic.

Example:

```text
Normal Load
     ↓
Peak Load
     ↓
Stress Load
     ↓
Observe
```

The goal is to determine whether:

* Application remains stable
* Auto Scaling works
* Database remains healthy
* Error rates remain acceptable
* Latency remains acceptable

---

## 51. Auto Scaling Test

Where applicable:

```text
Increase Load
    ↓
CPU/Memory/Request Metric
    ↓
Scaling Policy
    ↓
Task Count Increases
```

Then:

```text
Load Decreases
    ↓
Cooldown
    ↓
Task Count Decreases
```

---

## 52. Failure Testing

Staging should test important failure scenarios.

Examples:

```text
Database unavailable
Redis unavailable
LLM unavailable
MCP unavailable
ECR image pull failure
Invalid secret
External API timeout
Container crash
Task health failure
```

---

## 53. Retry Validation

Retries must be bounded.

Example:

```text
Request
 ↓
Failure
 ↓
Retry 1
 ↓
Retry 2
 ↓
Retry 3
 ↓
Fail
```

Avoid infinite retries.

---

## 54. Timeout Validation

Every external dependency should have an appropriate timeout.

Examples:

```text
LLM Timeout
Database Timeout
HTTP Timeout
MCP Timeout
Job Timeout
```

---

## 55. Observability

Staging must provide enough observability to diagnose production-like failures.

Monitor:

```text
Application Logs
ECS Logs
CPU
Memory
Task Count
ALB Metrics
HTTP Errors
Latency
Database Metrics
Agent Jobs
LLM Errors
RAG Errors
MCP Errors
```

---

## 56. CloudWatch

Staging should use CloudWatch where production uses CloudWatch.

This allows dashboards and alarms to be tested before production.

---

## 57. Staging Alarms

Important staging alarms should be configured for:

```text
High CPU
High Memory
High 5xx
Unhealthy Targets
Task Count
Application Errors
Database Problems
```

Staging alarms may have different thresholds from production.

---

## 58. Log Retention

Staging logs should have a defined retention period.

Do not retain unlimited logs without a business or compliance reason.

---

## 59. Deployment Strategy

Staging may use:

```text
Rolling Deployment
```

or, when production uses advanced traffic shifting:

```text
Blue/Green
Canary
Linear
```

Staging should validate the same deployment mechanism intended for production where practical.

---

## 60. Blue/Green Validation

For blue/green deployments:

```text
Blue
 ↓
Current Version

Green
 ↓
New Version
```

Test the green environment before traffic is shifted.

Modern ECS supports native blue/green deployments with testing, traffic shifting, monitoring, bake time, and rollback mechanisms.

---

## 61. Canary Validation

For high-risk releases, staging can validate canary deployment behavior.

Example:

```text
Old Version = 100%
        ↓
New Version = 10%
        ↓
Monitor
        ↓
New Version = 100%
```

AWS recommends validating new revisions in staging before canary production deployment.

---

## 62. Staging Deployment Rollback

Rollback must be tested.

Example:

```text
Staging v2
   ↓
Failure
   ↓
Rollback
   ↓
Staging v1
   ↓
Health Check
```

Rollback should use the previous known-good immutable artifact.

---

## 63. Database Rollback

Application rollback and database rollback are not always the same.

Example:

```text
Application
Rollback v2 → v1

Database
Migration may remain
```

Therefore database migrations must be designed for compatibility.

---

## 64. Environment Variables

Staging configuration must be explicitly separated from production.

Example:

```text
ENVIRONMENT=staging
DATABASE_URL=<staging>
REDIS_URL=<staging>
LLM_CONFIGURATION=<staging>
```

Never accidentally load production configuration.

---

## 65. Secrets

Staging secrets should be separate from production secrets.

Example:

```text
/staging/myapp/database
/staging/myapp/llm
/staging/myapp/github
```

Production:

```text
/production/myapp/database
/production/myapp/llm
/production/myapp/github
```

---

## 66. IAM Separation

Staging IAM roles should not automatically receive production permissions.

Example:

```text
Staging ECS Task Role
       ↓
Staging Resources

Production ECS Task Role
       ↓
Production Resources
```

---

## 67. Network Separation

Staging and production network access must be controlled.

Security groups, routing, and network policies must prevent unintended cross-environment access.

---

## 68. Staging Data Cleanup

Test data should be cleaned periodically.

Examples:

```text
Temporary Projects
Test Users
Generated Files
Test Jobs
Temporary Database Records
Test Vector Documents
```

---

## 69. Test Data Isolation

Tests must not interfere with each other.

Use:

* Unique IDs
* Dedicated test databases
* Transactions where appropriate
* Cleanup fixtures
* Isolated namespaces/resources

---

## 70. Staging Environment Reset

The environment should have a documented reset strategy.

Possible approaches:

```text
Database Reset
Seed Data
Infrastructure Recreation
Container Redeployment
Test Data Cleanup
```

---

## 71. Staging Stability

The staging environment should remain stable enough for teams and agents to validate releases.

Avoid frequent unrelated manual changes.

Infrastructure should preferably be managed through Terraform.

---

## 72. Infrastructure Drift

Detect infrastructure drift.

Recommended:

```bash
terraform plan
```

Unexpected changes should be investigated.

---

## 73. Manual Changes

Manual production-like changes should be avoided.

If a manual staging change is required:

1. Document it.
2. Validate it.
3. Reconcile Terraform.
4. Remove temporary configuration where appropriate.

---

## 74. Staging CI/CD Pipeline

Recommended pipeline:

```text
Checkout
   ↓
Lint
   ↓
Type Check
   ↓
Unit Tests
   ↓
Integration Tests
   ↓
Security Scan
   ↓
Docker Build
   ↓
Image Scan
   ↓
ECR Push
   ↓
Deploy Staging
   ↓
Health Check
   ↓
E2E Tests
   ↓
Performance/Security Tests
   ↓
Staging Gate
   ↓
Production Approval
```

---

## 75. Staging Quality Gate

The staging gate must verify:

```text
Build Passed
Tests Passed
Security Passed
Image Passed
Deployment Passed
Health Passed
E2E Passed
Critical Regression = 0
Critical Security Findings = 0
```

---

## 76. Mandatory Production Promotion Conditions

Production promotion must not occur when:

```text
Staging Deployment Failed
        OR
Health Check Failed
        OR
Critical Test Failed
        OR
Critical Security Finding
        OR
Required E2E Test Failed
        OR
Required Performance Gate Failed
        OR
Rollback Test Failed
```

---

## 77. Staging Approval

For controlled production releases:

```text
Staging
   ↓
All Gates Passed
   ↓
Release Candidate
   ↓
Production Approval
   ↓
Production
```

The approval should identify:

* Build number
* Commit SHA
* Image digest
* Test result
* Security result
* Release version

---

## 78. Staging Release Candidate

A release candidate should be immutable.

Example:

```text
Application
Commit: a81f92c

Docker:
sha256:abc123

Jenkins:
Build #152

Environment:
Staging
```

The same artifact should be promoted to production.

---

## 79. Staging and Agentic SDLC

The complete Agentic SDLC should be validated in staging.

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
        ↓
Security Agent
        ↓
DevOps Agent
        ↓
Deployment Agent
        ↓
Staging
        ↓
Validation
        ↓
Production
```

---

## 80. Agent Quality Gates

Each mandatory agent should return structured status.

Example:

```json
{
  "status": "passed",
  "errors": [],
  "warnings": []
}
```

A mandatory failure should stop the workflow.

---

## 81. Staging Job Validation

Long-running Agentic SDLC jobs should be tested.

Example:

```text
POST /projects
       ↓
job_id
       ↓
queued
       ↓
running
       ↓
completed
```

Failure:

```text
queued
 ↓
running
 ↓
failed
```

---

## 82. Staging Job Recovery

If an agent job fails:

```text
Detect Failure
     ↓
Record Error
     ↓
Preserve State
     ↓
Retry if Safe
     ↓
Resume or Fail
```

Do not blindly restart destructive operations.

---

## 83. Idempotency

Repeated staging requests should not create duplicate resources unexpectedly.

Examples:

```text
Repeated Project Creation
Repeated Deployment
Repeated Database Migration
Repeated Git Commit
Repeated ECS Update
```

Each operation should have an appropriate idempotency strategy.

---

## 84. Staging Security Boundaries

Generated code must not automatically gain unrestricted access to:

```text
AWS
GitHub
Jenkins
Production
Databases
Secrets
```

Tools should provide only the permissions required for the current task.

---

## 85. RAG Knowledge Validation

The Staging Agent should retrieve relevant RAG standards before deployment.

Relevant files:

```text
company/coding_standards.md
company/security_standards.md
security/security_standards.md
security/secret_management.md
devops/docker_rules.md
devops/ecr_rules.md
devops/ecs_rules.md
devops/jenkins_rules.md
devops/terraform_rules.md
testing/integration_testing.md
testing/e2e_testing.md
deployment/staging_rules.md
```

---

## 86. Staging Agent Input

Example:

```json
{
  "project_id": "project-123",
  "environment": "staging",
  "image_digest": "sha256:abc123",
  "commit_sha": "a81f92c",
  "build_number": "152",
  "ecs_service": "backend-staging",
  "run_e2e": true,
  "run_security_tests": true,
  "run_performance_tests": true
}
```

---

## 87. Staging Agent Output

Example:

```json
{
  "environment": "staging",
  "deployment": "passed",
  "image_digest": "sha256:abc123",
  "health_check": "passed",
  "integration_tests": "passed",
  "e2e_tests": "passed",
  "security_tests": "passed",
  "performance_tests": "passed",
  "rollback_test": "passed",
  "production_ready": true,
  "status": "passed"
}
```

---

## 88. Staging Agent Workflow

```text
Receive Release Candidate
          ↓
Validate Commit
          ↓
Validate Image Digest
          ↓
Retrieve RAG Standards
          ↓
Validate Security
          ↓
Deploy ECS Staging
          ↓
Wait for Healthy Tasks
          ↓
Run Smoke Tests
          ↓
Run Integration Tests
          ↓
Run E2E Tests
          ↓
Run Security Tests
          ↓
Run Performance Tests
          ↓
Validate Observability
          ↓
Validate Rollback
          ↓
Generate Staging Report
          ↓
Production Ready?
```

---

## 89. Staging Agent Safety Rules

The Staging Agent must not:

* Access production secrets
* Deploy directly to production
* Bypass failed tests
* Ignore critical vulnerabilities
* Disable health checks
* Modify production resources
* Use unrestricted IAM permissions
* Promote an unvalidated image
* Delete production data
* Skip mandatory quality gates

---

## 90. Staging Validation Checklist

### Infrastructure

* [ ] Correct AWS account
* [ ] Correct environment
* [ ] Correct VPC
* [ ] Correct subnets
* [ ] Correct security groups
* [ ] ECS available
* [ ] ALB healthy
* [ ] Database available
* [ ] Redis available where required

### Application

* [ ] Correct image
* [ ] Correct image digest
* [ ] Correct configuration
* [ ] Correct secrets
* [ ] Application starts
* [ ] `/health` passes
* [ ] `/readiness` passes

### Testing

* [ ] Unit tests pass
* [ ] Integration tests pass
* [ ] API tests pass
* [ ] E2E tests pass
* [ ] Regression tests pass
* [ ] Security tests pass
* [ ] Performance tests pass where required

### Agentic AI

* [ ] Agents execute successfully
* [ ] RAG retrieval works
* [ ] MCP tools work
* [ ] Tool permissions are restricted
* [ ] Agent failures are handled
* [ ] Job status works
* [ ] State/checkpoints work

### Deployment

* [ ] ECS deployment succeeds
* [ ] Tasks healthy
* [ ] Target group healthy
* [ ] Smoke tests pass
* [ ] Logs available
* [ ] Metrics available
* [ ] Rollback validated

---

## 91. Staging Implementation Decision Matrix

| Situation            | Recommended Implementation | Avoid                             |
| -------------------- | -------------------------- | --------------------------------- |
| Staging architecture | Production-like            | Completely different stack        |
| Data                 | Synthetic/masked           | Uncontrolled production data      |
| Database             | Dedicated staging DB       | Production DB                     |
| Secrets              | Staging secrets            | Production secrets                |
| Image                | Same validated artifact    | Rebuild before production         |
| Deployment           | Automated                  | Manual-only                       |
| Testing              | Integration + E2E          | Unit tests only                   |
| Security             | Full required scans        | Security only in production       |
| ECS                  | Production-like            | Different runtime                 |
| Networking           | Isolated                   | Open cross-environment access     |
| IAM                  | Least privilege            | Production admin access           |
| Monitoring           | CloudWatch                 | No observability                  |
| Rollback             | Tested                     | Untested                          |
| Production promotion | Gate + approval            | Direct deployment                 |
| Agent execution      | Controlled                 | Unrestricted tools                |
| RAG                  | Standards-aware            | Agent decisions without standards |
| MCP                  | Restricted                 | Full credential exposure          |

---

## 92. Staging Acceptance Criteria

A release is considered staging-ready only when:

1. The correct release candidate is deployed.
2. The image digest is recorded.
3. ECS tasks become healthy.
4. ALB targets are healthy.
5. Application health checks pass.
6. Authentication works.
7. Authorization works.
8. Integration tests pass.
9. E2E tests pass.
10. Regression tests pass.
11. Security tests pass.
12. Required performance tests pass.
13. Agent workflows pass.
14. RAG retrieval passes.
15. MCP integrations pass.
16. External integrations pass.
17. Logs are available.
18. Metrics are available.
19. No critical security issue remains.
20. Rollback has been validated.
21. Test data is isolated.
22. Production resources remain protected.
23. The release candidate is traceable.
24. All mandatory quality gates pass.

---

## 93. Production Promotion Gate

Only after staging passes:

```text
STAGING
   ↓
All Mandatory Tests Passed
   ↓
Security Passed
   ↓
Performance Passed
   ↓
Health Passed
   ↓
Rollback Validated
   ↓
Release Candidate Approved
   ↓
Production Approval
```

---

## 94. Final Staging Rule

Staging is not simply another deployment environment.

It is the **final controlled validation layer between development and production**.

The Agentic SDLC platform must use staging to prove that:

```text
Code
 ↓
Application
 ↓
Infrastructure
 ↓
Security
 ↓
Agents
 ↓
RAG
 ↓
MCP
 ↓
Docker
 ↓
ECR
 ↓
ECS
 ↓
Monitoring
 ↓
Rollback
```

all work correctly together.

**Final Rule:**

> No production deployment is allowed unless the exact release candidate has successfully passed all mandatory staging deployment, functional, integration, E2E, security, performance, health, observability, and rollback gates.
