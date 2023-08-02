import pymysql
from typing import Any
class MySqlQueryManaer:
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

    def query(self, sql: str) -> list[dict[str, Any]]:
        try:
            if not self.connection or not self.connection.ping(reconnect=True):
                self.connect()
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
            return result
        except Exception as e:
            print(f"Error while executing query: {e}")

query_manager = MySqlQueryManaer("mysql", "root", "chatchat-admin", "db")

if __name__ == "__main__":
    print(query_manager.query("SELECT * FROM users"))