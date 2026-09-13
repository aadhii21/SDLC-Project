# Rollback Rules

## 1. Purpose

This document defines standards for safely reversing failed, unhealthy, or unsafe application and infrastructure changes.

Rollback must restore the system to a known-good state while minimizing:

* Downtime
* Data loss
* User impact
* Security exposure
* Infrastructure instability
* Deployment risk

---

## 2. Rollback Principle

Rollback must always prefer a **known-good immutable state** over rebuilding an uncertain state during an incident.

Preferred:

```text
Current Release
     ↓
Failure
     ↓
Previous Known-Good Release
     ↓
Validation
```

---

## 3. Rollback Scope

Rollback may apply to:

```text
Application Code
Docker Image
ECS Deployment
Configuration
Infrastructure
Database
Agent Workflow
RAG Knowledge
MCP Configuration
```

Each rollback type must be evaluated independently.

---

## 4. Rollback Is Not Always Reversal

A rollback does not necessarily mean reversing every change.

Example:

```text
Application
v2 → v1

Database
v2 → remains v2
```

if the database migration is backward compatible.

---

## 5. Known-Good Version

Every production deployment must have a known-good previous version.

It should contain:

```text
Git Commit
Jenkins Build
Docker Image
ECR Digest
ECS Task Definition
Configuration Version
Deployment Timestamp
```

---

## 6. Immutable Rollback Artifact

Rollback should use an immutable image.

Preferred:

```text
myapp@sha256:abc123...
```

or:

```text
myapp:build-145
```

Avoid rebuilding the previous release during an incident.

---

## 7. Rollback Trigger

Rollback may be triggered by:

* Failed health checks
* Failed smoke tests
* High 5xx rate
* Severe latency increase
* ECS task failures
* ALB target failures
* Database compatibility problems
* Critical security vulnerability
* Application crash loops
* Incorrect configuration
* Business-critical functionality failure
* Deployment alarm
* Manual incident decision

---

## 8. Automatic Rollback

Automatic rollback should be used where the failure condition can be reliably detected.

Example:

```text
Deployment
    ↓
Health Failure
    ↓
ECS Circuit Breaker / Alarm
    ↓
Rollback
    ↓
Previous Deployment
```

---

## 9. Manual Rollback

Manual rollback must be available even when automatic rollback is configured.

Example:

```text
Incident
   ↓
Assess
   ↓
Authorize Rollback
   ↓
Deploy Known-Good Version
   ↓
Validate
   ↓
Monitor
```

---

## 10. Rollback Decision

The system should consider:

```text
Severity
User Impact
Failure Rate
Duration
Security Risk
Data Risk
Recovery Time
Rollback Safety
```

---

## 11. Immediate Rollback Conditions

Rollback should be strongly considered immediately for:

```text
Critical outage
Critical security issue
Repeated task crashes
Severe API failure
Broken authentication
Broken authorization
Corrupted application behavior
Deployment causing major user impact
```

---

## 12. Do Not Rollback Blindly

Before rollback, determine whether rollback itself could cause:

```text
Data Loss
Schema Incompatibility
Security Regression
Duplicate Processing
Queue Problems
State Corruption
```

---

## 13. Rollback Flow

Standard rollback flow:

```text
Failure Detected
      ↓
Stop Deployment
      ↓
Identify Current Release
      ↓
Identify Known-Good Release
      ↓
Check Rollback Compatibility
      ↓
Rollback
      ↓
Health Check
      ↓
Smoke Test
      ↓
Monitor
      ↓
Close or Escalate Incident
```

---

## 14. Jenkins Rollback

Jenkins should support controlled rollback to a previous validated build.

Example:

```text
Build 152 → Failed
       ↓
Build 151 → Known Good
       ↓
Deploy Build 151
```

---

## 15. Jenkins Rollback Parameters

A rollback pipeline may accept:

```text
Environment
Application
Build Number
Image Digest
Reason
Approver
```

Example:

```text
ROLLBACK_BUILD=151
ENVIRONMENT=production
```

---

## 16. Jenkins Rollback Safety

The Jenkins rollback pipeline must not allow arbitrary production artifacts.

Validate:

```text
Build Exists
Image Exists
Image Approved
Environment Valid
User Authorized
Artifact Traceable
```

---

## 17. ECR Rollback

ECR must retain previous production images according to the organization's retention policy.

Rollback should reference the exact image digest.

Example:

```text
Current:
myapp@sha256:new

Rollback:
myapp@sha256:old
```

---

## 18. ECR Image Retention

Lifecycle policies must not delete images that are still required for operational rollback.

At minimum, retain an appropriate number of previous production releases.

The exact retention period must be based on:

* Release frequency
* Compliance requirements
* Recovery requirements
* Storage cost

---

## 19. ECS Rollback

ECS rollback should deploy the previous known-good task definition/image.

Example:

```text
Task Definition 25
       ↓
Failure
       ↓
Task Definition 24
       ↓
Healthy
```

---

## 20. ECS Deployment Circuit Breaker

For appropriate rolling deployments, configure the ECS deployment circuit breaker.

Conceptually:

```text
New Tasks
   ↓
Repeated Failure
   ↓
Circuit Breaker
   ↓
Deployment Failed
   ↓
Rollback
```

---

## 21. ECS CloudWatch Rollback

CloudWatch alarms can be used to detect deployment failures.

Example:

```text
5xx > Threshold
      ↓
Alarm
      ↓
Deployment Failure
      ↓
Rollback
```

---

## 22. Blue/Green Rollback

For blue/green:

```text
Blue = Current
Green = New
```

If Green fails:

```text
Traffic
  ↓
Blue
```

should remain or be restored.

---

## 23. Canary Rollback

For canary:

```text
90% Old
10% New
```

If New fails:

```text
10% New
   ↓
0% New
   ↓
100% Old
```

Stop further traffic shifting.

---

## 24. Linear Rollback

For linear deployment:

```text
10%
 ↓
25%
 ↓
50%
```

If failure occurs at 50%:

```text
Stop
 ↓
Restore previous version
```

Do not continue traffic promotion.

---

## 25. Rollback During Bake Time

If metrics degrade during the bake period:

```text
New Version
     ↓
Bake Time
     ↓
Alarm
     ↓
Rollback
```

Do not wait for the full rollout if critical failure is already confirmed.

---

## 26. Rollback Health Checks

After rollback verify:

```text
ECS Tasks
Target Health
/health
/readiness
Critical APIs
```

---

## 27. Rollback Smoke Tests

At minimum:

```bash
curl --fail https://api.example.com/health
```

Then execute critical business API smoke tests.

---

## 28. Rollback Monitoring

After rollback, monitor:

```text
5xx
Latency
CPU
Memory
Task Restarts
ALB Health
Database Connections
Queue Depth
Agent Failures
```

---

## 29. Rollback Observation Period

Do not immediately declare rollback successful after the first health check.

Observe the service for an appropriate period.

Validate:

```text
Immediate Health
+
Short-Term Stability
```

---

## 30. Rollback Success

Rollback is successful only when:

```text
Previous Version Running
AND
Tasks Healthy
AND
Targets Healthy
AND
Health Check Passed
AND
Smoke Tests Passed
AND
Critical Errors Normal
AND
No Critical Alarm
```

---

## 31. Rollback Failure

If rollback fails:

```text
Rollback
   ↓
Still Unhealthy
   ↓
Incident Escalation
   ↓
Emergency Recovery
```

Do not repeatedly deploy versions without diagnosis.

---

## 32. Multiple Rollback Versions

If the immediate previous release is known to be broken:

```text
v5 Current
v4 Broken
v3 Known Good
```

rollback to:

```text
v3
```

not automatically to v4.

---

## 33. Rollback Metadata

Every rollback must record:

```text
Current Version
Rollback Version
Image Digest
Reason
Trigger
Approver
Start Time
End Time
Result
```

---

## 34. Rollback Audit Trail

Maintain an audit trail showing:

```text
Who initiated rollback
What was rolled back
Why it was rolled back
Which artifact was used
Which environment was affected
What validation occurred
```

---

## 35. Database Rollback

Database rollback requires special handling.

Application rollback and database rollback must not be treated as the same operation.

---

## 36. Preferred Database Strategy

Prefer forward-compatible migrations.

Example:

```text
Release 1
     ↓
Add Column
     ↓
Release 2
     ↓
Use Column
```

This makes application rollback safer.

---

## 37. Database Rollback Risk

Avoid automatically reversing database migrations in production.

A migration may have:

```text
Deleted Data
Transformed Data
Changed Constraints
Changed Types
```

and may not be safely reversible.

---

## 38. Expand-and-Contract Pattern

Preferred database migration pattern:

```text
Expand
 ↓
Deploy Compatible Code
 ↓
Migrate Data
 ↓
Switch Application
 ↓
Contract
```

---

## 39. Application Rollback With New Database Schema

Before application rollback verify:

```text
Old Application
      ↓
New Database Schema
      ↓
Compatible?
```

If yes:

```text
Rollback Application
```

If no:

```text
Block Blind Rollback
```

---

## 40. Database Recovery

For severe database problems, recovery may require:

```text
Backup
Point-in-Time Recovery
Replica
Restore
Data Repair
```

Database recovery must follow the organization's approved recovery procedure.

---

## 41. Terraform Rollback

Terraform rollback must not be treated as simply:

```text
terraform apply previous code
```

Terraform changes infrastructure state and may involve dependencies.

---

## 42. Terraform Rollback Principle

Prefer a controlled configuration change that restores the desired known-good infrastructure state.

Example:

```text
Known Good Terraform
        ↓
Review
        ↓
Plan
        ↓
Approval
        ↓
Apply
        ↓
Validate
```

---

## 43. Terraform State Protection

Never delete or replace Terraform state during a normal rollback.

The remote state must remain protected.

---

## 44. Terraform State Backup

Production Terraform state must have appropriate:

* Encryption
* Access control
* Versioning/recovery
* Locking
* Backup/recovery procedures

---

## 45. Terraform Rollback Plan

Before infrastructure changes, understand:

```text
Current State
Desired State
Expected Changes
Dependencies
Potential Destruction
Recovery Path
```

---

## 46. Terraform Destructive Rollback

Operations involving:

```text
terraform destroy
terraform state rm
terraform state mv
```

must be treated as high-risk operations.

They require explicit authorization.

---

## 47. Infrastructure Rollback Validation

After Terraform recovery validate:

```text
VPC
Security Groups
ECS
ALB
RDS
ECR
IAM
CloudWatch
```

as applicable.

---

## 48. Configuration Rollback

Configuration changes can cause production failures even when the application image is unchanged.

Examples:

```text
Environment Variables
Feature Flags
Timeouts
URLs
API Endpoints
Scaling Parameters
```

Configuration rollback must be versioned and traceable.

---

## 49. Secret Rollback

Do not blindly restore old secrets.

If a secret was rotated:

```text
New Secret
   ↓
Application Failure
```

first determine whether:

```text
Application
```

or:

```text
Credential
```

is responsible.

---

## 50. Compromised Credential

If a credential is compromised:

```text
Revoke
 ↓
Rotate
 ↓
Update Application
 ↓
Validate
```

Do not rollback to a compromised credential.

---

## 51. Agent Workflow Rollback

Agentic workflows may require rollback of workflow state.

Example:

```text
Job
 ↓
Requirements
 ↓
Design
 ↓
Backend
 ↓
Deployment
 ↓
Failure
```

The system should preserve the job state and failure point.

---

## 52. Agent Job Recovery

A failed agent job should support:

```text
Retry
Resume
Rollback
Restart From Checkpoint
```

depending on workflow design.

---

## 53. Agent Checkpoint

Long-running workflows should persist checkpoints.

Example:

```text
Requirements ✓
Design ✓
Frontend ✓
Backend ✓
Testing ✓
Security ✓
Deployment ✗
```

The system should not unnecessarily repeat completed stages.

---

## 54. Agent Deployment Rollback

If the Deployment Agent fails:

```text
Deployment Agent
       ↓
Failure
       ↓
Rollback Agent / Recovery Workflow
       ↓
Known-Good Release
```

---

## 55. Agent Rollback Authorization

Agents must not autonomously perform unrestricted production rollback unless explicitly designed and authorized to do so.

Use:

```text
Risk Assessment
+
Policy
+
Authorization
```

---

## 56. RAG-Based Rollback Decision

The Production/Rollback Agent may retrieve:

```text
Production Rules
Rollback Rules
ECS Rules
ECR Rules
Terraform Rules
Security Rules
Database Rules
Incident Runbooks
```

before making a rollback recommendation.

---

## 57. RAG Must Not Override Safety

Retrieved RAG content must not override:

```text
Authorization
Security Policy
Current Infrastructure State
Explicit Production Controls
```

RAG provides knowledge, not unrestricted authority.

---

## 58. MCP Rollback Tools

MCP tools used for rollback must expose restricted operations.

Example:

```text
get_current_deployment
get_previous_deployment
get_ecs_health
get_alarm_status
rollback_ecs
validate_deployment
```

Avoid exposing unrestricted:

```text
aws_execute_any_command
```

to an agent.

---

## 59. Rollback Tool Validation

Before execution validate:

```text
Environment = production
Target Service = expected service
Rollback Version = known-good
Image Digest = valid
Authorization = valid
```

---

## 60. Rollback Idempotency

Rollback operations should be idempotent where possible.

If the service is already running the desired version:

```text
Rollback Request
      ↓
Already On Target
      ↓
No Duplicate Action
```

---

## 61. Rollback Retry

Retries must be bounded.

Example:

```text
Attempt 1
 ↓
Failure
 ↓
Attempt 2
 ↓
Failure
 ↓
Escalate
```

Do not retry indefinitely.

---

## 62. Rollback Timeout

Every rollback operation must have a timeout.

Example:

```text
Rollback Start
      ↓
Maximum Allowed Duration
      ↓
Success / Failure
```

---

## 63. Rollback Concurrency

Do not allow multiple rollback processes to modify the same production service simultaneously.

Example:

```text
Rollback A → Running
Rollback B → BLOCK
```

---

## 64. Rollback During Deployment

If a new deployment is currently progressing:

```text
Deployment
   ↓
Failure
   ↓
Stop Promotion
   ↓
Rollback
```

Do not start an unrelated deployment simultaneously.

---

## 65. Rollback During Incident

During an active incident:

```text
Freeze Non-Essential Changes
```

Avoid unrelated production modifications until service stability is restored.

---

## 66. Security Rollback

If the release introduces a security vulnerability:

```text
Identify
 ↓
Contain
 ↓
Rollback / Patch
 ↓
Rotate Credentials if Required
 ↓
Validate
 ↓
Monitor
```

---

## 67. Vulnerability Discovered After Deployment

If a critical vulnerability is discovered:

```text
Current Image
     ↓
Vulnerability
     ↓
Determine Exposure
     ↓
Rollback or Patch
     ↓
Security Validation
     ↓
Redeploy
```

Do not automatically rollback to an older image if the older image contains an equal or worse vulnerability.

---

## 68. Rollback and Data Integrity

Always consider whether the failed release modified:

```text
Database
Cache
Queues
Files
Object Storage
External APIs
```

before rollback.

---

## 69. Cache Rollback

Application rollback may require cache handling.

Potential actions:

```text
Invalidate
Warm
Version
Ignore
```

based on application behavior.

Do not blindly flush production caches.

---

## 70. Queue Rollback

For asynchronous systems, consider messages already processed by the failed version.

Validate:

```text
Queued
Processing
Completed
Failed
Dead Letter
```

states before rollback.

---

## 71. Duplicate Processing

Rollback of worker services must consider duplicate job execution.

Use:

```text
Idempotency
Job IDs
Deduplication
Checkpoints
```

where appropriate.

---

## 72. External API Side Effects

Some operations cannot be rolled back.

Example:

```text
Application
   ↓
External Payment API
   ↓
Payment Completed
```

Rolling back the application does not automatically reverse the external side effect.

---

## 73. Rollback Limitations

The rollback plan must explicitly document non-reversible operations.

Examples:

```text
External Transactions
Email Sent
Payment Completed
Data Exported
Third-Party Mutation
```

---

## 74. Production Rollback Runbook

Every critical production service should have a rollback runbook containing:

```text
Trigger
Prerequisites
Current Version Check
Known-Good Version
Rollback Command/Process
Health Checks
Smoke Tests
Monitoring
Escalation
Recovery
```

---

## 75. Rollback Command Standards

Commands must be environment-specific and validated before execution.

Never copy production commands blindly from development documentation.

---

## 76. Example ECS Rollback Concept

Conceptually:

```text
Current:
Task Definition 152
Image Digest A

Previous:
Task Definition 151
Image Digest B
```

Rollback:

```text
ECS Service
    ↓
Task Definition 151
    ↓
Image Digest B
    ↓
Deploy
    ↓
Health Check
```

---

## 77. Example Jenkins Rollback Flow

```text
Rollback Request
      ↓
Authenticate User
      ↓
Validate Authorization
      ↓
Validate Build
      ↓
Validate ECR Image
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

## 78. Rollback Environment Separation

Rollback must target the intended environment.

Never allow:

```text
Staging Rollback
```

to accidentally target:

```text
Production
```

or vice versa.

---

## 79. Production Rollback Confirmation

Before production rollback:

```text
Environment = production
Service = expected
Target Version = expected
Approval = valid
```

must be confirmed.

---

## 80. Rollback Quality Gate

Rollback must be blocked if:

```text
Target Artifact Missing
OR
Target Artifact Untrusted
OR
Target Version Unknown
OR
Authorization Missing
OR
Database Incompatible
OR
Rollback Creates Security Risk
```

---

## 81. Rollback Acceptance Criteria

A rollback is accepted only when:

1. Target version is known-good.
2. Target image is immutable.
3. Target image exists in ECR.
4. Correct environment is confirmed.
5. Required authorization exists.
6. ECS deployment succeeds.
7. Tasks are healthy.
8. ALB targets are healthy.
9. Health checks pass.
10. Smoke tests pass.
11. Critical alarms are clear.
12. Application metrics stabilize.
13. Logs are available.
14. Rollback is recorded.
15. Incident information is preserved.

---

## 82. Rollback Decision Matrix

| Situation                         | Action                                   |
| --------------------------------- | ---------------------------------------- |
| New version fails health check    | Rollback                                 |
| New version causes severe 5xx     | Rollback                                 |
| Canary fails                      | Stop traffic + rollback                  |
| Blue/green fails                  | Restore previous environment             |
| Security vulnerability introduced | Rollback or emergency patch              |
| Previous image unavailable        | Follow emergency recovery                |
| Database incompatible             | Do not blindly rollback                  |
| Previous version also vulnerable  | Patch forward                            |
| Terraform drift only              | Investigate before changing              |
| Terraform destructive change      | Stop and review                          |
| Secret compromised                | Revoke/rotate, not blind rollback        |
| External side effect completed    | Perform compensating action if available |
| Rollback repeatedly fails         | Escalate incident                        |

---

## 83. Rollback Testing

Rollback must be tested periodically.

Test:

```text
Application Rollback
ECS Rollback
ECR Artifact Availability
Jenkins Rollback
Database Compatibility
Health Checks
Smoke Tests
Monitoring
Incident Escalation
```

---

## 84. Rollback Drill

A rollback drill should simulate:

```text
Deployment
 ↓
Failure
 ↓
Detection
 ↓
Rollback
 ↓
Validation
 ↓
Monitoring
```

The drill should verify that the documented process actually works.

---

## 85. Rollback Metrics

Track:

```text
Rollback Frequency
Rollback Duration
Time to Detect
Time to Recover
Failed Rollbacks
Repeated Rollbacks
Incident Impact
```

---

## 86. Mean Time to Recovery

Measure:

```text
MTTR =
Incident Detection → Service Recovery
```

Reducing rollback time can reduce production impact.

---

## 87. Root Cause Analysis

After significant rollback:

```text
Incident
 ↓
Rollback
 ↓
Service Restored
 ↓
Root Cause Analysis
 ↓
Corrective Action
```

Rollback is recovery, not root-cause resolution.

---

## 88. Preventive Action

The incident should result in improvements where appropriate.

Examples:

```text
New Test
New Guardrail
New Alarm
New RAG Rule
New Security Rule
New Deployment Check
New Rollback Test
```

---

## 89. Rollback Knowledge Feedback

Production rollback incidents should feed back into the RAG knowledge base.

```text
Incident
   ↓
Root Cause
   ↓
Lesson
   ↓
Standard Update
   ↓
RAG
   ↓
Future Agent
```

---

## 90. Rollback Agent Input

Example:

```json
{
  "project_id": "project-123",
  "environment": "production",
  "service": "backend",
  "current_version": "1.4.2",
  "current_image_digest": "sha256:new...",
  "previous_version": "1.4.1",
  "previous_image_digest": "sha256:old...",
  "failure_reason": "high_5xx",
  "approval_status": "approved"
}
```

---

## 91. Rollback Agent Output

Example:

```json
{
  "project_id": "project-123",
  "environment": "production",
  "rollback_version": "1.4.1",
  "image_digest": "sha256:old...",
  "rollback_status": "completed",
  "tasks_healthy": true,
  "target_health": "healthy",
  "smoke_test": "passed",
  "monitoring": "healthy",
  "status": "passed"
}
```

---

## 92. Rollback Agent Workflow

```text
Rollback Request
       ↓
Validate Environment
       ↓
Validate Authorization
       ↓
Retrieve Rollback Rules
       ↓
Identify Current Version
       ↓
Identify Known-Good Version
       ↓
Validate Image
       ↓
Check Database Compatibility
       ↓
Check Security Status
       ↓
Execute Rollback
       ↓
Health Check
       ↓
Smoke Test
       ↓
Monitor
       ↓
Record Rollback
```

---

## 93. Rollback Agent Safety Rules

The Rollback Agent must never:

* Roll back to an unknown artifact
* Deploy an untrusted image
* Expose credentials
* Ignore database incompatibility
* Disable security controls
* Delete Terraform state
* Destroy production infrastructure without authorization
* Roll back to a known-compromised credential
* Ignore active critical alarms
* Execute unlimited retries
* Modify unrelated production resources

---

## 94. Final Rollback Quality Gate

A rollback is considered complete only when:

```text
Known-Good Artifact
       ↓
Authorized Rollback
       ↓
Correct Environment
       ↓
ECS Healthy
       ↓
ALB Healthy
       ↓
Application Healthy
       ↓
Smoke Tests Passed
       ↓
Critical Metrics Normal
       ↓
Monitoring Stable
       ↓
Audit Recorded
```

---

## 95. Final Rule

> Rollback must restore production to a known-good, traceable, immutable, and validated state without introducing additional security, data, or infrastructure risk.

The platform must always prefer:

```text
Known-Good Artifact
        +
Controlled Rollback
        +
Health Validation
        +
Smoke Testing
        +
Monitoring
```

over uncontrolled emergency changes.

**Final Production Recovery Rule:**

> A deployment is not considered recovered merely because the previous version is running. Recovery is complete only after the previous known-good artifact is deployed, ECS and ALB health are restored, critical application behavior is validated, monitoring is stable, data integrity is considered, and the rollback is fully recorded.
