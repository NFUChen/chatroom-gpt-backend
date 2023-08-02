from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room, emit, send


from chat_room import RoomManager, Room, create_new_room
from user import User
from utils import handle_server_errors

app = Flask(__name__)
CORS(app)
sio = SocketIO(app, cors_allowed_origins="*")
room_manager = RoomManager()


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

@sio.on('join')
def on_join(data):
    user_name = data['user_name']
    room_id = data['room']
    join_room(room_id)
    target_room = room_manager.get_room_by_id(room_id)
    target_room.user_join_room(User(user_name))
    notification = {
        "message":"{user_name} has join the room.",
        "room_info": target_room.to_dict()
    }
    sio.emit('room_message_resp', notification, to=room_id)

@sio.on('leave')
def on_leave(data):
    user_name = data['user_name']
    room_id = data['room']
    leave_room(room_id)
    target_room = room_manager.get_room_by_id(room_id)
    target_room.user_leave_room(User(user_name))
    notification = {
        "message":"{user_name} has left the room.",
        "room_info": target_room.to_dict()
    }
    sio.emit('room_message_resp', notification, to=room_id)


@app.route("/create_room", methods=["POST"])
@handle_server_errors
def create_room():
    request_json = request.get_json()
    room_name = request_json["room_name"]
    new_room = create_new_room(room_name)
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
    room = room_manager.get_room_by_id(room_id)
    return room.to_dict()

@app.route("/emit_message_to_room", methods=["POST"])
@handle_server_errors
def emit_message_to_room():
    request_json = request.get_json()
    room_id = request_json("room_id")
    message = request_json("message")
    sio.emit('on_chat_bot_message_message', {"message": message}, to=room_id)
    return f"message [{message}] sent to room [{room_id}]"

@app.route("/list_room")
@handle_server_errors
def list_room():
    return room_manager.get_all_rooms_info()

# add ai message

# add user message




if __name__ == "__main__":
    sio.run(app, host="0.0.0.0", debug= False)
    