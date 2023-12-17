from langchain.chat_models import ChatOpenAI
from langchain.evaluation.criteria import CriteriaEvalChain
import asyncio
import os 

api_key = os.getenv('OPENAI_API_KEY')
# Define the language model and criteria for evaluation
llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=api_key)
criteria = {"conciseness": "Is the text concise and avoids unnecessary words?"}

# Create the evaluator
evaluator = CriteriaEvalChain.from_llm(llm=llm, criteria=criteria,api_key=api_key)

# Hardcoded test data
test_input = "Explain the concept of gravity"
test_answer = "Gravityts center."
#print(test_input)
# Evaluate conciseness
try:
    scores = evaluator.evaluate_strings(prediction=test_answer, input=test_input,api_key=api_key)
    #print("Evaluation scores:", scores)
except Exception as error:
    print("Error during evaluation:", error)

