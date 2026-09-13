from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

from ai_agents.design_agent.figma_mcp_auth import build_oauth_provider
from ai_agents.schemas.design_schema import DesignSpecification, FigmaGenerationResult
from config.settings import settings

FIGMA_GENERATION_INSTRUCTIONS = """
You are a Figma design generation agent. You have access to Figma's MCP tools
(create_new_file, use_figma, get_screenshot, get_metadata, whoami, get_figma_skill, ...).

WORKFLOW

1. Call create_new_file to create a new Figma design file for this feature.
   - editorType: "design"
   - fileName: the feature name
   - planKey: use the configured plan key given below if present; otherwise
     call `whoami` and use the first plan's `key`.

2. Using the returned file_key, call use_figma to build out each screen in
   the design specification, following these rules:
   - Use `return` to send data back from every use_figma script; never call
     figma.closePlugin() or rely on console.log() for output.
   - Never call figma.notify() -- it throws "not implemented".
   - Switch pages with `await figma.setCurrentPageAsync(page)` -- the sync
     setter figma.currentPage = page does not work.
   - Colors are 0-1 range, e.g. {r: 1, g: 0, b: 0} for red.
   - Use figma.createAutoLayout() for any container whose children are
     stacked/side-by-side/aligned, instead of absolute x/y positioning.
   - Before editing text: load the font with `await figma.loadFontAsync(...)`
     first, then mutate `characters`/size/etc.
   - Work incrementally: one screen (or a small group of related nodes) per
     use_figma call, at most ~10 logical operations per call. Validate with
     get_metadata / a screenshot after each step before moving on.
   - Always return the created/mutated node IDs from every use_figma call.
   - Position new top-level nodes away from (0,0) to avoid overlapping
     existing content.
   - If you need the full rule set, call get_figma_skill with
     uri="skill://figma/figma-use/SKILL.md" before your first use_figma call.

3. After building all screens, take a final screenshot to confirm the result
   looks correct, then return the FigmaGenerationResult with file_key,
   file_url (https://www.figma.com/design/<file_key>), and a short note
   summarizing what was built.

Follow the design specification exactly. Prefer reusable components where
the specification calls for them. Include loading, empty, validation and
error states where the specification lists them. Do not alter business
requirements. Never fabricate a Figma URL -- it must come from create_new_file.
"""


def _build_prompt(design: DesignSpecification) -> str:
    plan_key_line = (
        settings.figma_team_plan_key
        if settings.figma_team_plan_key
        else "(not configured -- call whoami and pick the first plan)"
    )

    return f"""
Create the following product design in Figma.

Feature:
{design.feature_name}

Summary:
{design.design_summary}

Screens:
{design.screens}

Reusable Components:
{design.reusable_components}

Accessibility:
{design.accessibility_requirements}

Design System Rules:
{design.design_system_rules}

Configured Figma plan key: {plan_key_line}
"""


async def generate_figma_design(design: DesignSpecification) -> FigmaGenerationResult:
    oauth_provider = build_oauth_provider()

    async with MCPServerStreamableHttp(
        {"url": settings.figma_mcp_url, "auth": oauth_provider},
        name="figma",
    ) as figma_server:

        agent = Agent(
            name="Figma Generation Agent",
            instructions=FIGMA_GENERATION_INSTRUCTIONS,
            mcp_servers=[figma_server],
            output_type=FigmaGenerationResult,
        )

        result = await Runner.run(agent, _build_prompt(design))

    return result.final_output
