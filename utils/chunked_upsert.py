import os

def slice_into_chunks(arr, chunk_size):
    """Splits a list into chunks of specified size."""
    return [arr[i:i + chunk_size] for i in range(0, len(arr), chunk_size)]

async def chunked_upsert(index, vectors, chunk_size = 10):
    """Upserts vectors into a Pinecone index in chunks."""
    try:
        upsert_response = index.upsert(vectors=vectors)
    except Exception as e:
        print('Error upserting chunk:', e)
        raise e
