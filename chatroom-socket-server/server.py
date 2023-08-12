from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO
from utils import handle_server_errors

app = Flask(__name__)
CORS(app)
sio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def index():
    return "Welcome to chatroom central socket server"


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
    sio.run(app, host="0.0.0.0", debug= False)
    