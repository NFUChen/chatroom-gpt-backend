from enum import Enum
from user_database_manager import user_db_manager
from session_store import session_store
from authenticator import Authenticator
from user import User
from typing import Any

class LoginError(Enum):
    USER_NOT_FOUND = "User not found"
    TOKEN_NOT_FOUND = "Token not found"
    WRONG_PASSWORD = "Wrong password"
    MISSING_EMAIL_OR_PASSWORD = "Missing email or password"

class LoginManager:
    @staticmethod
    def login_with_email_and_password(email: str | None, password: str | None) -> dict[str, Any]:

        if email is None or password is None:
            raise ValueError(LoginError.MISSING_EMAIL_OR_PASSWORD.value)
        
        user = user_db_manager.get_user_by_email(email)

        user_dict = user.to_dict()

        if not Authenticator.verify_password(password, user.password):
            raise ValueError(LoginError.WRONG_PASSWORD.value)
        # session_store.remove_duplicated_user(user_dict)
        sid = session_store.add_user_in_session(user_dict)
        return {
                "user": user_dict,
                "sid": sid,
                "is_sid": False,
            }
    


    @staticmethod
    def login_with_sid(sid: str | None) -> dict[str, str] | None:
        if sid is None:
            return

        user_dict = session_store.get_user_dict_from_session(sid)
        if user_dict is None:
            return
        
        user = User(**user_dict)
        session_store.refresh_session(sid)
        return {
                "user": user.to_dict(),
                "sid": sid,
                "is_sid": True,
        }
    
    def logout(sid: str | None) -> None:
        if sid is None:
            return
        session_store.remove_sid_from_session(sid)
    
    