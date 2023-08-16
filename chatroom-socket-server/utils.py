import functools

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
            }, 200  # Return JSON response with error message and status code 500
    return decorated