"""DesignSpecification -> FigmaRenderPlan. This is where every design
decision lives: which screens become frames, what a "Components" section
looks like, how reusable components and design notes are laid out.
integrations/figma/plugin/code.ts contains none of this -- it only knows how
to execute the operations produced here.
"""
import itertools
from typing import Iterator, List, Tuple

from ai_agents.schemas.design_schema import DesignSpecification, ScreenDesign, UIComponent
from integrations.figma.render_plan.schema import (
    CreateComponentOp,
    CreateFrameOp,
    CreatePageOp,
    CreateTextOp,
    FigmaRenderPlan,
    Operation,
    SetAutoLayoutOp,
    SetFillOp,
)

WHITE = (1.0, 1.0, 1.0)


class _RefCounter:
    """Human-readable, unique node references -- e.g. frame_3, text_11 --
    so a failed operation in the plugin's error report ("operation 14
    (create_text, ref=text_11) failed") is traceable back to this file."""

    def __init__(self) -> None:
        self._counters: dict[str, Iterator[int]] = {}

    def next(self, prefix: str) -> str:
        counter = self._counters.setdefault(prefix, itertools.count(1))
        return f"{prefix}_{next(counter)}"


def _component_summary_line(component: UIComponent) -> str:
    extras = []
    if component.states:
        extras.append(f"states: {', '.join(component.states)}")
    if component.validation:
        extras.append(f"validation: {', '.join(component.validation)}")
    suffix = f" ({'; '.join(extras)})" if extras else ""
    return f"{component.name} [{component.type}] -- {component.description}{suffix}"


def _append_section(ops: List[Operation], refs: _RefCounter, parent_ref: str, title: str, lines: List[str]) -> None:
    if not lines:
        return
    section_ref = refs.next("frame")
    ops.append(CreateFrameOp(ref=section_ref, parent_ref=parent_ref, name=title))
    ops.append(SetAutoLayoutOp(ref=section_ref, direction="vertical", spacing=6, padding=0))
    ops.append(CreateTextOp(ref=refs.next("text"), parent_ref=section_ref, text=title, font_size=13, bold=True))
    for line in lines:
        ops.append(CreateTextOp(ref=refs.next("text"), parent_ref=section_ref, text=f"- {line}", font_size=11))


def _append_screen(ops: List[Operation], refs: _RefCounter, screens_row_ref: str, screen: ScreenDesign) -> str:
    screen_ref = refs.next("frame")
    name = screen.screen_name or "Untitled screen"
    ops.append(CreateFrameOp(ref=screen_ref, parent_ref=screens_row_ref, name=name))
    ops.append(SetAutoLayoutOp(ref=screen_ref, direction="vertical", spacing=16, padding=24))
    ops.append(SetFillOp(ref=screen_ref, r=WHITE[0], g=WHITE[1], b=WHITE[2]))

    ops.append(CreateTextOp(ref=refs.next("text"), parent_ref=screen_ref, text=name, font_size=20, bold=True))
    if screen.purpose:
        ops.append(CreateTextOp(ref=refs.next("text"), parent_ref=screen_ref, text=screen.purpose, font_size=12))
    if screen.layout:
        ops.append(
            CreateTextOp(ref=refs.next("text"), parent_ref=screen_ref, text=f"Layout: {screen.layout}", font_size=11)
        )

    if screen.components:
        lines = [_component_summary_line(c) for c in screen.components]
        _append_section(ops, refs, screen_ref, "Components", lines)

    state_lines = (
        [f"Loading: {s}" for s in screen.loading_states]
        + [f"Empty: {s}" for s in screen.empty_states]
        + [f"Error: {s}" for s in screen.error_states]
    )
    _append_section(ops, refs, screen_ref, "States", state_lines)
    _append_section(ops, refs, screen_ref, "User Actions", screen.user_actions)
    _append_section(ops, refs, screen_ref, "Navigation", screen.navigation)
    _append_section(ops, refs, screen_ref, "Responsive Requirements", screen.responsive_requirements)

    return name


def _append_reusable_components_page(ops: List[Operation], refs: _RefCounter, names: List[str]) -> None:
    if not names:
        return
    page_ref = refs.next("page")
    ops.append(CreatePageOp(ref=page_ref, name="Reusable Components"))
    column_ref = refs.next("frame")
    ops.append(CreateFrameOp(ref=column_ref, parent_ref=page_ref, name="Components"))
    ops.append(SetAutoLayoutOp(ref=column_ref, direction="vertical", spacing=24, padding=0))

    for name in names:
        holder_ref = refs.next("frame")
        ops.append(CreateFrameOp(ref=holder_ref, parent_ref=column_ref, name=name))
        ops.append(SetAutoLayoutOp(ref=holder_ref, direction="vertical", spacing=8, padding=16))
        ops.append(CreateTextOp(ref=refs.next("text"), parent_ref=holder_ref, text=name, font_size=14, bold=True))
        ops.append(CreateComponentOp(ref=holder_ref))


def _append_notes_page(ops: List[Operation], refs: _RefCounter, design: DesignSpecification) -> None:
    sections: List[Tuple[str, List[str]]] = [
        ("Accessibility Requirements", design.accessibility_requirements),
        ("Design System Rules", design.design_system_rules),
        ("Assumptions", design.assumptions),
        ("Design Dependencies", design.design_dependencies),
    ]
    if not any(lines for _, lines in sections):
        return

    page_ref = refs.next("page")
    ops.append(CreatePageOp(ref=page_ref, name="Design Notes"))
    column_ref = refs.next("frame")
    ops.append(CreateFrameOp(ref=column_ref, parent_ref=page_ref, name="Notes"))
    ops.append(SetAutoLayoutOp(ref=column_ref, direction="vertical", spacing=24, padding=0))

    for title, lines in sections:
        _append_section(ops, refs, column_ref, title, lines)


def compile_design_to_render_plan(design: DesignSpecification) -> FigmaRenderPlan:
    ops: List[Operation] = []
    refs = _RefCounter()

    main_page_ref = refs.next("page")
    ops.append(CreatePageOp(ref=main_page_ref, name=design.feature_name or "Untitled feature", activate=True))

    # One horizontal auto-layout row holding every screen -- Figma spaces
    # the screens itself as their (auto-sized) widths change, so nothing
    # here has to predict a screen's rendered width to position the next
    # one, the way a page-level absolute x/y placement scheme would.
    screens_row_ref = refs.next("frame")
    ops.append(CreateFrameOp(ref=screens_row_ref, parent_ref=main_page_ref, name="Screens"))
    ops.append(SetAutoLayoutOp(ref=screens_row_ref, direction="horizontal", spacing=200, padding=0))

    screen_names = [_append_screen(ops, refs, screens_row_ref, screen) for screen in design.screens]

    _append_reusable_components_page(ops, refs, design.reusable_components)
    _append_notes_page(ops, refs, design)

    return FigmaRenderPlan(operations=ops, main_page_ref=main_page_ref, screen_names=screen_names)
