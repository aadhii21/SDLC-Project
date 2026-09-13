def format_success_message(message:str)->dict:
    """
    Format a successfull response for Slack
    """
    return{
        "response_type":"in_channel",#Show the response to everyone in the Slack channel.
        "text":message,
    }
def format_error_message(message:str)->dict:
    """
    Format a error for Slack
    """
    return{
        "response_type":"ephemeral",#Show the response only to the user who triggered the command.
        "text":f"{message}"
    }
def format_info_message(message:str)->dict:
    """
    Format a informational message for slack
    """
    return{
        "response_type":"ephemeral",#Show the response only to the user who triggered the command.
        "text":f"{message}"

    }