import openai
import os
from typing import List
import json

from config import config

openai.api_key = config.openai_api_key

def get_openai_embedding_question(question: str):
    """
    Get the embedding for single question

    Parameters:
        texts str: list of text for which embeddings needs to generate
    """
    try:
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=question
        )

        return response["data"][0]["embedding"]
    except Exception as e:
        print(f"Error occured while generating emveddings for question [{question}]\n{e}")
    
    return []

def get_openai_embeddings(texts: List[str]):
    """
    Get the embedding for list of text

    Parameters:
        texts List[str]: list of text for which embeddings needs to generate
    """
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=texts
    )

    embeddings = [x["embedding"] for x in response["data"]]
    tokens = response["usage"]["total_tokens"]
    return embeddings, tokens

def get_answer_from_context(question: str, context: str, stream: bool):
    """
    Get answer from context using GPT

    Parameters:
        question str: question asked by user
        context str: Information from which answer for question needs to extracted
        last_message dict: last question and answer pair
        stream boolean: stream the response
    """
    try:
        start_message = f"{open(os.path.join(os.getcwd(),'prompts', config.context_answer_prompt_filename)).read()}"
        messages = [
            {"role": "system", "content": f"{start_message}"},
            {"role": "user", "content": f"Make sure not to provide answer if it does not exists in provided information.\n\nInformation: {context}\n\nQuestion: {question}. Explain in detail.\nAnswer:"}
        ]
        response = openai.ChatCompletion.create(
            model=config.gpt_model,
            messages=messages,
            n = 1,
            stream = stream
        )

        return response
    except Exception as e:
        print(f"Error occured from gpt:\n{e}")

def op_to_json(op: str) -> dict:
    """
    JSON output Parser

    Parameters:
        op str: output from openai, which contains json that needs to parse

    Returns:
        parsed_op dict: json extracted from output
    """

    try:
        parsed_op = json.loads(op)
    except:
        op = op[op.find("{"):]
        op = op[:op.rindex("}")]
        parsed_op = json.loads(op)
        
    return parsed_op

def merge_two_questions(question_1: str, question_2: str) -> str:
    """
    Merge two questions in meaningful way.

    Parameters:
        question_1 str: question 1
        question_2 str: question 2
    
    Returns:
        merge_question str: merger of 2 questions
    """

    prompt = open(os.path.join(os.getcwd(), 'prompts', config.question_merge_prompt_filename)).read()
    prompt = prompt.replace("question_1", question_1)
    prompt = prompt.replace("question_2", question_2)

    response = openai.ChatCompletion.create(
        model=config.gpt_model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        n=1,
        max_tokens=258
    )

    op = response["choices"][0]["message"]["content"]
    try:
        op = op_to_json(op)
    except:
        op = {
            "new_question": question_2
        }

    merge_question = op.get("new_question","") or question_2
    return merge_question
