# Terraform Rules

## 1. Purpose

This document defines Terraform standards for the Agentic SDLC platform.

Terraform must be used to provision and manage infrastructure in a consistent, reproducible, secure, reviewable, and automated manner.

Generated Terraform must pass validation, security checks, planning, and required approval gates before infrastructure changes are applied.

---

## 2. Terraform Standards Summary

Terraform implementations must be:

* Declarative
* Reproducible
* Version-controlled
* Modular
* Secure
* Environment-aware
* Idempotent
* Reviewable
* State-managed
* Least-privilege
* CI/CD compatible

---

## 3. Terraform Version Standards

The project must define a supported Terraform version.

Example:

```hcl
terraform {
  required_version = ">= 1.9, < 2.0"
}
```

Terraform versions must be tested before being upgraded.

---

## 4. Provider Version Standards

Providers must be explicitly declared.

Example:

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
```

Provider versions should be controlled to prevent unexpected infrastructure changes.

---

## 5. Terraform Project Structure

Recommended structure:

```text
infrastructure/
└── terraform/
    ├── main.tf
    ├── variables.tf
    ├── outputs.tf
    ├── providers.tf
    ├── versions.tf
    ├── locals.tf
    ├── data.tf
    ├── terraform.tfvars.example
    ├── modules/
    │   ├── networking/
    │   ├── ecs/
    │   ├── ecr/
    │   ├── iam/
    │   └── monitoring/
    └── environments/
        ├── dev/
        ├── staging/
        └── prod/
```

The exact structure may vary according to project complexity.

---

## 6. Terraform File Responsibilities

Recommended responsibilities:

| File               | Responsibility                     |
| ------------------ | ---------------------------------- |
| `main.tf`          | Main resources/modules             |
| `providers.tf`     | Provider configuration             |
| `versions.tf`      | Terraform/provider versions        |
| `variables.tf`     | Input variables                    |
| `outputs.tf`       | Output values                      |
| `locals.tf`        | Local computed values              |
| `data.tf`          | Data sources                       |
| `terraform.tfvars` | Environment-specific values        |
| `modules/`         | Reusable infrastructure components |

---

## 7. Provider Configuration

AWS provider configuration should be centralized.

Example:

```hcl
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
```

---

## 8. AWS Region Standards

AWS region must not be hardcoded throughout resource definitions.

Preferred:

```hcl
variable "aws_region" {
  type        = string
  description = "AWS region"
}
```

Then:

```hcl
provider "aws" {
  region = var.aws_region
}
```

---

## 9. Environment Separation

Infrastructure must clearly separate:

```text
Development
Staging
Production
```

Production infrastructure must never accidentally use development configuration.

---

## 10. Environment Configuration

Environment-specific values should be passed through variables or environment-specific configuration.

Example:

```text
environments/
├── dev/
├── staging/
└── prod/
```

Environment values must not be duplicated unnecessarily inside resource definitions.

---

## 11. Terraform Variables

Variables must have:

* Meaningful names
* Explicit types
* Descriptions
* Validation where appropriate

Example:

```hcl
variable "environment" {
  type        = string
  description = "Deployment environment"

  validation {
    condition = contains(
      ["dev", "staging", "prod"],
      var.environment
    )

    error_message = "Environment must be dev, staging, or prod."
  }
}
```

---

## 12. Sensitive Variables

Sensitive values must be marked appropriately.

Example:

```hcl
variable "database_password" {
  type      = string
  sensitive = true
}
```

Marking a variable sensitive does not remove the secret from Terraform state.

Secret management must therefore be handled separately.

---

## 13. Terraform Secrets

Secrets must never be hardcoded.

Forbidden:

```hcl
password = "MyPassword123"
```

Use approved mechanisms such as:

```text
AWS Secrets Manager
AWS Systems Manager Parameter Store
Jenkins Credentials
Environment-based secure injection
```

---

## 14. AWS Authentication

Terraform running on AWS should preferably use IAM roles.

Preferred:

```text
Jenkins EC2/ECS Agent
        ↓
IAM Role
        ↓
AWS API
```

Avoid storing long-lived AWS access keys in Terraform files.

---

## 15. Least Privilege

Terraform execution roles must have only the permissions required to manage the target infrastructure.

Avoid:

```text
AdministratorAccess
```

unless explicitly required and approved.

---

## 16. Resource Naming

Resources should use predictable naming.

Example:

```hcl
name = "${var.project_name}-${var.environment}-ecs"
```

Names should make it possible to identify:

* Project
* Environment
* Resource purpose

---

## 17. Resource Tags

AWS resources should use consistent tags.

Recommended:

```text
Project
Environment
ManagedBy
Owner
CostCenter
Application
```

Example:

```hcl
tags = {
  Project     = var.project_name
  Environment = var.environment
  ManagedBy   = "Terraform"
}
```

---

## 18. Terraform Modules

Reusable infrastructure should be implemented using modules.

Example:

```text
modules/
├── vpc/
├── ecs/
├── ecr/
├── iam/
├── rds/
└── monitoring/
```

Modules should have clear inputs and outputs.

---

## 19. Module Structure

Recommended:

```text
modules/ecs/
├── main.tf
├── variables.tf
├── outputs.tf
└── README.md
```

Modules should avoid hidden dependencies.

---

## 20. Module Versioning

Shared modules should use controlled versions.

Avoid silently changing a shared module used by production environments.

Module changes must go through code review and CI validation.

---

## 21. Data Sources

Use data sources when referencing existing infrastructure.

Example:

```hcl
data "aws_caller_identity" "current" {}

data "aws_vpc" "existing" {
  id = var.vpc_id
}
```

Do not recreate resources that are intentionally managed outside Terraform.

---

## 22. Resource Dependencies

Terraform should normally determine dependencies automatically.

Example:

```hcl
resource "aws_ecs_service" "app" {
  task_definition = aws_ecs_task_definition.app.arn
}
```

Use `depends_on` only when an implicit dependency cannot represent the required relationship.

---

## 23. Terraform State

Terraform state is critical infrastructure data.

State may contain:

* Resource IDs
* Configuration metadata
* Sensitive values
* Infrastructure relationships

State must therefore be protected.

---

## 24. Remote State

Production Terraform must use remote state.

For AWS, a common implementation is:

```text
S3
+
State Locking
+
Encryption
+
Restricted IAM Access
```

Example:

```hcl
terraform {
  backend "s3" {
    bucket       = "company-terraform-state"
    key          = "myapp/prod/terraform.tfstate"
    region       = "ap-south-1"
    encrypt      = true
    use_lockfile = true
  }
}
```

---

## 25. Terraform State Locking

State locking must be enabled for shared environments.

Locking prevents multiple Terraform executions from modifying the same state simultaneously.

Current S3 backend configurations should use the supported S3 lock-file mechanism where appropriate:

```hcl
use_lockfile = true
```

Legacy locking approaches must follow the Terraform version and organizational standard.

---

## 26. State Access Control

Only authorized users and CI/CD roles should access Terraform state.

Permissions should be separated between:

```text
Read State
Write State
Administrative State Operations
```

---

## 27. State Encryption

Remote Terraform state must be encrypted.

For AWS S3:

```text
S3
 ↓
Server-Side Encryption
 ↓
Restricted IAM
```

Where organizational requirements demand it, use an approved KMS key.

---

## 28. State File Security

Never commit:

```text
terraform.tfstate
terraform.tfstate.backup
```

to Git.

Recommended `.gitignore`:

```text
*.tfstate
*.tfstate.*
.terraform/
.terraform.lock.hcl
*.tfvars
```

The lock file should only be ignored if the organization explicitly chooses not to commit it. Normally `.terraform.lock.hcl` should be committed.

---

## 29. Terraform Lock File

`.terraform.lock.hcl` should normally be committed to source control.

It records selected provider versions and checksums.

Example:

```text
.terraform.lock.hcl
```

This improves reproducibility across environments.

---

## 30. Terraform Backend Separation

Development, staging, and production should not accidentally share the same state.

Example:

```text
S3
├── app/dev/terraform.tfstate
├── app/staging/terraform.tfstate
└── app/prod/terraform.tfstate
```

---

## 31. Terraform Workspaces

Terraform workspaces may be used when appropriate.

Example:

```bash
terraform workspace list
terraform workspace select dev
terraform workspace select prod
```

Workspaces should not be used as a substitute for proper environment architecture when environments have significantly different infrastructure or access requirements.

---

## 32. Terraform Formatting

All Terraform code must be formatted.

Command:

```bash
terraform fmt -recursive
```

CI validation:

```bash
terraform fmt -check -recursive
```

Formatting failures should block the pipeline.

---

## 33. Terraform Validation

Terraform configuration must be validated before planning.

Commands:

```bash
terraform init
terraform validate
```

Validation must pass before `terraform plan`.

---

## 34. Terraform Initialization

CI should initialize Terraform in a controlled manner.

Example:

```bash
terraform init
```

For automated environments:

```bash
terraform init -input=false
```

Provider downloads must use the approved Terraform registry/provider sources.

---

## 35. Terraform Plan

Infrastructure changes must be reviewed through a plan.

Command:

```bash
terraform plan
```

CI example:

```bash
terraform plan \
  -input=false \
  -out=tfplan
```

The generated plan should be reviewed before production apply.

---

## 36. Terraform Apply

Production changes should use an approved plan.

Example:

```bash
terraform apply \
  -input=false \
  tfplan
```

Avoid uncontrolled:

```bash
terraform apply -auto-approve
```

for production unless the organization's automation policy explicitly allows it.

---

## 37. Terraform Approval

Production infrastructure changes should require appropriate approval.

Recommended:

```text
Terraform Plan
      ↓
Review
      ↓
Approval
      ↓
Terraform Apply
```

---

## 38. Terraform Destroy

`terraform destroy` is a high-risk operation.

Production destruction must require explicit authorization.

Never allow an agent to execute production destroy automatically without a strict approval gate.

---

## 39. Resource Protection

Critical resources should have deletion protection where supported.

Examples:

```text
Production RDS
Production databases
Critical S3 buckets
Important ECS services
```

Terraform lifecycle rules may also be used where appropriate.

Example:

```hcl
lifecycle {
  prevent_destroy = true
}
```

---

## 40. Lifecycle Rules

Use lifecycle rules carefully.

Example:

```hcl
lifecycle {
  create_before_destroy = true
}
```

This may help reduce downtime for replaceable resources.

Do not use lifecycle rules to hide legitimate infrastructure drift or prevent necessary updates indefinitely.

---

## 41. Infrastructure Drift

Terraform drift occurs when infrastructure changes outside Terraform.

Example:

```text
Terraform State
      ≠
AWS Actual Infrastructure
```

Drift should be detected and investigated.

Avoid making manual production changes unless operationally necessary and documented.

---

## 42. Drift Detection

CI or scheduled infrastructure validation may run:

```bash
terraform plan
```

Unexpected changes should be reported.

The Agentic SDLC platform may use scheduled drift detection for production infrastructure.

---

## 43. Terraform Security Scanning

Terraform code should be security scanned.

Approved tools may include:

```text
Checkov
tfsec
Trivy
Terrascan
```

Example:

```bash
checkov -d .
```

---

## 44. Terraform Static Validation

The Terraform pipeline should perform:

```text
terraform fmt
        ↓
terraform validate
        ↓
Security Scan
        ↓
terraform plan
```

Failures must block promotion.

---

## 45. AWS Infrastructure Security

Terraform-generated AWS infrastructure must follow least-privilege and secure-default principles.

Examples:

* Private subnets where appropriate
* Restricted security groups
* Encryption enabled
* IAM least privilege
* No public database unless required
* Restricted S3 access
* Logging enabled
* Secrets stored securely

---

## 46. VPC Standards

Terraform-managed VPCs should define:

```text
VPC
├── Public Subnets
├── Private Subnets
├── Route Tables
├── Internet Gateway
├── NAT Gateway where required
└── Security Controls
```

Production application workloads should normally run in private subnets when architecture permits.

---

## 47. Security Group Standards

Security groups must allow only required traffic.

Avoid:

```text
0.0.0.0/0
```

for administrative ports such as SSH unless there is a documented and secured requirement.

Example:

```text
ALB
 ↓
ECS
 ↓
RDS
```

Each layer should permit only required communication.

---

## 48. IAM Standards

IAM policies must follow least privilege.

Avoid broad:

```json
{
  "Action": "*",
  "Resource": "*"
}
```

unless explicitly justified and approved.

Terraform-generated IAM roles should contain only required permissions.

---

## 49. ECR Terraform Standards

Terraform may provision:

```text
ECR Repository
Image Scanning
Encryption
Lifecycle Policy
Repository Policy
```

Example:

```hcl
resource "aws_ecr_repository" "app" {
  name                 = "${var.project_name}-${var.environment}"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
```

---

## 50. ECS Terraform Standards

Terraform may manage:

```text
ECS Cluster
Task Definition
ECS Service
Load Balancer
Target Group
IAM Roles
Security Groups
CloudWatch Logs
Auto Scaling
```

ECS services should define appropriate health checks and deployment configuration.

---

## 51. ECS Auto Scaling

Terraform may configure ECS Service Auto Scaling.

Conceptual architecture:

```text
ECS Service
    ↓
Desired Tasks
    ↓
CloudWatch Metrics
    ↓
Auto Scaling
    ├── Minimum Tasks
    └── Maximum Tasks
```

Example resources:

```text
aws_appautoscaling_target
aws_appautoscaling_policy
```

Scaling values must be based on workload requirements and performance testing.

---

## 52. RDS Terraform Standards

Production RDS resources should consider:

* Encryption
* Backup retention
* Multi-AZ where required
* Private networking
* Security groups
* Deletion protection
* Monitoring
* Maintenance windows

Database credentials must not be hardcoded.

---

## 53. S3 Terraform Standards

S3 buckets should use:

* Encryption
* Restricted bucket policies
* Block Public Access where appropriate
* Versioning where required
* Lifecycle rules
* Logging/auditing where required

Avoid public buckets unless explicitly required.

---

## 54. CloudWatch Terraform Standards

Terraform should manage required monitoring resources where appropriate.

Examples:

```text
CloudWatch Log Groups
CloudWatch Alarms
ECS Metrics
Application Metrics
Infrastructure Alarms
```

Monitoring should support deployment validation and operational troubleshooting.

---

## 55. Terraform and Jenkins CI/CD

Recommended pipeline:

```text
Checkout
   ↓
terraform fmt -check
   ↓
terraform validate
   ↓
Security Scan
   ↓
terraform plan
   ↓
Approval
   ↓
terraform apply
   ↓
Validation
```

Production apply must occur only after required approval.

---

## 56. Terraform Plan Artifacts

Terraform plans may be stored as CI artifacts when required.

Example:

```bash
terraform plan -out=tfplan
```

Plan artifacts must be protected because they may contain sensitive infrastructure information.

---

## 57. Terraform Output Security

Do not expose sensitive outputs unnecessarily.

Example:

```hcl
output "database_password" {
  value     = var.database_password
  sensitive = true
}
```

Even sensitive outputs should not be printed into CI logs.

---

## 58. Terraform Provider Credentials

Provider credentials should come from the runtime environment or IAM role.

Example:

```text
Jenkins Agent
      ↓
IAM Role
      ↓
Terraform
      ↓
AWS
```

Terraform source code should remain credential-free.

---

## 59. Terraform Environment Variables

Terraform supports environment variables such as:

```text
AWS_REGION
AWS_PROFILE
TF_VAR_environment
TF_VAR_project_name
```

Secrets must still use approved secure injection.

---

## 60. Terraform Command Standards

Common commands:

```bash
terraform version
terraform init
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
terraform state list
terraform state show <resource>
terraform output
terraform providers
terraform workspace list
```

State commands must be used carefully in production.

---

## 61. Terraform State Modification

Commands such as:

```bash
terraform state rm
terraform state mv
terraform import
```

are high-impact operations.

They require review and must not be executed automatically by an agent without appropriate safeguards.

---

## 62. Terraform Import

Existing resources may be imported when infrastructure is being brought under Terraform management.

Example:

```bash
terraform import aws_vpc.main vpc-123456
```

After import, configuration must be created and validated so that Terraform accurately represents the resource.

---

## 63. Terraform Refactoring

Terraform refactoring must avoid accidental resource destruction.

Use appropriate Terraform mechanisms such as:

```text
moved blocks
```

when resource addresses change.

Example:

```hcl
moved {
  from = aws_instance.old
  to   = aws_instance.new
}
```

---

## 64. Terraform Testing

Terraform should be tested at multiple levels:

```text
Formatting
Validation
Security
Plan
Infrastructure Integration
Deployment Validation
```

Where applicable, infrastructure testing tools may validate generated resources.

---

## 65. Terraform Documentation

Modules should document:

* Purpose
* Inputs
* Outputs
* Dependencies
* Example usage
* Security assumptions
* Environment requirements

---

## 66. Terraform Code Review

Infrastructure changes must be reviewed like application code.

Reviewers should check:

* Resource changes
* IAM permissions
* Networking
* Security groups
* Encryption
* Cost impact
* Availability
* Data protection
* Destructive changes

---

## 67. Terraform Cost Awareness

Terraform changes must consider cloud cost.

Examples:

* NAT Gateways
* RDS
* ECS capacity
* Load Balancers
* CloudWatch
* Data transfer
* Large EC2 instances

Unexpected high-cost resources should require review.

---

## 68. Terraform Rollback

Terraform rollback should normally be performed by reverting the infrastructure code to a known-good version and applying the resulting plan.

For application deployment, rollback should generally use the previous immutable Docker image rather than recreating infrastructure.

---

## 69. Terraform Failure Handling

If Terraform fails, the Agent must report:

* Command
* Resource
* Error
* Root cause
* Severity
* Recommended fix
* State impact

Example:

```json
{
  "status": "failed",
  "stage": "terraform_apply",
  "resource": "aws_ecs_service.app",
  "severity": "high",
  "recommendation": "inspect ECS task health and deployment configuration"
}
```

---

## 70. Terraform Agent Input

Example:

```json
{
  "project_id": "project-123",
  "environment": "staging",
  "cloud": "aws",
  "region": "ap-south-1",
  "services": [
    "vpc",
    "ecr",
    "ecs",
    "rds",
    "cloudwatch"
  ],
  "deployment_method": "jenkins",
  "requirements": {
    "private_subnets": true,
    "encryption": true,
    "autoscaling": true,
    "monitoring": true
  }
}
```

---

## 71. Terraform Agent Output

Example:

```json
{
  "terraform_generated": true,
  "terraform_fmt": true,
  "terraform_validate": true,
  "security_scan": true,
  "plan_generated": true,
  "resources_to_add": 18,
  "resources_to_change": 2,
  "resources_to_destroy": 0,
  "status": "passed"
}
```

---

## 72. Terraform Agent Workflow

The Terraform Agent should follow:

```text
Receive Requirements
        ↓
Read Architecture
        ↓
Read Security Standards
        ↓
Read AWS Standards
        ↓
Analyze Existing Infrastructure
        ↓
Generate Terraform
        ↓
terraform fmt
        ↓
terraform validate
        ↓
Security Scan
        ↓
terraform plan
        ↓
Analyze Plan
        ↓
Check Destructive Changes
        ↓
Generate Report
        ↓
Approval
        ↓
terraform apply
        ↓
Validate Infrastructure
        ↓
Return Result
```

---

## 73. Terraform Agent Safety Rules

The Terraform Agent must not automatically execute high-risk operations such as:

```text
terraform destroy
terraform state rm
terraform state mv
```

without explicit authorization.

The Agent must detect unexpected destructive changes.

Example:

```text
Plan:
Add:     3
Change:  4
Destroy: 12
```

This should trigger a review/blocking gate unless the destruction is explicitly expected.

---

## 74. Terraform Validation Checklist

The Terraform Agent must validate:

### Configuration

* [ ] Terraform version defined
* [ ] Provider version defined
* [ ] Formatting passes
* [ ] Validation passes
* [ ] Variables typed
* [ ] Variables documented
* [ ] Modules structured correctly

### State

* [ ] Remote state configured
* [ ] State locking enabled
* [ ] State encrypted
* [ ] State access restricted
* [ ] State not committed to Git
* [ ] Lock file handled correctly

### Security

* [ ] No hardcoded secrets
* [ ] IAM least privilege
* [ ] Encryption enabled where required
* [ ] Security groups restricted
* [ ] Public access minimized
* [ ] Security scan passes

### Infrastructure

* [ ] Resource naming consistent
* [ ] Tags configured
* [ ] Environment separation exists
* [ ] Dependencies correct
* [ ] Health checks configured
* [ ] Monitoring configured
* [ ] Auto Scaling configured where required

### CI/CD

* [ ] `terraform fmt` passes
* [ ] `terraform validate` passes
* [ ] Security scan passes
* [ ] Terraform plan generated
* [ ] Plan reviewed
* [ ] Approval configured
* [ ] Apply controlled

---

## 75. Terraform Implementation Decision Matrix

| Situation            | Recommended Implementation                      | Avoid                                |
| -------------------- | ----------------------------------------------- | ------------------------------------ |
| Terraform state      | Encrypted remote S3 state                       | Local production state               |
| State locking        | Supported S3 locking                            | Concurrent unmanaged applies         |
| AWS authentication   | IAM role                                        | Long-lived access keys               |
| Provider version     | Controlled version                              | Uncontrolled latest                  |
| Infrastructure reuse | Terraform modules                               | Duplicated resources                 |
| Environments         | Separate state/configuration                    | Shared production/dev state          |
| Production apply     | Reviewed plan + approval                        | Uncontrolled auto-approve            |
| Secrets              | Secrets Manager/secure injection                | Hardcoded values                     |
| IAM                  | Least privilege                                 | `Action: *`                          |
| Network              | Private subnets where appropriate               | Unnecessary public workloads         |
| Database             | Encryption + backups + private access           | Public unsecured DB                  |
| ECR                  | Immutable tags + scan                           | Only `latest`                        |
| ECS                  | Health checks + controlled deployment           | No health validation                 |
| Scaling              | ECS Auto Scaling                                | Manual task management               |
| Security             | Checkov/tfsec/Trivy                             | No IaC scanning                      |
| Destructive change   | Explicit review                                 | Automatic destroy                    |
| Rollback             | Revert known-good IaC                           | Random manual changes                |
| Drift                | Scheduled plan/review                           | Ignoring drift                       |
| CI/CD                | fmt → validate → scan → plan → approval → apply | Direct apply                         |
| Agent execution      | Plan + safety gate                              | Unrestricted infrastructure mutation |

---

## 76. Terraform Acceptance Criteria

Terraform infrastructure is accepted only when:

1. Terraform version is controlled.
2. Providers are controlled.
3. Formatting passes.
4. Validation passes.
5. Security scanning passes.
6. Remote state is configured.
7. State locking is enabled.
8. State is encrypted.
9. State access is restricted.
10. No secrets are hardcoded.
11. IAM follows least privilege.
12. Required resources are correctly configured.
13. Required tags exist.
14. Environment separation is correct.
15. Auto Scaling is configured where required.
16. Monitoring is configured.
17. Terraform plan is generated.
18. Unexpected destructive changes are absent.
19. Required approval is obtained.
20. Apply succeeds.
21. Infrastructure health validation succeeds.
22. Deployment report is generated.

---

## 77. Terraform Production Quality Gate

Production infrastructure changes must be blocked when:

```text
terraform fmt Failed
        OR
terraform validate Failed
        OR
Security Scan Failed
        OR
Secrets Detected
        OR
Unexpected Destroy Detected
        OR
IAM Security Violation
        OR
Required Approval Missing
        OR
terraform apply Failed
        OR
Infrastructure Health Check Failed
```

---

## 78. Final Terraform Rule

The Agentic SDLC platform must never treat a successful `terraform apply` as sufficient evidence that infrastructure is production-ready.

Production infrastructure must pass:

```text
Terraform Code
      ↓
Format
      ↓
Validate
      ↓
Security Scan
      ↓
Plan
      ↓
Destructive Change Check
      ↓
Review
      ↓
Approval
      ↓
Apply
      ↓
Infrastructure Validation
      ↓
Monitoring Validation
      ↓
Production Ready
```

**Final Rule:**

> Every Terraform configuration generated or modified by the Agentic SDLC platform must be version-controlled, reproducible, securely state-managed, least-privilege, validated, security-scanned, plan-reviewed, and approval-gated before production infrastructure is changed.
