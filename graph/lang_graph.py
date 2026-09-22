import asyncio
from typing_extensions import TypedDict
from typing import Optional

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from pymongo import MongoClient
from slack_sdk import WebClient

from config.settings import settings
from ai_agents.research_agent.search_planer_agent import RequestRejectedError, run_research_agent
from ai_agents.research_agent.writer_agent import generate_jira_prd
from ai_agents.jira.create_issues import create_jira_from_prd
from ai_agents.jira.comments import add_jira_comment
from ai_agents.jira.mapper import prd_description_text
from ai_agents.design_agent.design_agent import generate_design
from ai_agents.design_agent.formatting import design_summary_text
from ai_agents.schemas.prd_schema import JiraPRD
from ai_agents.schemas.design_schema import DesignSpecification, FigmaGenerationResult
from ai_agents.schemas.evaluation_schema import PRDEvaluation, DesignEvaluation
from integrations.figma.publisher import figma_publisher
from integrations.figma.render_plan.compiler import compile_design_to_render_plan
from ai_agents.evaluation.prd_evaluator import evaluate_prd
from ai_agents.evaluation.design_evaluator import evaluate_design as run_design_evaluation
from ai_agents.learning.store import (
    record_approved_design,
    record_approved_prd,
    record_reviewer_feedback,
    retrieve_relevant_feedback,
    retrieve_similar_approved_designs,
    retrieve_similar_approved_prds,
)
from slack.blocks import prd_approval_block, design_approval_block

#states
class PipelineState(TypedDict):
    user_query: str
    channel_id: str
    thread_id: str  # Slack root message ts -- doubles as the LangGraph checkpoint thread id
    research_context: Optional[str]
    prd: Optional[JiraPRD]  # current working draft -- overwritten on every rework, whether or not it's ever approved
    approved_prd: Optional[JiraPRD]  # set exactly once, the instant the epic is approved -- never touched again
    jira_parent_key: Optional[str]
    jira_children: Optional[list]
    approved: Optional[bool]
    design: Optional[object]  # current working draft -- overwritten on every rework, whether or not it's ever approved
    approved_design: Optional[object]  # set exactly once, the instant the design is approved -- never touched again
    figma_job_id: Optional[str]  # set by submit_figma_job_node -- the job the Figma plugin is polling for
    figma_result: Optional[object]
    error: Optional[str]
    feedback_history: Optional[list]
    prd_evaluation: Optional[object]  # PRDEvaluation -- automated quality gate verdict, shown to the human alongside the content
    prd_fix_attempts: Optional[int]
    best_prd: Optional[JiraPRD]  # best-scoring auto-fix attempt so far this round, in case the cap is hit without passing
    best_prd_evaluation: Optional[object]
    prd_learned_context: Optional[str]  # computed once per round, reused by every fix_prd_node call in that round
    design_evaluation: Optional[object]  # DesignEvaluation -- same idea, for the design stage
    design_fix_attempts: Optional[int]
    best_design: Optional[object]  # same "best attempt" tracking as best_prd, for the design auto-fix loop
    best_design_evaluation: Optional[object]
    design_learned_context: Optional[str]  # computed once per round, reused by every fix_design_node call in that round


# An evaluator-driven auto-fix loop that never converges would silently
# stall the reviewer forever -- cap it and surface to the human anyway,
# with the evaluator's last verdict attached so they know it wasn't silently
# cleared. Kept at 1 (not higher) for latency: each attempt is a full
# evaluate+regenerate LLM round trip, and best-of tracking (see
# finalize_best_prd_node/finalize_best_design_node) means a second attempt
# is not needed for safety -- it would only ever be presented if it scored
# at least as well as the first, never a regression.
#is only for your automatic evaluator → fix loop, before the PRD/design is shown to the human.
MAX_AUTO_FIX_ATTEMPTS = 1


#nodes

# RESEARCH NODE
# Input: user_query → run user_query with run_research_agent() → returns context → map context to research_context as Output
async def research_node(state: PipelineState) -> dict:
    # The scope guardrail (search_planer_agent.py) rejects off-topic, empty,
    # or prompt-injection input before any research/generation is spent on
    # it -- caught here so the pipeline reports it cleanly instead of
    # crashing on an unhandled agents-SDK exception.
    try:
        context = await run_research_agent(state["user_query"])
    except RequestRejectedError as error:
        return {"error": f"This request wasn't processed: {error}"}
    return {"research_context": context}
#              ↑ state key        ↑ value


# ROUTE AFTER RESEARCH
# Input: current state → check state["error"] → error: report_error_node | no error: prd_node
def _route_after_research(state: PipelineState) -> str:
    return "report_error_node" if state.get("error") else "prd_node"


# --- Epic (PRD) review loop -- runs entirely BEFORE any Jira ticket exists.
# Nothing is created until the reviewer explicitly approves this content.

# LEARNED PRD CONTEXT
# Input: user_query → retrieve similar approved PRDs + relevant PRD feedback from Qdrant
# → combine both into one text → Output: learned context used for better PRD generation


async def _learned_prd_context(user_query: str) -> str:

    # Run both Qdrant retrievals in parallel
    examples, themes = await asyncio.gather(
        asyncio.to_thread(
            retrieve_similar_approved_prds,
            user_query
        ),
        asyncio.to_thread(
            retrieve_relevant_feedback,
            "prd",
            user_query
        ),
    )

    # If Qdrant has no relevant previous knowledge
    if not examples and not themes:
        return ""

    parts = []

    # Add similar previously-approved PRDs
    if examples:
        parts.append(
            "PAST APPROVED EPICS FOR SIMILAR REQUESTS "
            "(match this org's style, structure, and level of detail; "
            "only reuse content that actually applies to this request):"
        )

        for ex in examples:
            prd = ex.get("prd", {})

            parts.append(
                f"- {prd.get('title', '(untitled)')}: "
                f"{prd.get('description', '')}"
            )

    # Add previous reviewer feedback
    if themes:
        parts.append(
            "\nRECURRING REVIEWER FEEDBACK ON SIMILAR PAST REQUESTS "
            "(proactively address these where relevant, so the first draft "
            "doesn't need the same correction again):"
        )

        for theme in themes:
            parts.append(
                f"- {theme.get('feedback', '')}"
            )

    # Convert the collected knowledge into one string
    return "\n".join(parts)

async def _generate_prd(state: PipelineState, feedback: Optional[list] = None) -> JiraPRD:
    # feedback=None means "use whatever the human reviewer said" (the normal
    # reject/rework path). An explicit feedback list is how the automated
    # evaluator's findings get applied instead, via fix_prd_node below --
    # same revision machinery, different source of the requested changes.
    if feedback is None:
        feedback = state.get("feedback_history") or []
    context = state["research_context"]

    # Computed once per round by prd_node/regenerate_prd_node and cached in
    # state -- every fix_prd_node call within the same round reuses it
    # instead of repeating identical Qdrant/embedding lookups.
    learned = state.get("prd_learned_context")
    if learned:
        context = f"{context}\n\n{learned}"

    return await generate_jira_prd(
        state["user_query"],
        context,
        previous_prd=state.get("prd") if feedback else None,
        feedback=feedback,
    )

# PRD EVALUATOR NODE
# Input: user_query + current PRD
# → evaluate PRD quality
# → save evaluation
# → compare score with previous best attempt
# → Output: prd_evaluation + best PRD/evaluation when applicable
def _prd_evaluator_feedback(evaluation) -> list:
    """Turn a failed PRDEvaluation's findings into feedback items the
    writer agent's existing REVISION MODE can apply, exactly like a human
    reviewer's rejection reason."""
    #to convert the evaluator's structured problems into clear feedback instructions that your Writer Agent can use to fix the PRD automatically
    items = [f"Add missing requirement: {m}" for m in evaluation.missing_requirements]
    items += [f"Resolve this contradiction: {c}" for c in evaluation.contradictions]
    items += [f"Clarify this ambiguous requirement: {a}" for a in evaluation.ambiguous_requirements]
    return items

#This function's purpose is to calculate one total score for the current PRD evaluation.
def _prd_overall_score(evaluation) -> int:
    return (
        evaluation.completeness_score
        + evaluation.clarity_score
        + evaluation.testability_score
        + evaluation.company_standard_score
    )


async def evaluate_prd_node(state: PipelineState) -> dict:
    evaluation = await evaluate_prd(state["user_query"], state["prd"])
    result = {"prd_evaluation": evaluation}

    # Track whichever attempt scored best so far -- a later auto-fix pass
    # isn't guaranteed to improve on an earlier one (observed live: a fix
    # that resolved missing requirements introduced new vague "as per
    # approved policy" language, dropping testability/clarity). If the cap
    # is hit without passing, we present the best attempt, not the last one.
    best_evaluation = state.get("best_prd_evaluation")
    if best_evaluation is None or _prd_overall_score(evaluation) >= _prd_overall_score(best_evaluation):
        result["best_prd"] = state["prd"]
        result["best_prd_evaluation"] = evaluation

    return result


def _route_after_prd_evaluation(state: PipelineState) -> str:
    evaluation = state["prd_evaluation"]
    if evaluation.passed:
        return "present_prd_node"
    attempts = state.get("prd_fix_attempts") or 0
    if attempts >= MAX_AUTO_FIX_ATTEMPTS:
        return "finalize_best_prd_node"
    return "fix_prd_node"


async def fix_prd_node(state: PipelineState) -> dict:
    feedback = _prd_evaluator_feedback(state["prd_evaluation"])
    attempts = (state.get("prd_fix_attempts") or 0) + 1
    return {
        "prd": await _generate_prd(state, feedback=feedback),
        "prd_fix_attempts": attempts,
    }


async def finalize_best_prd_node(state: PipelineState) -> dict:
    # Auto-fix hit its cap without ever passing -- roll back to whichever
    # attempt actually scored best rather than handing the reviewer
    # whatever the last (possibly regressed) attempt happened to produce.
    return {
        "prd": state["best_prd"],
        "prd_evaluation": state["best_prd_evaluation"],
    }


async def _start_prd_round(state: PipelineState) -> dict:
    """Shared by prd_node and regenerate_prd_node -- both start a fresh
    round, so both compute (once) and cache the learned context that every
    fix_prd_node call in this round will reuse."""
    learned = await _learned_prd_context(state["user_query"])
    prd = await _generate_prd({**state, "prd_learned_context": learned})
    return {
        "prd": prd,
        "prd_fix_attempts": 0,
        "best_prd": None,
        "best_prd_evaluation": None,
        "prd_learned_context": learned,
        # Cleared so present_prd_node never shows a stale verdict from a
        # previous round -- prd_node's own evaluate_prd_node overwrites this
        # moments later anyway; regenerate_prd_node skips evaluation
        # entirely, so this must be None rather than leftover.
        "prd_evaluation": None,
    }


async def prd_node(state: PipelineState) -> dict:
    return await _start_prd_round(state)


async def regenerate_prd_node(state: PipelineState) -> dict:
    return await _start_prd_round(state)


def _prd_evaluation_line(state: PipelineState) -> str:
    evaluation = state.get("prd_evaluation")
    if not evaluation:
        return ""
    if evaluation.passed:
        return (
            f"\n✅ Automated quality check passed (completeness {evaluation.completeness_score}, "
            f"clarity {evaluation.clarity_score}, testability {evaluation.testability_score})."
        )
    return (
        f"\n⚠️ Automated quality check still has concerns after "
        f"{state.get('prd_fix_attempts') or 0} auto-fix attempt(s): {evaluation.recommendation}"
    )


# Prints the generated epic content, then explicitly asks for approval.
# Reused both for the first draft and every reworked draft after a rejection.
# Posted as two messages -- a message with `blocks` set only renders the
# blocks (the buttons), NOT the plain `text`, which becomes just a fallback
# notification string. So the content goes out as its own plain-text message
# first, then the approval question + buttons follow as a second message.
async def present_prd_node(state: PipelineState) -> dict:
    prd = state["prd"]
    client = _slack_client()

    client.chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["thread_id"],
        text=f"*{prd.title}*\n\n{prd_description_text(prd)}\n{_prd_evaluation_line(state)}",
    )
    client.chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["thread_id"],
        text="Do you want to proceed with this as your epic?",
        blocks=prd_approval_block(state["thread_id"]),
    )
    return {}


# THIS is the one that actually pauses. On resume, Command(resume={"approved": bool})
# becomes interrupt()'s return value -- execution continues from this exact
# line, not from the top of the node.
def await_prd_approval_node(state: PipelineState) -> dict:
    decision = interrupt({"waiting_for": "prd_approval"})
    return {"approved": decision.get("approved", False)}


def _route_after_prd_approval(state: PipelineState) -> str:
    return "notify_creating_jira_node" if state.get("approved") else "ask_prd_why_node"


# Ack posted right after approval -- creating the epic + every child ticket
# is a handful of sequential Jira API calls, so the reviewer needs to know
# it's in progress rather than staring at a silent thread.
async def notify_creating_jira_node(state: PipelineState) -> dict:
    _slack_client().chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["thread_id"],
        text="⏳ Creating the Jira epic and sub-tasks. This can take a minute...",
    )
    return {}


async def ask_prd_why_node(state: PipelineState) -> dict:
    _slack_client().chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["thread_id"],
        text="Why? What would you like changed about the epic? Reply here with the reason.",
    )
    return {}


# Loops back into notify_reworking_prd_node -> regenerate_prd_node -> present_prd_node until approved.
def await_prd_feedback_node(state: PipelineState) -> dict:
    decision = interrupt({"waiting_for": "prd_feedback"})
    history = (state.get("feedback_history") or []) + [decision.get("text", "")]
    return {"feedback_history": history}


# Ack posted right after the reason comes in -- regeneration is an LLM call
# and can take a while, so the reviewer needs to know it's in progress
# rather than staring at a silent thread.
async def notify_reworking_prd_node(state: PipelineState) -> dict:
    _slack_client().chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["thread_id"],
        text="⏳ Reworking the epic based on your feedback. This can take a minute...",
    )
    return {}


# --- Jira epic creation -- only reached after the epic content is approved.

async def jira_node(state: PipelineState) -> dict:
    jira = await create_jira_from_prd(state["prd"], settings.jira_project_key)

    if not jira["success"]:
        return {
            "jira_parent_key": None,
            "error": f"Failed to create Jira ticket(s) at stage '{jira['stage']}': {jira['jira_error']}",
        }

    jira_url = f"{settings.jira_base_url}/browse/{jira['parent']}"
    _slack_client().chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["thread_id"],
        text=f"Epic created: <{jira_url}|{jira['parent']}>. Generating the design now...",
    )

    # Self-learning: this epic just got approved, and any feedback that led
    # to it is a real signal of what reviewers ask for -- both feed future
    # generations for similar requests via _learned_prd_context.
    record_approved_prd(state["user_query"], jira["parent"], state["prd"])
    feedback = state.get("feedback_history") or []
    if feedback:
        record_reviewer_feedback("prd", state["user_query"], feedback)

    return {
        "jira_parent_key": jira["parent"],
        "jira_children": jira["children"],
        "approved_prd": state["prd"],  # stamped exactly once, here, at the moment of approval
        "feedback_history": [],  # clear epic-stage feedback before the design stage starts
    }


def _route_after_jira(state: PipelineState) -> str:
    # jira_node signals failure by leaving jira_parent_key unset
    return "design_node" if state.get("jira_parent_key") else "report_error_node"


async def report_error_node(state: PipelineState) -> dict:
    _slack_client().chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["thread_id"],
        text=state.get("error", "Something went wrong."),
    )
    return {}


# --- Design review loop -- runs entirely BEFORE Figma is touched, so the
# (slow, expensive) Figma build only happens once the design content itself
# has been approved.

async def _learned_design_context(prd_text: str) -> str:
    """Same self-learning loop as _learned_prd_context, for designs -- same
    reasoning for running both lookups concurrently and caching the result
    per round (see design_node/regenerate_design_node)."""
    examples, themes = await asyncio.gather(
        asyncio.to_thread(retrieve_similar_approved_designs, prd_text),
        asyncio.to_thread(retrieve_relevant_feedback, "design", prd_text),
    )
    if not examples and not themes:
        return ""

    parts = []
    if examples:
        parts.append(
            "PAST APPROVED DESIGNS FOR SIMILAR FEATURES (match this org's "
            "conventions; only reuse content that actually applies here):"
        )
        for ex in examples:
            design = ex.get("design", {})
            parts.append(f"- {design.get('feature_name', '(untitled)')}: {design.get('design_summary', '')}")
    if themes:
        parts.append(
            "\nRECURRING REVIEWER FEEDBACK ON SIMILAR PAST DESIGNS (proactively "
            "address these where relevant):"
        )
        for theme in themes:
            parts.append(f"- {theme.get('feedback', '')}")
    return "\n".join(parts)


def _approved_prd_text(state: PipelineState) -> str:
    # Always the epic exactly as approved -- never the mid-rework "prd"
    # working draft -- no matter how many design rework loops have run since.
    # Falls back to "prd" for runs checkpointed before approved_prd existed.
    approved_prd = state.get("approved_prd") or state["prd"]
    return f"{approved_prd.title}\n\n{prd_description_text(approved_prd)}"


async def _generate_design(state: PipelineState, feedback: Optional[list] = None):
    prd_text = _approved_prd_text(state)

    # feedback=None means "use whatever the human reviewer said" (the normal
    # reject/rework path). An explicit feedback list is how the automated
    # evaluator's findings get applied instead, via fix_design_node below.
    if feedback is None:
        feedback = state.get("feedback_history") or []

    # Computed once per round by design_node/regenerate_design_node and
    # cached in state -- fix_design_node reuses it rather than repeating
    # identical Qdrant/embedding lookups on every auto-fix iteration.
    learned = state.get("design_learned_context")
    if learned:
        prd_text = f"{prd_text}\n\n{learned}"

    return await generate_design(
        prd_text,
        previous_design=state.get("design") if feedback else None,
        feedback=feedback,
    )


def _design_evaluator_feedback(evaluation) -> list:
    """Same idea as _prd_evaluator_feedback -- feed the design evaluator's
    findings back through the existing REVISION MODE machinery."""
    items = [f"Add this missing state: {m}" for m in evaluation.missing_states]
    items += [f"Fix this accessibility issue: {a}" for a in evaluation.accessibility_issues]
    items += [f"Fix this consistency issue: {c}" for c in evaluation.consistency_issues]
    items += [f"Cover this PRD requirement, not yet reflected in the design: {g}" for g in evaluation.prd_coverage_gaps]
    return items


def _design_overall_score(evaluation) -> int:
    return (
        evaluation.accessibility_score
        + evaluation.consistency_score
        + evaluation.completeness_score
        + evaluation.prd_coverage_score
    )


async def evaluate_design_node(state: PipelineState) -> dict:
    approved_prd = state.get("approved_prd") or state["prd"]
    evaluation = await run_design_evaluation(approved_prd, state["design"])
    result = {"design_evaluation": evaluation}

    # Same "best attempt so far" tracking as the PRD loop -- a later
    # auto-fix pass isn't guaranteed to improve on an earlier one.
    best_evaluation = state.get("best_design_evaluation")
    if best_evaluation is None or _design_overall_score(evaluation) >= _design_overall_score(best_evaluation):
        result["best_design"] = state["design"]
        result["best_design_evaluation"] = evaluation

    return result


def _route_after_design_evaluation(state: PipelineState) -> str:
    evaluation = state["design_evaluation"]
    if evaluation.passed:
        return "present_design_node"
    attempts = state.get("design_fix_attempts") or 0
    if attempts >= MAX_AUTO_FIX_ATTEMPTS:
        return "finalize_best_design_node"
    return "fix_design_node"


async def fix_design_node(state: PipelineState) -> dict:
    feedback = _design_evaluator_feedback(state["design_evaluation"])
    attempts = (state.get("design_fix_attempts") or 0) + 1
    return {
        "design": await _generate_design(state, feedback=feedback),
        "design_fix_attempts": attempts,
    }


async def finalize_best_design_node(state: PipelineState) -> dict:
    # Auto-fix hit its cap without ever passing -- roll back to whichever
    # attempt actually scored best, same reasoning as finalize_best_prd_node.
    return {
        "design": state["best_design"],
        "design_evaluation": state["best_design_evaluation"],
    }


async def _start_design_round(state: PipelineState) -> dict:
    """Shared by design_node and regenerate_design_node -- both start a
    fresh round, so both compute (once) and cache the learned context that
    every fix_design_node call in this round will reuse."""
    learned = await _learned_design_context(_approved_prd_text(state))
    design = await _generate_design({**state, "design_learned_context": learned})
    return {
        "design": design,
        "design_fix_attempts": 0,
        "best_design": None,
        "best_design_evaluation": None,
        "design_learned_context": learned,
        # Same reasoning as _start_prd_round -- avoid showing a stale
        # verdict from a previous round.
        "design_evaluation": None,
    }


async def design_node(state: PipelineState) -> dict:
    return await _start_design_round(state)


async def regenerate_design_node(state: PipelineState) -> dict:
    return await _start_design_round(state)


def _design_evaluation_line(state: PipelineState) -> str:
    evaluation = state.get("design_evaluation")
    if not evaluation:
        return ""
    if evaluation.passed:
        return (
            f"\n✅ Automated quality check passed (accessibility {evaluation.accessibility_score}, "
            f"consistency {evaluation.consistency_score}, PRD coverage {evaluation.prd_coverage_score})."
        )
    return (
        f"\n⚠️ Automated quality check still has concerns after "
        f"{state.get('design_fix_attempts') or 0} auto-fix attempt(s): {evaluation.recommendation}"
    )


# Same two-message split as present_prd_node -- `blocks` suppresses `text`,
# so the design content and the approval question go out separately.
async def present_design_node(state: PipelineState) -> dict:
    jira_url = f"{settings.jira_base_url}/browse/{state['jira_parent_key']}"
    client = _slack_client()

    client.chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["thread_id"],
        text=f"{design_summary_text(state['design'])}\n{_design_evaluation_line(state)}",
    )
    client.chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["thread_id"],
        text="Do you want to proceed with this design?",
        blocks=design_approval_block(state["jira_parent_key"], jira_url, state["thread_id"]),
    )
    return {}


def await_design_approval_node(state: PipelineState) -> dict:
    decision = interrupt({"waiting_for": "design_approval", "parent_key": state["jira_parent_key"]})
    return {"approved": decision.get("approved", False)}


def _route_after_design_approval(state: PipelineState) -> str:
    return "notify_generating_figma_node" if state.get("approved") else "ask_design_why_node"


async def ask_design_why_node(state: PipelineState) -> dict:
    _slack_client().chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["thread_id"],
        text=(
            "Why? What would you like changed about the design? "
            "(e.g. colors, layout, button placement) Reply here with the reason."
        ),
    )
    return {}


# Loops back into notify_reworking_design_node -> regenerate_design_node -> present_design_node until approved.
def await_design_feedback_node(state: PipelineState) -> dict:
    decision = interrupt({"waiting_for": "design_feedback", "parent_key": state["jira_parent_key"]})
    history = (state.get("feedback_history") or []) + [decision.get("text", "")]
    return {"feedback_history": history}


# Ack posted right after the reason comes in, same reasoning as
# notify_reworking_prd_node -- design regeneration is an LLM call too.
async def notify_reworking_design_node(state: PipelineState) -> dict:
    _slack_client().chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["thread_id"],
        text="⏳ Reworking the design based on your feedback. This can take a minute...",
    )
    return {}


# --- Figma build + post-back -- only reached once the design is approved.

async def notify_generating_figma_node(state: PipelineState) -> dict:
    _slack_client().chat_postMessage(
        channel=state["channel_id"],
        thread_ts=state["thread_id"],
        text="🎨 Building the Figma file now. This can take a couple of minutes...",
    )

    # Self-learning, same reasoning as jira_node -- this design just got
    # approved, and any feedback that led to it feeds future generations
    # for similar features via _learned_design_context.
    record_approved_design(state["jira_parent_key"], state["design"])
    feedback = state.get("feedback_history") or []
    if feedback:
        approved_prd = state.get("approved_prd") or state["prd"]
        record_reviewer_feedback("design", approved_prd.title, feedback)

    return {
        "approved_design": state["design"],  # stamped exactly once, here, at the moment of approval
        "feedback_history": [],
    }


async def submit_figma_job_node(state: PipelineState) -> dict:
    # Always the design exactly as approved -- never the mid-rework
    # "design" working draft -- no matter how many rework loops ran before it.
    # Goes through figma_publisher (integrations/figma/publisher.py), not a
    # concrete transport -- this node never imports integrations.figma.client
    # directly, so swapping the transport later never touches this file.
    # This only hands the job to the Figma job service (api/main.py) -- it
    # does NOT wait for the Figma plugin to actually build anything. That
    # wait happens in await_figma_job_node below, via interrupt(), the same
    # pause/resume mechanism already used for human approval -- a real
    # Figma plugin only runs while a person has it open inside the Figma
    # desktop app, so this step could be pending for minutes; blocking this
    # node on it would tie up the pipeline (and, if this runs in the same
    # process, the Slack Socket Mode connection) for that whole time.
    try:
        plan = compile_design_to_render_plan(state["approved_design"])
        job_id = await figma_publisher.publish(plan, state["approved_design"], state["thread_id"])
    except Exception as error:
        return {"error": f"Could not submit the Figma job for `{state['jira_parent_key']}`: {error}"}
    return {"figma_job_id": job_id}


def await_figma_job_node(state: PipelineState) -> dict:
    # Resumed from api/main.py's /figma/jobs/{id}/complete or .../fail
    # handler, via Command(resume={"result": {...}}) or
    # Command(resume={"error": "..."})  -- see integrations/figma/service/routes.py.
    decision = interrupt({"waiting_for": "figma_job", "job_id": state.get("figma_job_id")})
    if decision.get("error"):
        return {"error": f"Figma generation failed for `{state['jira_parent_key']}`: {decision['error']}"}
    return {"figma_result": FigmaGenerationResult(**decision["result"])}


def _route_after_submit_figma_job(state: PipelineState) -> str:
    return "await_figma_job_node" if state.get("figma_job_id") else "report_error_node"


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
graph_builder.add_node("evaluate_prd_node", evaluate_prd_node)
graph_builder.add_node("fix_prd_node", fix_prd_node)
graph_builder.add_node("finalize_best_prd_node", finalize_best_prd_node)
graph_builder.add_node("present_prd_node", present_prd_node)
graph_builder.add_node("await_prd_approval_node", await_prd_approval_node)
graph_builder.add_node("ask_prd_why_node", ask_prd_why_node)
graph_builder.add_node("await_prd_feedback_node", await_prd_feedback_node)
graph_builder.add_node("notify_reworking_prd_node", notify_reworking_prd_node)
graph_builder.add_node("regenerate_prd_node", regenerate_prd_node)
graph_builder.add_node("notify_creating_jira_node", notify_creating_jira_node)
graph_builder.add_node("jira_node", jira_node)
graph_builder.add_node("report_error_node", report_error_node)
graph_builder.add_node("design_node", design_node)
graph_builder.add_node("evaluate_design_node", evaluate_design_node)
graph_builder.add_node("fix_design_node", fix_design_node)
graph_builder.add_node("finalize_best_design_node", finalize_best_design_node)
graph_builder.add_node("present_design_node", present_design_node)
graph_builder.add_node("await_design_approval_node", await_design_approval_node)
graph_builder.add_node("ask_design_why_node", ask_design_why_node)
graph_builder.add_node("await_design_feedback_node", await_design_feedback_node)
graph_builder.add_node("notify_reworking_design_node", notify_reworking_design_node)
graph_builder.add_node("regenerate_design_node", regenerate_design_node)
graph_builder.add_node("notify_generating_figma_node", notify_generating_figma_node)
graph_builder.add_node("submit_figma_job_node", submit_figma_job_node)
graph_builder.add_node("await_figma_job_node", await_figma_job_node)
graph_builder.add_node("post_back_node", post_back_node)
# NOTE: _route_after_research / _route_after_prd_evaluation / _route_after_prd_approval /
# _route_after_jira / _route_after_design_evaluation / _route_after_design_approval /
# _route_after_submit_figma_job / _route_after_figma are routers (they return a node-name
# string), NOT nodes -- never add_node() them.

graph_builder.add_edge(START, "research_node")
graph_builder.add_conditional_edges("research_node", _route_after_research)
graph_builder.add_edge("prd_node", "evaluate_prd_node")
graph_builder.add_conditional_edges("evaluate_prd_node", _route_after_prd_evaluation)
graph_builder.add_edge("fix_prd_node", "evaluate_prd_node")  # re-check every auto-fix attempt
graph_builder.add_edge("finalize_best_prd_node", "present_prd_node")
graph_builder.add_edge("present_prd_node", "await_prd_approval_node")
graph_builder.add_conditional_edges("await_prd_approval_node", _route_after_prd_approval)
graph_builder.add_edge("notify_creating_jira_node", "jira_node")

graph_builder.add_edge("ask_prd_why_node", "await_prd_feedback_node")
graph_builder.add_edge("await_prd_feedback_node", "notify_reworking_prd_node")
graph_builder.add_edge("notify_reworking_prd_node", "regenerate_prd_node")
graph_builder.add_edge("regenerate_prd_node", "present_prd_node")  # human is already the quality gate on rework -- skip auto-evaluation to save the extra LLM call

graph_builder.add_conditional_edges("jira_node", _route_after_jira)
graph_builder.add_edge("report_error_node", END)

graph_builder.add_edge("design_node", "evaluate_design_node")
graph_builder.add_conditional_edges("evaluate_design_node", _route_after_design_evaluation)
graph_builder.add_edge("fix_design_node", "evaluate_design_node")  # re-check every auto-fix attempt
graph_builder.add_edge("finalize_best_design_node", "present_design_node")
graph_builder.add_edge("present_design_node", "await_design_approval_node")
graph_builder.add_conditional_edges("await_design_approval_node", _route_after_design_approval)

graph_builder.add_edge("ask_design_why_node", "await_design_feedback_node")
graph_builder.add_edge("await_design_feedback_node", "notify_reworking_design_node")
graph_builder.add_edge("notify_reworking_design_node", "regenerate_design_node")
graph_builder.add_edge("regenerate_design_node", "present_design_node")  # human is already the quality gate on rework -- skip auto-evaluation to save the extra LLM call

graph_builder.add_edge("notify_generating_figma_node", "submit_figma_job_node")
graph_builder.add_conditional_edges("submit_figma_job_node", _route_after_submit_figma_job)
graph_builder.add_conditional_edges("await_figma_job_node", _route_after_figma)
graph_builder.add_edge("post_back_node", END)


# --- Lazy singletons -----------------------------------------------------
# Mirrors the rag/retrieval.py fix from earlier: don't touch external
# services (Mongo, Slack) at import time -- build them on first real use so
# importing this module never depends on Mongo/Slack already being up.
_mongo_client: Optional[MongoClient] = None
_slack_client_instance: Optional[WebClient] = None
_compiled_graph = None

DB_URL = "mongodb://localhost:27017"

# Every custom (non-JSON-native) type that ever appears as a PipelineState
# value gets checkpointed here. Passing this explicitly stops MongoDBSaver's
# default JsonPlusSerializer from falling back to its "unregistered type"
# path for these -- which today only warns, but is documented to start
# blocking deserialization entirely in a future langgraph-checkpoint release.
# Verified against every real pre-existing checkpoint in this Mongo instance:
# identical checkpoint content loads back either way, zero warnings with this
# list in place. If a new Pydantic type is ever added directly to
# PipelineState, add it here too, or it will be silently blocked (not just
# warned about) once encountered.
CHECKPOINTED_MODEL_TYPES = [JiraPRD, PRDEvaluation, DesignSpecification, DesignEvaluation, FigmaGenerationResult]


def _slack_client() -> WebClient:
    global _slack_client_instance
    if _slack_client_instance is None:
        _slack_client_instance = WebClient(token=settings.slack_bot_token)
    return _slack_client_instance


def get_graph():
    global _mongo_client, _compiled_graph
    if _compiled_graph is None:
        _mongo_client = MongoClient(DB_URL)
        serde = JsonPlusSerializer(allowed_msgpack_modules=CHECKPOINTED_MODEL_TYPES)
        checkpointer = MongoDBSaver(_mongo_client, serde=serde)
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
    # Without this, resuming an unknown thread_id doesn't fail cleanly --
    # Command(resume=...) against a thread with no checkpoint at all falls
    # through to running the graph from START with an empty state, which
    # crashes deep inside research_node with a confusing KeyError('user_query')
    # instead of saying what's actually wrong.
    if not graph.get_state(config).values:
        raise ValueError(f"No checkpoint found for thread_id '{thread_id}' -- nothing to resume.")
    return await graph.ainvoke(Command(resume=resume_value), config)


def get_pending_node(thread_id: str) -> Optional[str]:
    """Which node (if any) a paused run is currently waiting at. Used by the
    message-event handler to decide whether an incoming thread reply is
    actually feedback for a paused run, or just unrelated conversation."""
    graph = get_graph()
    state = graph.get_state({"configurable": {"thread_id": thread_id}})
    return state.next[0] if state.next else None


def get_jira_parent_key(thread_id: str) -> Optional[str]:
    """Read-only lookup of a paused run's Jira epic key, for the
    View Epic / View Sub Tasks buttons. Does NOT touch/resume the graph --
    those buttons must be side reads that leave the pending interrupt
    exactly as it was, so Approve/Reject etc. still work afterward."""
    graph = get_graph()
    state = graph.get_state({"configurable": {"thread_id": thread_id}})
    return state.values.get("jira_parent_key")


def has_existing_run(thread_id: str) -> bool:
    """True if this thread_id already has pipeline state. Slack redelivers
    an event (app_mention, slash command) if the handler doesn't finish
    fast enough -- e.g. the process being restarted mid-run, as happened
    live during testing, forked a single thread's checkpoint history into
    two concurrent branches. Callers must check this before start_pipeline()
    and skip if it's already true, so the same event can never start a
    second run on top of an existing one."""
    graph = get_graph()
    state = graph.get_state({"configurable": {"thread_id": thread_id}})
    return bool(state.values)
