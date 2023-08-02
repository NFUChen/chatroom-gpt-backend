from flask import request
from flask import Flask
from flask_cors import CORS
from session_store import session_store
from authenticator import Authenticator
from user_database_manager import user_db_manager
from user_validator import UserValidator
from login_manager import LoginManager
from utils import handle_server_errors
app = Flask(__name__)
CORS(app)

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


@app.route("/logout", methods= ["POST"])
@handle_server_errors
def logout():
    sid = request.cookies.get("sid")
    LoginManager.logout(sid)
    return "Logout successfully"

@app.route("/is_valid_sid", methods= ["POST"])
@handle_server_errors
def is_valid_sid():
    response_dict = {
        "is_valid_sid": False,
    }
    sid = request.get_json()["sid"]
    if session_store.is_valid_sid(sid):
        response_dict["is_valid_sid"] = True
    return response_dict
        
# is valid user

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug= True)