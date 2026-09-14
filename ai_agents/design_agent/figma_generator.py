import asyncio
import json
import re

from ai_agents.schemas.design_schema import DesignSpecification, FigmaGenerationResult
from config.settings import settings

# Figma's remote MCP server only accepts OAuth registration from a small
# allowlist of named clients (Claude Code, Cursor, Windsurf) -- a
# from-scratch OAuth client gets a flat 403 on Dynamic Client Registration,
# confirmed both via our own client and a bare unauthenticated curl to
# Figma's registration endpoint. So instead of talking to the Figma MCP
# server ourselves, we shell out to the `claude` CLI (already an
# allowlisted, already-authenticated client) and let it do the MCP calls.
FIGMA_TOOL_PREFIX = "mcp__claude_ai_Figma__"

ALLOWED_FIGMA_TOOLS = [
    f"{FIGMA_TOOL_PREFIX}create_new_file",
    f"{FIGMA_TOOL_PREFIX}use_figma",
    f"{FIGMA_TOOL_PREFIX}get_figma_skill",
    f"{FIGMA_TOOL_PREFIX}get_screenshot",
    f"{FIGMA_TOOL_PREFIX}get_metadata",
    f"{FIGMA_TOOL_PREFIX}whoami",
]

FIGMA_GENERATION_INSTRUCTIONS = """
You are a Figma design generation agent. You have access to Figma's MCP tools
(create_new_file, use_figma, get_screenshot, get_metadata, whoami, get_figma_skill).

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
   looks correct.

Follow the design specification exactly. Prefer reusable components where
the specification calls for them. Include loading, empty, validation and
error states where the specification lists them. Do not alter business
requirements. Never fabricate a Figma URL -- it must come from create_new_file.

FINAL OUTPUT

End your response with exactly one JSON object on its own line, in this
shape, and nothing else after it:
{"file_key": "<file_key from create_new_file>", "file_url": "https://www.figma.com/design/<file_key>", "notes": "<one sentence summary of what was built>"}
"""


def _build_prompt(design: DesignSpecification) -> str:
    plan_key_line = (
        settings.figma_team_plan_key
        if settings.figma_team_plan_key
        else "(not configured -- call whoami and pick the first plan)"
    )

    return f"""{FIGMA_GENERATION_INSTRUCTIONS}

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


def _extract_result(result_text: str) -> FigmaGenerationResult:
    match = re.search(r"\{.*\}", result_text, re.DOTALL)

    if not match:
        raise RuntimeError(
            f"Could not find a JSON result in the Figma generation output:\n{result_text}"
        )

    return FigmaGenerationResult.model_validate_json(match.group(0))


async def generate_figma_design(design: DesignSpecification) -> FigmaGenerationResult:
    prompt = _build_prompt(design)

    proc = await asyncio.create_subprocess_exec(
        "claude",
        "-p", prompt,
        "--output-format", "json",
        "--allowedTools", ",".join(ALLOWED_FIGMA_TOOLS),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(
            f"claude CLI exited with {proc.returncode}: {stderr.decode(errors='replace')[:2000]}"
        )

    payload = json.loads(stdout.decode())

    if payload.get("is_error") or payload.get("subtype") != "success":
        raise RuntimeError(f"Figma generation did not complete successfully: {payload.get('result')}")

    return _extract_result(payload.get("result", ""))
