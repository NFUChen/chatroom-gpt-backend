
import ast
from database_manager import db_manager
from consumer import Consumer
consumer = Consumer("guest", "guest", "rabbitmq")

def save_doc(ch, method, properties, body):
    print(" [x] Received %r" % body)
    message_dict = ast.literal_eval(body.decode())
    db_name = message_dict["db"]
    collection_name = message_dict["collection"]
    doc = message_dict["doc"]
    db_manager.insert_data_into_db(db_name, collection_name, doc)

queues = ["user"]
for queue in queues:
    consumer.consume(queue, save_doc)

consumer.start_consuming()