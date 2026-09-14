from agents import Agent, Runner

FEEDBACK_CHAT_INSTRUCTIONS = """
You are chatting with a product reviewer who just rejected a generated
design/PRD and is explaining what they want changed.

Acknowledge what they just said in 1-2 short sentences. Ask a clarifying
question ONLY if what they said is genuinely ambiguous -- otherwise just
confirm you understood.

Always end by reminding them they can click "Regenerate PRD" (for
requirement/functionality changes) or "Regenerate Design" (for visual/layout
changes) whenever they're ready -- they can also keep replying here first if
they want to add more context.

Keep the whole reply under 4 sentences. Do not use markdown headers.
"""

feedback_chat_agent = Agent(
    name="Feedback Chat Agent",
    instructions=FEEDBACK_CHAT_INSTRUCTIONS,
)


async def generate_chat_reply(feature_name: str, feedback_history: list[str]) -> str:
    history_text = "\n".join(f"- {item}" for item in feedback_history)
    prompt = f"""
Feature: {feature_name}

Conversation so far (most recent last):
{history_text}
"""
    result = await Runner.run(feedback_chat_agent, prompt)
    return result.final_output
