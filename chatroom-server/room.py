from __future__ import annotations
from typing import Any
from copy import deepcopy
from enum import Enum
from chat_message import ChatMessage
import uuid
from chat_room_database_manager import chat_room_db_manager

class RoomType(Enum):
    PUBLIC = "public"
    PRIVATE = "private"





class Room:
    MAX_MESSAGE_LENGTH = 50
    DEFAULT_ROOM_RULE = "Please enter your custom instruction."
    def __init__(self, 
                 room_id: str, 
                 room_name: str, 
                 owner_id: int,
                 room_rule: str,
                 is_deleted: bool = 0,
                 room_type: str = RoomType.PUBLIC.value
                 ) -> None:
        self.room_id = room_id
        self.room_name = room_name
        self.owner_id = owner_id
        self.room_rule = room_rule
        self.room_type = room_type
        self.user_ids: list[str] = []
        self.messages = self._get_empty_messages()
        self.is_deleted = True if is_deleted else False
        self.is_locked = False
        self.cached_prompt_message = None
        
    @property
    def number_of_people(self) -> int:
        return len(self.user_ids)

    def get_room_members(self) -> list[dict[str, int | str]]:
        members = []
        for user in self.user_ids:
            user_id, user_name = user.split("-")
            members.append({
                "user_id": int(user_id),
                "user_name": user_name,
            })
        return members

    def _get_empty_messages(self) -> dict[str, list[ChatMessage]]:
        return {
            "regular": [],
            "ai": [],
        }
    
    def add_cached_prompt_message(self, message: ChatMessage) -> None:
        self.cached_prompt_message = message
    
    def remove_cacached_message(self,) -> None:
        self.cached_prompt_message = None
    
    def lock_room(self) -> None:
        self.is_locked = True
    
    def unlock_room(self) -> None:
        self.is_locked = False

    def get_socket_event(self, message_type: str) -> str:
        return f"{message_type}/{self.room_id}"

    def set_messages(self, messages: dict[str, list[ChatMessage]]) -> None:
        self.messages = messages

    def get_ai_messages(self, last_n: int) -> list[ChatMessage]:
        return self.messages["ai"][-last_n:]
            
    def user_join_room(self, user_id: str) -> None:
        if user_id in self.user_ids:
            return
        
        self.user_ids.append(user_id)

    def user_leave_room(self, user_id: str) -> None:
        if user_id not in self.user_ids:
            return

        self.user_ids.remove(user_id)

    @staticmethod
    def create_new_room(room_name: str, owner_id: int, room_rule: str) -> Room:
        room_id = str(uuid.uuid4())
        return Room(room_id, room_name, owner_id, room_rule)

    def add_message(self, message: ChatMessage) -> None:
        '''
        Make sure only the last fifty messages is cached in RAM
        '''
        current_messages = self.messages[message.message_type]
        if len(current_messages) >= self.MAX_MESSAGE_LENGTH:
            current_messages.pop(0)
        # add messages to db via publisher
        chat_room_db_manager.add_message(message)

        current_messages.append(message)
    
    def to_dict(self, is_message_included: bool = False) -> dict[str, Any]:
        dict_copy = deepcopy(self.__dict__)
        if is_message_included:
            json_messages = {}
            for message_type in ["regular", "ai"]:
                message_dicts:list[dict[str, str]] = [
                    message.to_dict() for message in self.messages[message_type]
                ]
                json_messages[message_type] = message_dicts
            
            dict_copy["messages"] = json_messages
        else:
            dict_copy.pop("messages")
        

        dict_copy["socket_events"] = {
            "regular": self.get_socket_event("regular"), 
            "ai": self.get_socket_event("ai"),
            "notification": self.get_socket_event("notification"),
            "thinking": self.get_socket_event("thinking"),
            "number_of_people": self.get_socket_event("number_of_people")
        }

        dict_copy["num_of_people"] = self.number_of_people
        dict_copy["room_members"] = self.get_room_members()
        dict_copy.pop("user_ids")
        dict_copy.pop("room_rule")
        return dict_copy
        
