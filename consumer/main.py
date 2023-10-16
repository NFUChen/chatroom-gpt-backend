from datetime import datetime
import ast
from mysql_database_manager import mysqldb_manager
from utils import create_all_tables
from consumer import Consumer

consumer = Consumer("guest", "guest", "rabbitmq")

def insert_user_callback(ch, method, properties, body):
    
    message_dict = ast.literal_eval(body.decode())
    mysqldb_manager.insert_user(
       message_dict["user_email"],
       message_dict["user_name"],
       message_dict["password"],
    )

def insert_room_callback(ch, method, properties, body):
    '''
    room_id VARCHAR(36) PRIMARY KEY NOT NULL,
    owner_id INT NOT NULL,
    room_name VARCHAR(255) NOT NULL UNIQUE,
    room_type VARCHAR(10) NOT NULL,
    '''
    message_dict = ast.literal_eval(body.decode())
    mysqldb_manager.insert_room(
        message_dict["room_id"],
        message_dict["owner_id"],
        message_dict["room_name"],
        message_dict["room_type"]
    )
    
def insert_room_configs_callback(ch, method, properties, body):
    '''
    room_id VARCHAR(36) PRIMARY KEY NOT NULL,
    room_rule TEXT NOT NULL
    '''
    message_dict = ast.literal_eval(body.decode())
    mysqldb_manager.insert_room_config(
        message_dict["room_id"],
        message_dict["room_rule"],
        message_dict["room_password"]
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
    datetime_format = "%Y-%m-%d %H:%M:%S.%f"
    mysqldb_manager.insert_message(
        message_dict["message_id"], 
        message_dict["message_type"],
        message_dict["room_id"], 
        message_dict["user_id"], 
        message_dict["content"],
        datetime.strptime(message_dict["created_at"], datetime_format),
        message_dict["is_memo"]
    )
    
def delete_room_callback(ch, method, properties, body):
    message_dict = ast.literal_eval(body.decode())
    room_id = message_dict["room_id"]
    mysqldb_manager.delete_room(room_id)

def insert_embedding_callback(ch, method, properties, body):
    collection_name_with_embeddings = ast.literal_eval(body.decode())
    datetime_format = "%Y-%m-%d %H:%M:%S.%f"
    embeddings = collection_name_with_embeddings["embeddings"]
    collection_name = collection_name_with_embeddings["collection_name"]
    for embedding_dict in embeddings:
        mysqldb_manager.insert_embedding(
            collection_name, 
            embedding_dict["document_id"], 
            embedding_dict["chunk_id"], 
            embedding_dict["text"],
            embedding_dict["text_hash"],
            datetime.strptime(embedding_dict["updated_at"], datetime_format),
            embedding_dict["vector"]
        )

def insert_personal_room_list_callback(ch, method, properties, body):
    user_id_with_room_id = ast.literal_eval(body.decode())
    mysqldb_manager.insert_personal_room(
        user_id_with_room_id["room_id"],
        user_id_with_room_id["user_id"]
    )

# gpt response
def insert_gpt_response(ch, method, properties, body):
    '''
        gpt_responses (
        response_id VARCHAR(36) PRIMARY KEY NOT NULL,
        datetime TIMESTAMP NOT NULL,
        answer TEXT NOT NULL,
        prompt_tokens INT NOT NULL,
        response_tokens INT NOT NULL,
        room_id VARCHAR(36) NOT NULL,
        user_id INT NOT NULL,
        api_key VARCHAR(255) NOT NULL,
        FOREIGN KEY (room_id) REFERENCES rooms(room_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

            gpt_messages (
            response_id VARCHAR(36) NOT NULL,
            role VARCHAR(10) CHECK (
                role = 'assistant' or role = 'user'
            ) NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY (response_id) REFERENCES gpt_responses(response_id)
        );
    '''

queue_with_callbacks = (
    ("user", insert_user_callback),
    ("add_room", insert_room_callback),
    ("add_room_config", insert_room_configs_callback),
    ("add_personal_room_list", insert_personal_room_list_callback),
    ("add_message", insert_message_callback),
    ("delete_room", delete_room_callback),
    ("embeddings", insert_embedding_callback)
)

for queue, callback in queue_with_callbacks:
    consumer.consume(queue, callback)


create_all_tables()
consumer.start_consuming()