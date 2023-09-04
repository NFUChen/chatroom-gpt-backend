from typing import Any
import requests

Embeddings = dict[str, str | list[float]]

class ResponseDatabaseManager:
    def __init__(self) -> None:
        self.produce_api =  "http://producer:5000/produce"

    def save_embeddings(self, collection_name: str, embeddings: dict[str, str | Embeddings]) -> None:
        post_json = {
            "queue": "embeddings",
            "data": {
                "collection_name": collection_name,
                "embeddings": embeddings
            }
        }
        return self.__post_to_producer(post_json)
    
    def __post_to_producer(self, post_json: dict[str, Any]) -> dict[str, str]:
        resp_json = requests.post(
            self.produce_api, json= post_json
        ).json()
        error = resp_json["error"]
        if error is not None:
            raise ValueError(f"Producer: {error}")
        return resp_json
    

    

response_db_manager = ResponseDatabaseManager()