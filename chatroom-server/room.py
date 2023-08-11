from __future__ import annotations
from copy import deepcopy
from enum import Enum
from chat_message import MessageType, ChatMessage
import uuid
from room_database_manager import room_db_manager

class RoomType(Enum):
    PUBLIC = "public"
    PRIVATE = "private"





class Room:
    MAX_MESSAGE_LENGTH = 50
    def __init__(self, 
                 room_id: str, 
                 room_name: str, 
                 owner_id: str,
                 is_deleted: bool,
                 messages: dict[str, list[ChatMessage]],
                 room_type: str = RoomType.PUBLIC.value
                 ) -> None:
        self.room_id = room_id
        self.room_name = room_name
        self.owner_id = owner_id
        self.room_type = room_type
        self.user_ids: list[str] = []
        self.messages = messages
        self.is_deleted = is_deleted

    def get_socket_event(self, message_type: MessageType) -> str:
        return f"room_broadcast_{message_type}_{self.room_id}"

    def set_messages(self, messages: dict[str, list[ChatMessage]]) -> None:
        self.messages = messages
        
    def user_join_room(self, user_id: str) -> None:
        self.user_ids.append(user_id)

    def user_leave_room(self, user_id: str) -> None:
        self.user_ids.remove(user_id)

    @staticmethod
    def create_new_room(room_name: str) -> Room:
        room_id = str(uuid.uuid4())
        return Room(room_id, room_name)

    def add_message(self, message: ChatMessage) -> None:
        '''
        Make sure only the last fifty messages is cached in RAM
        '''
        current_messages = self.messages[message.message_type]
        if len(current_messages) >= self.MAX_MESSAGE_LENGTH:
            current_messages.pop(0)
        # add messages to db via publisher
        room_db_manager.add_message(message)

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

        return dict_copy
        