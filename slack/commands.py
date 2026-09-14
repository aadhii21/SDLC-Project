import asyncio

from slack_bolt import App
from slack_sdk import WebClient

from config.settings import settings
from graph.lang_graph import start_pipeline

slack_client = WebClient(token=settings.slack_bot_token)


def register_commands(slack_app: App):
    @slack_app.command("/sdlc")
    def handle_sdlc_command(
        ack,
        command,
        respond,
        logger
    ):
        ack()
        user_request = command.get("text", "").strip()
        channel_id = command.get("channel_id")

        if not user_request:
            respond("Please provide ur sdlc request")
            return
        try:
            # /sdlc has no originating channel message to thread on, so post
            # the processing ack ourselves and thread everything else under it.
            ack_message = slack_client.chat_postMessage(
                channel=channel_id,
                text="⏳ Working on your request — researching, drafting a PRD, and creating Jira tickets. This can take a minute...",
            )
            thread_ts = ack_message["ts"]

            asyncio.run(start_pipeline(user_request, channel_id, thread_ts))
            # start_pipeline posts the approval-request message itself
            # once it reaches the interrupt -- nothing further needed here.
        except Exception as error:
            logger.exception(f"Sdlc command failed{error}")
            respond("Something went wrong while processing your SDLC request.")
