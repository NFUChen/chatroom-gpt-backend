from datetime import datetime
import ast
from mysql_database_manager import mysqldb_manger
from utils import create_all_tables
from consumer import Consumer

consumer = Consumer("guest", "guest", "rabbitmq")

def insert_user_callback(ch, method, properties, body):
    datetime_format = "%Y-%m-%d %H:%M:%S.%f"
    message_dict = ast.literal_eval(body.decode())
    mysqldb_manger.insert_user(
       message_dict["user_email"],
       message_dict["user_name"],
       message_dict["password"],
       datetime.strptime(message_dict["created_at"], datetime_format)
    )

def insert_room_callback(ch, method, properties, body):
    '''
    room_id VARCHAR(36) PRIMARY KEY NOT NULL,
    owner_id INT NOT NULL,
    room_name VARCHAR(255) NOT NULL UNIQUE,
    room_type VARCHAR(10) NOT NULL,
    '''
    message_dict = ast.literal_eval(body.decode())
    mysqldb_manger.insert_room(
        message_dict["room_id"],
        message_dict["owner_id"],
        message_dict["room_name"],
        message_dict["room_type"]
    )

def insert_message_callback(ch, method, properties, body):
    '''
    "message_id": message.message_id,
    "message_type": message.message_type,
    "room_id": message.room_id,
    "user_id": message.user_id,
    "content": message.content,
    "created_at": message.created_at
    '''
    message_dict = ast.literal_eval(body.decode())
    
    mysqldb_manger.insert_message(
        message_dict["message_id"], 
        message_dict["message_type"],
        message_dict["room_id"], 
        message_dict["user_id"], 
        message_dict["content"],
        message_dict["created_at"]
    )
    
def delete_room_callback(ch, method, properties, body):
    message_dict = ast.literal_eval(body.decode())
    room_id = message_dict["room_id"]
    mysqldb_manger.delete_room(room_id)


queue_with_callbacks = (
    ("user", insert_user_callback),
    ("add_room", insert_room_callback),
    ("add_message", insert_message_callback),
    ("delete_room", delete_room_callback),
)
for queue, callback in queue_with_callbacks:
    consumer.consume(queue, callback)


create_all_tables()
consumer.start_consuming()