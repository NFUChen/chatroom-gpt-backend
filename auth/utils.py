import functools
import traceback
from flask import jsonify
import datetime
from session_store import session_store 
def get_error_detail(e: Exception):
    error_name = e.__class__.__name__
    file_name = traceback.extract_tb(e.__traceback__)[-1].filename
    line_number = traceback.extract_tb(e.__traceback__)[-1].lineno
    error_message = str(e)
    return {
        'error_name': error_name,
        'file_name': file_name,
        'line_number': line_number,
        'error_message': error_message
    }


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
                cookie_response = jsonify(result_json)
                expired_time_stamp = datetime.datetime.now() + datetime.timedelta(seconds= session_store.expired_time)
                cookie_response.set_cookie("sid", result["sid"], expires= expired_time_stamp)
                return cookie_response
            return result_json, 200
        
        except Exception as error:
            return {
                "data": None,
                "error": str(error)
            }, 200  # Return JSON response with error message and status code 500
    return decorated