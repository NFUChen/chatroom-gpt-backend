from chat_room import ChatMessage, Room
import requests
from typing import Any
class ChatRoomDataBaseManager:
    def __init__(self) -> None:
        self.query_api = f"http://query_manager:5000/query"
        self.produce_api =  "http://producer:5000/produce"

    def add_room(self, room: Room) -> None:
        '''
        room_id VARCHAR(36) PRIMARY KEY NOT NULL,
        owner_id INT NOT NULL,
        room_name VARCHAR(255) NOT NULL UNIQUE,
        room_type VARCHAR(10) NOT NULL,
        is_deleted BOOLEAN NOT NULL DEFAULT 0,
        FOREIGN KEY (owner_id) REFERENCES users(user_id)
        '''
        post_json = {
            "queue": "add_room", 
            "data": {
                "room_id": room.room_id,
                "owner_id": room.owner_id,
                "room_name": room.room_name,
                "room_type": room.room_type
            }
        }
        return requests.post(
            self.produce_api, json= post_json
        ).json()
    
    def delete_room(self, room: Room) -> None:
        
        post_json = {
            "queue": "delete_room",
            "data": {
                "room_id": room.room_id
            }
        }

        return requests.post(
            self.produce_api, json= post_json
        ).json()
    
    def add_message(self, message: ChatMessage) -> None:
        '''
        message_id VARCHAR(36) PRIMARY KEY NOT NULL,
        message_type VARCHAR(10) CHECK (
            type = 'regular' OR type = 'ai'
        ) NOT NULL,
        room_id VARCHAR(36) NOT NULL,
        user_id INT NOT NULL,
        content TEXT NOT NUL,
        created_at TIMESTAMP,
        /* created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, */
        modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (room_id) REFERENCES rooms(room_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        '''
        post_json = {
            "queue": "add_message",
            "data": {
                "message_id": message.message_id,
                "message_type": message.message_type,
                "room_id": message.room_id,
                "user_id": message.user_id,
                "content": message.content,
                "created_at": message.created_at
            }
        }

        return requests.post(
            self.produce_api, json= post_json
        ).json()
    
    def __convert_to_sql_array(self, words: list[str]) -> str:
        single_quoted_words = list(map(lambda word: f"'{word}'", words))
        return f"({' ,'.join(single_quoted_words)})"
    
    def query_all_rooms(self) -> list[dict[str, str]]:
        sql = f"""
            SELECT * FROM rooms WHERE room_id
        """ 
        post_json = {
            "query": sql
        }
        return requests.post(
            self.query_api, json= post_json
        ).json()["data"]


    def query_rooms(self, room_ids: list[str]) -> list[dict[str, str]]:
        '''
        room_id VARCHAR(36) PRIMARY KEY NOT NULL,
        owner_id INT NOT NULL,
        room_name VARCHAR(255) NOT NULL UNIQUE,
        room_type VARCHAR(10) NOT NULL,
        is_deleted BOOLEAN NOT NULL DEFAULT 0,
        '''
        sql_arrays = self.__convert_to_sql_array(room_ids)
        sql = f"""
            SELECT * FROM rooms WHERE room_id IN {sql_arrays}
        """ 
        post_json = {
            "query": sql
        }
        return requests.post(
            self.query_api, json= post_json
        ).json()["data"]


    def query_chat_messsages(self, n_records: int, room_id: str, message_type: str) -> list[dict[str]]:
        '''
        message_id VARCHAR(36) PRIMARY KEY NOT NULL,
        message_type VARCHAR(10) CHECK (
            type = 'regular' OR type = 'ai'
        ) NOT NULL,
        room_id VARCHAR(36) NOT NULL,
        user_id INT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP,
        /* created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, */
        modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        '''
        sql = f"""
            SELECT * FROM chat_messages 
            WHERE room_id = {room_id} AND message_type = {message_type} 
            ORDER BY created_at DESC
            LIMIT {n_records}
        """
        post_json = {
            "query": sql
        }
        return requests.post(
            self.query_api, json= post_json
        ).json()["data"]


room_db_manager = ChatRoomDataBaseManager()