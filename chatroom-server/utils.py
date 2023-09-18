from typing import Any
import functools
from flask import request
import requests
import traceback
import json
from paho.mqtt.publish import single

query_api = f"http://query_manager:5000/query"

def get_error_detail(e: Exception):
    error_name = e.__class__.__name__
    trace_back = traceback.extract_tb(e.__traceback__)
    file_name = trace_back[-1].filename
    line_number = trace_back[-1].lineno
    error_message = str(e)
    return {
        'error_name': error_name,
        'file_name': file_name,
        'line_number': line_number,
        'error_message': error_message,
        "trace_back": str(trace_back)
    }

def handle_server_errors(func):
    @functools.wraps(func)
    def decorated(*args, **kwargs):
        try:
            return {
                "data": func(*args, **kwargs),
                "error": None,
                "is_success": True
            }
        except Exception as error:
            return {
                "data": None,
                "error": get_error_detail(error),
                "is_success": False
            }, 200
    return decorated

def login_required(func):
    query_user_api = "http://auth:5000/query_user_with_sid"
    @functools.wraps(func)
    def decorated(*args, **kwargs):
        is_ai = request.get_json().get("is_ai", False)
        if is_ai:
            return func(*args, **kwargs)

        response = requests.post(
            query_user_api, json= {
                "sid": request.cookies.get("sid")
            }
        )
        user_dict = response.json()["data"]
        if user_dict is None:
            raise ValueError("Please login first before this API call.")
        
        request.json["user"] = user_dict
        return func(*args, **kwargs)
        
    return decorated

def query_api_keys() -> list[str]:
    sql = "SELECT api_key FROM api_keys WHERE is_disabled = 0"
    post_json = {
            "query": sql
    }
    key_dicts = requests.post(
        query_api, json= post_json
    ).json()["data"]

    return [_dict["api_key"] for _dict in key_dicts]


def emit_socket_event(socket_event: str, data: Any) -> None:
    payload = {
            "data": data
    }
    single(socket_event, json.dumps(payload), 1, hostname= "mosquitto")