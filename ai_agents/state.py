from dataclasses import dataclass

from ai_agents.schemas.prd_schema import JiraPRD

# Process-local pending-approval store, keyed by the Jira epic (parent) key.
# Lost on process restart -- acceptable for now. The natural upgrade is to back
# this with Redis (already a dependency via queues/redis_queue.py) once the
# orchestration moves to LangGraph with real checkpointing.
_PENDING_APPROVALS: dict[str, "PendingApproval"] = {}


@dataclass
class PendingApproval:
    user_query: str
    prd: JiraPRD


def save_pending_approval(parent_key: str, user_query: str, prd: JiraPRD) -> None:
    _PENDING_APPROVALS[parent_key] = PendingApproval(user_query=user_query, prd=prd)


def get_pending_approval(parent_key: str) -> PendingApproval | None:
    return _PENDING_APPROVALS.get(parent_key)


def clear_pending_approval(parent_key: str) -> None:
    _PENDING_APPROVALS.pop(parent_key, None)
