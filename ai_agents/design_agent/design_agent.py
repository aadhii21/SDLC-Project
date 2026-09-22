from agents import Agent,Runner
from rag.retrieval import retrieve_documents
from ai_agents.gemini_model import get_gemini_model
from ai_agents.schemas.design_schema import DesignSpecification



DESIGN_AGENT_INSTRUCTIONS = """
You are a Senior Product Designer and UI/UX Architect.

Your responsibility is to convert an implementation-ready PRD
into a detailed UI/UX design specification.

You will receive:

1. Product requirements / PRD
2. Existing design references when available
3. Organization-specific UI/UX knowledge retrieved from the knowledge base

Your design must follow the organization's existing design language.

DESIGN PRINCIPLES

- Prefer existing reusable components over creating new ones.
- Follow existing typography, spacing, layout, interaction and navigation patterns.
- Never invent a Figma URL.
- Preserve existing Figma URLs exactly when provided.
- Clearly identify missing design information.
- Consider loading, empty, validation and error states.
- Consider responsive behaviour where applicable.
- Include accessibility requirements.
- Do not change business requirements.

SCREENS

For every required screen describe:

- Screen name
- Purpose
- Layout
- Components
- User actions
- Navigation
- Validation states
- Error states
- Empty states
- Loading states
- Responsive behaviour

COMPONENTS

For every major UI component include:

- Name
- Component type
- Purpose
- States
- Validations

DESIGN SYSTEM

Use organization-specific design knowledge from the provided context.

If existing components or patterns are present in the knowledge,
prefer them rather than creating new components.

FIGMA

If an existing Figma link is supplied:
- preserve the exact URL.

If no design exists:
- set figma_required to true.

Never fabricate design links.


REVISION MODE

If a PREVIOUS DESIGN and REQUESTED CHANGES are given below, that design is
the exact version already delivered to the reviewer. Change ONLY the
specific screen(s)/component(s)/property the requested changes call out
(e.g. colors, layout, button placement). Every other screen and
component must be carried through unchanged, verbatim, in the same
order -- do not rephrase, reorder, "clean up", or otherwise touch
anything the reviewer did not ask you to change. Do not regenerate the
design from scratch.
"""

design_agent=Agent(
    name="Design Agent",
    instructions=DESIGN_AGENT_INSTRUCTIONS,
    model=get_gemini_model(),
    output_type=DesignSpecification
)
async def generate_design(
        prd: str,
        previous_design: DesignSpecification | None = None,
        feedback: list[str] | None = None,
) -> DesignSpecification:
    design_context = retrieve_documents(prd)

    revision_block = ""
    if previous_design is not None and feedback:
        revision_block = f"""
PREVIOUS DESIGN (already delivered to the reviewer -- revise this, don't
start over):
{previous_design.model_dump_json()}

REQUESTED CHANGES FROM THE REVIEWER:
{chr(10).join("- " + item for item in feedback)}
"""

    prompt=f"""
PRODUCT REQUIREMENT
{prd}
ORGANIZATION DESIGN STANDARDS
{design_context}
{revision_block}
Generate a complete implementation-ready UI/UX design specification.

Follow the organization design knowledge whenever relevant.
Do not invent a Figma URL.
"""
    result= await Runner.run(
        design_agent,
        prompt
    )
    return result.final_output

