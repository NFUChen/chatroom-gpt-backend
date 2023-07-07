from typing import Literal, Iterable
import openai
from openai_utils import num_tokens_from_messages
from datetime import datetime, timedelta
import traceback
import requests
import dataclasses

@dataclasses.dataclass
class ChatBotResponse:
    datetime: str
    messages: list[dict[str, str]]
    answer: str
    prompt_tokens: int
    response_tokens: int

    def to_dict(self) -> dict[str, str]:
        return self.__dict__

def get_taipei_time() -> str:
    return str(datetime.now() + timedelta(hours=8))

def log_error(exception: Exception) -> None:
    def create_error_document(exception: Exception) -> dict[str, str]:
        error_document = {
            'time': get_taipei_time(),
            'type': type(exception).__name__,
            'message': str(exception),
            'traceback': traceback.format_exc()
        }
        return error_document
    
    post_json = {
            "queue": "error",
            "db": "error",
            "collection": "chatbot",
            "doc": {
               create_error_document(exception)
            }
        }
    
    response = requests.post("http://producer:8080/produce", json= post_json)
    return response.json()

def log_response(response: ChatBotResponse) -> None:
    post_json = {
            "queue": "response",
            "db": "chatbot",
            "collection": "chatbot",
            "doc": {
                response.to_dict()
            }
        }
    
    response = requests.post("http://producer:8080/produce", json= post_json)
    return response.json()

Role =  Literal["system", "user", "assistant"]

class ChatBot:
    PROMPT = f"""
    You are performing a role of a friendly and nice assistant. 
    You will receive a chat history in the context of multiple people talking to each other.
    Yor job is to answer the question for a user.
    Please strictly follow the following rules of answering the given question
        - Don't make up an answer if you don't know what user is asking.
        - Politely states tell the user you don't know the answoer 
          if the given messages lack enough context for you to clearly understand the question.
        - Don't be rude, sarcastic to the user.
        - Provide detailed explaination or exaples if the your answer is not easily understandable.
    """
    def __init__(self, api_key: str, chat_messages: list[dict[str, str]]) -> None:
        self.messages = [self._get_system_prompt(), *chat_messages]
        print(self.messages)
        openai.api_key = api_key
        self.source_token_count = num_tokens_from_messages(self.messages)
        self.current_message = ""
        self.bot_reponse: ChatBotResponse | None = None

    @property
    def model(self) -> str:
        if self.source_token_count < 3500:
            return "gpt-3.5-turbo" # 4k
        return "gpt-3.5-turbo-16k"

    def _get_system_prompt(self) -> list[dict[str, str]]:
        return {"role": "system", "content": self.PROMPT}
        
        
    def _update_current_message(self, msg: str) -> None:
        self.current_message += msg

    def _log_response(self, response: list[dict[str, str]]) -> None:
        ...

    def answer(self) -> Iterable[str]:
        chosen_model = self.model
        try:
            generator = openai.ChatCompletion.create(
                model= chosen_model,
                stream= True,
                messages= self.messages
            )
            self._update_current_message("assistant:")
            yield self.current_message
            for response in generator:
                choice = response['choices'][0]["delta"]
                if "content" in choice:
                    content = choice["content"]
                    self._update_current_message(content)
                    yield self.current_message
            self._update_current_message("\n")

            yield self.current_message
        except Exception as error:
            log_error(error)
        finally:
            reponse_message_token_count = num_tokens_from_messages([
                {
                "role": "assistant", "content": self.current_message
            }
            ])
            self.bot_reponse = ChatBotResponse(
                datetime= get_taipei_time(),
                messages= self.messages,
                answer= self.current_message,
                prompt_tokens= self.source_token_count,
                response_tokens= reponse_message_token_count,
            )
    
            
            

if __name__ == "__main__":
    messages = [
        {
            "role": "user",
            "content": "I don't kown how to learn python."
        },
        {
            "role": "user",
            "content": "How to learn python"
        }
    ]
    bot = ChatBot("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", messages)
    for msg in bot.answer():
        print(msg)
    print(bot.bot_reponse)