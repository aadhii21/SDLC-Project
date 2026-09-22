"""Decouples LangGraph from the Figma publishing transport.

graph/lang_graph.py depends on FigmaPublisher, never on a concrete
transport. Swapping PluginFigmaPublisher for a future MCPFigmaPublisher or
DirectFigmaPublisher (if Figma ever opens direct MCP access) means adding
one class here and pointing `figma_publisher` at it -- nothing in
graph/lang_graph.py, the render-plan compiler, or the job service changes.
"""
from typing import Protocol

from ai_agents.schemas.design_schema import DesignSpecification
from integrations.figma.client import submit_figma_job
from integrations.figma.render_plan.schema import FigmaRenderPlan


class FigmaPublisher(Protocol):
    async def publish(self, plan: FigmaRenderPlan, design: DesignSpecification, thread_id: str) -> str:
        """Publish a validated FigmaRenderPlan. Returns a job id the caller
        can use to correlate the eventual completion/failure."""
        ...


class PluginFigmaPublisher:
    """Publishes via the existing FastAPI job service + thin Figma plugin
    (integrations/figma/service/, integrations/figma/plugin/), unchanged by
    this abstraction. `plan` isn't used directly here -- the existing job
    service recompiles it from `design` itself (job_service.create_job) --
    it's threaded through only so this class satisfies FigmaPublisher's
    shape; a future publisher whose transport actually accepts a render
    plan directly would use `plan` and could ignore `design` entirely."""

    async def publish(self, plan: FigmaRenderPlan, design: DesignSpecification, thread_id: str) -> str:
        return await submit_figma_job(design, thread_id)


figma_publisher: FigmaPublisher = PluginFigmaPublisher()
