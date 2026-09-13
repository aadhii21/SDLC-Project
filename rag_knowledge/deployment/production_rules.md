# Production Rules

## 1. Purpose

This document defines production deployment and operational standards for the Agentic SDLC platform.

Production is the final environment where validated applications serve real users and real business workloads.

Every production deployment must be:

* Authorized
* Traceable
* Secure
* Tested
* Observable
* Reversible
* Automated where appropriate
* Protected by quality gates

---

## 2. Production Principle

Production must never be treated as an experimentation environment.

The production environment must contain only:

```text
Validated Code
Validated Infrastructure
Validated Docker Image
Validated Configuration
Approved Secrets
Approved Deployment
```

---

## 3. Production Deployment Flow

The standard flow is:

```text
Developer
    ↓
Git
    ↓
CI
    ↓
Unit Tests
    ↓
Integration Tests
    ↓
Security Tests
    ↓
Docker Build
    ↓
ECR
    ↓
Staging
    ↓
E2E Tests
    ↓
Security Validation
    ↓
Production Approval
    ↓
Production Deployment
    ↓
Health Check
    ↓
Smoke Test
    ↓
Monitoring
```

---

## 4. Production Promotion Principle

Production must receive the same validated artifact that passed staging whenever possible.

Preferred:

```text
Build Once
    ↓
ECR
    ↓
Staging
    ↓
Validation
    ↓
Production
```

Avoid:

```text
Build Staging Image
       ↓
Build Different Production Image
```

---

## 5. Production Release Candidate

Every production release must have a release candidate.

It should identify:

```text
Application
Version
Git Commit
Jenkins Build
Docker Image
ECR Digest
Terraform Version
Database Migration
Release Date
Approver
```

---

## 6. Production Artifact

The production artifact must be immutable.

Preferred:

```text
myapp@sha256:abc123...
```

or:

```text
myapp:build-152
```

Do not rely solely on:

```text
myapp:latest
```

---

## 7. Production Image

Production images must come from the approved ECR repository.

The image must have:

* Successful build
* Successful tests
* Security scan
* No prohibited secrets
* Traceable Git commit
* Immutable identifier
* Approved vulnerability status

---

## 8. Production Approval

Production deployment must require explicit approval unless the organization has intentionally adopted fully automated production deployment.

Recommended flow:

```text
Staging Passed
     ↓
Release Candidate
     ↓
Production Approval
     ↓
Deploy
```

---

## 9. Approval Information

The approver should be able to see:

```text
Build Number
Commit SHA
Image Digest
Test Results
Security Results
Staging Result
Database Changes
Rollback Plan
Expected Impact
```

---

## 10. Production Deployment Authorization

Only authorized users or automation should be able to deploy to production.

Production deployment permissions must be separated from normal development permissions.

---

## 11. Production IAM

Production IAM must follow least privilege.

Avoid:

```text
AdministratorAccess
```

for application workloads.

Grant only required permissions.

---

## 12. Production AWS Authentication

AWS workloads should use:

```text
IAM Roles
```

instead of long-lived static AWS credentials.

For ECS:

```text
ECS Task
   ↓
Task Role
   ↓
AWS Service
```

---

## 13. Production Secrets

Production secrets must be stored in an approved centralized secret manager.

Recommended:

```text
AWS Secrets Manager
```

Secrets must not be stored in:

```text
Git
Docker Image
Dockerfile
Jenkinsfile
Terraform source
Logs
LLM prompts
RAG documents
```

---

## 14. Production Secret Separation

Production secrets must be separate from staging secrets.

Example:

```text
/staging/myapp/database
```

and:

```text
/production/myapp/database
```

must be treated as different credentials.

---

## 15. Production Infrastructure

Production infrastructure should be managed through Infrastructure as Code.

Preferred:

```text
Terraform
```

Terraform should manage:

* VPC
* Subnets
* Security Groups
* ECS
* ECR
* ALB
* IAM
* RDS
* Redis
* CloudWatch
* Auto Scaling

---

## 16. Production Infrastructure Changes

Production infrastructure changes must go through:

```text
Terraform
    ↓
fmt
    ↓
validate
    ↓
security scan
    ↓
plan
    ↓
review
    ↓
approval
    ↓
apply
    ↓
validation
```

---

## 17. Terraform Production Plan

Production Terraform plans must be reviewed before applying.

Pay particular attention to:

```text
Destroy
Replace
IAM changes
Security group changes
Database changes
Networking changes
Public access changes
Encryption changes
```

---

## 18. Destructive Terraform Changes

Unexpected destructive changes must block deployment.

Example:

```text
Terraform Plan
     ↓
Destroy RDS
     ↓
BLOCK
```

unless explicitly authorized.

---

## 19. Production Database

Production database changes require additional validation.

Before migration:

```text
Backup
 ↓
Migration Validation
 ↓
Compatibility Check
 ↓
Approval
 ↓
Migration
 ↓
Validation
```

---

## 20. Backward-Compatible Migrations

Database migrations should preferably be backward compatible.

Preferred:

```text
Release 1
Add New Column
     ↓
Deploy Compatible Code
     ↓
Migrate Data
     ↓
Release 2
Remove Old Column
```

Avoid combining risky destructive schema changes with application deployment.

---

## 21. Production Database Backup

Production database backups must follow organizational recovery requirements.

Before high-risk schema operations, verify that an appropriate recovery point exists.

---

## 22. Production ECS

Production application services should run on ECS using the approved ECR image.

Architecture:

```text
Route 53
   ↓
ALB
   ↓
ECS Service
   ↓
ECS Tasks
   ↓
ECR
```

---

## 23. Production ECS Task Count

Production services should normally run multiple tasks where availability requirements demand it.

Example:

```text
Desired = 3

Task A → AZ-1
Task B → AZ-2
Task C → AZ-3
```

Exact capacity must be based on workload requirements.

---

## 24. Production Networking

Production ECS tasks should normally run in private subnets.

Preferred:

```text
Internet
   ↓
ALB
   ↓
Private ECS
```

Avoid directly exposing ECS tasks to the public internet unless explicitly required.

---

## 25. Production Security Groups

Production security groups must allow only required traffic.

Example:

```text
Internet
   ↓
ALB SG
   ↓
ECS SG
   ↓
RDS SG
```

Avoid unrestricted inbound rules.

---

## 26. Production HTTPS

External production APIs must use HTTPS.

Example:

```text
https://api.example.com
```

TLS certificates should be managed using an approved certificate-management solution.

---

## 27. Production Health Checks

Production services must have health checks.

At minimum where applicable:

```text
GET /health
```

and preferably:

```text
GET /readiness
```

Health checks must be reliable and fast.

---

## 28. Production ALB Health

The ALB target group must report healthy targets before deployment is considered successful.

Example:

```text
ECS Task
   ↓
/health
   ↓
Target Group
   ↓
Healthy
```

---

## 29. Production Deployment Strategies

Choose a deployment strategy based on application risk.

Supported strategies may include:

```text
Rolling
Blue/Green
Canary
Linear
```

AWS currently supports these ECS deployment approaches depending on service configuration.

---

## 30. Rolling Deployment

Rolling deployment gradually replaces old tasks with new tasks.

Example:

```text
Old:
Task 1
Task 2
Task 3

      ↓

New:
Task 1
Task 2
Task 3
```

Minimum and maximum healthy capacity must be configured appropriately.

---

## 31. Rolling Deployment Safety

Rolling deployments must ensure that sufficient healthy capacity remains available.

Do not configure deployment parameters that unnecessarily take the entire application offline.

---

## 32. Deployment Circuit Breaker

Production ECS services using rolling deployment should use the ECS deployment circuit breaker where appropriate.

Conceptually:

```text
Deployment
    ↓
Tasks Fail
    ↓
Circuit Breaker
    ↓
Deployment Failed
    ↓
Rollback
```

ECS can automatically roll back to the last completed deployment when rollback is enabled.

---

## 33. CloudWatch Deployment Alarms

Production deployments should use CloudWatch alarms for important application-level failure signals where appropriate.

Examples:

```text
5xx Errors
Latency
Unhealthy Targets
CPU
Memory
Application Errors
```

ECS supports deployment failure detection using both the deployment circuit breaker and CloudWatch alarms.

---

## 34. Automatic Rollback

Where appropriate, failed deployments should automatically roll back.

Example:

```text
New Deployment
      ↓
Health Failure
      ↓
CloudWatch / Circuit Breaker
      ↓
Rollback
      ↓
Last Known Good Version
```

---

## 35. Rollback Target

Rollback should use the last known-good deployment.

The rollback target must be:

* Previously validated
* Traceable
* Available
* Immutable

---

## 36. Manual Rollback

A manual rollback procedure must also exist.

Example:

```text
Detect Incident
     ↓
Stop Promotion
     ↓
Select Previous Version
     ↓
Deploy Previous Version
     ↓
Health Check
     ↓
Smoke Test
     ↓
Monitor
```

---

## 37. Rollback Testing

Rollback must be tested periodically.

Do not assume rollback works simply because a previous image exists.

Test:

```text
Application Rollback
ECS Rollback
Database Compatibility
Traffic Recovery
Health Validation
```

---

## 38. Blue/Green Deployment

Blue/green deployments maintain:

```text
Blue → Current
Green → New
```

Example:

```text
ALB
 ↓
Blue → Current Production
Green → New Release
```

The new environment can be validated before full traffic is shifted.

AWS recommends sufficient capacity, accurate health checks, bake time, alarms, and tested rollback for ECS blue/green deployments.

---

## 39. Canary Deployment

High-risk services may use canary deployments.

Example:

```text
Old = 90%
New = 10%
```

Monitor:

```text
Errors
Latency
CPU
Memory
Business Metrics
```

Then gradually increase traffic.

---

## 40. Canary Failure

If canary metrics breach the defined threshold:

```text
Canary
 ↓
Failure
 ↓
Stop Traffic Shift
 ↓
Rollback
```

Do not automatically shift 100% traffic after a failed canary.

---

## 41. Linear Deployment

Linear deployments gradually increase traffic to the new revision.

Example:

```text
10%
 ↓
25%
 ↓
50%
 ↓
75%
 ↓
100%
```

At every stage:

```text
Monitor
Validate
Continue or Rollback
```

---

## 42. Bake Time

For blue/green, canary, or linear deployments, use an appropriate observation period before completing the rollout.

The bake period should be long enough to detect:

* Startup problems
* Memory leaks
* Error spikes
* Latency degradation
* Dependency failures
* Business logic failures

---

## 43. Deployment Monitoring

Monitor during and immediately after deployment:

```text
ECS
ALB
CloudWatch
Application Logs
Database
Redis
External APIs
Agent Jobs
```

---

## 44. Production Metrics

Important metrics include:

```text
Request Count
Latency
p50
p95
p99
4xx
5xx
CPU
Memory
Task Count
Target Health
Database Connections
Queue Depth
Agent Job Failures
LLM Errors
```

---

## 45. Error Budget

Production services should define acceptable reliability targets where applicable.

Example:

```text
Availability
Error Rate
Latency
Recovery Time
```

The exact thresholds depend on business requirements.

---

## 46. Production Logging

Production logs must be:

* Structured
* Centralized
* Searchable
* Retained according to policy
* Free from secrets

Example:

```json
{
  "level": "ERROR",
  "service": "backend",
  "request_id": "abc123",
  "message": "Database request failed"
}
```

---

## 47. Request Correlation

Every production request should have a correlation/request ID where applicable.

Example:

```text
Client
 ↓
Request ID
 ↓
ALB
 ↓
FastAPI
 ↓
Agent
 ↓
Database
```

This makes incident investigation easier.

---

## 48. Agent Job Monitoring

Long-running Agentic SDLC jobs must expose status.

Example:

```text
queued
 ↓
running
 ↓
completed
```

or:

```text
queued
 ↓
running
 ↓
failed
```

The job ID must be traceable through logs and workflow state.

---

## 49. Production Agent Execution

Production agents must run with controlled permissions.

An agent must not automatically receive unrestricted:

```text
AWS
GitHub
Jenkins
Database
Secrets
Production Infrastructure
```

access.

---

## 50. Production RAG

Production agents must use approved RAG knowledge.

Relevant standards should be retrieved before high-risk operations.

Examples:

```text
Security Rules
Deployment Rules
ECS Rules
ECR Rules
Terraform Rules
Secret Management Rules
```

---

## 51. Production MCP

MCP tools must use least privilege.

The LLM should not receive raw credentials.

Preferred:

```text
Agent
 ↓
MCP Tool
 ↓
Secure Credential Retrieval
 ↓
External Service
```

---

## 52. Production Tool Authorization

Before a tool executes a high-risk operation, validate:

```text
User
Project
Environment
Permission
Requested Action
Resource
Risk Level
Approval
```

---

## 53. High-Risk Operations

The following should require additional authorization where appropriate:

```text
Production Deploy
Database Migration
Terraform Apply
Terraform Destroy
IAM Changes
Security Group Changes
Secret Rotation
Production Data Changes
Production Resource Deletion
```

---

## 54. Production Guardrails

Production actions must be protected by guardrails.

Example:

```text
Agent Request
     ↓
Input Guardrail
     ↓
Authorization
     ↓
Security Guardrail
     ↓
Approval
     ↓
Tool
     ↓
Output Validation
```

---

## 55. Production Input Validation

Validate:

* Project ID
* Environment
* Image
* Version
* Resource
* Operation
* Parameters

Never trust agent-generated input blindly.

---

## 56. Production Output Validation

Tool results should be validated before being passed to the next agent.

Example:

```text
ECS Deployment Result
      ↓
Validate
      ↓
Expected Service?
Expected Task Count?
Healthy?
      ↓
Continue
```

---

## 57. Production Database Access

Agents should not receive unrestricted production database access.

Prefer:

```text
Read-only diagnostics
```

for monitoring agents.

Write access should require explicit authorization.

---

## 58. Production Data Protection

Production data must not be unnecessarily copied into:

```text
Logs
Prompts
RAG
Vector DB
Agent Memory
Chat History
```

Sensitive data must be protected.

---

## 59. Production RAG Security

Before ingesting production information into RAG:

```text
Data Classification
      ↓
Secret Detection
      ↓
PII/Sensitive Data Check
      ↓
Access Control
      ↓
Ingestion
```

Do not automatically ingest sensitive production data.

---

## 60. Production API Security

Production APIs must use appropriate:

* Authentication
* Authorization
* Rate limiting
* Input validation
* Output validation
* CORS configuration
* Security headers
* Request IDs
* Error handling

---

## 61. Rate Limiting

Public APIs should have appropriate rate limiting.

Rate limits should protect against:

* Abuse
* Accidental overload
* Automated attacks
* Cost explosions

---

## 62. Production Cost Controls

Monitor:

```text
ECS
NAT Gateway
RDS
Redis
ECR
CloudWatch
LLM Usage
Vector DB
Data Transfer
```

Unexpected cost spikes should trigger investigation.

---

## 63. ECS Auto Scaling

Production ECS services should use Auto Scaling where workload variability requires it.

Example:

```text
Normal Load
    ↓
2 Tasks

High Load
    ↓
5 Tasks

Peak Load
    ↓
10 Tasks
```

Maximum capacity must be explicitly configured.

---

## 64. Auto Scaling Safety

Auto Scaling must not create uncontrolled cost.

Define:

```text
Minimum
Desired
Maximum
```

Example:

```text
Min = 2
Desired = 3
Max = 10
```

---

## 65. Scaling Metrics

Choose scaling metrics based on workload.

Possible metrics:

```text
CPU
Memory
ALB Requests
Queue Depth
Custom Application Metric
```

For agent workers, queue depth may be more meaningful than CPU.

---

## 66. Production Health

Production health must include more than "container is running."

Validate:

```text
Container
   ↓
Application
   ↓
Database
   ↓
External Dependencies
   ↓
Business-Critical APIs
```

---

## 67. Smoke Tests

After deployment:

```bash
curl --fail https://api.example.com/health
```

Then execute critical API smoke tests.

---

## 68. Post-Deployment Validation

Validate:

```text
ECS Tasks
Target Health
Application Health
Error Rate
Latency
Logs
Database
Critical API
Agent Jobs
```

---

## 69. Deployment Success

A deployment is successful only when:

```text
New Version Running
AND
Tasks Healthy
AND
Targets Healthy
AND
Health Check Passed
AND
Smoke Test Passed
AND
No Critical Alarm
```

---

## 70. Deployment Failure

If deployment fails:

```text
Stop Promotion
     ↓
Capture Logs
     ↓
Identify Failure
     ↓
Rollback if Required
     ↓
Validate Previous Version
     ↓
Open Incident
```

---

## 71. Incident Detection

Production incidents may be detected through:

* CloudWatch
* ALB
* Application logs
* Monitoring systems
* User reports
* Agent monitoring
* Synthetic tests

---

## 72. Incident Severity

Suggested classification:

| Severity | Description                               |
| -------- | ----------------------------------------- |
| SEV-1    | Major production outage/security incident |
| SEV-2    | Major functionality degraded              |
| SEV-3    | Limited functionality affected            |
| SEV-4    | Minor/non-critical issue                  |

Exact organizational definitions must take precedence.

---

## 73. SEV-1 Response

For a major incident:

```text
Detect
 ↓
Alert
 ↓
Assess
 ↓
Stop Deployment
 ↓
Rollback if Appropriate
 ↓
Restore Service
 ↓
Investigate
 ↓
Communicate
 ↓
Root Cause Analysis
```

---

## 74. Security Incident

If credentials or sensitive information are compromised:

```text
Revoke
 ↓
Rotate
 ↓
Contain
 ↓
Investigate
 ↓
Patch
 ↓
Redeploy
 ↓
Validate
```

Do not simply delete the exposed credential.

---

## 75. Production Rollback

Rollback should be preferred over risky live debugging when the release is clearly responsible for an outage.

Example:

```text
v2
 ↓
Incident
 ↓
Rollback
 ↓
v1
 ↓
Healthy
```

---

## 76. Rollback Validation

After rollback:

```text
ECS Healthy
ALB Healthy
Health Endpoint
Critical API
Database
Error Rate
Latency
```

must be checked.

---

## 77. Database Rollback Considerations

Application rollback does not automatically mean database rollback.

Example:

```text
Application v2
Database v2
```

may not safely support:

```text
Application v1
Database v2
```

Therefore database migration compatibility must be considered before rollback.

---

## 78. Production Deployment Audit

Record:

```text
Who
What
When
Why
Which Commit
Which Build
Which Image
Which Digest
Which Task Definition
Which Environment
Which Approval
```

---

## 79. CloudTrail

Production AWS actions should be auditable using AWS logging facilities such as CloudTrail where applicable.

Audit important actions including:

```text
IAM Changes
ECS Changes
ECR Changes
Security Group Changes
Terraform Actions
Secret Changes
Production Resource Changes
```

---

## 80. Production Change Management

Every production change should have:

```text
Change Description
Risk
Impact
Testing Evidence
Rollback Plan
Approver
Execution Time
Result
```

---

## 81. Emergency Changes

Emergency changes may follow an expedited process.

They must still be:

* Authorized
* Logged
* Audited
* Tested as much as practical
* Followed by review

---

## 82. Production Maintenance

Maintenance should be planned to minimize user impact.

Consider:

```text
Traffic
Deployment Window
Database Connections
Long-Running Jobs
Background Workers
External Integrations
```

---

## 83. Background Jobs During Deployment

Long-running Agentic SDLC jobs must be considered during deployments.

Do not terminate important jobs unexpectedly.

Use:

* Graceful shutdown
* Job persistence
* Checkpoints
* Queue-based execution
* Retry mechanisms

---

## 84. Production Concurrency

Only one production deployment should normally be active for a service unless the deployment strategy explicitly supports concurrent release behavior.

Jenkins should prevent conflicting production deployments.

---

## 85. Production Locking

Deployment pipelines should use appropriate concurrency controls.

Example:

```text
Production Deployment
       ↓
Lock
       ↓
Deploy
       ↓
Validate
       ↓
Unlock
```

---

## 86. Production Configuration

Configuration must be environment-specific and version-controlled where appropriate.

Sensitive values must remain outside source control.

---

## 87. Configuration Drift

Unexpected production configuration changes must be detected.

Use:

```text
Terraform Plan
AWS Config where appropriate
CloudTrail
CloudWatch
```

---

## 88. Production Backup and Recovery

Production systems must have a documented recovery strategy.

Consider:

```text
Database Backup
ECR Image Retention
Terraform State
Secrets Recovery
Infrastructure Recreation
Multi-AZ
Multi-Region where required
```

---

## 89. Recovery Time Objective

Production architecture should define:

```text
RTO
```

The Recovery Time Objective describes how quickly the service should be restored.

---

## 90. Recovery Point Objective

Production architecture should define:

```text
RPO
```

The Recovery Point Objective describes the acceptable amount of data loss.

---

## 91. Disaster Recovery

Critical services should have a disaster recovery strategy.

Possible components:

```text
Multi-AZ
ECR Replication
Database Backups
Infrastructure as Code
Secrets Recovery
Secondary Region
```

Use only the level of redundancy required by business requirements.

---

## 92. Production Capacity Testing

Capacity should be periodically validated.

Test:

```text
Normal Load
Peak Load
Failure Load
Scaling
Recovery
```

---

## 93. Production Observability

Production monitoring should provide:

```text
Metrics
Logs
Traces where appropriate
Alerts
Dashboards
Deployment Events
Agent Job Status
```

---

## 94. Production Dashboard

A production dashboard should expose critical signals.

Recommended:

```text
Request Rate
Error Rate
Latency
CPU
Memory
Task Count
Target Health
Database Health
Queue Depth
Agent Failures
LLM Failures
```

---

## 95. Alerting

Alerts should be actionable.

Avoid excessive alerts that do not require human or automated action.

Every critical alert should have:

```text
Condition
Severity
Owner
Action
Runbook
```

---

## 96. Production Runbooks

Important incidents should have documented runbooks.

Examples:

```text
ECS Deployment Failure
Database Failure
High 5xx
High Latency
ECR Image Failure
Secret Compromise
LLM Outage
MCP Failure
Agent Workflow Failure
```

---

## 97. Agentic SDLC Production Flow

The complete production flow is:

```text
Requirements
      ↓
Research
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
Jenkins
      ↓
ECR
      ↓
Staging
      ↓
E2E
      ↓
Production Approval
      ↓
ECS
      ↓
Health
      ↓
Monitoring
      ↓
Production
```

---

## 98. Production Agent Input

Example:

```json
{
  "project_id": "project-123",
  "environment": "production",
  "release_version": "1.4.2",
  "commit_sha": "a81f92c",
  "build_number": "152",
  "image_digest": "sha256:abc123...",
  "staging_status": "passed",
  "security_status": "passed",
  "approval_status": "approved",
  "deployment_strategy": "rolling"
}
```

---

## 99. Production Agent Output

Example:

```json
{
  "project_id": "project-123",
  "environment": "production",
  "release_version": "1.4.2",
  "image_digest": "sha256:abc123...",
  "deployment_status": "completed",
  "tasks_healthy": true,
  "target_health": "healthy",
  "smoke_test": "passed",
  "monitoring": "healthy",
  "rollback_available": true,
  "status": "passed"
}
```

---

## 100. Production Agent Workflow

The Production Agent should follow:

```text
Receive Release Candidate
          ↓
Validate Production Authorization
          ↓
Validate Staging Result
          ↓
Validate Image Digest
          ↓
Retrieve Production Standards
          ↓
Validate Security Gates
          ↓
Validate Terraform Changes
          ↓
Validate Database Changes
          ↓
Validate Rollback
          ↓
Obtain Required Approval
          ↓
Deploy
          ↓
Monitor
          ↓
Health Check
          ↓
Smoke Test
          ↓
Validate Metrics
          ↓
Production Complete
```

---

## 101. Production Agent Safety Rules

The Production Agent must never:

* Bypass production approval
* Deploy an untested image
* Deploy an image with blocked vulnerabilities
* Expose secrets to the LLM
* Grant unrestricted IAM permissions
* Disable security groups
* Disable health checks
* Ignore failed smoke tests
* Ignore critical CloudWatch alarms
* Destroy production resources without authorization
* Deploy directly from an unvalidated development branch
* Use `latest` as the only release identifier

---

## 102. Production Quality Gate

Production deployment must be blocked when:

```text
Staging Failed
        OR
Approval Missing
        OR
Image Invalid
        OR
Image Digest Missing
        OR
Security Gate Failed
        OR
Critical Vulnerability Exists
        OR
Secret Detected
        OR
Terraform Plan Has Unexpected Destruction
        OR
Database Migration Not Approved
        OR
ECS Deployment Failed
        OR
Health Check Failed
        OR
Smoke Test Failed
        OR
Critical Alarm Triggered
```

---

## 103. Production Validation Checklist

### Release

* [ ] Release candidate created
* [ ] Git commit recorded
* [ ] Build number recorded
* [ ] Image digest recorded
* [ ] Staging passed
* [ ] Security passed
* [ ] Approval obtained

### Infrastructure

* [ ] Terraform validated
* [ ] Terraform plan reviewed
* [ ] No unexpected destructive changes
* [ ] IAM reviewed
* [ ] Security groups reviewed
* [ ] Networking validated

### ECS

* [ ] Task definition valid
* [ ] Correct image deployed
* [ ] Desired task count maintained
* [ ] Tasks healthy
* [ ] Target group healthy
* [ ] Deployment completed

### Security

* [ ] Secrets secure
* [ ] Vulnerability scan passed
* [ ] No secrets in image
* [ ] IAM least privilege
* [ ] Network access restricted

### Application

* [ ] `/health` passes
* [ ] `/readiness` passes
* [ ] Critical API passes
* [ ] Authentication passes
* [ ] Authorization passes
* [ ] Smoke tests pass

### Monitoring

* [ ] CloudWatch metrics available
* [ ] Logs available
* [ ] Alarms configured
* [ ] Error rate normal
* [ ] Latency normal

### Recovery

* [ ] Previous image available
* [ ] Rollback tested
* [ ] Database recovery considered
* [ ] Incident runbook available

---

## 104. Production Implementation Decision Matrix

| Situation             | Recommended Implementation                      | Avoid                             |
| --------------------- | ----------------------------------------------- | --------------------------------- |
| Production deployment | Controlled CI/CD                                | Manual laptop deployment          |
| Artifact              | Immutable image/digest                          | `latest`                          |
| Promotion             | Staging → Production                            | Dev → Production                  |
| Approval              | Required for controlled releases                | Unrestricted deployment           |
| AWS authentication    | IAM role                                        | Static keys                       |
| Secrets               | Secrets Manager                                 | Git/.env                          |
| Infrastructure        | Terraform                                       | Manual infrastructure             |
| ECS                   | Multi-task service                              | Single task where HA required     |
| Networking            | Private ECS + ALB                               | Public task exposure              |
| Deployment            | Rolling/Blue-Green/Canary/Linear as appropriate | Uncontrolled replacement          |
| Failure detection     | Circuit breaker + alarms                        | No rollback protection            |
| Rollback              | Last known-good artifact                        | Rebuild during incident           |
| Database              | Backward-compatible migration                   | Unvalidated destructive migration |
| Monitoring            | CloudWatch + application metrics                | Logs only                         |
| Agent access          | Least privilege                                 | Full AWS access                   |
| Production RAG        | Approved standards                              | Uncontrolled production data      |
| MCP                   | Restricted tools                                | Raw credentials                   |
| Scaling               | Explicit min/desired/max                        | Unlimited scaling                 |
| Audit                 | CloudTrail/logging                              | No audit trail                    |

---

## 105. Production Acceptance Criteria

A production release is accepted only when:

1. Release candidate is identified.
2. Staging validation passed.
3. Security validation passed.
4. Required approval exists.
5. Image digest is recorded.
6. Image is immutable.
7. ECS deployment succeeds.
8. Tasks become healthy.
9. Target group becomes healthy.
10. Application health passes.
11. Smoke tests pass.
12. Authentication works.
13. Authorization works.
14. Critical APIs work.
15. No mandatory CloudWatch alarm is active.
16. Logs are available.
17. Metrics are available.
18. Rollback is available.
19. Production resources remain protected.
20. Deployment is fully traceable.

---

## 106. Production Incident Acceptance

After a production incident:

```text
Service Restored
     ↓
Root Cause Identified
     ↓
Impact Recorded
     ↓
Logs Preserved
     ↓
Security Checked
     ↓
Rollback/Recovery Validated
     ↓
Corrective Action Created
     ↓
Post-Incident Review
```

---

## 107. Post-Deployment Review

For significant releases, review:

```text
Deployment Duration
Deployment Errors
Rollback Events
CPU
Memory
Latency
5xx
Task Restarts
Database Performance
Agent Failures
LLM Failures
User Impact
```

---

## 108. Continuous Improvement

Production incidents and deployment failures must feed improvements back into:

```text
Coding Standards
Testing Standards
Security Standards
Docker Rules
ECR Rules
ECS Rules
Jenkins Rules
Terraform Rules
Staging Rules
Production Rules
Agent Guardrails
RAG Knowledge
```

---

## 109. Production Knowledge Feedback Loop

The Agentic SDLC platform should continuously improve using production lessons.

```text
Production Incident
       ↓
Root Cause
       ↓
Corrective Action
       ↓
Standard Update
       ↓
RAG Knowledge Base
       ↓
Future Agents
       ↓
Improved Deployment
```

---

## 110. Final Production Rule

Production is the final controlled environment of the Agentic SDLC platform.

The platform must never treat production deployment as merely:

```text
docker push
+
ecs update
```

Instead, production must follow:

```text
Validated Code
      ↓
Validated Tests
      ↓
Validated Security
      ↓
Validated Docker Image
      ↓
Validated ECR Artifact
      ↓
Validated Staging
      ↓
Production Approval
      ↓
Controlled ECS Deployment
      ↓
Health Validation
      ↓
Smoke Testing
      ↓
Monitoring
      ↓
Rollback Protection
      ↓
Production
```

**Final Rule:**

> No application may be promoted to production unless the exact release candidate has passed all mandatory development, testing, security, staging, artifact, authorization, deployment, health, monitoring, and rollback gates. Every production deployment must be traceable, least-privileged, observable, and reversible.
