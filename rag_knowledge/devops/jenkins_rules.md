# Jenkins Rules

## 1. Purpose

This document defines Jenkins CI/CD standards for the Agentic SDLC platform.

Jenkins pipelines must provide automated, repeatable, secure, traceable, and production-ready software delivery.

---

## 2. Jenkins Standards Summary

Jenkins implementations must be:

* Declarative where practical
* Version-controlled
* Reproducible
* Secure
* Parameterized
* Environment-aware
* Observable
* Failure-safe
* Artifact-aware
* Deployment-gated

---

## 3. Jenkinsfile Standard

The pipeline definition must be stored in source control.

Standard location:

```text
Jenkinsfile
```

Recommended project structure:

```text
project/
├── Jenkinsfile
├── Dockerfile
├── requirements.txt
└── app/
```

The Jenkinsfile should normally be committed to the application repository rather than manually maintained only inside Jenkins.

---

## 4. Declarative Pipeline

Declarative Pipeline should be preferred.

Example:

```groovy
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                sh 'pytest'
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t myapp:${BUILD_NUMBER} .'
            }
        }
    }
}
```

---

## 5. Pipeline Structure

A standard application pipeline should follow:

```text
Checkout
   ↓
Environment Setup
   ↓
Dependency Installation
   ↓
Formatting
   ↓
Linting
   ↓
Type Checking
   ↓
Unit Tests
   ↓
Integration Tests
   ↓
Security Scanning
   ↓
Docker Build
   ↓
Image Scan
   ↓
Push to ECR
   ↓
Deploy
   ↓
Health Check
   ↓
Smoke Test
```

---

## 6. Jenkins Agent Standards

Jenkins agents should execute builds in isolated environments.

Agents may be:

* EC2 instances
* Docker-based agents
* Kubernetes agents
* Ephemeral cloud agents

Production deployments should not depend on a developer's local machine.

---

## 7. Agent Labels

Jenkins agents should use meaningful labels.

Example:

```text
linux
docker
aws
python
terraform
```

Pipeline:

```groovy
agent {
    label 'linux-docker'
}
```

---

## 8. Agent Isolation

Builds must not unnecessarily share:

* Workspace files
* Credentials
* Temporary files
* Docker state
* Application artifacts

Sensitive or production deployments should use appropriately isolated agents.

---

## 9. Workspace Standards

Jenkins workspaces should contain only files required for the current build.

Temporary files must be cleaned after execution.

Example:

```groovy
post {
    always {
        cleanWs()
    }
}
```

---

## 10. Source Control Checkout

The pipeline should retrieve source code using Jenkins SCM integration.

Example:

```groovy
stage('Checkout') {
    steps {
        checkout scm
    }
}
```

The pipeline should build the exact commit associated with the Jenkins build.

---

## 11. Git Branch Standards

Branch-based pipelines should clearly distinguish environments.

Example:

```text
feature/*
develop
qa
main
```

A common deployment mapping may be:

```text
develop → Development
qa     → Staging
main   → Production
```

The actual mapping must follow project requirements.

---

## 12. Multibranch Pipeline

Jenkins Multibranch Pipeline should be used when multiple Git branches require independent CI/CD execution.

Example:

```text
Repository
   ├── develop
   ├── qa
   └── main
```

Each branch can contain its own Jenkinsfile or use a shared pipeline strategy.

---

## 13. Environment Separation

Jenkins must clearly separate:

```text
Development
Staging
Production
```

Production credentials and deployment targets must never be reused for development jobs.

---

## 14. Environment Variables

Non-secret configuration may be defined using environment variables.

Example:

```groovy
environment {
    AWS_REGION = 'ap-south-1'
    ECR_REPOSITORY = 'myapp'
}
```

Secrets must not be stored directly in the Jenkinsfile.

---

## 15. Jenkins Credentials

Secrets must be stored using Jenkins Credentials or an approved centralized secret manager.

Example:

```groovy
withCredentials([
    string(
        credentialsId: 'github-token',
        variable: 'GITHUB_TOKEN'
    )
]) {
    sh 'some-command'
}
```

Credentials must be scoped to the smallest required operation.

---

## 16. AWS Authentication

Jenkins should preferably use IAM roles or short-lived approved credentials when running on AWS infrastructure.

Avoid:

```groovy
environment {
    AWS_ACCESS_KEY_ID = 'hardcoded-key'
}
```

AWS credentials must never be committed to Git.

---

## 17. Jenkins Credential Security

Never print credentials.

Forbidden:

```groovy
echo "${AWS_SECRET_ACCESS_KEY}"
```

Credentials should also not appear in:

* Build logs
* Artifacts
* Test reports
* Docker images
* Environment dumps

---

## 18. Secret Masking

Jenkins credentials should use supported credential-binding mechanisms so sensitive values can be masked from logs.

Even with masking enabled, pipelines must avoid intentionally echoing secret values.

---

## 19. Build Parameters

Pipelines may use parameters for controlled runtime choices.

Example:

```groovy
parameters {
    choice(
        name: 'ENVIRONMENT',
        choices: ['dev', 'qa', 'prod'],
        description: 'Deployment environment'
    )
}
```

Production parameters must have appropriate authorization controls.

---

## 20. Prevent Unsafe Production Parameters

A user must not be able to bypass deployment controls simply by selecting:

```text
ENVIRONMENT=prod
```

Production deployment should require branch protection, approval, or another organizational control.

---

## 21. Build Number

Every Jenkins build receives a unique build number.

The build number may be used for:

* Artifact identification
* Docker image tags
* Deployment tracking
* Audit records

Example:

```text
myapp:build-152
```

---

## 22. Git Commit Traceability

Every artifact should be traceable to:

```text
Git Repository
↓
Branch
↓
Commit SHA
↓
Jenkins Build
↓
Docker Image
↓
Deployment
```

The commit SHA should be recorded in build metadata.

---

## 23. Docker Build

Docker images should be built inside the controlled CI environment.

Example:

```groovy
stage('Docker Build') {
    steps {
        sh """
            docker build \
              -t ${ECR_REPOSITORY}:${BUILD_NUMBER} .
        """
    }
}
```

The Docker build must use the project's approved Dockerfile.

---

## 24. Docker Image Tagging

Images should use immutable or traceable tags.

Preferred:

```text
myapp:build-152
myapp:git-a81f92c
```

Avoid deploying production using only:

```text
latest
```

---

## 25. ECR Authentication

For AWS deployments, Jenkins should authenticate to Amazon ECR using approved AWS credentials or IAM roles.

Example:

```bash
aws ecr get-login-password --region $AWS_REGION |
docker login \
  --username AWS \
  --password-stdin \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
```

---

## 26. ECR Push

Example:

```bash
docker tag myapp:$BUILD_NUMBER \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/myapp:$BUILD_NUMBER

docker push \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/myapp:$BUILD_NUMBER
```

The image must pass required quality and security gates before production push.

---

## 27. Testing Standards

Jenkins must execute automated tests before deployment.

For Python/FastAPI:

```bash
pytest
```

Recommended sequence:

```bash
ruff format --check .
ruff check .
mypy .
pytest tests/unit/
pytest tests/integration/
pytest tests/api/
pytest tests/security/
pytest tests/e2e/
```

---

## 28. Code Quality Gates

The pipeline should validate:

```text
Formatting
Linting
Type Checking
Unit Tests
Integration Tests
API Tests
Security Tests
E2E Tests
Coverage
```

A mandatory quality gate failure must stop promotion.

---

## 29. Dependency Security

Dependencies should be scanned in CI.

Example:

```bash
pip-audit
```

Additional scanners may be used according to organizational requirements.

Critical dependency vulnerabilities must block production deployment unless formally approved.

---

## 30. Static Security Scanning

Application security scanning should run before deployment.

For Python:

```bash
bandit -r app/
```

Secret scanning should also be enabled.

---

## 31. Docker Security Scanning

Built images should be scanned before deployment.

Example:

```bash
trivy image $IMAGE
```

Critical vulnerabilities must block promotion according to security policy.

---

## 32. Terraform Pipeline Standards

Terraform pipelines should follow:

```text
terraform fmt
      ↓
terraform validate
      ↓
terraform plan
      ↓
Approval
      ↓
terraform apply
```

Production `apply` should require appropriate approval controls.

---

## 33. Terraform State Security

Jenkins must never commit Terraform state.

Forbidden:

```text
terraform.tfstate
terraform.tfstate.backup
```

Terraform state should use the approved remote backend.

Example:

```text
S3
+
state locking
+
encryption
+
restricted IAM access
```

---

## 34. Terraform Credentials

Terraform credentials must be injected securely.

Never place:

```hcl
access_key = "..."
secret_key = "..."
```

directly into Terraform source code.

Prefer IAM roles or approved temporary credentials.

---

## 35. Deployment Approval

Production deployment should require an explicit gate when organizational policy requires it.

Example:

```groovy
stage('Production Approval') {
    steps {
        input message: 'Deploy to production?'
    }
}
```

Approval must occur before the production deployment action.

---

## 36. Deployment Standards

Deployment should follow:

```text
Build
 ↓
Validate
 ↓
Scan
 ↓
Publish
 ↓
Deploy
 ↓
Health Check
 ↓
Smoke Test
```

A deployment must not be considered successful merely because the deployment command returned successfully.

---

## 37. ECS Deployment

For ECS:

```text
Jenkins
  ↓
ECR Image
  ↓
Task Definition
  ↓
ECS Service
  ↓
New Tasks
  ↓
Health Checks
  ↓
Traffic
```

The pipeline should verify ECS task health after deployment.

---

## 38. AWS Deployment Validation

After deployment Jenkins should validate:

* ECS task started
* Task is healthy
* Target group is healthy
* Application health endpoint succeeds
* Required application request succeeds

Example:

```bash
curl --fail https://example.com/health
```

---

## 39. Deployment Timeout

Deployment stages must have explicit timeouts.

Example:

```groovy
options {
    timeout(time: 30, unit: 'MINUTES')
}
```

Long-running operations must not run indefinitely.

---

## 40. Retry Standards

Retries should only be used for transient failures.

Example:

```groovy
retry(2) {
    sh 'some-transient-operation'
}
```

Do not repeatedly retry deterministic failures such as:

* Compilation errors
* Failed tests
* Invalid Terraform
* Invalid Dockerfile
* Security policy violations

---

## 41. Idempotent Pipeline Operations

Pipeline operations should be safe to retry where possible.

Examples:

```text
Docker build
Artifact upload
Terraform plan
ECS deployment
```

Operations that create duplicate resources must use appropriate safeguards.

---

## 42. Parallel Execution

Independent CI stages may run in parallel.

Example:

```text
             ┌── Unit Tests
             ├── Lint
Checkout ────┼── Type Check
             └── Security Scan
```

Deployment must wait until all required gates pass.

---

## 43. Pipeline Failure Handling

When a pipeline fails, Jenkins should identify:

* Stage
* Build number
* Commit SHA
* Error
* Root cause
* Severity
* Recommended fix

Example:

```json
{
  "status": "failed",
  "stage": "docker_build",
  "build_number": 152,
  "severity": "high",
  "recommendation": "fix dependency or Docker build configuration"
}
```

---

## 44. Post Actions

Pipelines should define appropriate post-build behavior.

Example:

```groovy
post {
    always {
        junit 'reports/**/*.xml'
        cleanWs()
    }

    success {
        echo 'Pipeline completed successfully'
    }

    failure {
        echo 'Pipeline failed'
    }
}
```

---

## 45. Test Reports

Jenkins should publish test results where applicable.

Example:

```groovy
post {
    always {
        junit 'reports/**/*.xml'
    }
}
```

Reports should allow engineers and agents to determine which tests failed.

---

## 46. Artifact Standards

Build artifacts should be:

* Versioned
* Traceable
* Secure
* Reproducible

Examples:

```text
Docker image
Python package
Frontend bundle
Terraform plan
Test reports
SBOM
```

Sensitive files must never be archived as artifacts.

---

## 47. Build Retention

Jenkins should use build retention policies.

Example:

```groovy
options {
    buildDiscarder(
        logRotator(
            numToKeepStr: '30'
        )
    )
}
```

Retention should comply with organizational audit requirements.

---

## 48. Pipeline Concurrency

Concurrent builds should be controlled where they can cause conflicts.

Example:

```groovy
options {
    disableConcurrentBuilds()
}
```

This is especially useful for deployments where simultaneous releases could interfere with each other.

---

## 49. Production Deployment Concurrency

Production deployments should normally be serialized unless the deployment strategy explicitly supports concurrent releases.

Examples:

```text
Deployment A
     ↓
Health Check
     ↓
Deployment B
```

---

## 50. Jenkins Log Standards

Logs should contain enough information to troubleshoot the pipeline.

Logs should include:

* Build number
* Stage
* Commit SHA
* Environment
* Major operation
* Failure information

Logs must never include credentials or sensitive application data.

---

## 51. Jenkins Pipeline Security

Jenkins must use:

* Role-based access control
* Credential restrictions
* Agent isolation
* Approved plugins
* Plugin updates
* Secure controller configuration
* Audit logging

Jenkins users should receive only the permissions required for their role.

---

## 52. Jenkins Plugin Security

Only required plugins should be installed.

Plugins should be:

* Approved
* Maintained
* Regularly updated
* Vulnerability monitored

Unused plugins should be removed.

---

## 53. Jenkins Controller Security

Build execution should preferably occur on agents rather than directly on the Jenkins controller.

The controller should not be treated as a general-purpose build server.

---

## 54. Jenkins and Docker Security

Jenkins agents requiring Docker access must be carefully isolated.

Avoid granting unrestricted Docker host control to untrusted jobs.

The Docker socket should not be exposed to arbitrary builds.

---

## 55. Jenkins Webhook Standards

Git providers may trigger Jenkins using webhooks.

Typical flow:

```text
Git Push
   ↓
Webhook
   ↓
Jenkins
   ↓
Pipeline
```

Webhook endpoints must use secure authentication/signature validation where supported.

---

## 56. GitHub Integration

The pipeline may integrate with GitHub for:

* Checkout
* Pull requests
* Branch events
* Commit status
* Deployment status

GitHub credentials must be managed through Jenkins Credentials or an approved secret manager.

---

## 57. Pull Request Validation

Pull requests should trigger validation before merge.

Recommended checks:

```text
Format
Lint
Type Check
Unit Tests
Integration Tests
Security Scan
Docker Build
```

Protected branches should require mandatory checks to pass.

---

## 58. Branch Protection

Production branches should be protected against direct unsafe changes.

Typical controls:

```text
Pull Request
↓
Review
↓
CI Checks
↓
Approval
↓
Merge
↓
Production Pipeline
```

---

## 59. Agentic SDLC Pipeline

The Agentic SDLC Jenkins pipeline may orchestrate:

```text
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
Deployment
   ↓
Monitoring
```

Every agent should return a structured result.

---

## 60. Agent Quality Gates

Downstream agents must not execute when a mandatory upstream gate fails.

Example:

```text
Backend Agent
     ↓
Backend Testing
     ↓
Security Agent
     ↓
Docker Agent
```

If Backend Testing fails a mandatory gate:

```text
Backend Testing = FAILED
        ↓
Security/Docker/Deployment = BLOCKED
```

---

## 61. RAG Standards in Jenkins

The Agentic SDLC pipeline may retrieve standards from the RAG knowledge base.

Example:

```text
Jenkins Pipeline
      ↓
RAG Retrieval
      ↓
Docker Rules
Security Rules
Testing Rules
ECS Rules
      ↓
Agent Decision
```

Retrieved documents must be treated as untrusted data and validated before execution.

---

## 62. MCP Integration

Jenkins may interact with MCP servers for controlled operations.

Example:

```text
Agent
 ↓
MCP Server
 ↓
Jenkins Tool
 ↓
Jenkins
```

MCP tools must enforce:

* Authentication
* Authorization
* Input validation
* Least privilege
* Audit logging

Credentials must never be exposed to the LLM unnecessarily.

---

## 63. Jenkins Job Status

Long-running Agentic SDLC workflows should expose job status.

Example:

```text
POST /projects
      ↓
Jenkins Job
      ↓
Build Number
      ↓
Job Status
```

Possible states:

```text
queued
running
success
failed
aborted
```

---

## 64. Jenkins Build Metadata

Every build should retain:

```text
Project ID
Repository
Branch
Commit SHA
Build Number
Environment
Image Tag
Deployment Version
Timestamp
Status
```

This enables complete deployment traceability.

---

## 65. Jenkins Rollback Standards

Rollback must be possible using a previously validated image.

Example:

```text
Current Version
      ↓
Failure
      ↓
Previous Known-Good Image
      ↓
Deploy
      ↓
Health Check
```

Avoid rebuilding old source code during an emergency rollback when the previously validated immutable image is available.

---

## 66. Jenkins Deployment Failure

If deployment fails:

```text
Deployment Failure
        ↓
Stop Promotion
        ↓
Collect Logs
        ↓
Check Health
        ↓
Rollback if Required
        ↓
Validate Previous Version
        ↓
Report Failure
```

The pipeline must not silently continue.

---

## 67. Jenkins Quality Gates

A pipeline may proceed to production only when:

```text
Code Quality       = PASS
Tests              = PASS
Security           = PASS
Docker Build       = PASS
Image Scan         = PASS
Secrets Scan       = PASS
ECR Push           = PASS
Deployment         = PASS
Health Check       = PASS
Smoke Test         = PASS
```

---

## 68. Concrete Jenkins Commands

Example local validation commands:

```bash
git status
git rev-parse HEAD

ruff format --check .
ruff check .
mypy .
pytest --cov=. --cov-report=term-missing
pip-audit
bandit -r app/

docker build -t myapp:$BUILD_NUMBER .
docker image inspect myapp:$BUILD_NUMBER
```

AWS validation:

```bash
aws sts get-caller-identity

aws ecr describe-repositories \
  --repository-names myapp

aws ecs describe-services \
  --cluster my-cluster \
  --services myapp
```

---

## 69. Example Jenkinsfile

A conceptual production pipeline:

```groovy
pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-south-1'
        ECR_REPOSITORY = 'myapp'
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(
            logRotator(numToKeepStr: '30')
        )
        disableConcurrentBuilds()
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Quality') {
            parallel {
                stage('Format') {
                    steps {
                        sh 'ruff format --check .'
                    }
                }

                stage('Lint') {
                    steps {
                        sh 'ruff check .'
                    }
                }

                stage('Type Check') {
                    steps {
                        sh 'mypy .'
                    }
                }
            }
        }

        stage('Test') {
            steps {
                sh 'pytest --cov=. --cov-report=term-missing'
            }
        }

        stage('Security') {
            steps {
                sh 'pip-audit'
                sh 'bandit -r app/'
            }
        }

        stage('Docker Build') {
            steps {
                sh """
                    docker build \
                      -t ${ECR_REPOSITORY}:${BUILD_NUMBER} .
                """
            }
        }

        stage('Docker Scan') {
            steps {
                sh """
                    trivy image \
                    ${ECR_REPOSITORY}:${BUILD_NUMBER}
                """
            }
        }

        stage('Push to ECR') {
            steps {
                sh '''
                    aws ecr get-login-password \
                    --region $AWS_REGION |
                    docker login \
                    --username AWS \
                    --password-stdin \
                    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
                '''

                sh '''
                    docker tag \
                    $ECR_REPOSITORY:$BUILD_NUMBER \
                    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$BUILD_NUMBER
                '''

                sh '''
                    docker push \
                    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$BUILD_NUMBER
                '''
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }

            steps {
                input message: 'Deploy to production?'

                sh './scripts/deploy.sh'
            }
        }

        stage('Health Check') {
            when {
                branch 'main'
            }

            steps {
                sh 'curl --fail https://example.com/health'
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true,
                  testResults: 'reports/**/*.xml'

            cleanWs()
        }

        success {
            echo 'Pipeline completed successfully'
        }

        failure {
            echo 'Pipeline failed'
        }
    }
}
```

The exact pipeline must be adapted to the project's infrastructure and security requirements.

---

## 70. Jenkins Agent Input

Example:

```json
{
  "project_id": "project-123",
  "repository": "github.com/company/myapp",
  "branch": "main",
  "framework": "fastapi",
  "deployment_target": "ecs",
  "registry": "ecr",
  "environment": "production",
  "quality_gates": [
    "lint",
    "type_check",
    "unit_tests",
    "security",
    "docker_scan"
  ]
}
```

---

## 71. Jenkins Agent Output

Example:

```json
{
  "build_number": 152,
  "commit_sha": "a81f92c",
  "image_tag": "152",
  "tests_passed": true,
  "security_scan_passed": true,
  "docker_build_passed": true,
  "ecr_push_passed": true,
  "deployment_passed": true,
  "health_check_passed": true,
  "status": "passed"
}
```

---

## 72. Jenkins Agent Workflow

The Jenkins Agent should follow:

```text
Receive Project
      ↓
Read Pipeline Requirements
      ↓
Read Testing Standards
      ↓
Read Security Standards
      ↓
Read Docker Standards
      ↓
Checkout Source
      ↓
Run Quality Gates
      ↓
Run Tests
      ↓
Run Security Scans
      ↓
Build Docker Image
      ↓
Scan Image
      ↓
Push Image
      ↓
Deploy
      ↓
Health Check
      ↓
Smoke Test
      ↓
Generate Report
      ↓
Return Result
```

---

## 73. Jenkins Validation Checklist

The Jenkins Agent must validate:

### Pipeline

* [ ] Jenkinsfile exists
* [ ] Declarative pipeline used where appropriate
* [ ] Checkout works
* [ ] Build stages are defined
* [ ] Environment separation exists
* [ ] Timeouts configured
* [ ] Retry policy is controlled
* [ ] Workspace cleanup configured

### Quality

* [ ] Formatting passes
* [ ] Linting passes
* [ ] Type checking passes
* [ ] Unit tests pass
* [ ] Integration tests pass
* [ ] API tests pass
* [ ] Security tests pass
* [ ] E2E tests pass where required

### Security

* [ ] No hardcoded credentials
* [ ] Jenkins Credentials used
* [ ] AWS IAM/approved credentials used
* [ ] Secret masking configured
* [ ] Dependency scan passes
* [ ] Secret scan passes
* [ ] Docker image scan passes
* [ ] Jenkins permissions are restricted

### Deployment

* [ ] Image tagged
* [ ] Image traceable to commit
* [ ] ECR push succeeds
* [ ] ECS deployment succeeds
* [ ] Health check passes
* [ ] Smoke test passes
* [ ] Rollback is available

---

## 74. Jenkins Implementation Decision Matrix

| Situation           | Recommended Implementation                  | Avoid                             |
| ------------------- | ------------------------------------------- | --------------------------------- |
| Pipeline definition | Jenkinsfile in Git                          | Manual-only Jenkins configuration |
| Multiple branches   | Multibranch Pipeline                        | One manually configured job       |
| AWS authentication  | IAM role/short-lived credentials            | Long-lived keys in Jenkinsfile    |
| Application secrets | Jenkins Credentials/approved secret manager | Hardcoded secrets                 |
| Docker build        | Controlled Jenkins agent                    | Developer laptop                  |
| Image registry      | Amazon ECR for AWS                          | Unapproved registry               |
| Image tagging       | Build number/Git SHA/digest                 | Only `latest`                     |
| Production deploy   | Approval + protected branch                 | Unrestricted manual parameter     |
| Terraform           | fmt → validate → plan → approval → apply    | Direct uncontrolled apply         |
| Testing             | Automated CI tests                          | Manual-only testing               |
| Security            | Automated scanning                          | Security after deployment         |
| Logs                | Jenkins logs without secrets                | Credential printing               |
| Workspace           | Cleanup after build                         | Permanent sensitive files         |
| Rollback            | Previous immutable image                    | Rebuild during incident           |
| Agent execution     | Isolated build agent                        | Jenkins controller                |
| Docker access       | Restricted agent                            | Unrestricted Docker socket        |
| Long-running job    | Build number + status                       | Blocking API indefinitely         |
| Agentic workflow    | Structured gates                            | Uncontrolled agent chaining       |

---

## 75. Jenkins Acceptance Criteria

A Jenkins pipeline is accepted only when:

1. Jenkinsfile is version-controlled.
2. Pipeline can execute from a clean workspace.
3. Source checkout succeeds.
4. Required quality gates execute.
5. Required tests execute.
6. Security scanning executes.
7. Docker image builds successfully.
8. Image scanning passes.
9. Secrets are not exposed.
10. Image is traceable to source commit.
11. ECR push succeeds when AWS deployment is required.
12. Deployment succeeds when required.
13. Application health check passes.
14. Smoke tests pass.
15. Pipeline failure blocks promotion.
16. Production deployment has required authorization.
17. Rollback is available.
18. Build metadata is retained.
19. Reports are generated.
20. Workspace cleanup occurs.

---

## 76. Jenkins Production Quality Gate

Production deployment must be blocked when:

```text
Required Test Failed
        OR
Security Scan Failed
        OR
Secret Exposure Detected
        OR
Docker Build Failed
        OR
Image Scan Failed
        OR
ECR Push Failed
        OR
Deployment Failed
        OR
Health Check Failed
        OR
Smoke Test Failed
```

---

## 77. Final Jenkins Rule

The Agentic SDLC platform must never treat a successful Jenkins build as sufficient evidence that an application is production-ready.

Production promotion requires:

```text
Source Validation
      ↓
Code Quality
      ↓
Testing
      ↓
Security
      ↓
Docker Build
      ↓
Image Security
      ↓
ECR
      ↓
Deployment
      ↓
Health Check
      ↓
Smoke Test
      ↓
Production Ready
```

**Final Rule:**

> Every Jenkins pipeline generated or executed by the Agentic SDLC platform must be version-controlled, secure, reproducible, traceable, automatically validated, and deployment-gated. No application may reach production while a mandatory quality, security, deployment, or health gate is failing.
