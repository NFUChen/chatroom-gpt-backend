from enum import Enum
import re
from user_database_manager import user_db_manager
class ValidatorError(Enum):
    NULL_EMAIL = "Email (email) is not provided"
    NULL_USER_NAME = "User name (user_name) is not provided"
    NULL_PASSWORD = "Password (password) is not provided"
    INVALID_EMAIL = "Email is not valid"
    DUPLICATE_USER = "Duplicate user"

class ValidationResult:
    
    def __init__(self, error_messages: list[str]) -> None:
        self.error_messages = error_messages

    def is_valid(self) -> bool:
        return len(self.error_messages) == 0
    
    @property
    def message(self) -> str:
        return "Validation passed" if self.is_valid() else "Validation failed"
    
    
    def to_json(self) -> dict[str, str]:
        return {"failed_items": self.error_messages,
                "message": self.message,
                "is_valid": self.is_valid()
            }

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

    def _validate_null_attr(self) -> None:
        attr_lookup =(
            (self.email, ValidatorError.NULL_EMAIL), 
            (self.user_name, ValidatorError.NULL_USER_NAME), 
            (self.password , ValidatorError.NULL_PASSWORD)
        )


        for attr, error in attr_lookup:
            if attr is None:
                self.error_messages.append(error.value)

    def _validate_email(self) -> None:
        if self.email is None:
            return
        
        if not self.EMAIL_REGEX.match(self.email):
            self.error_messages.append(ValidatorError.INVALID_EMAIL.value)
            return

        if user_db_manager.is_duplicate_user(self.email):
            self.error_messages.append(ValidatorError.DUPLICATE_USER.value)

    def validate(self) -> ValidationResult:
        validators = (
            self._validate_null_attr,
            self._validate_email,
        )
        for validator in validators:
            validator()
        
        return ValidationResult(self.error_messages)
    
    
        
    