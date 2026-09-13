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
                "type":"mrkdwm",#Tells Slack to interpret the text using Slack Markdown formatting.
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
                "type":"mrkdown",
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