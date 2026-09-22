import time
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
from openai import RateLimitError
import os

from ai_agents.gemini_embeddings import get_gemini_embeddings

load_dotenv()
gemini_api_key=os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError ("GEMINI_API_KEY is not configured")

KNOWLEDGE_PATH=Path(__file__).parent.parent/"rag_knowledge"
documents=[]
for file_path in KNOWLEDGE_PATH.rglob("*.md"):
    content=file_path.read_text(encoding="utf-8")
    docs = Document(
        page_content=content,
        metadata={
            "source":str(file_path),
            "category":file_path.parent.name,
            "filename":file_path.name
 
        }

    )
    documents.append(docs)
    #docs is only the last single Document created inside the loop.
print(f"Loaded{len(documents)}documents")

text_splitter=RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=400
)
chunks=text_splitter.split_documents(documents=documents)
print('Total chunks:',len(chunks))
embedding_mode=get_gemini_embeddings()

# Gemini's free-tier embedding quota is 100 requests/minute -- confirmed
# live by hitting 429s partway through both an unbatched from_documents()
# call and a naive fixed-delay batched retry. Retrying on the server's own
# suggested retry-after delay (from the 429 body) is more robust than
# guessing a fixed delay, since the rolling window depends on whatever
# else already hit the same quota (e.g. prior test calls).
BATCH_SIZE = 50
DELAY_SECONDS = 5
MAX_RETRIES_PER_BATCH = 6


def _add_with_retry(vector_store, batch):
    for attempt in range(1, MAX_RETRIES_PER_BATCH + 1):
        try:
            vector_store.add_documents(batch)
            return
        except RateLimitError as error:
            if attempt == MAX_RETRIES_PER_BATCH:
                raise
            wait_seconds = 15
            body = getattr(error, "body", None) or {}
            message = (body.get("error") or {}).get("message", "") if isinstance(body, dict) else ""
            if "retry in" in message:
                try:
                    wait_seconds = float(message.split("retry in")[1].split("s")[0].strip()) + 2
                except (IndexError, ValueError):
                    pass
            print(f"Rate limited, waiting {wait_seconds:.0f}s before retrying (attempt {attempt}/{MAX_RETRIES_PER_BATCH})...")
            time.sleep(wait_seconds)


first_batch = chunks[:BATCH_SIZE]
vector_store = None
for attempt in range(1, MAX_RETRIES_PER_BATCH + 1):
    try:
        vector_store=QdrantVectorStore.from_documents(
            documents=first_batch,
            embedding=embedding_mode,
            url="http://localhost:6333",
            collection_name="sdlc_knowledge"
        )
        break
    except RateLimitError:
        if attempt == MAX_RETRIES_PER_BATCH:
            raise
        print(f"Rate limited on first batch, waiting 15s (attempt {attempt}/{MAX_RETRIES_PER_BATCH})...")
        time.sleep(15)
print(f"Indexed batch 1: {min(BATCH_SIZE, len(chunks))}/{len(chunks)}")

for start in range(BATCH_SIZE, len(chunks), BATCH_SIZE):
    time.sleep(DELAY_SECONDS)
    batch = chunks[start:start + BATCH_SIZE]
    _add_with_retry(vector_store, batch)
    print(f"Indexed batch: {start + len(batch)}/{len(chunks)}")

print("Indexing of markdown documents done")

