import pinecone
from utils.chunked_upsert import chunked_upsert
from dataclasses import dataclass
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from hashlib import md5
from langchain.document_loaders import PyPDFLoader
from utils.truncateStringByBytes import truncate_string_by_bytes
import asyncio
from utils.embeddings import get_embeddings

@dataclass
class SeedOptions:
    chunk_size: int = 1500
    chunk_overlap: int = 50

async def parse_pdf(pdf_file):
    try:
        pdf_storage_dir = os.path.join(os.path.dirname(__file__), './tmp/pdf_storage')
        os.makedirs(pdf_storage_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_storage_dir, pdf_file.filename)
        pdf_file.save(pdf_path)

        loader = PyPDFLoader(pdf_path)
        pages = loader.load_and_split()
        os.remove(pdf_path)
        doc_strings = [{"content": page.page_content, "metadata": {"page_number": page.metadata['page'], "title": pdf_file.filename}} for page in pages]
        return doc_strings
    except Exception as e:
        raise e

async def upload_and_generate_embedding(file, index_name: str, options: SeedOptions = SeedOptions()):
    try:
        pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))
        parsed_pdf = await parse_pdf(file)
        index_list = pinecone.list_indexes()
        if index_name not in index_list:
            pinecone.create_index(name=index_name, dimension=1536)
        index = pinecone.Index(index_name)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size = options.chunk_size, chunk_overlap = options.chunk_overlap, length_function = len, is_separator_regex = False)
        chunked_pdf = await asyncio.gather(*[chunk_pdf(x, text_splitter) for x in parsed_pdf])
        chunked_pdf = [item for sublist in chunked_pdf for item in sublist]
        vectors = await asyncio.gather(*[embed_chunks(chunk) for chunk in chunked_pdf])
        await chunked_upsert(index=index, vectors=vectors)
        return vectors[0]
    except Exception as e:
        raise e

async def embed_chunks(doc):
    try:
        embedding = get_embeddings(doc["page_content"])
        hashed = md5(doc["page_content"].encode()).hexdigest()
        hashed_doc_id = md5(doc["metadata"]["title"].encode()).hexdigest()
        return {
            "id": hashed,
            "values": embedding,
            "metadata": {
                "chunk": doc["page_content"],
                "hash": doc["metadata"]["hash"],
                "page_number": doc["metadata"]["page_number"],
                "doc_id": hashed_doc_id
            }
        }
    except Exception as e:
        raise e
        
async def chunk_pdf(page, splitter):
    docs = splitter.create_documents([page["content"]])
    proc_docs = [{"page_content": doc.page_content, "metadata": {**doc.metadata, **page["metadata"], "hash": md5(doc.page_content.encode()).hexdigest()}} for doc in docs]
    return proc_docs

    
