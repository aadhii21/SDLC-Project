# Git Standards

## 1. General Principles

- Use Git for version control of all source code and configuration.
- Keep commits small, focused, and logically organized.
- Do not commit secrets or sensitive information.
- Keep the main branch stable.
- Use pull requests for code integration.
- Review changes before merging.

## 2. Branch Naming

Use descriptive branch names.

```text
feature/add-research-agent
feature/add-rag-retrieval
bugfix/fix-agent-timeout
bugfix/fix-api-validation
hotfix/production-deployment
refactor/improve-agent-workflow
docs/update-security-standards
test/add-rag-tests

Avoid vague names:

test
new
changes
mybranch
temp
3. Main Branches

Recommended branches:

main
develop
feature/*
bugfix/*
hotfix/*
Main
Represents production-ready code.
Must remain stable.
Production deployments should originate from approved changes in main.
Develop
Contains integrated development changes.
Features are merged here before production.
Feature
Used for new functionality.
Bugfix
Used for fixing non-production bugs.
Hotfix
Used for urgent production fixes.
4. Commit Messages

Use clear and meaningful commit messages.

Recommended format:

<type>: <description>

Examples:

feat: add research agent
feat: implement RAG retrieval
fix: handle deployment timeout
fix: validate project request
test: add agent workflow tests
refactor: simplify graph state
docs: update deployment documentation
chore: update dependencies

Avoid:

updated code
changes
final
test
asdf
working
5. Commit Types

Use:

Type	Purpose
feat	New functionality
fix	Bug fix
refactor	Code restructuring without behavior change
test	Test changes
docs	Documentation changes
chore	Maintenance tasks
security	Security-related changes
ci	CI/CD changes
6. Commit Best Practices
One commit should represent one logical change.
Keep commit messages concise.
Do not commit generated files unnecessarily.
Do not commit debugging code.
Do not commit temporary files.
Do not commit commented-out experimental code.
7. Pull Request Standards

Every pull request should:

Have a clear title.
Explain what was changed.
Explain why the change was required.
Include relevant tests.
Pass CI/CD checks.
Pass security checks.
Avoid unrelated changes.
Be reviewed before merging.

Example PR title:

Add backend agent for FastAPI project generation
8. Pull Request Checklist

Before merging:

 Code follows coding standards.
 Tests are added or updated.
 All tests pass.
 Security checks pass.
 No secrets are committed.
 Documentation is updated where required.
 No unnecessary files are included.
 CI/CD pipeline passes.
 Code review is completed.
9. Git Ignore Standards

The repository must not track sensitive or unnecessary files.

Example .gitignore entries:

.env
.env.*
!.env.example

__pycache__/
*.pyc

.venv/
venv/

.pytest_cache/
.mypy_cache/

.idea/
.vscode/

*.log

*.pem
*.key

terraform/.terraform/
*.tfstate
*.tfstate.*
crash.log

generated_projects/*
!generated_projects/.gitkeep
10. Secrets

Never commit:

API keys
AWS access keys
AWS secret keys
Passwords
JWT secrets
Private keys
SSH keys
Database credentials
Cloud credentials

If a secret is accidentally committed:

Revoke the secret immediately.
Rotate the credential.
Remove it from the repository history if required.
Check logs and CI/CD systems for exposure.
11. Generated Files

Avoid committing automatically generated files unless they are explicitly required.

Examples:

__pycache__/
*.pyc
build/
dist/
coverage/
logs/
temporary files

Generated application projects should generally remain outside the platform source-control history unless explicitly required.

12. Merge Standards
Prefer pull requests over direct pushes to protected branches.
Resolve merge conflicts before merging.
Do not overwrite another developer's changes without review.
Avoid unnecessary merge commits.
Keep branches synchronized with the target branch.
13. Rebase Standards

Rebase feature branches when appropriate to keep history clean.

Example:

git checkout feature/my-feature
git fetch origin
git rebase origin/develop

Do not rebase shared branches that other developers are actively using unless agreed upon.

14. Protected Branches

Production branches should be protected.

Recommended controls:

Require pull requests.
Require code review.
Require successful CI checks.
Prevent force pushes.
Prevent direct pushes where appropriate.
15. Git Tags

Use Git tags for important releases.

Example:

v1.0.0
v1.1.0
v1.1.1

Semantic versioning should follow:

MAJOR.MINOR.PATCH

Example:

v2.1.3
16. Release Standards

A release should only be created after:

Code Review
     ↓
Tests
     ↓
Security Checks
     ↓
CI/CD Validation
     ↓
Release Tag
     ↓
Deployment
17. Agentic SDLC Git Rules

AI agents interacting with Git must:

Use the correct repository and branch.
Never push directly to protected production branches unless explicitly authorized.
Create descriptive commits.
Never commit secrets.
Review generated changes before committing.
Run tests before creating a pull request.
Avoid destructive Git operations unless explicitly authorized.

AI agents must not execute commands such as:

git reset --hard
git push --force
git branch -D

on shared or production branches without explicit authorization.

18. Git Security Rule

Git repositories are considered production assets.

All source-code changes must maintain:

Traceability
    ↓
Code Review
    ↓
Testing
    ↓
Security Validation
    ↓
Controlled Merge

No AI agent or developer should bypass these controls for production code.