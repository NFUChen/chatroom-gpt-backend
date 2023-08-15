from typing import Literal
from flask import request
from flask import Flask, jsonify
from flask_cors import CORS
import requests
import socket
from openai_utils import num_tokens_from_messages
from chatbot import ChatBot
from utils import handle_server_errors, convert_messages
import requests
from response_database_manager import response_db_manager
import json
from paho.mqtt.publish import single
app = Flask(__name__)
CORS(app)

server_print = lambda content: app.logger.info(content)
host = socket.gethostname()


def emit_message_to_room(room_id: str, message_type: Literal["regular" , "ai"], content:str, is_message_persist: bool = False) -> requests.Response:
    '''
    {
        "message_type": "regular" | "ai"
        "room_id": str
        "user_id": str
        "content": str
        "is_message_persist": bool
    } 
    '''
    post_json = {
        "message_type": message_type,
        "room_id": room_id,
        "user_id": 1, # 1 is openAI
        "content": content,
        "is_message_persist": is_message_persist
    }
    socket_event = f"{message_type}/{room_id}"
    topic = f"message/{socket_event}"
    payload = {
            "data": {"user_id": 1, "content": content},
            "socket_event": socket_event
    }
    single(topic, json.dumps(payload), 1, hostname= "mosquitto")
    if is_message_persist: # only post if true
        response = requests.post("http://chatroom-server:5000/save_ai_message", json= post_json)
        return response

@app.route("/")
def index():
    return f"Welcome to a server for answering question {host}", 200

@app.route("/answer", methods=["POST"])
@handle_server_errors
def answer():
    request_json = request.get_json()
    messages = convert_messages(request_json["messages"])
    api_key = request_json["api_key"]
    room_id = request_json["room_id"]
    asker_id = request_json["asker_id"]
    message_type = "ai"
    bot = ChatBot(api_key, messages)
    for current_message in bot.answer():
        emit_message_to_room(room_id, message_type, current_message)

    emit_message_to_room(room_id, message_type, current_message, is_message_persist= True)

    response_dict = {
        **bot.bot_response.to_dict(),
        "asker_id": asker_id,
        "room_id": room_id
    }

    response_db_manager.save_response(response_dict)
    return response_dict

@app.route("/count_tokens", methods=["POST"])
def count_tokens():
    request_json = request.get_json()
    messages = request_json["messages"]
    num_tokens = num_tokens_from_messages(messages)
    return jsonify({"num_tokens": num_tokens, "host": host}), 200


        


