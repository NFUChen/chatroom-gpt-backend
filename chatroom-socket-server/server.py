from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from mqtt_client import Client
from utils import handle_server_errors
import socket
import ast
from message_queue import MessageQueue
app = Flask(__name__)

CORS(app)
sio = SocketIO(app, cors_allowed_origins="*")
queue = MessageQueue()
host = socket.gethostname()

@app.route("/")
def index():
    return f"Welcome to chatroom central socket server [{host}]"


client = Client(f"socket-server-{socket.gethostname()}", "mosquitto", "message/#", 1)
def default_on_message(client, userdata, message):
    message_dict = ast.literal_eval(message.payload.decode('utf-8'))
    queue.push(message_dict)

client.set_on_message_callback(default_on_message)


def start_queue_consumer():
    def wrapper():
        while (True):
            for message_dict in queue.next():
                if message_dict is None:
                    sio.sleep(1)
                    continue
                socket_event = message_dict["socket_event"]
                data = message_dict["data"]
                sio.start_background_task(sio.emit(socket_event, {"data": data}))
                sio.sleep(0.01)
    sio.start_background_task(target= wrapper)

@sio.on('connect')
def handle_connect():
    print(f'Client {request.sid} connected')
    emit('connect_resp', {'message': f'connected sucessfully with server [{host}]'})

@sio.on('disconnect')
def handle_disconnect():
    print(f'Client {request.sid} disconnected')
    emit('connect_resp', {'message': f'disconnected sucessfully with server [{host}]'})


@app.route("/emit", methods=["POST"])
@handle_server_errors
def emit_message_to_socekt_event():
    '''
    {
        "socket_event": str
        "content"
    }
    '''
    request_json = request.get_json()
    socket_event = request_json["socket_event"]
    data = request_json["data"]
    sio.emit(socket_event, {"data": data})

    return f"data: {data} is sent to event: {socket_event}]"


@app.route("/help", methods=["GET"])
def show_help():
    help_message = """
    Welcome to the Help Page
    
    /emit Route Documentation:
    
    This route allows you to emit a socket event with a specified message content.
    
    Request Method: POST
    Endpoint: /emit
    
    Request JSON Schema:
    {
        "socket_event": "str",
        "content": "str"
    }
    
    Example Usage:
    POST /emit
    {
        "socket_event": "new_message",
        "content": "Hello, world!"
    }
    
    Response:
    The message content is sent to the specified socket event.

    """
    
    return {"data": help_message}, 200



if __name__ == "__main__":
    client.listen()
    start_queue_consumer()
    sio.run(app, host="0.0.0.0", debug= False)
    