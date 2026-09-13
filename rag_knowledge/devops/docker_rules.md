# Docker Rules

## 1. Purpose

This document defines Docker standards for the Agentic SDLC platform.

Docker must be used to create reproducible, secure, portable, and production-ready application containers.

Generated projects must follow these standards before they are allowed to proceed to CI/CD and deployment.

---

# 2. Docker Standards Summary

Docker implementations must be:

* Reproducible
* Secure
* Minimal
* Immutable
* Non-root
* Health-checkable
* Resource-aware
* Environment-independent
* CI/CD compatible
* Production-ready

The Docker Agent must validate the generated Docker configuration against these standards.

---

# 3. Supported Docker Standards

The platform should use a currently supported Docker Engine and BuildKit-enabled build environment.

Dockerfiles must use modern Dockerfile syntax and avoid deprecated instructions or patterns.

Example:

```dockerfile
# syntax=docker/dockerfile:1
```

---

# 4. Dockerfile Naming

The standard Dockerfile name is:

```text
Dockerfile
```

Additional Dockerfiles may be used when multiple environments require different images.

Examples:

```text
Dockerfile
Dockerfile.dev
Dockerfile.test
Dockerfile.prod
```

Production builds must use an explicitly identified production Dockerfile when multiple Dockerfiles exist.

---

# 5. Dockerfile Structure

Dockerfiles should generally follow this order:

```text
Base Image
↓
Environment Configuration
↓
System Dependencies
↓
Application Dependencies
↓
Application Files
↓
User Configuration
↓
Health Check
↓
Entrypoint / Command
```

Example:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN useradd --create-home appuser

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

# 6. Base Image Standards

Base images must:

* Come from trusted registries
* Use actively supported versions
* Be regularly updated
* Have minimal unnecessary packages
* Be vulnerability scanned

Avoid unnecessary full operating-system images.

Prefer:

```text
python:3.12-slim
```

over unnecessarily large images such as:

```text
python:3.12
```

when the application does not require the additional packages.

---

# 7. Base Image Pinning

Production images should use controlled and reproducible base images.

Where appropriate, pin images using immutable digests.

Example:

```dockerfile
FROM python:3.12-slim@sha256:<digest>
```

This prevents an identical Dockerfile from silently receiving a different base image.

---

# 8. Python/FastAPI Container Standards

FastAPI applications should use a production ASGI server.

Example:

```dockerfile
CMD [
  "uvicorn",
  "app.main:app",
  "--host",
  "0.0.0.0",
  "--port",
  "8000"
]
```

Development-only options such as auto-reload must not be enabled in production.

Avoid:

```bash
uvicorn app.main:app --reload
```

in production.

---

# 9. Working Directory

Containers should define an explicit working directory.

Example:

```dockerfile
WORKDIR /app
```

Application files should be placed under this directory unless there is a documented reason otherwise.

---

# 10. Multi-Stage Builds

Multi-stage Docker builds should be used when build dependencies are not required at runtime.

Example:

```dockerfile
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --prefix=/install \
    --no-cache-dir \
    -r requirements.txt


FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY app ./app
```

Build-time dependencies must not unnecessarily remain in the production image.

---

# 11. Dependency Installation

Dependencies must be installed from controlled dependency files.

Examples:

```text
requirements.txt
pyproject.toml
poetry.lock
uv.lock
```

Avoid:

```dockerfile
RUN pip install fastapi
```

for production builds when dependencies are supposed to be controlled by a project dependency file.

---

# 12. Dependency Version Pinning

Production dependencies should use controlled versions.

Example:

```text
fastapi==0.115.x
uvicorn==0.x.x
pydantic==2.x.x
```

or an approved lock-file strategy.

Dependency versions must be compatible with the project's dependency security standards.

---

# 13. Pip Cache Standards

Docker images should avoid unnecessary package-manager caches.

Example:

```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```

This reduces image size.

---

# 14. Docker Layer Optimization

Dockerfiles should place infrequently changing layers before frequently changing layers.

Preferred:

```dockerfile
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
```

This allows Docker to reuse dependency layers when application code changes.

---

# 15. Build Context

Docker builds must use the smallest practical build context.

Avoid:

```bash
docker build .
```

when the current directory contains unnecessary large files that could be included.

Use `.dockerignore` to control the build context.

---

# 16. `.dockerignore`

Every production Docker project should contain `.dockerignore`.

Example:

```text
.git
.gitignore
.venv
venv
__pycache__
*.pyc
.pytest_cache
.mypy_cache
.ruff_cache
.env
.env.*
*.log
tests
node_modules
dist
build
terraform.tfstate
terraform.tfstate.*
```

Sensitive files must never be included in the Docker build context.

---

# 17. Secrets Must Not Be Copied

Never copy secret files into an image.

Forbidden:

```dockerfile
COPY .env /app/.env
```

Also forbidden:

```dockerfile
COPY credentials.json /app/
```

Secrets must be injected at runtime through approved secret-management mechanisms.

---

# 18. Docker `ARG` and Secrets

Secrets must not be passed through normal Docker build arguments.

Avoid:

```dockerfile
ARG API_KEY
ENV API_KEY=$API_KEY
```

Build arguments may become visible through image metadata or build history.

Use secure BuildKit secret mechanisms when a build genuinely requires a secret.

---

# 19. Environment Variables

Non-secret configuration should be provided through environment variables.

Example:

```text
APP_ENV=production
LOG_LEVEL=INFO
DATABASE_HOST=...
```

Application code should read configuration from environment variables or the project's centralized configuration system.

---

# 20. Secret Injection

Production secrets should be injected at runtime.

For AWS ECS:

```text
AWS Secrets Manager
        ↓
ECS Task Definition
        ↓
Container Environment
        ↓
FastAPI Application
```

The Docker image itself must remain secret-free.

---

# 21. Non-Root User

Production containers must run as a non-root user whenever possible.

Example:

```dockerfile
RUN useradd --create-home appuser

USER appuser
```

Avoid running application processes as:

```text
root
```

unless a documented exception exists.

---

# 22. File Permissions

Application files must have only the permissions required by the application.

Avoid:

```bash
chmod -R 777 /app
```

Use least-privilege permissions.

---

# 23. Read-Only Filesystem

Production containers should use a read-only root filesystem when supported.

For example, ECS can configure:

```text
readonlyRootFilesystem = true
```

Applications requiring temporary files should use a dedicated writable temporary location.

---

# 24. Temporary File Handling

Temporary files must be stored only in controlled locations.

Example:

```text
/tmp
```

or a dedicated mounted temporary filesystem.

Applications must not write arbitrary files into the application source directory.

---

# 25. Container Capabilities

Containers should run with the minimum Linux capabilities required.

Unnecessary capabilities must be dropped.

Production containers should not receive broad host-level capabilities.

---

# 26. Privileged Containers

Production workloads must not use:

```text
--privileged
```

unless explicitly approved for a legitimate infrastructure requirement.

Application containers should never require privileged mode.

---

# 27. Host Networking

Host networking should not be used for normal application containers.

Avoid:

```bash
docker run --network host
```

unless there is a documented infrastructure requirement.

Containers should use isolated Docker/ECS networking.

---

# 28. Docker Socket Security

Application containers must not receive unrestricted access to:

```text
/var/run/docker.sock
```

Docker socket access effectively provides high-level control over the Docker host.

If Docker operations are required, use an approved isolated build or execution environment.

---

# 29. Container Networking

Containers should communicate through explicitly defined networks.

Example:

```text
Frontend
   ↓
Backend
   ↓
Database
```

Only required network communication should be permitted.

---

# 30. Port Standards

Only required application ports should be exposed.

For FastAPI:

```dockerfile
EXPOSE 8000
```

`EXPOSE` documents the intended port; actual network access must still be controlled by Docker, ECS, security groups, load balancers, or other infrastructure controls.

---

# 31. Health Check Standards

Production containers should provide health checks.

Example:

```dockerfile
HEALTHCHECK --interval=30s \
            --timeout=5s \
            --retries=3 \
            CMD curl --fail http://localhost:8000/health || exit 1
```

If `curl` is not installed, an application-supported health-check mechanism should be used.

---

# 32. Application Health Endpoints

FastAPI applications should provide:

```text
/health
/readiness
```

Example:

```text
GET /health
GET /readiness
```

Health checks must return meaningful status information.

---

# 33. Startup and Shutdown

Containers must handle operating-system termination signals correctly.

The application should support graceful shutdown.

For FastAPI:

```text
SIGTERM
   ↓
Application shutdown
   ↓
Finish/stop active work safely
   ↓
Release resources
   ↓
Container exits
```

This is especially important for ECS deployments.

---

# 34. Entrypoint Standards

Use `ENTRYPOINT` and `CMD` intentionally.

Example:

```dockerfile
ENTRYPOINT ["python", "-m", "app"]
```

or:

```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Avoid complicated shell commands when direct executable invocation is sufficient.

---

# 35. Exec Form

Prefer exec-form commands.

Preferred:

```dockerfile
CMD ["uvicorn", "app.main:app"]
```

Avoid unnecessarily using:

```dockerfile
CMD uvicorn app.main:app
```

Exec form improves signal handling and process management.

---

# 36. Logging Standards

Containers should log application output to:

```text
stdout
stderr
```

Applications should not depend on local container log files.

Example:

```python
logger.info("Application started")
```

Docker/ECS/CloudWatch should handle centralized log collection.

---

# 37. Sensitive Logging

Containers must never log:

* Passwords
* API keys
* Access tokens
* JWTs
* Private keys
* Database credentials
* Cloud credentials
* LLM credentials

Logs must be treated as potentially accessible operational data.

---

# 38. Resource Management

Containers must have appropriate CPU and memory limits.

Example conceptual configuration:

```text
CPU limit
Memory limit
```

The values should be based on application requirements and performance testing.

Containers must not consume unlimited host resources.

---

# 39. Resource Requests and Scaling

Container resource requirements should be defined before production deployment.

Example:

```text
CPU: 512
Memory: 1024 MB
```

These values are examples only and must be adjusted based on workload.

Container resource configuration feeds into ECS capacity planning and Auto Scaling decisions.

Full Auto Scaling rules belong in:

```text
rag_knowledge/devops/ecs_rules.md
```

---

# 40. Restart Policy

Production workloads should have an appropriate restart strategy.

For local Docker:

```bash
docker run --restart unless-stopped ...
```

For ECS, the ECS service scheduler should maintain the required desired task count.

Containers that repeatedly crash must be investigated rather than hidden through infinite restarts.

---

# 41. Image Tagging Standards

Images should use meaningful tags.

Example:

```text
myapp:1.4.0
myapp:build-152
myapp:git-a81f92c
```

Avoid relying only on:

```text
latest
```

for production deployments.

---

# 42. Immutable Image Deployment

Production deployments should reference immutable image versions.

Preferred:

```text
myapp:git-a81f92c
```

or an image digest:

```text
myapp@sha256:<digest>
```

This makes deployments reproducible and rollback-safe.

---

# 43. Image Size Optimization

Production images should contain only required runtime dependencies.

Avoid unnecessary:

* Compilers
* Debugging tools
* Package caches
* Development dependencies
* Source-control metadata
* Test files
* Documentation
* Temporary files

Image size should be monitored during CI.

---

# 44. BuildKit Standards

BuildKit should be used for modern Docker builds.

Example:

```bash
DOCKER_BUILDKIT=1 docker build -t myapp:latest .
```

BuildKit can provide:

* Improved caching
* Parallel builds
* Secure build secrets
* Better build performance

---

# 45. Docker Build Cache

CI/CD pipelines should use Docker layer caching where practical.

Caching must not compromise:

* Security
* Dependency updates
* Reproducibility
* Secret protection

Security-sensitive build steps must not incorrectly reuse stale data.

---

# 46. Docker Vulnerability Scanning

Docker images must be vulnerability scanned before production deployment.

Example tools may include:

```text
Trivy
Amazon Inspector
Docker Scout
```

Critical vulnerabilities must block production deployment unless formally approved and mitigated.

---

# 47. Image Security Scanning

The security pipeline should scan:

```text
Base image
↓
OS packages
↓
Python dependencies
↓
Application dependencies
↓
Configuration
```

Example:

```bash
trivy image myapp:build-152
```

---

# 48. Secret Scanning

Images and Docker build contexts must be checked for accidentally included secrets.

Examples:

```text
API keys
AWS credentials
GitHub tokens
Private keys
.env files
Database credentials
```

Secret detection failures must block the image from promotion.

---

# 49. SBOM Standards

Production images should have a Software Bill of Materials (SBOM).

The SBOM should identify:

* Base image
* OS packages
* Python packages
* Application dependencies
* Package versions

Example tooling:

```text
Syft
Trivy
Docker Scout
```

---

# 50. Image Provenance

Production images should have traceable build provenance.

The deployment system should be able to identify:

```text
Git Commit
↓
CI Build
↓
Docker Image
↓
ECR Repository
↓
ECS Deployment
```

This allows the platform to trace exactly which source code produced a running application.

---

# 51. ECR Integration

AWS ECR should be used as the approved container registry for AWS deployments.

Typical flow:

```text
GitHub
   ↓
Jenkins
   ↓
Docker Build
   ↓
Security Scan
   ↓
Tag Image
   ↓
Push to ECR
   ↓
ECS
```

Example:

```bash
docker build -t myapp:$BUILD_NUMBER .

docker tag myapp:$BUILD_NUMBER \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/myapp:$BUILD_NUMBER

docker push \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/myapp:$BUILD_NUMBER
```

---

# 52. ECR Image Security

ECR repositories should use:

* Image scanning
* Encryption
* Restricted IAM access
* Lifecycle policies
* Immutable tagging where appropriate

Only authorized CI/CD systems should push production images.

---

# 53. ECS Container Standards

For ECS deployments:

```text
ECR Image
   ↓
ECS Task Definition
   ↓
ECS Service
   ↓
Load Balancer
   ↓
Users
```

The ECS task definition should specify:

* Image
* CPU
* Memory
* Port
* Environment variables
* Secrets
* Health checks
* IAM roles
* Logging
* Network configuration

---

# 54. ECS Health and Deployment Integration

ECS should use container and load-balancer health checks.

Deployment flow:

```text
New Image
   ↓
ECS Task Starts
   ↓
Container Health Check
   ↓
Target Group Health Check
   ↓
Healthy Task
   ↓
Traffic
```

Unhealthy tasks must not receive production traffic.

---

# 55. Docker and Agent-Generated Applications

The Agentic SDLC platform may generate Dockerfiles automatically.

The Docker Agent must validate generated Dockerfiles before they are accepted.

Validation must check:

```text
Base Image
↓
Dependencies
↓
Secrets
↓
User
↓
Ports
↓
Health Check
↓
Command
↓
Security
↓
Image Build
```

---

# 56. Generated Code Execution

Generated applications must never be executed directly on the host system.

Required flow:

```text
Generated Code
      ↓
Security Validation
      ↓
Sandbox
      ↓
Docker Build
      ↓
Isolated Container
      ↓
Tests
```

The Agentic SDLC platform must isolate generated code execution from the platform host.

---

# 57. Docker Sandbox Standards

Agent-generated code execution must use restricted containers.

The sandbox should enforce:

* Non-root execution
* CPU limits
* Memory limits
* Execution timeout
* Network restrictions
* Filesystem restrictions
* No Docker socket
* No host filesystem access
* No privileged mode
* No unrestricted cloud credentials

---

# 58. LLM/RAG Container Standards

LLM and RAG applications running inside containers must follow the same container security standards.

Additionally:

* API keys must not be baked into images.
* Vector database credentials must be runtime-injected.
* Retrieved RAG content must be treated as untrusted.
* Prompt data must not expose infrastructure credentials.
* Agent state must not contain unnecessary secrets.

---

# 59. MCP Container Standards

MCP servers deployed in containers must:

* Run with least privilege.
* Use secure authentication.
* Avoid exposing secrets to the LLM.
* Restrict network access.
* Avoid privileged containers.
* Avoid Docker socket access.
* Log tool activity without credentials.

---

# 60. Docker Compose Standards

Docker Compose may be used for local development and integration testing.

Example:

```yaml
services:

  backend:
    build: .
    ports:
      - "8000:8000"

  postgres:
    image: postgres:16
```

Production deployment should use the organization's approved orchestration platform, such as ECS.

---

# 61. Local Docker Commands

Build:

```bash
docker build -t myapp:local .
```

Run:

```bash
docker run --rm -p 8000:8000 myapp:local
```

List images:

```bash
docker images
```

List containers:

```bash
docker ps
```

View logs:

```bash
docker logs <container_id>
```

Stop container:

```bash
docker stop <container_id>
```

Remove container:

```bash
docker rm <container_id>
```

---

# 62. Docker Validation Commands

Build:

```bash
docker build -t myapp:test .
```

Inspect image:

```bash
docker inspect myapp:test
```

Check image history:

```bash
docker history myapp:test
```

Run container:

```bash
docker run --rm -p 8000:8000 myapp:test
```

Check health:

```bash
curl http://localhost:8000/health
```

---

# 63. Docker Security Validation

Example:

```bash
trivy image myapp:test
```

Secret scanning should also be performed using the organization's approved scanner.

Dockerfile configuration should be reviewed for:

```text
Root user
Secrets
Privileged mode
Unsafe capabilities
Unnecessary ports
Large images
Untrusted base images
Docker socket access
```

---

# 64. Docker CI/CD Standards

CI/CD should follow:

```text
Checkout
   ↓
Dependency Installation
   ↓
Tests
   ↓
Lint
   ↓
Type Check
   ↓
Security Scan
   ↓
Docker Build
   ↓
Image Scan
   ↓
SBOM
   ↓
Push to ECR
   ↓
Deploy
```

A failed mandatory Docker security gate must stop the pipeline.

---

# 65. Docker Quality Gates

A production Docker image must satisfy:

```text
Dockerfile valid
        AND
Build successful
        AND
Application starts
        AND
Health check passes
        AND
Non-root execution
        AND
No critical vulnerabilities
        AND
No exposed secrets
        AND
Approved base image
        AND
Image traceable to Git commit
```

---

# 66. Docker Failure Handling

If Docker build fails, the Docker Agent must identify:

* Build stage
* Error message
* Root cause
* Affected dependency
* Recommended fix
* Severity

Example:

```json
{
  "status": "failed",
  "stage": "docker_build",
  "error": "dependency installation failed",
  "severity": "high",
  "recommendation": "validate dependency version compatibility"
}
```

---

# 67. Docker Agent Input

Example:

```json
{
  "project_id": "project-123",
  "language": "python",
  "framework": "fastapi",
  "python_version": "3.12",
  "port": 8000,
  "deployment_target": "ecs",
  "registry": "ecr",
  "requirements": [
    "fastapi",
    "uvicorn"
  ],
  "security_requirements": [
    "non_root",
    "health_check",
    "no_secrets"
  ]
}
```

---

# 68. Docker Agent Output

Example:

```json
{
  "dockerfile_generated": true,
  "image_built": true,
  "image_tag": "project-123:a81f92c",
  "container_started": true,
  "health_check_passed": true,
  "security_scan_passed": true,
  "secret_scan_passed": true,
  "status": "passed"
}
```

---

# 69. Docker Agent Workflow

The Docker Agent should follow:

```text
Receive Application
        ↓
Analyze Project
        ↓
Read Docker Standards
        ↓
Read Deployment Requirements
        ↓
Generate Dockerfile
        ↓
Generate .dockerignore
        ↓
Validate Dockerfile
        ↓
Build Image
        ↓
Run Container
        ↓
Health Check
        ↓
Security Scan
        ↓
Secret Scan
        ↓
Generate SBOM
        ↓
Tag Image
        ↓
Return Result
```

---

# 70. Docker Agent Validation Checklist

The Docker Agent must validate:

### Dockerfile

* [ ] Valid Dockerfile
* [ ] Approved base image
* [ ] Controlled dependencies
* [ ] Efficient layers
* [ ] Multi-stage build where appropriate
* [ ] `.dockerignore` exists
* [ ] No secrets
* [ ] Non-root user
* [ ] Correct port
* [ ] Correct startup command
* [ ] Health check

### Security

* [ ] No privileged mode
* [ ] No unnecessary capabilities
* [ ] No Docker socket
* [ ] No host filesystem access
* [ ] No hardcoded credentials
* [ ] Vulnerability scan passed
* [ ] Secret scan passed

### Runtime

* [ ] Container starts
* [ ] Health endpoint works
* [ ] Graceful shutdown works
* [ ] Logs go to stdout/stderr
* [ ] Resource requirements defined

### CI/CD

* [ ] Image tagged
* [ ] Image traceable to Git commit
* [ ] Image scan completed
* [ ] SBOM generated
* [ ] ECR push successful when required

---

# 71. Docker Implementation Decision Matrix

| Situation              | Recommended Implementation         | Avoid                        |
| ---------------------- | ---------------------------------- | ---------------------------- |
| FastAPI production app | `python:3.12-slim` + non-root      | Large unnecessary base image |
| Python dependencies    | Controlled requirements/lock file  | Unpinned ad-hoc installs     |
| Production build       | Multi-stage build when useful      | Build tools in runtime image |
| Secrets                | Runtime secret injection           | `COPY .env`                  |
| AWS credentials        | ECS IAM role                       | Static AWS keys              |
| ECS secrets            | AWS Secrets Manager                | Credentials in image         |
| Container user         | Non-root                           | Root                         |
| Temporary files        | `/tmp` or controlled volume        | Application source directory |
| Filesystem             | Read-only where possible           | Writable root filesystem     |
| Docker capabilities    | Minimum required                   | Broad capabilities           |
| Privileged container   | Forbidden by default               | `--privileged`               |
| Docker socket          | Never expose by default            | `/var/run/docker.sock`       |
| Health                 | `/health` + container health check | No health check              |
| Logs                   | stdout/stderr                      | Application log files        |
| Image tag              | Git SHA/build ID                   | Only `latest`                |
| Registry               | ECR for AWS                        | Unapproved registry          |
| Vulnerability scan     | Trivy/Inspector/approved scanner   | No scan                      |
| SBOM                   | Generate during CI                 | Unknown image contents       |
| Agent code             | Sandbox container                  | Host execution               |
| CI build               | BuildKit                           | Legacy-only build            |
| Production deployment  | Immutable image                    | Mutable image                |
| Scaling                | ECS service + Auto Scaling         | Manual container count       |

---

# 72. Docker Acceptance Criteria

A Docker implementation is accepted only when:

1. Dockerfile builds successfully.
2. Application container starts successfully.
3. Application health check passes.
4. Correct application port is configured.
5. Production container runs as non-root.
6. No secrets are present in the image.
7. `.dockerignore` is configured.
8. Vulnerability scanning passes required thresholds.
9. Secret scanning passes.
10. Image is traceable to a source Git commit.
11. Image has an immutable/controlled tag.
12. Runtime resources are defined.
13. Logging works correctly.
14. Graceful shutdown works.
15. Required security restrictions are applied.
16. ECR push succeeds when AWS deployment is required.
17. ECS deployment succeeds when ECS is the target.
18. Critical security findings are zero.
19. High-severity blockers are zero.
20. Docker validation report is generated.

---

# 73. Docker Quality Gate

The Docker pipeline must block promotion when:

```text
Docker Build Failure
        OR
Health Check Failure
        OR
Critical Vulnerability
        OR
Critical Secret Exposure
        OR
Invalid Dockerfile
        OR
Unsafe Privileged Configuration
        OR
Production Image Not Traceable
```

Any blocking condition must be resolved before deployment.

---

# 74. Production Docker Rule

Production Docker images must be:

```text
Minimal
+
Secure
+
Non-root
+
Immutable
+
Scanned
+
Health-checked
+
Traceable
+
Resource-controlled
```

---

# 75. Final Docker Rule

The Agentic SDLC platform must never treat a successfully built Docker image as automatically production-ready.

A Docker image is production-ready only when:

```text
Dockerfile Valid
      ↓
Image Builds
      ↓
Container Starts
      ↓
Health Check Passes
      ↓
Security Scan Passes
      ↓
Secret Scan Passes
      ↓
SBOM Generated
      ↓
Image Traceability Verified
      ↓
ECR Validation
      ↓
ECS Deployment Validation
      ↓
Production Ready
```

**Final Rule:**

> Every Docker image generated by the Agentic SDLC platform must be reproducible, secure, non-root, secret-free, health-checkable, vulnerability-scanned, traceable to source code, and validated before it can proceed to production deployment.
