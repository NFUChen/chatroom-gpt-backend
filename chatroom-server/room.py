from __future__ import annotations
from copy import deepcopy
from enum import Enum
from chat_message import MessageType, ChatMessage
import uuid
from chat_room_database_manager import chat_room_db_manager

class RoomType(Enum):
    PUBLIC = "public"
    PRIVATE = "private"





class Room:
    MAX_MESSAGE_LENGTH = 50
    def __init__(self, 
                 room_id: str, 
                 room_name: str, 
                 owner_id: int,
                 is_deleted: bool = 0,
                 room_type: str = RoomType.PUBLIC.value
                 ) -> None:
        self.room_id = room_id
        self.room_name = room_name
        self.owner_id = owner_id
        self.room_type = room_type
        self.user_ids: list[str] = []
        self.messages = self._get_empty_messages()
        self.is_deleted = True if is_deleted else False
        self.is_locked = False

    def _get_empty_messages(self) -> dict[str, list[ChatMessage]]:
        return {
            "regular": [],
            "ai": [],
        }
    
    def lock_room(self) -> None:
        self.is_locked = True
    
    def unlock_room(self) -> None:
        self.is_locked = False

    def get_socket_event(self, message_type: MessageType) -> str:
        return f"message/{message_type}/{self.room_id}"

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
    def create_new_room(room_name: str, owner_id: int) -> Room:
        room_id = str(uuid.uuid4())
        return Room(room_id, room_name, owner_id)

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
    
    def to_dict(self, is_message_included: bool = False, is_user_ids_included: bool = False) -> dict[str, str]:
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

        if not is_user_ids_included:
            dict_copy.pop("user_ids")

        dict_copy["socket_events"] = {
            "regular": self.get_socket_event("regular"), 
            "ai": self.get_socket_event("ai"),
            "notification": self.get_socket_event("notification")
        }
        dict_copy["num_of_people"] = len(self.user_ids)

        return dict_copy
        
