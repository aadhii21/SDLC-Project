# Technology Research Standards

## 1. Purpose

Technology research must identify, evaluate, and compare technologies that may be useful for a project.

The research should help the architecture and development agents make evidence-based technology decisions.

## 2. Research Objectives

Before researching a technology, clearly define:

- What problem needs to be solved?
- What capabilities are required?
- What technologies are being considered?
- What constraints exist?
- What scale is expected?
- What is the expected cost?
- What security and compliance requirements exist?

## 3. Technology Evaluation Criteria

Evaluate technologies based on:

- Functionality
- Performance
- Scalability
- Reliability
- Security
- Maintainability
- Community support
- Documentation
- Integration capability
- Ecosystem maturity
- Licensing
- Cost
- Operational complexity

## 4. Technology Categories

Research may cover:

- Programming languages
- Frameworks
- Databases
- Vector databases
- Cloud services
- AI/LLM platforms
- Agent frameworks
- APIs
- Message queues
- Caching systems
- Container technologies
- CI/CD platforms
- Monitoring tools
- Infrastructure tools

## 5. Source Standards

Prefer:

- Official documentation
- Official GitHub repositories
- Official product documentation
- Cloud-provider documentation
- Academic papers
- Standards organizations
- Reputable technical publications

For technical capabilities, prefer official documentation over blogs or third-party summaries.

## 6. Technology Comparison

When multiple technologies solve the same problem, compare them using consistent criteria.

Example:

| Criteria | Technology A | Technology B | Technology C |
|---|---|---|---|
| Performance | | | |
| Scalability | | | |
| Cost | | | |
| Security | | | |
| Community | | | |
| Documentation | | | |
| Integration | | | |
| Complexity | | | |

Do not select a technology based on a single criterion.

## 7. Version and Compatibility

Always consider:

- Current stable version
- Supported versions
- Python/runtime compatibility
- Operating-system compatibility
- Cloud compatibility
- Dependency compatibility
- API compatibility
- Breaking changes

Version-sensitive information should be verified before being used in implementation.

## 8. Open Source Evaluation

For open-source technologies, evaluate:

- Repository activity
- Release frequency
- Maintainer activity
- Community adoption
- Documentation quality
- Issue activity
- Security history
- License
- Long-term sustainability

Do not assume that an open-source project is production-ready simply because it is popular.

## 9. Cloud Technology Evaluation

When evaluating cloud services, consider:

- Supported regions
- Pricing model
- Scalability
- Availability
- Managed-service capabilities
- Security controls
- IAM integration
- Networking requirements
- Monitoring capabilities
- Vendor lock-in

## 10. AI Technology Evaluation

When evaluating AI/LLM technologies, consider:

- Model capabilities
- Context window
- Latency
- Cost
- Tool/function calling
- Structured output support
- Multimodal capabilities
- Embedding support
- Fine-tuning options
- Security and privacy
- Availability
- Rate limits

Do not select an LLM solely based on benchmark scores.

## 11. Agent Framework Evaluation

When evaluating agent frameworks, consider:

- Agent orchestration
- Workflow support
- State management
- Tool integration
- Memory
- Human-in-the-loop support
- Observability
- Error handling
- Scalability
- Community and ecosystem

The framework should match the workflow complexity rather than being selected only because it is popular.

## 12. Database Evaluation

Database research should consider:

- Data model
- Read/write patterns
- Query requirements
- Scalability
- Consistency requirements
- Availability
- Indexing capabilities
- Backup and recovery
- Security
- Operational complexity
- Cost

For vector databases, additionally evaluate:

- Embedding compatibility
- Similarity-search algorithms
- Filtering
- Metadata support
- Hybrid search
- Scalability
- Retrieval latency

## 13. Technology Proof of Concept

For critical technology decisions, create a small proof of concept when necessary.

The POC should validate:

- Integration
- Performance
- Compatibility
- Reliability
- Security
- Developer experience

Do not introduce a technology into production solely based on theoretical capabilities.

## 14. Technology Risks

Identify risks such as:

- Vendor lock-in
- Immature technology
- Poor documentation
- Limited community support
- High operational complexity
- Security vulnerabilities
- High cost
- Poor scalability
- Compatibility problems
- Project abandonment

Every major technology decision should document important risks.

## 15. Cost Analysis

Where applicable, estimate:

- Development cost
- Infrastructure cost
- API cost
- Storage cost
- Compute cost
- Network cost
- Maintenance cost
- Scaling cost

Clearly distinguish estimated costs from confirmed pricing.

## 16. Security Evaluation

Before selecting a technology, consider:

- Authentication
- Authorization
- Encryption
- Secret management
- Vulnerability history
- Dependency security
- Network security
- Data privacy
- Compliance requirements

Security-sensitive technology choices require additional validation.

## 17. AI-Assisted Technology Research

AI agents may assist with:

- Technology discovery
- Documentation summarization
- Feature comparison
- Compatibility analysis
- Cost comparison
- Risk identification
- Architecture recommendations

AI-generated information must be validated against authoritative sources.

## 18. Technology Research Agent

The technology research agent should:

1. Understand the technical requirement.
2. Identify possible technologies.
3. Gather authoritative information.
4. Compare alternatives.
5. Check compatibility.
6. Evaluate security.
7. Evaluate cost.
8. Identify risks.
9. Recommend suitable technologies.
10. Provide supporting sources.

## 19. Recommendation Format

Technology recommendations should follow:

```text
Requirement
     ↓
Candidate Technologies
     ↓
Evaluation Criteria
     ↓
Comparison
     ↓
Risks
     ↓
Cost
     ↓
Recommendation
     ↓
Evidence / Sources

The recommendation must explain why the selected technology is appropriate.

20. Avoid Technology Bias

Do not recommend a technology simply because:

It is popular.
It is new.
It is used by a large company.
An AI model prefers it.
It is familiar to the developer.
It has more GitHub stars.

The decision must be based on project requirements and evidence.

21. Research Freshness

Verify information that can change over time, including:

Product features
API capabilities
Pricing
Supported versions
Licensing
Cloud availability
Model availability
Framework capabilities
Service limits
22. Technology Selection Checklist

Before selecting a technology:

 Requirement is clearly defined.
 Multiple alternatives were considered.
 Functionality was evaluated.
 Performance was considered.
 Scalability was considered.
 Security was evaluated.
 Compatibility was checked.
 Cost was considered.
 Licensing was checked.
 Community and documentation were evaluated.
 Risks were identified.
 Important information was validated.
 Recommendation is evidence-based.
23. Agentic SDLC Rule

Technology research must provide validated technical recommendations to downstream agents.

Technology Research
        ↓
Technology Evaluation
        ↓
Validated Recommendation
        ↓
Architecture Agent
        ↓
Development Agents

Downstream agents should use approved technology recommendations rather than independently introducing unapproved technologies.