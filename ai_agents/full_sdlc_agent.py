from ai_agents.research_agent_folder.research_agent import run_research_agent
from ai_agents.design_agent import run_design_agent
from ai_agents.frontend_agent import run_frontend_agent
from ai_agents.backend_agent import run_backend_agent
from ai_agents.testing_agent import run_testing_agent
from ai_agents.code_review_agent import run_code_review_agent
from ai_agents.security_agent import run_security_agent
from ai_agents.devops_agent import run_devops_agent
from ai_agents.monitoring_agent import run_monitoring_agent
def run_full_sdlc_agent(user_query:str):
    research_result=run_research_agent(user_query)
    design_result=run_design_agent(research_result)
    frontend_result=run_frontend_agent(design_result)
    backend_result=run_backend_agent(design_result)
    testing_input={
        "frontend":frontend_result,
        "backend":backend_result
    }
    testing_result=run_testing_agent(testing_input)
    code_review_input={
        "frontend":frontend_result,
        "backend":backend_result,
        "tests":testing_result
    }
    code_review_result=run_code_review_agent(code_review_input)
    security_result=run_security_agent(code_review_result)
    devops_input={
        "code review":code_review_result,
        "security":security_result
    }
    devops_result=run_devops_agent(devops_input)
    monitoring_result=run_monitoring_agent(devops_result)
    return monitoring_result


