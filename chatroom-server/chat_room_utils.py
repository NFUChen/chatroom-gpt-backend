from room_database_manager import room_db_manager
from chat_message import ChatMessage
from room import Room
from room_manager import RoomManager
# from user_manager import UserManager

def init_messages(room_id: str, message_length: int) -> dict[str, ChatMessage]:
    messages_dict = {
        "regular": [], "ai": []
    }

    for message_type in messages_dict.keys():
        message_dicts = room_db_manager.query_chat_messsages(
            message_type= message_type, 
            room_id= room_id, 
            n_records= message_length
        )
        messages_dict[message_type] = [
            ChatMessage(**message_dict) for message_dict in message_dicts
        ]
    
    return messages_dict


def init_room_manager() -> RoomManager:
    all_rooms = [
        Room(**room_dict) for room_dict in room_db_manager.query_all_rooms()
    ]
    #messages
    for room in all_rooms:
        messages_dict = init_messages(room.room_id, room.MAX_MESSAGE_LENGTH)
        room.set_messages(messages_dict)
    return RoomManager(rooms= all_rooms)


# user_manager = UserManager()
room_manager = init_room_manager()