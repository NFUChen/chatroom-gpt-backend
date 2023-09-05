import functools
from flask import request
import requests
import traceback

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
                "error": None
            }
        except Exception as error:
            return {
                "data": None,
                "error": get_error_detail(error)
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
        if response.status_code == 401:
            return {
                "data": None,
                "error": "SID Unauthorized"
            }, 401

        user_dict = response.json()["data"]
        if user_dict is None:
            return {
                "data": None,
                "error": "Please login first before this API call."
            }, 401
        request.json["user"] = user_dict
        return func(*args, **kwargs)
        
    return decorated