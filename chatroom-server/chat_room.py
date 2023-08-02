from enum import Enum
from user import User
from dataclasses import dataclass
import uuid
class RoomType(Enum):
    PUBLIC = "public"
    PRIVATE = "private"

from dataclasses import dataclass

@dataclass
class AiChatMessage:
    room_id: str
    role: str
    content: str
    user_name: str
    
    def to_dict(self) -> dict[str, str]:
        return self.__dict__

@dataclass
class RegularChatMessage:
    root_id: str
    user_name: str
    content: str
    def to_dict(self) -> dict[str, str]:
        return self.__dict__


class Room:
    def __init__(self, 
                 room_id: str, 
                 room_name: str, 
                 ai_messages: list[dict[str, str]] = [],  
                 regular_messages: list[dict[str, str]] = [], 
                 ) -> None:
        self.room_id = room_id
        self.room_name = room_name
        self.ai_messages = ai_messages
        self.regular_messages = regular_messages
        self.users = []

    def user_join_room(self, user: User) -> None:
        user_dict = user.to_dict()
        self.users.append(user_dict)

    def user_leave_room(self, user: User) -> None:
        user_dict = user.to_dict()
        self.users.remove(user_dict)

    def add_ai_message(self, message: AiChatMessage) -> None:
        message_dict = message.to_dict()
        self.ai_messages.append(message_dict)

    def add_regular_message(self, message: RegularChatMessage) -> None:
        message_dict = message.to_dict()
        self.regular_messages.append(message_dict)

    def get_ai_messages(self) -> list[dict[str, str]]:
        return self.ai_messages
    
    def get_regular_messages(self) -> list[dict[str, str]]:
        return self.regular_messages
    
    def to_dict(self) -> dict[str, str]:
        return self.__dict__
    



    
class RoomManager:
    def __init__(self, rooms: list[Room] = []) -> None:
        self.rooms_dict = {
            room.room_id: room for room in rooms
        }

    def get_all_room_ids(self) -> list[str]:
        return list(self.rooms_dict.keys())
    
    def get_room_by_id(self, room_id: str) -> Room:
        if room_id not in self.rooms_dict:
            raise ValueError(f"Room {room_id} not found")

        return self.rooms_dict[room_id]
    
    def add_room(self, room: Room) -> None:
        self.rooms_dict[room.room_id] = room
    
    def pop_room(self, room_id: str) -> Room:
        if room_id not in self.rooms_dict:
            raise ValueError(f"Room {room_id} not found")
        return self.rooms_dict.pop(room_id)
    
    def get_all_rooms_info(self) -> list[dict[str, str]]:
        return [room.to_dict() for room in self.rooms_dict.values()]
    
def create_new_room(room_name: str) -> Room:
    room_id = str(uuid.uuid4())
    return Room(room_id, room_name)