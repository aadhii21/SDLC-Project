from slack_bolt import App
from ai_agents.orchestrator import run_orchestrator


def register_events(slack_app: App):

    @slack_app.event("app_mention")
    def handle_app_mention(
        event,
        say,
        logger,
    ):

        # STEP 1:
        # Get actual message sent by user
        user_query = event.get(
            "text",
            ""
        ).strip()

        print(
            "USER QUERY:",
            user_query
        )


        try:

            # STEP 2:
            # Send user message to orchestrator
            #
            # events.py
            #    ↓
            # orchestrator.py

            result = run_orchestrator(
                user_query
            )


            # STEP 3:
            # Send dynamic result back to Slack
            say(
                text=result.get("text", ""),
                blocks=result.get("blocks"),
            )


        except Exception as error:

            logger.exception(
                f"Agent execution failed: {error}"
            )

            say(
                text="Something went wrong while processing your request."
            )
