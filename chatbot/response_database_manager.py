from typing import Any
import requests
class ResponseDatabaseManager:
    def __init__(self) -> None:
        self.produce_api =  "http://producer:5000/produce"

    def save_response(self, response_dict: dict[str, Any]) -> None:
        return requests.post(
            self.produce_api, json= response_dict
        )
    

response_db_manager = ResponseDatabaseManager()