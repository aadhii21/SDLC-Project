from slack_bolt import App

from ai_agents.orchestrator import run_orchestrator

def register_commands(slack_app:App):
    @slack_app.command("/sdlc")
    def handle_sdlc_command(
        ack,
        command,
        respond,
        logger
    ):
        ack()
        user_request=command.get(
            "text",
            ""

        ).strip()
        if not user_request:
            respond("Please provide ur sdlc request")
            return
        try:
            result=run_orchestrator(
                user_request
            )
            respond(result)
        except Exception as error:
            logger.exception(
                f"Sdlc command failed{error}"
                            
            )
            respond(
                "Something went wrong while processing your SDLC request."
            )