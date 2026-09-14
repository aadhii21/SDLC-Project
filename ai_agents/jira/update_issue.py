from ai_agents.jira.client import jira_put
from ai_agents.jira.mapper import prd_description_text, text_to_adf


async def update_jira_epic(issue_key: str, prd) -> dict:
    return await jira_put(
        f"/rest/api/3/issue/{issue_key}",
        {
            "fields": {
                "summary": prd.title,
                "description": text_to_adf(prd_description_text(prd)),
            }
        },
    )
