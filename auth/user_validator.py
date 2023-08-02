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
    
    def is_null_email(self) -> bool:
        return self.email is None

    def is_null_user_name(self) -> bool:
        return self.user_name is None
    
    def is_null_password(self) -> bool:
        return self.password is None
    
    def is_not_match_email_pattern(self) -> bool:
        return not self.EMAIL_REGEX.match(self.email)

    def is_duplicate_user(self) -> bool:
        return user_db_manager.is_duplicate_user(self.email)

    def validate(self) -> str | None:
        validation_func_with_error_code:tuple[bool, ValidatorError] = (
            (self.is_null_email, ValidatorError.NULL_EMAIL), 
            (self.is_null_user_name, ValidatorError.NULL_USER_NAME), 
            (self.is_null_password , ValidatorError.NULL_PASSWORD),
            (self.is_not_match_email_pattern, ValidatorError.INVALID_EMAIL),
            (self.is_duplicate_user, ValidatorError.DUPLICATE_USER),
        )

        for is_error_func, error_code in validation_func_with_error_code:
            if is_error_func():
                raise ValueError(error_code.value)
            
        

    
    
        
    