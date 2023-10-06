from typing import Literal, Any
import traceback
import functools
import os
import datetime
import hashlib
import requests
import ast
import json
from paho.mqtt.publish import single

query_api = f"http://query_manager:5000/query"

def get_current_datetime() -> str:
    _format = "%Y-%m-%d %H:%M:%S.%f"
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime(_format)
    return formatted_datetime


def create_assistant_base_pompt(room_rule: str) -> str:
    return f"""
You are will receive messages in a multi-user Chinese chat context. 
Your primary responsibility is to answer the user's questions based on given contextual information. 
Please strictly adhere to the following guidelines with additional custom room rules in a given room:
    - Only answer the question in "Traditional Chinese", even if given context is mixed with English and Simplified Chinese.
    - Do not invent answers if the context is unclear; politely acknowledge your inability to answer in such cases.
    - Maintain a polite and respectful tone in all interactions with the user.
    - If necessary, provide detailed explanations or examples to ensure clear communication with the user.
    - Provide responses in a clear and concise manner, focusing on presenting factual information. Avoid unnecessary elaboration.
    - When multiple documents or sources are available, prioritize those with higher similarity scores pertain to user's question. This ensures that the responses are more relevant to the question.
    - When faced with duplicate information across documents, typically resulting from initial disinformation, choose the instance with higher similarity scores and the most recent timestamp. 
    - When merging potentially conflicting documents, substitute outdated information with the latest updates, and ensure you offer a detailed explanation when presenting these instances.
    - You are encouraged to extract insights from multiple documents that share the same 'document_id' key while responding to the questions.
    - Do not mention the specific similarity score used in ranking the responses. Keep the responses natural and focused on the content.
    - Mention the source of information especially when news, articles are provided, also attach source url if possible, and provide detailed explanation if needed.
    - Ensure that all responses are accurate and truthful. Avoid speculation or conjecture, and rely on verified information.
    - Respond in a manner that resembles a natural conversation between an AI assistant and a user. 
    - Avoid using technical jargon or overly formal language.
    - Prioritize provided context over chat history when confirming relevant information, especially in cases where no prior information was available on a topic for answering the question.
    - In cases where the you has previously indicated a lack of knowledge, concentrate on the most recent question or message provided by the user to enhance responsiveness and accuracy.
Additional custom room rule:
    {room_rule}
Execute this task while ensuring that your responses are accurate and helpful in chat context scenarios.\n
"""

def create_vector_store_context_prompt(query_results: str) -> str:
    return f'''
You are provided with the following contextual information (query result from the vector database and current timestamp) for answering the question:
Current timestamp: {get_current_datetime()}
Query result:
{query_results}
'''

def create_web_context_prompt(web_content: str) -> str:
    return f'''
You are provided with the following contextual information (content from the web in a form of your thinking process and current timestamp) for answering the question:
Current timestamp: {get_current_datetime()}
Query result:
{web_content}
'''

def create_web_query_prompt(prompt: str, messages: list[dict[str, str]]) -> str:
    return f"""
Building upon the information discussed in the following chat messages:
{messages}
Also making sure you include the source the information in your response.
Please answer the following question: {prompt}

"""

def create_memorization_prompt(prompt: str, lang: Literal["eng", "chi"]) -> str:
    lang_lookup = {
        "eng": "English",
        "chi": "Traditional Chinese"
    }
    if lang not in lang_lookup:
        raise ValueError(f"Invalid target language for prompt improvement, please enter one of the following: {lang_lookup.keys()}, entering {lang}")

    return f'''
Please provide the data you intend to store in long-term memory (i.e., a vector database).
**Guidelines:**
    - Ensure the data is accurate, relevant, and well-structured in {lang_lookup[lang]}.
    - If needed, paraphrase or summarize the content to enhance its quality.
    - Ensure that any modifications made do not alter the original meaning of the content.
    - Adhere to your specified language consistently.
    - If the provided content is an article, please exclude noisy data and preserve only the main body of the article.

You may exclude introductory phrases like "The data to be input into long-term memory is as follows:" and provide the modified prompt below.
Here is the data you are given:
    {prompt}
    '''

def get_error_detail(e: Exception):
    error_name = e.__class__.__name__
    trace_back = traceback.extract_tb(e.__traceback__)
    file_name = trace_back[-1].filename
    line_number = trace_back[-1].lineno
    error_message = str(e)
    return {
        'error_name': error_name,
        'file_name': file_name,
        'line_number': line_number,
        'error_message': error_message,
        "trace_back": str(trace_back)
    }

def concat_messages_till_threshold(messages:list[str],threshold: int):
    final_message = ""
    for message in messages:
        final_message += f"| {message}"
        if len(final_message) >= threshold:
            return final_message

    return final_message

def handle_server_errors(func):
    @functools.wraps(func)
    def decorated(*args, **kwargs):
        try:
            return {
                    "data": func(*args, **kwargs),
                    "error": None,
                    "is_success": True 
            }, 200
        except Exception as error:
            return {
                "data": None,
                "error": get_error_detail(error),
                "is_success": False
            }, 200  # Return JSON response with error message and status code 500
    return decorated

def convert_messages(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    '''
    [
        {"user_id": 1, "content": "how can I help u"}
        {"user_id": 2, "content": "Hi"},
    ]
    -> 
    [
        {"role": "assistant", "content": "how can I help u"}
        {"role": "user", "content": "Hi"},
    ]
    '''

    converted_messages = []
    for message in messages:
        role = "assistant" if message["user_id"] == 1 else "user" # 1 = openAI
        content = message["content"]
        converted_messages.append(
            {"role": role, "content": content}
        )
    return converted_messages


def get_hash(string: str) -> str:
    return hashlib.sha256(string.encode("utf-8")).hexdigest()

def is_duplicate_embedding(text_hash: str) -> str:
    sql = f'''
    SELECT CASE 
    WHEN subquery.count = 1 THEN TRUE 
    ELSE FALSE 
    END 
    AS is_exists
    FROM (
    SELECT COUNT(*) AS "count"
    FROM embeddings
    WHERE text_hash = '{text_hash}'
    ) AS subquery;
    '''
    post_json = {
            "query": sql
    }
    return requests.post(
        query_api, json= post_json
    ).json()["data"].pop()["is_exists"] == 1

def query_ai_user_dict() -> dict[str, str | int]:
    sql = "SELECT * FROM users WHERE user_id = 1"
    post_json = {
            "query": sql
    }
    return requests.post(
        query_api, json= post_json
    ).json()["data"].pop()

def query_all_embeddings() -> list[dict[str, str | list[float]]]:
    sql = "SELECT * FROM embeddings"
    post_json = {
            "query": sql
    }
    embeddings = requests.post(
        query_api, json= post_json
    ).json()["data"]
    for embedding in embeddings:
        embedding["vector"] = ast.literal_eval(embedding["vector"])
    return embeddings

def emit_socket_event(socket_event: str, data: Any) -> None:
    payload = {
            "data": data
    }
    single(socket_event, json.dumps(payload), 1, hostname= "mosquitto")