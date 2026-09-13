from ai_agents.jira.client import jira_post
from ai_agents.jira.mapper import parent_payload, child_payload
from ai_agents.jira.assignee_resolver import resolve_assignee


async def create_jira_from_prd(prd, project_key: str):

    parent = await jira_post(
        "/rest/api/3/issue",
        parent_payload(prd, project_key)
    )

    print("PARENT RESPONSE:", parent)

    if parent.get("error"):
        return {
            "success": False,
            "stage": "parent_creation",
            "jira_error": parent
        }

    parent_key = parent["key"]

    created_children = []

    for child in prd.child_work_items:

        assignee_id = resolve_assignee(child.work_type)

        child_result = await jira_post(
            "/rest/api/3/issue",
            child_payload(
                child=child,
                project_key=project_key,
                parent_key=parent_key,
                assignee_id=assignee_id
            )
        )

        print("CHILD RESPONSE:", child_result)

        if child_result.get("error"):
            return {
                "success": False,
                "stage": "child_creation",
                "parent": parent_key,
                "created_children":created_children,
                "failed_child":child.title,
                "jira_error": child_result
            }

        created_children.append(child_result["key"])

    return {
        "success": True,
        "parent": parent_key,
        "children": created_children
    }