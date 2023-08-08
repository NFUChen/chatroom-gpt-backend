from user import User
import requests
class UserDatabaseManager:
    def __init__(self) -> None:
        self.query_api = f"http://query_manager:5000/query"
        self.produce_api =  "http://producer:5000/produce"
        

    def _query_user_by(self, by: str, value: str) -> dict[str, str] | None:

        query_dict = {"query": f"SELECT * FROM users WHERE {by} = '{value}'"}
        users = requests.post(self.query_api, json= query_dict).json()["data"]
        if len(users) == 0:
            return
    
        return users.pop()

    def is_duplicate_user(self, user_email: str) -> bool:
        if user_email is None:
            return False
        
        user = self._query_user_by("user_email", user_email)
        if user is None:
            return False
        
        return True

    def register_user(self, email: str, user_name: str, hashed_password: str) -> dict[str, str]:
        post_json = {
            "queue": "user",
            "data": {
                "user_email": email,
                "user_name": user_name,
                "password": hashed_password
            }
        }
        response = requests.post(
            self.produce_api, json= post_json
        )
        return response.json()

        
    def get_user_by_email(self, user_email: str) -> User:
        user_dict = self._query_user_by("user_email", user_email)
        if user_dict is None:
            raise ValueError("User not found")

        return User(**user_dict)

    def get_user_by_user_id(self, user_id: str) -> User:
        user_dict = self._query_user_by("user_id", user_id)
        if user_dict is None:
            raise ValueError("User not found")

        return User(**user_dict)

user_db_manager = UserDatabaseManager()

if __name__ == "__main__":
    print(user_db_manager.get_user_by_email("wich@sram.com").to_dict())
