# Coding Standards

## 1. General Principles

- Write clean, readable, maintainable, and reusable code.
- Follow the principle of **KISS (Keep It Simple)**.
- Avoid unnecessary complexity and duplicated code.
- Follow **DRY (Don't Repeat Yourself)**.
- Use meaningful names for variables, functions, classes, files, and modules.
- Keep functions and classes focused on a single responsibility.
- Prefer readability over clever or overly compact code.
- Write code that is easy for another developer or AI agent to understand and modify.

## 2. Python Standards

- Follow **PEP 8**.
- Use 4 spaces for indentation.
- Use `snake_case` for variables and functions.
- Use `PascalCase` for classes.
- Use `UPPER_CASE` for constants.
- Add type hints to function parameters and return values.
- Prefer explicit code over implicit behavior.
- Use `pathlib` instead of manual path string manipulation.
- Use list/dictionary comprehensions only when they improve readability.
- Avoid global mutable variables.
- Use `dataclass` or Pydantic models where appropriate.

### Example

```python
def calculate_score(
    confidence: float,
    quality: float,
) -> float:
    return confidence * quality
3. FastAPI Standards
Organize APIs using routers.
Keep API routes thin.
Business logic must be placed in service modules.
Database operations must be separated from API route handlers.
Use Pydantic models for request and response validation.
Use appropriate HTTP status codes.
Provide meaningful error responses.
Use dependency injection for shared dependencies.
Add API documentation through clear schemas and descriptions.
Recommended Structure
app/
├── main.py
├── api/
│   └── routes/
├── services/
├── models/
├── schemas/
├── repositories/
├── core/
└── utils/
4. Naming Standards

Use descriptive names.

Good
user_id
job_status
knowledge_chunks
generate_embedding()
validate_code()
Avoid
x
data1
tmp
abc()

Boolean variables should clearly represent a condition.

is_valid
has_permission
is_completed
5. Function Standards
Each function should perform one clear responsibility.
Keep functions reasonably small.
Avoid deeply nested logic.
Validate inputs at the appropriate boundary.
Return predictable values.
Raise meaningful exceptions when necessary.
Good
def validate_generated_code(code: str) -> bool:
    if not code.strip():
        return False

    return True
6. Error Handling
Never silently ignore exceptions.
Catch only exceptions that can be handled.
Use meaningful error messages.
Do not expose secrets, tokens, passwords, or internal system details in errors.
Use custom exceptions for important domain-specific failures.
Example
try:
    result = deploy_application()
except DeploymentError as exc:
    logger.error("Deployment failed: %s", exc)
    raise

Avoid:

try:
    deploy_application()
except Exception:
    pass
7. Logging
Use the Python logging module.
Do not use print() for application logging.
Log important workflow events.
Include job IDs, request IDs, or agent IDs where useful.
Never log passwords, API keys, tokens, or sensitive data.
Example
logger.info("Starting code generation for job_id=%s", job_id)
logger.error("Deployment failed for job_id=%s", job_id)
8. Environment Variables and Secrets
Never hardcode secrets in source code.
Store configuration in environment variables or a secure secret manager.
Do not commit .env files containing real secrets.
Provide .env.example with placeholder values.
Good
api_key = os.getenv("OPENAI_API_KEY")
Bad
api_key = "sk-real-secret-key"
9. Database Standards
Use parameterized queries.
Never construct SQL using unsafe string concatenation.
Use migrations for schema changes.
Keep database access inside repository/data-access layers.
Use transactions for operations that must be atomic.
Add indexes for frequently queried fields where appropriate.
10. API Response Standards

Use consistent response structures.

Example:

{
  "status": "success",
  "data": {},
  "message": "Operation completed successfully"
}

For errors:

{
  "status": "error",
  "message": "Invalid request"
}
11. Testing Standards
Write unit tests for business logic.
Write integration tests for important API/database interactions.
Test both successful and failure scenarios.
Use meaningful test names.
Tests must be deterministic.
Avoid depending on external services in unit tests.
Mock external services where appropriate.
Example
def test_validate_code_returns_false_for_empty_code():
    assert validate_generated_code("") is False
12. Agentic AI Standards

For AI agents:

Give every agent a clearly defined responsibility.
Avoid giving one agent unnecessary responsibilities.
Define clear inputs and outputs.
Validate agent outputs before passing them to another agent.
Do not blindly trust LLM-generated code or decisions.
Use structured outputs whenever possible.
Add guardrails for security-sensitive operations.
Maintain traceability between jobs, agents, tools, and generated artifacts.
Example Agent Flow
User Request
     ↓
Planner Agent
     ↓
Developer Agent
     ↓
Testing Agent
     ↓
Security Agent
     ↓
Deployment Agent
13. LLM Usage Standards
Use structured prompts.
Clearly define the agent's role and responsibilities.
Provide relevant context only.
Use RAG when organizational knowledge is required.
Validate generated responses.
Do not expose confidential information through prompts.
Avoid unnecessarily large prompts.
Store important prompts as version-controlled configuration where appropriate.
14. RAG Standards
Chunk documents logically.
Preserve document metadata.
Generate embeddings consistently.
Use appropriate similarity search.
Retrieve only relevant context.
Do not blindly trust retrieved documents.
Include source metadata where possible.
Keep knowledge documents version controlled.

Recommended metadata:

{
  "source": "coding_standards.md",
  "category": "company",
  "version": "1.0",
  "last_updated": "2026-09-08"
}
15. Generated Code Standards

AI-generated code must:

Follow project coding standards.
Pass formatting and linting checks.
Pass automated tests.
Pass security checks.
Avoid hardcoded secrets.
Use approved dependencies.
Be reviewed or validated before production deployment.

Generated code must never be deployed directly without validation.

16. Dependency Standards
Use only approved and necessary dependencies.
Avoid unnecessary packages.
Pin dependency versions where appropriate.
Regularly check dependencies for vulnerabilities.
Remove unused dependencies.
17. Git Standards

Use meaningful branch names.

feature/add-rag-agent
bugfix/fix-deployment-error
hotfix/security-patch

Use meaningful commit messages.

feat: add code generation agent
fix: handle deployment failure
test: add API validation tests
refactor: simplify agent workflow
docs: update deployment documentation

Do not commit:

.env
*.pem
*.key
credentials
API keys
passwords
18. Code Review Standards

Before merging code, verify:

Code follows project standards.
Tests are included.
Tests pass.
No secrets are committed.
Error handling is appropriate.
Security implications are considered.
Documentation is updated where necessary.
Unnecessary code or dependencies are removed.
19. File Organization

Keep responsibilities separated.

src/
├── agents/
├── api/
├── services/
├── repositories/
├── models/
├── schemas/
├── tools/
├── workflows/
├── utils/
└── config/

Avoid placing the entire application inside a single file.

20. Documentation
Document complex business logic.
Document public APIs.
Document important configuration.
Use docstrings for reusable functions and classes.
Keep documentation synchronized with code changes.

Avoid comments that simply repeat the code.

Bad
# Add two numbers
result = a + b
Good
# Calculate the final score after applying the confidence multiplier.
result = score * confidence
21. Code Quality Checklist

Before code is considered complete:

 Code follows PEP 8.
 Naming is meaningful.
 Type hints are used.
 Functions have clear responsibilities.
 Errors are handled appropriately.
 Logging is implemented where required.
 No secrets are hardcoded.
 Tests are added.
 Tests pass.
 Security checks pass.
 Unused dependencies are removed.
 Documentation is updated.
22. Agentic SDLC Rule

Every generated application should follow this lifecycle:

Requirement
    ↓
Planning
    ↓
Code Generation
    ↓
Code Validation
    ↓
Testing
    ↓
Security Validation
    ↓
Docker Build
    ↓
CI/CD
    ↓
Deployment
    ↓
Monitoring

No agent should bypass validation, testing, security, or deployment controls.