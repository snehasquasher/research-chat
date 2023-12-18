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
        "Please rate the faithfulness of the answer in terms of how accurately and faithfully it reflects the specific context retrieved, on a scale from 0 to 1, where 0 is completely unfaithful and 1 is completely faithful.\n"
        "Example 1:\nContext: Retrieval-augmented generation reduces hallucinations significantly.\nAnswer: Retrieval-augmented generation was found to be helpful in reducing model hallucination.\nRating: 0.9\n"
        "Example 2:\nContext: Recent studies show a correlation between sleep patterns and learning efficiency.\nAnswer: There is evidence suggesting that diet affects learning abilities.\nRating: 0.5\n"
        "Example 3:\nContext: Advancements in AI have led to more efficient natural language processing algorithms.\nAnswer: Modern AI developments have mainly focused on improving computer vision.\nRating: 0\n"
        "Example 4:\nContext: The Kepler telescope has significantly expanded our knowledge of exoplanets.\nAnswer: The Kepler mission has been pivotal in discovering new exoplanets and understanding their characteristics.\nRating: 0.6\n"
        "Example 5:\nContext: Blockchain technology can enhance cybersecurity.\nAnswer: Blockchain is primarily used for cryptocurrency transactions.\nRating: 0.5\n"
        "Example 6:\nContext: Studies indicate that regular exercise contributes to improved mental health.\nAnswer: Exercise has been shown to have positive effects on mental well-being and stress reduction.\nRating: 0.8\n"
        f"Your Turn:\nContext: {context}\nAnswer: {answer}\nRating:"
    )
    return get_evaluation_score(client, model_name, prompt)



def evaluate_context_relevance(client, model_name, question, context):
    prompt = (
        "Please rate the context relevance to the question asked on a scale from 0 to 1, where 0 is not relevant and 1 is highly relevant. Higher values indicate better relevancy.\n"
        "Example 1:\nQuestion: What are the environmental impacts of deforestation?\nContext: The study focuses on the loss of habitat and biodiversity due to deforestation.\nRating: 0.9\n"
        "Example 2:\nQuestion: How does meditation affect mental health?\nContext: Research on physical exercise and mental wellness.\nRating: 0.3\n"
        "Example 3:\nQuestion: What advancements have been made in electric vehicle technology?\nContext: Overview of renewable energy sources and their applications.\nRating: 0.6\n"
        "Example 4:\nQuestion: What is the significance of the Hubble Space Telescope's discoveries?\nContext: Detailed review of major astronomical discoveries made by the Hubble Space Telescope.\nRating: 1\n"
        "Example 5:\nQuestion: What are the latest treatments for type 2 diabetes?\nContext: General information on lifestyle diseases, including diabetes and heart diseases.\nRating: 0.4\n"
        "Example 6:\nQuestion: What role do microorganisms play in ecosystems?\nContext: The role of microorganisms in soil nutrient cycling and ecosystem stability.\nRating: 0.9\n"
        f"Your Turn:\nQuestion: {question}\nContext: {context}\nRating:"
    )
    return get_evaluation_score(client, model_name, prompt)




def evaluate_answer_relevance(client, model_name, question, answer):
    prompt = (
        "Please rate the relevance of the response to the specific question on a scale from 0 to 1, where 0 is not relevant at all and 1 is highly relevant. Provide a score based on how well the answer addresses the question asked.\n"
        "Example 1:\nQuestion: What are the health benefits of regular exercise?\nAnswer: Regular exercise helps in maintaining healthy body weight and improving cardiovascular health.\nRating: 0.9\n"
        "Example 2:\nQuestion: What is blockchain technology?\nAnswer: Blockchain technology involves advanced computing techniques and cryptography.\nRating: 0.7\n"
        "Example 3:\nQuestion: How does photosynthesis work?\nAnswer: Photosynthesis is a biological process in plants involving sunlight, carbon dioxide, and water.\nRating: 0.9\n"
        "Example 4:\nQuestion: Who wrote 'Pride and Prejudice'?\nAnswer: 'Pride and Prejudice' is a novel by Jane Austen focusing on themes of marriage, morality, and manners.\nRating: 1\n"
        "Example 5:\nQuestion: What causes rain?\nAnswer: Rain occurs due to climate change and global warming.\nRating: 0.3\n"
        "Example 6:\nQuestion: Can you name a famous physicist?\nAnswer: Albert Einstein is known for his theory of relativity.\nRating: 0.8\n"
        "Example 7:\nQuestion: What is the capital of France?\nAnswer: Paris is the capital and most populous city of France.\nRating: 1\n"
        "Example 8:\nQuestion: What was the first question asked?\nAnswer: The first question was about the health benefits of regular exercise.\nRating: 0.9\n"
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
