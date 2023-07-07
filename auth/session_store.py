from util import generate_unique_random_string
import redis
import json
class SessionStore:
    def __init__(self, host: str, port: int) -> None:
        self.redis_client = redis.Redis(host, port, db=0)
        self.expired_time = 180

    def add_user_in_session(self, user_dict: dict[str, str]) -> str:
        sid = generate_unique_random_string(100)
        user_json = json.dumps(user_dict)
        self.redis_client.setex(sid, self.expired_time, user_json)
        return sid
    
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
    
    def get_user_dict_from_session(self, sid: str) -> dict[str, str]:
        user_dict_byte = self.redis_client.get(sid)
        if user_dict_byte is None:
            return None
        return json.loads(user_dict_byte.decode())
    
session_store = SessionStore("redis", 6379)