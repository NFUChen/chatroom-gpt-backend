from enum import Enum
import re
from user_database_manager import user_db_manager
class ValidatorError(Enum):
    NULL_EMAIL = "Email (email) is not provided"
    NULL_USER_NAME = "User name (user_name) is not provided"
    NULL_PASSWORD = "Password (password) is not provided"
    INVALID_EMAIL = "Email is not valid"
    DUPLICATE_USER = "Duplicate user"

class UserValidator:
    EMAIL_REGEX = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    def __init__(self, email: str, user_name: str, password: str) -> None:
        self.email = email
        self.user_name = user_name
        self.password = password

        self.validators_with_error_message = (
            (self.email, ValidatorError.NULL_EMAIL),
        )
        self.error_messages: list[str] = []

    def validate(self) -> str | None:
        validation_func_with_error_code:tuple[bool, ValidatorError] = {
            (self.email is None, ValidatorError.NULL_EMAIL), 
            (self.user_name is None, ValidatorError.NULL_USER_NAME), 
            (self.password is None , ValidatorError.NULL_PASSWORD),
            (not self.EMAIL_REGEX.match(self.email), ValidatorError.INVALID_EMAIL),
            (user_db_manager.is_duplicate_user(self.email), ValidatorError.DUPLICATE_USER),
        }

        for is_valid, error_code  in validation_func_with_error_code:
            if is_valid:
                return error_code.value

    
    
        
    