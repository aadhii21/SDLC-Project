"""FastAPI routes the Figma plugin (and our own LangGraph process) talk to.

This module is the ONLY place that bridges the job queue back into
LangGraph -- job_service.py itself has no knowledge of graph.lang_graph, so
it stays independently testable. Every route requires the shared
X-Plugin-Token header (see auth.py); this service is meant to run on
localhost in dev, but the token still stops any other local process/tab
from creating fake jobs or spoofing plugin results.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException

from ai_agents.schemas.design_schema import FigmaGenerationResult
from integrations.figma.schemas.job import (
    CompleteJobRequest,
    CreateJobRequest,
    CreateJobResponse,
    FailJobRequest,
    JobResponse,
    NextJobResponse,
)
from integrations.figma.service import job_service
from integrations.figma.service.auth import verify_plugin_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/figma/jobs", tags=["figma"], dependencies=[Depends(verify_plugin_token)])


def _to_job_response(job) -> JobResponse:
    return JobResponse(
        job_id=job.job_id,
        status=job.status,
        result=job.result,
        error=job.error,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


async def _resume_pipeline(thread_id: str, resume_value: dict, job_id: str) -> None:
    # Imported lazily (not at module import time) so importing this router
    # never depends on Mongo already being reachable -- same reasoning as
    # graph.lang_graph's own lazy singletons.
    from graph.lang_graph import resume_pipeline

    try:
        await resume_pipeline(thread_id, resume_value)
    except Exception as error:
        logger.exception("Job %s finished but resuming pipeline thread %s failed", job_id, thread_id)
        raise HTTPException(
            status_code=502,
            detail=f"Job {job_id} was recorded, but resuming the pipeline failed: {error}",
        ) from error


@router.post("", response_model=CreateJobResponse, status_code=201)
async def create_job(request: CreateJobRequest) -> CreateJobResponse:
    job = await job_service.create_job(request.design, request.thread_id)
    return CreateJobResponse(job_id=job.job_id, status=job.status)


@router.get("/next", response_model=NextJobResponse)
async def get_next_job() -> NextJobResponse:
    job = await job_service.claim_next_job()
    if job is None:
        return NextJobResponse(job_id=None, render_plan=None)
    return NextJobResponse(job_id=job.job_id, render_plan=job.render_plan)


@router.post("/{job_id}/complete", response_model=JobResponse)
async def complete_job(job_id: str, request: CompleteJobRequest) -> JobResponse:
    result = FigmaGenerationResult(
        file_key=request.file_key,
        file_url=request.file_url,
        success=True,
        built_screens=request.built_screens,
        notes=request.notes,
    )
    try:
        job = await job_service.complete_job(job_id, result)
    except job_service.JobNotFoundError:
        raise HTTPException(status_code=404, detail=f"No job with id {job_id}")
    except job_service.InvalidJobTransitionError as error:
        raise HTTPException(status_code=409, detail=str(error))

    await _resume_pipeline(job.thread_id, {"result": result.model_dump()}, job_id)
    return _to_job_response(job)


@router.post("/{job_id}/fail", response_model=JobResponse)
async def fail_job(job_id: str, request: FailJobRequest) -> JobResponse:
    try:
        job = await job_service.fail_job(job_id, request.error)
    except job_service.JobNotFoundError:
        raise HTTPException(status_code=404, detail=f"No job with id {job_id}")
    except job_service.InvalidJobTransitionError as error:
        raise HTTPException(status_code=409, detail=str(error))

    await _resume_pipeline(job.thread_id, {"error": request.error}, job_id)
    return _to_job_response(job)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str) -> JobResponse:
    try:
        job = await job_service.get_job(job_id)
    except job_service.JobNotFoundError:
        raise HTTPException(status_code=404, detail=f"No job with id {job_id}")
    return _to_job_response(job)
