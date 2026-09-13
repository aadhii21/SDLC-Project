import os
from dotenv import load_dotenv
from slack_bolt import App
from slack.commands import register_commands
from slack.events import register_events
load_dotenv()
bot_token=os.getenv("SLACK_BOT_TOKEN")
if not bot_token:
    raise ValueError ("SLACK_BOT_TOKEN is not configured")
slack_app=App(
    token=bot_token
)
register_events(slack_app)
register_commands(slack_app)
