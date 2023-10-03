
from flask import request
from flask import Flask
from flask_cors import CORS
from mysql_query_manager import query_manager
app = Flask(__name__)
CORS(app)

server_print = lambda content: app.logger.info(content)

@app.route("/index")
def index():
    return "Welcome to a server for query SQL database"

@app.route("/query", methods= ["POST"])
def query():
    request_json: dict[str, str] = request.get_json()
    query = request_json["query"]
    return query_manager.query(query)

@app.route("/update", methods= ["POST"])
def execute_update():
    request_json: dict[str, str] = request.get_json()
    query = request_json["query"]
    return query_manager.execute_update(query)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug= True)