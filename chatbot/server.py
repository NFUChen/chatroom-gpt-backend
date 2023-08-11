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
    response = requests.post("http://chatroom-server:5000/emit_message_to_room", json= post_json)
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
        resp = emit_message_to_room(room_id, message_type, current_message)
        server_print(resp.json())

    resp = emit_message_to_room(room_id, message_type, current_message, is_message_persist= True)
    server_print(resp.json())


    return {
        **bot.bot_response.to_dict(),
        "asker_id": asker_id,
        "room_id": room_id
    }

'''
CREATE TABLE 
    IF NOT EXISTS gpt_responses (
        response_id VARCHAR(36) PRIMARY KEY NOT NULL,
        datetime TIMESTAMP NOT NULL,
        answer TEXT NOT NULL,
        prompt_tokens INT NOT NULL,
        response_tokens INT NOT NULL,
        room_id VARCHAR(36) NOT NULL,
        user_id INT NOT NULL,
        api_key VARCHAR(255) NOT NULL,
        FOREIGN KEY (room_id) REFERENCES rooms(room_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE
    IF NOT EXISTS gpt_messages (
        response_id VARCHAR(36) NOT NULL,
        role VARCHAR(10) CHECK (
            role = 'assistant' or role = 'user'
        ) NOT NULL,
        content TEXT NOT NULL,
        FOREIGN KEY (response_id) REFERENCES gpt_responses(response_id)
);
'''
        


@app.route("/count_tokens", methods=["POST"])
def count_tokens():
    request_json = request.get_json()
    messages = request_json["messages"]
    num_tokens = num_tokens_from_messages(messages)
    return jsonify({"num_tokens": num_tokens, "host": host}), 200


        


