from typing import Any

from fastapi import APIRouter, Request

from slack.commands import handle_command
from slack.events import handle_event

router = APIRouter()


@router.post("/slack/events")
async def slack_events(request: Request) -> dict[str, Any]:
    """
    Receive Slack Events API requests.
    """

    payload = await request.json()

    return handle_event(payload)


@router.post("/slack/commands")
async def slack_commands(request: Request) -> dict[str, Any]:
    """
    Receive Slack slash command requests.
    """

    form = await request.form()

    command = form.get("command", "")
    text = form.get("text", "")
    user_id = form.get("user_id")
    channel_id = form.get("channel_id")

    return handle_command(
        command=str(command),
        text=str(text),
        user_id=str(user_id) if user_id else None,
        channel_id=str(channel_id) if channel_id else None,
    )
