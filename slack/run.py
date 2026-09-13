import os
from dotenv import load_dotenv
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slack.app import slack_app

load_dotenv()
app_token=os.getenv("SLACK_APP_TOKEN")

if not app_token:
    raise ValueError("SLACK_APP_TOKEN is not configured")

def main():
    print("Starting Slack Socket Mode...")
    handler=SocketModeHandler(
        slack_app,
        app_token
    )
    handler.start()
if __name__=="__main__":
    main()