from typing import Callable
from flask import request
from flask import Flask
from flask_cors import CORS
from session_store import session_store
from authenticator import Authenticator
from user_database_manager import user_db_manager, User
from user_validator import UserValidator
from login_manager import LoginManager
from utils import handle_server_errors, UnauthorizedError
app = Flask(__name__)
CORS(app, supports_credentials=True)
server_print = lambda content: app.logger.info(content)

@app.route("/index")
def index():
    return "Welcome to a server for managing session"
    
@app.route("/register", methods= ["POST"])
@handle_server_errors
def register():
    user_info: dict[str, str] = request.get_json()
    email = user_info.get("user_email")
    user_name = user_info.get("user_name")
    pwd = user_info.get("password")
    UserValidator(email, user_name, pwd).validate()
    hashed_pwd = Authenticator.hash_password(pwd)
    response = user_db_manager.register_user(email, user_name, hashed_pwd)
    server_print(response)

    return "register successfully"

@app.route("/login", methods= ["POST"])
@handle_server_errors
def login():
    cookie_sid = request.cookies.get("sid")
    user_dict =  LoginManager.login_with_sid(cookie_sid)
    if user_dict is not None:
        return user_dict

    user_info: dict[str, str] = request.get_json()
    email = user_info.get("user_email")
    pwd = user_info.get("password")
    
    user_dict = LoginManager.login_with_email_and_password(email, pwd)

    
    return user_dict

@app.route("/user_status")
@handle_server_errors
def user_status():
    cookie_sid = request.cookies.get("sid")
    user_dict = session_store.get_user_dict_from_session(cookie_sid)
    if user_dict is None:
        raise ValueError(f"Invalid SID: {cookie_sid}")
    
    return user_dict

@app.route("/query_user", methods= ["POST"])
@handle_server_errors
def query_user():
    query: dict[str, str] = request.get_json()
    by = query["by"]
    value = query["value"]
    func_lookup:dict[str, Callable[[str], User]] = {
        "user_email":user_db_manager.get_user_by_email,
        "user_id": user_db_manager.get_user_by_user_id
    }
    user_dict = func_lookup[by](value).to_dict()
    user_dict.pop("password")
    
    return user_dict



@app.route("/logout", methods= ["POST"])
@handle_server_errors
def logout():
    sid = request.cookies.get("sid")
    LoginManager.logout(sid)
    return "Logout successfully"



@app.route("/query_user_with_sid", methods= ["POST"])
@handle_server_errors
def query_user_with_sid():
    sid = request.get_json()["sid"]
    user_dict = session_store.get_user_dict_from_session(sid)
    if user_dict is None:
        raise UnauthorizedError(f"SID: {sid} has expired")
       
    return user_dict
        


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug= True)