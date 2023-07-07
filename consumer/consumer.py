import pika
def construct_connection(user_name: str, password: str, rabbitMQ_host: str):
    credentials = pika.PlainCredentials(user_name, password)
    connection_param = pika.ConnectionParameters(host=rabbitMQ_host, credentials=credentials)
    connection = pika.BlockingConnection(connection_param)

    return connection

class Consumer:
    def __init__(self,
                 user_name: str, 
                 password: str,
                 rabbitMQ_host: str,) -> None:
        self.connection = construct_connection(user_name, password, rabbitMQ_host)
        self.channel = self.connection.channel()

    def consume(self, queue: str, callback: callable) -> None:
        print(f"Registering callback on queue: {queue} with {callback.__name__}")
        self.channel.queue_declare(queue=queue)
        self.channel.basic_consume(queue=queue,on_message_callback=callback, auto_ack=True)

    def start_consuming(self) -> None:
        '''
        This is a blocking method. It will not return until the connection is closed.
        '''
        print("Start consuming...")
        self.channel.start_consuming()
        

'''
Queue:
    - credential - User

'''

