from enum import Enum
from user_database_manager import user_db_manager
from session_manager import session_store
from authenticator import Authenticator
from user import User


class LoginError(Enum):
    USER_NOT_FOUND = "User not found"
    TOKEN_NOT_FOUND = "Token not found"
    WRONG_PASSWORD = "Wrong password"
    MISSING_EMAIL_OR_PASSWORD = "Missing email or password"


class LoginResponse:
    def __init__(self, 
                 error_message: str | None = None, 
                 user: User | None = None, 
                 is_sid: bool = False,
                 sid: str = None) -> None:
        self.error_message = error_message
        self.user = user
        self.is_sid = is_sid
        self.sid = sid
    

    def is_login(self) -> bool:
        return self.user is not None
    
    def to_dict(self) -> dict[str, str]:
        return {
            "error_message": self.error_message,
            "is_login": self.is_login(),
            "user": None if self.user is None else self.user.to_dict(),
            "is_sid": self.is_sid,
        }

class LoginManager:
    
    @staticmethod
    def login_with_email_and_password(email: str | None, password: str | None) -> LoginResponse:

        if email is None or password is None:
            return LoginResponse(error_message=LoginError.MISSING_EMAIL_OR_PASSWORD.value)
        
        user = user_db_manager.get_user_by_email(email)
        if user is None:
            return LoginResponse(error_message=LoginError.USER_NOT_FOUND.value)
    
        if not Authenticator.verify_password(password, user.hashed_password):
            
            return LoginResponse(error_message=LoginError.WRONG_PASSWORD.value)
        sid = session_store.add_user_in_session(user.to_dict())
        return LoginResponse(user=user, sid=sid)
    @staticmethod
    def login_with_sid(sid: str) -> LoginResponse:
        user_dict = session_store.get_user_dict_from_session(sid)
        if user_dict is None:
            return LoginResponse(error_message=LoginError.TOKEN_NOT_FOUND.value)
        
        user = User(**user_dict)
        session_store.refresh_session(sid)
        return LoginResponse(user=user, is_sid=True)
    
    def logout(sid: str | None) -> None:
        if sid is None:
            return
        session_store.remove_sid_from_session(sid)
    
    