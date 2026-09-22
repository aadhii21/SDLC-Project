"""Job lifecycle for the Figma job queue. Pure job bookkeeping only -- this
module knows nothing about LangGraph/Slack/Mongo; the route handlers that
call complete_job/fail_job are the ones that resume the paused pipeline
(graph.lang_graph.resume_pipeline), keeping this package independently
testable and reusable.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from ai_agents.schemas.design_schema import DesignSpecification, FigmaGenerationResult
from integrations.figma.render_plan.compiler import compile_design_to_render_plan
from integrations.figma.schemas.job import FigmaJob, FigmaJobStatus
from integrations.figma.service.repository import FigmaJobRepository, get_repository


class JobNotFoundError(Exception):
    pass


class InvalidJobTransitionError(Exception):
    """Raised when the plugin reports completion/failure for a job that
    isn't currently in `processing` -- e.g. a duplicate completion call, or
    a stale retry after the job already failed."""
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def create_job(
    design: DesignSpecification,
    thread_id: str,
    repository: Optional[FigmaJobRepository] = None,
) -> FigmaJob:
    repository = repository or get_repository()
    now = _now()
    job = FigmaJob(
        job_id=uuid.uuid4().hex,
        status=FigmaJobStatus.pending,
        design=design,
        render_plan=compile_design_to_render_plan(design),
        thread_id=thread_id,
        created_at=now,
        updated_at=now,
    )
    await repository.save(job)
    return job


async def claim_next_job(repository: Optional[FigmaJobRepository] = None) -> Optional[FigmaJob]:
    repository = repository or get_repository()
    return await repository.claim_next_pending()


async def get_job(job_id: str, repository: Optional[FigmaJobRepository] = None) -> FigmaJob:
    repository = repository or get_repository()
    job = await repository.get(job_id)
    if job is None:
        raise JobNotFoundError(job_id)
    return job


async def complete_job(
    job_id: str,
    result: FigmaGenerationResult,
    repository: Optional[FigmaJobRepository] = None,
) -> FigmaJob:
    repository = repository or get_repository()
    job = await get_job(job_id, repository)
    if job.status != FigmaJobStatus.processing:
        raise InvalidJobTransitionError(
            f"job {job_id} is '{job.status.value}', not 'processing' -- refusing to complete it again"
        )
    updated = job.model_copy(
        update={"status": FigmaJobStatus.completed, "result": result, "updated_at": _now()}
    )
    await repository.save(updated)
    return updated


async def fail_job(
    job_id: str,
    error: str,
    repository: Optional[FigmaJobRepository] = None,
) -> FigmaJob:
    repository = repository or get_repository()
    job = await get_job(job_id, repository)
    if job.status != FigmaJobStatus.processing:
        raise InvalidJobTransitionError(
            f"job {job_id} is '{job.status.value}', not 'processing' -- refusing to fail it again"
        )
    updated = job.model_copy(update={"status": FigmaJobStatus.failed, "error": error, "updated_at": _now()})
    await repository.save(updated)
    return updated
