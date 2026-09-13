from ai_agents.jira.client import jira_post
from ai_agents.jira.mapper import text_to_adf


async def add_jira_comment(issue_key: str, text: str) -> dict:
    return await jira_post(
        f"/rest/api/3/issue/{issue_key}/comment",
        {"body": text_to_adf(text)},
    )
