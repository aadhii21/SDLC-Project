import uuid
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
from ai_agents.jira.comments import add_jira_comment
from ai_agents.jira.mapper import prd_description_text
from ai_agents.design_agent.design_agent import generate_design
from ai_agents.design_agent.figma_generator import generate_figma_design
from ai_agents.schemas.prd_schema import JiraPRD
from slack.blocks import design_generation_approval_block

#states
class PipelineState(TypedDict):
    user_query: str
    channel_id: str
    slack_thread_ts: str        # Slack message ts to thread all replies under
    thread_id: str              # LangGraph checkpoint thread id (uuid4) -- NOT the same as slack_thread_ts
    research_context: Optional[str]
    prd: Optional[JiraPRD]
    jira_parent_key: Optional[str]
    jira_children: Optional[list]
    approved: Optional[bool]
    design: Optional[object]
    figma_result: Optional[object]
    error: Optional[str]


#nodes
async def research_node(state: PipelineState) -> dict:
    context = await run_research_agent(state["user_query"])
    return {"research_context": context}


async def prd_node(state: PipelineState) -> dict:
    prd = await generate_jira_prd(state["user_query"], state["research_context"])
    return {"prd": prd}


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
        thread_ts=state["slack_thread_ts"],
        text=state.get("error", "Something went wrong."),
    )
    return {}


# NODE 1 of 2 for the approval step: fires the Slack message.
# Runs exactly once -- never re-executes on resume, because the
# interrupt() call lives in a SEPARATE node below.
async def notify_approval_node(state: PipelineState) -> dict:
    jira_url = f"{settings.jira_base_url}/browse/{state['jira_parent_key']}"
    blocks = design_generation_approval_block(state["jira_parent_key"], jira_url, state["thread_id"])

    _slack_client().chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["slack_thread_ts"],
        text=f"Created Jira Epic {state['jira_parent_key']}",
        blocks=blocks,
    )
    return {}


# NODE 2 of 2: THIS is the one that actually pauses. On resume,
# Command(resume={"approved": bool}) becomes interrupt()'s return value --
# execution continues from this exact line, not from the top of the node.
def await_approval_node(state: PipelineState) -> dict:
    decision = interrupt({"waiting_for": "design_approval", "parent_key": state["jira_parent_key"]})
    return {"approved": decision.get("approved", False)}


def _route_after_approval(state: PipelineState) -> str:
    return "notify_generating_node" if state.get("approved") else "rejected_node"


async def rejected_node(state: PipelineState) -> dict:
    _slack_client().chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["slack_thread_ts"],
        text=f"Design generation for `{state['jira_parent_key']}` was rejected.",
    )
    return {}


# Processing ack for the long leg (design + Figma generation can take a
# couple of minutes) -- separate node so it runs exactly once, same reason
# notify_approval_node is split from await_approval_node.
async def notify_generating_node(state: PipelineState) -> dict:
    _slack_client().chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["slack_thread_ts"],
        text="🎨 Approved — generating the design and Figma file now. This can take a couple of minutes...",
    )
    return {}


async def design_node(state: PipelineState) -> dict:
    prd_text = f"{state['prd'].title}\n\n{prd_description_text(state['prd'])}"
    design = await generate_design(prd_text)
    return {"design": design}


async def figma_node(state: PipelineState) -> dict:
    try:
        figma_result = await generate_figma_design(state["design"])
    except Exception as error:
        return {"error": f"Design generation failed for `{state['jira_parent_key']}`: {error}"}
    return {"figma_result": figma_result}


def _route_after_figma(state: PipelineState) -> str:
    return "post_back_node" if state.get("figma_result") else "report_error_node"


async def post_back_node(state: PipelineState) -> dict:
    await add_jira_comment(
        state["jira_parent_key"],
        f"Figma design generated by the agent: {state['figma_result'].file_url}",
    )
    _slack_client().chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["slack_thread_ts"],
        text=f"Design generated for `{state['jira_parent_key']}`: {state['figma_result'].file_url}",
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
graph_builder.add_node("rejected_node", rejected_node)
graph_builder.add_node("notify_generating_node", notify_generating_node)
graph_builder.add_node("design_node", design_node)
graph_builder.add_node("figma_node", figma_node)
graph_builder.add_node("post_back_node", post_back_node)
# NOTE: _route_after_jira / _route_after_approval / _route_after_figma are
# routers (they return a node-name string), NOT nodes -- never add_node() them.

graph_builder.add_edge(START, "research_node")
graph_builder.add_edge("research_node", "prd_node")
graph_builder.add_edge("prd_node", "jira_node")
graph_builder.add_conditional_edges("jira_node", _route_after_jira)
graph_builder.add_edge("report_error_node", END)
graph_builder.add_edge("notify_approval_node", "await_approval_node")
graph_builder.add_conditional_edges("await_approval_node", _route_after_approval)
graph_builder.add_edge("rejected_node", END)
graph_builder.add_edge("notify_generating_node", "design_node")
graph_builder.add_edge("design_node", "figma_node")
graph_builder.add_conditional_edges("figma_node", _route_after_figma)
graph_builder.add_edge("post_back_node", END)


# --- Lazy singletons -----------------------------------------------------
# Mirrors the rag/retrieval.py fix from earlier today: don't touch external
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


async def start_pipeline(user_query: str, channel_id: str, slack_thread_ts: str) -> dict:
    graph = get_graph()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    return await graph.ainvoke(
        {
            "user_query": user_query,
            "channel_id": channel_id,
            "slack_thread_ts": slack_thread_ts,
            "thread_id": thread_id,
        },
        config,
    )


async def resume_pipeline(thread_id: str, approved: bool) -> dict:
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}
    return await graph.ainvoke(Command(resume={"approved": approved}), config)
