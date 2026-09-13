# Security Standards

## 1. General Security Principles

- Follow the principle of least privilege.
- Treat all user input as untrusted.
- Never trust AI-generated code or commands without validation.
- Apply security controls at every stage of the SDLC.
- Fail securely when validation or authorization fails.
- Do not expose sensitive information in logs, responses, prompts, or generated code.

## 2. Secrets Management

- Never hardcode passwords, API keys, tokens, private keys, or credentials.
- Store secrets using environment variables or an approved secret manager.
- Never commit `.env` files containing real secrets.
- Never commit `.pem`, `.key`, credential, or certificate files containing private information.
- Use `.env.example` with placeholder values only.
- Rotate compromised or exposed credentials immediately.

### Bad

```python
API_KEY = "real-secret-key"
Good
API_KEY = os.getenv("API_KEY")
3. Authentication
All protected APIs must require authentication.
Use secure authentication mechanisms such as OAuth2 or JWT where appropriate.
Validate token expiration.
Validate token signatures.
Do not accept expired or malformed tokens.
Never store passwords in plain text.
Use strong password hashing algorithms when password authentication is required.
4. Authorization
Authentication determines who the user is.
Authorization determines what the user is allowed to do.
Check authorization before sensitive operations.
Follow role-based or permission-based access control where required.
Never rely only on frontend authorization checks.

Example:

Request
   ↓
Authentication
   ↓
Authorization
   ↓
Permission Check
   ↓
Operation
5. Input Validation
Validate all external input.
Use Pydantic models for FastAPI request validation.
Validate file types and file sizes.
Validate URLs before external requests.
Reject unexpected or malformed input.
Never directly execute user-provided commands.

Example:

class ProjectRequest(BaseModel):
    project_name: str
    description: str
6. Injection Prevention

Protect against:

SQL Injection
Command Injection
Prompt Injection
Code Injection
XSS
Path Traversal
Template Injection

Use parameterized queries instead of dynamically constructed SQL.

Never execute arbitrary user input:

os.system(user_input)
7. AI / LLM Security

AI-generated output must be considered untrusted.

Validate LLM-generated code before execution.
Never allow an LLM to directly execute arbitrary system commands.
Apply tool-level authorization.
Restrict tools to required permissions.
Use allowlists for sensitive operations.
Protect system prompts and confidential context.
Prevent prompt injection from overriding security policies.
Sanitize retrieved RAG content before using it in sensitive workflows.
8. Agent Tool Security

Every tool should have clearly defined permissions.

Example:

Agent
  ↓
Tool Authorization
  ↓
Input Validation
  ↓
Tool Execution
  ↓
Output Validation

Sensitive tools such as deployment, infrastructure modification, and credential management require additional validation.

9. Code Execution Security

AI-generated code must not be executed directly on the host system.

Use an isolated execution environment such as:

Docker sandbox
Restricted container
Dedicated execution environment

Apply:

CPU limits
Memory limits
Execution timeouts
Network restrictions
Filesystem restrictions
Process restrictions
10. API Security
Use HTTPS in production.
Validate request payloads.
Implement authentication and authorization.
Apply rate limiting where appropriate.
Configure appropriate CORS policies.
Do not expose internal stack traces.
Return safe error messages.
Use appropriate HTTP methods and status codes.
11. Database Security
Use least-privilege database accounts.
Never expose database credentials.
Use parameterized queries.
Encrypt sensitive data where required.
Restrict database network access.
Avoid exposing databases directly to the public internet.
Use secure database connections in production.
12. AWS Security
Follow AWS least-privilege IAM policies.
Avoid using the AWS root account for application operations.
Do not hardcode AWS access keys.
Prefer IAM roles for AWS workloads.
Restrict security groups to required ports.
Keep S3 buckets private unless public access is explicitly required.
Enable encryption for sensitive resources.
Monitor AWS activity using appropriate logging and monitoring services.
13. Docker Security
Use trusted base images.
Keep base images updated.
Do not store secrets inside Docker images.
Run containers as non-root users where possible.
Minimize installed packages.
Scan images for vulnerabilities.
Do not expose unnecessary ports.
14. Dependency Security
Use trusted package repositories.
Pin dependency versions where appropriate.
Regularly scan dependencies for known vulnerabilities.
Remove unused dependencies.
Update vulnerable dependencies.
Review new dependencies before adding them.
15. Logging and Monitoring
Log security-relevant events.
Do not log passwords, tokens, API keys, or private keys.
Use appropriate log levels.
Monitor authentication failures.
Monitor unauthorized access attempts.
Monitor suspicious agent/tool activity.
Monitor deployment failures and security violations.
16. Error Handling

Never expose internal implementation details to users.

Bad
DatabaseError: password authentication failed for user admin
Good
An internal error occurred. Please try again later.

Detailed technical information should remain in secure internal logs.

17. File Upload Security
Validate file extensions.
Validate MIME types.
Limit file size.
Store uploaded files outside executable directories.
Generate safe filenames.
Prevent path traversal.
Scan uploaded files when required.
Never execute uploaded files automatically.
18. Network Security
Use HTTPS/TLS for external communication.
Restrict inbound and outbound network access.
Expose only required ports.
Use private networking for internal services where possible.
Do not expose internal databases, vector databases, or infrastructure services unnecessarily.
19. RAG Security

RAG data may contain confidential company information.

Apply access control to knowledge sources.
Store document metadata.
Prevent unauthorized retrieval.
Do not expose confidential documents to unauthorized users or agents.
Validate retrieved content before using it for sensitive actions.
Separate public and confidential knowledge where required.
20. CI/CD Security

The CI/CD pipeline must:

Protect Jenkins credentials.
Use secure credential storage.
Scan dependencies.
Run security checks.
Scan Docker images.
Prevent secrets from appearing in build logs.
Restrict deployment permissions.
Require approval for sensitive production deployments where appropriate.
21. Infrastructure Security

Infrastructure changes must:

Be managed through Terraform or approved IaC.
Follow least privilege.
Avoid publicly exposed resources unless required.
Use secure security-group rules.
Protect Terraform state.
Never store secrets in Terraform source code.
Review infrastructure changes before production deployment.
22. Production Deployment Security

Production deployments must pass:

Code Validation
      ↓
Testing
      ↓
Security Scan
      ↓
Dependency Scan
      ↓
Container Scan
      ↓
Approval / Policy Check
      ↓
Production Deployment

A failed security check must block deployment.

23. AI-Generated Application Security

Every AI-generated application must be checked for:

Hardcoded secrets
Insecure dependencies
SQL injection
Command injection
Authentication weaknesses
Authorization weaknesses
Unsafe file handling
Insecure APIs
Exposed credentials
Vulnerable Docker configuration
Unsafe infrastructure configuration
24. Security Incident Handling

When a security issue is detected:

Stop or block the affected operation.
Record the security event.
Identify the affected resource.
Revoke or rotate compromised credentials.
Fix the vulnerability.
Re-run security validation.
Deploy the corrected version only after validation.
25. Security Checklist

Before production deployment:

 No hardcoded secrets.
 Authentication is implemented where required.
 Authorization is implemented.
 Input validation is implemented.
 Injection vulnerabilities are checked.
 Dependencies are scanned.
 Docker image is scanned.
 AWS permissions follow least privilege.
 Sensitive data is protected.
 Logs do not contain secrets.
 RAG access is controlled.
 AI-generated code is validated.
 Production deployment security checks pass.
26. Agentic SDLC Security Rule

No AI agent should be allowed to bypass security controls.

Sensitive operations such as:

Production deployment
Infrastructure modification
Database modification
Credential operations
Destructive operations

must require appropriate authorization, validation, and guardrails before execution.