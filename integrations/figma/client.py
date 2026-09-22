"""HTTP client the LangGraph pipeline uses to submit work to the Figma job
service (api/main.py). A real HTTP call, not an in-process function call,
because the job queue is in-memory (integrations/figma/service/repository.py)
and must live in the SAME process the plugin polls -- i.e. the `uvicorn
api.main:app` process, not the `python -m slack.run` process this pipeline
runs in. Going over HTTP keeps that true regardless of which process ends up
calling this.
"""
import httpx

from config.settings import settings
from ai_agents.schemas.design_schema import DesignSpecification

REQUEST_TIMEOUT_SECONDS = 10.0


def _base_url() -> str:
    return f"http://127.0.0.1:{settings.figma_job_service_port}"


def _headers() -> dict:
    return {"X-Plugin-Token": settings.figma_plugin_api_token}


async def submit_figma_job(design: DesignSpecification, thread_id: str) -> str:
    """Creates a pending job on the Figma job service and returns its job_id.
    Raises on any non-2xx response or connection failure -- callers (figma_node)
    already convert exceptions into the pipeline's error state."""
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.post(
            f"{_base_url()}/figma/jobs",
            headers=_headers(),
            json={"design": design.model_dump(), "thread_id": thread_id},
        )
    response.raise_for_status()
    return response.json()["job_id"]
