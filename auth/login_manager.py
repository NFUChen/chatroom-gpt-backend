from enum import Enum
from user_database_manager import user_db_manager
from authenticator import Authenticator
from user import User


class LoginError(Enum):
    USER_NOT_FOUND = "User not found"
    WRONG_PASSWORD = "Wrong password"


class LoginResponse:
    def __init__(self, error_message: str | None = None, user: User | None = None, is_sid: bool = False) -> None:
        self.error_message = error_message
        self.user = user
        self.is_sid = is_sid

    def is_login(self) -> bool:
        return self.user is not None
    
    def is_error(self) -> bool:
        return self.error_message is not None
    
    def to_dict(self) -> dict[str, str]:
        return {
            "error_message": self.error_message,
            "is_login": self.is_login(),
            "user": None if self.user is None else self.user.to_dict(),
            "is_sid": self.is_sid
        }

class LoginManager:
    def __init__(self, email: str, password: str) -> None:
        self.email = email
        self.password = password

    
    def login(self) -> LoginResponse:
        user = user_db_manager.get_user_by_email(self.email)
        if user is None:
            return LoginResponse(error_message=LoginError.USER_NOT_FOUND.value)
    
        if not Authenticator.verify_password(self.password, user.hashed_password):
            
            return LoginResponse(error_message=LoginError.WRONG_PASSWORD.value)
        
        return LoginResponse(user=user)
    