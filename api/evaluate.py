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
        "Please rate the faithfulness of the answer in terms of how accurately and faithfully it reflects the specific context retrieved, on a scale from 0 to 0.9, where 0 is completely unfaithful and 1 is completely faithful.\n"
        "Example 1:\nContext: Retrieval-augmented generation reduces hallucinations significantly.\nAnswer: Retrieval-augmented generation was found to be helpful in reducing model hallucination.\nRating: 0.9\n"
        "Example 2:\nContext: Recent studies show a correlation between sleep patterns and learning efficiency.\nAnswer: There is evidence suggesting that diet affects learning abilities.\nRating: 0.5\n"
        "Example 3:\nContext: Advancements in AI have led to more efficient natural language processing algorithms.\nAnswer: Modern AI developments have mainly focused on improving computer vision.\nRating: 0\n"
        "Example 4:\nContext: The Kepler telescope has significantly expanded our knowledge of exoplanets.\nAnswer: The Kepler mission has been pivotal in discovering new exoplanets and understanding their characteristics.\nRating: 0.6\n"
        "Example 5:\nContext: Blockchain technology can enhance cybersecurity.\nAnswer: Blockchain is primarily used for cryptocurrency transactions.\nRating: 0.5\n"
        "Example 6:\nContext: Studies indicate that regular exercise contributes to improved mental health.\nAnswer: Exercise has been shown to have positive effects on mental well-being and stress reduction.\nRating: 0.8\n"
        f"Your Turn:\nContext: {context}\nAnswer: {answer}\nRating:"
    )
    return get_evaluation_score(client, model_name, prompt)



def evaluate_context_relevance(client, model_name, context, answer):
    prompt = (
        "Please rate the context relevance of the response to the research paper based on the given question on a scale from 0 to 1, where 0 is not relevant and 0.9 is highly relevant. If answer is perfect than give it a 1. Higher values indicate better relevancy.\n"
        "Example 1:\nQuestion: How do renewable energy policies impact carbon emissions?\nContext: Analysis of renewable energy policies.\nAnswer: The response discusses the impact of these policies on reducing carbon emissions.\nRating: 0.8\n"
        "Example 2:\nQuestion: What are the key factors in cognitive development during childhood?\nContext: Research on cognitive development in children.\nAnswer: The response talks about general educational methods, not specific cognitive development factors.\nRating: 0.5\n"
        "Example 3:\nQuestion: What are the latest findings on gravitational waves?\nContext: Study on gravitational waves.\nAnswer: The response discusses the history of astronomy, not recent findings on gravitational waves.\nRating: 0\n"
        "Example 4:\nQuestion: What role does diet play in managing diabetes?\nContext: Research on diet and diabetes management.\nAnswer: The response accurately discusses how diet affects blood sugar control in diabetic patients.\nRating: 0.9\n"
        "Example 5:\nQuestion: What are the implications of blockchain in finance beyond cryptocurrencies?\nContext: Blockchain technology in financial applications.\nAnswer: The response mainly focuses on blockchain for cryptocurrencies, not other financial applications.\nRating: 0.5\n"
        "Example 6:\nQuestion: Can regular physical activity improve mental health?\nContext: Studies on exercise and mental health.\nAnswer: The response details how regular exercise contributes to better mental health and stress reduction.\nRating: 1\n"
        f"Your Turn:\nQuestion: {context}\nAnswer: {answer}\nRating:"
    )
    return get_evaluation_score(client, model_name, prompt)


def evaluate_answer_relevance(client, model_name, question, answer):
    prompt = (
        "Please rate the relevance of the response to specific questions about the research paper on a scale from 0 to 1, where 0 is not relevant and 1 is highly relevant.\n"
        "Example 1:\nQuestion: What are the novel contributions of the paper?\nAnswer: The response accurately outlines the unique contributions and how they advance the field.\nRating: 1\n"
        "Example 2:\nQuestion: How does the paper support its hypotheses?\nAnswer: The response vaguely refers to the methodologies used but lacks specifics.\nRating: 0.5\n"
        "Example 3:\nQuestion: What implications does the research have for future studies?\nAnswer: The response diverts to a different topic unrelated to future implications.\nRating: 0\n"
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
