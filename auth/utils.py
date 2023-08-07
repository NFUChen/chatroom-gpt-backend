import functools
import traceback
from flask import jsonify
import datetime
import random
import string

EXPIRE_TIME =  60 * 60 * 24 * 3
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


def generate_unique_random_string(string_len: int = 50) -> str:
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(string_len))
    return random_string


def handle_server_errors(func):
    @functools.wraps(func)
    def decorated(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            result_json = {
                    "data": result,
                    "error": None
            }
            if "sid" in result:
                sid = result.pop("sid")
                cookie_response = jsonify(result_json)
                expired_time_stamp = datetime.datetime.now() + datetime.timedelta(seconds= EXPIRE_TIME)
                cookie_response.set_cookie("sid", sid, expires= expired_time_stamp)
                return cookie_response
            return result_json, 200
        
        except Exception as error:
            return {
                "data": None,
                "error": get_error_detail(error)
            }, 200  # Return JSON response with error message and status code 500
    return decorated