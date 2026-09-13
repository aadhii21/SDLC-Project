def text_to_adf(text: str) -> dict:
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": text
                    }
                ]
            }
        ]
    }


def prd_description_text(prd) -> str:
    return f"""
{prd.description}

Problem Statement:
{prd.problem_statement}

Objective:
{prd.objective}

Solution:
{prd.solution}

Business Rules:
{chr(10).join("- " + x for x in prd.business_rules)}

Functional Requirements:
{chr(10).join("- " + x for x in prd.functional_requirements)}

Acceptance Criteria:
{chr(10).join("- " + x for x in prd.acceptance_criteria)}
"""


def parent_payload(prd, project_key: str):

    description = prd_description_text(prd)

    return {
        "fields": {
            "project": {
                "key": project_key
            },
            "summary": prd.title,
            "description": text_to_adf(description),
            "issuetype": {
                "name": "Epic"
            }
        }
    }


def child_payload(child, project_key: str,parent_key:str, assignee_id: str | None):

    description = f"""
{child.description}

Requirements:
{chr(10).join("- " + x for x in child.requirements)}

Dependencies:
{chr(10).join("- " + x for x in child.dependencies)}

Acceptance Criteria:
{chr(10).join("- " + x for x in child.acceptance_criteria)}
"""

    fields = {
        "project": {
            "key": project_key
        },
        "summary": child.title,
        "description": text_to_adf(description),
        "issuetype": {
            "name": "Task"
        },
    
        #link this task to newly created epic
        "parent":{
            "key":parent_key
        }
    }


    if assignee_id:
        fields["assignee"] = {
            "accountId": assignee_id
        }

    return {
        "fields": fields
    }