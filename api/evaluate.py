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
    logging.debug('Request received for answer evaluation')
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
    prompt = (
        "Please rate the faithfulness of the answers to their contexts on a scale from 0 to 1, where 0 is completely unfaithful and 1 is completely faithful.\n"
        "Example 1:\nContext: The sky is blue.\nAnswer: The sky is blue.\nRating: 1\n"
        "Example 2:\nContext: The sky is blue.\nAnswer: The sky is often cloudy.\nRating: 0.5\n"
        "Example 3:\nContext: Apples are usually red.\nAnswer: Oranges are orange.\nRating: 0\n"
        f"Your Turn:\nContext: {context}\nAnswer: {answer}\nRating:"
    )
    return get_evaluation_score(client, model_name, prompt)

def evaluate_context_relevance(client, model_name, context, answer):
    prompt = (
        "Please rate the context relevance of the answers on a scale from 0 to 1, where 0 is not relevant and 1 is highly relevant.\n"
        "Example 1:\nContext: History of the Roman Empire.\nAnswer: Julius Caesar was a Roman ruler.\nRating: 1\n"
        "Example 2:\nContext: History of the Roman Empire.\nAnswer: The Roman Empire was in Africa.\nRating: 0.5\n"
        "Example 3:\nContext: Computer Programming Basics.\nAnswer: Apples grow on trees.\nRating: 0\n"
        f"Your Turn:\nContext: {context}\nAnswer: {answer}\nRating:"
    )
    return get_evaluation_score(client, model_name, prompt)

def evaluate_answer_relevance(client, model_name, question, answer):
    prompt = (
        "Please rate the relevance of the answers to the questions on a scale from 0 to 1, where 0 is not relevant and 1 is highly relevant.\n"
        "Example 1:\nQuestion: What is the capital of France?\nAnswer: Paris is the capital of France.\nRating: 1\n"
        "Example 2:\nQuestion: What is the capital of France?\nAnswer: France is in Europe.\nRating: 0.5\n"
        "Example 3:\nQuestion: What is the capital of France?\nAnswer: Elephants are the largest land animals.\nRating: 0\n"
        f"Your Turn:\nQuestion: {question}\nAnswer: {answer}\nRating:"
    )
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
