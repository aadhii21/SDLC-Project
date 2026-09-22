"""Shared Gemini embeddings factory -- used by rag/ingest.py, rag/retrieval.py,
and ai_agents/learning/store.py. Same OpenAI-SDK-compatible-endpoint approach
as gemini_model.py, so the whole pipeline (generation + embeddings) runs
through Gemini with no remaining OpenAI dependency.

`gemini-embedding-001` was chosen because it returns 3072-dimensional
vectors -- the exact dimension the existing Qdrant collections were created
with for OpenAI's text-embedding-3-large, so switching providers needed no
collection migration.

Known limitation: langchain's OpenAIEmbeddings pre-tokenizes with tiktoken
and sends token-ID arrays by default (`check_embedding_ctx_length=True`,
the default) -- confirmed live to fail against Gemini's endpoint with
`501 UNIMPLEMENTED`. `check_embedding_ctx_length=False` is required so it
sends raw text instead.
"""
from langchain_openai import OpenAIEmbeddings

from config.settings import settings
from ai_agents.gemini_model import GEMINI_BASE_URL

GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"
GEMINI_EMBEDDING_DIM = 3072

_embeddings: OpenAIEmbeddings | None = None


def get_gemini_embeddings() -> OpenAIEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(
            model=GEMINI_EMBEDDING_MODEL,
            api_key=settings.gemini_api_key or "not-configured",
            base_url=GEMINI_BASE_URL,
            check_embedding_ctx_length=False,
        )
    return _embeddings
