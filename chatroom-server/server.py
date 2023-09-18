from flask import Flask, request
from flask_cors import CORS

from chat_room_utils import (
    init_room_manager, 
    init_openai_api_key_loadbalancer,
    init_personal_room_list_service,
)
from utils import (
    handle_server_errors, 
    login_required, 
    emit_socket_event
)
from room import Room
from chat_message import ChatMessage
import logging
import requests
import threading

logging.basicConfig(level=logging.DEBUG)
room_manager = init_room_manager()
api_key_load_balancer = init_openai_api_key_loadbalancer()
personal_room_list_service =  init_personal_room_list_service()

app = Flask(__name__)
CORS(app, supports_credentials=True)
CHATBOT_SERVER = "http://chatbot:5000"

@app.route("/")
def index():
    return "Welcome to chatroom central socket server"

@app.route("/update_api_keys")
def update_api_keys():
    global api_key_load_balancer
    api_key_load_balancer = init_openai_api_key_loadbalancer()
    return "ok"

@app.route("/join_room", methods = ["POST"])
@handle_server_errors
@login_required
def join_room():
    request_json = request.get_json()
    room_id = request_json["room_id"] #required

    user_id = request_json["user"]["user_id"]
    user_name = request_json["user"]["user_name"]
    full_id = f"{user_id}-{user_name}"

    joined_room = room_manager.user_join_room(full_id, room_id)
    socket_event = joined_room.get_socket_event("notification")
    notification = {
        "user_id": user_id,
        "user_name": user_name,
        "is_join": True
    }

    emit_socket_event(socket_event, notification)

    return "ok"

@app.route("/leave_room", methods = ["POST"])
@handle_server_errors
@login_required
def leave_room():
    request_json = request.get_json()
    user_id = request_json["user"]["user_id"]
    user_name = request_json["user"]["user_name"]
    full_id = f"{user_id}-{user_name}"

    left_room = room_manager.user_leave_room(full_id)

    socket_event = left_room.get_socket_event("notification")
    notification = {
            "user_name": user_name,
            "user_id": user_id,
            "is_join": False
    }
    emit_socket_event(socket_event, notification)
    
    return "ok"

@app.route("/user_location", methods = ["POST"])
@handle_server_errors
@login_required
def user_location():
    request_json = request.get_json()
    user_id = request_json["user"]["user_id"]
    user_name = request_json["user"]["user_name"]
    full_id = f"{user_id}-{user_name}"

    return room_manager.get_user_location(full_id)


@app.route("/create_room", methods=["POST"])
@handle_server_errors
@login_required
def create_room():
    request_json = request.get_json()
    room_name = request_json["room_name"]
    owner_id = request_json["user"]["user_id"]
    new_room = Room.create_new_room(room_name, owner_id)
    room_manager.add_room(new_room)
    return new_room.to_dict()

@app.route("/delete_room", methods=["POST"])
@handle_server_errors
@login_required
def delete_room():
    request_json = request.get_json()
    room_id = request_json["room_id"]
    popped_room =  room_manager.pop_room(room_id)
    return popped_room.to_dict()

@app.route("/room_info", methods=["POST"])
@handle_server_errors
@login_required
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
@login_required
def emit_message_to_room():
    '''
    {
        "content": str
        "is_message_persist": bool
        "message_type": str
    } 
    '''
    request_json = request.get_json()
    user_dict = request_json["user"]
    user_id = user_dict["user_id"]
    user_name = user_dict["user_name"]
    full_id = f"{user_id}-{user_name}"

    message_type = request_json.get("message_type")
    is_memo = request_json.get("is_memo", False)
    is_ai = request_json.get("is_ai", False)
    content = request_json["content"] #required
    is_message_persist = request_json.get("is_message_persist")
    
    room_id = (
        request_json["room_id"] if is_ai 
        else room_manager.get_user_location(full_id)
    ) 
    room = room_manager.get_room_by_id(room_id)
    socket_event = room.get_socket_event(message_type)

    payload = {
        "user_id": user_id, 
        "content": content, 
        "user_name": user_name, 
        "is_message_persist": is_message_persist
    }
    emit_socket_event(socket_event, payload)
    chat_message = ChatMessage.create_chat_message(
        message_type, user_id, user_name ,room_id, content,is_memo
    )
    if is_message_persist:
        room.add_message(
            chat_message
        )
    return {
        **chat_message.to_dict(), "is_message_persist": is_message_persist
    }

@app.route("/cmd", methods = ["POST"])
@handle_server_errors
@login_required
def cmd():
    '''
    This route is give necessary information for accessing other services that may block the server thread 
    (e.g., answer the users question, create embedding for memorization), 
    such operations will be outsourced to other services
    '''

    request_json = request.get_json()
    is_test = request_json.get("is_test")
    
    user_id = request_json["user"]["user_id"]
    user_name = request_json["user"]["user_name"]
    full_id = f"{user_id}-{user_name}"
    room_id = room_manager.get_user_location(full_id)
    room = room_manager.get_room_by_id(room_id)
    if room_manager.is_room_locked(room_id):
        raise ValueError(f"The AI assistant is currently answering the question, please waiting it to unlock the room {room_id}")
    
    post_json = {
        "room_id": room_id,
        "user_id": user_id,
        "user_name": user_name
    }
    
    messages = [message.to_dict() for message in room.get_ai_messages(3)]
    
    cmd_lookup = [
        ("answer", "messages", messages), # operation_name, post_json_key, post_json_value
        ("answer", "prompt", request_json.get("prompt")),
        ("answer", "source", request_json.get("source")),
        ("memo", "prompt", request_json.get("prompt"))
    ]

    operation = request_json.get("operation")
    for operation_name, post_json_key, post_json_value in cmd_lookup:
        if operation == operation_name:
            post_json[post_json_key] = post_json_value

    post_json["api_key"] = api_key_load_balancer.get_key()
    if is_test:
        return post_json
    
    def wrapper():
        try:
            if operation == "answer":
                print(f"Lock the room: {room_id}", flush= True)
                room_manager.lock_room(room_id)

            resp = requests.post(f"{CHATBOT_SERVER}/{operation}", json= post_json)
            print(f"Posting json: {post_json}")
            print(resp.json(), flush= True)
        finally:
            if operation == "answer":
                room_manager.unlock_room(room_id)
                print(f"Unlock the room: {room_id}", flush= True)
    
    threading.Thread(target= wrapper).start()

    
    return post_json


@app.route("/acquire_room_lock") # the lock is acquired by robot, so no need for login
@handle_server_errors
def acquire_room_lock():
    request_json = request.get_json()
    room_id = request_json["room_id"]
    room_manager.lock_room(room_id)

    return f"Room: {room_id} locked"

@app.route("/release_room_lock")
def release_room_lock():
    request_json = request.get_json()
    room_id = request_json["room_id"]
    room_manager.lock_room(room_id)

    return f"Room: {room_id} unlocked"

@app.route("/list_room", methods = ["POST"])
@handle_server_errors
@login_required
def list_room():
    request_json = request.get_json()
    filter_room_name = request_json.get("filter_room_name", "")
    return room_manager.get_all_rooms_info(filter_room_name= filter_room_name)

@app.route("/list_personal_room_list", methods = ["POST"])
@handle_server_errors
@login_required
def list_personal_room_list():
    request_json = request.get_json()
    user_id = request_json["user"]["user_id"]

    return personal_room_list_service.get_room_list_by_user_id(user_id)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug= False)
    