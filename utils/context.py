from pinecone import get_matches_from_embeddings;
from embeddings import getEmbeddings;
from dataclasses import dataclass

@dataclass
class Metadata:
    url: str
    text: str
    chunk: str
    hash: str

def get_context(message: str, namespace: str, max_tokens : int = 3000, min_score : float = 0.7, get_only_text : bool = True, top_k : int = 3):
    embedding = await get_embeddings(message)
    matches = await get_matches_from_embeddings(embedding, top_k, namespace)

    qualifying_docs = []
    for match in matches:
        if match.score and match.score > min_score:
            try:
                metadata = json.loads(match.metadata)  # Assuming match.metadata is a JSON string
                qualifying_docs.append(Metadata(**metadata))
            except json.JSONDecodeError:
                raise Exception("Invalid JSON")

    if not get_only_text:
        return qualifying_docs
    
    docs = [doc.chunk for doc in qualifying_docs] if qualifying_docs else []
    return "\n".join(docs)[:max_tokens]
