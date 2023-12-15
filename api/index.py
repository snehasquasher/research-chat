from flask import Flask, request, jsonify, redirect
from openai import OpenAI
import pinecone
import os
from process_docs import upload_and_generate_embedding
from dotenv import load_dotenv
from hashlib import md5
from utils.context import get_context
import sys
import json
import logging
import os
os.environ['FLASK_ENV'] = 'development'
# Define the global variable here, at the top level
processed_filenames = []

load_dotenv()
app = Flask(__name__)
app.config['DEBUG'] = True
logger = logging.getLogger(__name__)

# Create a file handler
handler = logging.FileHandler("app.log")

# Add the handler to the logger
logger.addHandler(handler)

# Set the logging level
logger.setLevel(logging.DEBUG)
import routes
import evaluate
from dataclasses import dataclass

@dataclass
class SeedOptions:
    chunk_size: int = 1500
    chunk_overlap: int = 50
    method: str ='character'


@app.route("/api/chat", methods = ["POST"])
async def chat():
    """
    This endpoint handles POST requests for generating responses using the OpenAI API based on user messages.

    Request Body:
    -------------
    - messages (array): An array of message objects. Each object should have 'role' (user/system) and 'content'.
    - filename (List[str]): A list of filenames that are used for fetching context relevant to the conversation.

    Process:
    --------
    1. Initializes the OpenAI client using the API key.
    2. Extracts 'messages' and 'file_name' from the request's JSON body.
    3. Constructs the conversation context and prepares the prompt for the OpenAI API.
    4. Calls the OpenAI API's chat completions method with the constructed prompt to generate a response.

    Response:
    ---------
    - Success: Returns a JSON response containing the AI-generated message content.
    - Failure: Returns a JSON response with the error message and a 500 status code.

    Note:
    -----
    The 'messages' array must include the conversation history, where the last message is the user's latest input. 
    The 'filenames' is used to fetch additional context for the conversation.

    Example Usage:
    --------------
    ```
    POST /api/chat HTTP/1.1
    Host: <your_api_url>
    Content-Type: application/json

    {
        "messages": [
            {"role": "user", "content": "Hello, AI!"},
            ...
        ],
        "filenames": ["context_file.txt"]
    }
    ```
    """
    if os.getenv("OPENAI_API_KEY") == None:
        print("ERROR: need to set API key", file=sys.stderr)
        return jsonify("Must set API key"), 300
    
    try:
        
        client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
        data = json.loads(request.data.decode("utf-8"))
        print(data, file=sys.stderr)
        messages = data['messages']
        filenames = data['filenames']
        last_message = messages[-1]
        context = await get_context(last_message["content"], filenames=filenames)
        prompt = [
            {
                "role": "system",
                "content": f"""AI assistant is a brand new, powerful, human-like artificial intelligence.
                    The traits of AI include expert knowledge, helpfulness, cleverness, and articulateness.
                    AI is a well-behaved and well-mannered individual.
                    AI is always friendly, kind, and inspiring, and he is eager to provide vivid and thoughtful responses to the user.
                    AI has the sum of all knowledge in their brain, and is able to accurately answer nearly any question about any topic in conversation.
                    AI assistant is a big fan of Pinecone and Vercel.
                    START CONTEXT BLOCK
                    {context}
                    END OF CONTEXT BLOCK
                    AI assistant will take into account any CONTEXT BLOCK that is provided in a conversation.
                    If the context does not provide the answer to question, the AI assistant will say, "I'm sorry, but I don't know the answer to that question".
                    AI assistant will not apologize for previous responses, but instead will indicated new information was gained.
                    AI assistant will not invent anything that is not drawn directly from the context.
                    """,
            },
        ]
        user_messages = [message for message in messages if message['role'] == 'user']
        print("MESSAGES", user_messages, file=sys.stderr)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages= prompt + user_messages
        )
        print("RESPONSE", response.choices[0].message.content, file=sys.stderr)
        return jsonify({
            "response": response.choices[0].message.content,
            "context": context
        }), 200

    except Exception as e:
        print("ERROR", file=sys.stderr)
        return jsonify({"error": str(e)}), 500
@app.route("/api/clear_index", methods = ["POST"])
def clear_index():
    """
    This endpoint handles POST requests for deleting a specific Pinecone index.

    Process:
    --------
    1. Initializes Pinecone using the API key and environment variable.
    2. Retrieves the name of the Pinecone index from the environment variable.
    3. Deletes the specified Pinecone index.

    Response:
    ---------
    - Success: Returns a JSON response confirming successful deletion of the index.
    - Failure: Returns a JSON response with the error message and a 500 status code.

    Note:
    -----
    Ensure that the Pinecone API key and index name are correctly set in the environment variables.

    Example Usage:
    --------------
    ```
    POST /api/clear_index HTTP/1.1
    Host: <your_api_url>
    ```
    """
    try:
        pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))
        delete_response = pinecone.delete_index(name=os.getenv("PINECONE_INDEX"))
        return jsonify("Deleted Index Successfully"), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/generate_embeddings", methods=["POST"])
async def generate_embeddings():
    data = request.json

    if not data or "files" not in data:
        logger.debug("Invalid data format or missing 'files' key")
        return jsonify({"error": "Invalid data format or missing 'files' key"}), 400

    chunk_size = data.get('chunk_size', 1500)
    chunk_overlap = data.get('chunk_overlap', 50)
    method = data.get('method', 'character')  # Default to 'character' if not specified

    try:
        success_files = []
        unsuccessful_files = []

        for file in data['files']:
            response = await upload_and_generate_embedding(
                file,
                os.getenv("PINECONE_INDEX"),
                SeedOptions(chunk_size=chunk_size, chunk_overlap=chunk_overlap,method=method)
                
            )
            if response["success"]:
                success_files.append(response["filename"])
            else:
                unsuccessful_files.append(file)

        return jsonify({"success": True, "successful_uploads": success_files, "unsuccessful_uploads": unsuccessful_files}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
