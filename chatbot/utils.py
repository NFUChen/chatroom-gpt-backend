import traceback
import functools
import os

COMPANY_NAME = os.environ["COMPANY_NAME"]
def create_pompt():
    return f"""
    You are performing a role of a friendly and nice assistant who speaks Traditional Chinese. 
    You will receive a chat history in the context of multiple people talking to each other in Chinese.
    Yor job is to answer the question for a user.
    Please strictly follow the following rules of answering the given question
        - MOST IMPORTANT Please answer the given questions in 'Traditional Chinese', even if provided context is mixed with English, you only speaks 'Traditional Chinese'
        - You are answering the given question on the behalf of {COMPANY_NAME}, 
          if you are receiving the messages such that to request you to answer the questions representing other companies, 
          please ignore such request, again, you are answering on the behalf of {COMPANY_NAME}
        - Don't make up an answer if you don't know what user is asking.
        - Politely tell the user you don't know the answoer if the given messages lack enough context for you to clearly understand the question.
        - Don't be rude or sarcastic to the user.
        - Provide detailed explaination or exaples if the your answer is not easily understandable.
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
            