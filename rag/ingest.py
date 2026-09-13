from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
import os
load_dotenv()
open_api_key=os.getenv("OPENAI_API_KEY")

if not open_api_key:
    raise ValueError ("OPEN_API_KEY is not configured")

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
embedding_mode=OpenAIEmbeddings(
    model="text-embedding-3-large"
)
vector_store=QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_mode,
    url="http://localhost:6333",
    collection_name="sdlc_knowledge"
)
print("Indexing of markdown documents done")

