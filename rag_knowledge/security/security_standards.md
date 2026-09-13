# Security Standards

## 1. Purpose

This document defines application and security-engineering standards for the Agentic SDLC platform.

The Security Agent must use these standards when analyzing generated applications, code, dependencies, APIs, agents, tools, containers, cloud infrastructure, and deployment workflows.

The objective is to ensure that generated systems are:

* Secure
* Least-privilege
* Resilient against common attacks
* Safe for production deployment
* Auditable
* Compliant with company security requirements

---

# 2. Core Security Principles

All generated systems must follow:

* Defense in depth
* Least privilege
* Secure by default
* Zero trust
* Fail securely
* Explicit authorization
* Input validation
* Output validation
* Secrets protection
* Data minimization
* Continuous security testing

Security must be considered during design, development, testing, and deployment.

---

# 3. Zero Trust

Every request must be treated as untrusted until verified.

The system must not automatically trust:

* Users
* API clients
* Internal services
* Agents
* MCP servers
* Retrieved RAG content
* External APIs
* Uploaded files
* Generated code
* Cloud resources

Authentication and authorization must be explicitly verified.

---

# 4. Least Privilege

Every user, service, agent, tool, container, and AWS resource must receive only the permissions required for its task.

Avoid:

```text
AdministratorAccess
```

unless explicitly required and approved.

Prefer narrowly scoped permissions such as:

```text
ReadOnly
Specific API action
Specific S3 bucket
Specific ECR repository
Specific ECS service
```

---

# 5. Secure Defaults

Applications must use secure defaults.

Examples:

```text
Authentication enabled
Authorization required
HTTPS enabled
Secrets externalized
Debug disabled in production
Detailed errors disabled in production
CORS restricted
Rate limiting enabled where required
```

Security controls must not depend on developers remembering to enable them manually.

---

# 6. Authentication

Applications requiring user access must implement appropriate authentication.

Supported approaches may include:

* OAuth2
* OpenID Connect
* JWT
* API keys
* Service-to-service authentication

Authentication must verify:

* Identity
* Credential validity
* Token expiration
* Token signature
* Issuer
* Audience where applicable

Invalid credentials must be rejected.

---

# 7. Authorization

Authentication determines **who the user is**.

Authorization determines **what the user is allowed to do**.

Authorization must be enforced for protected operations.

Example:

```text
User A
  ↓
Authenticated
  ↓
Request project 123
  ↓
Check ownership/permission
  ↓
Allow or deny
```

Never rely only on frontend authorization.

Authorization must be enforced on the backend.

---

# 8. Role-Based Access Control

When multiple permission levels exist, use explicit roles.

Example:

```text
Admin
Developer
Tester
Viewer
```

Each role must have clearly defined permissions.

Avoid hardcoding authorization logic throughout application code.

---

# 9. Input Validation

All external input must be treated as untrusted.

Validate:

* Request bodies
* Query parameters
* Path parameters
* Headers
* Uploaded files
* URLs
* Configuration values
* Agent inputs
* Tool inputs
* LLM outputs

Use schema validation such as Pydantic for structured API inputs.

Reject invalid input early.

---

# 10. Output Validation

Generated or externally sourced output must also be validated.

Validate:

* LLM responses
* Agent outputs
* Tool responses
* RAG context
* External API responses
* Generated source code
* Generated configuration
* Generated infrastructure definitions

Never assume generated content is safe simply because it came from an internal agent.

---

# 11. SQL Injection Prevention

Never construct SQL queries using direct string interpolation.

Unsafe:

```python
query = f"SELECT * FROM users WHERE id = {user_id}"
```

Use:

* SQLAlchemy
* Parameterized queries
* ORM query builders

Example:

```python
user = db.query(User).filter(User.id == user_id).first()
```

All database inputs must be safely parameterized.

---

# 12. Command Injection Prevention

Never execute user-provided input directly as an operating-system command.

Unsafe:

```python
os.system(user_input)
```

Avoid:

```python
subprocess.run(user_input, shell=True)
```

When command execution is required:

* Use allowlists
* Avoid shell execution
* Validate arguments
* Restrict available commands
* Run inside a sandbox
* Apply resource limits
* Log execution

---

# 13. Agent Command Execution

Agentic SDLC agents may generate commands, but commands must not automatically execute with unrestricted host privileges.

Required flow:

```text
Agent
 ↓
Generate Command
 ↓
Validate Command
 ↓
Security Guardrail
 ↓
Sandbox
 ↓
Execute
 ↓
Validate Result
```

The agent must never receive unrestricted host access.

---

# 14. Path Traversal Prevention

Never allow user input to freely determine filesystem paths.

Unsafe:

```python
open("/app/files/" + user_input)
```

Validate and normalize paths.

Prevent access to:

```text
/etc
/root
/home
/proc
/sys
.env
private keys
credentials
application secrets
```

File operations should remain inside approved directories.

---

# 15. SSRF Prevention

Applications making outbound HTTP requests must protect against Server-Side Request Forgery.

Validate:

* URL scheme
* Hostname
* IP address
* Redirect destination
* Allowed domains

Block access to sensitive internal addresses such as:

```text
127.0.0.1
localhost
169.254.169.254
Private network ranges
Cloud metadata endpoints
```

Use domain allowlists whenever possible.

---

# 16. XSS Prevention

User-controlled content must not be rendered as executable HTML or JavaScript.

Use:

* Output encoding
* Safe templating
* Content Security Policy
* Framework-provided escaping

Never inject untrusted content directly into HTML.

---

# 17. CSRF Protection

State-changing browser requests must be protected against CSRF when cookie-based authentication is used.

Use appropriate:

* CSRF tokens
* SameSite cookies
* Origin validation
* Secure cookies

Stateless bearer-token APIs may use different protections depending on architecture.

---

# 18. API Security

APIs must implement:

* Authentication
* Authorization
* Input validation
* Rate limiting
* Request size limits
* Secure error handling
* HTTPS
* Request IDs
* Security logging

Sensitive endpoints must not expose unnecessary information.

---

# 19. Rate Limiting

Rate limiting must be applied to endpoints vulnerable to abuse.

Examples:

```text
Login
Password reset
LLM requests
Agent execution
File uploads
Project creation
Deployment
Webhook endpoints
```

Limits should consider:

* User
* IP
* API key
* Endpoint
* Resource

---

# 20. Secrets Management

Secrets must never be hardcoded in source code.

Never commit:

```text
API keys
AWS credentials
Passwords
JWT secrets
Private keys
Database passwords
LLM API keys
GitHub tokens
Jenkins credentials
```

Use:

* Environment variables
* AWS Secrets Manager
* AWS Systems Manager Parameter Store
* Jenkins Credentials
* Secret-management systems

Example:

```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

---

# 21. Environment Separation

Separate:

```text
Development
Testing
Staging
Production
```

Production credentials must never be used in development or testing.

Production databases must never be used for normal automated tests.

---

# 22. Sensitive Data Protection

Sensitive information must be protected during:

* Storage
* Processing
* Transmission
* Logging
* Backup

Avoid storing unnecessary sensitive information.

Use encryption where appropriate.

---

# 23. Encryption in Transit

External communication must use HTTPS/TLS.

Examples:

```text
Client → API
API → Database
API → Redis
Agent → LLM
Agent → MCP
Jenkins → AWS
Application → External API
```

Plaintext communication must not be used for production traffic.

---

# 24. Encryption at Rest

Sensitive stored information should use encryption at rest.

Examples:

* Database encryption
* S3 encryption
* EBS encryption
* Secrets Manager encryption
* Backup encryption

AWS-managed encryption keys or customer-managed keys should be selected according to security requirements.

---

# 25. Dependency Security

All dependencies must be reviewed for known vulnerabilities.

Use tools such as:

```bash
pip-audit
```

and appropriate package-security tooling.

Dependencies should:

* Be actively maintained
* Use supported versions
* Avoid unnecessary packages
* Be regularly updated
* Be scanned in CI/CD

Critical and High vulnerabilities must block production deployment unless explicitly approved.

---

# 26. Container Security

Docker images must:

* Use trusted base images
* Avoid unnecessary packages
* Avoid embedded secrets
* Run as non-root where possible
* Minimize image size
* Be vulnerability scanned
* Pin important dependencies

Example:

```dockerfile
USER appuser
```

Containers must not receive unnecessary host privileges.

---

# 27. AWS Security

AWS resources must follow least privilege.

Security controls include:

* IAM roles
* Security groups
* NACLs where required
* Encryption
* CloudTrail
* CloudWatch
* Secrets Manager
* S3 bucket policies
* ECR image scanning

Avoid storing AWS access keys directly inside application containers.

Prefer IAM roles for AWS workloads.

---

# 28. IAM Standards

IAM policies must grant only required permissions.

Avoid:

```text
Action: *
Resource: *
```

unless explicitly justified.

Prefer:

```text
Specific Action
Specific Resource
Specific Role
```

IAM credentials must never be committed to Git.

---

# 29. RAG Security

RAG-retrieved content must be treated as **untrusted data**.

Retrieved documents may contain:

* Malicious instructions
* Prompt injection
* Fake system instructions
* Sensitive information
* Incorrect information

The LLM must not automatically treat retrieved content as an authoritative instruction.

Required flow:

```text
User Query
 ↓
Retrieve Documents
 ↓
Security Filtering
 ↓
Trust Boundary
 ↓
LLM Context
 ↓
Validate Response
```

---

# 30. Prompt Injection Protection

Agentic systems must defend against prompt injection.

Potential injection sources include:

* User prompts
* RAG documents
* GitHub files
* README files
* Figma content
* External APIs
* MCP tool responses
* Generated code
* Web content

Instructions from retrieved or external content must not override system-level security rules.

---

# 31. LLM Security

LLM outputs must be considered probabilistic and potentially unsafe.

The application must validate:

* Structured output
* Tool calls
* Commands
* Code
* API parameters
* Deployment instructions

Never allow an LLM to directly perform unrestricted privileged operations.

---

# 32. Agent Security

Every agent must have:

* Explicit responsibilities
* Defined input schema
* Defined output schema
* Allowed tools
* Permission boundaries
* Validation rules
* Failure handling

Example:

```text
Security Agent
    ↓
Can inspect code
Can scan dependencies
Can analyze configuration
    ↓
Cannot directly modify production infrastructure
```

Agents must not automatically gain permissions beyond their role.

---

# 33. Tool Security

Tools must define explicit input and output schemas.

A tool should expose only required operations.

Example:

```text
GitHub Tool
 ├── read_repository
 ├── create_branch
 └── create_pull_request
```

Do not expose unrestricted shell access when a specific tool operation is sufficient.

---

# 34. MCP Security

MCP servers must be treated as security boundaries.

Validate:

* Tool identity
* Tool permissions
* Tool input
* Tool output
* Authentication
* Authorization

MCP tools must not automatically receive unrestricted access to:

```text
Filesystem
AWS
GitHub
Jenkins
Production infrastructure
```

---

# 35. Sandbox Security

Generated code and commands must execute inside controlled environments.

Sandbox controls should include:

* CPU limits
* Memory limits
* Execution timeout
* Filesystem isolation
* Network restrictions
* Process restrictions
* Non-root execution

The sandbox must be isolated from production infrastructure.

---

# 36. Generated Code Security

AI-generated code must undergo security validation before deployment.

Required checks include:

```text
Static analysis
Dependency scanning
Secret scanning
Security tests
Input validation
Authentication
Authorization
Injection protection
```

Generated code must not bypass security standards simply because it was produced by an agent.

---

# 37. Logging Security

Security-relevant events must be logged.

Examples:

```text
Authentication failure
Authorization failure
Admin actions
Agent execution
Tool execution
Deployment
Rollback
Security violations
Suspicious requests
```

Never log:

```text
Passwords
API keys
Access tokens
Private keys
Full secrets
Sensitive personal data
```

---

# 38. Audit Logging

Important security actions must be auditable.

Audit records should include:

```text
Timestamp
Request ID
Actor
Action
Resource
Result
Reason
```

For agentic workflows, also record:

```text
Agent
Tool
Operation
Execution status
```

---

# 39. Error Handling

Production errors must not expose:

* Stack traces
* Database credentials
* Internal paths
* Secrets
* Infrastructure details
* Sensitive configuration

Return safe errors to clients.

Detailed information should remain in protected logs.

---

# 40. Security Headers

Production APIs and web applications should configure appropriate security headers.

Depending on the application:

```text
Content-Security-Policy
Strict-Transport-Security
X-Content-Type-Options
X-Frame-Options
Referrer-Policy
```

Headers should be configured according to the application's actual requirements.

---

# 41. File Upload Security

Uploaded files must be validated for:

* File size
* Extension
* MIME type
* Content
* Filename
* Storage location

Do not trust the client-provided filename or MIME type.

Uploaded files should not automatically be executed.

---

# 42. Webhook Security

Webhook endpoints must validate incoming requests.

Use:

* Signature verification
* Authentication
* Timestamp validation
* Replay protection
* Request size limits

Never trust webhook payloads without verification.

---

# 43. Security Testing

Security testing must include:

```text
Authentication testing
Authorization testing
Input validation
SQL injection
Command injection
Path traversal
SSRF
XSS
CSRF where applicable
Dependency vulnerabilities
Secret detection
Container vulnerabilities
API security
Agent/tool permissions
Prompt injection
```

Critical security paths must have automated tests.

---

# 44. Security Scanning Commands

Recommended commands include:

```bash
pip-audit
bandit -r app/
```

Additional project-specific scanners may include:

```text
Secret scanning
Container image scanning
IaC scanning
SAST
DAST
```

Security scanning must run during CI/CD.

---

# 45. Vulnerability Severity

Security findings must be classified.

| Severity      | Action                     |
| ------------- | -------------------------- |
| Critical      | Deployment blocked         |
| High          | Deployment blocked         |
| Medium        | Security review required   |
| Low           | Track and remediate        |
| Informational | Document where appropriate |

Critical and High vulnerabilities must not be ignored.

---

# 46. Security Gates

The Security Agent must enforce security gates before deployment.

Minimum gates:

```text
No critical vulnerabilities
No high vulnerabilities
No exposed secrets
Authentication validated
Authorization validated
Security tests passed
Dependency scan passed
Container scan passed where applicable
Agent permissions validated
Tool permissions validated
```

---

# 47. Security Agent Input

The Security Agent should receive structured input.

Example:

```json
{
  "project_id": "project-123",
  "source_code": "...",
  "requirements": "...",
  "architecture": "...",
  "api_contract": "...",
  "dependencies": [],
  "dockerfile": "...",
  "terraform": "...",
  "agent_definitions": [],
  "tool_definitions": []
}
```

---

# 48. Security Agent Output

The Security Agent should return structured output.

Example:

```json
{
  "status": "passed",
  "critical_findings": 0,
  "high_findings": 0,
  "medium_findings": 2,
  "low_findings": 1,
  "secrets_detected": false,
  "dependency_scan_passed": true,
  "security_tests_passed": true,
  "deployment_allowed": true,
  "findings": []
}
```

---

# 49. Security Agent Workflow

The Security Agent should follow:

```text
Receive Project
      ↓
Analyze Requirements
      ↓
Analyze Architecture
      ↓
Analyze Source Code
      ↓
Analyze Dependencies
      ↓
Analyze APIs
      ↓
Analyze Docker
      ↓
Analyze Terraform
      ↓
Analyze Agents
      ↓
Analyze Tools / MCP
      ↓
Run Security Scans
      ↓
Run Security Tests
      ↓
Classify Vulnerabilities
      ↓
Apply Security Gates
      ↓
Generate Security Report
      ↓
Allow / Block Deployment
```

---

# 50. Security Validation Checklist

The Security Agent must verify:

* [ ] Authentication implemented correctly
* [ ] Authorization implemented correctly
* [ ] Inputs validated
* [ ] Outputs validated
* [ ] SQL injection prevented
* [ ] Command injection prevented
* [ ] Path traversal prevented
* [ ] SSRF protections implemented
* [ ] XSS protections implemented where applicable
* [ ] CSRF protections implemented where applicable
* [ ] Secrets are not hardcoded
* [ ] Dependencies scanned
* [ ] Docker image secured
* [ ] AWS IAM follows least privilege
* [ ] Encryption configured where required
* [ ] Security logging implemented
* [ ] Audit logging implemented where required
* [ ] Rate limiting configured where required
* [ ] File uploads secured
* [ ] Webhooks verified
* [ ] RAG content treated as untrusted
* [ ] Prompt injection protections implemented
* [ ] Agent permissions restricted
* [ ] MCP permissions restricted
* [ ] Tool inputs validated
* [ ] Sandbox configured
* [ ] Security tests pass
* [ ] Critical vulnerabilities = 0
* [ ] High vulnerabilities = 0
* [ ] Security report generated

---

# 51. Concrete Security Acceptance Criteria

The Security Agent must consider security validation successful only when:

1. No Critical vulnerabilities exist.
2. No High vulnerabilities exist.
3. No secrets are detected in source code or container images.
4. Authentication tests pass.
5. Authorization tests pass.
6. Injection tests pass.
7. Dependency security checks pass.
8. Required container security checks pass.
9. Required AWS/IAM security checks pass.
10. Agent permissions are restricted.
11. Tool and MCP permissions are restricted.
12. RAG content cannot override system security instructions.
13. Generated commands cannot execute outside the approved sandbox.
14. Security findings are classified and reported.
15. Deployment is blocked when mandatory security gates fail.

Example successful result:

```json
{
  "status": "passed",
  "critical": 0,
  "high": 0,
  "medium": 1,
  "low": 2,
  "secrets": 0,
  "deployment_allowed": true
}
```

---

# 52. Security Failure Handling

When a security gate fails, the Security Agent must:

```text
Detect
 ↓
Classify
 ↓
Record Evidence
 ↓
Identify Component
 ↓
Recommend Fix
 ↓
Block Deployment
```

The agent must never report security validation as successful when mandatory security gates fail.

---

# 53. Security Report

The Security Agent should produce a report containing:

```text
Project
Scan timestamp
Security status
Critical findings
High findings
Medium findings
Low findings
Secret detection result
Dependency scan result
Container scan result
Security test result
Agent/tool security result
Recommended fixes
Deployment decision
```

---

# 54. Final Security Rule

Every application, agent, tool, generated codebase, container, and deployment workflow must pass the required security validation before production deployment.

**No Critical vulnerabilities.
No High vulnerabilities.
No exposed secrets.
No unrestricted agent/tool access.
No unvalidated generated commands.
No security gate bypass.**

The Security Agent must block deployment whenever mandatory security requirements are not satisf