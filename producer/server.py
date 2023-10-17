
from flask import request
from flask import Flask
from flask_cors import CORS
from producer import producer
from utils import handle_server_errors
app = Flask(__name__)
CORS(app)

server_print = lambda content: app.logger.info(content)

@app.route("/index")
def index():
    return "Welcome to a server for storing mongodb document"

'''
Signature:
    {
        "queue": str,
        "data": dict[str, Any],
    }
'''

@app.route("/produce", methods= ["POST"])
@handle_server_errors
def produce():
    request_json: dict[str, str] = request.get_json()
    keys = ["queue", "data"]
    missing_keys = []
    for key in keys:
        value = request_json.get(key)
        if value is not None:
            continue
        missing_keys.append(key)
    if len(missing_keys) != 0:
        return f"Missing {missing_keys}"

    queue = request_json.pop("queue")

    producer.publish(queue, str(request_json["data"]))
    return f"Message {request_json} published to {queue}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug= True)