import asyncio

from ai_agents.jira.create_issues import create_jira_from_prd
from ai_agents.research_agent.search_planer_agent import run_research_agent
from ai_agents.research_agent.writer_agent import generate_jira_prd
from ai_agents.state import save_pending_approval
from config.settings import settings
from slack.blocks import design_generation_approval_block


async def _run_orchestrator_async(user_query: str) -> dict:

    print("Orchestrator received", user_query)

    research_context = await run_research_agent(user_query)

    prd = await generate_jira_prd(user_query, research_context)

    jira_result = await create_jira_from_prd(prd, settings.jira_project_key)

    if not jira_result["success"]:
        return {
            "text": (
                f"Failed to create Jira ticket(s) at stage "
                f"'{jira_result['stage']}': {jira_result['jira_error']}"
            )
        }

    parent_key = jira_result["parent"]

    save_pending_approval(parent_key, user_query=user_query, prd=prd)

    jira_url = f"{settings.jira_base_url}/browse/{parent_key}"

    return {
        "text": (
            f"Created Jira Epic <{jira_url}|{parent_key}> with "
            f"{len(jira_result['children'])} child task(s)."
        ),
        "blocks": design_generation_approval_block(parent_key, jira_url),
    }


def run_orchestrator(user_query: str) -> dict:
    return asyncio.run(_run_orchestrator_async(user_query))
