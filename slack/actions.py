import asyncio

from slack_bolt import App

from ai_agents.jira.queries import get_child_tasks, get_epic_description
from graph.lang_graph import get_jira_parent_key, get_pending_node, resume_pipeline


def _mark_handled(client, body, confirmation_text: str) -> None:
    """Replace the clicked message's button row with a plain confirmation,
    so the same message can't be acted on again -- neither a double-click
    nor a stale click on an orphaned duplicate message (the exact failure
    mode seen live: a forked checkpoint history left two messages with
    live-looking buttons pointing at the same thread)."""
    channel_id = body["channel"]["id"]
    message_ts = body["message"]["ts"]
    kept_blocks = [b for b in body["message"].get("blocks", []) if b.get("type") != "actions"]
    kept_blocks.append({"type": "context", "elements": [{"type": "mrkdwn", "text": confirmation_text}]})
    client.chat_update(channel=channel_id, ts=message_ts, text=confirmation_text, blocks=kept_blocks)


def register_actions(slack_app: App) -> None:

    @slack_app.action("approve_prd")
    def handle_approve_prd(ack, body, client, say, logger):
        ack()
        thread_id = body["actions"][0]["value"]
        # Guards against exactly what happened live: a duplicate/stale
        # message whose button no longer matches what the pipeline is
        # actually paused on. Only act if this is genuinely still pending.
        if get_pending_node(thread_id) != "await_prd_approval_node":
            logger.info(f"Ignoring stale approve_prd click for thread {thread_id} -- not currently pending here.")
            return
        try:
            asyncio.run(resume_pipeline(thread_id, {"approved": True}))
            _mark_handled(client, body, "✅ Approved.")
        except Exception as error:
            logger.exception(f"Resume (approve_prd) failed for thread {thread_id}: {error}")
            say(text="Something went wrong while processing that approval.", thread_ts=thread_id)

    @slack_app.action("reject_prd")
    def handle_reject_prd(ack, body, client, say, logger):
        ack()
        thread_id = body["actions"][0]["value"]
        if get_pending_node(thread_id) != "await_prd_approval_node":
            logger.info(f"Ignoring stale reject_prd click for thread {thread_id} -- not currently pending here.")
            return
        try:
            asyncio.run(resume_pipeline(thread_id, {"approved": False}))
            _mark_handled(client, body, "❌ Rejected.")
        except Exception as error:
            logger.exception(f"Resume (reject_prd) failed for thread {thread_id}: {error}")
            say(text="Something went wrong while processing that rejection.", thread_ts=thread_id)

    @slack_app.action("approve_design")
    def handle_approve_design(ack, body, client, say, logger):
        ack()
        thread_id = body["actions"][0]["value"]
        if get_pending_node(thread_id) != "await_design_approval_node":
            logger.info(f"Ignoring stale approve_design click for thread {thread_id} -- not currently pending here.")
            return
        try:
            asyncio.run(resume_pipeline(thread_id, {"approved": True}))
            _mark_handled(client, body, "✅ Approved.")
        except Exception as error:
            logger.exception(f"Resume (approve_design) failed for thread {thread_id}: {error}")
            say(text="Something went wrong while processing that approval.", thread_ts=thread_id)

    @slack_app.action("reject_design")
    def handle_reject_design(ack, body, client, say, logger):
        ack()
        thread_id = body["actions"][0]["value"]
        if get_pending_node(thread_id) != "await_design_approval_node":
            logger.info(f"Ignoring stale reject_design click for thread {thread_id} -- not currently pending here.")
            return
        try:
            asyncio.run(resume_pipeline(thread_id, {"approved": False}))
            _mark_handled(client, body, "❌ Rejected.")
        except Exception as error:
            logger.exception(f"Resume (reject_design) failed for thread {thread_id}: {error}")
            say(text="Something went wrong while processing that rejection.", thread_ts=thread_id)

    # Read-only info buttons -- these must NEVER call resume_pipeline, and
    # are left clickable (repeatedly, if desired) since re-reading Jira is
    # harmless. They just read Jira and post back, leaving the paused
    # interrupt (waiting on approve/reject) exactly as it was.
    @slack_app.action("view_epic")
    def handle_view_epic(ack, body, say, logger):
        ack()
        thread_id = body["actions"][0]["value"]
        try:
            parent_key = get_jira_parent_key(thread_id)
            if not parent_key:
                say(text="No Jira epic found for this run yet.", thread_ts=thread_id)
                return

            epic = asyncio.run(get_epic_description(parent_key))
            if epic["error"]:
                say(text=f"Couldn't fetch `{parent_key}`: {epic['detail']}", thread_ts=thread_id)
                return

            say(
                text=f"*{parent_key}: {epic['summary']}*\n\n{epic['description']}",
                thread_ts=thread_id,
            )
        except Exception as error:
            logger.exception(f"View epic failed for thread {thread_id}: {error}")
            say(text="Something went wrong while fetching the epic.", thread_ts=thread_id)

    @slack_app.action("view_subtasks")
    def handle_view_subtasks(ack, body, say, logger):
        ack()
        thread_id = body["actions"][0]["value"]
        try:
            parent_key = get_jira_parent_key(thread_id)
            if not parent_key:
                say(text="No Jira epic found for this run yet.", thread_ts=thread_id)
                return

            result = asyncio.run(get_child_tasks(parent_key))
            if result["error"]:
                say(text=f"Couldn't fetch sub-tasks for `{parent_key}`: {result['detail']}", thread_ts=thread_id)
                return

            if not result["tasks"]:
                say(text=f"No sub-tasks found under `{parent_key}`.", thread_ts=thread_id)
                return

            lines = [f"- `{t['key']}` [{t['status']}] {t['summary']}" for t in result["tasks"]]
            say(text=f"*Sub-tasks under {parent_key}:*\n" + "\n".join(lines), thread_ts=thread_id)
        except Exception as error:
            logger.exception(f"View sub-tasks failed for thread {thread_id}: {error}")
            say(text="Something went wrong while fetching sub-tasks.", thread_ts=thread_id)
