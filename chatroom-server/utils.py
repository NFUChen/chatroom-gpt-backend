import functools
from flask import request
import requests


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
                "error": str(error)
            }, 500  # Return JSON response with error message and status code 500
    return decorated

def login_required(func):
    query_user_api = "http://auth:5000/query_user_with_sid"
    @functools.wraps(func)
    def decorated(*args, **kwargs):
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
        request.json["user"] = user_dict


        return func(*args, **kwargs)
        
    return decorated