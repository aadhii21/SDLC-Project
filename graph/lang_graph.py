from typing_extensions import TypedDict
from typing import Optional

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.mongodb import MongoDBSaver
from pymongo import MongoClient
from slack_sdk import WebClient

from config.settings import settings
from ai_agents.research_agent.search_planer_agent import run_research_agent
from ai_agents.research_agent.writer_agent import generate_jira_prd
from ai_agents.jira.create_issues import create_jira_from_prd
from ai_agents.jira.update_issue import update_jira_epic
from ai_agents.jira.comments import add_jira_comment
from ai_agents.jira.mapper import prd_description_text
from ai_agents.design_agent.design_agent import generate_design
from ai_agents.design_agent.figma_generator import generate_figma_design
from ai_agents.design_agent.feedback_chat import generate_chat_reply
from ai_agents.schemas.prd_schema import JiraPRD
from slack.blocks import design_generation_approval_block, regeneration_choice_block

#states
class PipelineState(TypedDict):
    user_query: str
    channel_id: str
    thread_id: str  # Slack root message ts -- doubles as the LangGraph checkpoint thread id
    research_context: Optional[str]
    prd: Optional[JiraPRD]
    jira_parent_key: Optional[str]
    jira_children: Optional[list]
    approved: Optional[bool]
    design: Optional[object]
    figma_result: Optional[object]
    error: Optional[str]
    feedback_history: Optional[list]
    last_decision_type: Optional[str]
    regeneration_target: Optional[str]


#nodes
async def research_node(state: PipelineState) -> dict:
    context = await run_research_agent(state["user_query"])
    return {"research_context": context}


async def _generate_prd(state: PipelineState) -> JiraPRD:
    context = state["research_context"]
    feedback = state.get("feedback_history") or []
    if feedback:
        context = f"{context}\n\nReviewer feedback on the previous PRD/design:\n" + "\n".join(feedback)
    return await generate_jira_prd(state["user_query"], context)


async def prd_node(state: PipelineState) -> dict:
    prd = await _generate_prd(state)
    return {"prd": prd}


async def regenerate_prd_node(state: PipelineState) -> dict:
    prd = await _generate_prd(state)
    return {"prd": prd}


async def update_jira_node(state: PipelineState) -> dict:
    await update_jira_epic(state["jira_parent_key"], state["prd"])
    feedback = "\n".join(state.get("feedback_history") or [])
    await add_jira_comment(
        state["jira_parent_key"],
        f"PRD updated based on reviewer feedback:\n{feedback}",
    )
    return {}


async def jira_node(state: PipelineState) -> dict:
    jira = await create_jira_from_prd(state["prd"], settings.jira_project_key)

    if not jira["success"]:
        return {
            "jira_parent_key": None,
            "error": f"Failed to create Jira ticket(s) at stage '{jira['stage']}': {jira['jira_error']}",
        }

    return {
        "jira_parent_key": jira["parent"],
        "jira_children": jira["children"],
    }


def _route_after_jira(state: PipelineState) -> str:
    # jira_node signals failure by leaving jira_parent_key unset
    return "notify_approval_node" if state.get("jira_parent_key") else "report_error_node"


async def report_error_node(state: PipelineState) -> dict:
    _slack_client().chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["thread_id"],
        text=state.get("error", "Something went wrong."),
    )
    return {}


# Runs exactly once per approval prompt -- never re-executes on resume,
# because the interrupt() call lives in a SEPARATE node below. Reused both
# the first time (right after Jira creation) and every time a regenerated
# design/PRD needs re-approval (looped back to from post_back_node).
async def notify_approval_node(state: PipelineState) -> dict:
    jira_url = f"{settings.jira_base_url}/browse/{state['jira_parent_key']}"
    blocks = design_generation_approval_block(state["jira_parent_key"], jira_url, state["thread_id"])

    _slack_client().chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["thread_id"],
        text=f"Ready to review the design for {state['jira_parent_key']}",
        blocks=blocks,
    )
    return {}


# THIS is the one that actually pauses. On resume, Command(resume={"approved": bool})
# becomes interrupt()'s return value -- execution continues from this exact
# line, not from the top of the node.
def await_approval_node(state: PipelineState) -> dict:
    decision = interrupt({"waiting_for": "design_approval", "parent_key": state["jira_parent_key"]})
    return {"approved": decision.get("approved", False)}


def _route_after_approval(state: PipelineState) -> str:
    return "notify_generating_node" if state.get("approved") else "ask_why_node"


async def ask_why_node(state: PipelineState) -> dict:
    _slack_client().chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["thread_id"],
        text="Why? What would you like changed? Reply here, or click a button below whenever you're ready.",
        blocks=regeneration_choice_block(state["thread_id"]),
    )
    return {}


# Loops on itself: every thread reply resumes here, gets classified as
# either a plain message (-> chat_reply_node, loop back) or a button choice
# (-> regenerate_prd_node / notify_generating_node).
def await_feedback_node(state: PipelineState) -> dict:
    decision = interrupt({"waiting_for": "feedback_or_choice", "parent_key": state["jira_parent_key"]})

    if decision.get("type") == "message":
        history = (state.get("feedback_history") or []) + [decision.get("text", "")]
        return {"last_decision_type": "message", "feedback_history": history}

    return {"last_decision_type": "choice", "regeneration_target": decision.get("target")}


def _route_after_feedback(state: PipelineState) -> str:
    if state.get("last_decision_type") == "message":
        return "chat_reply_node"
    target = state.get("regeneration_target")
    if target == "prd":
        return "regenerate_prd_node"
    if target == "design":
        return "notify_generating_node"
    return "await_feedback_node"  # shouldn't happen, but fail safe rather than crash


async def chat_reply_node(state: PipelineState) -> dict:
    reply = await generate_chat_reply(
        state["prd"].title if state.get("prd") else state["user_query"],
        state.get("feedback_history") or [],
    )
    _slack_client().chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["thread_id"],
        text=reply,
        blocks=regeneration_choice_block(state["thread_id"]),
    )
    return {}


# Processing ack for the long leg (design + Figma generation can take a
# couple of minutes). Also resets feedback_history -- it's been consumed by
# whichever path got here (regenerate_prd_node/update_jira_node, or
# straight from a "regenerate design" choice), so the next rejection cycle
# starts clean instead of re-surfacing already-addressed feedback.
async def notify_generating_node(state: PipelineState) -> dict:
    _slack_client().chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["thread_id"],
        text="🎨 Generating the design and Figma file now. This can take a couple of minutes...",
    )
    return {"feedback_history": []}


async def design_node(state: PipelineState) -> dict:
    prd_text = f"{state['prd'].title}\n\n{prd_description_text(state['prd'])}"
    return {"design": await generate_design(prd_text)}


async def figma_node(state: PipelineState) -> dict:
    try:
        figma_result = await generate_figma_design(state["design"])
    except Exception as error:
        return {"error": f"Design generation failed for `{state['jira_parent_key']}`: {error}"}
    return {"figma_result": figma_result}


def _route_after_figma(state: PipelineState) -> str:
    return "post_back_node" if state.get("figma_result") else "report_error_node"


async def post_back_node(state: PipelineState) -> dict:
    figma_result = state["figma_result"]
    built = ", ".join(figma_result.built_screens) if figma_result.built_screens else "(not reported)"

    message = (
        f"Design generated for `{state['jira_parent_key']}`: {figma_result.file_url}\n"
        f"Screens built: {built}\n"
        f"Notes: {figma_result.notes}"
    )

    await add_jira_comment(state["jira_parent_key"], message)
    _slack_client().chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["thread_id"],
        text=message,
    )
    return {}


#graph wiring
graph_builder = StateGraph(PipelineState)

graph_builder.add_node("research_node", research_node)
graph_builder.add_node("prd_node", prd_node)
graph_builder.add_node("jira_node", jira_node)
graph_builder.add_node("report_error_node", report_error_node)
graph_builder.add_node("notify_approval_node", notify_approval_node)
graph_builder.add_node("await_approval_node", await_approval_node)
graph_builder.add_node("ask_why_node", ask_why_node)
graph_builder.add_node("await_feedback_node", await_feedback_node)
graph_builder.add_node("chat_reply_node", chat_reply_node)
graph_builder.add_node("regenerate_prd_node", regenerate_prd_node)
graph_builder.add_node("update_jira_node", update_jira_node)
graph_builder.add_node("notify_generating_node", notify_generating_node)
graph_builder.add_node("design_node", design_node)
graph_builder.add_node("figma_node", figma_node)
graph_builder.add_node("post_back_node", post_back_node)
# NOTE: _route_after_jira / _route_after_approval / _route_after_feedback /
# _route_after_figma are routers (they return a node-name string), NOT
# nodes -- never add_node() them.

graph_builder.add_edge(START, "research_node")
graph_builder.add_edge("research_node", "prd_node")
graph_builder.add_edge("prd_node", "jira_node")
graph_builder.add_conditional_edges("jira_node", _route_after_jira)
graph_builder.add_edge("report_error_node", END)

graph_builder.add_edge("notify_approval_node", "await_approval_node")
graph_builder.add_conditional_edges("await_approval_node", _route_after_approval)

graph_builder.add_edge("ask_why_node", "await_feedback_node")
graph_builder.add_conditional_edges("await_feedback_node", _route_after_feedback)
graph_builder.add_edge("chat_reply_node", "await_feedback_node")

graph_builder.add_edge("regenerate_prd_node", "update_jira_node")
graph_builder.add_edge("update_jira_node", "notify_generating_node")

graph_builder.add_edge("notify_generating_node", "design_node")
graph_builder.add_edge("design_node", "figma_node")
graph_builder.add_conditional_edges("figma_node", _route_after_figma)
graph_builder.add_edge("post_back_node", "notify_approval_node")  # loop back for re-approval


# --- Lazy singletons -----------------------------------------------------
# Mirrors the rag/retrieval.py fix from earlier: don't touch external
# services (Mongo, Slack) at import time -- build them on first real use so
# importing this module never depends on Mongo/Slack already being up.
_mongo_client: Optional[MongoClient] = None
_slack_client_instance: Optional[WebClient] = None
_compiled_graph = None

DB_URL = "mongodb://localhost:27017"


def _slack_client() -> WebClient:
    global _slack_client_instance
    if _slack_client_instance is None:
        _slack_client_instance = WebClient(token=settings.slack_bot_token)
    return _slack_client_instance


def get_graph():
    global _mongo_client, _compiled_graph
    if _compiled_graph is None:
        _mongo_client = MongoClient(DB_URL)
        checkpointer = MongoDBSaver(_mongo_client)
        _compiled_graph = graph_builder.compile(checkpointer=checkpointer)
    return _compiled_graph


async def start_pipeline(user_query: str, channel_id: str, thread_id: str) -> dict:
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}
    return await graph.ainvoke(
        {
            "user_query": user_query,
            "channel_id": channel_id,
            "thread_id": thread_id,
            "feedback_history": [],
        },
        config,
    )


async def resume_pipeline(thread_id: str, resume_value: dict) -> dict:
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}
    return await graph.ainvoke(Command(resume=resume_value), config)


def get_pending_node(thread_id: str) -> Optional[str]:
    """Which node (if any) a paused run is currently waiting at. Used by the
    message-event handler to decide whether an incoming thread reply is
    actually feedback for a paused run, or just unrelated conversation."""
    graph = get_graph()
    state = graph.get_state({"configurable": {"thread_id": thread_id}})
    return state.next[0] if state.next else None
