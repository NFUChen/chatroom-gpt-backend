from flask import request
from flask import Flask, jsonify
from flask_cors import CORS
import requests
import socket
from openai_utils import num_tokens_from_messages
from chatbot import ChatBot

app = Flask(__name__)
CORS(app)

server_print = lambda content: app.logger.info(content)
host = socket.gethostname()


def emit_message_to_room(room_id: str, message:str) -> requests.Response:
    post_json = {
        "room_id": room_id,
        "message": message
    }
    response = requests.post("http://chatroom-server:8080/emit_message_to_room", json= post_json)
    return response

@app.route("/")
def index():
    return f"Welcome to a server for answering question {host}", 200

@app.route("/answer", methods=["POST"])
def answer():
    request_json = request.get_json()
    messages = request_json["messages"]
    api_key = request_json["api_key"]
    room_id = request_json["room_id"]
    bot = ChatBot(api_key, messages)
    for current_message in bot.answer():
        resp = emit_message_to_room(room_id, current_message)
        server_print(resp)
    
    bot.bot_reponse["room_id"] = room_id

    return bot.bot_reponse, 200
        


@app.route("/count_tokens", methods=["POST"])
def count_tokens():
    request_json = request.get_json()
    messages = request_json["messages"]
    num_tokens = num_tokens_from_messages(messages)
    return jsonify({"num_tokens": num_tokens, "host": host}), 200


        


