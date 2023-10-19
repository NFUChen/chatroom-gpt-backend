from __future__ import annotations
from typing import Any
from copy import deepcopy
from enum import Enum
from chat_message import ChatMessage
import uuid

class RoomType(Enum):
    PUBLIC = "public"
    PRIVATE = "private"





class Room:
    MAX_MESSAGE_LENGTH = 20
    DEFAULT_ROOM_RULE = "Please enter your custom instruction."
    MAX_RULE_LENGTH = 500
    PASSWORD_MIN_LENGTH = 4
    PASSWORD_MAX_LENGTH = 16
    def __init__(self, 
                 room_id: str, 
                 room_name: str, 
                 owner_id: int,
                 room_rule: str,
                 room_type: str,
                 room_password: str,
                 is_deleted: bool = 0,
                 ) -> None:
        self.room_id = room_id
        self.room_name = room_name
        self.owner_id = owner_id
        self.room_rule = room_rule
        self.room_type = room_type
        self.room_password = room_password
        self.user_ids: list[str] = []
        self.messages = self._get_empty_messages()
        self.is_deleted = True if is_deleted else False
        self.is_locked = False
        self.cached_prompt_message = None
        
    @property
    def number_of_people(self) -> int:
        return len(self.user_ids)
    
    def __get_user_id_and_name(self, full_user_id: str) -> tuple[int, str]:
        user_id, user_name = full_user_id.split("-")
        return int(user_id), user_name

    def get_room_members(self) -> list[dict[str, int | str]]:
        members = []
        for full_user_id in self.user_ids:
            user_id, user_name = self.__get_user_id_and_name(full_user_id)
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
            
    def user_join_room(self, full_user_id: str, room_password: str, is_in_personal_room_list: bool) -> None:
        if full_user_id in self.user_ids:
            return
        current_user_id, _ = self.__get_user_id_and_name(full_user_id)
        if current_user_id == self.owner_id or is_in_personal_room_list:
            self.user_ids.append(full_user_id)
            return
        
        if self.room_type == RoomType.PRIVATE.value and self.room_password != room_password:
            raise ValueError(f"Wrong password for joining room: {self.room_id}")
                
        self.user_ids.append(full_user_id)

    def user_leave_room(self, full_user_id: str) -> None:
        if full_user_id not in self.user_ids:
            return

        self.user_ids.remove(full_user_id)

    @classmethod
    def _validate_room_type(self, room_type: str) -> None:
        valid_room_types = [RoomType.PRIVATE.value, RoomType.PUBLIC.value]
        if room_type not in valid_room_types:
            raise ValueError(f"Room type '{room_type}' is not supported, please enter one of the following: {valid_room_types}")
        
    @classmethod
    def create_new_room(cls, room_type: str, room_name: str, owner_id: int, room_password: str) -> Room:
        if len(room_name) == 0:
            raise ValueError("Room name should not be empty")
        
        cls._validate_room_type(room_type)
        
        if room_type == RoomType.PRIVATE.value:
            password_length = len(room_password)
            if password_length < cls.PASSWORD_MIN_LENGTH:
                raise ValueError(f"Room password should be at least {cls.PASSWORD_MIN_LENGTH} characters long")
            if password_length > cls.PASSWORD_MAX_LENGTH:
                raise ValueError(f"Room password should be at most {cls.PASSWORD_MAX_LENGTH} characters long")
    
        room_id = str(uuid.uuid4())
        return Room(room_id, room_name, owner_id, cls.DEFAULT_ROOM_RULE, room_type, room_password)

    def add_message(self, message: ChatMessage) -> None:
        '''
        Make sure only the last fifty messages is cached in RAM
        '''
        current_messages = self.messages[message.message_type]
        if len(current_messages) >= self.MAX_MESSAGE_LENGTH:
            current_messages.pop(0)

        current_messages.append(message)

    def update_room_rule(self, user_id: int, rule: str) -> str:
        if user_id != self.owner_id:
            raise ValueError(f"Only owner can update room rule, current owner: {self.owner_id}")
        
        if len(rule) > self.MAX_RULE_LENGTH:
            raise ValueError(f"Room rule should be at most {self.MAX_RULE_LENGTH} characters long")
        

        
        self.room_rule = rule
        return self.room_rule
    
    def update_room_password(self, user_id: int, new_password: str) -> str:
        if user_id != self.owner_id:
            raise ValueError(f"Only owner can update room password, current owner: {self.owner_id}")
        if len(new_password) < self.PASSWORD_MIN_LENGTH:
            raise ValueError(f"Room password should be at least {self.PASSWORD_MIN_LENGTH} characters long")
        if len(new_password) > self.PASSWORD_MAX_LENGTH:
            raise ValueError(f"Room password should be at most {self.PASSWORD_MAX_LENGTH} characters long")
        self.room_password = new_password
        return self.room_password
    
    def change_to_rooom_type(self, target_room_type: str) -> str:
        self._validate_room_type(target_room_type)

        if target_room_type == RoomType.PUBLIC.value:
            self.room_type = RoomType.PUBLIC.value
            return
        
        if len(self.room_password) == 0:
            raise ValueError("Room password should not be empty, please update password first")
        self.room_type = RoomType.PRIVATE.value
        
        return self.room_type
    
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
        dict_copy.pop("room_password")
        return dict_copy
        
