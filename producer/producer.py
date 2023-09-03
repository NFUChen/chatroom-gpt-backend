from utils import construct_connection
class Producer:
    def __init__(self,
                 user_name: str,
                 password: str,
                 rabbitMQ_host: str,
                 exchange: str = '') -> None:
        self.exchange = exchange
        self.user_name = user_name
        self.password = password
        self.rabbitMQ_host = rabbitMQ_host
    def publish(self, queue: str,message: str) -> None:
        self.connection = construct_connection(
            self.user_name, self.password, self.rabbitMQ_host
        )
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue)
        self.channel.basic_publish(
            exchange=self.exchange, routing_key=queue, body=message)
        self.channel.close()
        self.connection.close()

producer = Producer("guest", "guest", "rabbitmq")
