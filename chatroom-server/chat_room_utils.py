from chat_room_database_manager import chat_room_db_manager
from chat_message import ChatMessage
from room import Room
from room_manager import RoomManager
from api_key_load_balancer import ApiKeyLoadBalancer
from personal_room_list_service import PersonalRoomListService
from utils import query_api_keys

def init_messages(room_id: str, message_length: int) -> dict[str, list[ChatMessage]]:
    messages_dict = {
        "regular": [], "ai": []
    }

    for message_type in messages_dict.keys():
        message_dicts = chat_room_db_manager.query_recent_n_chat_messsages(
            room_id= room_id, 
            message_type= message_type, 
            n_records= message_length,
        )
        messages_dict[message_type] = [
            ChatMessage(**message_dict) for message_dict in message_dicts
        ]
    
    return messages_dict


def init_room_manager() -> RoomManager:
    all_rooms = [
        Room(**room_dict) for room_dict in chat_room_db_manager.query_all_rooms()
    ]
    for room in all_rooms:
        messages_dict = init_messages(room.room_id, room.MAX_MESSAGE_LENGTH)
        room.set_messages(messages_dict)
    return RoomManager(rooms= all_rooms)

def init_openai_api_key_loadbalancer() -> ApiKeyLoadBalancer:
    keys = query_api_keys()
    return ApiKeyLoadBalancer(keys)

def init_personal_room_list_service() -> PersonalRoomListService:
    '''
    [
        {"room_id": "xxx", "user_id": 2},
        {"room_id": "yyy", "user_id": 2}
    ] ->
    {
        2: ["xxx", "yyy"]
    }
    '''
    personal_room_list_dict:dict[int, list[str]] = {}
    for room_dict in chat_room_db_manager.query_all_personal_rooms():
        user_id = room_dict["user_id"]
        room_id = room_dict["room_id"]
        if user_id not in personal_room_list_dict:
            personal_room_list_dict[user_id] = []
        personal_room_list_dict[user_id].append(room_id)
    return PersonalRoomListService(personal_room_list_dict)
