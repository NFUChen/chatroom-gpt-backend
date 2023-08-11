# from dataclasses import dataclass
# import requests

# @dataclass
# class User:
#     user_id: int
#     user_email: str
#     user_name: str
#     is_deleted: bool
#     password: str = None

#     def to_dict(self) -> dict[str, str]:
#         user_dict = self.__dict__
#         user_dict.pop("password")

#         return user_dict

# class UserManager:
#     def __init__(self) -> None:
#         self.query_api = f"http://query_manager:5000/query"
#     def get_user_by_id(self, id: int) -> User:
#         sql = f"SELECT * FROM users WHERE user_id = {id}"

#         user_dicts = requests.post(
#             self.query_api, json= {"query": sql}
#         ).json()["data"]

#         if len(user_dicts) == 0:
#             raise ValueError(f"User with user_id {id} not found in database.")
#         user_dict = user_dicts.pop()

#         return User(
#             **user_dict
#         )
    
#     def get_all_users(self) -> list[User]:
#         sql = f"SELECT * FROM users"
        
#         user_dicts = requests.post(
#             self.query_api, json= {"query": sql}
#         ).json()["data"]

#         if len(user_dicts) == 0:
#             raise ValueError("No user found in database.")
        
#         return [
#             User(**user_dict) for user_dict in user_dicts
#         ]



