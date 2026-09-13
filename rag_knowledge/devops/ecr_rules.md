# ECR Rules

## 1. Purpose

This document defines Amazon Elastic Container Registry (ECR) standards for the Agentic SDLC platform.

ECR must provide secure, versioned, traceable, and controlled storage of Docker images used by development, staging, and production environments.

---

## 2. ECR Standards Summary

ECR repositories must be:

* Secure
* Private by default
* Environment-aware
* Version-controlled
* Immutable where appropriate
* Vulnerability-scanned
* Encrypted
* Access-controlled
* Lifecycle-managed
* CI/CD compatible
* Traceable to source code

---

## 3. ECR Repository Structure

Repositories should follow a predictable naming convention.

Example:

```text
company/myapp
company/myapp-frontend
company/myapp-backend
```

For environment-specific repositories:

```text
company/myapp-dev
company/myapp-staging
company/myapp-prod
```

The organization should choose one consistent repository strategy.

---

## 4. Repository Naming

Repository names should identify:

* Organization/project
* Application
* Component where required
* Environment where required

Example:

```text
agentic-sdlc/backend-prod
agentic-sdlc/frontend-prod
```

Avoid ambiguous names such as:

```text
test
app1
newimage
final
final2
```

---

## 5. Private Repository Standard

Application repositories should be private unless public distribution is explicitly required.

Production application images must not be stored in public repositories without security approval.

---

## 6. Repository Creation

ECR repositories may be created using Terraform.

Example:

```hcl
resource "aws_ecr_repository" "app" {
  name                 = "${var.project_name}-${var.environment}"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}
```

---

## 7. Image Tag Mutability

Production repositories should use immutable image tags.

Example:

```hcl
image_tag_mutability = "IMMUTABLE"
```

This prevents an existing tag from being overwritten with a different image.

---

## 8. Avoid Mutable Production Tags

Avoid using:

```text
latest
stable
production
release
```

as the only production image identifier.

Instead use:

```text
build-152
git-a81f92c
v1.4.2
```

---

## 9. Image Tagging Strategy

Recommended:

```text
<application>:<build-number>
```

Example:

```text
myapp:152
```

Git SHA may also be used:

```text
myapp:a81f92c
```

A release version may additionally be used:

```text
myapp:v1.4.2
```

---

## 10. Image Traceability

Every production image must be traceable to:

```text
ECR Image
   ↓
Jenkins Build
   ↓
Git Commit
   ↓
Git Repository
   ↓
Application Version
```

Recommended metadata:

```text
Project
Commit SHA
Build Number
Branch
Version
Environment
Build Timestamp
```

---

## 11. Image Digest

The image digest is the strongest identifier for a container image.

Example:

```text
sha256:abc123...
```

Production deployments should preferably record the exact image digest.

---

## 12. Digest-Based Deployment

Preferred production flow:

```text
Build Image
     ↓
Push ECR
     ↓
Get Digest
     ↓
Deploy Exact Digest
     ↓
ECS
```

This ensures the deployed image cannot silently change.

---

## 13. Docker Image Push

Example:

```bash
docker tag myapp:$BUILD_NUMBER \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/myapp:$BUILD_NUMBER

docker push \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/myapp:$BUILD_NUMBER
```

---

## 14. ECR Authentication

Jenkins or another CI/CD system should authenticate using approved AWS credentials.

Example:

```bash
aws ecr get-login-password \
  --region $AWS_REGION |
docker login \
  --username AWS \
  --password-stdin \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
```

Credentials must never be hardcoded.

---

## 15. IAM Access

ECR access must follow least privilege.

CI/CD may require permissions such as:

```text
ecr:GetAuthorizationToken
ecr:BatchCheckLayerAvailability
ecr:CompleteLayerUpload
ecr:InitiateLayerUpload
ecr:UploadLayerPart
ecr:PutImage
```

Runtime workloads such as ECS should receive only the ECR permissions required to pull images.

---

## 16. ECS Image Pull Access

ECS task execution roles should have appropriate permissions to pull private ECR images.

Conceptual flow:

```text
ECS Task
   ↓
Task Execution Role
   ↓
ECR
   ↓
Docker Image
```

The application container should not receive unnecessary ECR administrative permissions.

---

## 17. ECR Encryption

Repositories must use encryption.

Options include:

```text
AES-256
AWS KMS
```

Use KMS when organizational requirements require customer-managed encryption keys.

---

## 18. KMS Standards

If a customer-managed KMS key is used:

* Key access must be restricted.
* Key rotation should follow organizational requirements.
* CI/CD roles should receive only required permissions.
* ECS execution roles should receive only required permissions.

---

## 19. Scan on Push

ECR image vulnerability scanning should be enabled where supported by the organization's AWS configuration.

Example:

```hcl
image_scanning_configuration {
  scan_on_push = true
}
```

Images should be scanned before production deployment.

---

## 20. Enhanced Image Scanning

Where available and required, use enhanced scanning capabilities integrated with Amazon Inspector.

Enhanced scanning should be evaluated for production workloads requiring continuous vulnerability visibility.

---

## 21. Vulnerability Severity

Vulnerabilities should be classified as:

```text
Critical
High
Medium
Low
Informational
```

Recommended policy:

```text
Critical → Block
High     → Block or Security Approval
Medium   → Review
Low      → Track
```

The final policy must follow organizational security standards.

---

## 22. Image Scan Quality Gate

Production deployment should not proceed when a mandatory vulnerability gate fails.

Example:

```text
ECR Image
    ↓
Vulnerability Scan
    ↓
Critical = 0
High = 0
    ↓
Approved
```

---

## 23. Base Image Security

Docker images pushed to ECR must use approved base images.

Preferred characteristics:

* Official
* Maintained
* Minimal
* Recently patched
* Vulnerability monitored

Avoid obsolete or unsupported base images.

---

## 24. Minimal Images

Images should contain only required runtime dependencies.

Avoid unnecessary:

```text
Compilers
Debugging tools
Package managers
Development dependencies
Source artifacts
Temporary files
```

when they are not required at runtime.

---

## 25. Multi-Stage Builds

Multi-stage Docker builds should be used when they reduce runtime image size and attack surface.

Example:

```text
Builder Image
     ↓
Compile / Install
     ↓
Runtime Image
     ↓
ECR
```

---

## 26. Production Runtime Image

The production image should contain only what the application needs to run.

For Python/FastAPI:

```text
Python Runtime
Application Code
Production Dependencies
Required System Libraries
```

Development tooling should normally remain outside the runtime image.

---

## 27. Image Size

Image size should be monitored.

Large images can increase:

* Pull time
* Deployment time
* Storage cost
* Attack surface

The CI pipeline should identify unexpectedly large image changes.

---

## 28. Image Layer Optimization

Docker layers should be structured to maximize caching while keeping images secure.

Example:

```dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
```

Dependencies should be separated from frequently changing application code where practical.

---

## 29. Build Reproducibility

The same source commit and build configuration should produce a predictable image.

Builds should control:

* Base image
* Dependencies
* Build arguments
* Runtime configuration
* Build tools

---

## 30. Build Secrets

Secrets must never be copied into the image.

Forbidden:

```dockerfile
COPY .env .
```

Also avoid:

```dockerfile
ARG API_KEY
ENV API_KEY=$API_KEY
```

for production secrets.

Use secure build-secret mechanisms only when a secret is genuinely required during the build.

---

## 31. Runtime Secrets

Application secrets should be injected at runtime.

Example:

```text
ECS
 ↓
Secrets Manager
 ↓
Container
```

The secret should not be stored in the ECR image.

---

## 32. Secret Scanning

Images and repositories should be scanned for accidentally embedded secrets.

Potential secrets include:

* AWS credentials
* GitHub tokens
* API keys
* Database passwords
* Private keys
* LLM API keys

Secret exposure must block production deployment.

---

## 33. ECR Repository Policies

Repository policies must be restrictive.

Cross-account access should only be granted when explicitly required.

Avoid unnecessary:

```text
Principal: "*"
```

permissions.

---

## 34. Cross-Account ECR Access

When cross-account image access is required:

```text
AWS Account A
ECR Repository
      ↓
Repository Policy
      ↓
AWS Account B
ECS / CI/CD
```

Only the required account and actions should be permitted.

---

## 35. ECR Lifecycle Policies

Repositories should have lifecycle policies to remove obsolete images.

Example:

```json
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Keep last 30 images",
      "selection": {
        "tagStatus": "any",
        "countType": "imageCountMoreThan",
        "countNumber": 30
      },
      "action": {
        "type": "expire"
      }
    }
  ]
}
```

The retention period must account for rollback requirements.

---

## 36. Production Image Retention

Production images should be retained long enough to support:

* Rollback
* Incident investigation
* Auditing
* Compliance
* Release comparison

Do not delete the only known-good production image.

---

## 37. Untagged Images

Untagged images should be cleaned periodically.

Example lifecycle rule:

```text
Untagged Images
      ↓
Retention Period
      ↓
Automatic Cleanup
```

---

## 38. Image Promotion

The same validated image should preferably be promoted between environments rather than rebuilt.

Preferred:

```text
Build Once
   ↓
Scan
   ↓
Dev
   ↓
Staging
   ↓
Production
```

Avoid:

```text
Build Dev
Build Staging
Build Production
```

with potentially different artifacts.

---

## 39. Environment Promotion

Recommended:

```text
ECR
 ↓
Image: a81f92c
 ↓
Development
 ↓
Testing
 ↓
Staging
 ↓
Approval
 ↓
Production
```

The production image should be the exact validated artifact.

---

## 40. ECR and Jenkins

Jenkins should:

```text
Checkout
   ↓
Test
   ↓
Security Scan
   ↓
Docker Build
   ↓
Image Scan
   ↓
ECR Push
   ↓
Record Digest
   ↓
Deploy
```

ECR push should occur only after required build and security gates pass.

---

## 41. ECR and Terraform

Terraform should manage repository infrastructure where appropriate.

Terraform may create:

```text
ECR Repository
Encryption
Lifecycle Policy
Repository Policy
Scanning Configuration
```

Application images themselves should normally be built and pushed by CI/CD rather than Terraform.

---

## 42. ECR and ECS

ECS should consume images from ECR.

Flow:

```text
Developer
   ↓
Git
   ↓
Jenkins
   ↓
Docker Build
   ↓
ECR
   ↓
ECS
```

The ECS task definition should reference the intended image tag or digest.

---

## 43. ECR and ECS Auto Scaling

ECR does not perform application scaling.

Scaling belongs to ECS/Application Auto Scaling.

Architecture:

```text
ECR
 ↓
ECS Task Definition
 ↓
ECS Service
 ↓
Auto Scaling
 ↓
Multiple Tasks
```

ECR's responsibility is secure image storage and distribution.

---

## 44. Image Pull Reliability

Production ECS deployments should ensure that:

* ECR is reachable
* IAM permissions are valid
* Image exists
* Image architecture matches the runtime
* Image digest is valid
* Required network connectivity exists

---

## 45. CPU Architecture

The image architecture must match the ECS runtime architecture.

Common architectures:

```text
amd64
arm64
```

If multi-architecture images are required, build and publish appropriate manifests.

---

## 46. Multi-Architecture Images

Example:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t $IMAGE \
  --push .
```

Only use architectures supported by the deployment environment.

---

## 47. Image Metadata

Images should include useful metadata where practical.

Example:

```dockerfile
LABEL org.opencontainers.image.source="repository"
LABEL org.opencontainers.image.revision="commit-sha"
LABEL org.opencontainers.image.version="1.0.0"
```

This improves traceability.

---

## 48. SBOM

Software Bill of Materials should be generated for production images where required.

Example:

```bash
trivy image --format cyclonedx $IMAGE
```

The SBOM should identify:

* OS packages
* Python packages
* Application dependencies
* Versions

---

## 49. Image Provenance

Production images should have build provenance where organizational supply-chain requirements require it.

Recommended metadata:

```text
Source Repository
Commit SHA
Build System
Build Number
Builder
Timestamp
```

---

## 50. Image Signing

For high-security environments, images should be cryptographically signed.

Conceptual flow:

```text
Build
 ↓
Scan
 ↓
Sign
 ↓
Push
 ↓
Verify
 ↓
Deploy
```

Deployment systems may enforce signature verification.

---

## 51. ECR Replication

For multi-region or disaster-recovery architectures, ECR replication may be configured.

Example:

```text
Primary Region
      ↓
ECR Replication
      ↓
Secondary Region
```

Replication must follow security and compliance requirements.

---

## 52. Disaster Recovery

Critical production images should have a recovery strategy.

Consider:

* ECR replication
* Image retention
* Immutable tags
* Image digests
* Backup region
* Registry availability

---

## 53. ECR Monitoring

Monitor:

* Image scan findings
* Repository usage
* Image push failures
* Image pull failures
* Repository policy changes
* Unexpected image changes
* Lifecycle cleanup

AWS logging and monitoring services should be used where appropriate.

---

## 54. ECR Audit

Important ECR operations should be auditable.

Examples:

```text
Repository creation
Image push
Image deletion
Repository policy change
Image retrieval
Permission changes
```

AWS CloudTrail should be used where applicable.

---

## 55. ECR Deletion Protection

Critical production images should not be deleted accidentally.

Use:

* Restricted IAM permissions
* Lifecycle policies
* Protected release processes
* Explicit approval for destructive operations

---

## 56. ECR Incident Response

If a malicious or vulnerable image is discovered:

```text
Detect
 ↓
Block Promotion
 ↓
Identify Affected Images
 ↓
Identify Deployments
 ↓
Remove/Quarantine Image
 ↓
Build Patched Image
 ↓
Scan
 ↓
Deploy Patched Version
 ↓
Validate
```

If a compromised credential was included, revoke and rotate it immediately.

---

## 57. Vulnerable Image Handling

Do not simply delete a vulnerable image and assume the issue is resolved.

First identify:

```text
Which environment uses it?
Which ECS service uses it?
Which version is affected?
Which vulnerabilities exist?
Is rollback available?
```

Then remediate and redeploy.

---

## 58. ECR Agent Input

Example:

```json
{
  "project_id": "project-123",
  "repository": "myapp",
  "environment": "production",
  "aws_region": "ap-south-1",
  "image_tag": "152",
  "commit_sha": "a81f92c",
  "deployment_target": "ecs",
  "security_requirements": {
    "scan": true,
    "immutable_tags": true,
    "encryption": true
  }
}
```

---

## 59. ECR Agent Output

Example:

```json
{
  "repository": "myapp",
  "image_tag": "152",
  "image_digest": "sha256:abc123...",
  "pushed": true,
  "scan_passed": true,
  "critical_vulnerabilities": 0,
  "high_vulnerabilities": 0,
  "image_signed": true,
  "status": "passed"
}
```

---

## 60. ECR Agent Workflow

The ECR Agent should follow:

```text
Receive Image
      ↓
Validate Repository
      ↓
Validate Tag
      ↓
Validate AWS Authentication
      ↓
Authenticate to ECR
      ↓
Push Image
      ↓
Retrieve Image Digest
      ↓
Run/Validate Security Scan
      ↓
Check Vulnerabilities
      ↓
Generate SBOM if Required
      ↓
Validate Metadata
      ↓
Validate Deployment Eligibility
      ↓
Generate Report
      ↓
Return Result
```

---

## 61. ECR Agent Safety Rules

The ECR Agent must not:

* Expose AWS credentials
* Push unapproved images
* Overwrite immutable production tags
* Delete production images without authorization
* Bypass vulnerability gates
* Push images containing detected secrets
* Promote an unvalidated image

---

## 62. ECR Validation Checklist

### Repository

* [ ] Repository exists
* [ ] Repository name is correct
* [ ] Repository is private where required
* [ ] Encryption is enabled
* [ ] Lifecycle policy exists
* [ ] Repository policy is restricted
* [ ] Image mutability is configured

### Image

* [ ] Image builds successfully
* [ ] Image tag is traceable
* [ ] Commit SHA is known
* [ ] Image digest is recorded
* [ ] Image architecture is correct
* [ ] Image size is reasonable
* [ ] Image metadata exists where required

### Security

* [ ] Image scan completed
* [ ] Critical vulnerabilities resolved
* [ ] High vulnerabilities resolved/approved
* [ ] Secrets scan passes
* [ ] SBOM generated where required
* [ ] Image signing completed where required

### Deployment

* [ ] ECR push succeeds
* [ ] ECS can pull image
* [ ] Task execution role has required access
* [ ] Exact image version is deployed
* [ ] Health checks pass
* [ ] Rollback image remains available

---

## 63. ECR Implementation Decision Matrix

| Situation             | Recommended Implementation             | Avoid                             |
| --------------------- | -------------------------------------- | --------------------------------- |
| Production repository | Private ECR                            | Public repository                 |
| Image tags            | Immutable build/Git tags               | Only `latest`                     |
| Deployment identity   | Image digest                           | Uncontrolled mutable tag          |
| Encryption            | AES-256/KMS                            | Unencrypted repository            |
| CI authentication     | IAM role/secure credentials            | Hardcoded AWS keys                |
| Image scanning        | ECR/Inspector scanning                 | No vulnerability scanning         |
| Image build           | Jenkins/CI                             | Manual laptop-only build          |
| Image promotion       | Same validated artifact                | Rebuilding for each environment   |
| Image retention       | Lifecycle policy                       | Unlimited accumulation            |
| Production deletion   | Restricted + approved                  | Unrestricted deletion             |
| Secrets               | Runtime secret injection               | Secrets inside image              |
| Base image            | Supported/minimal image                | Obsolete image                    |
| Supply chain          | SBOM/provenance/signing where required | Unknown image origin              |
| ECS deployment        | Tag + preferably digest                | Arbitrary mutable tag             |
| Rollback              | Previous immutable image               | Rebuilding during incident        |
| Cross-account access  | Restricted repository policy           | `Principal: "*"`                  |
| Multi-region          | ECR replication where required         | Manual image copying              |
| Security gate         | Block Critical/required High findings  | Deploying known vulnerable images |

---

## 64. ECR Acceptance Criteria

An ECR implementation is accepted only when:

1. Repository exists.
2. Repository naming is consistent.
3. Repository is private where required.
4. Encryption is enabled.
5. Image mutability follows policy.
6. Lifecycle policy is configured.
7. IAM permissions follow least privilege.
8. CI/CD authentication is secure.
9. Image tags are traceable.
10. Image digest is recorded.
11. Vulnerability scanning is enabled where required.
12. Critical vulnerabilities are zero before production.
13. Required High vulnerabilities are resolved or approved.
14. Secret scanning passes.
15. Image contains no production secrets.
16. Image architecture matches deployment environment.
17. Image can be pulled by ECS.
18. Production image is immutable.
19. Rollback image remains available.
20. Required SBOM/provenance/signing controls pass.
21. Auditability is enabled.
22. Deployment health validation succeeds.

---

## 65. ECR Production Quality Gate

Production promotion must be blocked when:

```text
Image Build Failed
        OR
Image Scan Failed
        OR
Critical Vulnerability Detected
        OR
Required High Vulnerability Detected
        OR
Secret Detected
        OR
Image Not Traceable
        OR
Image Digest Missing
        OR
Repository Access Invalid
        OR
ECR Push Failed
        OR
Image Signature Invalid
        OR
ECS Cannot Pull Image
```

---

## 66. Final ECR Rule

The Agentic SDLC platform must treat the ECR image as a **production software artifact**, not simply as a Docker file stored in AWS.

The complete flow must be:

```text
Source Code
     ↓
Jenkins
     ↓
Test
     ↓
Security Scan
     ↓
Docker Build
     ↓
Image Scan
     ↓
Secret Scan
     ↓
SBOM / Provenance
     ↓
ECR
     ↓
Immutable Tag / Digest
     ↓
ECS
     ↓
Health Check
     ↓
Production
```

**Final Rule:**

> Every production Docker image generated by the Agentic SDLC platform must be securely built, vulnerability-scanned, free from embedded secrets, traceable to its source commit, stored in an appropriately secured ECR repository, identified by an immutable version or digest, and validated before deployment.
