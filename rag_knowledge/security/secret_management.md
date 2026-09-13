# Secret Management Standards

## 1. Purpose

This document defines standards for securely creating, storing, accessing, rotating, auditing, and removing secrets used by applications, agents, tools, CI/CD pipelines, containers, and cloud infrastructure.

The Security Agent must verify that secrets are never unnecessarily exposed in source code, logs, containers, repositories, prompts, agent state, or deployment artifacts.

---

# 2. What Is a Secret?

Secrets include any sensitive value that can provide authentication, authorization, or privileged access.

Examples:

```text
API keys
Passwords
AWS access keys
AWS secret keys
Database credentials
JWT signing secrets
OAuth client secrets
GitHub tokens
Jenkins credentials
LLM API keys
Private SSH keys
TLS private keys
Webhook signing secrets
Encryption keys
Cloud credentials
```

---

# 3. Core Secret Management Principles

All systems must follow:

* Never hardcode secrets
* Never commit secrets to Git
* Never expose secrets in API responses
* Never log secrets
* Never place secrets in Docker images
* Use centralized secret management
* Apply least privilege
* Rotate secrets regularly
* Revoke compromised secrets immediately
* Separate secrets by environment

---

# 4. Never Hardcode Secrets

Unsafe:

```python
OPENAI_API_KEY = "sk-xxxxxxxx"
```

Unsafe:

```python
DATABASE_PASSWORD = "MyPassword123"
```

Secrets must never be embedded directly in source code.

Use environment variables or an approved secret-management system.

---

# 5. Environment Variables

Environment variables may be used for application configuration and secrets when appropriate.

Example:

```python
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

Do not commit actual secret values.

Use:

```text
.env.example
```

to document required variables without containing real secrets.

Example:

```text
OPENAI_API_KEY=
DATABASE_URL=
JWT_SECRET=
```

---

# 6. `.env` File Standards

Local `.env` files containing real secrets must not be committed.

Add:

```text
.env
.env.*
```

to `.gitignore` where appropriate.

Keep:

```text
.env.example
```

in the repository with placeholder values.

---

# 7. AWS Secrets Manager

Production applications should use AWS Secrets Manager when centralized secret storage is required.

Example architecture:

```text
ECS Task
   ↓
IAM Role
   ↓
AWS Secrets Manager
   ↓
Secret
   ↓
Application
```

The application should retrieve only the secrets it requires.

---

# 8. AWS Systems Manager Parameter Store

AWS Systems Manager Parameter Store may be used for configuration and secrets according to project requirements.

Sensitive values should use appropriate encryption such as:

```text
SecureString
```

Access must be controlled using IAM.

---

# 9. IAM-Based Secret Access

Applications running on AWS should prefer IAM roles over static AWS credentials.

Avoid storing:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

inside application source code or Docker images.

Prefer:

```text
ECS Task Role
EC2 Instance Role
Lambda Execution Role
```

where applicable.

---

# 10. Least-Privilege Secret Access

An application should have access only to the secrets it actually requires.

Example:

```text
Backend Service
    ↓
Can read:
    /prod/backend/database
    /prod/backend/openai

Cannot read:
    /prod/payment
    /prod/admin
    /prod/other-service
```

IAM policies must restrict access by resource.

---

# 11. Environment Separation

Secrets must be separated between:

```text
Development
Testing
Staging
Production
```

Example:

```text
/dev/database
/staging/database
/prod/database
```

Production secrets must never be reused in development or testing.

---

# 12. Secret Naming

Secret names should be predictable and environment-aware.

Example:

```text
/prod/agentic-sdlc/database
/prod/agentic-sdlc/openai
/prod/agentic-sdlc/github
/prod/agentic-sdlc/jenkins
```

Avoid ambiguous names such as:

```text
/mysecret
/password
/key
```

---

# 13. Secret Injection

Secrets should be injected at runtime rather than stored inside application code.

Example:

```text
Docker Image
    ↓
ECS Task Definition
    ↓
Secrets Manager
    ↓
Container Runtime
    ↓
Application
```

The Docker image itself must remain free of secrets.

---

# 14. Docker Secret Standards

Never include secrets in:

```dockerfile
ENV API_KEY="secret"
```

Never use:

```dockerfile
COPY .env /app/.env
```

Do not pass secrets through Docker build arguments unless the build system specifically supports secure secret handling.

---

# 15. Git Security

Secrets must never be committed to Git.

Examples of prohibited files:

```text
.env
credentials.json
aws_credentials
private_key.pem
id_rsa
service-account.json
```

Use `.gitignore` and secret-scanning tools.

---

# 16. Secret Scanning

Repositories must be scanned for exposed secrets.

Secret scanning should detect:

```text
API keys
AWS credentials
GitHub tokens
Private keys
Passwords
JWT secrets
Database credentials
Cloud tokens
```

Secret scanning should run:

```text
Pre-commit
CI/CD
Pull Request
Repository monitoring
```

where supported.

---

# 17. Exposed Secret Response

If a secret is accidentally committed:

```text
Detect
 ↓
Revoke
 ↓
Rotate
 ↓
Remove from source
 ↓
Clean repository history where required
 ↓
Scan again
 ↓
Audit usage
```

Deleting the file from the latest commit is not sufficient if the secret exists in Git history.

---

# 18. Secret Rotation

Secrets must be rotated according to organizational policy and risk.

Rotation should be performed after:

* Credential exposure
* Employee/service ownership changes
* Security incidents
* Suspected compromise
* Credential expiration
* Scheduled rotation period

---

# 19. Automatic Rotation

Where supported, automate secret rotation.

Example:

```text
Secret
 ↓
Rotation Trigger
 ↓
Generate New Credential
 ↓
Update Secret Store
 ↓
Update Application Access
 ↓
Validate
 ↓
Revoke Old Credential
```

Applications should support credential rotation without unnecessary downtime where possible.

---

# 20. Secret Expiration

Secrets with expiration requirements must be tracked.

The system should identify:

```text
Secret
Created At
Last Rotated
Expiration
Owner
Environment
```

Expired secrets must not remain active unnecessarily.

---

# 21. Secret Ownership

Every production secret should have an identifiable owner or owning service.

Example:

```text
Secret:
 /prod/backend/database

Owner:
 Backend Service

Environment:
 Production

Purpose:
 PostgreSQL connection
```

---

# 22. Secret Access Auditing

Access to sensitive secrets should be auditable.

Audit information should include:

```text
Timestamp
Actor
Service
Secret identifier
Operation
Success/failure
Environment
```

Never store the secret value itself in audit logs.

---

# 23. Logging Restrictions

Never log:

```python
logger.info("API key: %s", api_key)
```

Never log:

```python
logger.info("Authorization: %s", authorization_header)
```

Never log:

```text
Database password
JWT token
AWS secret key
Private key
LLM API key
```

---

# 24. Error Message Restrictions

Errors must not expose secret values.

Unsafe:

```text
Database connection failed:
postgres://user:password@host/db
```

Safe:

```text
Database connection failed
```

Detailed diagnostics should remain protected in server-side logs, with secrets redacted.

---

# 25. Secret Redaction

Applications should redact sensitive values before logging.

Example:

```text
sk-xxxxxxxxxxxxxxxx
```

may be represented as:

```text
sk-********
```

Prefer complete removal of secret values from logs rather than partial masking when possible.

---

# 26. API Response Security

Secrets must never be returned through normal API responses.

Do not expose:

```json
{
  "api_key": "...",
  "database_password": "...",
  "aws_secret": "..."
}
```

Use response schemas that explicitly exclude sensitive fields.

---

# 27. Agent State Security

Agent state must not unnecessarily contain secrets.

Avoid storing:

```text
API keys
Passwords
Access tokens
Private keys
Database credentials
```

inside LangGraph checkpoints, Redis state, databases, or persistent memory.

If secret references are required, store a secure identifier rather than the secret value.

---

# 28. LLM Secret Protection

Secrets must never be sent to an LLM unless explicitly required and approved.

Before sending context to an LLM:

```text
Application Data
 ↓
Secret Detection
 ↓
Redaction
 ↓
LLM Context
```

API keys, passwords, tokens, and credentials must be removed from prompts.

---

# 29. RAG Secret Protection

Documents ingested into the RAG knowledge base must be scanned for secrets.

Do not embed documents containing:

```text
API keys
Passwords
Private keys
Production credentials
Access tokens
```

unless there is an explicitly approved secure use case.

Secrets must never become retrievable through RAG.

---

# 30. Prompt Protection

System prompts and agent instructions must not contain unnecessary credentials.

Avoid:

```text
SYSTEM_PROMPT = """
Use this API key:
sk-xxxxxxxx
"""
```

Agents should access authorized tools through secure runtime mechanisms instead.

---

# 31. MCP Secret Security

MCP servers must not expose secrets directly to the LLM.

Prefer:

```text
LLM
 ↓
MCP Tool
 ↓
Secure Credential Store
 ↓
External Service
```

instead of:

```text
LLM
 ↓
Secret
 ↓
External Service
```

The tool should perform the authenticated operation without revealing the credential to the model.

---

# 32. GitHub Token Security

GitHub credentials must be stored using approved secret-management systems.

Never place GitHub tokens in:

```text
Source code
README
Git history
Agent prompts
RAG documents
Logs
Docker images
```

The GitHub MCP/tool should use controlled authentication.

---

# 33. Jenkins Credential Security

Jenkins credentials must be stored using Jenkins Credentials or an approved external secret-management mechanism.

Never hardcode credentials inside:

```text
Jenkinsfile
Shell scripts
Git repositories
Dockerfiles
Terraform files
```

Use Jenkins credential binding where appropriate.

---

# 34. Terraform Secret Security

Terraform configurations must not hardcode credentials.

Unsafe:

```hcl
password = "MySecretPassword"
```

Use:

```text
AWS Secrets Manager
SSM Parameter Store
Environment variables
Terraform sensitive variables
Approved secret-management integrations
```

Terraform state must also be treated as sensitive because it may contain secret values.

---

# 35. Terraform State Security

Terraform state must be:

* Stored securely
* Encrypted
* Access controlled
* Version controlled appropriately
* Protected from public access

Do not commit:

```text
terraform.tfstate
terraform.tfstate.backup
```

to Git.

---

# 36. CI/CD Secret Security

CI/CD pipelines must retrieve secrets securely.

Example:

```text
Jenkins
 ↓
Credential Store
 ↓
Temporary Credential
 ↓
Build / Deploy
 ↓
Credential Removed
```

Secrets must not appear in build logs.

---

# 37. Build Log Protection

CI/CD logs must be checked for accidental secret exposure.

Avoid commands that print environment variables:

```bash
env
printenv
set
```

when the environment contains secrets.

Use secret masking mechanisms provided by the CI/CD system.

---

# 38. Secret Security in Generated Projects

The Backend Agent, Frontend Agent, DevOps Agent, and Deployment Agent must never generate hardcoded secrets.

Generated configuration should contain placeholders.

Example:

```text
DATABASE_URL=${DATABASE_URL}
OPENAI_API_KEY=${OPENAI_API_KEY}
```

not actual credentials.

---

# 39. Secret Detection in Agentic SDLC

The workflow should include secret detection before deployment:

```text
Code Generation
      ↓
Secret Scan
      ↓
Dependency Scan
      ↓
Security Testing
      ↓
Docker Build
      ↓
Container Scan
      ↓
Deployment
```

If secrets are detected, deployment must be blocked.

---

# 40. Secret Access During Agent Execution

Agents should receive only the credentials required for the current operation.

Example:

```text
GitHub Agent
    ↓
GitHub credential only

AWS Deployment Agent
    ↓
AWS deployment role only

Jenkins Agent
    ↓
Jenkins credential only
```

Do not provide every agent with all platform credentials.

---

# 41. Temporary Credentials

Prefer short-lived credentials when supported.

Examples:

```text
AWS STS credentials
Temporary GitHub tokens
Short-lived OAuth tokens
Ephemeral CI/CD credentials
```

Temporary credentials reduce the impact of credential leakage.

---

# 42. Private Key Security

Private keys must:

* Never be committed
* Never be logged
* Never be sent to LLMs
* Have restricted filesystem permissions
* Be stored securely
* Be rotated when compromised

Example:

```bash
chmod 600 private_key.pem
```

---

# 43. Secret File Permissions

Files containing secrets must have restrictive permissions.

Example:

```bash
chmod 600 .env
```

Only the required application user should be able to read secret files.

---

# 44. Secret Backup Security

Secret backups must have the same or stronger protection as active secrets.

Do not store secret backups in:

```text
Public S3 buckets
Git repositories
Unencrypted local files
Shared drives
Unprotected databases
```

---

# 45. Production Secret Access

Production secrets must be accessible only to authorized production workloads and operators.

Developers should not receive unnecessary production credentials.

Prefer:

```text
Developer
   ↓
Development Secret

Production Application
   ↓
Production Secret
```

---

# 46. Secret Incident Response

If a secret is compromised:

```text
1. Detect
2. Identify affected credential
3. Revoke credential
4. Rotate credential
5. Identify affected systems
6. Review access logs
7. Remove exposure
8. Scan repository/history
9. Validate replacement credential
10. Document incident
```

The compromised credential must be considered unsafe even if the exposed value is later removed from the repository.

---

# 47. Secret Security Quality Gates

Production deployment must be blocked when:

```text
Secret detected in source code
OR
Secret detected in Docker image
OR
Secret detected in RAG documents
OR
Secret exposed in CI logs
OR
Required secret is missing
OR
Unauthorized secret access detected
```

---

# 48. Security Agent Secret Input

The Security Agent should receive:

```json
{
  "project_id": "project-123",
  "source_code": "...",
  "dockerfile": "...",
  "terraform": "...",
  "ci_config": "...",
  "rag_documents": [],
  "agent_definitions": [],
  "tool_definitions": []
}
```

The agent should scan these inputs without exposing detected secret values in its output.

---

# 49. Security Agent Secret Output

Example:

```json
{
  "status": "passed",
  "secrets_detected": false,
  "source_scan": "passed",
  "docker_scan": "passed",
  "rag_scan": "passed",
  "ci_scan": "passed",
  "secret_access_policy": "passed",
  "deployment_allowed": true,
  "findings": []
}
```

If a secret is detected:

```json
{
  "status": "failed",
  "secrets_detected": true,
  "deployment_allowed": false,
  "findings": [
    {
      "type": "potential_api_key",
      "location": "config/settings.py",
      "severity": "critical"
    }
  ]
}
```

The actual secret value must never be included in the report.

---

# 50. Security Agent Secret Workflow

The Security Agent should follow:

```text
Receive Project
      ↓
Scan Source Code
      ↓
Scan Configuration
      ↓
Scan Git Files
      ↓
Scan Docker Configuration
      ↓
Scan Terraform
      ↓
Scan CI/CD Configuration
      ↓
Scan RAG Documents
      ↓
Scan Agent Definitions
      ↓
Scan Tool/MCP Configuration
      ↓
Classify Potential Secrets
      ↓
Redact Secret Values
      ↓
Apply Security Gate
      ↓
Generate Report
      ↓
Allow / Block Deployment
```

---

# 51. Secret Validation Checklist

The Security Agent must verify:

* [ ] No hardcoded secrets
* [ ] `.env` is not committed
* [ ] `.env.example` contains placeholders only
* [ ] Production secrets use approved secret management
* [ ] AWS workloads use IAM roles where appropriate
* [ ] IAM permissions follow least privilege
* [ ] Secrets are separated by environment
* [ ] Secrets are not stored in Docker images
* [ ] Secrets are not stored in Terraform configuration
* [ ] Terraform state is protected
* [ ] CI/CD credentials are protected
* [ ] Build logs do not expose secrets
* [ ] Secrets are not returned in API responses
* [ ] Secrets are not stored unnecessarily in agent state
* [ ] Secrets are not sent to LLMs
* [ ] RAG documents are scanned
* [ ] MCP tools do not expose credentials to LLMs
* [ ] GitHub credentials are protected
* [ ] Jenkins credentials are protected
* [ ] Private keys are protected
* [ ] Temporary credentials are used where possible
* [ ] Secret rotation is supported
* [ ] Secret access is auditable
* [ ] Incident response process exists
* [ ] Secret scanning passes
* [ ] No Critical secret exposure exists

---

# 52. Secret Management Implementation Decision Matrix

The Security Agent should use the following decision matrix when determining how a secret must be implemented.

| Situation                                     | Recommended Implementation                            | Avoid                              | Environment        |
| --------------------------------------------- | ----------------------------------------------------- | ---------------------------------- | ------------------ |
| Local development                             | `.env` + `.gitignore`                                 | Committing `.env`                  | Development        |
| Local development with team-shared secrets    | Approved developer secret manager                     | Sharing secrets through chat/files | Development        |
| FastAPI application on ECS                    | AWS Secrets Manager + ECS task secret injection       | Hardcoded credentials              | Production         |
| AWS service-to-service access                 | IAM Task/Execution Role                               | Static AWS access keys             | Production         |
| CI/CD Jenkins credentials                     | Jenkins Credentials                                   | Hardcoding in Jenkinsfile          | CI/CD              |
| Jenkins accessing AWS                         | IAM role / approved short-lived credentials           | Long-lived AWS keys in Jenkinsfile | CI/CD              |
| Terraform variables containing sensitive data | Secure variable injection / secret manager            | Hardcoded values in `.tf`          | All                |
| Terraform state                               | Encrypted remote backend + restricted access          | Committing `terraform.tfstate`     | All                |
| Database password                             | AWS Secrets Manager / approved secret store           | Source code or Dockerfile          | Staging/Production |
| LLM API key                                   | Secret manager → runtime environment/tool             | Prompt, source code, Git           | All                |
| GitHub authentication                         | Secure CI/CD credential or controlled tool credential | Token in agent prompt              | All                |
| MCP authentication                            | MCP server/tool retrieves credential securely         | Exposing credential to LLM         | All                |
| Agent execution                               | Tool-specific temporary credential                    | Giving agent all credentials       | All                |
| RAG documents                                 | Secret scan before ingestion                          | Storing credentials in vector DB   | All                |
| Docker build                                  | Secure build secret mechanism only when required      | `ENV`, `ARG`, or copied `.env`     | Build              |
| Production application                        | Centralized secret manager                            | Developer machine secrets          | Production         |
| Temporary privileged operation                | Short-lived credential                                | Permanent admin credential         | All                |
| Credential compromise                         | Revoke + rotate immediately                           | Only deleting the exposed file     | All                |

### Decision Rules

Use these rules when selecting an implementation:

```text
If production AWS workload
        ↓
Prefer AWS Secrets Manager / IAM Role

If CI/CD credential
        ↓
Use Jenkins Credentials or approved secret manager

If AWS service authentication
        ↓
Prefer IAM Role / temporary credentials

If local development
        ↓
Use .env locally + .gitignore

If secret must be shared across services
        ↓
Use centralized secret manager

If LLM or Agent needs authenticated tool access
        ↓
Tool retrieves secret; do NOT expose secret to LLM

If RAG document contains a secret
        ↓
Block ingestion and remove/redact secret

If secret is committed to Git
        ↓
Revoke → Rotate → Remove exposure → Re-scan

If no secure implementation is available
        ↓
Block production deployment
```

The Security Agent must choose the least-privileged and most secure implementation that satisfies the application's actual requirement.

---

# 53. Concrete Secret Security Acceptance Criteria

Secret management passes only when:

1. No hardcoded production secrets exist.
2. No secrets are committed to Git.
3. No secrets are present in Docker images.
4. No secrets are exposed in CI/CD logs.
5. No secrets are present in RAG knowledge where prohibited.
6. No secrets are unnecessarily included in agent state.
7. LLM prompts do not contain credentials.
8. MCP tools do not expose credentials to the LLM.
9. Production workloads use approved secret-management mechanisms.
10. Secret access follows least privilege.
11. Required rotation and expiration policies are satisfied.
12. Secret scanning passes.
13. The security report contains no actual secret values.
14. Deployment is blocked when Critical secret exposure is detected.

Successful result:

```json
{
  "status": "passed",
  "secrets_detected": false,
  "secret_scan": "passed",
  "deployment_allowed": true
}
```

---

# 54. Final Secret Management Rule

Secrets must remain outside source code, generated code, Docker images, Git history, logs, API responses, LLM prompts, RAG content, and unnecessary agent state.

**Use secure storage.
Use least privilege.
Use short-lived credentials where possible.
Rotate compromised credentials immediately.
Never expose secret values in reports.
Block deployment when secrets are exposed.**

The Security Agent must verify secret protection across the complete Agentic SDLC pipeline before production deployment.
