import os
from flask import request
from flask import Flask, jsonify
from flask_cors import CORS
from session_store import session_store
from authenticator import Authenticator
from user_database_manager import user_db_manager
from user import User
from user_validator import UserValidator
from login_manager import LoginManager
import datetime
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
    error = UserValidator(email, user_name, pwd).validate()
    if error:
        return error, 400
    
    hashed_pwd = Authenticator.hash_password(pwd)
    user_db_manager.register_user(email, user_name, hashed_pwd)
    server_print(f"Saving to db with {email}, {user_name}")
    return "register successfully", 200

@app.route("/login", methods= ["POST"])
def login():
    cookie_sid = request.cookies.get("sid")
    if cookie_sid is not None:
        login_response =  LoginManager.login_with_sid(cookie_sid)
        if login_response.is_login():
            server_print(f"User already logged in with sid: {cookie_sid}")
            return login_response.to_dict(), 200

    user_info: dict[str, str] = request.get_json()
    email = user_info.get("email")
    pwd = user_info.get("password")
    
    login_response = LoginManager.login_with_email_and_password(email, pwd)
    if not login_response.is_login():
        return login_response.to_dict(), 400
    
    #set cookies for sid
    server_print(f"User logged in with sid: {login_response.sid}")
    cookie_response = jsonify(login_response.to_dict())
    expired_time_stamp = datetime.datetime.now() + datetime.timedelta(seconds= session_store.expired_time)
    cookie_response.set_cookie("sid", login_response.sid, expires= expired_time_stamp)


    return cookie_response, 200
@app.route("/logout", methods= ["POST"])
def logout():
    sid = request.cookies.get("sid")
    LoginManager.logout(sid)
    cookie_response = jsonify({"message": "Logout successfully"})
    cookie_response.set_cookie("sid", expires= 0)


    return cookie_response, 200


        
# is valid user

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug= True, port= PORT)