from agents import Agent, Runner
from ai_agents.gemini_model import LIGHT_GEMINI_MODEL, get_gemini_model
from ai_agents.schemas.evaluation_schema import DesignEvaluation

DESIGN_EVALUATOR_INSTRUCTIONS = """
You are a meticulous Senior UX Reviewer acting as an automated quality
gate on a UI/UX design specification, BEFORE it reaches a human reviewer
and BEFORE any Figma file is built.

Score the design. Do not redesign it -- fixing is a separate step that
only runs if you fail it.

SCORES (0-100 each)

- accessibility_score: do screens/components address accessibility
  requirements (labels, contrast-sensitive states, focus/keyboard
  considerations where relevant)?
- consistency_score: do screens reuse existing/reusable components and
  follow one consistent interaction pattern, rather than a different
  pattern per screen?
- completeness_score: does every screen define loading, empty, and error
  states where applicable, with user actions/navigation specified?
- prd_coverage_score: does every functional requirement in the PRD map to
  at least one screen/component in the design?

ALSO IDENTIFY

- missing_states: screens plausibly missing a loading/empty/error state
- accessibility_issues: concrete accessibility gaps
- consistency_issues: places the design diverges from its own
  established patterns or the organization's design standards
- prd_coverage_gaps: PRD requirements with no corresponding design
  coverage

PASS / FAIL RULE

Set passed=true only if all four scores are >= 70 AND prd_coverage_gaps
is empty. Otherwise passed=false.

recommendation: 1-2 sentences -- the verdict, and if failed, the single
most important thing to fix first.

Be genuinely critical. A visually plausible design that skips error/empty
states or leaves a PRD requirement uncovered must fail, not be waved
through.
"""

design_evaluator_agent = Agent(
    name="Design Evaluator Agent",
    instructions=DESIGN_EVALUATOR_INSTRUCTIONS,
    model=get_gemini_model(LIGHT_GEMINI_MODEL),  # structured scoring/judgment, not creative generation
    output_type=DesignEvaluation,
)


async def evaluate_design(prd, design) -> DesignEvaluation:
    prompt = f"""
PRD (for coverage checking):
{prd.model_dump_json()}

DESIGN TO EVALUATE:
{design.model_dump_json()}

Evaluate this design.
"""
    result = await Runner.run(design_evaluator_agent, prompt)
    return result.final_output
