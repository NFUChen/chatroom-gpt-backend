from __future__ import annotations
import datetime
import uuid
from copy import deepcopy
from typing import Literal
from dataclasses import dataclass

MessageType = Literal["regular", "ai", "notification"]

@dataclass
class ChatMessage:
    message_id: str
    message_type: MessageType
    user_id: int
    user_name: str
    room_id: str
    content: str
    created_at: datetime.datetime
    modified_at: datetime.datetime | None = None

    def to_dict(self) -> dict[str, str]:
        dict_copy = deepcopy(self.__dict__)
        dict_copy["created_at"] = str(dict_copy["created_at"])
        return dict_copy
    
    @classmethod
    def create_chat_message(cls,message_type: str, user_id: str, user_name: str, room_id: str, content: str) -> ChatMessage:
        message_id = str(uuid.uuid4())
        now = str(datetime.datetime.now())
        return ChatMessage(message_id, message_type, user_id, user_name, room_id, content, now, now, )