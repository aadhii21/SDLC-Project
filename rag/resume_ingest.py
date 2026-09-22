"""One-off resume script to finish an interrupted rag/ingest.py run,
picking up from whatever point count sdlc_knowledge already has, instead
of re-ingesting everything from scratch (which would duplicate the
chunks already indexed). Unlike the earlier ad-hoc attempt, this verifies
each batch actually landed in Qdrant before reporting success -- it does
NOT print success after a retry loop merely finishes; it prints success
only when Qdrant's own point count increased by the expected amount.
"""
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import RateLimitError
from qdrant_client import QdrantClient

load_dotenv()

from ai_agents.gemini_embeddings import get_gemini_embeddings  # noqa: E402

COLLECTION = "sdlc_knowledge"
BATCH_SIZE = 50
DELAY_BETWEEN_BATCHES = 5
MAX_RETRIES_PER_BATCH = 6
RETRY_WAIT_SECONDS = 15


def _load_all_chunks():
    knowledge_path = Path(__file__).parent.parent / "rag_knowledge"
    documents = []
    for file_path in sorted(knowledge_path.rglob("*.md")):
        content = file_path.read_text(encoding="utf-8")
        documents.append(
            Document(
                page_content=content,
                metadata={"source": str(file_path), "category": file_path.parent.name, "filename": file_path.name},
            )
        )
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=400)
    return splitter.split_documents(documents=documents)


def main():
    client = QdrantClient(url="http://localhost:6333")
    already_indexed = client.get_collection(COLLECTION).points_count
    print(f"Already indexed: {already_indexed}")

    chunks = _load_all_chunks()
    print(f"Total chunks: {len(chunks)}")

    remaining = chunks[already_indexed:]
    print(f"Remaining to ingest: {len(remaining)}")
    if not remaining:
        print("Nothing left to do.")
        return

    vector_store = QdrantVectorStore(embedding=get_gemini_embeddings(), client=client, collection_name=COLLECTION)

    for start in range(0, len(remaining), BATCH_SIZE):
        batch = remaining[start : start + BATCH_SIZE]
        before = client.get_collection(COLLECTION).points_count

        succeeded = False
        for attempt in range(1, MAX_RETRIES_PER_BATCH + 1):
            try:
                vector_store.add_documents(batch)
                succeeded = True
                break
            except RateLimitError:
                print(f"  rate limited, waiting {RETRY_WAIT_SECONDS}s (attempt {attempt}/{MAX_RETRIES_PER_BATCH})")
                time.sleep(RETRY_WAIT_SECONDS)

        after = client.get_collection(COLLECTION).points_count
        actually_added = after - before

        if not succeeded or actually_added != len(batch):
            print(
                f"STOPPING: batch starting at {already_indexed + start} did not fully land "
                f"(expected +{len(batch)}, got +{actually_added}). Quota is likely still exhausted."
            )
            print(f"Current verified total: {after}/{len(chunks)}")
            return

        print(f"Verified indexed: {after}/{len(chunks)}")
        time.sleep(DELAY_BETWEEN_BATCHES)

    final_count = client.get_collection(COLLECTION).points_count
    print(f"DONE -- verified final count: {final_count}/{len(chunks)}")


if __name__ == "__main__":
    main()
