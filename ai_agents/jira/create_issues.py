import asyncio

from ai_agents.jira.client import jira_post
from ai_agents.jira.mapper import parent_payload, child_payload
from ai_agents.jira.assignee_resolver import resolve_assignee


async def _create_child(child, project_key: str, parent_key: str):
    assignee_id = resolve_assignee(child.work_type)
    result = await jira_post(
        "/rest/api/3/issue",
        child_payload(
            child=child,
            project_key=project_key,
            parent_key=parent_key,
            assignee_id=assignee_id,
        ),
    )
    print("CHILD RESPONSE:", result)
    return child, result


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

    # Each child ticket is independent (only depends on parent_key, already
    # known) -- create them concurrently instead of one network round trip
    # at a time. All attempts run regardless of whether another one fails,
    # so on failure we report every child that DID get created, not just
    # the ones that happened to precede the failure in list order.
    results = await asyncio.gather(
        *[_create_child(child, project_key, parent_key) for child in prd.child_work_items]
    )

    created_children = [result["key"] for _, result in results if not result.get("error")]
    failed = [(child, result) for child, result in results if result.get("error")]

    if failed:
        failed_child, failed_result = failed[0]
        return {
            "success": False,
            "stage": "child_creation",
            "parent": parent_key,
            "created_children": created_children,
            "failed_child": failed_child.title,
            "jira_error": failed_result,
        }

    return {
        "success": True,
        "parent": parent_key,
        "children": created_children
    }