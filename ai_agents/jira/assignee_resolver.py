from config.settings import settings

WORK_TYPE_OWNERS = {
    "design": settings.jira_assignee_design,
    "frontend": settings.jira_assignee_frontend,
    "backend": settings.jira_assignee_backend,
    "integration": settings.jira_assignee_integration,
    "qa": settings.jira_assignee_qa,
    "devops": settings.jira_assignee_devops,
}


def resolve_assignee(work_type: str):
    return WORK_TYPE_OWNERS.get(work_type)
