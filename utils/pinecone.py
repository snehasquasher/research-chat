import pinecone
import os

async def get_matches_from_embeddings(embeddings, top_k, namespace = ''):
    pinecone.init(
        api_key=os.getenv("PINECONE_API_KEY"), 
        environment=os.getenv("PINECONE_ENVIRONMENT"))
    
    index_name = os.getenv("PINECONE_INDEX") if os.getenv("PINECONE_INDEX") else ""
    if index_name == "":
        raise Exception("PINECONE_INDEX environment variable not set")
    
    indexes = pinecone.list_indexes()
    if index_name not in indexes:
        raise ValueError("Index ${index_name} does not exist")

    index = pinecone.Index(index_name=index_name)

    try:
        query_result = await index.query(
            namespace=namespace,
            top_k=top_k,
            vector=embeddings,
            include_metadata=True
        )
        return query_result
    except Exception as e:
        raise Exception("Error querying embeddings: ${e}")