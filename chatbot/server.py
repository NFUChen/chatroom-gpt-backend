from typing import Literal
from flask import request
from flask import Flask, jsonify
from flask_cors import CORS
import requests
import socket
from openai_utils import num_tokens_from_messages
from chatbot import ChatBot
from utils import (
    handle_server_errors, 
    convert_messages, 
    create_assistant_pompt,
    get_hash,
    is_duplicate_embedding,
    query_ai_user_dict,
    create_memorization_prompt
)
import requests
from response_database_manager import response_db_manager
from qdrant_vector_store import qdrant_vector_store
from embedding_service import embedding_service
import json
from paho.mqtt.publish import single
from langchain.text_splitter import RecursiveCharacterTextSplitter
import uuid
import openai
import time
import opencc

app = Flask(__name__)
CORS(app, supports_credentials=True)
server_print = lambda content: app.logger.info(content)
host = socket.gethostname()
converter = opencc.OpenCC('s2twp.json')

ai_user_dict = query_ai_user_dict()
default_text_spliter = RecursiveCharacterTextSplitter(
    chunk_size = 500, chunk_overlap  = 50, length_function = len, add_start_index = True
)
CHATROOM_SERVER = "http://chatroom-server:5000"

def validate_prompt(prompt: str, size_limit: int = 15000) -> None:
    prompt_length = len(prompt)

    if prompt_length == 0:
        raise ValueError(f"Abort empty text memo request")

    if prompt_length > size_limit:
        raise ValueError(f"Prompt length must shorter than {size_limit}, entering {prompt_length}")

def emit_message_to_room(room_id: str, message_type: Literal["regular" , "ai"], user_id: str, user_name: str,content:str, is_message_persist: bool = False) -> requests.Response | None:
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
        "user": {
            "user_id": user_id,
            "user_name": user_name,
        },
        "is_ai": True,
        "content": content,
        "is_message_persist": is_message_persist
    }
    socket_event = f"{message_type}/{room_id}"
    topic = f"message/{socket_event}"
    payload = {
            "data": {"user_id": user_id,"content": content, "is_message_persist": is_message_persist},
            "socket_event": socket_event
    }
    single(topic, json.dumps(payload), 1, hostname= "mosquitto")
    if is_message_persist: # only post if true
        response = requests.post(f"{CHATROOM_SERVER}/emit_message_to_room", json= post_json)
        return response.json()

@app.route("/")
def index():
    return f"Welcome to a server for answering question {host} and creating embeddings", 200

@app.route("/answer", methods=["POST"])
@handle_server_errors
def answer():
    request_json = request.get_json()
    prompt = request_json["prompt"]
    openai.api_key = request_json["api_key"]
    room_id = request_json["room_id"]
    user_id = request_json["user_id"]
    user_name = request_json["user_name"]
    messages_with_prompt = convert_messages([*request_json["messages"], {"user_id": user_id, "content": prompt}])
    query = messages_with_prompt[-1]["content"]

    embedding = embedding_service.get_embedding(query, None, None)
    query_results = qdrant_vector_store.search_text_chunks(room_id, embedding, threshold= 0.8)

    
    system_prompt = create_assistant_pompt(query_results)
    print(system_prompt, flush= True)
    ai_id = ai_user_dict["user_id"]
    ai_name = ai_user_dict["user_name"]

    message_type = "ai"

    emit_message_to_room(room_id, message_type, user_id,user_name ,prompt)
    bot = ChatBot(system_prompt, messages_with_prompt)
    for current_message in bot.answer():
        emit_message_to_room(room_id, message_type,ai_id ,ai_name,current_message)

    emit_message_to_room(room_id, message_type, user_id,user_name , prompt, is_message_persist= True)
    time.sleep(1)
    emit_message_to_room(room_id, message_type, ai_id ,ai_name,current_message, is_message_persist= True)

    response_dict = {
        **bot.bot_response.to_dict(),
        "user_id": user_id,
        "room_id": room_id,
        "document_sources": list(set([
            result["document_id"] for result in query_results
        ]))
    }
    print(response_dict, flush= True)
    return "ok"

@app.route("/count_tokens", methods=["POST"])
def count_tokens():
    request_json = request.get_json()
    messages = request_json["messages"]
    num_tokens = num_tokens_from_messages(messages)
    return jsonify({"num_tokens": num_tokens, "host": host}), 200

@app.route("/improve_prompt", methods=["POST"])
@handle_server_errors
def improve_prompt():
    request_json = request.get_json()

    openai.api_key = request_json["api_key"]
    prompt = request_json["prompt"]
    user_id = request_json["user_id"]
    lang = request_json["language"]

    socket_event = f"prompt/{user_id}"
    topic = f"message/{socket_event}"
    validate_prompt(prompt)
    system_prompt = create_memorization_prompt(prompt, lang)
    bot = ChatBot(system_prompt, [])
    for current_message in bot.answer():
        payload = {
            "data": {"user_id": user_id,"content": current_message},
            "socket_event": socket_event
        }
        single(topic, json.dumps(payload), 1, hostname= "mosquitto")

    payload["data"]["is_message_persist"] = True
    payload["data"]["content"] = converter.convert(payload["data"]["content"])
    single(topic, json.dumps(payload), 1, hostname= "mosquitto")

@app.route("/memo", methods=["POST"])
@handle_server_errors
def memo():
    request_json = request.get_json()
    openai.api_key = request_json["api_key"]
    room_id = request_json["room_id"]
    prompt = request_json["prompt"]
    validate_prompt(prompt)

    chunks = [
        chunk for chunk in default_text_spliter.split_text(prompt)
    ]
    embeddings = []
    document_id = str(uuid.uuid4())
    for chunk in chunks:
        chunk_hash = get_hash(chunk)
        if is_duplicate_embedding(chunk_hash):
            continue
        embedding = embedding_service.get_embedding(chunk, document_id, chunk_hash) 
        embeddings.append(embedding)
    if len(embeddings) == 0:
        raise ValueError("All embeddings are duplicates")
    
    '''
    "is_ok": is_ok,
    "collection_name": collection_name,
    "embeddings": embeddings
    '''
    upsert_resp  = qdrant_vector_store.upsert_text(room_id, embeddings)
    
    if not upsert_resp["is_ok"]:
        raise ValueError("Failed to insert Text")
    response_db_manager.save_embeddings(
        collection_name= upsert_resp["collection_name"],
        embeddings= [embedding.to_dict() for embedding in upsert_resp["embeddings"]]
    )
    
    return upsert_resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug= True)
