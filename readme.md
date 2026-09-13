# Agentic SDLC

Agentic SDLC is an AI-powered software development lifecycle automation platform.

The platform takes an application idea from a Product Manager and uses specialized AI agents to automate software development activities such as:

- Research
- Requirements gathering
- System design
- Frontend development
- Backend development
- Testing
- Security analysis
- CI/CD
- Deployment
- Monitoring

Slack is used as the human interaction and approval interface.

LangGraph is used to orchestrate the complete workflow.


## High-Level Architecture

```text
Product Manager
       |
       v
     Slack
       |
       v
    FastAPI
       |
       v
   LangGraph
       |
       +-------------------+
       |                   |
       v                   v
 Research Agent     Requirements Agent
       |
       v
   Design Agent
       |
       +-------------------+
       |                   |
       v                   v
 Frontend Agent      Backend Agent
       |
       v
 Testing Agent
       |
       v
 Security Agent
       |
       v
 DevOps / Deployment
       |
       v
     AWS
       |
       v
   Monitoring