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
    create_system_pompt, 
    concat_messages_till_threshold,
    get_hash,
    is_duplicate_embedding
)
import requests
from response_database_manager import response_db_manager
from qdrant_vector_store import qdrant_vector_store
from embedding_service import embedding_service
import json
from paho.mqtt.publish import single
from langchain.text_splitter import RecursiveCharacterTextSplitter
import uuid
app = Flask(__name__)
CORS(app, supports_credentials=True)

server_print = lambda content: app.logger.info(content)
host = socket.gethostname()


default_text_spliter = RecursiveCharacterTextSplitter(
    chunk_size = 500, chunk_overlap  = 50, length_function = len, add_start_index = True
)

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
        "user_name": "openai",
        "content": content,
        "is_message_persist": is_message_persist
    }
    socket_event = f"{message_type}/{room_id}"
    topic = f"message/{socket_event}"
    payload = {
            "data": {"user_id": 1,"content": content, "is_message_persist": is_message_persist},
            "socket_event": socket_event
    }
    single(topic, json.dumps(payload), 1, hostname= "mosquitto")
    if is_message_persist: # only post if true
        response = requests.post("http://chatroom-server:5000/save_ai_message", json= post_json)
        return response

@app.route("/")
def index():
    return f"Welcome to a server for answering question {host} and creating embeddings", 200

@app.route("/answer", methods=["POST"])
@handle_server_errors
def answer():
    request_json = request.get_json()
    messages = convert_messages(request_json["messages"])
    api_key = request_json["api_key"]
    room_id = request_json["room_id"]
    asker_id = request_json["asker_id"]
    message_type = "ai"
    query = concat_messages_till_threshold([msg_dict["content"] for msg_dict in messages[:3][::-1]], 1000) or messages[-1]["content"]

    embedding = embedding_service.get_embedding(query, None, None)
    query_results = qdrant_vector_store.search_text_chunks(room_id, embedding, threshold= 0.7)
    
    system_prompt = create_system_pompt(query_results)
    print(system_prompt, flush= True)
    bot = ChatBot(api_key, system_prompt, messages)
    for current_message in bot.answer():
        emit_message_to_room(room_id, message_type, current_message)

    emit_message_to_room(room_id, message_type, current_message, is_message_persist= True)

    response_dict = {
        **bot.bot_response.to_dict(),
        "asker_id": asker_id,
        "room_id": room_id,
        "document_sources": list(set([
            result["document_id"] for result in query_results
        ]))
    }
    print(response_dict, flush= True)
    return response_dict

@app.route("/count_tokens", methods=["POST"])
def count_tokens():
    request_json = request.get_json()
    messages = request_json["messages"]
    num_tokens = num_tokens_from_messages(messages)
    return jsonify({"num_tokens": num_tokens, "host": host}), 200


@app.route("/memo", methods=["POST"])
@handle_server_errors
def memo():
    request_json = request.get_json()
    room_id = request_json["room_id"]
    text = request_json["text"]
    is_file_upload = request_json.get("is_file_upload")
    
    text_length = len(text)
    size_limit = 15000 if is_file_upload else 3000

    if text_length == 0:
        raise ValueError(f"Abort empty text memo request")

    if text_length > size_limit:
        raise ValueError(f"Text length must shorter than {size_limit}, entering {text_length}")

    chunks = [
        chunk for chunk in default_text_spliter.split_text(text)
    ]
    embeddings = []
    document_id = str(uuid.uuid4())
    for chunk in chunks:
        chunk_hash = get_hash(chunk)
        if is_duplicate_embedding(chunk_hash):
            continue

        embedding = embedding_service.get_embedding(chunk, document_id,chunk_hash) 
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



