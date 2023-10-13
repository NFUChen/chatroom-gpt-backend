from datetime import datetime
import requests
from typing import Any
from cache_service import cache_service



class ChatRoomDataBaseManager:
    def __init__(self) -> None:
        self.query_api = f"http://query_manager:5000/query"
        self.update_api = f"http://query_manager:5000/update"
        self.produce_api =  "http://producer:5000/produce"

    def add_room(self, room_id: str, owner_id: int, room_name: str, room_type: str, room_rule: str, room_password: str) -> None:
        '''
        room_id VARCHAR(36) PRIMARY KEY NOT NULL,
        owner_id INT NOT NULL,
        room_name VARCHAR(255) NOT NULL UNIQUE,
        room_type VARCHAR(10) NOT NULL,
        is_deleted BOOLEAN NOT NULL DEFAULT 0,
        FOREIGN KEY (owner_id) REFERENCES users(user_id)
        '''
        add_room_post_json = {
            "queue": "add_room", 
            "data": {
                "room_id": room_id,
                "owner_id": owner_id,
                "room_name": room_name,
                "room_type": room_type
            }
        }
        add_default_room_config_json = {
            "queue": "add_room_config",
            "data": {
                "room_id": room_id,
                "room_rule": room_rule,
                "room_password": room_password
            }
        }
        
        add_room_post_resp = self.__post_to_producer(add_room_post_json)
        add_default_room_rule_resp = self.__post_to_producer(add_default_room_config_json)
        
        return {
            "add_room_resp": add_room_post_resp,
            "add_room_rule_resp": add_default_room_rule_resp
        }
    
    def delete_room(self, room_id: str) -> None:
        
        post_json = {
            "queue": "delete_room",
            "data": {
                "room_id": room_id
            }
        }

        return self.__post_to_producer(post_json)
    
    def add_message(self, message_id: str, message_type: str, room_id: str, user_id: int, content: str, created_at: str, is_memo: bool) -> None:
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
                "message_id": message_id,
                "message_type": message_type,
                "room_id": room_id,
                "user_id": user_id,
                "content": content,
                "created_at": created_at,
                "is_memo": is_memo
            }
        }
        return self.__post_to_producer(post_json)
    
    def __convert_to_sql_array(self, words: list[str]) -> str:
        single_quoted_words = list(map(lambda word: f"'{word}'", words))
        return f"({' ,'.join(single_quoted_words)})"

    def __post_to_producer(self, post_json: dict[str, Any]) -> dict[str, str]:
        resp_json = requests.post(
            self.produce_api, json= post_json
        ).json()
        error = resp_json["error"]
        if error is not None:
            raise ValueError(f"Producer: {error}")
        return resp_json
    
    def __convert_gmt_into_utc_date(self, gmt_input_date: str) -> str:
        gmt_format = '%a, %d %b %Y %H:%M:%S GMT'
        utc_format = '%Y-%m-%d %H:%M:%S.%f'

        input_datetime = datetime.strptime(gmt_input_date, gmt_format)
        utc_date = input_datetime.strftime(utc_format)

        return utc_date
    
    def query_all_rooms(self) -> list[dict[str, str]]:
        sql = f"""
            SELECT rooms.*, room_configs.room_rule, room_configs.room_password FROM rooms
            LEFT JOIN room_configs ON rooms.room_id = room_configs.room_id 
            WHERE rooms.is_deleted = 0;
        """
        post_json = {
            "query": sql
        }
        rooms_dicts = requests.post(
            self.query_api, json= post_json
        ).json()["data"]
        return rooms_dicts


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


    def query_recent_n_chat_messsages(self, room_id: str, message_type: str, n_records: int) -> list[dict[str]]:
        '''
        message_idx INT AUTO_INCREMENT PRIMARY KEY,
        message_id VARCHAR(36) NOT NULL,
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
            SELECT * FROM (
                SELECT chat_messages.*, users.user_name FROM chat_messages 
                LEFT JOIN users on chat_messages.user_id = users.user_id 
                WHERE room_id = '{room_id}' AND message_type = '{message_type}'
                ORDER BY message_idx DESC LIMIT {n_records}
            ) AS subquery
            ORDER BY message_idx ASC;
        """
        post_json = {
            "query": sql
        }

        messages = requests.post(
            self.query_api, json= post_json
        ).json()["data"]

        for message in messages:
            message["created_at"] = self.__convert_gmt_into_utc_date(message["created_at"])
            message["modified_at"] = self.__convert_gmt_into_utc_date(message["modified_at"])

        return messages
    
    def query_n_history_messages(self, message_id: str, n_records: int) -> list[dict[str, Any]]:
        messages = cache_service.get(message_id)
        if messages is not None:
            print(f"Getting message_id: {message_id} from cache", flush= True)
            return messages
        
        sql = f"""
        SELECT subquery.*, users.user_name
            FROM (
                WITH message_info AS (
                    SELECT
                        room_id,
                        message_type,
                        message_idx
                    FROM
                        chat_messages
                    WHERE message_id = '{message_id}'
                )
                SELECT
                    *
                FROM
                    chat_messages
                WHERE
                    room_id = (SELECT room_id FROM message_info)
                    AND message_type = (SELECT message_type FROM message_info)
                    AND message_idx < (SELECT message_idx FROM message_info)
                ORDER BY message_idx DESC
                LIMIT {n_records}
            ) AS subquery
        JOIN users ON subquery.user_id = users.user_id
        ORDER BY subquery.message_idx;
        """
        post_json = {
            "query": sql
        }
        messages = requests.post(
            self.query_api, json= post_json
        ).json()["data"]

        for message in messages:
            message["created_at"] = self.__convert_gmt_into_utc_date(message["created_at"])
            message["modified_at"] = self.__convert_gmt_into_utc_date(message["modified_at"])
    
        print(f"Caching message_id: {message_id}, legnth: {len(messages)}", flush= True)
        cache_service.cache(message_id, messages)
        
        return messages
    
    def update_room_rule(self, room_id: str, room_rule: str) -> str:
        sql = f"""
            UPDATE room_configs SET room_rule = '{room_rule}' WHERE room_id = '{room_id}';
        """
        post_json = {
            "query": sql
        }
        updated_result =  requests.post(
            self.update_api, json= post_json
        ).json()
        print(updated_result, flush= True)

        if updated_result["error"] is not None:
            raise ValueError(updated_result["error"])
        return updated_result["message"]


chat_room_db_manager = ChatRoomDataBaseManager()