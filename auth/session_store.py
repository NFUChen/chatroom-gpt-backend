from utils import generate_unique_random_string
import redis
import json

EXPIRE_TIME =  60 * 60 * 24 * 3

class SessionStore:
    def __init__(self, host: str, port: int) -> None:
        self.redis_client = redis.Redis(host, port, db=15)
        self.expired_time = EXPIRE_TIME

    def add_user_in_session(self, user_dict: dict[str, str]) -> str:
        sid = generate_unique_random_string(100)
        user_json = json.dumps(user_dict)
        self.redis_client.setex(sid, self.expired_time, user_json)
        return sid
    
    def remove_duplicated_user(self, user_dict: dict[str, str]) -> None:
        sids = self.redis_client.keys('*')
        for sid in sids:
            user_dict_byte = self.redis_client.get(sid)
            current_user_dict = json.loads(user_dict_byte.decode())
            if current_user_dict == user_dict:
                self.redis_client.delete(sid)
                print(f"Remove duplicated user login: {current_user_dict}\n[{sid}]", flush= True)
                return
    
    def remove_sid_from_session(self, sid: str) -> None:
        self.redis_client.delete(sid)
    
    def refresh_session(self,sid: str) -> None:
        user_dict_byte = self.redis_client.get(sid)
        if user_dict_byte is None:
            raise ValueError(f"Invalid sid: {sid}")
        self.redis_client.setex(sid, self.expired_time, user_dict_byte.decode())

    def is_valid_sid(self, sid: str) -> bool:
        user_dict_byte = self.redis_client.get(sid)
        if user_dict_byte is None:
            return False
        return True
    
    def get_user_dict_from_session(self, sid: str) -> dict[str, str] | None:
        user_dict_byte = self.redis_client.get(sid)
        if user_dict_byte is None:
            return
        return json.loads(user_dict_byte.decode())
    
session_store = SessionStore("redis", 6379)