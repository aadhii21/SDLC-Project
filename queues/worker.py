from rag.retrieval import retrieve_documents
def process_query(query:str):
    docs=retrieve_documents(query)
    results=[]
    for doc in docs:
        results.append({
            "content":doc.page_content,
            "metadata":doc.metadata
        })
    return results
