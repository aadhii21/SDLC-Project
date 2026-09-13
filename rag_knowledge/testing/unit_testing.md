# Unit Testing Standards

## 1. Purpose

Define standards for creating reliable, fast, isolated, deterministic, and maintainable unit tests for backend applications and Agentic AI systems.

Unit tests must validate individual functions, classes, services, utilities, and isolated business logic without depending on external infrastructure.

---

# 2. Unit Testing Standards Summary

Unit tests must be:

* Fast
* Deterministic
* Isolated
* Repeatable
* Readable
* Maintainable
* Independent
* Focused on one behavior
* Easy to debug

Preferred framework:

```text
pytest
```

Supporting tools:

```text
pytest-asyncio
pytest-cov
unittest.mock
```

---

# 3. Definition of Unit Test

A unit test validates one small unit of application behavior independently.

Examples:

```text
Function
Class
Service method
Validation function
Business rule
Utility function
Agent decision logic
RAG transformation logic
```

A unit test should not require:

```text
Real database
Real AWS resources
Real external API
Real LLM
Real vector database
Real Jenkins server
Real GitHub repository
```

Those belong primarily to integration or E2E testing.

---

# 4. Unit Testing Goals

Unit testing must verify:

```text
Input
  ↓
Business Logic
  ↓
Expected Output
```

It should also verify:

```text
Invalid Input
      ↓
Expected Exception / Error
```

The objective is to detect defects as early as possible.

---

# 5. Unit Isolation

Each unit test must execute independently.

Example:

```python
def test_calculate_total():
    result = calculate_total(100, 10)

    assert result == 110
```

The test should not depend on another test having executed first.

Avoid:

```python
global_state = {}
```

or tests that require execution in a specific order.

---

# 6. What Should Be Unit Tested

Unit tests should cover:

* Business logic
* Service methods
* Utility functions
* Validation logic
* Data transformation
* Error handling
* Exception handling
* Configuration logic
* Authentication logic
* Authorization logic
* Retry logic
* Timeout handling
* Idempotency logic
* Agent decision logic
* Tool-selection logic
* RAG transformation logic
* LLM response parsing

---

# 7. What Should Not Be Unit Tested

Do not use unit tests as a replacement for:

* Database integration tests
* Real API integration tests
* End-to-end tests
* Infrastructure tests
* Real AWS deployment tests
* Real Jenkins execution tests

For example:

```text
Service → PostgreSQL
```

The service business logic can be unit tested with mocks.

Actual PostgreSQL interaction belongs in integration testing.

---

# 8. Test Project Structure

Recommended structure:

```text
tests/
├── unit/
│   ├── test_services.py
│   ├── test_repositories.py
│   ├── test_utils.py
│   ├── test_validators.py
│   ├── test_agents.py
│   ├── test_rag.py
│   └── test_security.py
│
├── conftest.py
└── fixtures/
```

Tests should mirror important application components.

Example:

```text
app/services/project_service.py

tests/unit/test_project_service.py
```

---

# 9. Test Naming Standards

Test names must clearly describe behavior.

Preferred:

```python
def test_create_project_returns_project():
    ...
```

```python
def test_create_project_raises_error_when_name_is_empty():
    ...
```

Avoid:

```python
def test_project():
    ...
```

Test names should communicate:

```text
What is tested
+
Condition
+
Expected result
```

---

# 10. Arrange-Act-Assert

Use the AAA pattern.

```python
def test_calculate_total():
    # Arrange
    price = 100
    tax = 10

    # Act
    result = calculate_total(price, tax)

    # Assert
    assert result == 110
```

Structure:

```text
Arrange
   ↓
Act
   ↓
Assert
```

---

# 11. One Behavior per Test

Each test should focus on one primary behavior.

Good:

```python
def test_user_creation():
    ...
```

```python
def test_user_creation_rejects_invalid_email():
    ...
```

Avoid combining unrelated behaviors in one test.

---

# 12. Deterministic Tests

The same test must produce the same result when executed repeatedly.

Avoid uncontrolled:

```python
random
datetime.now()
external network
environment-dependent state
```

Use controlled values.

Example:

```python
def test_expiry():
    current_time = datetime(2026, 1, 1)
    ...
```

Mock time when necessary.

---

# 13. Fast Tests

Unit tests should execute quickly.

Avoid:

```text
Network calls
Database connections
Large file operations
Real LLM requests
Cloud API calls
```

Mock external dependencies.

Fast tests allow developers and CI pipelines to run tests frequently.

---

# 14. Pure Function Testing

Pure functions are ideal candidates for unit testing.

Example:

```python
def calculate_total(price: float, tax: float) -> float:
    return price + tax
```

Test:

```python
def test_calculate_total():
    assert calculate_total(100, 10) == 110
```

Pure functions should have high unit-test coverage.

---

# 15. Business Logic Testing

Business rules must be tested independently.

Example:

```python
def is_eligible(age: int) -> bool:
    return age >= 18
```

Tests:

```python
def test_user_is_eligible_when_age_is_18():
    assert is_eligible(18) is True
```

```python
def test_user_is_not_eligible_when_age_is_below_18():
    assert is_eligible(17) is False
```

---

# 16. Service Layer Unit Tests

Service-layer business logic should be heavily unit tested.

Example:

```python
class ProjectService:

    def __init__(self, repository):
        self.repository = repository

    def create_project(self, name: str):
        if not name:
            raise ValueError("Project name is required")

        return self.repository.create(name)
```

Test:

```python
from unittest.mock import Mock

def test_create_project():
    repository = Mock()
    repository.create.return_value = {"id": 1, "name": "Demo"}

    service = ProjectService(repository)

    result = service.create_project("Demo")

    assert result["name"] == "Demo"
    repository.create.assert_called_once_with("Demo")
```

---

# 17. Repository Unit Tests

Repository business behavior can be unit tested by mocking database dependencies.

Example:

```python
def test_repository_calls_database():
    db = Mock()

    repository = ProjectRepository(db)

    repository.create("Demo")

    db.add.assert_called_once()
```

Actual SQL/database behavior should additionally be tested through integration tests.

---

# 18. API Layer Unit Testing

HTTP behavior should primarily be validated through API tests.

However, route-related helper logic can be unit tested independently.

Example:

```python
def build_project_response(project):
    return {
        "id": project.id,
        "name": project.name
    }
```

Test:

```python
def test_build_project_response():
    project = Mock(id=1, name="Demo")

    result = build_project_response(project)

    assert result == {
        "id": 1,
        "name": "Demo"
    }
```

---

# 19. Dependency Injection

Dependencies must be injectable so they can be replaced during unit testing.

Example:

```python
class ProjectService:

    def __init__(self, repository):
        self.repository = repository
```

Test:

```python
mock_repository = Mock()

service = ProjectService(mock_repository)
```

Avoid hard-coding dependencies inside business logic.

---

# 20. Mocking Standards

Use mocks for external dependencies.

Example:

```python
from unittest.mock import Mock

github_client = Mock()
github_client.get_repository.return_value = {
    "name": "demo"
}
```

Mock:

```text
Database
External APIs
AWS clients
GitHub
Jenkins
LLM providers
Vector databases
File systems
Message queues
```

when testing isolated business logic.

---

# 21. Mock vs Stub vs Fake

### Mock

Used to verify interactions.

```python
repository.save.assert_called_once()
```

### Stub

Provides controlled data.

```python
repository.get.return_value = project
```

### Fake

Simplified working implementation.

Example:

```text
In-memory repository
```

Use the simplest technique that keeps the test meaningful.

---

# 22. pytest Fixtures

Reusable setup should use fixtures.

Example:

```python
import pytest

@pytest.fixture
def project():
    return {
        "id": 1,
        "name": "Demo"
    }
```

Test:

```python
def test_project_name(project):
    assert project["name"] == "Demo"
```

Fixtures should remain small and reusable.

---

# 23. Parameterized Tests

Use parameterization when the same behavior must be tested with multiple inputs.

Example:

```python
import pytest

@pytest.mark.parametrize(
    "age,expected",
    [
        (18, True),
        (20, True),
        (17, False),
        (10, False),
    ]
)
def test_is_eligible(age, expected):
    assert is_eligible(age) is expected
```

This reduces duplicate test code.

---

# 24. Positive Testing

Validate expected valid behavior.

Example:

```python
def test_create_project_with_valid_name():
    result = create_project("Demo")

    assert result["name"] == "Demo"
```

Positive tests verify normal application behavior.

---

# 25. Negative Testing

Validate invalid conditions.

Example:

```python
import pytest

def test_create_project_without_name():
    with pytest.raises(ValueError):
        create_project("")
```

Negative tests must verify that invalid inputs fail safely.

---

# 26. Boundary Testing

Test values around business boundaries.

Example:

```text
Allowed minimum: 18
```

Test:

```text
17 → Fail
18 → Pass
19 → Pass
```

Boundary cases should be explicitly covered.

---

# 27. Exception Testing

Use `pytest.raises`.

Example:

```python
def test_invalid_project_raises_error():
    with pytest.raises(ValueError, match="Project name"):
        create_project("")
```

Verify both:

```text
Exception type
Exception message
```

when the message is part of the contract.

---

# 28. Async Unit Tests

Use `pytest-asyncio` for asynchronous functions.

Example:

```python
import pytest

@pytest.mark.asyncio
async def test_get_project():
    result = await get_project(1)

    assert result["id"] == 1
```

External async dependencies should use `AsyncMock`.

```python
from unittest.mock import AsyncMock

client = AsyncMock()
client.get.return_value = {"id": 1}
```

---

# 29. External API Unit Tests

Never call real external APIs in normal unit tests.

Example:

```python
from unittest.mock import AsyncMock

github_client = AsyncMock()

github_client.get_repository.return_value = {
    "name": "demo"
}
```

Test:

```python
result = await service.get_repository("demo")

assert result["name"] == "demo"
github_client.get_repository.assert_called_once_with("demo")
```

---

# 30. LLM Unit Tests

LLM calls must normally be mocked.

Example:

```python
from unittest.mock import AsyncMock

llm = AsyncMock()

llm.generate.return_value = {
    "answer": "Use FastAPI"
}
```

Test:

```python
result = await agent.generate_answer("Build an API")

assert result["answer"] == "Use FastAPI"
```

Unit tests should focus on:

* Prompt construction
* Response parsing
* Structured output validation
* Error handling
* Retry logic
* Tool selection

Real LLM behavior should be tested separately.

---

# 31. Agent Unit Tests

Agent logic must be tested independently from external tools.

Example:

```python
def choose_tool(task: str) -> str:
    if "github" in task.lower():
        return "github"

    return "default"
```

Test:

```python
def test_agent_selects_github_tool():
    assert choose_tool("Create GitHub repository") == "github"
```

Agent unit tests should validate deterministic decision logic.

---

# 32. Tool Selection Unit Tests

Test correct tool selection.

Example:

```python
def test_selects_jenkins_for_build_request():
    tool = select_tool("run Jenkins build")

    assert tool == "jenkins"
```

Also test unsupported requests:

```python
def test_returns_none_for_unknown_task():
    assert select_tool("unknown operation") is None
```

---

# 33. RAG Component Unit Tests

RAG components should be tested independently.

Example:

```python
def test_chunk_text():
    chunks = chunk_text("A" * 1000)

    assert len(chunks) > 1
```

Test:

```text
Chunking
Metadata creation
Query transformation
Filtering
Context formatting
Retrieved document processing
Prompt construction
```

Do not require a real vector database for unit tests.

---

# 34. Retry and Timeout Unit Tests

Retry logic must be tested with mocked failures.

Example:

```python
def test_retry_on_transient_error():
    client = Mock()

    client.call.side_effect = [
        TimeoutError(),
        {"status": "success"}
    ]

    result = execute_with_retry(client)

    assert result["status"] == "success"
    assert client.call.call_count == 2
```

Verify:

```text
Retry count
Backoff behavior
Transient error handling
Permanent error handling
Timeout handling
```

---

# 35. Idempotency Unit Tests

Repeated execution with the same idempotency key should not create duplicate effects.

Example:

```python
def test_same_idempotency_key_returns_existing_result():
    result1 = create_job("key-123")
    result2 = create_job("key-123")

    assert result1 == result2
```

Test duplicate prevention independently from the database implementation.

---

# 36. Security Logic Unit Tests

Security-related helper functions must have unit tests.

Examples:

```text
Authorization checks
Role validation
Permission checks
Input sanitization
Token validation logic
Path validation
Secret masking
```

Example:

```python
def test_admin_can_delete_project():
    assert can_delete_project("admin") is True
```

```python
def test_user_cannot_delete_project():
    assert can_delete_project("user") is False
```

---

# 37. Configuration Unit Tests

Configuration behavior should be tested.

Example:

```python
def test_default_environment():
    settings = Settings()

    assert settings.environment == "development"
```

Test:

```text
Required variables
Default values
Invalid configuration
Environment selection
Configuration validation
```

Never place real secrets in tests.

---

# 38. File Utility Unit Tests

File-processing utilities should be tested using temporary files.

Example:

```python
def test_read_file(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("hello")

    result = read_file(file)

    assert result == "hello"
```

Test:

```text
Valid files
Empty files
Missing files
Unsupported extensions
Large files
Invalid paths
```

---

# 39. Time and Date Unit Tests

Time-dependent logic should use controllable time.

Avoid:

```python
datetime.now()
```

directly inside business logic when deterministic testing is required.

Prefer injecting time:

```python
def is_expired(expiry_time, current_time):
    return current_time >= expiry_time
```

Test:

```python
def test_expired():
    assert is_expired(
        expiry_time=20,
        current_time=21
    ) is True
```

---

# 40. Test Data Standards

Test data must be:

* Minimal
* Meaningful
* Deterministic
* Reusable where appropriate
* Free of real secrets
* Free of production customer data

Good:

```python
{
    "id": 1,
    "name": "Test Project"
}
```

Avoid unnecessary fields.

---

# 41. Avoiding Over-Mocking

Do not mock the unit being tested.

Bad:

```python
service = Mock()
service.create_project.return_value = "success"

assert service.create_project("Demo") == "success"
```

This tests the mock rather than the application.

Correct:

```python
repository = Mock()

service = ProjectService(repository)

result = service.create_project("Demo")

assert result["name"] == "Demo"
```

Mock dependencies, not the behavior under test.

---

# 42. Assertions

Assertions must verify meaningful behavior.

Good:

```python
assert result.status == "success"
```

```python
assert repository.save.called
```

Avoid weak assertions such as:

```python
assert result is not None
```

when a stronger assertion is possible.

Prefer verifying:

```text
Value
Type
State
Exception
Interaction
Side effect
```

---

# 43. Coverage Standards

Coverage should measure meaningful tested behavior.

Run:

```bash
pytest --cov=. --cov-report=term-missing
```

Recommended minimum:

```text
80%
```

Critical business logic should target higher coverage.

Coverage alone does not guarantee quality.

---

# 44. Unit Test Quality Mindset

Tests must validate behavior rather than implementation details.

Prefer:

```text
Input → Behavior → Expected Result
```

Avoid excessive assertions against internal implementation details.

Tests should remain stable when internal code is refactored without changing behavior.

---

# 45. Local Unit Testing Commands

Run all unit tests:

```bash
pytest tests/unit/
```

Verbose:

```bash
pytest tests/unit/ -v
```

Specific file:

```bash
pytest tests/unit/test_services.py
```

Specific test:

```bash
pytest tests/unit/test_services.py::test_create_project
```

With coverage:

```bash
pytest tests/unit/ --cov=app --cov-report=term-missing
```

---

# 46. Unit Test CI Standards

CI must execute unit tests before integration and E2E tests.

Recommended order:

```text
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
API Tests
   ↓
Security Tests
   ↓
E2E Tests
```

Unit-test failures must block downstream stages.

---

# 47. Unit Test Failure Handling

When a unit test fails, identify:

```text
Test
↓
Failure
↓
Root Cause
↓
Severity
↓
Component
↓
Recommended Fix
```

Critical and High-severity failures must be resolved before deployment.

Do not simply skip failing tests.

---

# 48. Unit Testing Agent Input

The Unit Testing Agent should receive structured input.

Example:

```json
{
  "project_id": "project-001",
  "language": "python",
  "framework": "fastapi",
  "source_path": "app/",
  "requirements": [
    "business logic must be tested",
    "negative cases required",
    "minimum coverage 80%"
  ],
  "dependencies": [
    "postgresql",
    "redis",
    "github"
  ]
}
```

---

# 49. Unit Testing Agent Output

The agent should return structured results.

Example:

```json
{
  "tests_generated": 42,
  "tests_passed": 40,
  "tests_failed": 2,
  "coverage": 86,
  "critical_failures": 0,
  "high_failures": 0,
  "status": "passed"
}
```

The output must be machine-readable.

---

# 50. Unit Testing Agent Workflow

The Unit Testing Agent should follow:

```text
Receive Backend Code
        ↓
Analyze Project Structure
        ↓
Identify Testable Units
        ↓
Identify Dependencies
        ↓
Generate Unit Tests
        ↓
Generate Fixtures / Mocks
        ↓
Run pytest
        ↓
Analyze Failures
        ↓
Fix / Regenerate Tests
        ↓
Run Coverage
        ↓
Validate Coverage
        ↓
Generate Test Report
        ↓
Return Result
```

The agent must not skip test execution.

---

# 51. Unit Testing Validation Checklist

Before marking unit testing complete, verify:

* [ ] Unit test directory exists
* [ ] Business logic is tested
* [ ] Service logic is tested
* [ ] Utility functions are tested
* [ ] Positive cases exist
* [ ] Negative cases exist
* [ ] Boundary cases exist
* [ ] Exception cases exist
* [ ] Async logic is tested
* [ ] External dependencies are mocked
* [ ] LLM calls are mocked
* [ ] Agent logic is tested
* [ ] Tool selection is tested
* [ ] RAG components are tested
* [ ] Retry logic is tested
* [ ] Timeout logic is tested
* [ ] Idempotency logic is tested
* [ ] Security logic is tested
* [ ] Tests are deterministic
* [ ] Tests are isolated
* [ ] Tests are fast
* [ ] No production secrets exist
* [ ] No real external API calls occur
* [ ] Coverage meets the configured threshold
* [ ] All unit tests pass

---

# 52. Unit Testing Agent Quality Gates

The Unit Testing Agent must satisfy:

```text
Unit Tests Generated
        +
Unit Tests Executed
        +
Required Tests Passed
        +
Coverage Threshold Met
        +
No Critical Failures
        +
No High-Severity Failures
        +
No Unauthorized External Calls
        ↓
UNIT TESTING PASSED
```

Otherwise:

```text
UNIT TESTING FAILED
```

The agent must return the failure reason.

---

# 53. Final Unit Testing Rule

Generated backend code must have deterministic, isolated, maintainable unit tests covering core business logic, validation, error handling, security logic, asynchronous behavior, external dependency handling, and Agentic AI components.

Unit tests must execute successfully and satisfy the configured coverage threshold before the backend is considered ready for integration testing.

The Testing Agent must never mark unit testing as passed without actually executing the generated tests.
