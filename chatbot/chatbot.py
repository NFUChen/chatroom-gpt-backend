from typing import Literal, Iterable
import openai
from openai_utils import num_tokens_from_messages
from datetime import datetime, timedelta
import traceback
import uuid
import dataclasses
@dataclasses.dataclass
class ChatBotResponse:
    model_name: str
    response_id: str
    datetime: str
    messages: list[dict[str, str]]
    answer: str
    prompt_tokens: int
    response_tokens: int
    api_key: str

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
            "doc": create_error_document(exception)
        }
    
    # response = requests.post("http://producer:8080/produce", json= post_json)
    # return response.json()

Role =  Literal["system", "user", "assistant"]

class ChatBot:
    def __init__(self, system_prompt: str,chat_messages: list[dict[str, str]], is_token_lazy_eval: bool = True) -> None:
        self.messages = [self._create_system_prompt(system_prompt), *chat_messages]
        
        self.source_token_count = (
            len("|".join([msg_dict["content"] for msg_dict in self.messages])) 
            if is_token_lazy_eval else num_tokens_from_messages(self.messages)
        )
        self.reponse_message_token_count = 0 
        self.current_message = ""
        self.MAX_TOKENS_ACCEPTED = 15500

    @property
    def model(self) -> str | None:
        if self.source_token_count < (3500 + 1000):
            return "gpt-3.5-turbo" # 4k
        if self.source_token_count < self.MAX_TOKENS_ACCEPTED:
            return "gpt-3.5-turbo-16k"
        return

    def _create_system_prompt(self, system_prompt: str) -> list[dict[str, str]]:
        return {"role": "system", "content": system_prompt}        
        
    def _update_current_message(self, msg: str) -> None:
        self.current_message += msg

    def answer(self) -> Iterable[str]:
        chosen_model = self.model
        if chosen_model is None:
            raise ValueError(f"Token exceed max context length: {self.MAX_TOKENS_ACCEPTED}, getting {self.source_token_count}")


        print(f"Choosing {chosen_model} to answer the question.")
        try:
            generator = openai.ChatCompletion.create(
                model= chosen_model,
                stream= True,
                messages= self.messages
            )
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
            print(error)
        finally:
            reponse_message_token_count = len(self.current_message)
            self.bot_response = ChatBotResponse(
                model_name= chosen_model,
                response_id= str(uuid.uuid4()),
                datetime= get_taipei_time(),
                messages= self.messages,
                answer= self.current_message,
                prompt_tokens= self.source_token_count,
                response_tokens= reponse_message_token_count,
                api_key= openai.api_key
            )