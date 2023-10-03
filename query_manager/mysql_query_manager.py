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

    def query(self, sql: str) -> dict[str, str | list[dict[str, Any]]]:
        try:
            if not self.connection or not self.connection.ping(reconnect=True):
                self.connect()
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
            return {
                "data": result,
                "error": None
            }
        except Exception as error:
            print(f"Error while executing query: {error}", flush= True)
            return {
                "data": [],
                "error": str(error)
            }
        
    def execute_update(self, sql: str) -> dict[str, str]:
        try:
            if not self.connection or not self.connection.ping(reconnect=True):
                self.connect()
            with self.connection.cursor() as cursor:
                affected_rows = cursor.execute(sql)
                self.connection.commit()
            return {
                "message": f"UPDATE successful. {affected_rows} rows affected.",
                "error": None
            }
        except Exception as error:
            print(f"Error while executing UPDATE query: {error}", flush=True)
            return {
                "message": "UPDATE failed.",
                "error": str(error)
            }
        

query_manager = MySqlQueryManaer("mysql", "root", "chatchat-admin", "db")

if __name__ == "__main__":
    print(query_manager.query("SELECT * FROM users"))