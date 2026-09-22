"""Job storage abstraction for the Figma job queue.

InMemoryFigmaJobRepository is the only implementation today -- fine for a
single-process dev setup, and matches how everything else in this project
already runs (one Slack process, one LangGraph/Mongo checkpoint store). If
this ever needs to survive a process restart or run behind multiple workers,
swap in a Redis/Mongo-backed implementation of FigmaJobRepository; nothing
above this layer (job_service.py, routes.py) needs to change.
"""
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Optional

from integrations.figma.schemas.job import FigmaJob, FigmaJobStatus

# A job's plugin-facing life is minutes (poll, build, report back). Anything
# still sitting around finished this long after its last update is dead
# weight -- without this, a process left running for days would grow this
# dict forever, since nothing else ever removes a completed/failed job.
_FINISHED_JOB_RETENTION = timedelta(hours=1)

_TERMINAL_STATUSES = (FigmaJobStatus.completed, FigmaJobStatus.failed)


class FigmaJobRepository(ABC):
    @abstractmethod
    async def save(self, job: FigmaJob) -> None: ...

    @abstractmethod
    async def get(self, job_id: str) -> Optional[FigmaJob]: ...

    @abstractmethod
    async def claim_next_pending(self) -> Optional[FigmaJob]:
        """Atomically pick the oldest pending job and mark it processing,
        so two concurrent plugin instances can never claim the same job."""
        ...


class InMemoryFigmaJobRepository(FigmaJobRepository):
    def __init__(self) -> None:
        self._jobs: dict[str, FigmaJob] = {}
        self._lock = asyncio.Lock()

    def _prune_finished_locked(self) -> None:
        cutoff = datetime.now(timezone.utc) - _FINISHED_JOB_RETENTION
        stale = [
            job_id
            for job, job_id in ((j, j.job_id) for j in self._jobs.values())
            if job.status in _TERMINAL_STATUSES and job.updated_at < cutoff
        ]
        for job_id in stale:
            del self._jobs[job_id]

    async def save(self, job: FigmaJob) -> None:
        async with self._lock:
            self._jobs[job.job_id] = job
            self._prune_finished_locked()

    async def get(self, job_id: str) -> Optional[FigmaJob]:
        async with self._lock:
            return self._jobs.get(job_id)

    async def claim_next_pending(self) -> Optional[FigmaJob]:
        async with self._lock:
            pending = [j for j in self._jobs.values() if j.status == FigmaJobStatus.pending]
            if not pending:
                return None
            oldest = min(pending, key=lambda j: j.created_at)
            claimed = oldest.model_copy(
                update={"status": FigmaJobStatus.processing, "updated_at": datetime.now(timezone.utc)}
            )
            self._jobs[claimed.job_id] = claimed
            return claimed


_repository: Optional[FigmaJobRepository] = None


def get_repository() -> FigmaJobRepository:
    global _repository
    if _repository is None:
        _repository = InMemoryFigmaJobRepository()
    return _repository
