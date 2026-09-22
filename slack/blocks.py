def project_created_block(project_name:str)-> list:
    """
    Create Slack blocks for a successful project creation
    """
    return[
        {
            "type":"header",
            "text":{
                "type":"plain_text",
                "text":"🚀 Project Created"
            },
        },
        {
            "type":"section",
            "text":{
                "type":"mrkdwn",#Tells Slack to interpret the text using Slack Markdown formatting.
                "text":f"*Project:*'{project_name}'",
            },
        },
        {
            "type":"section",
            "text":{
                "type":"mrkdwn",
                "text":f"Your Project created successfully"
            }
        }
    ]
def project_status_block(
        project_name:str,
        status:str)->list:
    """
    Create Slack blocks showing project status.
    """
    return[
        {
            "type":"header",
            "text":{
                "type":"plain_text",
                "text":"📈Project Status"
            },
        },
        {
            "type":"section",
            "fields":[
                {
                "type":"mrkdwn",
                "text": f"*Project:*\n'{project_name}'",
            },
            {
                "type":"mrkdwn",
                "text": f"*Status:*\n'{status}'",
            }
        ] 
    }
]

def approval_block(project_name:str)->list:
    """
    Create Slack approval buttons for a project.
    """
    return[
        {
            "type":"section",
            "text":{
                "type":"mrkdwn",
                "text":(
                    f"⚠️Deployment approval required for"
                    f"*{project_name}*."
                )
            }
        },
        {
            "type":"actions",
            "elements":[
                {
                    "type":"button",
                    "text":{
                        "type":"plain_text",
                        "text":"Approve"
                    },
                    "style":"primary",
                    "action_id":"approve_deployment",
                    "value":project_name,
                },
                {
                    "type":"button",
                    "text":{
                        "type":"plain_text",
                        "text":"Reject",
                    },
                    "style":"danger",
                    "action_id":"reject_deployment",
                    "value":project_name,
                }


            ]
        }

    ]


def prd_approval_block(thread_id: str) -> list:
    """
    Approve/Reject buttons shown directly under the printed epic content,
    before any Jira ticket exists yet. `thread_id` is the LangGraph
    checkpoint thread id (the Slack root message ts) -- what resume_pipeline()
    needs to wake the correct paused graph back up.
    """
    return [
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Approve Epic",
                    },
                    "style": "primary",
                    "action_id": "approve_prd",
                    "value": thread_id,
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Reject",
                    },
                    "style": "danger",
                    "action_id": "reject_prd",
                    "value": thread_id,
                },
            ],
        },
    ]


def design_approval_block(parent_key: str, jira_url: str, thread_id: str) -> list:
    """
    Approve/Reject buttons shown directly under the printed design content,
    plus read-only View Epic / View Sub Tasks buttons -- the epic already
    exists by this point. `thread_id` is the LangGraph checkpoint thread id.
    `parent_key`/`jira_url` are only used by the caller for the message text.
    """
    return [
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Approve Design",
                    },
                    "style": "primary",
                    "action_id": "approve_design",
                    "value": thread_id,
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Reject",
                    },
                    "style": "danger",
                    "action_id": "reject_design",
                    "value": thread_id,
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Epic",
                    },
                    "action_id": "view_epic",
                    "value": thread_id,
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Sub Tasks",
                    },
                    "action_id": "view_subtasks",
                    "value": thread_id,
                },
            ],
        },
    ]