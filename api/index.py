from flask import Flask, request, jsonify
from openai import OpenAI
import pinecone
import os
from process_docs import upload_and_generate_embedding
from dotenv import load_dotenv
from hashlib import md5
from utils.context import get_context
import sys

load_dotenv()
app = Flask(__name__)

@app.route("/api/chat", methods = ["POST"])
async def chat():
    try:
        client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
        data = request.json
        messages = data['messages']
        file_name = data['file_name']
        last_message = messages[-1]
        context = await get_context(last_message["content"], file_name=file_name)
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
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages= prompt + user_messages
        )
        return jsonify(response.choices[0].message.content)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/clear_index", methods = ["POST"])
def clear_index():
    try:
        pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))
        index = pinecone.Index(index_name = os.getenv("PINECONE_INDEX"))
        delete_response = pinecone.delete_index(name=os.getenv("PINECONE_INDEX"))
        return jsonify("Deleted Index Successfully"), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate_embeddings", methods = ["POST"])
async def generate_embeddings():
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
    print("FILES: ", request.files, file=sys.stderr)
    return redirect("/chat")