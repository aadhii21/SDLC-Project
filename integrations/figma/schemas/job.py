from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from ai_agents.schemas.design_schema import DesignSpecification, FigmaGenerationResult
from integrations.figma.render_plan.schema import FigmaRenderPlan


class FigmaJobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class FigmaJob(BaseModel):
    job_id: str
    status: FigmaJobStatus
    design: DesignSpecification  # kept for traceability/debugging -- the plugin never sees this
    render_plan: FigmaRenderPlan  # what the plugin actually fetches and executes
    thread_id: str
    created_at: datetime
    updated_at: datetime
    result: Optional[FigmaGenerationResult] = None
    error: Optional[str] = None


# --- Request/response schemas for the FastAPI endpoints ---------------------


class CreateJobRequest(BaseModel):
    design: DesignSpecification
    thread_id: str


class CreateJobResponse(BaseModel):
    job_id: str
    status: FigmaJobStatus


class NextJobResponse(BaseModel):
    """job is None when there is currently no pending work -- the plugin
    should treat that as "poll again later", not an error. The plugin only
    ever sees render_plan, never the raw DesignSpecification."""
    job_id: Optional[str] = None
    render_plan: Optional[FigmaRenderPlan] = None


class CompleteJobRequest(BaseModel):
    file_key: str
    file_url: str
    built_screens: List[str] = Field(default_factory=list)
    notes: str = ""


class FailJobRequest(BaseModel):
    error: str


class JobResponse(BaseModel):
    job_id: str
    status: FigmaJobStatus
    result: Optional[FigmaGenerationResult] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
