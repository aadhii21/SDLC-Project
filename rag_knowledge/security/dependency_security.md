# Dependency Security Standards

## 1. Purpose

This document defines security standards for third-party libraries, packages, frameworks, container dependencies, and other software components used by generated applications.

The Security Agent must verify that project dependencies are:

* Trusted
* Supported
* Vulnerability-free where required
* Properly versioned
* Minimal
* Reproducible
* Regularly scanned

---

# 2. Dependency Security Principles

All projects must follow:

* Use only required dependencies
* Prefer trusted and maintained packages
* Pin or constrain important dependencies
* Scan dependencies continuously
* Remove unused dependencies
* Patch known vulnerabilities
* Avoid abandoned packages
* Review dependency licenses where required
* Never bypass Critical or High vulnerabilities without approval

---

# 3. Approved Package Sources

Dependencies should come from trusted package registries.

For Python:

```text
PyPI
Private company package registry
Approved internal repositories
```

Avoid installing packages from unknown URLs or untrusted sources.

---

# 4. Minimal Dependencies

Applications should include only dependencies that are actually required.

Avoid unnecessary packages such as:

```text
Unused frameworks
Unused utilities
Duplicate libraries
Development-only packages in production
```

Fewer dependencies reduce the attack surface.

---

# 5. Dependency Version Standards

Dependencies should use controlled versions.

Example:

```text
fastapi>=0.115,<1.0
```

For production applications, dependency versions should be reproducible through a lock or pinned dependency strategy.

Avoid unrestricted versions such as:

```text
fastapi
```

when reproducible builds are required.

---

# 6. Requirements File Standards

Python projects should maintain dependency files such as:

```text
requirements.txt
requirements-dev.txt
```

or use a modern Python dependency-management approach through `pyproject.toml`.

Production dependencies must be separated from development-only dependencies where practical.

---

# 7. Dependency Locking

Production builds should use deterministic dependency resolution.

The same source revision should produce the same dependency set unless dependencies are intentionally updated.

Dependency locking helps prevent unexpected package upgrades.

---

# 8. Vulnerability Scanning

Dependency vulnerabilities must be scanned automatically.

For Python projects:

```bash
pip-audit
```

Example:

```bash
pip-audit -r requirements.txt
```

The scan should run locally and in CI/CD.

---

# 9. Bandit Security Scanning

Bandit should be used for Python source-code security analysis.

Example:

```bash
bandit -r app/
```

Dependency scanning and source-code security scanning are complementary and must not be treated as the same check.

---

# 10. Critical Vulnerabilities

Critical vulnerabilities must block production deployment.

Required action:

```text
Detect
 ↓
Identify dependency
 ↓
Identify vulnerable version
 ↓
Upgrade / replace
 ↓
Run tests
 ↓
Re-scan
 ↓
Approve deployment
```

---

# 11. High Vulnerabilities

High-severity vulnerabilities must normally block production deployment.

An exception requires explicit security approval and documented justification.

The Security Agent must not silently ignore High vulnerabilities.

---

# 12. Medium Vulnerabilities

Medium vulnerabilities must be:

* Recorded
* Evaluated
* Prioritized
* Assigned for remediation

Production deployment may continue only according to project security policy and approval requirements.

---

# 13. Low Vulnerabilities

Low-severity findings should be tracked and remediated during normal maintenance.

They should not be automatically ignored.

---

# 14. Vulnerability Exceptions

If a vulnerability cannot immediately be fixed, the project must document:

```text
Dependency
Version
CVE / advisory
Severity
Reason for exception
Compensating control
Owner
Expiration/review date
Approval
```

Exceptions must not become permanent security bypasses.

---

# 15. Dependency Updates

Dependencies should be updated regularly.

Update process:

```text
Check Updates
 ↓
Review Security Advisories
 ↓
Update Dependency
 ↓
Run Unit Tests
 ↓
Run Integration Tests
 ↓
Run Security Tests
 ↓
Run Dependency Scan
 ↓
Create PR
```

---

# 16. Breaking Dependency Updates

Major-version upgrades must be evaluated carefully.

Example:

```text
FastAPI 0.x → 1.x
Pydantic 2.x → 3.x
SQLAlchemy 2.x → 3.x
```

Before upgrading:

* Review release notes
* Review breaking changes
* Update code
* Run complete test suite
* Run security scans

---

# 17. Transitive Dependencies

Security analysis must include transitive dependencies.

Example:

```text
Application
    ↓
FastAPI
    ↓
Starlette
    ↓
Other dependency
```

A vulnerability in a transitive dependency can still affect the application.

The Security Agent must analyze the complete dependency tree where tooling supports it.

---

# 18. Dependency Conflicts

Dependency conflicts must be resolved explicitly.

Avoid forcing incompatible versions simply to make installation succeed.

Example:

```text
Package A requires X < 2
Package B requires X >= 3
```

The project must identify a compatible solution rather than bypassing dependency resolution.

---

# 19. Abandoned Packages

Avoid packages that:

* Are no longer maintained
* Have unresolved critical vulnerabilities
* Have no recent releases
* Have poor security history
* Have insufficient community or organizational support

The Security Agent should flag suspicious or abandoned dependencies for review.

---

# 20. Malicious Package Protection

Before adding a new dependency, evaluate:

* Package name
* Maintainer
* Repository
* Release history
* Download/community activity
* Known vulnerabilities
* Dependency behavior

Be especially careful with packages that closely resemble popular package names.

---

# 21. Dependency Typosquatting

Do not install packages solely because their names look similar to trusted packages.

Example:

```text
trusted-package
trusted_packag
trusted-package-new
```

Package names must be verified before installation.

---

# 22. Secret Detection

Dependencies and configuration files must not contain secrets.

Scan for:

```text
AWS keys
API keys
Tokens
Passwords
Private keys
Database credentials
LLM credentials
GitHub tokens
Jenkins credentials
```

Secrets must be stored through approved secret-management mechanisms.

---

# 23. License Security

Dependencies should be reviewed for licensing requirements.

The project should avoid dependencies whose licenses conflict with company or product requirements.

License compliance should be automated where required.

---

# 24. Development Dependencies

Development-only packages should not unnecessarily enter the production image.

Examples:

```text
pytest
ruff
mypy
bandit
debugging tools
```

Use separate dependency groups or multi-stage Docker builds where appropriate.

---

# 25. Production Dependency Isolation

Production environments should contain only required runtime dependencies.

Example:

```text
Development Environment
 ├── Application dependencies
 ├── Testing tools
 ├── Linting tools
 └── Debugging tools

Production Environment
 └── Runtime dependencies only
```

---

# 26. Docker Dependency Security

Docker builds must use controlled dependency installation.

Example:

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

The final image should not contain unnecessary package-management caches or development dependencies.

---

# 27. Base Image Security

Container base images must be:

* Trusted
* Supported
* Regularly updated
* Vulnerability scanned

Avoid obsolete operating-system images.

Example:

```text
python:3.12-slim
```

is generally preferable to an obsolete Python/OS image when compatible with the application.

---

# 28. Container Dependency Scanning

Container images must be scanned before deployment.

The scan should identify:

```text
OS vulnerabilities
Python vulnerabilities
System libraries
Known CVEs
Outdated packages
```

Deployment must be blocked according to the configured severity policy.

---

# 29. AWS Dependency Security

AWS SDK dependencies must be maintained and updated.

Examples:

```text
boto3
botocore
AWS CLI
AWS provider dependencies
```

AWS SDK versions should be reviewed for security advisories.

---

# 30. LLM and AI Dependencies

Agentic AI projects must scan AI-related dependencies.

Examples:

```text
langchain
langgraph
openai
anthropic
google-genai
qdrant-client
transformers
sentence-transformers
```

AI libraries can introduce security vulnerabilities just like normal application dependencies.

---

# 31. RAG Dependency Security

RAG systems must review dependencies related to:

```text
Embedding models
Vector databases
Document loaders
PDF parsers
File parsers
Web loaders
LLM SDKs
```

Document-processing libraries require particular attention because they process potentially untrusted content.

---

# 32. File Parser Security

Libraries processing uploaded documents must be security-reviewed.

Examples:

```text
PDF
DOCX
XLSX
CSV
HTML
XML
Images
Archives
```

Potential risks include:

* Malicious files
* Resource exhaustion
* Parser vulnerabilities
* Embedded payloads
* Path traversal

Uploaded files must be processed inside controlled environments where appropriate.

---

# 33. Dependency Security for Agents

Agents must not dynamically install arbitrary packages based on LLM-generated instructions.

Unsafe:

```text
User
 ↓
LLM
 ↓
pip install <arbitrary-package>
```

Package installation must require controlled validation and approved sources.

---

# 34. MCP Dependency Security

MCP servers and their dependencies must also be scanned.

Security validation should include:

```text
MCP server dependencies
Tool dependencies
Transport libraries
Authentication libraries
External SDKs
```

MCP should not be considered trusted merely because it is used internally.

---

# 35. Dependency Provenance

Where possible, dependency provenance should be traceable.

Record:

```text
Package
Version
Source
Checksum / lock information
Build timestamp
Application version
```

This helps reproduce and investigate production builds.

---

# 36. Software Bill of Materials

Production applications should generate an SBOM where required.

The SBOM should identify:

```text
Application
Direct dependencies
Transitive dependencies
Versions
Component identifiers
```

SBOM generation improves vulnerability tracking and supply-chain visibility.

---

# 37. Supply Chain Security

The complete software supply chain must be considered:

```text
Source Code
 ↓
Dependencies
 ↓
Build System
 ↓
Docker Image
 ↓
Container Registry
 ↓
Deployment
```

Each stage must have appropriate security controls.

---

# 38. CI/CD Dependency Security

Dependency checks must run before deployment.

Recommended sequence:

```bash
ruff check .
mypy .
pytest
pip-audit
bandit -r app/
```

Dependency vulnerabilities must be evaluated before the deployment stage.

---

# 39. Dependency Security Quality Gate

Minimum CI security gate:

```text
Dependency scan passed
AND
No Critical vulnerabilities
AND
No High vulnerabilities
AND
No exposed secrets
AND
Security tests passed
```

If the gate fails:

```text
Build → Failed
Deployment → Blocked
```

---

# 40. Dependency Security Commands

Recommended commands:

```bash
pip-audit
pip-audit -r requirements.txt
bandit -r app/
pip list --outdated
pip check
```

For Docker:

```bash
docker build -t application .
```

followed by the organization's approved container vulnerability scanner.

---

# 41. Dependency Review Process

Every new dependency should be evaluated before merging.

Review:

```text
Why is it needed?
Is there an existing dependency that provides the same functionality?
Is it maintained?
Does it have known vulnerabilities?
Does its license comply?
Does it increase attack surface?
Is it compatible with the project?
```

---

# 42. Dependency Update Process

Recommended workflow:

```text
Dependency Update Available
        ↓
Security / Compatibility Review
        ↓
Update Version
        ↓
Run Tests
        ↓
Run Security Scan
        ↓
Review Changes
        ↓
Merge
        ↓
Build Container
        ↓
Scan Container
        ↓
Deploy
```

---

# 43. Security Agent Dependency Input

The Security Agent should receive:

```json
{
  "requirements": [],
  "pyproject": {},
  "lock_file": {},
  "dockerfile": "",
  "application": "python-fastapi",
  "environment": "production"
}
```

---

# 44. Security Agent Dependency Output

Example:

```json
{
  "status": "passed",
  "total_dependencies": 42,
  "direct_dependencies": 18,
  "transitive_dependencies": 24,
  "critical": 0,
  "high": 0,
  "medium": 2,
  "low": 1,
  "outdated": 4,
  "secrets_detected": false,
  "deployment_allowed": true,
  "findings": []
}
```

---

# 45. Security Agent Dependency Workflow

The Security Agent should:

```text
Receive Dependency Manifest
        ↓
Identify Direct Dependencies
        ↓
Resolve Transitive Dependencies
        ↓
Check Versions
        ↓
Check Known Vulnerabilities
        ↓
Check Package Provenance
        ↓
Check Licenses
        ↓
Check Secrets
        ↓
Check Docker Dependencies
        ↓
Classify Findings
        ↓
Apply Security Gates
        ↓
Generate Report
```

---

# 46. Dependency Security Validation Checklist

The Security Agent must verify:

* [ ] Dependencies are required
* [ ] Versions are controlled
* [ ] Dependencies are from trusted sources
* [ ] Direct dependencies are scanned
* [ ] Transitive dependencies are scanned
* [ ] Known vulnerabilities are identified
* [ ] Critical vulnerabilities = 0
* [ ] High vulnerabilities = 0
* [ ] Unused dependencies are reviewed
* [ ] Abandoned packages are reviewed
* [ ] Typosquatting risks are considered
* [ ] Secrets are not embedded
* [ ] Licenses are acceptable
* [ ] Development dependencies are separated
* [ ] Docker dependencies are scanned
* [ ] Base image is supported
* [ ] AI dependencies are scanned
* [ ] RAG/file-parser dependencies are reviewed
* [ ] MCP dependencies are scanned
* [ ] Dependency provenance is traceable where required
* [ ] SBOM is generated where required
* [ ] CI/CD security checks pass

---

# 47. Concrete Dependency Security Acceptance Criteria

Dependency security passes only when:

1. All production dependencies are identified.
2. Direct and transitive dependencies are scanned.
3. No Critical vulnerabilities exist.
4. No High vulnerabilities exist.
5. No production secrets are detected.
6. Dependencies come from approved or trusted sources.
7. Production dependencies are separated from development dependencies where appropriate.
8. Container dependencies pass the configured security threshold.
9. Required AI/RAG/MCP dependencies are scanned.
10. Required license and provenance checks pass.
11. Security results are recorded.
12. The deployment decision is explicitly generated.

Successful result:

```json
{
  "status": "passed",
  "critical": 0,
  "high": 0,
  "secrets": 0,
  "security_scan": "passed",
  "deployment_allowed": true
}
```

---

# 48. Dependency Security Failure Handling

When a dependency security gate fails:

```text
Detect
 ↓
Identify Vulnerable Component
 ↓
Classify Severity
 ↓
Identify Safe Upgrade / Replacement
 ↓
Update Dependency
 ↓
Run Tests
 ↓
Re-scan
 ↓
Approve or Block Deployment
```

The Security Agent must not mark the project as secure while mandatory Critical or High findings remain unresolved.

---

# 49. Final Dependency Security Rule

Every production application generated by the Agentic SDLC platform must use controlled, trusted, scanned, and reproducible dependencies.

**No unapproved dependencies.
No unresolved Critical vulnerabilities.
No unresolved High vulnerabilities.
No embedded secrets.
No uncontrolled package installation.
No dependency-security gate bypass.**

The Security Agent must validate the complete software dependency supply chain before allowing production deployment.
