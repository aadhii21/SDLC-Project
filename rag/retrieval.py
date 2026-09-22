import logging

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from config.settings import settings
from ai_agents.gemini_embeddings import get_gemini_embeddings

logger = logging.getLogger(__name__)

# Built lazily on first use, not at import time -- importing this module
# (e.g. transitively via design_agent.py) must not require Qdrant to
# already be reachable.
_vector_store = None


def _get_vector_store():
    global _vector_store
    if _vector_store is None:
        embeddings = get_gemini_embeddings()
        client = QdrantClient(url=settings.qdrant_url or "http://localhost:6333")
        _vector_store = QdrantVectorStore(
            embedding=embeddings,
            client=client,
            collection_name="sdlc_knowledge",
        )
    return _vector_store


def retrieve_documents(query: str) -> str:
    # Best-effort, like ai_agents/learning/store.py -- an embedding-provider
    # hiccup (confirmed live: the free-tier daily embedding quota) must
    # degrade design generation to "no org design-standards context"
    # rather than crash it outright.
    try:
        # k=4 -> retrieve the top 4 most similar chunks from Qdrant for the query.
        docs = _get_vector_store().similarity_search(query=query, k=4)
    except Exception:
        logger.exception("Failed to retrieve design-standards RAG context -- continuing without it")
        return ""

    # Join the retrieved LangChain Documents' page_content into one string
    # to pass to the agent as RAG context.
    return "\n\n".join(doc.page_content for doc in docs)
