from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from chat_room_utils import room_manager
from utils import handle_server_errors
from room import Room
from chat_message import ChatMessage
import requests


app = Flask(__name__)
CORS(app)
sio = SocketIO(app, cors_allowed_origins="*")
socket_server_api = "http://chatroom-socket-server:5000/emit"

@app.route("/")
def index():
    return "Welcome to chatroom central socket server"


@sio.on('connect')
def handle_connect():
    print(f'Client {request.sid} connected')
    emit('connect_resp', {'message': 'connected sucessfully with server'})

@sio.on('disconnect')
def handle_disconnect():
    print(f'Client {request.sid} disconnected')
    emit('connect_resp', {'message': 'disconnected sucessfully with server'})


@app.route("/join_room", methods = ["POST"])
@handle_server_errors
def join_room():
    request_json = request.get_json()
    room_id = request_json["room_id"]
    user_id = request_json["user_id"]
    user_name = request_json["user_name"]

    room = room_manager.get_room_by_id(room_id)
    room.user_join_room(user_id)
    notification = {
            "message":f"{user_name} has joined the room.",
            "room_info": room.to_dict()
    }
    sio.emit(room.get_socket_event("notification"), notification)
    return "ok"

@app.route("/leave_room", methods = ["POST"])
@handle_server_errors
def leave_room():
    request_json = request.get_json()
    room_id = request_json["room_id"]
    user_id = request_json["user_id"]
    user_name = request_json["user_name"]

    room = room_manager.get_room_by_id(room_id)
    room.user_leave_room(user_id)

    notification = {
            "message":f"{user_name} has left the room.",
            "room_info": room.to_dict()
    }
    sio.emit(room.get_socket_event("notification"), notification)
    return "ok"

@app.route("/create_room", methods=["POST"])
@handle_server_errors
def create_room():
    request_json = request.get_json()
    room_name = request_json["room_name"]
    owner_id = request_json["owner_id"]
    new_room = Room.create_new_room(room_name, owner_id)
    room_manager.add_room(new_room)
    return new_room.to_dict()

@app.route("/delete_room", methods=["POST"])
@handle_server_errors
def delete_room():
    request_json = request.get_json()
    room_id = request_json["room_id"]
    popped_room =  room_manager.pop_room(room_id)
    return popped_room.to_dict()

@app.route("/room_info", methods=["POST"])
@handle_server_errors
def get_room_info():
    request_json = request.get_json()
    room_id = request_json["room_id"]
    is_message_included = request_json.get("is_message_included", False)
    is_user_ids_included = request_json.get("is_user_ids_included", False)

    room = room_manager.get_room_by_id(room_id)
    return room.to_dict(
            is_message_included= is_message_included, 
            is_user_ids_included= is_user_ids_included
            )

@app.route("/emit_message_to_room", methods=["POST"])
@handle_server_errors
def emit_message_to_room():
    '''
    {
        "message_type": "regular" | "ai"
        "room_id": str
        "user_id": str
        "content": str
        "is_message_persist": bool
    } 
    '''
    request_json = request.get_json()
    valid_message_type = ["regular", "ai"]
    message_type = request_json["message_type"]
    if message_type not in valid_message_type:
        raise ValueError(f"Invalid message type: {message_type}, please enter one of the following: {valid_message_type}")

    room_id = request_json["room_id"]
    user_id = request_json["user_id"]
    content = request_json["content"]
    room = room_manager.get_room_by_id(room_id)
    
    requests.post(
        socket_server_api, 
        json= {
            "socket_event": room.get_socket_event(message_type),
            "content": content
        }
    )
    is_message_persist = request_json.get("is_message_persist", False)
    chat_message = ChatMessage.create_chat_message(
        message_type, user_id, room_id, content
    )
    if is_message_persist:
        room.add_message(
            chat_message
        )
    return {
        **chat_message.to_dict(), "is_message_persist": is_message_persist
    }

@app.route("/list_room")
@handle_server_errors
def list_room():
    return room_manager.get_all_rooms_info()



if __name__ == "__main__":
    sio.run(app, host="0.0.0.0", debug= False)
    