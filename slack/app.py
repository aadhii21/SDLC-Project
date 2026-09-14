from slack_bolt import App

from config.settings import settings
from slack.actions import register_actions
from slack.commands import register_commands
from slack.events import register_events
from slack.messages import register_messages

if not settings.slack_bot_token:
    raise ValueError("SLACK_BOT_TOKEN is not configured")

slack_app = App(token=settings.slack_bot_token)

register_events(slack_app)
register_commands(slack_app)
register_actions(slack_app)
register_messages(slack_app)
