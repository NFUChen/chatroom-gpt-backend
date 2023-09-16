import pika
import functools
import traceback
def construct_connection(user_name: str, password: str, rabbitMQ_host: str):
    credentials = pika.PlainCredentials(user_name, password)
    connection_param = pika.ConnectionParameters(host=rabbitMQ_host, credentials=credentials)
    connection = pika.BlockingConnection(connection_param)

    return connection

def get_error_detail(e: Exception):
    error_name = e.__class__.__name__
    trace_back = traceback.extract_tb(e.__traceback__)
    file_name = trace_back[-1].filename
    line_number = trace_back[-1].lineno
    error_message = str(e)
    return {
        'error_name': error_name,
        'file_name': file_name,
        'line_number': line_number,
        'error_message': error_message,
        "trace_back": str(trace_back)
    }

def handle_server_errors(func):
    @functools.wraps(func)
    def decorated(*args, **kwargs):
        try:
            return {
                "data": func(*args, **kwargs),
                "error": None,
                "is_success": True
            }
        except Exception as error:
            return {
                "data": None,
                "error": get_error_detail(error),
                "is_success": False
            }, 200
    return decorated