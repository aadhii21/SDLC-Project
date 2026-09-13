import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

bot_token = os.getenv("SLACK_BOT_TOKEN")
app_token = os.getenv("SLACK_APP_TOKEN")

print("BOT TOKEN:", bool(bot_token))
print("APP TOKEN:", bool(app_token))

slack_app = App(token=bot_token)


@slack_app.event("app_mention")
def handle_app_mention(body, event, say):
    print("FULL BODY:", body)
    print("EVENT:", event)

    say("Hello, I received your mention!")


if __name__ == "__main__":
    print("Starting Slack Socket Mode...")
    SocketModeHandler(slack_app, app_token).start()