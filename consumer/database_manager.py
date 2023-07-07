import time
import pymongo
from logger import Logger

class DataBaseManager:
    ERROR = "error"
    def __init__(self, user_name: str, password: str, host: str, port: int) -> None:
        url = f"mongodb://{user_name}:{password}@{host}:{port}/"
        self.client = pymongo.MongoClient(url)
        self.error_collection = self.client[self.ERROR][self.ERROR]
        self.db_logger = Logger("db-log.log")


    def insert_data_into_db(self, db_name: str, collection_name: str, info_dict: dict[str, str]) -> None:
        while (True):
            try:
                print(
                    f"Saving {info_dict} into [{db_name}, {collection_name}]")
                inserted_one_result = self.client[db_name][collection_name].insert_one(
                    info_dict)
                print(inserted_one_result)
                print("Data saved.")
                return
            except Exception as error:
                self.db_logger.log_error(error)
                time.sleep(0.1)



db_manager = DataBaseManager("chat-admin", "chatchat-admin", "mongo", 27017)
