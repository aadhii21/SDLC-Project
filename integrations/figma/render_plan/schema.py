"""The contract between Python and the Figma plugin.

Every operation here maps to exactly ONE Figma Plugin API call (see
integrations/figma/plugin/code.ts's applyOperation switch statement). None
of them encode a design decision -- "which screens exist, what text they
contain, how they're grouped" is decided in compiler.py, in Python. The
plugin just replays whatever operations show up here, in order.

Deliberately NOT included: a generic "set any property" op, a stroke op,
width/height on frames. Every screen/section frame in this project uses
auto-layout with AUTO sizing (Figma computes the box from its children), so
nothing here has ever needed to set a fixed size or a border -- adding ops
nothing uses would just be unvalidated surface area.
"""
from typing import Annotated, List, Literal, Union

from pydantic import BaseModel, Field


class CreatePageOp(BaseModel):
    type: Literal["create_page"] = "create_page"
    ref: str
    name: str
    # True for exactly one page per plan -- the plugin switches the user's
    # visible page to this one after the plan finishes, so they land
    # somewhere useful instead of wherever they happened to be.
    activate: bool = False


class CreateFrameOp(BaseModel):
    type: Literal["create_frame"] = "create_frame"
    ref: str
    parent_ref: str  # a page ref or another frame ref
    name: str


class CreateTextOp(BaseModel):
    type: Literal["create_text"] = "create_text"
    ref: str
    parent_ref: str
    text: str
    font_size: int = 14
    bold: bool = False


class SetAutoLayoutOp(BaseModel):
    type: Literal["set_auto_layout"] = "set_auto_layout"
    ref: str  # must already exist as a frame
    direction: Literal["horizontal", "vertical"]
    spacing: int = 0
    padding: int = 0  # uniform on all 4 sides -- nothing here has needed asymmetric padding


class SetFillOp(BaseModel):
    type: Literal["set_fill"] = "set_fill"
    ref: str
    r: float = Field(ge=0, le=1)
    g: float = Field(ge=0, le=1)
    b: float = Field(ge=0, le=1)


class CreateComponentOp(BaseModel):
    type: Literal["create_component"] = "create_component"
    ref: str  # converts the frame already at this ref into a Component, in place


Operation = Annotated[
    Union[CreatePageOp, CreateFrameOp, CreateTextOp, SetAutoLayoutOp, SetFillOp, CreateComponentOp],
    Field(discriminator="type"),
]


class FigmaRenderPlan(BaseModel):
    operations: List[Operation]
    main_page_ref: str  # which ref's node.id goes into the reported file_url
    screen_names: List[str] = Field(default_factory=list)  # echoed back verbatim as built_screens
