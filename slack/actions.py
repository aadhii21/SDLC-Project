import asyncio

from slack_bolt import App

from graph.lang_graph import resume_pipeline


def register_actions(slack_app: App) -> None:

    @slack_app.action("approve_design_generation")
    def handle_approve_design(ack, body, logger):
        ack()
        thread_id = body["actions"][0]["value"]
        try:
            asyncio.run(resume_pipeline(thread_id, {"approved": True}))
        except Exception as error:
            logger.exception(f"Resume (approve) failed for thread {thread_id}: {error}")

    @slack_app.action("reject_design_generation")
    def handle_reject_design(ack, body, logger):
        ack()
        thread_id = body["actions"][0]["value"]
        try:
            asyncio.run(resume_pipeline(thread_id, {"approved": False}))
        except Exception as error:
            logger.exception(f"Resume (reject) failed for thread {thread_id}: {error}")

    @slack_app.action("regenerate_prd")
    def handle_regenerate_prd(ack, body, logger):
        ack()
        thread_id = body["actions"][0]["value"]
        try:
            asyncio.run(resume_pipeline(thread_id, {"type": "choice", "target": "prd"}))
        except Exception as error:
            logger.exception(f"Resume (regenerate_prd) failed for thread {thread_id}: {error}")

    @slack_app.action("regenerate_design")
    def handle_regenerate_design(ack, body, logger):
        ack()
        thread_id = body["actions"][0]["value"]
        try:
            asyncio.run(resume_pipeline(thread_id, {"type": "choice", "target": "design"}))
        except Exception as error:
            logger.exception(f"Resume (regenerate_design) failed for thread {thread_id}: {error}")
