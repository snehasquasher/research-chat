from flask import Flask, request, jsonify
import json
import logging
import os
from openai import Client

from index import app

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Load OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    logging.error("OPENAI_API_KEY is not set.")
    exit(1)

# Initialize OpenAI client
client = Client(api_key=api_key)

@app.route('/api/evaluate-answers', methods=['POST'])
def evaluate_answers():
    logging.debug('comes here to evaluare')
    data = request.json
    context = data['context']
    answer = data['answer']
    question = data['question']

    # Choose a specific OpenAI model for evaluation
    model_name = "text-davinci-003"  # Replace with your desired model

    # Evaluate using OpenAI model
    faithfulness_score = evaluate_faithfulness(client, model_name, context, answer)
    context_relevance_score = evaluate_context_relevance(client, model_name, context, answer)
    answer_relevance_score = evaluate_answer_relevance(client, model_name, question, answer)

    return jsonify({
        'faithfulness_score': faithfulness_score,
        'context_relevance_score': context_relevance_score,
        'answer_relevance_score': answer_relevance_score
    })

def evaluate_faithfulness(client, model_name, context, answer):
    prompt = f"How faithful is this answer to the provided context? Rate on a scale of 0 to 1.\nContext: {context}\nAnswer: {answer}"
    return get_evaluation_score(client, model_name, prompt)

def evaluate_context_relevance(client, model_name, context, answer):
    prompt = f"How relevant is this answer to the provided context? Rate on a scale of 0 to 1.\nContext: {context}\nAnswer: {answer}"
    return get_evaluation_score(client, model_name, prompt)

def evaluate_answer_relevance(client, model_name, question, answer):
    prompt = f"How relevant is this answer to the following question? Rate on a scale of 0 to 1.\nQuestion: {question}\nAnswer: {answer}"
    return get_evaluation_score(client, model_name, prompt)

def get_evaluation_score(client, model_name, prompt):
    try:
        response = client.completions.create(model=model_name, prompt=prompt, max_tokens=60)
        score_text = response.choices[0].text.strip()
        score = float(score_text)
        return max(0, min(score, 1))  # Ensure score is within 0 to 1
    except Exception as e:
        logging.error(f"Error in getting evaluation score: {e}")
        return 0  # Return 0 or some default value in case of an error
