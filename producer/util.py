import pika
def construct_connection(user_name: str, password: str, rabbitMQ_host: str):
    credentials = pika.PlainCredentials(user_name, password)
    connection_param = pika.ConnectionParameters(host=rabbitMQ_host, credentials=credentials)
    connection = pika.BlockingConnection(connection_param)

    return connection