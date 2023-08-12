import pymysql
from typing import Any
from datetime import datetime
class MySqlDataBaseManaer:
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
    def __init__(self, host: str, user: str, password: str, database: str) -> None:
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self) -> None:
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=pymysql.cursors.DictCursor
            )
            print("Connected to the database.")
        except Exception as e:
            print(f"Error while connecting: {e}")

    def _execute(self, sql: str, data: Any=None) -> list[dict[str, Any]]:
        try:
            if not self.connection or not self.connection.ping(reconnect=True):
                self.connect()
            with self.connection.cursor() as cursor:
                if data is not None:
                    cursor.execute(sql, data)
                else:
                    cursor.execute(sql)
                result = cursor.fetchall()
            self.connection.commit()
            return result
        except Exception as e:
            print(f"Error while executing query: {e}")
    def insert_user(self, user_email: str,user_name: str, password: str) -> Any:
        sql = "INSERT INTO users (user_email, user_name, password) VALUES (%s, %s, %s)"
        return self._execute(sql, (user_email ,user_name, password))

    def insert_room(self, room_id: str, owner_id: str, room_name: str, room_type: str) -> Any:
        sql = "INSERT INTO rooms (room_id, owner_id, room_name, room_type) VALUES (%s, %s, %s, %s)"
        return self._execute(sql, (room_id ,owner_id, room_name, room_type))
    
    def delete_room(self, room_id: str) -> Any:
        sql = f"UPDATE rooms SET is_deleted = 1 WHERE room_id = {room_id}"
        return self._execute(sql)
    def insert_message(self, message_id: str, message_type:str, room_id: str, user_id: str, content: str, created_at: datetime):

        sql = "INSERT INTO chat_messages (message_id, message_type, room_id, user_id, content, created_at) VALUES (%s, %s, %s, %s, %s, %s)"
        return self._execute(sql, (message_id, message_type, room_id, user_id, content, created_at.strftime(self.TIMESTAMP_FORMAT)))

mysqldb_manger = MySqlDataBaseManaer("mysql", "root", "chatchat-admin", "db")

if __name__ == "__main__":
    print(mysqldb_manger.insert_user("wichen@sram.com","wichen", "chatchat-admin"))
    print(mysqldb_manger.insert_user("rili@sram.com","rili", "chatchat-admin"))
    print(mysqldb_manger._execute("SELECT * FROM users"))