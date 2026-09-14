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


def design_generation_approval_block(parent_key: str, jira_url: str, thread_id: str) -> list:
    """
    Create Slack approval buttons for kicking off Figma design generation
    once the product owner approves the Jira PRD/epic.

    `thread_id` is the LangGraph checkpoint thread id for this paused run --
    it's what the button carries (not `parent_key`), since that's what
    resume_pipeline() needs to wake the correct paused graph back up.
    `parent_key`/`jira_url` are only used for the human-readable message text.
    """
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"🎨 Ready to generate the design for <{jira_url}|{parent_key}>?\n"
                    f"Approve to have the agent create the Figma design and link it back here + on the ticket."
                ),
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Approve design generation",
                    },
                    "style": "primary",
                    "action_id": "approve_design_generation",
                    "value": thread_id,
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Reject",
                    },
                    "style": "danger",
                    "action_id": "reject_design_generation",
                    "value": thread_id,
                },
            ],
        },
    ]