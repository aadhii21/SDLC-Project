import asyncio

from slack_bolt import App

from graph.lang_graph import start_pipeline


def register_events(slack_app: App):

    @slack_app.event("app_mention")
    def handle_app_mention(
        event,
        say,
        logger,
    ):

        user_query = event.get("text", "").strip()
        channel_id = event.get("channel")
        thread_ts = event.get("ts")

        print("USER QUERY:", user_query)

        try:
            say(
                text="⏳ Working on your request — researching, drafting a PRD, and creating Jira tickets. This can take a minute...",
                thread_ts=thread_ts,
            )
            asyncio.run(start_pipeline(user_query, channel_id, thread_ts))
            # start_pipeline posts the Jira-created + approval-request
            # message itself (via notify_approval_node) once it reaches
            # the interrupt -- nothing further to say() here.

        except Exception as error:
            logger.exception(f"Agent execution failed: {error}")
            say(text="Something went wrong while processing your request.", thread_ts=thread_ts)
