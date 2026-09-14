from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from config.settings import settings

# Built lazily on first use, not at import time -- importing this module
# (e.g. transitively via design_agent.py) must not require Qdrant to
# already be reachable.
_vector_store = None


def _get_vector_store():
    global _vector_store
    if _vector_store is None:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        client = QdrantClient(url=settings.qdrant_url or "http://localhost:6333")
        _vector_store = QdrantVectorStore(
            embedding=embeddings,
            client=client,
            collection_name="sdlc_knowledge",
        )
    return _vector_store


def retrieve_documents(query: str) -> str:
    # k=4 -> retrieve the top 4 most similar chunks from Qdrant for the query.
    docs = _get_vector_store().similarity_search(query=query, k=4)

    # Join the retrieved LangChain Documents' page_content into one string
    # to pass to the agent as RAG context.
    return "\n\n".join(doc.page_content for doc in docs)
