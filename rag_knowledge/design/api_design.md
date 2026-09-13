# API Design Standards

## 1. Purpose

This document defines the API design standards that all AI agents must follow when designing, generating, testing, securing, and modifying APIs for applications created by the Agentic SDLC platform.

APIs must be:

* Consistent
* Secure
* Maintainable
* Scalable
* Versioned
* Observable
* Well documented
* Backward compatible where required
* Suitable for production workloads

API design must be derived from approved requirements, architecture, database design, and system design.

---

# 2. API Design Principles

All APIs should follow:

1. Design from business requirements.
2. Use clear resource-oriented endpoints.
3. Use appropriate HTTP methods.
4. Use consistent request and response formats.
5. Validate all inputs.
6. Return meaningful HTTP status codes.
7. Implement authentication and authorization where required.
8. Never expose sensitive information.
9. Support pagination for large collections.
10. Provide consistent error responses.
11. Design for backward compatibility.
12. Document APIs.
13. Make APIs observable.
14. Apply rate limiting where appropriate.
15. Keep business logic outside API route handlers.

---

# 3. API Style

The default API style should be:

**RESTful HTTP APIs**

Example:

```text
GET    /api/v1/projects
GET    /api/v1/projects/{project_id}
POST   /api/v1/projects
PUT    /api/v1/projects/{project_id}
PATCH  /api/v1/projects/{project_id}
DELETE /api/v1/projects/{project_id}
```

Other styles such as:

* GraphQL
* gRPC
* WebSockets
* Server-Sent Events
* Event-driven APIs

may be used when justified by the architecture.

---

# 4. URL Structure

Use lowercase `kebab-case` or consistent resource naming.

Preferred:

```text
/api/v1/projects
/api/v1/projects/{project_id}/tasks
```

Avoid:

```text
/getProjects
/createProject
/projectData
```

URLs should represent resources rather than actions whenever possible.

---

# 5. API Versioning

APIs should be versioned when long-term compatibility is required.

Preferred:

```text
/api/v1/projects
```

When breaking changes are introduced:

```text
/api/v2/projects
```

Breaking changes should not silently modify the behavior of an existing production API.

---

# 6. HTTP Methods

Use HTTP methods according to their intended semantics.

| Method | Purpose                                            |
| ------ | -------------------------------------------------- |
| GET    | Retrieve resource                                  |
| POST   | Create resource / trigger non-idempotent operation |
| PUT    | Replace resource                                   |
| PATCH  | Partially update resource                          |
| DELETE | Delete resource                                    |

Example:

```text
POST /api/v1/projects
```

creates a project.

```text
PATCH /api/v1/projects/{project_id}
```

updates selected project fields.

---

# 7. HTTP Status Codes

Use appropriate status codes.

| Status | Meaning                                      |
| ------ | -------------------------------------------- |
| 200    | Successful request                           |
| 201    | Resource created                             |
| 202    | Request accepted for asynchronous processing |
| 204    | Successful request with no response body     |
| 400    | Invalid request                              |
| 401    | Authentication required/failed               |
| 403    | Permission denied                            |
| 404    | Resource not found                           |
| 409    | Resource conflict                            |
| 422    | Validation error                             |
| 429    | Rate limit exceeded                          |
| 500    | Internal server error                        |
| 502    | Bad gateway                                  |
| 503    | Service unavailable                          |

Do not return `200` for failed operations.

---

# 8. Request Design

Requests must have clearly defined schemas.

Example:

```json
{
  "name": "AI Project",
  "description": "Generate an application using Agentic SDLC"
}
```

Requests should define:

* Required fields
* Optional fields
* Data types
* Validation rules
* Maximum lengths
* Allowed values
* Default values

---

# 9. Response Design

Responses should use consistent structures.

Example:

```json
{
  "id": "project-id",
  "name": "AI Project",
  "status": "created",
  "created_at": "2026-09-08T10:00:00Z"
}
```

Collection responses should support pagination.

Example:

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 100
}
```

---

# 10. Standard Error Response

All APIs should return a consistent error format.

Example:

```json
{
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Project was not found",
    "details": null,
    "request_id": "request-id"
  }
}
```

Errors should provide enough information for clients to handle the failure without exposing internal implementation details.

Never expose:

* Stack traces
* Database credentials
* API keys
* Internal secrets
* Sensitive system information

---

# 11. Validation

All external input must be validated.

Validate:

* Data types
* Required fields
* String length
* Numeric ranges
* Enum values
* IDs
* URLs
* File types
* Request size

FastAPI applications should use **Pydantic** models for request and response validation.

Example:

```python
class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
```

---

# 12. Authentication

APIs requiring user identity must implement authentication.

Possible mechanisms include:

* OAuth 2.0
* OpenID Connect
* JWT
* API keys
* Service-to-service authentication

Authentication mechanism must be selected based on system requirements.

---

# 13. Authorization

Authentication and authorization are separate concerns.

The API must verify that the authenticated identity has permission to perform the requested operation.

Example:

```text
Request
   ↓
Authentication
   ↓
Identity
   ↓
Authorization
   ↓
Resource Access
```

Never rely only on frontend authorization.

---

# 14. Resource-Level Authorization

For resource-based APIs, authorization must validate ownership or access.

Example:

```text
GET /api/v1/projects/{project_id}
```

The backend must verify that the current user can access that specific project.

Never assume that knowing a resource ID grants access.

---

# 15. Pagination

Collection endpoints should support pagination.

Example:

```text
GET /api/v1/projects?page=1&page_size=20
```

For large datasets, cursor-based pagination may be preferred:

```text
GET /api/v1/projects?limit=20&cursor=<cursor>
```

The API must define:

* Maximum page size
* Default page size
* Pagination mechanism
* Ordering behavior

---

# 16. Filtering

Filtering should use query parameters.

Example:

```text
GET /api/v1/projects?status=active
```

Multiple filters:

```text
GET /api/v1/projects?status=active&owner_id=123
```

Filtering behavior must be documented.

---

# 17. Sorting

Sorting should use query parameters.

Example:

```text
GET /api/v1/projects?sort=created_at&order=desc
```

Only approved sortable fields should be accepted.

Do not directly inject user-provided query strings into SQL.

---

# 18. Search

Search endpoints should clearly define search semantics.

Example:

```text
GET /api/v1/projects?search=payment
```

Search implementation may use:

* PostgreSQL search
* Elasticsearch/OpenSearch
* Vector search
* Qdrant
* Other approved search systems

The API layer should remain independent of the underlying search implementation.

---

# 19. Idempotency

Operations that may be retried should support idempotency when appropriate.

Example:

```text
POST /api/v1/payments
Idempotency-Key: <unique-key>
```

This prevents duplicate operations when clients retry requests.

Idempotency is especially important for:

* Payments
* Orders
* Deployments
* Resource creation
* External service operations

---

# 20. Asynchronous APIs

Long-running operations should not keep HTTP connections open unnecessarily.

Example:

```text
POST /api/v1/projects/{project_id}/generate
```

Response:

```json
{
  "job_id": "job-123",
  "status": "accepted"
}
```

Client can then query:

```text
GET /api/v1/jobs/{job_id}
```

Flow:

```text
Request
   ↓
API
   ↓
Create Job
   ↓
202 Accepted
   ↓
Background Worker
   ↓
Job Status
```

---

# 21. Agentic SDLC API

The Agentic SDLC platform may expose APIs such as:

```text
POST /api/v1/projects
POST /api/v1/projects/{project_id}/generate
GET  /api/v1/projects/{project_id}
GET  /api/v1/projects/{project_id}/status
GET  /api/v1/jobs/{job_id}
POST /api/v1/projects/{project_id}/approve
POST /api/v1/projects/{project_id}/deploy
```

Long-running AI workflows should normally return a `job_id` rather than blocking the request.

---

# 22. Agent Workflow API

Agent workflow execution should expose meaningful states.

Example:

```text
created
queued
running
waiting_for_approval
completed
failed
cancelled
```

Example response:

```json
{
  "job_id": "job-123",
  "status": "running",
  "current_agent": "backend_agent",
  "progress": 65
}
```

Do not expose internal chain-of-thought or hidden reasoning.

---

# 23. Webhooks

Webhooks may be used for asynchronous event notifications.

Example:

```text
Agent Workflow
      ↓
Deployment Completed
      ↓
Webhook
      ↓
External System
```

Webhook endpoints must:

* Authenticate requests
* Validate payloads
* Verify signatures where supported
* Handle retries
* Be idempotent
* Log relevant events

---

# 24. File Upload APIs

File uploads must validate:

* File size
* File type
* File extension
* Content type
* Filename
* Storage destination

Example:

```text
POST /api/v1/projects/{project_id}/documents
```

Large files should preferably be uploaded directly to object storage using controlled pre-signed URLs.

---

# 25. Streaming APIs

Streaming may be used for:

* AI responses
* Long-running workflow progress
* Real-time status
* Logs

Possible technologies:

* Server-Sent Events
* WebSockets
* HTTP streaming

Streaming should not expose sensitive internal information.

---

# 26. Rate Limiting

Rate limiting should be applied to APIs where abuse or excessive usage is possible.

Examples:

```text
Authentication endpoints
AI generation endpoints
Deployment endpoints
File upload endpoints
Public APIs
```

Possible implementation:

```text
Client
   ↓
API Gateway / Middleware
   ↓
Redis
   ↓
Rate Limit Check
```

Rate limits should return:

```text
429 Too Many Requests
```

when exceeded.

---

# 27. API Security

APIs must protect against:

* SQL injection
* Command injection
* XSS
* SSRF
* Path traversal
* Broken access control
* Authentication bypass
* Excessive request sizes
* Malicious file uploads
* Credential leakage

Use parameterized database queries and validated inputs.

---

# 28. CORS

CORS must be explicitly configured.

Do not use unrestricted origins in production unless there is a documented requirement.

Avoid:

```text
allow_origins=["*"]
```

for authenticated production APIs unless explicitly justified.

---

# 29. Secrets

API keys, tokens, passwords, and credentials must never be hardcoded.

Use:

* Environment variables
* AWS Secrets Manager
* Secure CI/CD secrets
* Approved secret-management systems

Never return secrets through API responses.

---

# 30. API Logging

API logs should include useful observability information.

Example:

```text
request_id
method
path
status_code
latency
user/service identity
timestamp
```

Do not log:

* Passwords
* Tokens
* API keys
* Authorization headers
* Sensitive request bodies

---

# 31. Request ID / Correlation ID

Every request should have a correlation identifier.

Example:

```text
Client
   ↓
request_id
   ↓
API
   ↓
Agent
   ↓
Database
   ↓
External Service
```

This allows failures to be traced across distributed components.

---

# 32. API Architecture

FastAPI applications should generally follow:

```text
Request
   ↓
Router
   ↓
Schema Validation
   ↓
Authentication
   ↓
Authorization
   ↓
Service Layer
   ↓
Repository / External Service
   ↓
Response Schema
   ↓
Client
```

Route handlers should remain thin.

Business logic should primarily exist in the service layer.

---

# 33. FastAPI Project Structure

Recommended structure:

```text
api/
├── main.py
├── routes/
│   ├── projects.py
│   ├── jobs.py
│   └── health.py
├── schemas/
├── services/
├── repositories/
├── dependencies/
├── middleware/
└── exceptions/
```

The exact structure may vary according to project complexity.

---

# 34. API Documentation

All production APIs must be documented.

FastAPI applications should use OpenAPI documentation.

Documentation should describe:

* Endpoint
* HTTP method
* Parameters
* Request body
* Response
* Status codes
* Authentication
* Errors
* Examples

API documentation should remain synchronized with implementation.

---

# 35. API Testing

API testing should include:

* Unit tests
* Integration tests
* Authentication tests
* Authorization tests
* Validation tests
* Error handling tests
* Rate-limit tests
* Security tests
* Contract tests
* End-to-end tests

Example:

```text
Client
   ↓
API
   ↓
Service
   ↓
Database
```

Integration tests should validate this complete interaction where appropriate.

---

# 36. Backward Compatibility

Changes to production APIs must consider existing clients.

Avoid breaking changes such as:

* Removing fields
* Renaming fields
* Changing data types
* Changing endpoint semantics
* Removing endpoints

Breaking changes should use versioning or an approved migration strategy.

---

# 37. API Deprecation

Deprecated endpoints should have a defined lifecycle.

Example:

```text
Active
  ↓
Deprecated
  ↓
Migration Period
  ↓
Removed
```

Clients should receive appropriate documentation and migration guidance.

---

# 38. Health and Readiness APIs

Production services should expose health endpoints where appropriate.

Example:

```text
GET /health
GET /ready
```

Health checks should distinguish between:

```text
Liveness
Readiness
Dependency Health
```

A readiness failure should not necessarily mean the application process itself has crashed.

---

# 39. API and Database Separation

API handlers must not directly depend on database implementation details.

Preferred:

```text
API Router
    ↓
Service
    ↓
Repository
    ↓
Database
```

Avoid:

```text
API Router
    ↓
Raw SQL Everywhere
```

This improves:

* Testability
* Maintainability
* Separation of concerns
* Future database changes

---

# 40. API and Agent Separation

AI agents should not directly manipulate HTTP requests without controlled interfaces.

Preferred:

```text
Agent
  ↓
Approved Tool
  ↓
Service/API
  ↓
Resource
```

Agent access must be controlled through:

* Tool definitions
* Authentication
* Authorization
* Guardrails
* Validation
* Audit logging

---

# 41. MCP Integration

When MCP tools expose APIs or external services:

```text
Agent
   ↓
MCP Client
   ↓
MCP Server
   ↓
API / External Service
```

MCP tools must:

* Validate arguments
* Enforce permissions
* Restrict available operations
* Handle failures
* Avoid exposing secrets
* Log important operations

Destructive operations should require explicit authorization.

---

# 42. API Error Handling

Errors should be handled centrally where practical.

The application should define consistent exceptions for:

```text
ValidationError
AuthenticationError
AuthorizationError
NotFoundError
ConflictError
ExternalServiceError
InternalServerError
```

Internal exceptions should not be exposed directly to clients.

---

# 43. External API Integration

External services should be accessed through dedicated service or integration layers.

Example:

```text
FastAPI
   ↓
Service
   ↓
GitHub Client
   ↓
GitHub API
```

External API integrations should include:

* Timeout
* Retry policy
* Error handling
* Authentication
* Rate-limit handling
* Circuit-breaking where necessary
* Observability

Never retry non-idempotent operations blindly.

---

# 44. API Performance

API performance should consider:

* Response latency
* Database query time
* External API latency
* Serialization overhead
* Connection pooling
* Caching
* Payload size
* Concurrent requests

Long-running operations should be asynchronous.

---

# 45. API Scalability

APIs should be designed to support horizontal scaling.

Example:

```text
             ┌── API Instance 1
Load Balancer ├── API Instance 2
             └── API Instance 3
                    ↓
                PostgreSQL
                    +
                  Redis
```

Application instances should remain stateless whenever practical.

Persistent state should be stored in appropriate external systems.

---

# 46. API Design Template

Every API designed by an AI agent must follow this template.

## Endpoint

```text
Name:
Purpose:
HTTP Method:
Path:
Authentication:
Authorization:
```

## Request

```text
Path Parameters:
Query Parameters:
Headers:
Request Body:
Validation Rules:
```

## Response

```text
Success Status:
Response Schema:
Example Response:
```

## Errors

```text
400:
401:
403:
404:
409:
422:
429:
500:
```

## Security

```text
Input Validation:
Authentication:
Authorization:
Rate Limiting:
Sensitive Data:
Audit Requirements:
```

## Performance

```text
Expected Traffic:
Pagination:
Caching:
Timeout:
Async Processing:
```

## Dependencies

```text
Database:
Redis:
External APIs:
MCP Tools:
AI Agents:
```

## Testing

```text
Unit Tests:
Integration Tests:
Security Tests:
Error Cases:
Performance Tests:
```

---

# 47. Agent-Generated API Design

When an AI agent designs an API, it must:

1. Read approved requirements.
2. Read architecture standards.
3. Read database design.
4. Identify required resources.
5. Define endpoints.
6. Define request schemas.
7. Define response schemas.
8. Define status codes.
9. Define authentication.
10. Define authorization.
11. Define validation.
12. Define error handling.
13. Define pagination where required.
14. Define asynchronous processing where required.
15. Define security requirements.
16. Define testing requirements.
17. Generate API documentation.
18. Validate the design before implementation.

The agent must not generate endpoints without understanding the underlying business requirements.

---

# 48. Expected API Design Artifacts

The API Design Agent should produce:

```text
Requirements
      ↓
API Resource Model
      ↓
Endpoint Definitions
      ↓
Request Schemas
      ↓
Response Schemas
      ↓
Error Model
      ↓
Authentication / Authorization
      ↓
Security Rules
      ↓
Pagination / Filtering
      ↓
Async Job Design
      ↓
OpenAPI Documentation
      ↓
API Implementation
      ↓
API Tests
```

---

# 49. API Design Checklist

Before implementation, verify:

* [ ] Resources identified
* [ ] Endpoints defined
* [ ] HTTP methods selected correctly
* [ ] API version defined
* [ ] Request schemas defined
* [ ] Response schemas defined
* [ ] Validation rules defined
* [ ] HTTP status codes defined
* [ ] Error response format defined
* [ ] Authentication defined
* [ ] Authorization defined
* [ ] Resource-level authorization considered
* [ ] Pagination considered
* [ ] Filtering considered
* [ ] Sorting considered
* [ ] Idempotency considered
* [ ] Async processing considered
* [ ] Rate limiting considered
* [ ] CORS configured
* [ ] Security requirements defined
* [ ] Logging requirements defined
* [ ] Request correlation ID defined
* [ ] API documentation defined
* [ ] Testing strategy defined
* [ ] Backward compatibility considered
* [ ] External API dependencies identified
* [ ] MCP integration secured where required
* [ ] Agent access controlled where required
* [ ] Health/readiness endpoints considered

---

# 50. Agentic SDLC API Rule

> **API design must be derived from approved requirements, architecture, and database design; use consistent resource-oriented endpoints, validated schemas, proper authentication and authorization, standardized errors and status codes, secure agent/tool access, asynchronous processing for long-running workflows, complete API documentation, and production-ready testing before implementation.**


# 4A. Concrete API Naming Conventions

All APIs generated by the Agentic SDLC platform must follow these naming conventions.

## 1. Base Path

Use:

```text
/api/{version}/{resource}
```

Example:

```text
/api/v1/projects
/api/v1/users
/api/v1/orders
```

Avoid:

```text
/api/projects
/api/projectAPI
/api/v1/getProjects
```

---

## 2. Version Naming

Use lowercase `v` followed by the version number:

```text
/v1
/v2
/v3
```

Example:

```text
/api/v1/projects
```

Do not use:

```text
/api/version1/projects
/api/V1/projects
```

---

## 3. Resource Naming

Resource names must:

* Be lowercase
* Use plural nouns
* Use `kebab-case` for multi-word resources

Examples:

```text
/api/v1/users
/api/v1/projects
/api/v1/project-tasks
/api/v1/generated-artifacts
/api/v1/deployment-records
```

Avoid:

```text
/api/v1/User
/api/v1/project
/api/v1/getProjects
/api/v1/project_tasks
/api/v1/ProjectTasks
```

---

## 4. Nested Resources

Use nested resources when the child resource belongs directly to the parent.

Example:

```text
/api/v1/projects/{project_id}/tasks
/api/v1/projects/{project_id}/documents
/api/v1/projects/{project_id}/deployments
```

Example:

```text
GET /api/v1/projects/123/tasks
```

Avoid excessive nesting.

Avoid:

```text
/api/v1/users/{user_id}/projects/{project_id}/tasks/{task_id}/results
```

Prefer a direct resource endpoint when the relationship does not need to be represented in the URL:

```text
/api/v1/task-results/{task_result_id}
```

---

## 5. Path Parameter Naming

Use descriptive `snake_case` identifiers inside `{}`.

Preferred:

```text
/projects/{project_id}
/users/{user_id}
/tasks/{task_id}
/jobs/{job_id}
```

Avoid:

```text
/projects/{id}
/projects/{projectId}
/projects/{project-ID}
/projects/{PROJECT_ID}
```

---

## 6. Query Parameter Naming

Use lowercase `snake_case`.

Preferred:

```text
?page=1&page_size=20
?created_after=2026-01-01
?project_id=123
?sort_by=created_at
```

Avoid:

```text
?pageSize=20
?CreatedAfter=2026-01-01
?projectId=123
?sortBy=created_at
```

---

## 7. Boolean Query Parameters

Use clear boolean names.

Preferred:

```text
?is_active=true
?include_deleted=false
?include_metadata=true
```

Avoid ambiguous names:

```text
?active=1
?deleted=0
?metadata=yes
```

---

## 8. Filtering Parameters

Use the field name directly when filtering.

Preferred:

```text
/api/v1/projects?status=active
/api/v1/tasks?priority=high
/api/v1/users?role=admin
```

For ranges:

```text
?created_after=2026-01-01
?created_before=2026-09-01
```

Avoid action-style filters:

```text
?filterByStatus=active
?getActiveProjects=true
```

---

## 9. Sorting Parameters

Use:

```text
sort_by
sort_order
```

Example:

```text
/api/v1/projects?sort_by=created_at&sort_order=desc
```

Allowed values should be explicitly defined.

Example:

```text
sort_order=asc
sort_order=desc
```

Never allow arbitrary SQL expressions through sorting parameters.

---

## 10. Pagination Parameters

Use consistent names across APIs.

Preferred:

```text
?page=1&page_size=20
```

or cursor-based:

```text
?limit=20&cursor=abc123
```

Do not mix naming styles across endpoints.

Avoid:

```text
?pageNumber=1
?itemsPerPage=20
?record_count=20
```

---

## 11. Action Endpoints

REST APIs should prefer resources and HTTP methods over action names.

Preferred:

```text
POST /api/v1/projects
PATCH /api/v1/projects/{project_id}
DELETE /api/v1/projects/{project_id}
```

Avoid:

```text
POST /api/v1/createProject
POST /api/v1/updateProject
POST /api/v1/deleteProject
```

However, explicit action endpoints may be used when an operation is not naturally represented as CRUD.

Examples:

```text
POST /api/v1/projects/{project_id}/deploy
POST /api/v1/projects/{project_id}/approve
POST /api/v1/projects/{project_id}/cancel
```

Use action names as lowercase verbs.

---

## 12. Agentic SDLC Endpoint Naming

The Agentic SDLC platform should follow:

```text
/api/v1/projects
/api/v1/projects/{project_id}
/api/v1/projects/{project_id}/requirements
/api/v1/projects/{project_id}/tasks
/api/v1/projects/{project_id}/artifacts
/api/v1/projects/{project_id}/deployments
/api/v1/projects/{project_id}/deploy
/api/v1/jobs/{job_id}
/api/v1/jobs/{job_id}/status
```

For example:

```text
POST /api/v1/projects/{project_id}/generate
```

starts application generation.

The API should return a job identifier for long-running workflows:

```json
{
  "job_id": "job-123",
  "status": "accepted"
}
```

Then:

```text
GET /api/v1/jobs/{job_id}
```

retrieves the job status.

---

## 13. Header Naming

Use standard HTTP headers where available.

Custom headers should use clear names.

Example:

```text
X-Request-ID
X-Correlation-ID
Idempotency-Key
```

Avoid application-specific variations such as:

```text
X-Req
X-RequestId
Request-ID
```

when an established standard already exists.

---

## 14. JSON Field Naming

JSON request and response fields should use `snake_case`.

Preferred:

```json
{
  "project_id": "123",
  "created_at": "2026-09-08T10:00:00Z",
  "is_active": true
}
```

Avoid:

```json
{
  "projectId": "123",
  "createdAt": "2026-09-08T10:00:00Z",
  "isActive": true
}
```

---

## 15. Enum Naming

Enum values should use lowercase `snake_case`.

Example:

```json
{
  "status": "waiting_for_approval"
}
```

Preferred:

```text
created
queued
running
waiting_for_approval
completed
failed
cancelled
```

Avoid inconsistent formats:

```text
Running
RUNNING
waitingForApproval
WAITING-FOR-APPROVAL
```

---

## 16. Endpoint Naming Examples

| Purpose          | Preferred                                     | Avoid                          |
| ---------------- | --------------------------------------------- | ------------------------------ |
| List projects    | `GET /api/v1/projects`                        | `GET /api/v1/getProjects`      |
| Get project      | `GET /api/v1/projects/{project_id}`           | `GET /api/v1/project/{id}`     |
| Create project   | `POST /api/v1/projects`                       | `POST /api/v1/createProject`   |
| Update project   | `PATCH /api/v1/projects/{project_id}`         | `POST /api/v1/updateProject`   |
| Delete project   | `DELETE /api/v1/projects/{project_id}`        | `POST /api/v1/deleteProject`   |
| List tasks       | `GET /api/v1/projects/{project_id}/tasks`     | `GET /api/v1/getProjectTasks`  |
| Start generation | `POST /api/v1/projects/{project_id}/generate` | `POST /api/v1/generateProject` |
| Deploy project   | `POST /api/v1/projects/{project_id}/deploy`   | `POST /api/v1/deployProject`   |
| Get job          | `GET /api/v1/jobs/{job_id}`                   | `GET /api/v1/getJobStatus`     |

---

## 17. API Naming Rule

> **All APIs generated by the Agentic SDLC platform must use versioned, lowercase, resource-oriented URLs; plural resource names; descriptive `snake_case` parameters and JSON fields; standard HTTP methods; and explicit action endpoints only when an operation cannot naturally be represented as CRUD.**
