from langchain.chains import LLMChain
from langchain.schema.prompt_template import BasePromptTemplate
from langchain.evaluation.criteria import CriteriaEvalChain  # Adjusted path based on your package structure

from index import app

from flask import Flask, request, jsonify
import json

from langchain.chat_models import ChatOpenAI
import logging 

logging.basicConfig(
    level=logging.DEBUG,  # Set the desired log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file
        logging.StreamHandler()  # Log to the console
    ]
)
import os 

api_key = os.getenv('OPENAI_API_KEY')
# Define the llm and criteria for evaluation
llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=api_key)
criteria = {"conciseness": "Is the text concise and avoids unnecessary words?"}

# Create the evaluator
evaluator = CriteriaEvalChain.from_llm(
    llm=llm,
    criteria=criteria,
)

@app.route("/api/evaluate", methods=["POST"])
def evaluate_conciseness():
    # Get input and answer from the request body
    try:
        logging.debug("comes ehre to evaluate")
        data = json.loads(request.data)
        input = data["input"]
        answer = data["answer"]
      
    except KeyError:
        return jsonify({"error": "Missing required fields in request body"}), 400

    # Evaluate conciseness
    try:
        scores = evaluator.evaluate_strings(input=input, prediction=answer)
        logging.debug(f"Scores: {scores}")
        return jsonify(scores)  # Return the calculated scores
    except Exception as error:
        logging.error(f"Error during evaluation: {error}, Type: {type(error)}, Args: {error.args}")
        return jsonify({"error": str(error)}), 500


