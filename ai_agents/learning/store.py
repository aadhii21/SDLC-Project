"""Self-learning store: remembers approved PRDs/designs and reviewer
feedback in Qdrant, so future generations can retrieve real past-approved
examples and recurring feedback themes as few-shot guidance instead of
starting from a blank slate every time.

Best-effort by design -- a Qdrant hiccup here must never break epic
creation or design generation, so every public function swallows its own
errors and degrades to a no-op / empty result.
"""
import hashlib
import logging
from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams

from config.settings import settings
from ai_agents.gemini_embeddings import GEMINI_EMBEDDING_DIM, get_gemini_embeddings

logger = logging.getLogger(__name__)

EMBEDDING_DIM = GEMINI_EMBEDDING_DIM

APPROVED_PRDS_COLLECTION = "approved_prds"
APPROVED_DESIGNS_COLLECTION = "approved_designs"
REVIEWER_FEEDBACK_COLLECTION = "reviewer_feedback"

# Lazy singletons -- mirrors rag/retrieval.py: importing this module must
# not require Qdrant/Gemini credentials to already be resolvable.
_client: Optional[QdrantClient] = None


def _get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=settings.qdrant_url or "http://localhost:6333")
    return _client


def _get_embeddings():
    return get_gemini_embeddings()


def _ensure_collection(name: str) -> None:
    client = _get_client()
    if not client.collection_exists(name):
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )


def _point_id(*parts: str) -> int:
    # Deterministic id from the parts -- re-recording the same source (e.g.
    # the same Jira epic key) upserts in place instead of duplicating.
    digest = hashlib.sha1("::".join(parts).encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def _upsert(collection: str, point_id: int, text: str, payload: dict) -> None:
    _ensure_collection(collection)
    vector = _get_embeddings().embed_query(text)
    _get_client().upsert(
        collection_name=collection,
        points=[PointStruct(id=point_id, vector=vector, payload=payload)],
    )


def _search(collection: str, text: str, k: int, query_filter: Optional[Filter] = None) -> list[dict]:
    client = _get_client()
    if not client.collection_exists(collection):
        return []
    vector = _get_embeddings().embed_query(text)
    results = client.query_points(
        collection_name=collection,
        query=vector,
        limit=k,
        query_filter=query_filter,
    )
    return [point.payload for point in results.points if point.payload]


# --- Approved epics ----------------------------------------------------------

def record_approved_prd(user_query: str, jira_parent_key: str, prd) -> None:
    try:
        _upsert(
            APPROVED_PRDS_COLLECTION,
            _point_id(jira_parent_key),
            f"{user_query}\n\n{prd.title}\n\n{prd.description}",
            {"user_query": user_query, "jira_parent_key": jira_parent_key, "prd": prd.model_dump()},
        )
    except Exception:
        logger.exception(f"Failed to record approved PRD for {jira_parent_key} -- continuing without it")


def retrieve_similar_approved_prds(user_query: str, k: int = 2) -> list[dict]:
    try:
        return _search(APPROVED_PRDS_COLLECTION, user_query, k)
    except Exception:
        logger.exception("Failed to retrieve similar approved PRDs -- continuing without them")
        return []


# --- Approved designs ---------------------------------------------------------

def record_approved_design(jira_parent_key: str, design) -> None:
    try:
        _upsert(
            APPROVED_DESIGNS_COLLECTION,
            _point_id(jira_parent_key),
            f"{design.feature_name}\n\n{design.design_summary}",
            {"jira_parent_key": jira_parent_key, "design": design.model_dump()},
        )
    except Exception:
        logger.exception(f"Failed to record approved design for {jira_parent_key} -- continuing without it")


def retrieve_similar_approved_designs(prd_text: str, k: int = 2) -> list[dict]:
    try:
        return _search(APPROVED_DESIGNS_COLLECTION, prd_text, k)
    except Exception:
        logger.exception("Failed to retrieve similar approved designs -- continuing without them")
        return []


# --- Reviewer feedback ---------------------------------------------------------
# Recorded regardless of whether the run that produced it eventually got
# approved -- a rejection reason is a real signal of what reviewers want,
# independent of how that particular draft turned out.

def record_reviewer_feedback(stage: str, context_text: str, feedback_items: list[str]) -> None:
    for item in feedback_items:
        if not item:
            continue
        try:
            _upsert(
                REVIEWER_FEEDBACK_COLLECTION,
                _point_id(stage, item),
                item,
                {"stage": stage, "context": context_text[:500], "feedback": item},
            )
        except Exception:
            logger.exception(f"Failed to record {stage} reviewer feedback -- continuing without it")


def retrieve_relevant_feedback(stage: str, context_text: str, k: int = 3) -> list[dict]:
    try:
        query_filter = Filter(must=[FieldCondition(key="stage", match=MatchValue(value=stage))])
        return _search(REVIEWER_FEEDBACK_COLLECTION, context_text, k, query_filter=query_filter)
    except Exception:
        logger.exception(f"Failed to retrieve {stage} reviewer feedback -- continuing without it")
        return []
