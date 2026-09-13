from slack_bolt.adapter.socket_mode import SocketModeHandler

from config.settings import settings
from slack.app import slack_app

if not settings.slack_app_token:
    raise ValueError("SLACK_APP_TOKEN is not configured")


def main():
    print("Starting Slack Socket Mode...")
    handler = SocketModeHandler(slack_app, settings.slack_app_token)
    handler.start()


if __name__ == "__main__":
    main()
