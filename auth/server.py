import os
from flask import request
from flask import Flask, jsonify
from flask_cors import CORS
from session_store import session_store
from authenticator import Authenticator
from user_database_manager import user_db_manager
from user import User
from user_validator import UserValidator
from login_manager import LoginManager, LoginResponse

app = Flask(__name__)
CORS(app)

server_print = lambda content: app.logger.info(content)

PORT = os.environ["PORT"]

@app.route("/index")
def index():
    return "Welcome to a server for managing session"
    
@app.route("/register", methods= ["POST"])
def register():
    user_info: dict[str, str] = request.get_json()
    email = user_info.get("email")
    user_name = user_info.get("user_name")
    pwd = user_info.get("password")
    validation_result = UserValidator(email, user_name, pwd).validate()
    validation_json = validation_result.to_json()
    if not validation_result.is_valid():
        return validation_json, 400
    
    hashed_pwd = Authenticator.hash_password(pwd)
    user_db_manager.register_user(email, user_name, hashed_pwd)
    server_print(f"Saving to db with {email}, {user_name}")
    return validation_json, 200

@app.route("/login", methods= ["POST"])
def login():
    sid = request.cookies.get("sid")
    if sid is not None and session_store.is_valid_sid(sid):
        session_store.refresh_session(sid)
        user_dict = session_store.get_user_dict_from_session(sid)
        current_user = User(**user_dict)
        login_response =  LoginResponse(user=current_user, is_sid=True)
        server_print(f"User already logged in with sid: {sid}")
        return login_response.to_dict(), 200

    user_info: dict[str, str] = request.get_json()
    email = user_info.get("email")
    pwd = user_info.get("password")
    if email is None or pwd is None:
        return {"error_message": "Missing email or password"}, 400

    
    login_response = LoginManager(email, pwd).login()
    if login_response.is_error():
        return login_response.to_dict(), 400
    
    if login_response.is_login():
        user_dict = login_response.user.to_dict()
        sid = session_store.add_user_in_session(user_dict)
        #set cookies for sid
        cookie_response = jsonify(login_response.to_dict())
        cookie_response.set_cookie("sid", sid)


    return cookie_response, 200
        


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug= True, port= PORT)