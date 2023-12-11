import openai
import os

def get_embeddings(input: str):
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = api_key  # Set t
        response = openai.embeddings.create( 
            model = "text-embedding-ada-002",
            input = input.replace("\n", " ")
        )
        return response.data[0].embedding
    
    except Exception as e:
        raise e