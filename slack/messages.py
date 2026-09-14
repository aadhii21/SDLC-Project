import asyncio

from slack_bolt import App

from graph.lang_graph import get_pending_node, resume_pipeline


def register_messages(slack_app: App) -> None:

    @slack_app.event("message")
    def handle_message(event, logger):
        # Only interested in genuine threaded replies to one of our own
        # pipeline runs -- not top-level messages, not the bot's own posts,
        # not edits/deletes (which arrive with a subtype).
        thread_ts = event.get("thread_ts")
        if not thread_ts:
            return
        if event.get("bot_id") is not None:
            return
        if event.get("subtype") is not None:
            return

        text = event.get("text", "").strip()
        if not text:
            return

        try:
            pending_node = get_pending_node(thread_ts)
        except Exception as error:
            logger.exception(f"Failed to check pending state for thread {thread_ts}: {error}")
            return

        if pending_node != "await_feedback_node":
            # Not a thread we're waiting on feedback for -- ignore silently,
            # this could be unrelated conversation in the same thread.
            return

        try:
            asyncio.run(resume_pipeline(thread_ts, {"type": "message", "text": text}))
        except Exception as error:
            logger.exception(f"Resume (message) failed for thread {thread_ts}: {error}")
