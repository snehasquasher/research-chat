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
import requests

load_dotenv()
app = Flask(__name__)

@app.route("/api/chat", methods = ["POST"])
async def chat():
    """
    This endpoint handles POST requests for generating responses using the OpenAI API based on user messages.

    Request Body:
    -------------
    - messages (array): An array of message objects. Each object should have 'role' (user/system) and 'content'.
    - file_name (string): A file name that is used for fetching context relevant to the conversation.

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
    The 'file_name' is used to fetch additional context for the conversation.

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
        "file_name": "context_file.txt"
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
        file_name = data['file_name']
        last_message = messages[-1]
        # commented out because didn't seem to be used?
        #context = await get_context(last_message["content"], file_name=file_name)
        prompt = [
            {
                "role": "system",
                "content": """AI assistant is a brand new, powerful, human-like artificial intelligence.
                    The traits of AI include expert knowledge, helpfulness, cleverness, and articulateness.
                    AI is a well-behaved and well-mannered individual.
                    AI is always friendly, kind, and inspiring, and he is eager to provide vivid and thoughtful responses to the user.
                    AI has the sum of all knowledge in their brain, and is able to accurately answer nearly any question about any topic in conversation.
                    AI assistant is a big fan of Pinecone and Vercel.
                    START CONTEXT BLOCK
                    ${context}
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
        return jsonify(response.choices[0].message.content), 200

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
        index = pinecone.Index(index_name = os.getenv("PINECONE_INDEX"))
        delete_response = pinecone.delete_index(name=os.getenv("PINECONE_INDEX"))
        return jsonify("Deleted Index Successfully"), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate_embeddings", methods = ["POST"])
async def generate_embeddings():
    """
    This endpoint processes a POST request to generate embeddings from a provided PDF file.

    Request Body:
    -------------
    The request must include a 'pdf' field in the form-data, containing the PDF file from which embeddings will be generated.

    Process:
    --------
    1. The function checks if a 'pdf' file is included in the request. If not, it returns a 400 status code with an error message.
    2. If a PDF file is present, it calls the `upload_and_generate_embedding` function, passing the PDF file and an environment variable "PINECONE_INDEX".
    3. The `upload_and_generate_embedding` function is responsible for handling the PDF file, generating embeddings, and potentially interacting with the Pinecone service or similar.

    Response:
    ---------
    - Success: Returns a JSON response containing the generated embeddings.
    - Failure: If any exception occurs, the function returns a JSON response with the error message and a 500 status code.

    Note:
    -----
    Ensure that the 'pdf' file is provided in the correct format and that the "PINECONE_INDEX" environment variable is properly set for the function to execute successfully.
    
    Example Usage:
    --------------
    curl -X POST -F 'pdf=@path_to_pdf_file.pdf' http://<your_api_url>/api/generate_embeddings

    """
    try:
        if 'pdf' not in request.files:
            return 'No PDF file provided', 400
        pdf_file = request.files['pdf']
        response = await upload_and_generate_embedding(pdf_file, os.getenv("PINECONE_INDEX"))
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/uploadFiles", methods = ['POST'])
def upload_papers():
    print("FILES: ", request.files, len(request.files), file=sys.stderr)
    
    # save PDFs to user-uploads folder
    docID = 1
    for filename, file in request.files.items():
        name = request.files[filename].name
        print("file ", str(docID), name, file=sys.stderr)
        file.save('user-uploads/' + str(docID) + '.pdf')
        docID += 1
    
    # return total number of PDFs
    return jsonify(str(docID -1)), 200

@app.route("/api/chatHelper", methods = ["POST"])
def chat_helper():
    if request.data == None:
        return jsonify("empty message"), 300
    else:
        files = os.listdir('user-uploads')
        if len(files) == 0:
            return jsonify("no uploaded user files"), 400
        
        # for now, just do the first file
        data = {}
        data['messages'] = [{"role": "user", "content": str(request.data)}]
        data['filename'] = files[0]
        json_data = json.dumps(data)
        return requests.post(request.url_root + '/api/chat', data=json_data)