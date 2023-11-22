from openai import OpenAI
import os

def getEmbeddings(input: string):
    try:
        openai = OpenAI(apiKey = os.getenv("OPENAI_API_KEY"))
        response = await openai.embeddings.create( 
            model = "text-embedding-ada-002",
            input = input.replace("\n", " ")
        )

        return response['data'][0]['embedding']

    except Exception as e:
        console.log("Error calling OpenAI embedding API: ", e)
        raise e