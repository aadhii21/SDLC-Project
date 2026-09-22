import asyncio

from slack_bolt import App

from graph.lang_graph import has_existing_run, start_pipeline


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

        # Slack redelivers an event if this handler doesn't finish fast
        # enough (e.g. the process restarts mid-run, as happened live).
        # thread_ts is the original message's own ts, so a genuine redelivery
        # of the SAME event always carries the SAME thread_ts -- if a run
        # already exists for it, this is a duplicate delivery, not a new
        # request. Starting a second run on top of it forks the checkpoint
        # history and produces two racing, inconsistent executions.
        if has_existing_run(thread_ts):
            logger.info(f"Ignoring duplicate app_mention delivery for thread {thread_ts} -- run already exists.")
            return

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
