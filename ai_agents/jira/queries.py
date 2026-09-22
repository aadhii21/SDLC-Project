from ai_agents.jira.client import jira_get
from ai_agents.jira.mapper import adf_to_text


async def get_epic_description(issue_key: str) -> dict:
    issue = await jira_get(f"/rest/api/3/issue/{issue_key}")

    if issue.get("error"):
        return {"error": True, "detail": issue}

    fields = issue.get("fields", {})
    return {
        "error": False,
        "summary": fields.get("summary", ""),
        "description": adf_to_text(fields.get("description")),
    }


async def get_child_tasks(issue_key: str) -> dict:
    result = await jira_get(
        "/rest/api/3/search/jql",
        params={"jql": f'parent = "{issue_key}"', "fields": "summary,status"},
    )

    if result.get("error"):
        return {"error": True, "detail": result}

    tasks = [
        {
            "key": issue["key"],
            "summary": issue["fields"].get("summary", ""),
            "status": issue["fields"].get("status", {}).get("name", ""),
        }
        for issue in result.get("issues", [])
    ]
    return {"error": False, "tasks": tasks}
