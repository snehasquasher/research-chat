from utils.get_matches import get_matches_from_embeddings
from utils.embeddings import get_embeddings
from dataclasses import dataclass

@dataclass
class Metadata:
    url: str
    text: str
    chunk: str
    hashed: str

async def get_context(message: str, file_name = str, max_tokens : int = 3000, min_score : float = 0.7, get_only_text : bool = True, top_k : int = 3):
    embedding = get_embeddings(message)
    return embedding
    matches = await get_matches_from_embeddings(embedding, top_k, file_name)

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
