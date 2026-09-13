from ai_agents.research_agent_folder.research_agent import run_research_agent
from ai_agents.design_agent import run_design_agent
from ai_agents.frontend_agent import run_frontend_agent
from ai_agents.backend_agent import run_backend_agent
from ai_agents.testing_agent import run_testing_agent
from ai_agents.code_review_agent import run_code_review_agent
from ai_agents.security_agent import run_security_agent
from ai_agents.devops_agent import run_devops_agent
from ai_agents.monitoring_agent import run_monitoring_agent
from ai_agents.full_sdlc_agent import run_full_sdlc_agent

def run_orchestrator(user_query:str):
    print("Orchestrator recieved", user_query)
    query = user_query.lower().strip()
    if (
        "full sdlc" in query
        or "end to end" in query
        or "complete project" in query
    ):

        return run_full_sdlc_agent(
            user_query
        )
    elif (
        "design" in query
        or "architecture" in query
        or "database" in query
        or "db design" in query
        or "api design" in query
    ):

        return run_design_agent(
            user_query
        )
    elif (
        "frontend" in query
        or "react" in query
        or "next.js" in query
        or "nextjs" in query
        or "ui" in query
    ):

        return run_frontend_agent(
            user_query
        )
    elif (
        "backend" in query
        or "fastapi" in query
        or "api" in query
    ):

        return run_backend_agent(
            user_query
        )
    elif (
        "test" in query
        or "testing" in query
        or "qa" in query
        or "playwright" in query
        or "e2e" in query
        or "integration test" in query
        or "unit test" in query
    ):

        return run_testing_agent(
            user_query
        )
    elif (
        "review" in query
        or "code review" in query
    ):

        return run_code_review_agent(
            user_query
        )
    elif (
        "security" in query
        or "quality" in query
        or "vulnerability" in query
        or "scan" in query
    ):

        return run_security_agent(
            user_query
        )
    elif (
        "deploy" in query
        or "deployment" in query
        or "devops" in query
        or "docker" in query
        or "jenkins" in query
        or "ci/cd" in query
        or "cicd" in query
        or "ecs" in query
        or "eks" in query
        or "ecr" in query
    ):

        return run_devops_agent(
            user_query
        )
    elif (
        "monitor" in query
        or "monitoring" in query
        or "logs" in query
        or "metrics" in query
        or "cloudwatch" in query
    ):

        return run_monitoring_agent(
            user_query
        )
    else:

        # For now, if no agent matches,
        # return a simple response.
        #
        # Later:
        #
        # replace keyword routing with an LLM
        # that automatically chooses the correct agent.

        return (
            "I received your request, but I could not "
            f"identify the required agent: {user_query}"
        )