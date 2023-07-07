
from flask import request
from flask import Flask
from flask_cors import CORS
from producer import producer
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
        "db": str,
        "collection": str,
        "doc": dict[str, str]
    }
'''

@app.route("/produce", methods= ["POST"])
def produce():
    request_json: dict[str, str] = request.get_json()
    keys = ["queue", "db", "collection", "doc"]
    missing_keys = []
    for key in keys:
        value = request_json.get(key)
        if value is not None:
            continue
        missing_keys.append(key)
    if len(missing_keys) != 0:
        return {"message": f"Missing {missing_keys}"}, 400
    

    queue = request_json.pop("queue")

    producer.publish(queue, str(request_json))
    return {"message": f"Message {request_json} published to {queue}"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug= True, port= 8080)