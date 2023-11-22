from flask import Flask, request, jsonify
from openai import OpenAI
import pinecone
import scipdf
import os
from langchain.document_loaders import PyPDFLoader

app = Flask(__name__)

@app.route("/api/chat", methods = ["POST"])
def chat():
    try:
        client = OpenAI(apiKey = os.getenv("OPENAI_API_KEY"))
        data = request.json
        messages = data['messages']
        
        prompt = [
            {
                "role": "system",
                "content": ("AI assistant is a brand new, powerful, human-like artificial intelligence. "
                            "The traits of AI include expert knowledge, helpfulness, cleverness, and articulateness. "
                            "AI is a well-behaved and well-mannered individual. "
                            "AI is always friendly, kind, and inspiring, and he is eager to provide vivid and thoughtful responses to the user. "
                            "AI has the sum of all knowledge in their brain, and is able to accurately answer nearly any question about any topic in conversation.")
            },
        ]

        # Filter user messages
        user_messages = [message for message in messages if message['role'] == 'user']
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt + user_messages
        )

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/clearIndex", methods = ["POST"])
def clear_index():
    try:
        pinecone.init(api_key=os.getenv("PINECONE_API_KEY"),
                environment=os.getenv("PINECONE_ENVIRONMENT"))
        index = pinecone.index(os.getenv("PINECONE_INDEX"))
        namespace = os.getenv("PINECONE_NAMESPACE") if os.getenv("PINECONE_NAMESPACE") else ''
        delete_response = index.delete(deleteAll = True, namespace=namespace)
        return jsonify(delete_response)
    except Exception as e:
        # Handle exceptions and return an error message
        return jsonify({"error": str(e)}), 500

@app.route("/api/processDocs", methods = ["POST"])
def process_docs():
    try:
        if 'pdf' not in request.files:
            return 'No PDF file provided', 400
        pdf_file = request.files['pdf']
        pdf_storage_dir = os.path.join(os.path.dirname(__file__), './tmp/pdf_storage')
        os.makedirs(pdf_storage_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_storage_dir, pdf_file.filename)
        pdf_file.save(pdf_path)

        loader = PyPDFLoader(pdf_path)
        pages = loader.load_and_split()
        os.remove(pdf_path)
        doc_strings = [{"content": page.page_content, "metadata": {"page_number": page.metadata['page']}} for page in pages]
        return jsonify(doc_strings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
