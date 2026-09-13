from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from dotenv import load_dotenv
load_dotenv()
embddings=OpenAIEmbeddings(
    model="text-embedding-3-large"
)
qdrant_client=QdrantClient(
    url="http://localhost:6333"
)
vector_store=QdrantVectorStore(
    embedding=embddings,
    client=qdrant_client,
    collection_name="sdlc_knowledge"
)
def retrieve_documents(query:str):
    docs=vector_store.similarity_search(
        query=query,
#k=4 means retrieve the top 4 most similar/relevant chunks from Qdrant for the query.
        k=4
    )
#That line takes the retrieved LangChain Document objects and 
# converts their page_content into one string, which you can pass to your agent as RAG context.
    return "\n\n".join(
        doc.page_content
        for doc in docs
    )
