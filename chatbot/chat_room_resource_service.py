import requests

class ChatRoomResouceService:
    def __init__(self, room_id: str, user_id: int, user_name: str, prompt: str) -> None:

        CHATROOM_BASE_URL = "http://chatroom-server:5000"
        self.room_id = room_id
        self.user_id = user_id
        self.user_name = user_name
        self.prompt = prompt

        self.lock_room_api = f"{CHATROOM_BASE_URL}/acquire_room_lock"
        self.unlock_room_api = f"{CHATROOM_BASE_URL}/release_room_lock"
        self.add_cached_prompt_message_api = f"{CHATROOM_BASE_URL}/add_cached_prompt_message"
        self.remove_cached_prompt_message_api = f"{CHATROOM_BASE_URL}/remove_cached_prompt_message"

    def _acquire_room_lock(self) -> None:
        post_json = {
            "room_id": self.room_id,
        }

        resp = requests.post(self.lock_room_api, json= post_json)
        print(resp.content, flush= True)

    def _release_room_lock(self) -> None:
        post_json = {
            "room_id": self.room_id,
        }
        resp = requests.post(self.unlock_room_api, json= post_json)
        print(resp.content, flush= True)

    def _add_cached_prompt_message(self) -> None:
        post_json = {
            "room_id": self.room_id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "prompt":self.prompt
        }
        resp = requests.post(self.add_cached_prompt_message_api, json= post_json)
        print(resp.content, flush= True)
    def _remove_cached_prompt_message(self) -> None:
        post_json = {
            "room_id": self.room_id,
        }
        resp = requests.post(self.remove_cached_prompt_message_api, json= post_json)
        print(resp.content, flush= True)

    def run_external_service(self, service_callback: callable) -> None:
        try:
            self._add_cached_prompt_message()
            self._acquire_room_lock()
            service_callback()
        finally:
            self._release_room_lock()
            self._remove_cached_prompt_message()