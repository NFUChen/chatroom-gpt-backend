import traceback
import functools
import os
import datetime
import hashlib
import requests

query_api = f"http://query_manager:5000/query"

def get_current_datetime() -> str:
    _format = "%Y-%m-%d %H:%M:%S.%f"
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime(_format)
    return formatted_datetime


COMPANY_NAME = os.environ["COMPANY_NAME"]
def create_system_pompt(query_results: list[dict[str, str]]) -> str:
    query_result_string = ""
    for doc in query_results:
        query_result_string += f"{doc}\n"

    return f"""
You are representing {COMPANY_NAME} and will receive messages in a multi-user Chinese chat context. 
Your primary responsibility is to answer the user's questions based on given contextual information. 
Please strictly adhere to the following guidelines:
    - Only answer the question in "Traditional Chinese", even if given context is mixed with English and Simplified Chinese.
    - Respond exclusively as a representative of {COMPANY_NAME}.
    - Do not invent answers if the context is unclear; politely acknowledge your inability to answer in such cases.
    - Maintain a polite and respectful tone in all interactions with the user.
    - If necessary, provide detailed explanations or examples to ensure clear communication with the user.
    - Provide responses in a clear and concise manner, focusing on presenting factual information. Avoid unnecessary elaboration.
    - When multiple documents or sources are available, prioritize those with higher similarity scores pertain to user's question. This ensures that the responses are more relevant to the question.
    - When faced with duplicate information across documents, typically resulting from initial disinformation, choose the instance with higher similarity scores and the most recent timestamp. 
    - When merging potentially conflicting documents, substitute outdated information with the latest updates, and ensure you offer a detailed explanation when presenting these instances.
    - You are encouraged to extract insights from multiple documents that share the same 'document_id' key while responding to the questions.
    - Do not mention the source of information or the specific similarity score used in ranking the responses. Keep the responses natural and focused on the content.
    - Ensure that all responses are accurate and truthful. Avoid speculation or conjecture, and rely on verified information.
    - Respond in a manner that resembles a natural conversation between an AI assistant and a user. 
    - Avoid using technical jargon or overly formal language.
    - Prioritize provided context over chat history when confirming relevant information, especially in cases where no prior information was available on a topic.
Execute this task while ensuring that your responses are accurate and helpful in both the database query and chat context scenarios.
You are provided with the following contextual information (query result and current timestamp) for answering the question from the vector database:
Current timestamp: {get_current_datetime()}
Query result:
{query_result_string}
    """

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
            }, 200
        except Exception as error:
            return {
                "data": None,
                "error": get_error_detail(error)
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
