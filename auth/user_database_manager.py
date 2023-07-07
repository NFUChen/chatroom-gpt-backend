import pymongo
from user import User
import requests
class UserDatabaseManager:
    CREDENTIALS_DB = "credentials"
    USER = "USER"
    def __init__(self,host: str, port: int, user_name: str, password: str) -> None:
        url = f"mongodb://{user_name}:{password}@{host}:{port}/"
        self.mongo_client = pymongo.MongoClient(url)
        self.user_col = self.mongo_client[self.CREDENTIALS_DB][self.USER]

    def is_duplicate_user(self, user_email: str) -> bool:
        if user_email is None:
            return False
        
        doc = self.user_col.find_one(
            {"email": user_email}
        )
        if doc is None:
            return False
        return True

    def register_user(self, email: str, user_name: str, hashed_password: str) -> None:
        post_json = {
            "queue": "user",
            "db": "credentials",
            "collection": "USER",
            "doc": {
                "email": email,
                "user_name": user_name,
                "hashed_password": hashed_password
            }
        }
        response = requests.post(
            "http://producer:8080/produce", json= post_json
        )
        return response.json()

        
    def get_user_by_email(self, email: str) -> User | None:
        doc = self.user_col.find_one(
            {"email": email}
        )
        if doc is None:
            return
        doc.pop("_id")
        return User(**doc)

    







user_db_manager = UserDatabaseManager("mongo", 27017, "chat-admin", "chatchat-admin")