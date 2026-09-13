# System Design Standards

## 1. Purpose

This document defines the system design standards for applications generated and managed by the Agentic SDLC platform.

The System Design must describe:

* Overall system architecture
* Major components
* Component responsibilities
* Data flow
* API communication
* Database interactions
* Agent interactions
* RAG integration
* MCP integration
* Security architecture
* Deployment architecture
* Scalability
* Reliability
* Monitoring
* Failure handling
* Human approval points
* UI/UX and Figma integration

The System Design must be detailed enough for the Frontend Agent, Backend Agent, Testing Agent, Security Agent, DevOps Agent, and Deployment Agent to implement the application consistently.

---

# 2. System Design Principles

The generated system must follow these principles:

1. Prefer simple architecture over unnecessary complexity.
2. Use modular components.
3. Keep services loosely coupled.
4. Define clear responsibilities for every component.
5. Use secure-by-default configurations.
6. Design APIs before implementation.
7. Design database schema before database implementation.
8. Define failure scenarios before deployment.
9. Design for observability.
10. Design for scalability where required.
11. Avoid unnecessary microservices.
12. Use asynchronous processing for long-running operations.
13. Separate development, staging, and production environments.
14. Use infrastructure as code.
15. Keep secrets outside source code.
16. Apply guardrails to agent actions.
17. Require human approval for high-risk operations.
18. Use RAG knowledge before generating application code.
19. Use Figma as the UI/UX source of truth.
20. Every generated architecture must be explainable.

---

# 3. Requirements → System Design

The System Design Agent must consume the output of the Requirements Agent.

The flow is:

```text
User Requirement
      ↓
Requirements Agent
      ↓
Functional Requirements
Non-Functional Requirements
Business Rules
Constraints
      ↓
System Design Agent
      ↓
System Architecture
Database Design
API Design
UI/UX Design
Figma Design
      ↓
Implementation Agents
```

The System Design must map requirements to technical components.

Example:

```text
Requirement:
User should be able to create a project.

        ↓

System Design:

Frontend
    ↓
POST /api/v1/projects
    ↓
FastAPI Backend
    ↓
Project Service
    ↓
PostgreSQL
```

Every major requirement should have a corresponding component or workflow.

---

# 4. High-Level System Architecture

The architecture must identify:

* Client
* Frontend
* Backend
* API layer
* Authentication
* Database
* Cache
* Message queue if required
* Background workers
* External services
* AI/LLM services
* RAG system
* MCP servers
* Monitoring
* CI/CD
* Cloud infrastructure

Example:

```text
                    User
                     │
                     ↓
                Web Frontend
                     │
                     ↓
                API Layer
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
   Auth Service   Backend      WebSocket
                     │
        ┌────────────┼─────────────┐
        ↓            ↓             ↓
   PostgreSQL      Redis       Job Queue
        │                          │
        │                          ↓
        │                       Workers
        │                          │
        └──────────────┬───────────┘
                       ↓
                 Agent Orchestrator
                       │
              ┌────────┼────────┐
              ↓        ↓        ↓
           Agents     RAG      MCP
                       │        │
                       ↓        ↓
                 Vector DB   External Tools
```

The architecture must be adapted to the actual application requirements.

---

# 5. Major Components

Every system design must define the responsibility of each major component.

Example:

| Component      | Responsibility                |
| -------------- | ----------------------------- |
| Frontend       | User interface                |
| API            | Request/response handling     |
| Authentication | Identity and access control   |
| Backend        | Business logic                |
| PostgreSQL     | Persistent data               |
| Redis          | Cache/session/temporary state |
| Queue          | Asynchronous jobs             |
| Worker         | Background processing         |
| LLM            | AI reasoning/generation       |
| RAG            | Knowledge retrieval           |
| MCP            | Standardized tool access      |
| GitHub         | Source control                |
| Jenkins        | CI/CD                         |
| Docker         | Application packaging         |
| AWS ECR        | Container registry            |
| AWS ECS        | Container deployment          |
| CloudWatch     | Monitoring                    |

---

# 6. Component Responsibility

Each component must have a single primary responsibility.

Avoid:

```text
Frontend
    ↓
Frontend directly accesses database
```

Preferred:

```text
Frontend
    ↓
API
    ↓
Backend
    ↓
Database
```

Agents must also have clearly separated responsibilities.

For example:

```text
Research Agent
    ↓
Requirements Agent
    ↓
Design Agent
    ↓
Frontend Agent
    ↓
Backend Agent
    ↓
Testing Agent
    ↓
Security Agent
    ↓
DevOps Agent
    ↓
Deployment Agent
    ↓
Monitoring Agent
```

---

# 7. User/Application Request Flow

The system design must describe the complete request lifecycle.

Example:

```text
User
 ↓
Frontend
 ↓
API
 ↓
Authentication
 ↓
Request Validation
 ↓
Business Logic
 ↓
Database / Cache
 ↓
External Services
 ↓
Response
 ↓
Frontend
 ↓
User
```

For AI requests:

```text
User
 ↓
Frontend
 ↓
API
 ↓
Input Guardrail
 ↓
Agent Orchestrator
 ↓
RAG Retrieval
 ↓
LLM
 ↓
Tool/MCP Calls
 ↓
Output Guardrail
 ↓
Human Approval if required
 ↓
Response
```

---

# 8. Agentic SDLC Workflow

The Agentic SDLC platform must use a controlled multi-agent workflow.

```text
User
 ↓
Research Agent
 ↓
Requirements Agent
 ↓
Design Agent
 ↓
 ├── Architecture Design
 ├── Database Design
 ├── API Design
 └── Figma UI/UX Design
 ↓
Frontend Agent
 ↓
Backend Agent
 ↓
Testing Agent
 ↓
Security Agent
 ↓
DevOps Agent
 ↓
Deployment Agent
 ↓
Monitoring Agent
```

Agents must not randomly execute stages.

Each stage should have defined:

* Input
* Processing
* Output
* Validation
* Dependencies
* Approval requirements

---

# 9. Agent Responsibilities

| Agent              | Primary Responsibility                        |
| ------------------ | --------------------------------------------- |
| Research Agent     | Market, technology, competitor research       |
| Requirements Agent | Convert user requirements into specifications |
| Design Agent       | Architecture, database, API and Figma design  |
| Frontend Agent     | Generate frontend implementation              |
| Backend Agent      | Generate backend implementation               |
| Testing Agent      | Generate and execute tests                    |
| Security Agent     | Security analysis and remediation             |
| DevOps Agent       | Docker, Jenkins, Terraform and infrastructure |
| Deployment Agent   | Deploy application                            |
| Monitoring Agent   | Monitor application and infrastructure        |

Agents must not perform another agent's responsibilities unless explicitly authorized by the workflow.

---

# 10. LangGraph Orchestration

The Agentic SDLC workflow should use a graph-based orchestration model.

Example:

```text
START
  ↓
Research
  ↓
Requirements
  ↓
Design
  ↓
Figma
  ↓
Frontend
  ↓
Backend
  ↓
Testing
  ↓
Security
  ↓
DevOps
  ↓
Approval
  ↓
Deployment
  ↓
Monitoring
  ↓
END
```

Conditional edges may be used.

Example:

```text
Testing
   │
   ├── Tests Passed → Security
   │
   └── Tests Failed → Backend/Frontend Fix
```

Security:

```text
Security Scan
      │
      ├── Safe → Deployment
      │
      └── Vulnerability → Fix → Re-test
```

Deployment:

```text
Deployment
     │
     ├── Success → Monitoring
     │
     └── Failure → Rollback
```

---

# 11. Agent State

The system must maintain shared workflow state.

Example:

```text
ProjectState

project_id
user_request
requirements
research_results
architecture
database_design
api_design
figma_url
frontend_code
backend_code
test_results
security_results
docker_image
deployment_status
deployment_url
errors
approval_status
```

State must be persisted when workflows are long-running.

---

# 12. RAG Architecture

The system must use RAG for organizational and technical knowledge.

```text
Knowledge Files
      ↓
Document Loader
      ↓
Chunking
      ↓
Embeddings
      ↓
Vector Database
      ↓
Retriever
      ↓
Relevant Knowledge
      ↓
Agent
      ↓
LLM
```

Example:

```text
coding_standards.md
security_standards.md
api_design.md
database_design.md
docker_rules.md
jenkins_rules.md
```

Agents should retrieve relevant knowledge before generating implementation artifacts.

---

# 13. RAG Retrieval Strategy

Retrieval should consider:

* Agent type
* Project type
* Technology
* Environment
* Security requirements
* File category
* Task type

Example:

```text
Backend Agent
      ↓
Retrieve:
python_standards.md
fastapi_standards.md
backend_testing.md
api_design.md
security_standards.md
      ↓
Generate Backend
```

The system should avoid sending the entire knowledge base to every agent.

---

# 14. MCP Integration

MCP should be used to standardize access to external tools.

Example:

```text
Agent
  ↓
MCP Client
  ↓
MCP Server
  ↓
External Tool
```

Example:

```text
DevOps Agent
      ↓
Jenkins MCP
      ↓
Jenkins
```

```text
Deployment Agent
      ↓
AWS MCP
      ↓
AWS
```

```text
Monitoring Agent
      ↓
CloudWatch MCP
      ↓
CloudWatch
```

Agents should not directly contain large amounts of provider-specific integration logic when MCP can provide standardized access.

---

# 15. Figma Design Workflow

The Design Agent must create the application's UI/UX design in Figma.

The Figma design must cover:

* Page structure
* Layout
* Components
* Navigation
* Forms
* Buttons
* Tables
* Cards
* Error states
* Loading states
* Empty states
* Responsive behavior
* User flows

The workflow is:

```text
Requirements Agent
        ↓
Design Agent
        ↓
Architecture Design
        +
Figma UI/UX Design
        ↓
Figma Link
        ↓
Frontend Agent
        ↓
Frontend Implementation
```

The generated **Figma link must be stored in the project state**.

Example:

```text
figma_url:
https://www.figma.com/...
```

The Frontend Agent must treat the Figma design as the primary UI/UX source of truth.

Frontend implementation must follow:

```text
Figma
 ↓
Components
 ↓
Pages
 ↓
Responsive Layout
 ↓
Frontend Tests
```

If the implementation differs from the Figma design, the Frontend Agent should identify the deviation and correct it unless the deviation is explicitly approved.

---

# 16. Frontend Architecture

The system design must define:

* Framework
* Component structure
* Routing
* State management
* API client
* Authentication
* Error handling
* Form handling
* UI components
* Testing strategy

Example:

```text
React
 │
 ├── Pages
 ├── Components
 ├── Hooks
 ├── Services
 ├── State
 ├── API Client
 └── Tests
```

---

# 17. Backend Architecture

The backend should separate:

```text
API Routes
    ↓
Schemas
    ↓
Services
    ↓
Repositories
    ↓
Database
```

Example:

```text
POST /projects
      ↓
projects.py
      ↓
ProjectService
      ↓
ProjectRepository
      ↓
PostgreSQL
```

Business logic should not be placed directly inside route handlers when the logic is reusable or complex.

---

# 18. API Layer

The API layer must provide:

* Authentication
* Authorization
* Validation
* Rate limiting where required
* Error handling
* Request tracing
* Logging
* API versioning

Example:

```text
/api/v1/projects
/api/v1/projects/{project_id}
/api/v1/projects/{project_id}/deployments
```

API design must follow:

```text
rag_knowledge/design/api_design.md
```

---

# 19. Database Architecture

The system design must define:

* Database technology
* Entities
* Relationships
* Primary keys
* Foreign keys
* Indexes
* Constraints
* Transactions
* Data retention
* Backup strategy

Example:

```text
User
 │
 └── Project
       │
       ├── Requirement
       ├── Design
       ├── Deployment
       └── Job
```

Database implementation must follow:

```text
rag_knowledge/design/database_design.md
```

---

# 20. Cache Architecture

Redis may be used for:

* Frequently accessed data
* Sessions
* Temporary state
* Rate limiting
* Distributed locks
* Job coordination

Do not use cache as the primary permanent data store unless explicitly designed for that purpose.

---

# 21. Asynchronous Jobs

Long-running operations should not block synchronous API requests.

Examples:

* AI generation
* Code generation
* Test execution
* Docker builds
* Jenkins pipelines
* Deployment
* Security scans

Preferred:

```text
POST /projects/{id}/generate
        ↓
Create Job
        ↓
Return job_id
        ↓
Background Worker
        ↓
Execute Task
        ↓
Update Job Status
```

Example response:

```json
{
  "job_id": "job_123",
  "status": "queued"
}
```

---

# 22. Job State Management

Long-running jobs should maintain states such as:

```text
queued
running
completed
failed
cancelled
```

The system should expose job status through an API.

Example:

```text
GET /api/v1/jobs/{job_id}
```

The job record should contain:

```text
job_id
project_id
job_type
status
started_at
completed_at
error
result
```

---

# 23. Event-Driven Architecture

Events may be used where asynchronous communication is beneficial.

Example:

```text
ProjectCreated
      ↓
RequirementsGenerated
      ↓
DesignCompleted
      ↓
CodeGenerated
      ↓
TestsCompleted
      ↓
SecurityApproved
      ↓
DeploymentRequested
      ↓
DeploymentCompleted
```

Events must have clearly defined producers and consumers.

---

# 24. Security Architecture

Security must exist at every layer.

```text
User
 ↓
Authentication
 ↓
Authorization
 ↓
API Security
 ↓
Input Validation
 ↓
Business Logic
 ↓
Database Security
 ↓
Infrastructure Security
```

Security must also apply to agents:

```text
Agent
 ↓
Guardrail
 ↓
Permission Check
 ↓
Tool
 ↓
External System
```

Agents should receive only the permissions required for their tasks.

---

# 25. Guardrails

Guardrails must be applied before high-risk actions.

Examples:

```text
User Input
   ↓
Input Guardrail
   ↓
Agent
   ↓
Output Guardrail
   ↓
Tool Permission Check
   ↓
External System
```

Deployment actions should have additional deployment guardrails.

---

# 26. Human Approval Gates

Human approval must be used for high-risk operations.

Examples:

* Production deployment
* Database migration
* Infrastructure destruction
* Security policy changes
* IAM permission changes
* Production rollback
* Destructive cloud operations

Example:

```text
Security
   ↓
Approval Required
   ↓
Human Approval
   ↓
Deployment
```

The workflow must not bypass mandatory approval gates.

---

# 27. GitHub / Source Control Architecture

Generated code must be stored in Git.

Example:

```text
Agent
 ↓
Generated Project
 ↓
Git Repository
 ↓
Branch
 ↓
Commit
 ↓
Pull Request
 ↓
Review
 ↓
Merge
```

The system should avoid directly modifying protected branches unless explicitly authorized.

---

# 28. CI/CD Architecture

The CI/CD pipeline should follow:

```text
Git Push
   ↓
Jenkins
   ↓
Checkout
   ↓
Install Dependencies
   ↓
Lint
   ↓
Unit Tests
   ↓
Integration Tests
   ↓
Security Scan
   ↓
Docker Build
   ↓
Push Image to ECR
   ↓
Deploy
   ↓
Smoke Test
   ↓
Monitoring
```

The pipeline must follow:

```text
rag_knowledge/devops/jenkins_rules.md
```

---

# 29. Docker Architecture

Applications should be packaged as Docker images.

```text
Source Code
     ↓
Dockerfile
     ↓
Docker Build
     ↓
Docker Image
     ↓
ECR
     ↓
ECS
```

Images must:

* Use appropriate base images
* Avoid unnecessary packages
* Run as non-root where possible
* Avoid secrets
* Use deterministic dependencies
* Be scanned for vulnerabilities

---

# 30. AWS Deployment Architecture

For AWS deployments, the system design must identify:

* VPC
* Subnets
* Security Groups
* IAM
* ECR
* ECS
* Load Balancer
* CloudWatch
* S3 where required
* RDS where required
* Route 53 where required

Example:

```text
Internet
   ↓
Route 53
   ↓
ALB
   ↓
ECS
   ↓
Application Container
   ↓
RDS
```

Supporting services:

```text
ECS
 ├── ECR
 ├── CloudWatch
 ├── Secrets Manager
 └── IAM
```

Only required AWS services should be introduced.

---

# 31. Environment Separation

The architecture must separate:

```text
Development
     ↓
Staging
     ↓
Production
```

Each environment should have independent:

* Configuration
* Secrets
* Database
* Infrastructure
* Deployment process

Production credentials must never be reused in development.

---

# 32. Configuration Management

Configuration should be externalized.

Example:

```text
Environment Variables
        ↓
Application Configuration
```

Sensitive values must use:

* AWS Secrets Manager
* Parameter Store
* CI/CD credentials
* Secure environment variables

Never hard-code:

```text
API keys
Passwords
AWS credentials
Database credentials
Tokens
Private keys
```

---

# 33. Monitoring Architecture

Monitoring should cover:

* Application
* API
* Database
* Containers
* Infrastructure
* Agents
* LLM requests
* RAG retrieval
* Jobs
* Deployments

Example:

```text
Application
     ↓
Logs + Metrics + Traces
     ↓
CloudWatch
     ↓
Alerts
     ↓
Operations
```

---

# 34. Agent Observability

Agent workflows must track:

```text
project_id
workflow_id
agent_name
task
start_time
end_time
status
LLM_model
token_usage
retrieved_documents
tool_calls
errors
```

This allows debugging of multi-agent workflows.

---

# 35. Logging

Logs should contain structured information.

Example:

```json
{
  "timestamp": "...",
  "level": "INFO",
  "service": "backend",
  "agent": "backend_agent",
  "project_id": "123",
  "event": "code_generation_completed"
}
```

Logs must not expose:

* Passwords
* API keys
* Tokens
* Private keys
* Sensitive user information

---

# 36. Failure Handling

Every major component must define failure behavior.

Example:

```text
LLM Failure
   ↓
Retry
   ↓
Still Failed
   ↓
Fallback / Human Review
```

For external APIs:

```text
API Failure
   ↓
Retry with Backoff
   ↓
Failure
   ↓
Circuit Breaker / Error State
```

For deployment:

```text
Deployment Failure
       ↓
Health Check
       ↓
Rollback
       ↓
Alert
```

---

# 37. Retry Strategy

Retries should be used only for transient failures.

Examples:

* Network timeout
* Temporary AWS error
* Temporary database connection failure
* Rate limiting

Retries should use exponential backoff.

Avoid unlimited retries.

Example:

```text
Attempt 1
   ↓
Wait
   ↓
Attempt 2
   ↓
Wait
   ↓
Attempt 3
   ↓
Fail
```

---

# 38. Scalability

The architecture should identify possible bottlenecks.

Potential bottlenecks:

* LLM requests
* Vector database
* Database connections
* API traffic
* Background jobs
* Docker builds
* Deployment operations

Scaling strategies may include:

* Horizontal scaling
* Worker scaling
* Queue-based processing
* Database indexing
* Caching
* Connection pooling
* Rate limiting

Do not introduce scaling infrastructure without a real requirement.

---

# 39. Reliability

The system should avoid single points of failure where required.

Consider:

* Multiple application instances
* Load balancing
* Health checks
* Database backups
* Retry mechanisms
* Rollbacks
* Queue durability
* Failure recovery

Critical components should have documented recovery behavior.

---

# 40. Disaster Recovery

The system design must define:

* Backup strategy
* Recovery strategy
* Data retention
* Recovery Point Objective (RPO)
* Recovery Time Objective (RTO)

Example:

```text
Database
   ↓
Automated Backup
   ↓
Backup Storage
   ↓
Disaster
   ↓
Restore
   ↓
Application Recovery
```

---

# 41. Deployment Strategy

Deployment strategy must be explicitly defined.

Possible strategies:

* Rolling deployment
* Blue/green deployment
* Canary deployment

For smaller applications:

```text
Build
 ↓
Deploy
 ↓
Health Check
 ↓
Success
```

For production-critical systems:

```text
New Version
 ↓
Staging
 ↓
Approval
 ↓
Production
 ↓
Health Check
 ↓
Traffic Migration
```

---

# 42. Rollback Architecture

Every production deployment must have a rollback strategy.

Example:

```text
Version N
   ↓
Deploy Version N+1
   ↓
Health Check
   │
   ├── Success → Continue
   │
   └── Failure
          ↓
       Rollback
          ↓
       Version N
```

Rollback procedures must be automated where practical.

---

# 43. Performance Design

The system design must identify performance-sensitive operations.

Consider:

* API response time
* Database queries
* LLM latency
* RAG retrieval latency
* Tool calls
* Queue processing time
* Container startup time

Performance targets should be defined where appropriate.

---

# 44. Cost Design

The architecture should consider cloud and AI costs.

Potential cost drivers:

* LLM token usage
* Embeddings
* Vector database
* ECS compute
* RDS
* ECR
* CloudWatch
* Data transfer
* Jenkins infrastructure

Cost optimization strategies may include:

* Model selection
* Token limits
* Caching
* Batch processing
* Appropriate compute sizing
* Log retention policies
* Resource cleanup

---

# 45. Data Flow Documentation

Every major workflow must have a data flow.

Example:

```text
User Requirement
      ↓
Requirements Agent
      ↓
Requirement Object
      ↓
Design Agent
      ↓
Architecture Object
      ↓
Frontend / Backend Agents
      ↓
Generated Code
      ↓
Git Repository
      ↓
CI/CD
      ↓
Deployment
```

Data transformations should be documented.

---

# 46. External Dependencies

Every external dependency must be identified.

Example:

| Dependency | Purpose        | Failure Impact          | Fallback       |
| ---------- | -------------- | ----------------------- | -------------- |
| LLM        | AI generation  | Agent failure           | Retry/fallback |
| GitHub     | Source control | Cannot commit           | Queue/retry    |
| Jenkins    | CI/CD          | Build blocked           | Retry          |
| AWS        | Deployment     | Deployment blocked      | Retry          |
| Figma      | UI design      | Frontend design blocked | Human review   |

---

# 47. API → Database → External Service Flow

The architecture should clearly distinguish internal and external communication.

Example:

```text
Frontend
   ↓
FastAPI
   ↓
Service Layer
   ├── PostgreSQL
   ├── Redis
   ├── LLM
   ├── GitHub
   └── AWS
```

The frontend should not directly communicate with databases or privileged infrastructure services.

---

# 48. System Design Template

Every generated system design should contain:

```text
Project Name:

Project Description:

Business Requirements:

Functional Requirements:

Non-Functional Requirements:

Users / Actors:

System Architecture:

Major Components:

Component Responsibilities:

Frontend Architecture:

Backend Architecture:

API Architecture:

Database Architecture:

Cache:

Async Jobs:

Message Queue:

Agent Architecture:

Agent State:

LangGraph Workflow:

RAG Architecture:

MCP Architecture:

Figma Design:

Figma URL:

External Dependencies:

Security Architecture:

Guardrails:

Human Approval Gates:

GitHub Architecture:

CI/CD Architecture:

Docker Architecture:

AWS Architecture:

Monitoring:

Logging:

Tracing:

Scalability:

Reliability:

Failure Handling:

Retry Strategy:

Disaster Recovery:

RPO:

RTO:

Deployment Strategy:

Rollback Strategy:

Environment Strategy:

Configuration:

Secrets Management:

Cost Considerations:

Risks:

Assumptions:

Open Questions:
```

---

# 49. Agent-Generated System Design Process

The Design Agent should follow this process:

```text
1. Read Requirements
        ↓
2. Retrieve Relevant RAG Knowledge
        ↓
3. Identify Actors
        ↓
4. Identify Components
        ↓
5. Define Component Responsibilities
        ↓
6. Define Data Flow
        ↓
7. Define API Communication
        ↓
8. Define Database Architecture
        ↓
9. Define Agent Workflow
        ↓
10. Define Security
        ↓
11. Define Scalability
        ↓
12. Define Failure Handling
        ↓
13. Define Deployment Architecture
        ↓
14. Generate Figma UI/UX Design
        ↓
15. Store Figma Link
        ↓
16. Validate Architecture
        ↓
17. Produce System Design
```

---

# 50. Expected Design Artifacts

The Design Agent should produce:

```text
Architecture Design
        +
Database Design
        +
API Design
        +
System Design
        +
Figma UI/UX Design
        ↓
Design Package
```

The design package should be passed to implementation agents.

Example:

```text
Design Package
│
├── architecture
├── database_schema
├── api_specification
├── system_design
└── figma_url
```

---

# 51. Frontend Handoff

The Frontend Agent must receive:

```text
Requirements
+
System Design
+
API Design
+
Figma URL
+
Frontend Standards
```

The Frontend Agent must use the Figma design as the UI/UX source of truth.

---

# 52. Backend Handoff

The Backend Agent must receive:

```text
Requirements
+
System Design
+
Database Design
+
API Design
+
Backend Standards
+
Security Standards
```

The Backend Agent must implement according to the approved architecture.

---

# 53. Testing Handoff

The Testing Agent must receive:

```text
Requirements
+
System Design
+
API Design
+
Frontend Code
+
Backend Code
```

Testing should validate both functional behavior and architecture requirements.

---

# 54. Security Handoff

The Security Agent must validate:

```text
Architecture
+
Code
+
Dependencies
+
Docker
+
Infrastructure
+
Secrets
+
APIs
+
Agent Tools
```

Security findings must be returned to the appropriate agent for remediation.

---

# 55. DevOps Handoff

The DevOps Agent must receive:

```text
System Design
+
Application Code
+
Testing Results
+
Security Results
```

It should generate:

```text
Dockerfile
Jenkinsfile
Terraform
Deployment Configuration
```

according to project requirements.

---

# 56. Deployment Handoff

The Deployment Agent should receive:

```text
Approved Application
+
Docker Image
+
Infrastructure
+
Deployment Configuration
+
Approval Status
```

Production deployment must not occur without required approval.

---

# 57. System Design Validation Checklist

Before approving a system design, verify:

* [ ] Requirements mapped to architecture
* [ ] Actors identified
* [ ] Components identified
* [ ] Responsibilities defined
* [ ] Data flow defined
* [ ] API communication defined
* [ ] Database design defined
* [ ] Agent workflow defined
* [ ] LangGraph flow defined
* [ ] RAG integration defined
* [ ] MCP integration defined
* [ ] Figma design defined
* [ ] Figma URL captured
* [ ] Frontend handoff defined
* [ ] Backend handoff defined
* [ ] Security architecture defined
* [ ] Guardrails defined
* [ ] Human approval gates defined
* [ ] CI/CD defined
* [ ] Docker strategy defined
* [ ] Deployment architecture defined
* [ ] Monitoring defined
* [ ] Logging defined
* [ ] Failure handling defined
* [ ] Rollback defined
* [ ] Scalability considered
* [ ] Disaster recovery considered
* [ ] Environment separation defined
* [ ] Secrets management defined
* [ ] Cost considered
* [ ] External dependencies identified

---

# 58. Agentic SDLC System Design Rule

The Design Agent must never generate implementation architecture blindly.

It must:

```text
Understand Requirements
        ↓
Retrieve Relevant Knowledge
        ↓
Design Architecture
        ↓
Design Database
        ↓
Design APIs
        ↓
Design Figma UI/UX
        ↓
Validate Security
        ↓
Validate Scalability
        ↓
Define Failure Handling
        ↓
Generate Design Package
        ↓
Pass Approved Design to Implementation Agents
```

**The System Design is the technical contract between Requirements and Implementation.**

The Frontend Agent, Backend Agent, Testing Agent, Security Agent, DevOps Agent, and Deployment Agent must follow the approved System Design unless an explicit change is approved.

# 3A. Concrete Input Schema

The Design Agent must receive a structured input object rather than relying only on unstructured text.

## DesignAgentInput

```json
{
  "project_id": "proj_123",
  "project_name": "Expense Management System",
  "user_request": "Build an expense management application for employees.",
  "requirements": {
    "functional": [
      "Users can create expense reports",
      "Users can upload receipts",
      "Managers can approve expense reports"
    ],
    "non_functional": [
      "API response time should be below 500ms",
      "Application must support 1000 concurrent users"
    ],
    "business_rules": [
      "Only managers can approve expense reports"
    ]
  },
  "technology_preferences": {
    "frontend": "React",
    "backend": "FastAPI",
    "database": "PostgreSQL",
    "cloud": "AWS"
  },
  "constraints": {
    "authentication": "JWT",
    "deployment": "Docker + ECS",
    "ci_cd": "Jenkins"
  },
  "rag_context": [
    {
      "document": "architecture_standards.md",
      "content": "Retrieved architecture standards..."
    },
    {
      "document": "api_design.md",
      "content": "Retrieved API standards..."
    }
  ],
  "previous_artifacts": {
    "research": {},
    "requirements": {}
  }
}
```

## Input Field Definitions

| Field                         | Type   | Required | Description                    |
| ----------------------------- | ------ | -------: | ------------------------------ |
| `project_id`                  | string |      Yes | Unique project identifier      |
| `project_name`                | string |      Yes | Project name                   |
| `user_request`                | string |      Yes | Original application request   |
| `requirements`                | object |      Yes | Requirements Agent output      |
| `requirements.functional`     | array  |      Yes | Functional requirements        |
| `requirements.non_functional` | array  |      Yes | Non-functional requirements    |
| `requirements.business_rules` | array  |       No | Business rules                 |
| `technology_preferences`      | object |       No | Preferred technologies         |
| `constraints`                 | object |       No | Technical/business constraints |
| `rag_context`                 | array  |      Yes | Relevant retrieved knowledge   |
| `previous_artifacts`          | object |       No | Outputs from previous agents   |

---

# 3B. Concrete Output Schema

The Design Agent must return a structured design package.

## DesignAgentOutput

```json
{
  "project_id": "proj_123",
  "status": "completed",
  "architecture": {
    "architecture_style": "modular_monolith",
    "components": [
      {
        "name": "React Frontend",
        "type": "frontend",
        "responsibility": "User interface"
      },
      {
        "name": "FastAPI Backend",
        "type": "backend",
        "responsibility": "Business logic and API"
      },
      {
        "name": "PostgreSQL",
        "type": "database",
        "responsibility": "Persistent data storage"
      }
    ],
    "data_flow": [
      "User -> React Frontend",
      "React Frontend -> FastAPI Backend",
      "FastAPI Backend -> PostgreSQL"
    ]
  },
  "database_design": {
    "entities": [
      {
        "name": "User",
        "table": "users",
        "primary_key": "id"
      },
      {
        "name": "ExpenseReport",
        "table": "expense_reports",
        "primary_key": "id"
      }
    ]
  },
  "api_design": {
    "base_path": "/api/v1",
    "endpoints": [
      {
        "method": "POST",
        "path": "/expense-reports",
        "purpose": "Create expense report"
      },
      {
        "method": "GET",
        "path": "/expense-reports/{expense_report_id}",
        "purpose": "Get expense report"
      }
    ]
  },
  "system_design": {
    "actors": [
      "Employee",
      "Manager",
      "Administrator"
    ],
    "services": [
      "Frontend",
      "Backend",
      "Database",
      "Authentication"
    ],
    "security": [
      "JWT authentication",
      "Role-based authorization"
    ],
    "scalability": [
      "Horizontal ECS scaling",
      "Database connection pooling"
    ],
    "failure_handling": [
      "API retry for transient failures",
      "Database connection retry"
    ]
  },
  "figma": {
    "status": "completed",
    "url": "https://www.figma.com/...",
    "source_of_truth": true
  },
  "handoff": {
    "frontend_agent": true,
    "backend_agent": true,
    "testing_agent": true,
    "security_agent": true,
    "devops_agent": true
  },
  "validation": {
    "requirements_mapped": true,
    "security_reviewed": true,
    "scalability_reviewed": true,
    "failure_handling_defined": true
  },
  "errors": []
}
```

## Output Field Definitions

| Field                     | Type    | Required | Description                              |
| ------------------------- | ------- | -------: | ---------------------------------------- |
| `project_id`              | string  |      Yes | Project identifier                       |
| `status`                  | enum    |      Yes | `completed`, `failed`, `requires_review` |
| `architecture`            | object  |      Yes | High-level architecture                  |
| `architecture.components` | array   |      Yes | System components                        |
| `architecture.data_flow`  | array   |      Yes | Component communication flow             |
| `database_design`         | object  |      Yes | Database architecture                    |
| `api_design`              | object  |      Yes | API architecture                         |
| `system_design`           | object  |      Yes | Complete system design                   |
| `figma`                   | object  |      Yes | Figma design information                 |
| `figma.url`               | string  |      Yes | Generated Figma design URL               |
| `figma.source_of_truth`   | boolean |      Yes | Must be `true` for frontend handoff      |
| `handoff`                 | object  |      Yes | Downstream agent availability            |
| `validation`              | object  |      Yes | Design validation results                |
| `errors`                  | array   |      Yes | Errors or warnings                       |

---

# 3C. Pydantic Schema

The schemas should also be represented as typed application models.

```python
from typing import Any, Literal
from pydantic import BaseModel, Field


class Requirements(BaseModel):
    functional: list[str]
    non_functional: list[str]
    business_rules: list[str] = []


class TechnologyPreferences(BaseModel):
    frontend: str | None = None
    backend: str | None = None
    database: str | None = None
    cloud: str | None = None


class Constraints(BaseModel):
    authentication: str | None = None
    deployment: str | None = None
    ci_cd: str | None = None


class RAGDocument(BaseModel):
    document: str
    content: str


class DesignAgentInput(BaseModel):
    project_id: str
    project_name: str
    user_request: str
    requirements: Requirements
    technology_preferences: TechnologyPreferences | None = None
    constraints: Constraints | None = None
    rag_context: list[RAGDocument]
    previous_artifacts: dict[str, Any] = {}


class Component(BaseModel):
    name: str
    type: str
    responsibility: str


class Architecture(BaseModel):
    architecture_style: str
    components: list[Component]
    data_flow: list[str]


class FigmaDesign(BaseModel):
    status: Literal["completed", "failed", "requires_review"]
    url: str | None = None
    source_of_truth: bool


class Handoff(BaseModel):
    frontend_agent: bool
    backend_agent: bool
    testing_agent: bool
    security_agent: bool
    devops_agent: bool


class Validation(BaseModel):
    requirements_mapped: bool
    security_reviewed: bool
    scalability_reviewed: bool
    failure_handling_defined: bool


class DesignAgentOutput(BaseModel):
    project_id: str
    status: Literal["completed", "failed", "requires_review"]
    architecture: Architecture
    database_design: dict[str, Any]
    api_design: dict[str, Any]
    system_design: dict[str, Any]
    figma: FigmaDesign
    handoff: Handoff
    validation: Validation
    errors: list[str] = []
```

---

# 3D. Agent Contract

The Design Agent must follow this contract:

```text
DesignAgentInput
      ↓
Validate Input
      ↓
Retrieve RAG Knowledge
      ↓
Generate Design
      ↓
Generate Figma Design
      ↓
Validate Design
      ↓
DesignAgentOutput
```

The downstream agents consume the structured output:

```text
DesignAgentOutput
        │
        ├── architecture
        │       ↓
        │   All Agents
        │
        ├── database_design
        │       ↓
        │   Backend Agent
        │
        ├── api_design
        │       ↓
        │   Frontend + Backend
        │
        ├── figma
        │       ↓
        │   Frontend Agent
        │
        └── system_design
                ↓
        Testing + Security + DevOps
```

The **Design Agent must not return only free-form text**. Its final result must conform to the defined `DesignAgentOutput` schema so that LangGraph can reliably pass the result to downstream agents.
