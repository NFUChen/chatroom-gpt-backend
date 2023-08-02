
import ast
from mysql_database_manager import mysqldb_manger
from utils import create_all_tables
from consumer import Consumer

consumer = Consumer("guest", "guest", "rabbitmq")

def insert_user_callback(ch, method, properties, body):
    # print(" [x] Received %r" % body)
    message_dict = ast.literal_eval(body.decode())
    user = message_dict["data"]
    user_email = user["user_email"]
    uesr_name = user["user_name"]
    pwd = user["password"]
    mysqldb_manger.insert_user(
        user_email, 
        uesr_name,
        pwd
    )

queue_with_callbacks = (
    ("user", insert_user_callback),
)
for queue, callback in queue_with_callbacks:
    consumer.consume(queue, callback)


create_all_tables()
consumer.start_consuming()