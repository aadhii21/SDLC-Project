# React Development Standards

## 1. Purpose

This document defines standards for generating, reviewing, testing, and maintaining React frontend applications within the Agentic SDLC platform.

The Frontend Agent must follow these standards when generating frontend code.

The frontend must be:

* Maintainable
* Modular
* Responsive
* Accessible
* Secure
* Testable
* Performant
* Consistent with the approved Figma design
* Consistent with the API and System Design

---

# 2. Frontend Source of Truth

The Frontend Agent must treat the approved Figma design as the primary UI/UX source of truth.

The workflow is:

```text
Requirements
     ↓
Design Agent
     ↓
Figma UI/UX Design
     ↓
Figma URL
     ↓
Frontend Agent
     ↓
React Implementation
```

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

The generated UI should match:

* Layout
* Components
* Typography
* Spacing
* Colors
* Navigation
* Forms
* Tables
* Cards
* States
* Responsive behavior
* User flows

---

# 3. React Project Structure

Use a modular structure.

Recommended:

```text
src/
├── components/
├── pages/
├── layouts/
├── hooks/
├── services/
├── api/
├── types/
├── utils/
├── constants/
├── context/
├── assets/
├── styles/
└── tests/
```

For larger applications:

```text
src/
├── features/
│   ├── auth/
│   ├── projects/
│   ├── users/
│   └── deployments/
├── components/
├── layouts/
├── hooks/
├── services/
├── api/
├── types/
├── utils/
└── tests/
```

Feature-specific code should preferably remain within its feature directory.

---

# 4. Component Design

Components should have a single clear responsibility.

Preferred:

```text
ProjectPage
 ├── ProjectHeader
 ├── ProjectSummary
 ├── ProjectTable
 └── ProjectActions
```

Avoid extremely large components containing:

* UI
* API calls
* Business logic
* State management
* Validation
* Formatting

all in one file.

---

# 5. Component Naming

Use PascalCase for React components.

Examples:

```text
ProjectCard.tsx
UserProfile.tsx
DeploymentStatus.tsx
LoginForm.tsx
```

Do not use:

```text
projectcard.tsx
user_profile.tsx
deployment-status.tsx
```

---

# 6. File Naming

Use clear and consistent naming.

Recommended:

```text
ProjectCard.tsx
useProjects.ts
projectService.ts
project.types.ts
formatDate.ts
```

Avoid vague names:

```text
helper.ts
common.ts
misc.ts
stuff.ts
```

---

# 7. Props

Props should be explicitly typed.

Example:

```typescript
interface ProjectCardProps {
  projectId: string;
  name: string;
  status: ProjectStatus;
}

export function ProjectCard({
  projectId,
  name,
  status
}: ProjectCardProps) {
  return (
    <div>
      {name}
    </div>
  );
}
```

Avoid unnecessary use of `any`.

---

# 8. TypeScript

TypeScript should be preferred for production React applications.

Use:

```text
.ts
.tsx
```

instead of JavaScript where project requirements allow it.

Types should be defined for:

* API requests
* API responses
* Component props
* Application state
* Forms
* Enums
* Error responses

---

# 9. API Integration

Frontend API calls should be separated from UI components.

Preferred:

```text
Component
    ↓
Hook
    ↓
API Service
    ↓
Backend API
```

Example:

```text
ProjectPage
    ↓
useProjects()
    ↓
projectService.getProjects()
    ↓
GET /api/v1/projects
```

Avoid placing large API implementations directly inside components.

---

# 10. API Client

A centralized API client should be used where appropriate.

Example:

```typescript
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL
});
```

The API base URL must come from configuration.

Do not hard-code:

```text
http://localhost:8000
```

inside production components.

---

# 11. API Naming

Frontend API calls must follow the approved API design.

Example:

```text
GET    /api/v1/projects
POST   /api/v1/projects
GET    /api/v1/projects/{project_id}
PUT    /api/v1/projects/{project_id}
DELETE /api/v1/projects/{project_id}
```

JSON fields should follow the backend API contract.

---

# 12. State Management

Use the simplest state management approach appropriate for the application.

Use local component state for:

* Modal visibility
* Form state
* Temporary UI state
* Dropdown state

Use shared state for:

* Authentication
* User information
* Global settings
* Shared application state

Do not introduce Redux or another global state library unless the application actually requires it.

---

# 13. Server State

Server state should be handled separately from local UI state.

For applications with significant server-state requirements, use an appropriate data-fetching solution.

Example:

```text
React Component
      ↓
Query Hook
      ↓
API
      ↓
Backend
```

The implementation should support:

* Loading state
* Error state
* Success state
* Refetching
* Cache where appropriate

---

# 14. Loading States

Every asynchronous operation should have a loading state.

Example:

```text
Loading
   ↓
Success
```

or:

```text
Loading
   ↓
Error
```

Use:

* Skeletons
* Spinners
* Disabled buttons
* Progress indicators

depending on the Figma design.

---

# 15. Error Handling

Frontend applications must handle:

* Network errors
* Authentication errors
* Authorization errors
* Validation errors
* Server errors
* Timeout errors
* Unexpected responses

Example:

```text
API Request
    │
    ├── 2xx → Success
    ├── 400 → Validation Error
    ├── 401 → Authentication
    ├── 403 → Authorization
    ├── 404 → Not Found
    ├── 429 → Rate Limited
    └── 5xx → Server Error
```

Errors should be presented with user-friendly messages.

Do not expose internal stack traces to users.

---

# 16. Forms

Forms must include:

* Input validation
* Required field validation
* Error messages
* Loading state
* Success feedback
* Accessible labels

Example:

```text
Form
 ↓
Validate
 ↓
Submit
 ↓
Loading
 ↓
Success / Error
```

---

# 17. Authentication

Authentication state should be handled centrally.

The frontend should support:

```text
Login
 ↓
Authentication
 ↓
Token / Session
 ↓
Authenticated Application
```

Protected routes should require authentication.

Example:

```text
Public Route
 ├── Login
 └── Register

Protected Route
 ├── Dashboard
 ├── Projects
 └── Settings
```

---

# 18. Authorization

The UI may hide actions that the user is not allowed to perform.

Example:

```text
Admin
 ├── Create
 ├── Edit
 ├── Delete
 └── Deploy

Developer
 ├── Create
 ├── Edit
 └── Deploy

Viewer
 └── Read
```

However, frontend authorization is not a security boundary.

The backend must enforce authorization independently.

---

# 19. Routing

Routes must be predictable and REST-aligned where appropriate.

Example:

```text
/
 /login
 /dashboard
 /projects
 /projects/:projectId
 /projects/:projectId/settings
 /projects/:projectId/deployments
```

Avoid unnecessary route nesting.

---

# 20. Responsive Design

The application must support the required screen sizes.

Consider:

```text
Desktop
Tablet
Mobile
```

The Frontend Agent must use the responsive behavior defined by Figma.

Do not simply scale desktop layouts down without considering:

* Navigation
* Tables
* Forms
* Cards
* Buttons
* Typography
* Spacing

---

# 21. Accessibility

The frontend must follow accessibility best practices.

Use:

* Semantic HTML
* Proper labels
* Keyboard navigation
* Focus states
* Accessible buttons
* Accessible forms
* Appropriate ARIA attributes
* Sufficient contrast

Example:

Prefer:

```html
<button>Delete Project</button>
```

over:

```html
<div onClick={deleteProject}>Delete</div>
```

---

# 22. UI States

Every major UI component should define:

```text
Default
Loading
Success
Error
Empty
Disabled
```

Example:

```text
Project Table

Loading → Skeleton
Success → Data
Empty → No projects message
Error → Retry option
```

---

# 23. Figma → React Mapping

The Frontend Agent should map Figma components to reusable React components.

Example:

```text
Figma Component
      ↓
React Component
```

Example:

```text
Figma:
Project Card

React:
ProjectCard.tsx
```

Repeated Figma components should become reusable React components.

---

# 24. Design Tokens

Where available, Figma design tokens should be converted into application-level tokens.

Examples:

```text
Colors
Typography
Spacing
Border Radius
Shadows
Breakpoints
```

Avoid hard-coding the same design value across many components.

---

# 25. CSS Standards

Use the project's selected styling system consistently.

Possible approaches:

* CSS Modules
* Tailwind CSS
* Styled Components
* Standard CSS

Do not mix multiple styling systems unnecessarily.

---

# 26. Environment Configuration

Frontend environment variables should use the appropriate framework convention.

Example:

```text
VITE_API_BASE_URL
```

or the equivalent for the selected framework.

Never place secrets in frontend environment variables.

Anything bundled into frontend JavaScript should be considered potentially visible to users.

---

# 27. Security

Frontend code must follow secure development practices.

Avoid:

* `dangerouslySetInnerHTML` unless necessary
* Untrusted HTML rendering
* Client-side secrets
* Sensitive information in local storage without justification
* Exposing internal APIs
* Trusting client-side authorization

User-controlled data must be safely rendered.

---

# 28. Performance

The Frontend Agent should consider:

* Lazy loading
* Code splitting
* Image optimization
* Memoization where useful
* Efficient rendering
* API request reduction
* Pagination
* Virtualization for large lists

Do not optimize prematurely.

Performance optimization should be based on actual requirements or bottlenecks.

---

# 29. Large Lists

Large datasets should not automatically be rendered entirely in the browser.

Preferred:

```text
Frontend
   ↓
Pagination / Cursor
   ↓
Backend
   ↓
Database
```

For very large client-side lists, virtualization may be used.

---

# 30. Images and Assets

Images should be:

* Optimized
* Appropriately sized
* Lazy loaded where appropriate
* Given meaningful `alt` text when applicable

Avoid unnecessarily large assets.

---

# 31. Frontend Logging

Frontend logs must not expose sensitive information.

Do not log:

```text
Access Tokens
Passwords
API Keys
Session Secrets
Sensitive User Data
```

Production logging should be controlled and appropriate for the application's observability requirements.

---

# 32. Testing

The frontend should include:

```text
Unit Tests
Component Tests
Integration Tests
E2E Tests
```

Testing should prioritize:

* User behavior
* Important workflows
* Critical components
* API interactions
* Authentication
* Error states

---

# 33. Component Testing

Components should be tested based on behavior.

Example:

```text
ProjectCard
 ├── Displays project name
 ├── Displays status
 ├── Handles click
 └── Displays correct action
```

Avoid testing implementation details unnecessarily.

---

# 34. E2E Testing

Critical user flows should have E2E tests.

Examples:

```text
Login
 ↓
Dashboard
 ↓
Create Project
 ↓
View Project
 ↓
Deploy
```

Other critical flows:

```text
Login
Create
Edit
Delete
Search
Filter
Deploy
Logout
```

---

# 35. Frontend Testing Contract

The Frontend Agent should return testable artifacts.

Example:

```json
{
  "component_tests": [
    "ProjectCard",
    "ProjectForm"
  ],
  "integration_tests": [
    "Project creation flow"
  ],
  "e2e_tests": [
    "User login",
    "Create project",
    "Deploy project"
  ]
}
```

---

# 36. Frontend Agent Input Schema

The Frontend Agent must receive structured input.

```json
{
  "project_id": "proj_123",
  "requirements": {},
  "system_design": {},
  "api_design": {},
  "figma": {
    "url": "https://www.figma.com/...",
    "source_of_truth": true
  },
  "frontend_standards": {},
  "backend_contract": {}
}
```

Required fields:

| Field                   | Type    | Required |
| ----------------------- | ------- | -------: |
| `project_id`            | string  |      Yes |
| `requirements`          | object  |      Yes |
| `system_design`         | object  |      Yes |
| `api_design`            | object  |      Yes |
| `figma.url`             | string  |      Yes |
| `figma.source_of_truth` | boolean |      Yes |
| `frontend_standards`    | object  |      Yes |

---

# 37. Frontend Agent Output Schema

The Frontend Agent should return a structured result.

```json
{
  "project_id": "proj_123",
  "status": "completed",
  "framework": "react",
  "language": "typescript",
  "files": [
    {
      "path": "src/pages/ProjectPage.tsx",
      "type": "source"
    },
    {
      "path": "src/components/ProjectCard.tsx",
      "type": "source"
    }
  ],
  "api_integrations": [
    "GET /api/v1/projects",
    "POST /api/v1/projects"
  ],
  "components": [
    "ProjectPage",
    "ProjectCard",
    "ProjectForm"
  ],
  "tests": [
    "ProjectCard.test.tsx",
    "ProjectPage.test.tsx"
  ],
  "figma_compliance": {
    "matched": true,
    "deviations": []
  },
  "errors": []
}
```

---

# 38. Frontend Agent Workflow

```text
Frontend Agent Input
        ↓
Validate Input
        ↓
Read Figma Design
        ↓
Read System Design
        ↓
Read API Design
        ↓
Retrieve RAG Knowledge
        ↓
Generate Component Structure
        ↓
Generate Pages
        ↓
Generate API Integration
        ↓
Generate Responsive UI
        ↓
Generate Tests
        ↓
Validate Figma Compliance
        ↓
Frontend Agent Output
```

---

# 39. Frontend Validation

Before handing the frontend to the next stage, verify:

* [ ] Figma URL available
* [ ] Figma used as source of truth
* [ ] Requirements implemented
* [ ] API contract followed
* [ ] Components modular
* [ ] TypeScript types defined
* [ ] Loading states implemented
* [ ] Error states implemented
* [ ] Empty states implemented
* [ ] Responsive behavior implemented
* [ ] Accessibility considered
* [ ] Authentication implemented where required
* [ ] Authorization UI handled where required
* [ ] No secrets exposed
* [ ] Tests generated
* [ ] Critical flows covered
* [ ] No unnecessary dependencies
* [ ] Production build succeeds

---

# 40. Frontend Handoff

The Frontend Agent must provide the following to downstream agents:

```text
Frontend Code
+
Component Structure
+
API Integration
+
Tests
+
Build Result
+
Figma Compliance Result
```

The Testing Agent uses the frontend code and test information.

The Security Agent scans the frontend for security issues.

The DevOps Agent packages the frontend according to the deployment architecture.

---

# 41. Agentic SDLC Frontend Rule

The Frontend Agent must not independently invent the application's UI/UX when an approved Figma design exists.

The required workflow is:

```text
Requirements
      ↓
System Design
      ↓
Figma Design
      ↓
Figma URL
      ↓
Frontend Agent
      ↓
React Implementation
      ↓
Frontend Testing
      ↓
Security Validation
```

**Figma defines the intended UI/UX. System Design defines the technical architecture. API Design defines the frontend-backend contract. The Frontend Agent must integrate all three when generating the application.**

# 8A. Explicit Framework Standards

The Frontend Agent must select and use the frontend framework defined by the approved System Design.

## Default Framework

Unless the project requirements specify otherwise:

```text
Framework: React
Language: TypeScript
Build Tool: Vite
```

Recommended baseline:

```text
React
+
TypeScript
+
Vite
```

The Frontend Agent must not switch frameworks without an explicit requirement or approved architecture change.

---

# 8B. Framework Selection Rules

The Frontend Agent may use:

| Requirement               | Preferred Technology                       |
| ------------------------- | ------------------------------------------ |
| Standard SPA              | React + TypeScript + Vite                  |
| SEO-heavy application     | Next.js + TypeScript                       |
| Static frontend           | React + Vite                               |
| Large enterprise frontend | React + TypeScript                         |
| Mobile application        | React Native only when explicitly required |

Do not introduce Next.js, React Native, Vue, Angular, or another framework when the System Design specifies React + Vite.

---

# 8C. Version Standards

The generated project must use stable, mutually compatible versions.

The agent must:

1. Check the framework version.
2. Check Node.js compatibility.
3. Check dependency compatibility.
4. Avoid obsolete packages.
5. Avoid packages with known critical vulnerabilities.
6. Lock dependency versions.

Example:

```text
Node.js
   ↓
React
   ↓
TypeScript
   ↓
Vite
   ↓
Application Dependencies
```

The agent must not blindly use the latest package version.

---

# 8D. Package Manager

The project must use one package manager consistently.

Supported options:

```text
npm
pnpm
yarn
```

Preferred default:

```text
npm
```

Example:

```text
package.json
package-lock.json
```

Do not mix:

```text
npm
+
yarn
+
pnpm
```

within the same project.

---

# 8E. Explicit Dependency Standards

Dependencies must be added only when they provide meaningful functionality.

Before adding a dependency, the Frontend Agent should evaluate:

```text
Need
 ↓
Existing project capability
 ↓
Package maturity
 ↓
Maintenance status
 ↓
Security
 ↓
Bundle impact
 ↓
Compatibility
 ↓
Add dependency
```

Avoid dependencies for functionality that can be implemented simply with native React or browser APIs.

---

# 8F. Approved Core Dependencies

For a standard React application, the following dependency categories are allowed when required:

```text
React
React DOM
TypeScript
Vite
```

Additional dependencies should be selected based on project requirements.

Examples:

| Requirement       | Dependency Category      |
| ----------------- | ------------------------ |
| Routing           | React Router             |
| Server state      | TanStack Query           |
| Form management   | React Hook Form          |
| Schema validation | Zod                      |
| HTTP client       | Axios or Fetch           |
| UI components     | Approved UI library      |
| Testing           | Vitest / Testing Library |
| E2E testing       | Playwright               |
| Icons             | Approved icon library    |

The agent must not add every library by default.

---

# 8G. HTTP Client Standards

The project should use the native `fetch` API unless the application benefits from a dedicated HTTP client.

Allowed:

```text
fetch
Axios
```

If Axios is selected, it should be centralized:

```text
src/
└── api/
    └── client.ts
```

Components must not create independent Axios instances.

---

# 8H. Routing Standards

For applications requiring client-side routing:

```text
React Router
```

should be used unless the selected framework provides routing natively.

Routes should be centralized and organized.

Example:

```text
src/
└── routes/
    ├── index.tsx
    ├── publicRoutes.tsx
    └── protectedRoutes.tsx
```

---

# 8I. State Management Standards

Use the simplest appropriate solution.

Preferred order:

```text
1. React useState
        ↓
2. useReducer
        ↓
3. React Context
        ↓
4. Server-state library
        ↓
5. Global state library
```

Redux/Zustand or similar libraries must not be added unless the application has a real global-state requirement.

---

# 8J. Form and Validation Dependencies

For complex forms, the preferred combination is:

```text
React Hook Form
+
Zod
```

Example:

```text
User Input
   ↓
React Hook Form
   ↓
Zod Validation
   ↓
API
```

Validation must also be performed by the backend.

Frontend validation is for user experience and is not a security boundary.

---

# 8K. Testing Dependencies

A React application should use an appropriate testing stack.

Recommended:

```text
Vitest
+
React Testing Library
+
Playwright
```

Use:

```text
Vitest
```

for unit/component-level tests.

Use:

```text
Playwright
```

for end-to-end workflows.

---

# 8L. Dependency Categories

Dependencies should be classified as:

```text
Production Dependencies
Development Dependencies
Peer Dependencies
```

Example:

```json
{
  "dependencies": {
    "react": "...",
    "react-dom": "..."
  },
  "devDependencies": {
    "typescript": "...",
    "vite": "...",
    "vitest": "..."
  }
}
```

Testing, linting, formatting, and build-only tools should normally be development dependencies.

---

# 8M. Dependency Version Pinning

Dependencies must use controlled versions.

The project must commit the package lock file.

Example:

```text
package.json
package-lock.json
```

The lock file must be included in Git.

Avoid uncontrolled dependency installation during CI/CD.

---

# 8N. Dependency Security

Before dependencies are approved, check for known vulnerabilities.

The CI/CD pipeline should perform dependency security checks.

Example:

```text
Install Dependencies
        ↓
Dependency Audit
        ↓
Security Scan
        ↓
Build
```

Critical vulnerabilities should block production deployment unless explicitly approved.

---

# 8O. Dependency Minimization

Avoid dependency duplication.

For example, do not add multiple libraries for the same purpose:

```text
Axios + Fetch Wrapper + Another HTTP Client
```

Prefer:

```text
One HTTP approach
```

Similarly:

```text
Multiple Form Libraries
```

should be avoided.

---

# 8P. UI Library Standards

A UI component library may be used when it improves consistency and development speed.

Examples include:

```text
Material UI
Ant Design
Chakra UI
shadcn/ui
```

The selected library must be compatible with the Figma design.

The Frontend Agent must not replace Figma's design with the default appearance of a UI library.

Preferred:

```text
Figma Design
     ↓
Design Tokens
     ↓
UI Components
     ↓
React Application
```

---

# 8Q. Dependency Selection Output

The Frontend Agent should document selected dependencies.

Example:

```json
{
  "framework": {
    "name": "react",
    "version": "specified_version"
  },
  "language": {
    "name": "typescript",
    "version": "specified_version"
  },
  "build_tool": {
    "name": "vite",
    "version": "specified_version"
  },
  "dependencies": [
    {
      "name": "react-router",
      "version": "specified_version",
      "purpose": "Application routing"
    }
  ],
  "dev_dependencies": [
    {
      "name": "vitest",
      "version": "specified_version",
      "purpose": "Unit testing"
    }
  ]
}
```

---

# 8R. Framework and Dependency Validation

Before generating the final frontend, verify:

* [ ] Framework matches System Design
* [ ] React is used when React is specified
* [ ] TypeScript is used for production React applications
* [ ] Build tool is defined
* [ ] Node.js version is defined
* [ ] Package manager is defined
* [ ] Dependencies are necessary
* [ ] Dependency versions are controlled
* [ ] Lock file is generated
* [ ] No duplicate libraries provide the same functionality
* [ ] Dependencies are security-checked
* [ ] Testing dependencies are configured
* [ ] UI library matches Figma requirements
* [ ] No frontend secrets are included
* [ ] Production build succeeds

---

# 8S. Agentic SDLC Framework Rule

The Frontend Agent must follow this hierarchy:

```text
System Design
      ↓
Framework Selection
      ↓
Dependency Selection
      ↓
Figma Design
      ↓
React Implementation
      ↓
Testing
      ↓
Security Scan
      ↓
Production Build
```

**The Frontend Agent must not arbitrarily select frameworks or install dependencies. Every framework and significant dependency must be justified by the project requirements, System Design, or implementation need.**
